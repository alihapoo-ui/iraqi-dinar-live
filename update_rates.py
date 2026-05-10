from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import pandas as pd
import requests
import re
import os
from datetime import datetime

# =========================
# TELEGRAM LOGIN
# =========================

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
string_session = os.environ["STRING_SESSION"]

client = TelegramClient(
    StringSession(string_session),
    api_id,
    api_hash
)

client.connect()

print("Telegram connected successfully")

# =========================
# GET PMC GROUP MESSAGES
# =========================

channel = "PMCgroup"

messages = client.get_messages(channel, limit=20)

usd_rate = None

for msg in messages:

    text = msg.message

    if not text:
        continue

    match = re.search(r'100\$[\s:=\-]*([\d,]+)', text)

    if match:

        value = match.group(1).replace(",", "")

        usd_rate = float(value) / 100

        print("USD RATE FOUND:", usd_rate)

        break

# =========================
# FALLBACK IF NO RATE
# =========================

if usd_rate is None:

    print("No USD rate found from PMC")

    usd_rate = 1530

# =========================
# GET LIVE FOREX DATA
# =========================

url = "https://open.er-api.com/v6/latest/USD"

response = requests.get(url)

data = response.json()

rates = data["rates"]

# =========================
# CALCULATE IQD VALUES
# =========================

eur_iqd = round(usd_rate * rates["EUR"], 2)
gbp_iqd = round(usd_rate * rates["GBP"], 2)
try_iqd = round(usd_rate * rates["TRY"], 2)
aed_iqd = round(usd_rate * rates["AED"], 2)
sar_iqd = round(usd_rate * rates["SAR"], 2)
kwd_iqd = round(usd_rate * rates["KWD"], 2)

# =========================
# MARKET BUY/SELL
# =========================

market_price = usd_rate * 100
buy_price = market_price + 250
sell_price = market_price - 250

# =========================
# CREATE DATA ROW
# =========================

new_row = {
    "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "USD": usd_rate,
    "EUR": eur_iqd,
    "GBP": gbp_iqd,
    "TRY": try_iqd,
    "AED": aed_iqd,
    "SAR": sar_iqd,
    "KWD": kwd_iqd,
    "Market": market_price,
    "Buy": buy_price,
    "Sell": sell_price
}

# =========================
# SAVE CSV
# =========================

csv_file = "usd_history.csv"

if os.path.exists(csv_file):

    df = pd.read_csv(csv_file)

else:

    df = pd.DataFrame()

df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

df.to_csv(csv_file, index=False)

print("CSV updated successfully")

# =========================
# DISCONNECT
# =========================

client.disconnect()

print("Finished successfully")
