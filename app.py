import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import altair as alt

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="IQD Live — Iraqi Dinar Exchange Rates",
    page_icon="🇮🇶",
    layout="wide",
)

st_autorefresh(interval=60_000, key="auto_refresh")

# ─────────────────────────────────────────────
# DATA LOADING (cached)
# ─────────────────────────────────────────────

@st.cache_data(ttl=55)
def load_data() -> pd.DataFrame:
    df = pd.read_csv("usd_history.csv")
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    return df.dropna(subset=["Time"]).sort_values("Time").reset_index(drop=True)


df = load_data()

if df.empty:
    st.error("No market data available. Run the update workflow first.")
    st.stop()

latest        = df.iloc[-1]
latest_time   = latest["Time"].strftime("%Y-%m-%d %H:%M")
latest_usd    = float(latest["USD"])
latest_market = float(latest["Market"])
latest_buy    = float(latest["Buy"])
latest_sell   = float(latest["Sell"])
prev_market   = float(df["Market"].iloc[-2]) if len(df) >= 2 else latest_market
market_change = latest_market - prev_market

if market_change > 0:
    trend_label, trend_class = f"▲ Market up {market_change:,.0f} IQD", "trend-up"
elif market_change < 0:
    trend_label, trend_class = f"▼ Market down {abs(market_change):,.0f} IQD", "trend-down"
else:
    trend_label, trend_class = "● Market stable", "trend-neutral"

CURRENCIES = {
    "USD": ("🇺🇸", "US Dollar"),
    "EUR": ("🇪🇺", "Euro"),
    "GBP": ("🇬🇧", "British Pound"),
    "TRY": ("🇹🇷", "Turkish Lira"),
    "AED": ("🇦🇪", "UAE Dirham"),
    "SAR": ("🇸🇦", "Saudi Riyal"),
    "KWD": ("🇰🇼", "Kuwaiti Dinar"),
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def filter_by_period(dataframe, period):
    cutoffs = {
        "24h": pd.Timedelta(hours=24),
        "7d":  pd.Timedelta(days=7),
        "30d": pd.Timedelta(days=30),
    }
    if period not in cutoffs:
        return dataframe
    cutoff = dataframe["Time"].max() - cutoffs[period]
    return dataframe[dataframe["Time"] >= cutoff]


def make_chart(data, y_col="Market", color="#1549C8"):
    label = "IQD per 100 USD" if y_col == "Market" else f"IQD per 1 {y_col}"
    return (
        alt.Chart(data)
        .mark_area(
            color=color,
            opacity=0.12,
            line={"color": color, "strokeWidth": 2.5},
        )
        .encode(
            x=alt.X(
                "Time:T",
                title=None,
                axis=alt.Axis(format="%b %d", labelColor="#94a3b8", gridColor="#f1f5f9"),
            ),
            y=alt.Y(
                f"{y_col}:Q",
                title=label,
                scale=alt.Scale(zero=False),
                axis=alt.Axis(labelColor="#94a3b8", format=",.0f", gridColor="#f1f5f9"),
            ),
            tooltip=[
                alt.Tooltip("Time:T", title="Time", format="%Y-%m-%d %H:%M"),
                alt.Tooltip(f"{y_col}:Q", title=y_col, format=",.2f"),
            ],
        )
        .properties(height=340)
        .configure_view(strokeWidth=0)
        .interactive()
    )


st.markdown('\n<style>\n@import url(\'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800;900&family=DM+Mono:wght@400;500&display=swap\');\n\nhtml, body, [class*="css"] { font-family: \'DM Sans\', sans-serif; }\n\n.stApp { background: #EEF2F7; }\n.block-container {\n    padding-top: 0 !important;\n    padding-left: 2.5rem !important;\n    padding-right: 2.5rem !important;\n    max-width: 1240px;\n}\n\nsection[data-testid="stSidebar"] { background: #0B1D4E !important; border-right: 1px solid #162459; }\nsection[data-testid="stSidebar"] * { color: #C7D4F0 !important; }\nsection[data-testid="stSidebar"] .stRadio label { font-weight: 600 !important; }\nsection[data-testid="stSidebar"] hr { border-color: #1e3066 !important; }\n\n.hero {\n    background: linear-gradient(135deg, #0B1D4E 0%, #1549C8 65%, #0B2560 100%);\n    margin: 0 -2.5rem;\n    padding: 40px 2.5rem 120px;\n    position: relative;\n    overflow: hidden;\n}\n.hero::before {\n    content: "";\n    position: absolute;\n    width: 700px; height: 700px;\n    background: radial-gradient(circle, rgba(255,255,255,0.07) 0%, transparent 65%);\n    top: -250px; right: -150px;\n    border-radius: 50%;\n    pointer-events: none;\n}\n.hero::after {\n    content: "";\n    position: absolute;\n    left: -3%; right: -3%; bottom: -55px;\n    height: 110px;\n    background: #EEF2F7;\n    border-radius: 50%;\n    pointer-events: none;\n}\n.hero-inner { max-width: 860px; margin: 0 auto; text-align: center; position: relative; z-index: 2; }\n.hero-badge {\n    display: inline-flex; align-items: center; gap: 7px;\n    background: rgba(255,255,255,0.10); color: #A8C4FF;\n    border: 1px solid rgba(255,255,255,0.18);\n    padding: 6px 16px; border-radius: 999px;\n    font-size: 12.5px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase;\n    margin-bottom: 18px;\n}\n.live-dot {\n    width: 8px; height: 8px; background: #4ADE80;\n    border-radius: 50%; display: inline-block;\n    animation: pulse 2s infinite;\n}\n@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }\n.hero-title { font-size: 46px; font-weight: 900; color: #fff; letter-spacing: -0.05em; line-height: 1.08; margin-bottom: 12px; }\n.hero-sub { font-size: 16px; color: #A8C4FF; line-height: 1.6; }\n\n.conv-card {\n    background: #fff; border-radius: 22px; padding: 30px 34px;\n    margin-top: -76px;\n    box-shadow: 0 20px 70px rgba(11,29,78,0.16);\n    border: 1px solid #E2E8F0; position: relative; z-index: 10;\n}\n.conv-divider { height: 1px; background: #F1F5F9; margin: 18px 0; }\n.conv-result-big { font-size: 30px; font-weight: 900; color: #0B1D4E; letter-spacing: -0.03em; line-height: 1.2; }\n.conv-result-note { font-size: 13px; color: #94a3b8; font-family: \'DM Mono\', monospace; margin-top: 5px; }\n\n.sec-title { font-size: 20px; font-weight: 800; color: #0B1D4E; margin: 38px 0 14px; letter-spacing: -0.03em; }\n\ndiv[data-testid="metric-container"] {\n    background: #fff; border: 1px solid #E2E8F0;\n    border-radius: 18px; padding: 22px 24px;\n    box-shadow: 0 2px 16px rgba(11,29,78,0.06);\n}\ndiv[data-testid="metric-container"] label {\n    color: #64748b !important; font-size: 0.73rem !important;\n    font-weight: 700 !important; text-transform: uppercase; letter-spacing: 0.07em;\n}\ndiv[data-testid="metric-container"] [data-testid="stMetricValue"] {\n    color: #0B1D4E !important; font-weight: 900 !important;\n    font-size: 1.85rem !important; letter-spacing: -0.03em;\n}\n\n.trend-pill { display: inline-block; padding: 10px 18px; border-radius: 12px; font-weight: 700; font-size: 14px; margin: 8px 0 24px; }\n.trend-up      { background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }\n.trend-down    { background: #FEF2F2; color: #DC2626; border: 1px solid #FCA5A5; }\n.trend-neutral { background: #FFFBEB; color: #D97706; border: 1px solid #FDE68A; }\n\n.rate-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 10px; margin-bottom: 6px; }\n.rate-card {\n    background: #fff; border: 1px solid #E2E8F0; border-radius: 14px;\n    padding: 14px 18px; display: flex; align-items: center; justify-content: space-between;\n    box-shadow: 0 2px 10px rgba(11,29,78,0.05);\n    transition: box-shadow 0.2s, transform 0.15s;\n}\n.rate-card:hover { box-shadow: 0 8px 28px rgba(11,29,78,0.12); transform: translateY(-1px); }\n.rate-flag  { font-size: 28px; margin-right: 12px; }\n.rate-name  { font-weight: 700; font-size: 14px; color: #0B1D4E; }\n.rate-code  { font-size: 11px; color: #94a3b8; font-weight: 600; margin-top: 1px; }\n.rate-value { font-weight: 900; font-size: 17px; color: #1549C8; font-family: \'DM Mono\', monospace; }\n.rate-unit  { font-size: 11px; color: #94a3b8; text-align: right; margin-top: 2px; }\n\n.chart-card { background: #fff; border: 1px solid #E2E8F0; border-radius: 18px; padding: 22px 24px; box-shadow: 0 2px 16px rgba(11,29,78,0.06); }\n\ndiv[data-testid="stTextInput"] input { border-radius: 10px !important; font-weight: 500 !important; background: #F8FAFC !important; }\ndiv[data-baseweb="input"]  { border-radius: 10px !important; }\ndiv[data-baseweb="select"] { border-radius: 10px !important; }\ndiv[data-baseweb="input"] input { font-weight: 700 !important; }\n\n.footer { text-align: center; color: #94a3b8; margin-top: 50px; padding-bottom: 36px; font-size: 13px; line-height: 1.8; }\n\n@media (max-width: 768px) {\n    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }\n    .hero { margin: 0 -1rem; padding: 28px 1rem 100px; }\n    .hero-title { font-size: 28px; }\n    .hero-sub   { font-size: 14px; }\n    .conv-card  { padding: 20px; border-radius: 16px; }\n    .conv-result-big { font-size: 22px; }\n    .rate-grid  { grid-template-columns: 1fr; }\n    div[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 1.4rem !important; }\n}\n</style>\n', unsafe_allow_html=True)
