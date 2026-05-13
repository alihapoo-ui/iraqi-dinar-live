 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/app.py b/app.py
index 92266308c4b622336202f2cc1d5437f66f9815bf..23f955a7ca711dfeac5b58bd0c221989add0fd83 100644
--- a/app.py
+++ b/app.py
@@ -146,147 +146,158 @@ section[data-testid="stSidebar"]{background:#fff!important;border-right:1px soli
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
 
-@st.cache_data(ttl=55)
+@st.cache_data(ttl=20)
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
 
+
+
+def format_age_label(last_time: pd.Timestamp, lang: str) -> tuple[str, str]:
+    age_minutes = int((pd.Timestamp.now() - last_time).total_seconds() // 60)
+    if age_minutes <= 2:
+        return ("🟢 Live", "small")
+    if age_minutes <= 10:
+        return (f"🟡 Delayed {age_minutes}m", "small")
+    return (f"🔴 Stale {age_minutes}m", "small")
+
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
+status_label, status_class = format_age_label(pd.Timestamp(latest["Time"]), code)
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
-    <div class="pill"><span class="dot"></span>{T['last']}: {latest_time}</div>
+    <div class="pill"><span class="dot"></span>{T['last']}: {latest_time} • {status_label}</div>
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
 
EOF
)
