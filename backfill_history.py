from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import pandas as pd
import requests
import re
import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# =========================
# GITHUB SECRETS
# =========================

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
string_session = os.environ["STRING_SESSION"]

# =========================
# TELEGRAM CLIENT
# =========================

client = TelegramClient(
    StringSession(string_session),
    api_id,
    api_hash
)

client.connect()

channel = "PMCgroup"

# =========================
# DATE RANGE
# =========================

iraq_tz = ZoneInfo("Asia/Baghdad")

now_utc = datetime.now(timezone.utc)
start_date_utc = now_utc - timedelta(days=30)

# =========================
# GET CURRENT FX RATES
# =========================

url = "https://open.er-api.com/v6/latest/USD"
response = requests.get(url)
data = response.json()
rates = data["rates"]

currencies = ["EUR", "GBP", "TRY", "AED", "SAR", "KWD"]

records = []

# =========================
# READ LAST MONTH TELEGRAM HISTORY
# =========================

for msg in client.iter_messages(channel, limit=3000):

    if not msg.message:
        continue

    if msg.date < start_date_utc:
        break

    text = msg.message

    match = re.search(r'100\$\s*=\s*([\d,]+)', text)

    if not match:
        continue

    value = match.group(1).replace(",", "")

    usd_iqd = float(value) / 100

    msg_time_iraq = msg.date.astimezone(iraq_tz).strftime("%Y-%m-%d %H:%M:%S")

    result = {
        "Time": msg_time_iraq,
        "USD": usd_iqd,
        "Market": usd_iqd * 100,
        "Buy": (usd_iqd * 100) + 250,
        "Sell": (usd_iqd * 100) - 250
    }

    # Correct formula:
    # API gives foreign currency per 1 USD
    # so we divide USD/IQD by that rate
    for currency in currencies:
        result[currency] = round(usd_iqd / rates[currency], 2)

    records.append(result)

client.disconnect()

# =========================
# SAVE HISTORY
# =========================

if not records:
    print("No rates found in last 30 days.")
else:
    df = pd.DataFrame(records)

    # Telegram returns newest first, so reverse to oldest first
    df = df.iloc[::-1].reset_index(drop=True)

    df = df[
        [
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
            "Sell"
        ]
    ]

    df.to_csv("usd_history.csv", index=False)

    print(f"Backfill completed. Records saved: {len(df)}")
