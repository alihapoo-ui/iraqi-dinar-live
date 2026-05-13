 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/update_rates.py b/update_rates.py
index 08eae6ea22b4e80b4a000b05e95a0380bde17c59..d3dc37fa33b6d9b42ecdab32a8d2f21e751ec65c 100644
--- a/update_rates.py
+++ b/update_rates.py
@@ -91,55 +91,76 @@ def get_fx_rates() -> dict:
         raise RuntimeError(f"Missing FX rates: {missing}")
 
     return rates
 
 
 def build_row(usd_rate: float, fx_rates: dict) -> dict:
     market_price = round(usd_rate * 100, 0)
     spread = 250
 
     row = {
         "Time": datetime.now(IRAQ_TZ).strftime("%Y-%m-%d %H:%M:%S"),
         "USD": round(usd_rate, 2),
         "Market": market_price,
         "Buy": market_price + spread,
         "Sell": market_price - spread,
     }
 
     # FX API gives foreign currency per 1 USD.
     # Therefore IQD per 1 foreign currency = USD/IQD divided by FX quote.
     for currency in CURRENCIES:
         row[currency] = round(usd_rate / float(fx_rates[currency]), 2)
 
     return row
 
 
+def get_last_usd_rate_from_csv() -> float | None:
+    if not os.path.exists(CSV_FILE):
+        return None
+    try:
+        df = pd.read_csv(CSV_FILE)
+        if "USD" not in df.columns or df.empty:
+            return None
+        usd = pd.to_numeric(df["USD"], errors="coerce").dropna()
+        return float(usd.iloc[-1]) if not usd.empty else None
+    except Exception:
+        return None
+
+
 def update_csv(new_row: dict) -> None:
     columns = ["Time", "USD", "EUR", "GBP", "TRY", "AED", "SAR", "KWD", "Market", "Buy", "Sell"]
 
     if os.path.exists(CSV_FILE):
         df = pd.read_csv(CSV_FILE)
     else:
         df = pd.DataFrame(columns=columns)
 
     df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
     df = df[columns]
 
     # Keep the CSV small and fast for Streamlit.
     if len(df) > MAX_ROWS:
         df = df.tail(MAX_ROWS).reset_index(drop=True)
 
     df.to_csv(CSV_FILE, index=False)
 
     print("CSV updated successfully")
     print(new_row)
 
 
 # =====================================================
 # MAIN
 # =====================================================
 
 if __name__ == "__main__":
-    usd_rate = get_latest_pmc_rate()
+    try:
+        usd_rate = get_latest_pmc_rate()
+    except Exception as exc:
+        fallback = get_last_usd_rate_from_csv()
+        if fallback is None:
+            raise
+        print(f"Warning: failed to read Telegram rate ({exc}). Using last known USD rate: {fallback}")
+        usd_rate = fallback
+
     fx_rates = get_fx_rates()
     row = build_row(usd_rate, fx_rates)
     update_csv(row)
 
EOF
)
