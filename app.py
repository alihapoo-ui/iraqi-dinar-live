# IQD Live Streamlit app
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Iraqi Dinar Live", page_icon="🇮🇶", layout="wide")
st_autorefresh(interval=60_000, key="iqd_live_refresh")

COLUMNS = ["Time", "USD", "EUR", "GBP", "TRY", "AED", "SAR", "KWD", "Market", "Buy", "Sell"]

@st.cache_data(ttl=20)
def load_data() -> pd.DataFrame:
    df = pd.read_csv("usd_history.csv")
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    for c in COLUMNS:
        if c != "Time":
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Time", "Market", "USD", "Buy", "Sell"]).sort_values("Time")
    return df.tail(5000).reset_index(drop=True)


def age_label(last_time: pd.Timestamp) -> str:
    mins = int((pd.Timestamp.now() - last_time).total_seconds() // 60)
    if mins <= 2:
        return "🟢 Live"
    if mins <= 10:
        return f"🟡 Delayed ({mins}m)"
    return f"🔴 Stale ({mins}m)"


try:
    df = load_data()
except Exception as exc:
    st.error(f"Could not load data: {exc}")
    st.stop()

if df.empty:
    st.error("No data found in usd_history.csv")
    st.stop()

latest = df.iloc[-1]
last_time = pd.Timestamp(latest["Time"])

st.title("🇮🇶 IQD Live")
st.caption(f"Last updated: {last_time:%Y-%m-%d %H:%M:%S} • {age_label(last_time)}")

c1, c2, c3 = st.columns(3)
c1.metric("Market", f"{latest['Market']:,.0f} IQD")
c2.metric("Buy", f"{latest['Buy']:,.0f} IQD")
c3.metric("Sell", f"{latest['Sell']:,.0f} IQD")

amount = st.number_input("Amount (USD)", min_value=1.0, value=100.0, step=10.0)
st.subheader(f"{amount:,.0f} USD = {amount * float(latest['USD']):,.0f} IQD")

period = st.radio("Chart Period", ["1D", "1W", "1M", "ALL"], horizontal=True, index=2)
plot_df = df.copy()
if period != "ALL":
    days = {"1D": 1, "1W": 7, "1M": 30}[period]
    cutoff = plot_df["Time"].max() - pd.Timedelta(days=days)
    plot_df = plot_df[plot_df["Time"] >= cutoff]

chart = (
    alt.Chart(plot_df)
    .mark_line(color="#0B56B3", strokeWidth=3)
    .encode(x="Time:T", y="Market:Q", tooltip=["Time:T", "Market:Q"])
    .properties(height=340)
)
st.altair_chart(chart, use_container_width=True)

st.subheader("Recent rows")
st.dataframe(df.tail(200), use_container_width=True, hide_index=True)

st.download_button(
    "Download CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name=f"iqd_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv",
)
