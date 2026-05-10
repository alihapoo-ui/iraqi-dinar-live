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

st_autorefresh(interval=60000, key="refresh")

# =========================
# LOAD DATA
# =========================

@st.cache_data(ttl=55)
def load_data():
    df = pd.read_csv("usd_history.csv")
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    df = df.dropna(subset=["Time"])
    df = df.sort_values("Time").reset_index(drop=True)
    return df

df = load_data()

if df.empty:
    st.error("No market data found. Please run the update workflow first.")
    st.stop()

latest = df.iloc[-1]

latest_time = latest["Time"].strftime("%Y-%m-%d %H:%M")
latest_usd = float(latest["USD"])
latest_market = float(latest["Market"])
latest_buy = float(latest["Buy"])
latest_sell = float(latest["Sell"])

if len(df) >= 2:
    previous_market = float(df["Market"].iloc[-2])
    market_change = latest_market - previous_market
else:
    market_change = 0

if market_change > 0:
    trend_text = f"▲ Market up {market_change:,.0f} IQD"
    trend_class = "trend-up"
elif market_change < 0:
    trend_text = f"▼ Market down {abs(market_change):,.0f} IQD"
    trend_class = "trend-down"
else:
    trend_text = "● Market stable"
    trend_class = "trend-neutral"

CURRENCIES = {
    "USD": ("🇺🇸", "US Dollar"),
    "EUR": ("🇪🇺", "Euro"),
    "GBP": ("🇬🇧", "British Pound"),
    "TRY": ("🇹🇷", "Turkish Lira"),
    "AED": ("🇦🇪", "UAE Dirham"),
    "SAR": ("🇸🇦", "Saudi Riyal"),
    "KWD": ("🇰🇼", "Kuwaiti Dinar"),
}

# =========================
# HELPERS
# =========================

def filter_by_period(dataframe, period):
    if period == "24h":
        cutoff = dataframe["Time"].max() - pd.Timedelta(hours=24)
        return dataframe[dataframe["Time"] >= cutoff]

    if period == "7d":
        cutoff = dataframe["Time"].max() - pd.Timedelta(days=7)
        return dataframe[dataframe["Time"] >= cutoff]

    if period == "30d":
        cutoff = dataframe["Time"].max() - pd.Timedelta(days=30)
        return dataframe[dataframe["Time"] >= cutoff]

    return dataframe


def make_chart(data, y_col="Market"):
    label = "IQD per 100 USD" if y_col == "Market" else f"IQD per 1 {y_col}"

    chart = (
        alt.Chart(data)
        .mark_area(
            color="#0B74E5",
            opacity=0.16,
            line={"color": "#0B74E5", "strokeWidth": 3}
        )
        .encode(
            x=alt.X(
                "Time:T",
                title=None,
                axis=alt.Axis(
                    labelColor="#64748B",
                    gridColor="#F1F5F9"
                )
            ),
            y=alt.Y(
                f"{y_col}:Q",
                title=label,
                scale=alt.Scale(zero=False),
                axis=alt.Axis(
                    labelColor="#64748B",
                    gridColor="#F1F5F9"
                )
            ),
            tooltip=[
                alt.Tooltip("Time:T", title="Time", format="%Y-%m-%d %H:%M"),
                alt.Tooltip(f"{y_col}:Q", title=y_col, format=",.2f"),
            ]
        )
        .properties(height=360)
        .configure_view(strokeWidth=0)
        .interactive()
    )

    return chart

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
    background: #F5F7FB;
    color: #10203F;
}

.block-container {
    padding-top: 0rem;
    padding-left: 3rem;
    padding-right: 3rem;
    max-width: 1280px;
}

section[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E5EAF2;
}

section[data-testid="stSidebar"] * {
    color: #10203F;
}

.hero {
    background: linear-gradient(135deg, #07145F 0%, #0B1F7A 55%, #07134B 100%);
    margin-left: -3rem;
    margin-right: -3rem;
    padding: 34px 3rem 118px 3rem;
    color: white;
    position: relative;
    overflow: hidden;
}

.hero:after {
    content: "";
    position: absolute;
    left: -10%;
    right: -10%;
    bottom: -78px;
    height: 135px;
    background: #F5F7FB;
    border-radius: 50% 50% 0 0;
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1080px;
    margin: 0 auto 50px auto;
    position: relative;
    z-index: 2;
}

.brand {
    font-size: 28px;
    font-weight: 900;
    letter-spacing: -0.04em;
}

.navlinks span {
    margin-left: 26px;
    font-size: 14px;
    font-weight: 800;
    color: #E6ECFF;
}

.hero-title {
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    letter-spacing: -0.05em;
    margin-bottom: 12px;
    position: relative;
    z-index: 2;
}

.hero-subtitle {
    text-align: center;
    font-size: 17px;
    color: #D7E2FF;
    position: relative;
    z-index: 2;
}

.converter-card {
    background: #FFFFFF;
    border-radius: 30px;
    padding: 30px;
    margin-top: -80px;
    box-shadow: 0 30px 75px rgba(15, 23, 42, 0.16);
    border: 1px solid #E5EAF2;
    position: relative;
    z-index: 5;
}

.tab-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    background: #F8FAFC;
    border: 1px solid #E5EAF2;
    padding: 8px;
    border-radius: 999px;
    margin-bottom: 24px;
}

.tab-active {
    background: #263A5F;
    color: white;
    padding: 13px;
    border-radius: 999px;
    text-align: center;
    font-weight: 900;
}

.tab-muted {
    color: #64748B;
    padding: 13px;
    border-radius: 999px;
    text-align: center;
    font-weight: 900;
}

.result-line {
    font-size: 26px;
    font-weight: 900;
    color: #09245F;
    margin-top: 20px;
}

.result-note {
    color: #64748B;
    font-size: 14px;
    margin-top: 6px;
}

.blue-box {
    background: #0B74E5;
    color: white;
    padding: 16px 22px;
    border-radius: 12px;
    text-align: center;
    font-weight: 900;
    margin-top: 22px;
}

.section-title {
    font-size: 30px;
    font-weight: 900;
    letter-spacing: -0.04em;
    color: #10203F;
    margin-top: 42px;
    margin-bottom: 20px;
}

div[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E5EAF2;
    border-radius: 22px;
    padding: 22px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.07);
}

div[data-testid="metric-container"] label {
    color: #64748B !important;
    font-size: 0.82rem !important;
    font-weight: 800 !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #10203F !important;
    font-weight: 900 !important;
    font-size: 2rem !important;
}

.trend-card {
    padding: 18px 22px;
    border-radius: 18px;
    font-weight: 900;
    margin: 20px 0;
}

.trend-up {
    background: #E8F9EF;
    color: #0F9F4D;
    border: 1px solid #B8EBCB;
}

.trend-down {
    background: #FEECEC;
    color: #D92828;
    border: 1px solid #F7B8B8;
}

.trend-neutral {
    background: #FFF7E6;
    color: #C47A00;
    border: 1px solid #F4D38B;
}

.rate-card {
    background: #FFFFFF;
    border: 1px solid #E5EAF2;
    border-radius: 18px;
    padding: 18px 22px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
}

.rate-name {
    font-weight: 900;
    color: #10203F;
}

.rate-code {
    color: #64748B;
    font-size: 13px;
}

.rate-value {
    font-weight: 900;
    color: #0B74E5;
    font-size: 18px;
}

.chart-card {
    background: #FFFFFF;
    border: 1px solid #E5EAF2;
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.07);
    margin-top: 14px;
}

.footer {
    text-align: center;
    color: #64748B;
    margin-top: 45px;
    font-size: 13px;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero {
        margin-left: -1rem;
        margin-right: -1rem;
        padding: 28px 1rem 100px 1rem;
    }

    .hero-title {
        font-size: 30px;
    }

    .tab-row {
        grid-template-columns: repeat(2, 1fr);
    }

    .converter-card {
        padding: 20px;
        border-radius: 20px;
    }
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
# MAIN CONVERTER CARD
# =========================

st.markdown('<div class="converter-card">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="tab-row">
        <div class="tab-active">Convert</div>
        <div class="tab-muted">Rates</div>
        <div class="tab-muted">Charts</div>
        <div class="tab-muted">Alerts</div>
    </div>
    """,
    unsafe_allow_html=True
)

input_col, currency_col, output_col = st.columns([1.2, 1, 1.2])

with input_col:
    amount = st.number_input(
        "Amount",
        min_value=1.0,
        value=100.0,
        step=10.0,
        key="main_amount"
    )

with currency_col:
    from_currency = st.selectbox(
        "From currency",
        list(CURRENCIES.keys()),
        key="main_currency"
    )

with output_col:
    live_rate = float(latest[from_currency])
    converted_value = amount * live_rate
    st.metric("To IQD", f"{converted_value:,.0f} IQD")

bottom_left, bottom_right = st.columns([2, 1])

with bottom_left:
    st.markdown(
        f"""
        <div class="result-line">
            {amount:,.2f} {from_currency} = {converted_value:,.0f} IQD
        </div>
        <div class="result-note">
            Market reference from PMCgroup • Updated {latest_time}
        </div>
        """,
        unsafe_allow_html=True
    )

with bottom_right:
    st.markdown('<div class="blue-box">Track exchange rates</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# DASHBOARD PAGE
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

    st.markdown('<div class="section-title">Live Exchange Rates</div>', unsafe_allow_html=True)

    search = st.text_input(
        "Search currency",
        placeholder="Type USD, EUR, GBP, TRY, AED, SAR, KWD..."
    ).upper()

    for code, value in CURRENCIES.items():
        flag, name = value

        if search and search not in code and search not in name.upper():
            continue

        st.markdown(
            f"""
            <div class="rate-card">
                <div>
                    <div class="rate-name">{flag} {name}</div>
                    <div class="rate-code">{code}</div>
                </div>
                <div class="rate-value">{float(latest[code]):,.2f} IQD</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div class="section-title">Market Statistics</div>', unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)

    s1.metric("Highest Recorded", f"{df['Market'].max():,.0f} IQD")
    s2.metric("Lowest Recorded", f"{df['Market'].min():,.0f} IQD")
    s3.metric("Average Market", f"{df['Market'].mean():,.0f} IQD")

    st.markdown('<div class="section-title">Market Chart</div>', unsafe_allow_html=True)

    period = st.selectbox(
        "Chart period",
        ["All", "24h", "7d", "30d"],
        index=0
    )

    chart_df = filter_by_period(df, period)

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.altair_chart(make_chart(chart_df, "Market"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# HISTORICAL DATA PAGE
# =========================

elif page == "Historical Data":

    st.markdown('<div class="section-title">Historical Market Records</div>', unsafe_allow_html=True)

    st.dataframe(df.tail(100), use_container_width=True)

    st.markdown('<div class="section-title">Currency Chart</div>', unsafe_allow_html=True)

    chart_currency = st.selectbox(
        "Select currency",
        ["Market", "USD", "EUR", "GBP", "TRY", "AED", "SAR", "KWD"]
    )

    period = st.selectbox(
        "Chart period",
        ["All", "24h", "7d", "30d"],
        index=0,
        key="history_period"
    )

    chart_df = filter_by_period(df, period)

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.altair_chart(make_chart(chart_df, chart_currency), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# CONVERTER PAGE
# =========================

elif page == "Currency Converter":

    st.markdown('<div class="section-title">Advanced Currency Converter</div>', unsafe_allow_html=True)

    a1, a2 = st.columns(2)

    with a1:
        converter_amount = st.number_input(
            "Enter amount",
            min_value=1.0,
            value=100.0,
            step=10.0,
            key="converter_amount"
        )

    with a2:
        converter_currency = st.selectbox(
            "Currency",
            list(CURRENCIES.keys()),
            key="converter_currency"
        )

    converter_rate = float(latest[converter_currency])
    converter_result = converter_amount * converter_rate

    st.metric(
        "Converted Value",
        f"{converter_result:,.0f} IQD"
    )

    st.markdown('<div class="section-title">Quick USD Values</div>', unsafe_allow_html=True)

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
