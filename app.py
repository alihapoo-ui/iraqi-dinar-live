import io
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Iraqi Dinar Live",
    page_icon="🇮🇶",
    layout="wide",
    initial_sidebar_state="expanded",
)

st_autorefresh(interval=60_000, key="iqd_auto_refresh")

# =====================================================
# CONSTANTS
# =====================================================

CURRENCIES = {
    "USD": {"flag": "🇺🇸", "name": "US Dollar", "unit": "per 1 USD"},
    "EUR": {"flag": "🇪🇺", "name": "Euro", "unit": "per 1 EUR"},
    "GBP": {"flag": "🇬🇧", "name": "British Pound", "unit": "per 1 GBP"},
    "TRY": {"flag": "🇹🇷", "name": "Turkish Lira", "unit": "per 1 TRY"},
    "AED": {"flag": "🇦🇪", "name": "UAE Dirham", "unit": "per 1 AED"},
    "SAR": {"flag": "🇸🇦", "name": "Saudi Riyal", "unit": "per 1 SAR"},
    "KWD": {"flag": "🇰🇼", "name": "Kuwaiti Dinar", "unit": "per 1 KWD"},
}

MARKET_COLUMNS = ["Time", "USD", "EUR", "GBP", "TRY", "AED", "SAR", "KWD", "Market", "Buy", "Sell"]

# =====================================================
# DATA
# =====================================================

@st.cache_data(ttl=55)
def load_data() -> pd.DataFrame:
    df = pd.read_csv("usd_history.csv")

    missing = [col for col in MARKET_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in usd_history.csv: {', '.join(missing)}")

    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")

    for col in MARKET_COLUMNS:
        if col != "Time":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Time", "USD", "Market", "Buy", "Sell"])
    df = df.sort_values("Time").drop_duplicates(subset=["Time"], keep="last").reset_index(drop=True)

    return df


def get_latest_valid_row(df: pd.DataFrame) -> pd.Series:
    """Avoid showing old bad FX rows as latest foreign rates."""
    valid = df.copy()

    checks = (
        valid["USD"].between(1000, 2500)
        & valid["Market"].between(100000, 250000)
        & valid["EUR"].between(500, 4000)
        & valid["GBP"].between(500, 5000)
        & valid["TRY"].between(1, 500)
        & valid["AED"].between(100, 1000)
        & valid["SAR"].between(100, 1000)
        & valid["KWD"].between(1000, 10000)
    )

    valid = valid[checks]
    if not valid.empty:
        return valid.iloc[-1]

    return df.iloc[-1]


def filter_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    if period == "24h":
        cutoff = df["Time"].max() - pd.Timedelta(hours=24)
    elif period == "7d":
        cutoff = df["Time"].max() - pd.Timedelta(days=7)
    elif period == "30d":
        cutoff = df["Time"].max() - pd.Timedelta(days=30)
    else:
        return df.copy()

    filtered = df[df["Time"] >= cutoff].copy()
    return filtered if not filtered.empty else df.copy()


@st.cache_data(ttl=55)
def to_csv_bytes(data: pd.DataFrame) -> bytes:
    return data.to_csv(index=False).encode("utf-8")


try:
    df = load_data()
except Exception as exc:
    st.error(f"Could not load usd_history.csv: {exc}")
    st.stop()

if df.empty:
    st.error("No market data found. Run the GitHub Actions update workflow first.")
    st.stop()

latest = get_latest_valid_row(df)
latest_time = latest["Time"].strftime("%Y-%m-%d %H:%M")
latest_market = float(latest["Market"])
latest_buy = float(latest["Buy"])
latest_sell = float(latest["Sell"])
latest_usd = float(latest["USD"])

if len(df) >= 2:
    previous_market = float(df["Market"].iloc[-2])
    market_change = latest_market - previous_market
else:
    market_change = 0.0

if market_change > 0:
    trend_label = f"Market up by {market_change:,.0f} IQD"
    trend_badge = "📈 Up"
    trend_class = "trend-up"
elif market_change < 0:
    trend_label = f"Market down by {abs(market_change):,.0f} IQD"
    trend_badge = "📉 Down"
    trend_class = "trend-down"
else:
    trend_label = "Market is stable"
    trend_badge = "● Stable"
    trend_class = "trend-neutral"

# =====================================================
# STYLE
# =====================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --iqd-blue: #07145f;
    --iqd-blue-2: #0b5fe8;
    --iqd-text: #13213c;
    --iqd-muted: #667085;
    --iqd-border: #e4eaf3;
    --iqd-bg: #f5f7fb;
    --iqd-card: #ffffff;
    --iqd-green: #12a05c;
    --iqd-red: #d92d20;
    --iqd-yellow: #b7791f;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: var(--iqd-bg);
    color: var(--iqd-text);
}

.block-container {
    padding-top: 0rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    max-width: 1320px !important;
}

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid var(--iqd-border);
}

section[data-testid="stSidebar"] * {
    color: var(--iqd-text) !important;
}

.hero {
    background: linear-gradient(135deg, #07145f 0%, #0b1f7a 60%, #081139 100%);
    margin-left: -3rem;
    margin-right: -3rem;
    padding: 28px 3rem 118px 3rem;
    color: #fff;
    position: relative;
    overflow: hidden;
}

.hero::before {
    content: "";
    position: absolute;
    width: 720px;
    height: 720px;
    border-radius: 999px;
    background: radial-gradient(circle, rgba(31,119,255,.22) 0%, rgba(31,119,255,.06) 42%, transparent 70%);
    right: -180px;
    top: -300px;
}

.hero::after {
    content: "";
    position: absolute;
    left: -10%;
    right: -10%;
    bottom: -76px;
    height: 135px;
    background: var(--iqd-bg);
    border-radius: 50% 50% 0 0;
}

.hero-inner {
    max-width: 1120px;
    margin: 0 auto;
    position: relative;
    z-index: 2;
}

.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 46px;
}

.brand {
    font-size: 28px;
    font-weight: 900;
    letter-spacing: -0.04em;
}

.navlinks span {
    margin-left: 26px;
    color: #e7eeff;
    font-weight: 800;
    font-size: 14px;
}

.hero-title {
    text-align: center;
    font-size: clamp(32px, 5vw, 54px);
    line-height: 1.05;
    font-weight: 900;
    letter-spacing: -0.06em;
    margin-bottom: 14px;
}

.hero-subtitle {
    text-align: center;
    color: #dbe7ff;
    font-size: 18px;
    font-weight: 500;
}

.live-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.18);
    color: #dbe7ff;
    font-weight: 800;
    font-size: 13px;
    margin-bottom: 18px;
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #22c55e;
    box-shadow: 0 0 0 5px rgba(34,197,94,.16);
}

.converter-card {
    background: #ffffff;
    border: 1px solid var(--iqd-border);
    border-radius: 30px;
    padding: 28px;
    margin-top: -78px;
    box-shadow: 0 30px 70px rgba(15, 23, 42, .14);
    position: relative;
    z-index: 10;
}

.card-title {
    font-size: 18px;
    font-weight: 900;
    color: var(--iqd-text);
    margin-bottom: 4px;
}

.card-subtitle {
    color: var(--iqd-muted);
    font-size: 13px;
    margin-bottom: 18px;
}

.section-title {
    color: var(--iqd-text);
    font-size: 28px;
    font-weight: 900;
    letter-spacing: -0.04em;
    margin: 38px 0 16px 0;
}

.small-note {
    color: var(--iqd-muted);
    font-size: 13px;
}

.big-result {
    color: #07145f;
    font-size: clamp(24px, 4vw, 36px);
    font-weight: 900;
    letter-spacing: -0.04em;
    margin-top: 12px;
}

.trend-card {
    padding: 16px 20px;
    border-radius: 18px;
    font-weight: 900;
    margin: 18px 0;
}

.trend-up {
    background: #e8f8ef;
    color: var(--iqd-green);
    border: 1px solid #b7ebce;
}

.trend-down {
    background: #fff1f0;
    color: var(--iqd-red);
    border: 1px solid #ffc9c4;
}

.trend-neutral {
    background: #fff8e6;
    color: var(--iqd-yellow);
    border: 1px solid #f6d98b;
}

.rate-card {
    background: #ffffff;
    border: 1px solid var(--iqd-border);
    border-radius: 18px;
    padding: 17px 20px;
    margin-bottom: 10px;
    box-shadow: 0 8px 20px rgba(15, 23, 42, .05);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.rate-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.flag {
    font-size: 28px;
}

.rate-name {
    font-weight: 900;
    color: var(--iqd-text);
}

.rate-code {
    font-size: 12px;
    color: var(--iqd-muted);
    font-weight: 700;
}

.rate-value {
    color: var(--iqd-blue-2);
    font-weight: 900;
    font-size: 18px;
    text-align: right;
}

.rate-unit {
    color: var(--iqd-muted);
    font-size: 12px;
    text-align: right;
}

.panel {
    background: #ffffff;
    border: 1px solid var(--iqd-border);
    border-radius: 22px;
    padding: 22px;
    box-shadow: 0 10px 26px rgba(15,23,42,.06);
}

.chart-card {
    background: #ffffff;
    border: 1px solid var(--iqd-border);
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 10px 26px rgba(15,23,42,.06);
}

.footer {
    text-align: center;
    color: var(--iqd-muted);
    font-size: 13px;
    padding: 44px 0 30px 0;
}

/* Streamlit widgets */
div[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid var(--iqd-border);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 10px 26px rgba(15,23,42,.06);
}

div[data-testid="metric-container"] label {
    color: var(--iqd-muted) !important;
    font-weight: 800 !important;
    text-transform: uppercase;
    letter-spacing: .04em;
    font-size: .78rem !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--iqd-text) !important;
    font-weight: 900 !important;
    font-size: 1.85rem !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #f8fafc;
    border: 1px solid var(--iqd-border);
    padding: 8px;
    border-radius: 999px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 999px;
    padding: 10px 20px;
    font-weight: 900;
}

.stTabs [aria-selected="true"] {
    background: #263a5f !important;
    color: #ffffff !important;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 12px !important;
    font-weight: 900 !important;
    border: 1px solid var(--iqd-border) !important;
}

.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    background: #0b74e5 !important;
    color: white !important;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .hero {
        margin-left: -1rem;
        margin-right: -1rem;
        padding: 24px 1rem 100px 1rem;
    }

    .navbar {
        display: block;
        text-align: center;
        margin-bottom: 30px;
    }

    .navlinks {
        display: none;
    }

    .converter-card {
        padding: 18px;
        border-radius: 22px;
    }

    .rate-card {
        display: block;
    }

    .rate-value,
    .rate-unit {
        text-align: left;
        margin-top: 8px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.markdown("## 🇮🇶 IQD Live")
st.sidebar.markdown("Live Iraqi market exchange rates powered by PMCgroup.")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Historical Data", "Currency Converter"],
    key="main_navigation",
)

st.sidebar.divider()
st.sidebar.markdown(f"**Last update:**  \n{latest_time}")
st.sidebar.markdown("**Source:** PMCgroup")
st.sidebar.caption("Rates may vary by exchange office and timing.")

# =====================================================
# HERO
# =====================================================

st.markdown(
    f"""
<div class="hero">
  <div class="hero-inner">
    <div class="navbar">
      <div class="brand">IQD Live</div>
      <div class="navlinks">
        <span>Converter</span>
        <span>Rates</span>
        <span>Charts</span>
        <span>History</span>
      </div>
    </div>
    <div style="text-align:center;">
      <span class="live-pill"><span class="dot"></span> Live market data • {latest_time}</span>
    </div>
    <div class="hero-title">Iraqi Dinar live exchange rates</div>
    <div class="hero-subtitle">Real USD/IQD market rate, buy/sell prices, live charts, and currency conversion.</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# =====================================================
# MAIN CONVERTER CARD - REAL STREAMLIT WIDGETS
# =====================================================

with st.container():
    st.markdown('<div class="converter-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Currency converter</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-subtitle">Editable amount and currency. No fake HTML buttons.</div>', unsafe_allow_html=True)

    convert_tab, rates_tab, chart_tab, alerts_tab = st.tabs(["Convert", "Rates", "Charts", "Alerts"])

    with convert_tab:
        c1, c2, c3 = st.columns([1.1, 1.0, 1.2])

        with c1:
            amount = st.number_input(
                "Amount",
                min_value=1.0,
                value=100.0,
                step=10.0,
                key="hero_amount",
            )

        with c2:
            currency = st.selectbox(
                "From currency",
                list(CURRENCIES.keys()),
                index=0,
                key="hero_currency",
            )

        with c3:
            rate = float(latest[currency])
            result = amount * rate
            st.metric("To IQD", f"{result:,.0f} IQD")

        st.markdown(
            f"""
<div class="big-result">{amount:,.2f} {currency} = {result:,.0f} IQD</div>
<div class="small-note">Market reference from PMCgroup • Updated {latest_time}</div>
""",
            unsafe_allow_html=True,
        )

    with rates_tab:
        st.caption("Main USD/IQD market reference per 100 USD.")
        r1, r2, r3 = st.columns(3)
        r1.metric("Market", f"{latest_market:,.0f} IQD", f"{market_change:,.0f} IQD")
        r2.metric("Buy USD", f"{latest_buy:,.0f} IQD")
        r3.metric("Sell USD", f"{latest_sell:,.0f} IQD")

    with chart_tab:
        mini_period = st.selectbox("Mini chart period", ["24h", "7d", "30d", "All"], index=2, key="hero_chart_period")
        mini_df = filter_period(df, mini_period)
        st.altair_chart(
            alt.Chart(mini_df)
            .mark_area(color="#0B74E5", opacity=0.18, line={"color": "#0B74E5", "strokeWidth": 3})
            .encode(
                x=alt.X("Time:T", title=None),
                y=alt.Y("Market:Q", title="IQD per 100 USD", scale=alt.Scale(zero=False)),
                tooltip=[
                    alt.Tooltip("Time:T", title="Time", format="%Y-%m-%d %H:%M"),
                    alt.Tooltip("Market:Q", title="Market", format=",.0f"),
                ],
            )
            .properties(height=260)
            .interactive(),
            use_container_width=True,
        )

    with alerts_tab:
        alert_target = st.number_input("Alert level for market price", value=float(round(latest_market, 0)), step=250.0)
        if latest_market >= alert_target:
            st.error(f"Alert: market is {latest_market:,.0f} IQD, above {alert_target:,.0f} IQD")
        else:
            st.success(f"Market is below your alert level: {alert_target:,.0f} IQD")

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# CHART HELPER
# =====================================================

def market_chart(data: pd.DataFrame, y_col: str = "Market", chart_type: str = "Area"):
    label = "IQD per 100 USD" if y_col == "Market" else f"IQD per 1 {y_col}"
    base = alt.Chart(data).encode(
        x=alt.X("Time:T", title=None, axis=alt.Axis(labelColor="#667085", gridColor="#f1f5f9")),
        y=alt.Y(f"{y_col}:Q", title=label, scale=alt.Scale(zero=False), axis=alt.Axis(labelColor="#667085", gridColor="#f1f5f9")),
        tooltip=[
            alt.Tooltip("Time:T", title="Time", format="%Y-%m-%d %H:%M"),
            alt.Tooltip(f"{y_col}:Q", title=y_col, format=",.2f"),
        ],
    )

    if chart_type == "Line":
        chart = base.mark_line(color="#0B74E5", strokeWidth=3)
    else:
        chart = base.mark_area(color="#0B74E5", opacity=0.16, line={"color": "#0B74E5", "strokeWidth": 3})

    return chart.properties(height=380).configure_view(strokeWidth=0).interactive()

# =====================================================
# PAGES
# =====================================================

if page == "Dashboard":
    st.markdown('<div class="section-title">Market overview</div>', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Market Price", f"{latest_market:,.0f} IQD", f"{market_change:,.0f} IQD")
    m2.metric("Buy USD", f"{latest_buy:,.0f} IQD")
    m3.metric("Sell USD", f"{latest_sell:,.0f} IQD")

    st.markdown(f'<div class="trend-card {trend_class}">{trend_badge} — {trend_label}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Live exchange rates</div>', unsafe_allow_html=True)
    search = st.text_input("Search currency", placeholder="Type USD, EUR, GBP, TRY, AED, SAR, KWD...", key="rate_search").strip().upper()

    for code, details in CURRENCIES.items():
        if search and search not in code and search not in details["name"].upper():
            continue

        st.markdown(
            f"""
<div class="rate-card">
  <div class="rate-left">
    <div class="flag">{details['flag']}</div>
    <div>
      <div class="rate-name">{details['name']}</div>
      <div class="rate-code">{code}</div>
    </div>
  </div>
  <div>
    <div class="rate-value">{float(latest[code]):,.2f} IQD</div>
    <div class="rate-unit">{details['unit']}</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">Market statistics</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Highest", f"{df['Market'].max():,.0f} IQD")
    s2.metric("Lowest", f"{df['Market'].min():,.0f} IQD")
    s3.metric("Average", f"{df['Market'].mean():,.0f} IQD")
    s4.metric("Records", f"{len(df):,.0f}")

    st.markdown('<div class="section-title">Market chart</div>', unsafe_allow_html=True)
    p1, p2, p3 = st.columns([1, 1, 2])
    with p1:
        period = st.selectbox("Period", ["24h", "7d", "30d", "All"], index=3, key="dashboard_period")
    with p2:
        chart_type = st.selectbox("Chart type", ["Area", "Line"], index=0, key="dashboard_chart_type")

    chart_df = filter_period(df, period)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.altair_chart(market_chart(chart_df, "Market", chart_type), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Historical Data":
    st.markdown('<div class="section-title">Historical market records</div>', unsafe_allow_html=True)

    h1, h2, h3 = st.columns([1, 1, 2])
    with h1:
        history_period = st.selectbox("Period", ["24h", "7d", "30d", "All"], index=3, key="history_period")
    with h2:
        history_currency = st.selectbox("Currency", ["Market", *CURRENCIES.keys()], index=0, key="history_currency")

    history_df = filter_period(df, history_period)
    st.dataframe(history_df.tail(200), use_container_width=True, hide_index=True)

    st.download_button(
        "Download CSV",
        data=to_csv_bytes(history_df),
        file_name=f"iqd_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True,
    )

    st.markdown('<div class="section-title">Historical chart</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.altair_chart(market_chart(history_df, history_currency, "Area"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Currency Converter":
    st.markdown('<div class="section-title">Advanced converter</div>', unsafe_allow_html=True)

    with st.form("advanced_converter_form"):
        f1, f2 = st.columns(2)
        with f1:
            adv_amount = st.number_input("Amount", min_value=1.0, value=100.0, step=10.0)
        with f2:
            adv_currency = st.selectbox("From currency", list(CURRENCIES.keys()))

        submitted = st.form_submit_button("Convert now", type="primary", use_container_width=True)

    adv_result = adv_amount * float(latest[adv_currency])
    st.metric("Converted value", f"{adv_result:,.0f} IQD")

    st.markdown('<div class="section-title">Quick USD values</div>', unsafe_allow_html=True)
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("100 USD", f"{100 * latest_usd:,.0f} IQD")
    q2.metric("500 USD", f"{500 * latest_usd:,.0f} IQD")
    q3.metric("1,000 USD", f"{1000 * latest_usd:,.0f} IQD")
    q4.metric("5,000 USD", f"{5000 * latest_usd:,.0f} IQD")

st.markdown(
    """
<div class="footer">
  Built for Iraqi market monitoring. Rates are informational and may vary by exchange office, spread, and timing.
</div>
""",
    unsafe_allow_html=True,
)
