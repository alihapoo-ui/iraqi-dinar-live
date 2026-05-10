import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import altair as alt

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Iraqi Dinar Live",
    page_icon="🇮🇶",
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

df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
df = df.dropna(subset=["Time"])
df = df.sort_values("Time").reset_index(drop=True)

# =========================
# LATEST VALUES
# =========================

latest = df.iloc[-1]

latest_time = latest["Time"].strftime("%Y-%m-%d %H:%M:%S")
latest_usd = latest["USD"]
latest_market = latest["Market"]
latest_buy = latest["Buy"]
latest_sell = latest["Sell"]

if len(df) >= 2:
    previous_market = df["Market"].iloc[-2]
    market_change = latest_market - previous_market
else:
    market_change = 0

if market_change > 0:
    trend_text = f"▲ Market increased by {market_change:,.0f} IQD"
    trend_class = "good"
elif market_change < 0:
    trend_text = f"▼ Market decreased by {abs(market_change):,.0f} IQD"
    trend_class = "bad"
else:
    trend_text = "● Market is stable"
    trend_class = "neutral"

# =========================
# STYLE
# =========================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #F6F8FC;
    color: #0F172A;
}

.block-container {
    padding-top: 0rem;
    padding-left: 4rem;
    padding-right: 4rem;
    max-width: 1350px;
}

section[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E5E7EB;
}

section[data-testid="stSidebar"] * {
    color: #0F172A;
}

.hero {
    background: linear-gradient(135deg, #06145F 0%, #0B1F80 55%, #061B4D 100%);
    margin-left: -4rem;
    margin-right: -4rem;
    padding: 42px 4rem 130px 4rem;
    color: white;
    border-bottom-left-radius: 45% 8%;
    border-bottom-right-radius: 45% 8%;
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 55px;
}

.brand {
    font-size: 28px;
    font-weight: 900;
    letter-spacing: -0.04em;
}

.navlinks span {
    margin-left: 28px;
    font-size: 15px;
    font-weight: 700;
    color: #E0E7FF;
}

.hero-title {
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    letter-spacing: -0.05em;
    margin-bottom: 10px;
}

.hero-subtitle {
    text-align: center;
    font-size: 18px;
    color: #D8E4FF;
}

.converter-card {
    background: #FFFFFF;
    margin-top: -95px;
    border-radius: 28px;
    padding: 30px;
    box-shadow: 0 30px 70px rgba(15, 23, 42, 0.16);
    border: 1px solid #E5E7EB;
}

.card-tabs {
    display: flex;
    gap: 12px;
    margin-bottom: 25px;
}

.tab-active {
    background: #1E2A44;
    color: white;
    padding: 13px 45px;
    border-radius: 999px;
    font-weight: 800;
    font-size: 14px;
}

.tab-muted {
    background: #F1F5F9;
    color: #64748B;
    padding: 13px 45px;
    border-radius: 999px;
    font-weight: 800;
    font-size: 14px;
}

.converter-box {
    border: 1px solid #E5E7EB;
    border-radius: 18px;
    padding: 20px;
    background: #FBFDFF;
}

.converter-label {
    font-size: 13px;
    font-weight: 700;
    color: #64748B;
    margin-bottom: 6px;
}

.converter-value {
    font-size: 34px;
    font-weight: 900;
    color: #0F172A;
    letter-spacing: -0.04em;
}

.rate-line {
    margin-top: 22px;
    font-size: 24px;
    font-weight: 900;
    color: #0F2B66;
}

.rate-note {
    font-size: 14px;
    color: #64748B;
    margin-top: 5px;
}

.primary-button {
    background: #0B74E5;
    color: white;
    border-radius: 10px;
    padding: 15px 22px;
    text-align: center;
    font-weight: 900;
    margin-top: 28px;
}

.secondary-button {
    background: #EEF5FF;
    color: #0B74E5;
    border-radius: 10px;
    padding: 15px 22px;
    text-align: center;
    font-weight: 900;
    margin-top: 28px;
}

.section-title {
    font-size: 28px;
    font-weight: 900;
    letter-spacing: -0.04em;
    color: #0F172A;
    margin-top: 38px;
    margin-bottom: 18px;
}

div[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 22px;
    padding: 22px;
    box-shadow: 0 14px 35px rgba(15, 23, 42, 0.07);
}

div[data-testid="metric-container"] label {
    color: #64748B !important;
    font-weight: 800 !important;
    font-size: 0.82rem !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #0F172A !important;
    font-weight: 900 !important;
    font-size: 2rem !important;
}

.trend-card {
    padding: 18px 22px;
    border-radius: 18px;
    font-weight: 900;
    margin: 18px 0 28px 0;
}

.good {
    background: #E8F9EF;
    color: #0F9F4D;
    border: 1px solid #B8EBCB;
}

.bad {
    background: #FEECEC;
    color: #D92828;
    border: 1px solid #F7B8B8;
}

.neutral {
    background: #FFF7E6;
    color: #C47A00;
    border: 1px solid #F4D38B;
}

.chart-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 14px 35px rgba(15, 23, 42, 0.07);
    margin-top: 12px;
}

.footer {
    color: #64748B;
    font-size: 13px;
    margin-top: 35px;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

st.sidebar.markdown("## 🇮🇶 IQD Live")
st.sidebar.markdown("Live Iraqi market rates powered by PMCgroup.")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Historical Data", "Currency Converter"]
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Last update:**  \n{latest_time}")
st.sidebar.markdown("**Source:** PMCgroup")

# =========================
# HERO
# =========================

st.markdown(
    """
    <div class="hero">
        <div class="navbar">
            <div class="brand">IQD Live</div>
            <div class="navlinks">
                <span>Personal</span>
                <span>Business</span>
                <span>Charts</span>
                <span>Alerts</span>
            </div>
        </div>
        <div class="hero-title">Iraqi Dinar live exchange rates</div>
        <div class="hero-subtitle">
            Real Iraqi market USD/IQD data, buy/sell prices, charts, and currency conversion.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# CONVERTER CARD
# =========================

st.markdown('<div class="converter-card">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="card-tabs">
        <div class="tab-active">Convert</div>
        <div class="tab-muted">Rates</div>
        <div class="tab-muted">Charts</div>
        <div class="tab-muted">Alerts</div>
    </div>
    """,
    unsafe_allow_html=True
)

left, right = st.columns(2)

with left:
    st.markdown(
        f"""
        <div class="converter-box">
            <div class="converter-label">From</div>
            <div class="converter-value">$100.00 USD</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with right:
    st.markdown(
        f"""
        <div class="converter-box">
            <div class="converter-label">To</div>
            <div class="converter-value">{latest_market:,.0f} IQD</div>
        </div>
        """,
        unsafe_allow_html=True
    )

b1, b2 = st.columns([2, 1])

with b1:
    st.markdown(
        f"""
        <div class="rate-line">100 USD = {latest_market:,.0f} IQD</div>
        <div class="rate-note">
            Market reference rate from PMCgroup • Updated {latest_time}
        </div>
        """,
        unsafe_allow_html=True
    )

with b2:
    st.markdown('<div class="primary-button">Track exchange rates</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# DASHBOARD
# =========================

if page == "Dashboard":

    st.markdown('<div class="section-title">Market Overview</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    c1.metric("Market Price", f"{latest_market:,.0f} IQD", f"{market_change:,.0f} IQD")
    c2.metric("Buy USD", f"{latest_buy:,.0f} IQD")
    c3.metric("Sell USD", f"{latest_sell:,.0f} IQD")

    st.markdown(
        f"""
        <div class="trend-card {trend_class}">
            {trend_text}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-title">Foreign Currency Rates</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("USD", f"{df['USD'].iloc[-1]:,.2f}")
    col2.metric("EUR", f"{df['EUR'].iloc[-1]:,.2f}")
    col3.metric("GBP", f"{df['GBP'].iloc[-1]:,.2f}")
    col4.metric("TRY", f"{df['TRY'].iloc[-1]:,.2f}")

    col5, col6, col7 = st.columns(3)

    col5.metric("AED", f"{df['AED'].iloc[-1]:,.2f}")
    col6.metric("SAR", f"{df['SAR'].iloc[-1]:,.2f}")
    col7.metric("KWD", f"{df['KWD'].iloc[-1]:,.2f}")

    st.markdown('<div class="section-title">Market Statistics</div>', unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)

    s1.metric("Highest Recorded", f"{df['Market'].max():,.0f} IQD")
    s2.metric("Lowest Recorded", f"{df['Market'].min():,.0f} IQD")
    s3.metric("Average Market", f"{df['Market'].mean():,.0f} IQD")

    st.markdown('<div class="section-title">Market Chart</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    chart_data = df.tail(500).copy()

    chart = (
        alt.Chart(chart_data)
        .mark_line(color="#0B74E5", strokeWidth=3)
        .encode(
            x=alt.X("Time:T", title="Time"),
            y=alt.Y("Market:Q", title="IQD per 100 USD", scale=alt.Scale(zero=False)),
            tooltip=[
                alt.Tooltip("Time:T", title="Time"),
                alt.Tooltip("Market:Q", title="Market", format=",.0f"),
                alt.Tooltip("Buy:Q", title="Buy", format=",.0f"),
                alt.Tooltip("Sell:Q", title="Sell", format=",.0f"),
            ],
        )
        .properties(height=380)
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# HISTORICAL DATA
# =========================

elif page == "Historical Data":

    st.markdown('<div class="section-title">Historical Market Records</div>', unsafe_allow_html=True)

    st.dataframe(df.tail(100), use_container_width=True)

    st.markdown('<div class="section-title">Currency Chart</div>', unsafe_allow_html=True)

    chart_currency = st.selectbox(
        "Select Currency",
        ["Market", "USD", "EUR", "GBP", "TRY", "AED", "SAR", "KWD"]
    )

    chart_data = df.tail(500).copy()

    chart = (
        alt.Chart(chart_data)
        .mark_line(color="#0B74E5", strokeWidth=3)
        .encode(
            x=alt.X("Time:T", title="Time"),
            y=alt.Y(f"{chart_currency}:Q", title=chart_currency, scale=alt.Scale(zero=False)),
            tooltip=[
                alt.Tooltip("Time:T", title="Time"),
                alt.Tooltip(f"{chart_currency}:Q", title=chart_currency, format=",.2f"),
            ],
        )
        .properties(height=380)
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)

# =========================
# CURRENCY CONVERTER
# =========================

elif page == "Currency Converter":

    st.markdown('<div class="section-title">Currency Converter</div>', unsafe_allow_html=True)

    amount = st.number_input("Amount", min_value=1.0, value=100.0, step=10.0)

    currency = st.selectbox(
        "From Currency",
        ["USD", "EUR", "GBP", "TRY", "AED", "SAR", "KWD"]
    )

    converted = amount * df[currency].iloc[-1]

    st.metric(
        "Converted Value",
        f"{converted:,.0f} IQD"
    )

    q1, q2, q3, q4 = st.columns(4)

    q1.metric("100 USD", f"{100 * latest_usd:,.0f} IQD")
    q2.metric("500 USD", f"{500 * latest_usd:,.0f} IQD")
    q3.metric("1,000 USD", f"{1000 * latest_usd:,.0f} IQD")
    q4.metric("5,000 USD", f"{5000 * latest_usd:,.0f} IQD")

st.markdown(
    """
    <div class="footer">
        Built for Iraqi market monitoring. Rates may vary by exchange office and source timing.
    </div>
    """,
    unsafe_allow_html=True
)
