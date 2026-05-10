from telethon.sync import TelegramClient
from telethon.sessions import StringSession

import pandas as pd
import requests
import re
from datetime import datetime
import os

# =========================================
# GITHUB SECRETS
# =========================================

api_id = int(os.environ["37665414"])

api_hash = os.environ["0ed2ccc8cd3f95cfd2cbd5feb2749ea7"]

string_session = os.environ["1ApWapzMBu1ac2L3vV_qCsviYiFAmNG1o54k427H55ULHuwbMuVOX8aqEtCsjAQDD6y-fz2sv7nZBNWW8COdYeC-_SnkSDUxcx6JBMOhII4JMG3yDv-pAIjL5LWRlZ8Afe9fugCzVqMUtNnY6LgJgI1E_5sRl1ZHiASI5iNTDRaHm9Z2kp59J-eIm5NPmtLa76lU46EZ3BouWixyUKMjKwtCPCAKGDzDyomCwYeAV9YUOuLW55_VGqSv2HNtq9y99wqoTLDuSE8ZyvZipqkRM7qL27IelP7k2kWEa48uwGV5Cj1-i4VaHAr1v3l6Wir_lv_mA4iJrce-AVmUoIJcN6LWJwIOaMEQ="]

# =========================================
# TELEGRAM CLIENT
# =========================================

client = TelegramClient(
    StringSession(string_session),
    api_id,
    api_hash
)

channel = "PMCgroup"

client.connect()

# =========================================
# FETCH TELEGRAM MESSAGES
# =========================================

messages = client.get_messages(
    channel,
    limit=20
)

usd_iqd = None

for msg in messages:

    text = msg.message

    if not text:
        continue

    match = re.search(
        r'100\$\s*=\s*([\d,]+)',
        text
    )

    if match:

        value = match.group(1).replace(',', '')

        usd_iqd = int(value) / 100

        break

# =========================================
# FETCH FX API
# =========================================

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

        results[currency] = round(
            currency_iqd,
            2
        )

    # =====================================
    # IRAQI MARKET LOGIC
    # =====================================

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

    # =====================================
    # UPDATE CSV
    # =====================================

    if os.path.exists("usd_history.csv"):

        df = pd.read_csv("usd_history.csv")

        df = pd.concat(
            [df, pd.DataFrame([new_row])],
            ignore_index=True
        )

    else:

        df = pd.DataFrame([new_row])

    df.to_csv(
        "usd_history.csv",
        index=False
    )

    print("CSV Updated Successfully")

else:

    print("USD/IQD rate not found.")

# =========================================
# DISCONNECT CLIENT
# =========================================

client.disconnect()
