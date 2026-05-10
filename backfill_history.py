from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd
import requests
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

CHANNEL = "PMCgroup"
CSV_FILE = "usd_history.csv"
IRAQ_TZ = ZoneInfo("Asia/Baghdad")
CURRENCIES = ["EUR", "GBP", "TRY", "AED", "SAR", "KWD"]

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
STRING_SESSION = os.environ["STRING_SESSION"]


def extract_usd_iqd(text: str) -> float | None:
    patterns = [
        r"100\s*\$\s*[=:：\-]?\s*([0-9]{2,3}(?:,[0-9]{3})+|[0-9]{5,6})",
        r"100\s*دولار\s*[=:：\-]?\s*([0-9]{2,3}(?:,[0-9]{3})+|[0-9]{5,6})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        market_per_100 = float(match.group(1).replace(",", ""))
        if 100000 <= market_per_100 <= 250000:
            return market_per_100 / 100
    return None


def get_fx_rates() -> dict:
    response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=20)
    response.raise_for_status()
    data = response.json()
    return data["rates"]


fx_rates = get_fx_rates()
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
client.connect()

if not client.is_user_authorized():
    client.disconnect()
    raise RuntimeError("Telegram session is not authorized. Regenerate STRING_SESSION.")

start_date = datetime.now(timezone.utc) - timedelta(days=30)
records = []

try:
    for msg in client.iter_messages(CHANNEL, limit=5000):
        if msg.date < start_date:
            break
        if not msg.message:
            continue

        usd_rate = extract_usd_iqd(msg.message)
        if usd_rate is None:
            continue

        market_price = round(usd_rate * 100, 0)
        row = {
            "Time": msg.date.astimezone(IRAQ_TZ).strftime("%Y-%m-%d %H:%M:%S"),
            "USD": round(usd_rate, 2),
            "Market": market_price,
            "Buy": market_price + 250,
            "Sell": market_price - 250,
        }

        for currency in CURRENCIES:
            row[currency] = round(usd_rate / float(fx_rates[currency]), 2)

        records.append(row)
finally:
    client.disconnect()

if not records:
    raise RuntimeError("No records found for the last 30 days.")

df = pd.DataFrame(records).iloc[::-1].reset_index(drop=True)
df = df[["Time", "USD", "EUR", "GBP", "TRY", "AED", "SAR", "KWD", "Market", "Buy", "Sell"]]
df.to_csv(CSV_FILE, index=False)
print(f"Backfill completed. Saved {len(df)} rows.")
