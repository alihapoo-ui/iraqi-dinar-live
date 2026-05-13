from __future__ import annotations

import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import requests
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

# =====================================================
# CONFIG
# =====================================================

CHANNEL = "PMCgroup"
CSV_FILE = "usd_history.csv"
IRAQ_TZ = ZoneInfo("Asia/Baghdad")
CURRENCIES = ["EUR", "GBP", "TRY", "AED", "SAR", "KWD"]
MAX_ROWS = 5000

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
STRING_SESSION = os.environ["STRING_SESSION"]

# =====================================================
# HELPERS
# =====================================================

def extract_usd_iqd(text: str) -> float | None:
    """Extract patterns like 100$=153,250 and return IQD per 1 USD, e.g. 1532.5."""
    patterns = [
        r"100\s*\$\s*[=:：\-]?\s*([0-9]{2,3}(?:,[0-9]{3})+|[0-9]{5,6})",
        r"100\s*دولار\s*[=:：\-]?\s*([0-9]{2,3}(?:,[0-9]{3})+|[0-9]{5,6})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue

        raw_value = match.group(1).replace(",", "").strip()
        market_per_100 = float(raw_value)

        if 100000 <= market_per_100 <= 250000:
            return market_per_100 / 100

    return None


def get_latest_pmc_rate() -> float:
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    client.connect()

    if not client.is_user_authorized():
        client.disconnect()
        raise RuntimeError("Telegram session is not authorized. Regenerate STRING_SESSION.")

    try:
        messages = client.get_messages(CHANNEL, limit=50)

        for msg in messages:
            text = getattr(msg, "message", None)
            if not text:
                continue

            usd_rate = extract_usd_iqd(text)
            if usd_rate is not None:
                print(f"USD/IQD found: {usd_rate}")
                return usd_rate

        raise RuntimeError("No valid USD/IQD pattern found in latest market messages.")

    finally:
        client.disconnect()


def get_fx_rates() -> dict:
    url = "https://open.er-api.com/v6/latest/USD"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    data = response.json()

    if data.get("result") not in ["success", None]:
        raise RuntimeError(f"FX API returned unexpected result: {data.get('result')}")

    rates = data.get("rates", {})
    missing = [cur for cur in CURRENCIES if cur not in rates]
    if missing:
        raise RuntimeError(f"Missing FX rates: {missing}")

    return rates


def build_row(usd_rate: float, fx_rates: dict) -> dict:
    market_price = round(usd_rate * 100, 0)
    spread = 250

    row = {
        "Time": datetime.now(IRAQ_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "USD": round(usd_rate, 2),
        "Market": market_price,
        "Buy": market_price + spread,
        "Sell": market_price - spread,
    }

    # FX API gives foreign currency per 1 USD.
    # Therefore IQD per 1 foreign currency = USD/IQD divided by FX quote.
    for currency in CURRENCIES:
        row[currency] = round(usd_rate / float(fx_rates[currency]), 2)

    return row


def get_last_usd_rate_from_csv() -> float | None:
    if not os.path.exists(CSV_FILE):
        return None
    try:
        df = pd.read_csv(CSV_FILE)
        if "USD" not in df.columns or df.empty:
            return None
        usd = pd.to_numeric(df["USD"], errors="coerce").dropna()
        return float(usd.iloc[-1]) if not usd.empty else None
    except Exception:
        return None


def update_csv(new_row: dict) -> None:
    columns = ["Time", "USD", "EUR", "GBP", "TRY", "AED", "SAR", "KWD", "Market", "Buy", "Sell"]

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=columns)

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df = df[columns]

    # Keep the CSV small and fast for Streamlit.
    if len(df) > MAX_ROWS:
        df = df.tail(MAX_ROWS).reset_index(drop=True)

    df.to_csv(CSV_FILE, index=False)

    print("CSV updated successfully")
    print(new_row)


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    try:
        usd_rate = get_latest_pmc_rate()
    except Exception as exc:
        fallback = get_last_usd_rate_from_csv()
        if fallback is None:
            raise
        print(f"Warning: failed to read Telegram rate ({exc}). Using last known USD rate: {fallback}")
        usd_rate = fallback

    fx_rates = get_fx_rates()
    row = build_row(usd_rate, fx_rates)
    update_csv(row)
