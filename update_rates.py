from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import pandas as pd
import requests
import re
from datetime import datetime
import os

api_id = int(os.environ["37665414"])

api_hash = os.environ["0ed2ccc8cd3f95cfd2cbd5feb2749ea7"]

string_session = os.environ["1ApWapzMBu8Crl8f0DyagRo9LgNi9LvN7wWkAWMHRPrI9HFhvIMYCK5ZGzLCkROayMSKdl3mPPxT5emlfe2rLAF4wWfdnJ8BvF8qK6MaR6XyzAqm2fwk0LF8eGin0kCbiqx-0MM3GJjtj1FseKezXKE49465rgVqbh8HO7Ra918Saig18MKZhGyCNbshsoOXvGid4FvK6FtDa7sbfwZaGwdkVIvEHOfdU-zm9DGyezUmli8mAxbBieu_K3mmxlO9ORV2MaKSRpN7UyHr7jCsO1QRww26E3sSCaYll-Kzkxr24dXinxZsvmMcPBL-Af-UHuEQk36aoV_xMuyCfSpbDO71fI6eQUVQ="]

client = TelegramClient(
    StringSession(string_session),
    api_id,
    api_hash
)

client.connect()

channel = "PMCgroup"

messages = client.get_messages(channel, limit=20)

usd_iqd = None

for msg in messages:

    text = msg.message

    if not text:
        continue

    match = re.search(r'100\$\s*=\s*([\d,]+)', text)

    if match:

        value = match.group(1).replace(',', '')

        usd_iqd = int(value) / 100

        break

if usd_iqd:

    url = "https://open.er-api.com/v6/latest/USD"

    response = requests.get(url)

    data = response.json()

    rates = data["rates"]

    results = {
        "USD": usd_iqd
    }

    currencies = [
        "EUR",
        "GBP",
        "TRY",
        "AED",
        "SAR",
        "KWD"
    ]

    for currency in currencies:

        rate_vs_usd = rates[currency]

        currency_iqd = usd_iqd / rate_vs_usd

        results[currency] = round(currency_iqd, 2)

    market = usd_iqd * 100
    buy = market + 500
    sell = market - 250

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    new_row = {
        "Time": current_time,
        "USD": results["USD"],
        "EUR": results["EUR"],
        "GBP": results["GBP"],
        "TRY": results["TRY"],
        "AED": results["AED"],
        "SAR": results["SAR"],
        "KWD": results["KWD"],
        "Market": market,
        "Buy": buy,
        "Sell": sell
    }

    if os.path.exists("usd_history.csv"):

        df = pd.read_csv("usd_history.csv")

        df = pd.concat(
            [df, pd.DataFrame([new_row])],
            ignore_index=True
        )

    else:

        df = pd.DataFrame([new_row])

    df.to_csv("usd_history.csv", index=False)

    print("CSV Updated Successfully")

else:

    print("USD rate not found")

client.disconnect()
