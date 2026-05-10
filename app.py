import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="IQD Live Engine",
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

# =========================
# LATEST VALUES
# =========================

latest_usd = df["USD"].iloc[-1]
latest_market = df["Market"].iloc[-1]
latest_buy = df["Buy"].iloc[-1]
latest_sell = df["Sell"].iloc[-1]
latest_time = df["Time"].iloc[-1]

# =========================
# MARKET CHANGE
# =========================

if len(df) >= 2:
    market_change = df["Market"].iloc[-1] - df["Market"].iloc[-2]
else:
    market_change = 0

if market_change > 0:
    trend_label = "Bullish"
    trend_icon = "▲"
    trend_class = "trend-up"
    trend_message = f"+{market_change:,.0f} IQD"
elif market_change < 0:
    trend_label = "Bearish"
    trend_icon = "▼"
    trend_class = "trend-down"
    trend_message = f"{market_change:,.0f} IQD"
else:
    trend_label = "Neutral"
    trend_icon = "●"
    trend_class = "trend-neutral"
    trend_message = "No change"

# =========================
# STYLE
# =========================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(34, 197, 94, 0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(59, 130, 246, 0.14), transparent 30%),
        linear-gradient(135deg, #070B12 0%, #0E1117 45%, #111827 100%);
    color: #F8FAFC;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1220 0%, #111827 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: #E5E7EB;
}

.block-container {
    padding-top: 2.2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

h1, h2, h3 {
    color: #F8FAFC;
    letter-spacing: -0.03em;
}

div[data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.96), rgba(15, 23, 42, 0.98));
    border: 1px solid rgba(148, 163, 184, 0.18);
    padding: 20px;
    border-radius: 22px;
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.28);
}

div[data-testid="metric-container"] label {
    color: #94A3B8 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #F8FAFC !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
}

.modern-card {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.72));
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 26px;
    padding: 26px;
    box-shadow: 0 22px 60px rgba(0, 0, 0, 0.30);
    margin-bottom: 22px;
}

.hero-card {
    background:
        linear-gradient(135deg, rgba(34,197,94,0.20), rgba(59,130,246,0.14)),
        linear-gradient(145deg, #0F172A, #111827);
    border: 1px solid rgba(34,197,94,0.28);
    border-radius: 32px;
    padding: 34px;
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.38);
    margin-bottom: 26px;
}

.hero-title {
    font-size: 3rem;
    font-weight: 900;
    color: #FFFFFF;
    margin-bottom: 8px;
    letter-spacing: -0.05em;
}

.hero-subtitle {
    color: #CBD5E1;
    font-size: 1rem;
    margin-bottom: 26px;
}

.hero-price {
    font-size: 4rem;
    font-weight: 900;
    color: #22C55E;
    line-height: 1;
    letter-spacing: -0.06em;
}

.hero-caption {
    color: #94A3B8;
    font-size: 0.95rem;
    margin-top: 10px;
}

.ticker {
    background: rgba(2, 6, 23, 0.70);
    border: 1px solid rgba(34,197,94,0.25);
    color: #22C55E;
    padding: 13px 18px;
    border-radius: 18px;
    font-size: 1.05rem;
    font-weight: 800;
    margin: 18px 0 26px 0;
    box-shadow: inset 0 0 28px rgba(34,197,94,0.08);
}

.pill {
    display: inline-block;
    padding: 9px 14px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 800;
    margin-right: 8px;
}

.pill-green {
    background: rgba(34,197,94,0.16);
    color: #22C55E;
    border: 1px solid rgba(34,197,94,0.28);
}

.pill-blue {
    background: rgba(59,130,246,0.16);
    color: #60A5FA;
    border: 1px solid rgba(59,130,246,0.28);
}

.pill-gray {
    background: rgba(148,163,184,0.13);
    color: #CBD5E1;
    border: 1px solid rgba(148,163,184,0.20);
}

.trend-up {
    background: rgba(34,197,94,0.16);
    color: #22C55E;
    border: 1px solid rgba(34,197,94,0.30);
}

.trend-down {
    background: rgba(239,68,68,0.16);
    color: #EF4444;
    border: 1px solid rgba(239,68,68,0.30);
}

.trend-neutral {
    background: rgba(245,158,11,0.16);
    color: #F59E0B;
    border: 1px solid rgba(245,158,11,0.30);
}

.trend-box {
    border-radius: 22px;
    padding: 20px 24px;
    font-size: 1.15rem;
    font-weight: 800;
    margin: 12px 0 22px 0;
}

.small-muted {
    color: #94A3B8;
    font-size: 0.92rem;
}

.footer-note {
    color: #64748B;
    font-size: 0.85rem;
    margin-top: 22px;
}

[data-testid="stDataFrame"] {
    border-radius: 20px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

st.sidebar.markdown("## 🇮🇶 IQD Live")
st.sidebar.markdown("Live market dashboard powered by Salar data.")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Historical Data",
        "Currency Converter"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Last update:**  \n{latest_time}")
st.sidebar.markdown("**Source:** PMCgroup")

# =========================
# TITLE + TICKER
# =========================

st.markdown("""
<div class="hero-card">
    <div class="hero-title">Iraqi Dinar Live Engine</div>
    <div class="hero-subtitle">
        Live Iraqi market exchange dashboard for USD/IQD and major foreign currencies.
    </div>
""", unsafe_allow_html=True)

h1, h2 = st.columns([2, 1])

with h1:
    st.markdown(
        f"""
        <div class="hero-price">{latest_market:,.0f}</div>
        <div class="hero-caption">IQD per 100 USD market reference</div>
        """,
        unsafe_allow_html=True
    )

with h2:
    st.markdown(
        f"""
        <span class="pill pill-green">PMC Live</span>
        <span class="pill pill-blue">Auto Refresh</span>
        <span class="pill pill-gray">FX Engine</span>
        <br><br>
        <div class="small-muted">Updated: {latest_time}</div>
        """,
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

ticker_text = (
    f"Market: {latest_market:,.0f} IQD   •   "
    f"Buy: {latest_buy:,.0f} IQD   •   "
    f"Sell: {latest_sell:,.0f} IQD   •   "
    f"USD: {latest_usd:,.2f}   •   "
    f"EUR: {df['EUR'].iloc[-1]:,.2f}   •   "
    f"GBP: {df['GBP'].iloc[-1]:,.2f}   •   "
    f"TRY: {df['TRY'].iloc[-1]:,.2f}"
)

st.markdown(
    f"""
    <div class="ticker">
        <marquee>{ticker_text}</marquee>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# DASHBOARD
# =========================

if page == "Dashboard":

    st.markdown("## Market Overview")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Market Price",
        f"{latest_market:,.0f} IQD",
        f"{market_change:,.0f} IQD"
    )

    c2.metric(
        "Buy USD",
        f"{latest_buy:,.0f} IQD"
    )

    c3.metric(
        "Sell USD",
        f"{latest_sell:,.0f} IQD"
    )

    st.markdown(
        f"""
        <div class="trend-box {trend_class}">
            {trend_icon} Market Trend: {trend_label} — {trend_message}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## Foreign Currency Rates")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("USD", f"{df['USD'].iloc[-1]:,.2f}")
    col2.metric("EUR", f"{df['EUR'].iloc[-1]:,.2f}")
    col3.metric("GBP", f"{df['GBP'].iloc[-1]:,.2f}")
    col4.metric("TRY", f"{df['TRY'].iloc[-1]:,.2f}")

    col5, col6, col7 = st.columns(3)

    col5.metric("AED", f"{df['AED'].iloc[-1]:,.2f}")
    col6.metric("SAR", f"{df['SAR'].iloc[-1]:,.2f}")
    col7.metric("KWD", f"{df['KWD'].iloc[-1]:,.2f}")

    st.markdown("## Market Statistics")

    highest_price = df["Market"].max()
    lowest_price = df["Market"].min()
    average_price = df["Market"].mean()

    s1, s2, s3 = st.columns(3)

    s1.metric("Highest Recorded", f"{highest_price:,.0f} IQD")
    s2.metric("Lowest Recorded", f"{lowest_price:,.0f} IQD")
    s3.metric("Average Market", f"{average_price:,.0f} IQD")

    st.markdown("## Market Chart")

    chart_type = st.selectbox(
        "Chart Type",
        [
            "Line",
            "Area"
        ]
    )

    chart_df = df[["Market"]].copy()

    if chart_type == "Line":
        st.line_chart(chart_df)
    else:
        st.area_chart(chart_df)

# =========================
# HISTORICAL DATA
# =========================

elif page == "Historical Data":

    st.markdown("## Historical Market Records")

    st.dataframe(
        df.tail(50),
        use_container_width=True
    )

    st.markdown("## Currency Chart")

    chart_currency = st.selectbox(
        "Select Currency",
        [
            "Market",
            "USD",
            "EUR",
            "GBP",
            "TRY",
            "AED",
            "SAR",
            "KWD"
        ]
    )

    st.line_chart(df[[chart_currency]])

# =========================
# CONVERTER
# =========================

elif page == "Currency Converter":

    st.markdown("## Currency Converter")

    st.markdown(
        """
        <div class="modern-card">
        <h3>Convert USD to Iraqi Dinar</h3>
        <p class="small-muted">Uses latest live market price per 100 USD.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    amount = st.number_input(
        "USD Amount",
        min_value=1.0,
        value=100.0,
        step=10.0
    )

    converted = amount * latest_usd

    st.success(
        f"{amount:,.2f} USD = {converted:,.0f} IQD"
    )

    st.markdown("## Quick Values")

    q1, q2, q3, q4 = st.columns(4)

    q1.metric("100 USD", f"{100 * latest_usd:,.0f} IQD")
    q2.metric("500 USD", f"{500 * latest_usd:,.0f} IQD")
    q3.metric("1,000 USD", f"{1000 * latest_usd:,.0f} IQD")
    q4.metric("5,000 USD", f"{5000 * latest_usd:,.0f} IQD")

st.markdown(
    """
    <div class="footer-note">
        Built for Iraqi market monitoring. Rates are based on available source data and may vary by exchange office.
    </div>
    """,
    unsafe_allow_html=True
)
