 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/.github/workflows/update_rates.yml b/.github/workflows/update_rates.yml
index 4d98d638937904d8a4b0c5f862e2e2cd6e03a900..844f21144ba10be0eea1649610c7471efaec2244 100644
--- a/.github/workflows/update_rates.yml
+++ b/.github/workflows/update_rates.yml
@@ -1,48 +1,56 @@
 name: Update IQD Rates
 
 on:
   schedule:
-    - cron: "*/10 * * * *"
+    - cron: "* * * * *"
   workflow_dispatch:
 
 permissions:
   contents: write
 
+concurrency:
+  group: update-iqd-rates
+  cancel-in-progress: true
+
 jobs:
   update-rates:
     runs-on: ubuntu-latest
 
     steps:
       - name: Checkout Repository
         uses: actions/checkout@v4
+        with:
+          fetch-depth: 0
 
       - name: Set up Python
         uses: actions/setup-python@v5
         with:
           python-version: "3.11"
 
       - name: Install Requirements
         run: |
-          pip install pandas
-          pip install telethon
-          pip install requests
+          python -m pip install --upgrade pip
+          pip install -r requirements.txt
 
       - name: Run Update Script
         env:
           API_ID: ${{ secrets.API_ID }}
           API_HASH: ${{ secrets.API_HASH }}
           STRING_SESSION: ${{ secrets.STRING_SESSION }}
         run: python update_rates.py
 
       - name: Commit Updated CSV
+        shell: bash
         run: |
+          set -euo pipefail
+          BRANCH="${GITHUB_REF_NAME}"
           git config --global user.name "github-actions"
           git config --global user.email "actions@github.com"
-
-          git pull origin main --rebase
-
           git add usd_history.csv
-
-          git commit -m "Auto update IQD rates" || echo "No changes"
-
-          git push origin HEAD:main
+          if git diff --cached --quiet; then
+            echo "No CSV changes to commit"
+            exit 0
+          fi
+          git commit -m "Auto update IQD rates"
+          git pull --rebase --autostash origin "$BRANCH"
+          git push origin "HEAD:$BRANCH"
 
EOF
)
