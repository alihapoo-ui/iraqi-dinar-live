from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Iraqi Dinar Live",
    page_icon="🇮🇶",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st_autorefresh(interval=60_000, key="iqd_live_refresh")

LANGS = {
    "English": {"flag": "🇬🇧", "code": "en"},
    "العربية": {"flag": "🇮🇶", "code": "ar"},
    "کوردی": {"flag": "☀️", "code": "ku"},
}

TEXT = {
    "en": {
        "title": "Iraqi Dinar Live",
        "subtitle": "Live USD/IQD market rates with charts, history, and currency conversion.",
        "converter": "Currency converter",
        "charts": "Currency charts",
        "history": "History",
        "price_check": "Price Check",
        "amount": "Amount",
        "from": "From",
        "to": "To IQD",
        "market": "Market",
        "buy": "Buy USD",
        "sell": "Sell USD",
        "last": "Last updated",
        "source": "Source",
        "source_value": "Live market feed",
        "popular": "Popular currencies",
        "period": "Period",
        "high": "High",
        "low": "Low",
        "average": "Average",
        "data_points": "Data Points",
        "download": "Download CSV",
        "target_price": "Target price",
        "check_price": "Check price",
        "above": "Market is above your target price",
        "below": "Market is below your target price",
        "footer": "Rates are informational and may vary by exchange office, spread, and timing.",
        "stats": "Stats",
    },
    "ar": {
        "title": "الدينار العراقي مباشر",
        "subtitle": "سعر الدولار مقابل الدينار مع الرسوم البيانية والسجل وتحويل العملات.",
        "converter": "محول العملات",
        "charts": "رسوم العملات",
        "history": "السجل",
        "price_check": "فحص السعر",
        "amount": "المبلغ",
        "from": "من",
        "to": "إلى الدينار العراقي",
        "market": "السوق",
        "buy": "شراء الدولار",
        "sell": "بيع الدولار",
        "last": "آخر تحديث",
        "source": "المصدر",
        "source_value": "تغذية أسعار مباشرة",
        "popular": "العملات الرئيسية",
        "period": "الفترة",
        "high": "الأعلى",
        "low": "الأدنى",
        "average": "المعدل",
        "data_points": "نقاط البيانات",
        "download": "تحميل CSV",
        "target_price": "السعر المستهدف",
        "check_price": "فحص السعر",
        "above": "السوق أعلى من السعر المستهدف",
        "below": "السوق أقل من السعر المستهدف",
        "footer": "الأسعار معلوماتية وقد تختلف حسب مكتب الصرافة والسبريد والتوقيت.",
        "stats": "الإحصائيات",
    },
    "ku": {
        "title": "دیناری عێراقی ڕاستەوخۆ",
        "subtitle": "نرخی دۆلار بە دینار لەگەڵ چارت، مێژوو، و گۆڕینی دراو.",
        "converter": "گۆڕینی دراو",
        "charts": "چارتەکانی دراو",
        "history": "مێژوو",
        "price_check": "پشکنینی نرخ",
        "amount": "بڕ",
        "from": "لە",
        "to": "بۆ دیناری عێراقی",
        "market": "بازاڕ",
        "buy": "کڕینی دۆلار",
        "sell": "فرۆشتنی دۆلار",
        "last": "دوایین نوێکردنەوە",
        "source": "سەرچاوە",
        "source_value": "داتای ڕاستەوخۆی بازاڕ",
        "popular": "دراوە گرنگەکان",
        "period": "ماوە",
        "high": "بەرزترین",
        "low": "نزمترین",
        "average": "تێکڕا",
        "data_points": "خاڵەکانی داتا",
        "download": "داگرتنی CSV",
        "target_price": "نرخی ئامانج",
        "check_price": "پشکنینی نرخ",
        "above": "بازاڕ لە نرخی ئامانج بەرزترە",
        "below": "بازاڕ لە نرخی ئامانج خوارترە",
        "footer": "نرخەکان زانیاریین و دەتوانن بە پێی صرافە و کات جیاواز بن.",
        "stats": "ئامارەکان",
    },
}

FLAGS = {"USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "TRY": "🇹🇷", "AED": "🇦🇪", "SAR": "🇸🇦", "KWD": "🇰🇼"}
NAMES = {
    "en": {"USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound", "TRY": "Turkish Lira", "AED": "UAE Dirham", "SAR": "Saudi Riyal", "KWD": "Kuwaiti Dinar"},
    "ar": {"USD": "الدولار الأمريكي", "EUR": "اليورو", "GBP": "الجنيه الإسترليني", "TRY": "الليرة التركية", "AED": "الدرهم الإماراتي", "SAR": "الريال السعودي", "KWD": "الدينار الكويتي"},
    "ku": {"USD": "دۆلاری ئەمریکی", "EUR": "یۆرۆ", "GBP": "پاوەندی بەریتانی", "TRY": "لیرەی تورکی", "AED": "دەرەمی ئیمارات", "SAR": "ڕیالی سعودی", "KWD": "دیناری کوەیتی"},
}
CURRENCIES = list(FLAGS.keys())
COLUMNS = ["Time", "USD", "EUR", "GBP", "TRY", "AED", "SAR", "KWD", "Market", "Buy", "Sell"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
:root{--navy:#07145f;--text:#17213a;--muted:#657089;--bg:#f6f8fc;--line:#e5eaf3;--green:#0f9f5f;--red:#e23b67;}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;}
.stApp{background:var(--bg);color:var(--text);}
.block-container{padding:0 2.2rem 2rem!important;max-width:1180px!important;}
section[data-testid="stSidebar"]{background:#fff!important;border-right:1px solid var(--line);}
.topbar{background:linear-gradient(135deg,#07145f,#0c1e78);margin:0 -2.2rem;padding:24px 2.2rem 50px;color:white;overflow:hidden;}
.toprow{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:22px;}
.brand{font-weight:900;font-size:34px;letter-spacing:-.06em;white-space:nowrap;}
.pill{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.16);padding:8px 12px;border-radius:999px;font-weight:800;font-size:13px;color:#e7efff;white-space:nowrap;}
.dot{width:8px;height:8px;border-radius:50%;background:#28d779;box-shadow:0 0 0 5px rgba(40,215,121,.18);}
.hero-title{font-size:clamp(34px,6vw,58px);font-weight:900;letter-spacing:-.06em;line-height:1.02;text-align:center;margin:8px 0;}
.hero-sub{font-size:17px;color:#dce7ff;text-align:center;margin-bottom:10px;}
.main-card{background:#fff;border:1px solid var(--line);border-radius:30px;padding:28px;margin-top:-38px;box-shadow:0 18px 42px rgba(15,23,42,.10);position:relative;z-index:5;}
.section{font-size:28px;font-weight:900;letter-spacing:-.04em;margin:28px 0 14px;}
.small{color:var(--muted);font-size:13px;font-weight:600;}
.result{font-size:clamp(30px,5vw,46px);font-weight:900;color:#07145f;letter-spacing:-.05em;margin:8px 0;}
.change-up{color:var(--green);font-weight:900}.change-down{color:var(--red);font-weight:900}.change-flat{color:#667085;font-weight:900}
.market-strip{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0;}
.mini-card{background:#f8fbff;border:1px solid var(--line);border-radius:18px;padding:16px;}
.mini-label{font-size:12px;color:var(--muted);font-weight:800;text-transform:uppercase;}
.mini-value{font-size:26px;font-weight:900;color:var(--text);margin-top:4px;white-space:nowrap;}
.rates-list{display:flex;flex-direction:column;gap:10px;margin-top:8px;}
.rate-row{background:#fff;border:1px solid var(--line);border-radius:20px;padding:16px;display:grid;grid-template-columns:56px 1fr 120px 150px;align-items:center;gap:14px;box-shadow:0 8px 24px rgba(15,23,42,.05);}
.rate-row.featured{background:#06133e;color:white;border-color:#06133e;}
.rate-row.featured .code,.rate-row.featured .name,.rate-row.featured .value{color:white;}
.flag{font-size:32px}.code{font-size:24px;font-weight:900;color:var(--text);}.name{font-size:13px;color:var(--muted);font-weight:700}.value{font-size:22px;font-weight:900;color:var(--text);text-align:right}.spark{font-family:monospace;font-size:22px;color:var(--green);letter-spacing:1px;text-align:center;white-space:nowrap}.spark.down{color:var(--red)}
.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.stat{background:white;border:1px solid var(--line);border-radius:18px;padding:16px}.stat .label{font-size:12px;color:var(--muted);font-weight:800;text-transform:uppercase}.stat .num{font-size:24px;font-weight:900;white-space:nowrap;color:var(--text)}
.chart-card{background:linear-gradient(180deg,#fff,#f8fbff);border:1px solid var(--line);border-radius:24px;padding:18px;box-shadow:0 12px 34px rgba(15,23,42,.07);}
.footer{text-align:center;color:var(--muted);font-size:13px;padding:30px 0;}
div[data-testid="stMetricValue"]{font-weight:900!important;}
@media(max-width:768px){
  .block-container{padding:0 .8rem 1.5rem!important;}
  .topbar{margin:0 -.8rem;padding:18px .8rem 34px;}
  .toprow{margin-bottom:12px;align-items:flex-start}.brand{font-size:32px}.hero-title{font-size:31px}.hero-sub{font-size:14px;}
  .pill{font-size:10px;padding:6px 8px;}
  .main-card{margin-top:-24px;border-radius:22px;padding:16px;}
  .market-strip{grid-template-columns:1fr;gap:10px}.mini-value{font-size:27px;}
  .rate-row{grid-template-columns:48px 1fr 96px;gap:10px;padding:14px;border-radius:18px;}
  .rate-row .spark{grid-column:2/4;text-align:left;font-size:17px;}
  .code{font-size:22px}.value{font-size:21px}.section{font-size:25px;margin:24px 0 12px;}.stat-grid{grid-template-columns:repeat(2,1fr)}.stat .num{font-size:18px;white-space:normal}.chart-card{padding:8px;border-radius:18px}
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=20)
def load_data() -> pd.DataFrame:
    df = pd.read_csv("usd_history.csv")
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    for col in COLUMNS:
        if col != "Time":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Time", "USD", "Market", "Buy", "Sell"])
    df = df.sort_values("Time").drop_duplicates(subset=["Time"], keep="last")
    clean = df[
        df["USD"].between(1000, 2500)
        & df["Market"].between(100000, 250000)
        & df["EUR"].between(500, 4000)
        & df["GBP"].between(500, 5000)
        & df["TRY"].between(1, 500)
        & df["AED"].between(100, 1000)
        & df["SAR"].between(100, 1000)
        & df["KWD"].between(1000, 10000)
    ].copy()
    return clean.reset_index(drop=True) if not clean.empty else df.reset_index(drop=True)

def filter_period(data: pd.DataFrame, period: str) -> pd.DataFrame:
    if period == "1D":
        cutoff = data["Time"].max() - pd.Timedelta(days=1)
    elif period == "1W":
        cutoff = data["Time"].max() - pd.Timedelta(days=7)
    elif period == "1M":
        cutoff = data["Time"].max() - pd.Timedelta(days=30)
    else:
        return data.copy()
    out = data[data["Time"] >= cutoff].copy()
    return out if not out.empty else data.copy()



def format_age_label(last_time: pd.Timestamp, lang: str) -> tuple[str, str]:
    age_minutes = int((pd.Timestamp.now() - last_time).total_seconds() // 60)
    if age_minutes <= 2:
        return ("🟢 Live", "small")
    if age_minutes <= 10:
        return (f"🟡 Delayed {age_minutes}m", "small")
    return (f"🔴 Stale {age_minutes}m", "small")

def sparkline(vals) -> str:
    values = [float(v) for v in vals if pd.notna(v)]
    if len(values) < 2:
        return "▁▁▁▁▁▁▁"
    chars = "▁▂▃▄▅▆▇█"
    lo, hi = min(values), max(values)
    if hi == lo:
        return "▃" * min(len(values), 16)
    return "".join(chars[min(7, int((v - lo) / (hi - lo) * 7))] for v in values[-16:])

def make_chart(data: pd.DataFrame, col: str):
    plot = data.dropna(subset=["Time", col]).copy()
    y_min = float(plot[col].min())
    y_max = float(plot[col].max())
    span = max(y_max - y_min, 1)
    pad = max(span * 0.18, 500 if col == "Market" else 1)
    domain = [max(0, y_min - pad), y_max + pad]
    base = alt.Chart(plot).encode(
        x=alt.X("Time:T", title=None, axis=alt.Axis(grid=False, labelColor="#667085")),
        y=alt.Y(f"{col}:Q", title=None, scale=alt.Scale(domain=domain, zero=False), axis=alt.Axis(grid=True, gridColor="#e8edf5", labelColor="#667085", tickCount=4)),
        tooltip=[alt.Tooltip("Time:T", title="Time", format="%Y-%m-%d %H:%M"), alt.Tooltip(f"{col}:Q", title=col, format=",.2f")],
    )
    line = base.mark_line(color="#0B56B3", strokeWidth=3, interpolate="monotone")
    point = base.mark_circle(color="#ff4d7d", size=70).transform_window(rank="rank()", sort=[alt.SortField("Time", order="descending")]).transform_filter("datum.rank == 1")
    return (line + point).properties(height=360).configure_view(strokeWidth=0)

@st.cache_data(ttl=55)
def csv_bytes(data: pd.DataFrame) -> bytes:
    return data.to_csv(index=False).encode("utf-8")

try:
    df = load_data()
except Exception as exc:
    st.error(f"Could not load usd_history.csv: {exc}")
    st.stop()

if df.empty:
    st.error("No market data found. Run the update workflow first.")
    st.stop()

st.sidebar.markdown("## 🌐 Language")
lang_label = st.sidebar.radio("Language / اللغة / زمان", list(LANGS.keys()), format_func=lambda x: f"{LANGS[x]['flag']} {x}")
code = LANGS[lang_label]["code"]
T = TEXT[code]

latest = df.iloc[-1]
latest_time = latest["Time"].strftime("%Y-%m-%d %H:%M")
status_label, status_class = format_age_label(pd.Timestamp(latest["Time"]), code)
market = float(latest["Market"])
buy = float(latest["Buy"])
sell = float(latest["Sell"])
prev = float(df["Market"].iloc[-2]) if len(df) > 1 else market
change = market - prev
pct = (change / prev * 100) if prev else 0
change_class = "change-up" if change > 0 else "change-down" if change < 0 else "change-flat"
arrow = "🔺" if change > 0 else "🔻" if change < 0 else "●"

st.markdown(f"""
<div class="topbar">
  <div class="toprow">
    <div class="brand">IQD Live</div>
    <div class="pill"><span class="dot"></span>{T['last']}: {latest_time} • {status_label}</div>
  </div>
  <div class="hero-title">{T['title']}</div>
  <div class="hero-sub">{T['subtitle']}</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-card">', unsafe_allow_html=True)

tab_convert, tab_charts, tab_history, tab_check = st.tabs([T["converter"], T["charts"], T["history"], T["price_check"]])

with tab_convert:
    c1, c2, c3 = st.columns([1, 1, 1.2])
    with c1:
        amount = st.number_input(T["amount"], min_value=1.0, value=100.0, step=10.0)
    with c2:
        from_ccy = st.selectbox(T["from"], CURRENCIES, index=0, format_func=lambda x: f"{FLAGS[x]} {x}")
    result = amount * float(latest[from_ccy])
    with c3:
        st.metric(T["to"], f"{result:,.0f} IQD")
    st.markdown(f'<div class="result">{amount:,.0f} {from_ccy} = {result:,.0f} IQD</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="small">{T["last"]}: {latest_time} • {T["source"]}: {T["source_value"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="market-strip">', unsafe_allow_html=True)
    st.markdown(f'<div class="mini-card"><div class="mini-label">{T["market"]}</div><div class="mini-value">{market:,.0f} IQD</div><div class="{change_class}">{arrow} {change:,.0f} IQD ({pct:+.2f}%)</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mini-card"><div class="mini-label">{T["buy"]}</div><div class="mini-value" style="color:#0f9f5f">{buy:,.0f} IQD</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mini-card"><div class="mini-label">{T["sell"]}</div><div class="mini-value" style="color:#e23b67">{sell:,.0f} IQD</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section">{T["popular"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="rates-list">', unsafe_allow_html=True)
    for cur in CURRENCIES:
        val = float(latest[cur])
        series = df[cur].tail(16)
        sp = sparkline(series)
        spark_class = "spark down" if len(series) > 1 and float(series.iloc[-1]) < float(series.iloc[0]) else "spark"
        featured = " featured" if cur == "USD" else ""
        st.markdown(f'<div class="rate-row{featured}"><div class="flag">{FLAGS[cur]}</div><div><div class="code">{cur}</div><div class="name">{NAMES[code][cur]}</div></div><div class="{spark_class}">{sp}</div><div class="value">{val:,.2f}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_charts:
    c1, c2 = st.columns([1, 1])
    with c1:
        chart_ccy = st.selectbox(T["from"], ["Market", *CURRENCIES], index=0)
    with c2:
        period = st.radio(T["period"], ["1D", "1W", "1M", "ALL"], index=2, horizontal=True)
    chart_df = filter_period(df, period)
    first = float(chart_df[chart_ccy].iloc[0])
    last = float(chart_df[chart_ccy].iloc[-1])
    diff = last - first
    diff_pct = diff / first * 100 if first else 0
    diff_class = "change-up" if diff >= 0 else "change-down"
    title_unit = "IQD" if chart_ccy == "Market" else f"IQD / {chart_ccy}"
    st.markdown(f'<div class="result">{last:,.2f} {title_unit}</div><div class="{diff_class}">{diff:+,.2f} ({diff_pct:+.2f}%) • {period}</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.altair_chart(make_chart(chart_df, chart_ccy), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section">{T["stats"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-grid">', unsafe_allow_html=True)
    st.markdown(f'<div class="stat"><div class="label">{T["high"]}</div><div class="num">{chart_df[chart_ccy].max():,.2f}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat"><div class="label">{T["low"]}</div><div class="num">{chart_df[chart_ccy].min():,.2f}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat"><div class="label">{T["average"]}</div><div class="num">{chart_df[chart_ccy].mean():,.2f}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat"><div class="label">{T["data_points"]}</div><div class="num">{len(chart_df):,.0f}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_history:
    period = st.radio(T["period"], ["1D", "1W", "1M", "ALL"], index=3, horizontal=True, key="hist_period")
    hist = filter_period(df, period)
    st.dataframe(hist.tail(200), use_container_width=True, hide_index=True)
    st.download_button(T["download"], data=csv_bytes(hist), file_name=f"iqd_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv", type="primary", use_container_width=True)

with tab_check:
    target = st.number_input(T["target_price"], value=float(round(market, 0)), step=250.0)
    st.button(T["check_price"], type="primary", use_container_width=True)
    if market >= target:
        st.warning(f"{T['above']}: {market:,.0f} IQD")
    else:
        st.success(f"{T['below']}: {target:,.0f} IQD")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown(f'<div class="footer">{T["footer"]}</div>', unsafe_allow_html=True)
