from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Iraqi Dinar Live", page_icon="🇮🇶", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=60_000, key="refresh")

# -------------------------
# Languages
# -------------------------
LANGS = {
    "English": {"flag": "🇬🇧", "dir": "ltr", "code": "en"},
    "العربية": {"flag": "🇮🇶", "dir": "rtl", "code": "ar"},
    "کوردی": {"flag": "☀️", "dir": "rtl", "code": "ku"},
}

TEXT = {
    "en": {
        "title": "Iraqi Dinar live exchange rates",
        "subtitle": "Real Iraqi market USD/IQD rates, buy/sell prices, charts, and currency conversion.",
        "nav": "Navigation", "dashboard": "Dashboard", "history": "Historical Data", "converter": "Currency Converter",
        "language": "Language", "last": "Last update", "source": "Source", "live": "Live market data",
        "convert": "Convert", "rates": "Rates", "charts": "Charts", "alerts": "Alerts",
        "amount": "Amount", "from": "From currency", "to": "To IQD", "result": "Converted value",
        "market_ref": "Market reference from PMCgroup", "market": "Market", "buy": "Buy USD", "sell": "Sell USD",
        "overview": "Market overview", "live_rates": "Live exchange rates", "search": "Search currency",
        "stats": "Market statistics", "highest": "Highest", "lowest": "Lowest", "average": "Average", "records": "Records",
        "chart": "Market chart", "period": "Period", "chart_type": "Chart type", "area": "Area", "line": "Line",
        "historical_records": "Historical market records", "currency": "Currency", "download": "Download CSV",
        "historical_chart": "Historical chart", "advanced_converter": "Advanced converter", "convert_now": "Convert now",
        "converted_value": "Converted value", "quick": "Quick USD values", "alert": "Alert level",
        "up": "Market up", "down": "Market down", "stable": "Market stable",
        "per_100": "IQD per 100 USD", "per_1": "IQD per 1",
        "footer": "Rates are informational and may vary by exchange office, spread, and timing.",
    },
    "ar": {
        "title": "أسعار صرف الدينار العراقي مباشرة",
        "subtitle": "سعر السوق للدولار مقابل الدينار، أسعار البيع والشراء، الرسوم البيانية، وتحويل العملات.",
        "nav": "القائمة", "dashboard": "الرئيسية", "history": "السجل التاريخي", "converter": "محول العملات",
        "language": "اللغة", "last": "آخر تحديث", "source": "المصدر", "live": "بيانات السوق مباشرة",
        "convert": "تحويل", "rates": "الأسعار", "charts": "الرسوم", "alerts": "التنبيهات",
        "amount": "المبلغ", "from": "من العملة", "to": "إلى الدينار العراقي", "result": "القيمة المحولة",
        "market_ref": "سعر السوق من PMCgroup", "market": "السوق", "buy": "شراء الدولار", "sell": "بيع الدولار",
        "overview": "نظرة عامة على السوق", "live_rates": "أسعار العملات المباشرة", "search": "بحث عن عملة",
        "stats": "إحصائيات السوق", "highest": "الأعلى", "lowest": "الأدنى", "average": "المعدل", "records": "السجلات",
        "chart": "رسم السوق", "period": "الفترة", "chart_type": "نوع الرسم", "area": "مساحة", "line": "خط",
        "historical_records": "سجلات السوق التاريخية", "currency": "العملة", "download": "تحميل CSV",
        "historical_chart": "الرسم التاريخي", "advanced_converter": "محول متقدم", "convert_now": "حوّل الآن",
        "converted_value": "القيمة المحولة", "quick": "قيم سريعة بالدولار", "alert": "مستوى التنبيه",
        "up": "السوق ارتفع", "down": "السوق انخفض", "stable": "السوق مستقر",
        "per_100": "دينار لكل 100 دولار", "per_1": "دينار لكل 1",
        "footer": "الأسعار معلوماتية وقد تختلف حسب مكتب الصرافة والسبريد والتوقيت.",
    },
    "ku": {
        "title": "نرخی ڕاستەوخۆی دیناری عێراقی",
        "subtitle": "نرخی بازاڕی دۆلار/دینار، کڕین و فرۆشتن، چارت و گۆڕینی دراو.",
        "nav": "ڕێنیشاندەر", "dashboard": "داشبۆرد", "history": "داتای مێژوویی", "converter": "گۆڕینی دراو",
        "language": "زمان", "last": "دوایین نوێکردنەوە", "source": "سەرچاوە", "live": "داتای ڕاستەوخۆی بازاڕ",
        "convert": "گۆڕین", "rates": "نرخەکان", "charts": "چارتەکان", "alerts": "ئاگادارکردنەوە",
        "amount": "بڕ", "from": "لە دراو", "to": "بۆ دیناری عێراقی", "result": "بەهای گۆڕاو",
        "market_ref": "نرخی بازاڕ لە PMCgroup", "market": "بازاڕ", "buy": "کڕینی دۆلار", "sell": "فرۆشتنی دۆلار",
        "overview": "پوختەی بازاڕ", "live_rates": "نرخی ڕاستەوخۆی دراوەکان", "search": "گەڕان بۆ دراو",
        "stats": "ئاماری بازاڕ", "highest": "بەرزترین", "lowest": "نزمترین", "average": "تێکڕا", "records": "تۆمارەکان",
        "chart": "چارتى بازاڕ", "period": "ماوە", "chart_type": "جۆری چارت", "area": "ناوچە", "line": "هێڵ",
        "historical_records": "تۆمارە مێژووییەکانی بازاڕ", "currency": "دراو", "download": "داگرتنی CSV",
        "historical_chart": "چارتى مێژوویی", "advanced_converter": "گۆڕینی پێشکەوتوو", "convert_now": "ئێستا گۆڕە",
        "converted_value": "بەهای گۆڕاو", "quick": "بەها خێراکانی دۆلار", "alert": "ئاستی ئاگادارکردنەوە",
        "up": "بازاڕ بەرزبووەوە", "down": "بازاڕ دابەزیوە", "stable": "بازاڕ جێگیرە",
        "per_100": "دینار بۆ 100 دۆلار", "per_1": "دینار بۆ 1",
        "footer": "نرخەکان زانیاریین و دەتوانن بە پێی صرافە و کات جیاواز بن.",
    },
}

CURRENCY_FLAGS = {"USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "TRY": "🇹🇷", "AED": "🇦🇪", "SAR": "🇸🇦", "KWD": "🇰🇼"}
CURRENCY_NAMES = {
    "en": {"USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound", "TRY": "Turkish Lira", "AED": "UAE Dirham", "SAR": "Saudi Riyal", "KWD": "Kuwaiti Dinar"},
    "ar": {"USD": "الدولار الأمريكي", "EUR": "اليورو", "GBP": "الجنيه الإسترليني", "TRY": "الليرة التركية", "AED": "الدرهم الإماراتي", "SAR": "الريال السعودي", "KWD": "الدينار الكويتي"},
    "ku": {"USD": "دۆلاری ئەمریکی", "EUR": "یۆرۆ", "GBP": "پاوەندی بەریتانی", "TRY": "لیرەی تورکی", "AED": "دەرەمی ئیمارات", "SAR": "ڕیالی سعودی", "KWD": "دیناری کوەیتی"},
}
CURRENCIES = list(CURRENCY_FLAGS.keys())
COLUMNS = ["Time", "USD", "EUR", "GBP", "TRY", "AED", "SAR", "KWD", "Market", "Buy", "Sell"]

st.sidebar.markdown("## 🌐 Language")
lang_label = st.sidebar.radio(
    "Language / اللغة / زمان",
    list(LANGS.keys()),
    format_func=lambda x: f"{LANGS[x]['flag']} {x}",
    key="lang",
)
code = LANGS[lang_label]["code"]
dir_ = LANGS[lang_label]["dir"]
T = TEXT[code]
T.setdefault("market_price", T.get("market", "Market"))
T.setdefault("data_points", T.get("records", "Data Points"))
T.setdefault("feed_ok", "Live feed active")
T.setdefault("feed_stale", "Live feed may be delayed")
T.setdefault("data_points", {"en": "Data Points", "ar": "نقاط البيانات", "ku": "خاڵەکانی داتا"}.get(code, "Data Points"))
T.setdefault("feed_ok", {"en": "Live feed active", "ar": "التحديث المباشر يعمل", "ku": "نوێکردنەوەی ڕاستەوخۆ کاردەکات"}.get(code, "Live feed active"))
T.setdefault("feed_stale", {"en": "Live feed may be delayed", "ar": "قد يكون التحديث المباشر متأخراً", "ku": "نوێکردنەوەی ڕاستەوخۆ لەوانەیە دوا کەوتبێت"}.get(code, "Live feed may be delayed"))

@st.cache_data(ttl=55)
def load_data() -> pd.DataFrame:
    df = pd.read_csv("usd_history.csv")
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    for c in COLUMNS:
        if c != "Time":
            df[c] = pd.to_numeric(df[c], errors="coerce")
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
    ]
    return clean.reset_index(drop=True) if not clean.empty else df.reset_index(drop=True)

try:
    df = load_data()
except Exception as exc:
    st.error(f"Could not load usd_history.csv: {exc}")
    st.stop()
if df.empty:
    st.error("No market data found. Run GitHub Actions first.")
    st.stop()

latest = df.iloc[-1]
latest_time = latest["Time"].strftime("%Y-%m-%d %H:%M")
latest_market = float(latest["Market"])
latest_buy = float(latest["Buy"])
latest_sell = float(latest["Sell"])
latest_usd = float(latest["USD"])
change = latest_market - float(df["Market"].iloc[-2]) if len(df) >= 2 else 0.0
previous_market = float(df["Market"].iloc[-2]) if len(df) >= 2 else latest_market
pct_change = (change / previous_market * 100) if previous_market else 0.0
try:
    data_age_minutes = max(0, int((pd.Timestamp.now() - latest["Time"]).total_seconds() / 60))
except Exception:
    data_age_minutes = 0
feed_is_stale = data_age_minutes > 180

if change > 0:
    trend = f"📈 {T['up']} {change:,.0f} IQD ({pct_change:+.2f}%)"; trend_class = "trend-up"
elif change < 0:
    trend = f"📉 {T['down']} {abs(change):,.0f} IQD ({pct_change:+.2f}%)"; trend_class = "trend-down"
else:
    trend = f"● {T['stable']}"; trend_class = "trend-neutral"

def filter_period(data: pd.DataFrame, period: str) -> pd.DataFrame:
    if period == "24h":
        cutoff = data["Time"].max() - pd.Timedelta(hours=24)
    elif period == "7d":
        cutoff = data["Time"].max() - pd.Timedelta(days=7)
    elif period == "30d":
        cutoff = data["Time"].max() - pd.Timedelta(days=30)
    else:
        return data.copy()
    out = data[data["Time"] >= cutoff].copy()
    return out if not out.empty else data.copy()

@st.cache_data(ttl=55)
def csv_bytes(data: pd.DataFrame) -> bytes:
    return data.to_csv(index=False).encode("utf-8")

def sparkline_text(values) -> str:
    vals = [float(v) for v in values if pd.notna(v)]
    if len(vals) < 2:
        return "▁▁▁▁▁▁"
    chars = "▁▂▃▄▅▆▇█"
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return "▃" * min(len(vals), 12)
    return "".join(chars[min(7, int((v - lo) / (hi - lo) * 7))] for v in vals[-12:])

def make_chart(data: pd.DataFrame, y_col: str, chart_type: str):
    plot_df = data.copy().dropna(subset=["Time", y_col])
    if plot_df.empty:
        return alt.Chart(pd.DataFrame({"Time": [], y_col: []})).mark_line()

    y_min = float(plot_df[y_col].min())
    y_max = float(plot_df[y_col].max())
    span = max(y_max - y_min, 1)
    pad = max(span * 0.22, 600 if y_col == "Market" else 1)
    y_domain = [max(0, y_min - pad), y_max + pad]

    y_title = T.get("per_100", "IQD per 100 USD") if y_col == "Market" else f"{T.get('per_1', 'IQD per 1')} {y_col}"
    nearest = alt.selection_point(nearest=True, on="mouseover", fields=["Time"], empty=False)

    base = alt.Chart(plot_df).encode(
        x=alt.X("Time:T", title=None, axis=alt.Axis(labelColor="#667085", grid=False, labelPadding=10)),
        y=alt.Y(
            f"{y_col}:Q",
            title=y_title,
            scale=alt.Scale(domain=y_domain, nice=False, zero=False),
            axis=alt.Axis(labelColor="#667085", grid=True, gridColor="#EEF2F7", tickCount=5),
        ),
    )

    line = base.mark_line(color="#0B74E5", strokeWidth=3.5, interpolate="monotone").encode(
        tooltip=[
            alt.Tooltip("Time:T", title="Time", format="%Y-%m-%d %H:%M"),
            alt.Tooltip(f"{y_col}:Q", title=y_col, format=",.2f"),
        ]
    )

    area = base.mark_area(
        color=alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="#0B74E5", offset=0),
                alt.GradientStop(color="rgba(11,116,229,0.04)", offset=1),
            ],
            x1=1, x2=1, y1=1, y2=0,
        ),
        opacity=0.25,
        interpolate="monotone",
    )

    selector = base.mark_circle(size=60, color="#0B74E5", opacity=0).add_params(nearest)
    active = base.mark_circle(size=90, color="#0B74E5").encode(opacity=alt.condition(nearest, alt.value(1), alt.value(0)))
    rule = base.mark_rule(color="#94A3B8").encode(
        opacity=alt.condition(nearest, alt.value(0.45), alt.value(0)),
        tooltip=[
            alt.Tooltip("Time:T", title="Time", format="%Y-%m-%d %H:%M"),
            alt.Tooltip(f"{y_col}:Q", title=y_col, format=",.2f"),
        ],
    )

    if chart_type == T.get("line", "Line") or chart_type == "Line":
        chart = line + selector + active + rule
    else:
        chart = area + line + selector + active + rule

    return (
        chart.properties(height=340)
        .configure_view(strokeWidth=0)
        .configure_axis(labelFontSize=12, titleFontSize=12, titleColor="#667085")
    )

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
:root { --blue:#07145f; --blue2:#0b74e5; --text:#13213c; --muted:#667085; --border:#e4eaf3; --bg:#f5f7fb; --green:#12a05c; --red:#d92d20; --yellow:#b7791f; }
html, body, [class*="css"] { font-family:'Inter',sans-serif; }
.stApp { background:var(--bg); color:var(--text); }
.block-container { padding-top:0!important; padding-left:3rem!important; padding-right:3rem!important; max-width:1320px!important; }
section[data-testid="stSidebar"] { background:#fff!important; border-right:1px solid var(--border); }
section[data-testid="stSidebar"] * { color:var(--text)!important; }
.hero { background:linear-gradient(135deg,#07145f 0%,#0b1f7a 60%,#081139 100%); margin-left:-3rem; margin-right:-3rem; padding:28px 3rem 118px; color:#fff; position:relative; overflow:hidden; }
.hero::after { content:""; position:absolute; left:-10%; right:-10%; bottom:-76px; height:135px; background:var(--bg); border-radius:50% 50% 0 0; }
.hero-inner { max-width:1120px; margin:0 auto; position:relative; z-index:2; }
.navbar { display:flex; align-items:center; justify-content:space-between; margin-bottom:46px; }
.brand { font-size:28px; font-weight:900; letter-spacing:-.04em; }
.navlinks span { margin-left:26px; color:#e7eeff; font-weight:800; font-size:14px; }
.hero-title { text-align:center; font-size:clamp(32px,5vw,54px); line-height:1.05; font-weight:900; letter-spacing:-.06em; margin-bottom:14px; }
.hero-subtitle { text-align:center; color:#dbe7ff; font-size:18px; font-weight:500; }
.live-pill { display:inline-flex; align-items:center; gap:8px; padding:8px 14px; border-radius:999px; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.18); color:#dbe7ff; font-weight:800; font-size:13px; margin-bottom:18px; }
.dot { width:8px; height:8px; border-radius:999px; background:#22c55e; box-shadow:0 0 0 5px rgba(34,197,94,.16); }
.converter-card,.chart-card { background:#fff; border:1px solid var(--border); box-shadow:0 16px 36px rgba(15,23,42,.08); }
.converter-card { border-radius:30px; padding:28px; margin-top:-78px; position:relative; z-index:10; }
.chart-card { border-radius:22px; padding:22px; }
.card-title { font-size:18px; font-weight:900; color:var(--text); margin-bottom:4px; }
.card-subtitle,.small-note { color:var(--muted); font-size:13px; }
.section-title { color:var(--text); font-size:28px; font-weight:900; letter-spacing:-.04em; margin:38px 0 16px; }
.big-result { color:#07145f; font-size:clamp(24px,4vw,36px); font-weight:900; letter-spacing:-.04em; margin-top:12px; }
.trend-card { padding:16px 20px; border-radius:18px; font-weight:900; margin:18px 0; }
.trend-up { background:#e8f8ef; color:var(--green); border:1px solid #b7ebce; }
.trend-down { background:#fff1f0; color:var(--red); border:1px solid #ffc9c4; }
.trend-neutral { background:#fff8e6; color:var(--yellow); border:1px solid #f6d98b; }
.rate-card { background:#fff; border:1px solid var(--border); border-radius:18px; padding:17px 20px; margin-bottom:10px; box-shadow:0 8px 20px rgba(15,23,42,.05); display:flex; align-items:center; justify-content:space-between; }
.rate-left { display:flex; align-items:center; gap:12px; } .flag { font-size:28px; } .rate-name { font-weight:900; color:var(--text); } .rate-code,.rate-unit { font-size:12px; color:var(--muted); font-weight:700; } .rate-value { color:var(--blue2); font-weight:900; font-size:18px; text-align:right; }
div[data-testid="metric-container"] { background:#fff; border:1px solid var(--border); border-radius:20px; padding:20px; box-shadow:0 10px 26px rgba(15,23,42,.06); }
div[data-testid="metric-container"] label { color:var(--muted)!important; font-weight:800!important; text-transform:uppercase; letter-spacing:.04em; font-size:.78rem!important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { color:var(--text)!important; font-weight:900!important; font-size:1.85rem!important; }
.stTabs [data-baseweb="tab-list"] { gap:8px; background:#f8fafc; border:1px solid var(--border); padding:8px; border-radius:999px; }
.stTabs [data-baseweb="tab"] { border-radius:999px; padding:10px 20px; font-weight:900; }
.stTabs [aria-selected="true"] { background:#263a5f!important; color:#fff!important; }
.footer { text-align:center; color:var(--muted); font-size:13px; padding:44px 0 30px; }
@media(max-width:768px){ .block-container{padding-left:1rem!important;padding-right:1rem!important} .hero{margin-left:-1rem;margin-right:-1rem;padding:24px 1rem 100px} .navbar{display:block;text-align:center;margin-bottom:30px} .navlinks{display:none} .converter-card{padding:18px;border-radius:22px} .rate-card{display:block} .rate-value,.rate-unit{text-align:left;margin-top:8px} }

/* Final professional UX polish */
.sticky-rate{position:sticky;top:0;z-index:999;background:#07145f;color:white;padding:10px 16px;border-radius:0 0 16px 16px;font-weight:900;text-align:center;box-shadow:0 10px 24px rgba(15,23,42,.16);}
.stats-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:8px;}
.stat-card{background:#fff;border:1px solid #e4eaf3;border-radius:20px;padding:18px;box-shadow:0 10px 26px rgba(15,23,42,.06);min-width:0;}
.stat-label{font-size:12px;color:#667085;font-weight:800;text-transform:uppercase;letter-spacing:.04em;margin-bottom:8px;}
.stat-value{font-size:clamp(22px,3vw,34px);font-weight:900;color:#13213c;line-height:1.05;white-space:nowrap;}
.stat-unit{font-size:12px;color:#667085;font-weight:800;margin-top:4px;}
.sparkline{font-family:monospace;color:#0B74E5;font-weight:900;font-size:18px;letter-spacing:1px;margin-bottom:4px;text-align:right;}
.rate-right{text-align:right;}
.chart-card{background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%)!important;border:1px solid #e4eaf3!important;border-radius:24px!important;padding:22px!important;box-shadow:0 18px 42px rgba(15,23,42,.08)!important;}
@media(max-width:768px){
  .stats-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;}
  .stat-card{padding:13px;border-radius:16px;}
  .stat-value{font-size:20px;white-space:normal;word-break:keep-all;}
  .stat-unit{font-size:11px;}
  .sticky-rate{font-size:13px;padding:8px 12px;}
  .sparkline{text-align:left;font-size:15px;}
}

</style>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"## 🇮🇶 IQD Live")
st.sidebar.markdown(T["footer"])
st.sidebar.divider()
page_map = {T["dashboard"]: "dashboard", T["history"]: "history", T["converter"]: "converter"}
page_label = st.sidebar.radio(T["nav"], list(page_map.keys()), key="nav")
page = page_map[page_label]
st.sidebar.divider()
st.sidebar.markdown(f"**{T['last']}:**  \n{latest_time}")
st.sidebar.markdown(f"**{T['source']}:** PMCgroup")

st.markdown(f"""
<div class="hero"><div class="hero-inner"><div class="navbar"><div class="brand">IQD Live</div><div class="navlinks"><span>{T['converter']}</span><span>{T['rates']}</span><span>{T['charts']}</span><span>{T['history']}</span></div></div><div style="text-align:center;"><span class="live-pill"><span class="dot"></span> {T['live']} • {latest_time}</span></div><div class="hero-title">{T['title']}</div><div class="hero-subtitle">{T['subtitle']}</div></div></div>
""", unsafe_allow_html=True)


st.markdown(f'<div class="sticky-rate">USD/IQD {latest_market:,.0f} • {trend}</div>', unsafe_allow_html=True)
if feed_is_stale:
    st.warning(f"{T.get('feed_stale', 'Live feed may be delayed')} — {T['last']}: {latest_time}")
else:
    st.caption(f"✅ {T.get('feed_ok', 'Live feed active')} — {T['last']}: {latest_time}")

st.markdown('<div class="converter-card">', unsafe_allow_html=True)
st.markdown(f'<div class="card-title">{T["converter"]}</div><div class="card-subtitle">{T["market_ref"]}</div>', unsafe_allow_html=True)
convert_tab, rates_tab, chart_tab, alerts_tab = st.tabs([T["convert"], T["rates"], T["charts"], T["alerts"]])

with convert_tab:
    c1, c2, c3 = st.columns([1.1, 1.0, 1.2])
    with c1:
        amount = st.number_input(T["amount"], min_value=1.0, value=100.0, step=10.0, key="hero_amount")
    with c2:
        currency = st.selectbox(T["from"], CURRENCIES, format_func=lambda x: f"{CURRENCY_FLAGS[x]} {x} - {CURRENCY_NAMES[code][x]}", key="hero_currency")
    with c3:
        result = amount * float(latest[currency])
        st.metric(T["to"], f"{result:,.0f} IQD")
    st.markdown(f'<div class="big-result">{amount:,.2f} {currency} = {result:,.0f} IQD</div><div class="small-note">{T["market_ref"]} • {latest_time}</div>', unsafe_allow_html=True)

with rates_tab:
    r1, r2, r3 = st.columns(3)
    r1.metric(T["market"], f"{latest_market:,.0f} IQD", f"{change:,.0f} IQD")
    r2.metric(T["buy"], f"{latest_buy:,.0f} IQD")
    r3.metric(T["sell"], f"{latest_sell:,.0f} IQD")

with chart_tab:
    p = st.selectbox(T["period"], ["24h", "7d", "30d", "All"], index=2, key="mini_period")
    st.altair_chart(make_chart(filter_period(df, p), "Market", T["area"]), use_container_width=True)

with alerts_tab:
    target = st.number_input(T["alert"], value=float(round(latest_market, 0)), step=250.0)
    st.success(T["stable"] if latest_market < target else f"{T['market']} >= {target:,.0f}")
st.markdown('</div>', unsafe_allow_html=True)

if page == "dashboard":
    st.markdown(f'<div class="section-title">{T["overview"]}</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric(T["market"], f"{latest_market:,.0f} IQD", f"{change:,.0f} IQD")
    b.metric(T["buy"], f"{latest_buy:,.0f} IQD")
    c.metric(T["sell"], f"{latest_sell:,.0f} IQD")
    st.markdown(f'<div class="trend-card {trend_class}">{trend}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-title">{T["live_rates"]}</div>', unsafe_allow_html=True)
    search = st.text_input(T["search"], placeholder="USD, EUR, GBP, TRY, AED, SAR, KWD", key="search").strip().upper()
    for cur in CURRENCIES:
        name = CURRENCY_NAMES[code][cur]
        if search and search not in cur and search not in name.upper():
            continue
        spark = sparkline_text(df[cur].tail(12))
        st.markdown(f'<div class="rate-card"><div class="rate-left"><div class="flag">{CURRENCY_FLAGS[cur]}</div><div><div class="rate-name">{name}</div><div class="rate-code">{cur}</div></div></div><div class="rate-right"><div class="sparkline">{spark}</div><div class="rate-value">{float(latest[cur]):,.2f} IQD</div><div class="rate-unit">{T["per_1"]} {cur}</div></div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-title">{T["stats"]}</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">{T['highest']}</div><div class="stat-value">{df['Market'].max():,.0f}</div><div class="stat-unit">IQD</div></div>
            <div class="stat-card"><div class="stat-label">{T['lowest']}</div><div class="stat-value">{df['Market'].min():,.0f}</div><div class="stat-unit">IQD</div></div>
            <div class="stat-card"><div class="stat-label">{T['average']}</div><div class="stat-value">{df['Market'].mean():,.0f}</div><div class="stat-unit">IQD</div></div>
            <div class="stat-card"><div class="stat-label">{T.get('data_points', 'Data Points')}</div><div class="stat-value">{len(df):,.0f}</div><div class="stat-unit">Snapshots</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f'<div class="section-title">{T["chart"]}</div>', unsafe_allow_html=True)
    x1, x2, _ = st.columns([1, 1, 2])
    with x1:
        period = st.selectbox(T["period"], ["24h", "7d", "30d", "All"], index=3, key="dash_period")
    with x2:
        chart_type = st.selectbox(T["chart_type"], [T["area"], T["line"]], key="dash_chart")
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.altair_chart(make_chart(filter_period(df, period), "Market", chart_type), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "history":
    st.markdown(f'<div class="section-title">{T["historical_records"]}</div>', unsafe_allow_html=True)
    h1, h2, _ = st.columns([1, 1, 2])
    with h1:
        period = st.selectbox(T["period"], ["24h", "7d", "30d", "All"], index=3, key="hist_period")
    with h2:
        cur = st.selectbox(T["currency"], ["Market", *CURRENCIES], key="hist_cur")
    hist = filter_period(df, period)
    st.dataframe(hist.tail(200), use_container_width=True, hide_index=True)
    st.download_button(T["download"], data=csv_bytes(hist), file_name=f"iqd_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv", type="primary", use_container_width=True)
    st.markdown(f'<div class="section-title">{T["historical_chart"]}</div>', unsafe_allow_html=True)
    st.altair_chart(make_chart(hist, cur, T["area"]), use_container_width=True)

else:
    st.markdown(f'<div class="section-title">{T["advanced_converter"]}</div>', unsafe_allow_html=True)
    with st.form("advanced_converter"):
        f1, f2 = st.columns(2)
        with f1:
            adv_amount = st.number_input(T["amount"], min_value=1.0, value=100.0, step=10.0)
        with f2:
            adv_currency = st.selectbox(T["from"], CURRENCIES, format_func=lambda x: f"{CURRENCY_FLAGS[x]} {x} - {CURRENCY_NAMES[code][x]}")
        st.form_submit_button(T["convert_now"], type="primary", use_container_width=True)
    adv_result = adv_amount * float(latest[adv_currency])
    st.metric(T["result"], f"{adv_result:,.0f} IQD")
    st.markdown(f'<div class="section-title">{T["quick"]}</div>', unsafe_allow_html=True)
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("100 USD", f"{100 * latest_usd:,.0f} IQD")
    q2.metric("500 USD", f"{500 * latest_usd:,.0f} IQD")
    q3.metric("1,000 USD", f"{1000 * latest_usd:,.0f} IQD")
    q4.metric("5,000 USD", f"{5000 * latest_usd:,.0f} IQD")

st.markdown(f'<div class="footer">{T["footer"]}</div>', unsafe_allow_html=True)
