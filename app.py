
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd

st.set_page_config(page_title="IQD Live Engine", layout="wide")
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: white;
    }

    div[data-testid="metric-container"] {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 12px;
    }

    h1, h2, h3 {
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🇮🇶 Iraqi Dinar Live Exchange Rates")
ticker_text = f"""
USD: {df['USD'].iloc[-1]} |
EUR: {df['EUR'].iloc[-1]} |
GBP: {df['GBP'].iloc[-1]} |
TRY: {df['TRY'].iloc[-1]} |
AED: {df['AED'].iloc[-1]} |
SAR: {df['SAR'].iloc[-1]} |
KWD: {df['KWD'].iloc[-1]}
"""

st.markdown(
    f"""
    <marquee style='color:lime;
                     font-size:22px;
                     font-weight:bold;'>
        {ticker_text}
    </marquee>
    """,
    unsafe_allow_html=True
)
page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Historical Data",
        "Currency Converter"
    ]
)
st_autorefresh(interval=60000, key="refresh")

# Read CSV
df = pd.read_csv("usd_history.csv")

latest_usd = df["USD"].iloc[-1]
market_price = df["Market"].iloc[-1]
buy_price = df["Buy"].iloc[-1]
sell_price = df["Sell"].iloc[-1]
cbi_rate = 1320

market_difference = round(latest_usd - cbi_rate, 2)

if page == "Dashboard":

st.subheader("Live Exchange Rates")

col1, col2, col3, col4 = st.columns(4)

usd_change = round(df["USD"].iloc[-1] - df["USD"].iloc[-2], 2)
eur_change = round(df["EUR"].iloc[-1] - df["EUR"].iloc[-2], 2)
gbp_change = round(df["GBP"].iloc[-1] - df["GBP"].iloc[-2], 2)
try_change = round(df["TRY"].iloc[-1] - df["TRY"].iloc[-2], 2)

aed_change = round(df["AED"].iloc[-1] - df["AED"].iloc[-2], 2)
sar_change = round(df["SAR"].iloc[-1] - df["SAR"].iloc[-2], 2)
kwd_change = round(df["KWD"].iloc[-1] - df["KWD"].iloc[-2], 2)

col1.metric("USD", df["USD"].iloc[-1], usd_change)
col2.metric("EUR", df["EUR"].iloc[-1], eur_change)
col3.metric("GBP", df["GBP"].iloc[-1], gbp_change)
col4.metric("TRY", df["TRY"].iloc[-1], try_change)

col5.metric("AED", df["AED"].iloc[-1], aed_change)
col6.metric("SAR", df["SAR"].iloc[-1], sar_change)
col7.metric("KWD", df["KWD"].iloc[-1], kwd_change)

st.subheader("CBI Official Comparison")

c1, c2, c3 = st.columns(3)

c1.metric("Market USD", latest_usd)
c2.metric("CBI Official", cbi_rate)
c3.metric("Difference", market_difference)

st.subheader("Market Trend")

latest_change = usd_change

if latest_change > 0:
    st.success("🟢 USD Trend: Bullish")

elif latest_change < 0:
    st.error("🔴 USD Trend: Bearish")

else:
    st.warning("🟡 USD Trend: Neutral")
st.subheader("USD Historical Chart")
st.subheader("Latest Market Records")
if page == "Historical Data":
st.dataframe(df.tail(10))

chart_currency = st.selectbox(
    "Select Currency Chart",
    ["USD", "EUR", "GBP", "TRY", "AED", "SAR", "KWD"]
)

st.line_chart(df[chart_currency])
if page == "Currency Converter":
st.subheader("Currency Converter")

currency = st.selectbox(
    "Select Currency",
    ["USD", "EUR", "GBP", "TRY", "AED", "SAR", "KWD"]
)

amount = st.number_input("Enter Amount", min_value=1.0, value=100.0)

latest_rate = df[currency].iloc[-1]

converted_value = amount * latest_rate

st.success(f"{amount} {currency} = {round(converted_value, 2)} IQD")
st.subheader("USD Price Alert")

alert_price = st.number_input(
    "Alert me when USD exceeds:",
    value=1540.0
)

if latest_usd >= alert_price:

    st.error(f"🚨 ALERT: USD reached {latest_usd}")

else:

    st.success(f"USD still below alert price ({alert_price})")
