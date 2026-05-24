from __future__ import annotations

import os
import re
from datetime import datetime, timezone, timedelta

import pandas as pd
import requests
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

CSV_FILE = "usd_history.csv"
MAX_ROWS = 10000
IRAQ_TZ = timezone(timedelta(hours=3))

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
STRING_SESSION = os.getenv("STRING_SESSION", "")

CHAT_ID = int(os.getenv("PMC_CHAT_ID", "-1001035883465"))

FX_ENDPOINTS = [
    "https://open.er-api.com/v6/latest/USD",
    "https://api.exchangerate-api.com/v4/latest/USD",
]

CURRENCIES = ["EUR", "GBP", "TRY", "AED", "SAR", "KWD"]


def extract_rate_from_message(message_text: str) -> float | None:
    """Extract USD/IQD rate from message text."""
    if not message_text:
        return None

    try:
        numbers = re.findall(r"\d+(?:\.\d+)?", message_text)

        if not numbers:
            return None

        rates = [float(num) for num in numbers]

        valid_rates = [r for r in rates if 800 < r < 3000]

        if valid_rates:
            return valid_rates[-1]

        return rates[-1] if rates else None

    except Exception:
        return None


def get_latest_pmc_rate() -> float:
    """Fetch the latest USD/IQD rate from Telegram PMC market."""
    if not API_ID or not API_HASH or not STRING_SESSION:
        raise RuntimeError("Missing Telegram credentials")

    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        client.connect()
        if not client.is_user_authorized():
            raise RuntimeError("Telegram session is not authorized")

        messages = client.get_messages(CHAT_ID, limit=1)
        if not messages:
            raise RuntimeError("No messages found in PMC market channel")

        message_text = messages[0].text
        rate = extract_rate_from_message(message_text)
        if rate is None:
            raise RuntimeError(f"Could not extract rate from message: {message_text}")
        return rate
    except Exception as e:
        raise RuntimeError(f"Failed to fetch PMC rate: {e}") from e
    finally:
        client.disconnect()


def get_fx_rates() -> dict:
    """Fetch foreign exchange rates against USD."""
    last_error = None
    for endpoint in FX_ENDPOINTS:
        try:
            response = requests.get(endpoint, timeout=15)
            response.raise_for_status()
            data = response.json()
            if "rates" not in data:
                raise RuntimeError("Missing 'rates' in provider payload")
            rates = {}
            for currency in CURRENCIES:
                if currency not in data["rates"]:
                    raise RuntimeError(f"Missing rate for {currency}")
                rates[currency] = data["rates"][currency]
            return rates
        except Exception as exc:
            last_error = exc
            continue
    raise RuntimeError(f"Failed to fetch FX rates from all providers: {last_error}")


def build_row(usd_rate: float, fx_rates: dict) -> dict:
    """Build a data row with USD rate and calculated currency rates."""
    market_price = round(usd_rate * 100, 0)
    spread = 250

    row = {
        "Time": datetime.now(IRAQ_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "USD": round(usd_rate, 2),
        "Market": market_price,
        "Buy": market_price + spread,
        "Sell": market_price - spread,
    }

    for currency in CURRENCIES:
        row[currency] = round(usd_rate / float(fx_rates[currency]), 2)

    return row


def get_last_usd_rate_from_csv() -> float | None:
    """Get the last USD rate from CSV as fallback."""
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
    """Append a new row to the CSV file."""
    columns = [
        "Time",
        "USD",
        "EUR",
        "GBP",
        "TRY",
        "AED",
        "SAR",
        "KWD",
        "Market",
        "Buy",
        "Sell",
    ]

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=columns)

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df = df[columns]

    if len(df) > MAX_ROWS:
        df = df.tail(MAX_ROWS).reset_index(drop=True)

    df.to_csv(CSV_FILE, index=False)

    print("CSV updated successfully")
    print(new_row)


if __name__ == "__main__":
    try:
        usd_rate = get_latest_pmc_rate()
    except Exception as exc:
        fallback = get_last_usd_rate_from_csv()
        if fallback is None:
            raise
        print(
            f"Warning: failed to read Telegram rate ({exc}). "
            f"Using last known USD rate: {fallback}"
        )
        usd_rate = fallback

    fx_rates = get_fx_rates()
    row = build_row(usd_rate, fx_rates)
    update_csv(row)
