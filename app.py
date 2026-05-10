import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="IQD Live Engine",
    layout="wide"
)

# =========================
# AUTO REFRESH
# =========================

st_autorefresh(interval=60000, key="refresh")

# =========================
# LOAD DATA
# =========================

df = pd.read_csv("usd_history.csv")

# =========================
# LATEST VALUES
# =========================

latest_usd = df["USD"].iloc[-1]
latest_market = df["Market"].iloc[-1]
latest_buy = df["Buy"].iloc[-1]
latest_sell = df["Sell"].iloc[-1]

# =========================
# PAGE STYLE
# =========================

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
    border-radius: 15px;
}

h1, h2, h3 {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================

st.title("🇮🇶 Iraqi Dinar Live Engine")

# =========================
# LIVE TICKER
# =========================

ticker_text = f"""
Market: {latest_market:,.0f} IQD |
Buy: {latest_buy:,.0f} IQD |
Sell: {latest_sell:,.0f} IQD
"""

st.markdown(
    f"""
    <marquee style='
        color:lime;
        font-size:22px;
        font-weight:bold;
    '>
    {ticker_text}
    </marquee>
    """,
    unsafe_allow_html=True
)

# =========================
# SIDEBAR
# =========================

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Historical Data",
        "Currency Converter"
    ]
)

# =========================
# DASHBOARD
# =========================

if page == "Dashboard":

    st.subheader("USD IQD Market")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Market Price",
        f"{latest_market:,.0f} IQD"
    )

    c2.metric(
        "Buy USD",
        f"{latest_buy:,.0f} IQD"
    )

    c3.metric(
        "Sell USD",
        f"{latest_sell:,.0f} IQD"
    )

    # =========================
    # FOREIGN CURRENCY RATES
    # =========================

    st.subheader("Foreign Currency Rates")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("USD", df["USD"].iloc[-1])
    col2.metric("EUR", df["EUR"].iloc[-1])
    col3.metric("GBP", df["GBP"].iloc[-1])
    col4.metric("TRY", df["TRY"].iloc[-1])

    col5, col6, col7 = st.columns(3)

    col5.metric("AED", df["AED"].iloc[-1])
    col6.metric("SAR", df["SAR"].iloc[-1])
    col7.metric("KWD", df["KWD"].iloc[-1])

    # =========================
    # MARKET TREND
    # =========================

    st.subheader("Market Trend")

    if len(df) >= 2:

        latest_change = (
            df["Market"].iloc[-1]
            - df["Market"].iloc[-2]
        )

        if latest_change > 0:

            st.success(
                f"🟢 Bullish Market (+{latest_change:,.0f} IQD)"
            )

        elif latest_change < 0:

            st.error(
                f"🔴 Bearish Market ({latest_change:,.0f} IQD)"
            )

        else:

            st.warning(
                "🟡 Neutral Market"
            )

    # =========================
    # HIGH / LOW
    # =========================

    highest_price = df["Market"].max()
    lowest_price = df["Market"].min()

    h1, h2 = st.columns(2)

    h1.metric(
        "Highest Recorded",
        f"{highest_price:,.0f} IQD"
    )

    h2.metric(
        "Lowest Recorded",
        f"{lowest_price:,.0f} IQD"
    )

    # =========================
    # CHART
    # =========================

    st.subheader("USD Historical Chart")

    chart_type = st.selectbox(
        "Chart Type",
        [
            "Line",
            "Area"
        ]
    )

    if chart_type == "Line":

        st.line_chart(df["Market"])

    else:

        st.area_chart(df["Market"])

# =========================
# HISTORICAL DATA
# =========================

elif page == "Historical Data":

    st.subheader("Latest Market Records")

    st.dataframe(df.tail(20))

# =========================
# CONVERTER
# =========================

elif page == "Currency Converter":

    st.subheader("Currency Converter")

    amount = st.number_input(
        "USD Amount",
        min_value=1.0,
        value=100.0
    )

    converted = amount * latest_market

    st.success(
        f"{amount} USD = {converted:,.0f} IQD"
    )
