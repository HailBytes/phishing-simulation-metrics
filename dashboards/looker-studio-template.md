# Looker Studio Dashboard for GoPhish Phishing Metrics

Looker Studio (formerly Google Data Studio) is free and works well for executive-facing phishing metric dashboards — especially if your leadership already lives in Google Workspace.

## Architecture

GoPhish doesn't natively connect to Looker Studio. You'll use one of two approaches:

### Option A: Google Sheets as intermediary (recommended for small orgs)

1. Run `gophish-export.py` on a schedule (cron or GitHub Actions)
2. Write output to Google Sheets using the Sheets API or `gspread`
3. Connect Looker Studio to that Google Sheet

```python
# Append to existing Sheet after export
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service-account.json", scope)
client = gspread.authorize(creds)
sheet = client.open("GoPhish Metrics").sheet1
sheet.append_row([campaign_name, click_rate, report_rate, ...])
```

### Option B: BigQuery (recommended for >500 employees or multi-year data)

1. Export campaign JSON
2. Load to BigQuery with `bq load` or the BigQuery Python client
3. Connect Looker Studio to BigQuery directly (native connector)

```bash
bq load --source_format=NEWLINE_DELIMITED_JSON \
  your_project.phishing.campaigns \
  campaigns.json \
  schema.json
```

---

## Recommended Charts and Layout

### Page 1: Executive Summary
- **Scorecard (large):** Current click rate vs. last quarter
- **Scorecard:** Current report rate
- **Line chart:** Click rate trend (all campaigns, date on X axis)
- **Bar chart:** Click rate vs. report rate per campaign

### Page 2: Department Breakdown
- **Table with heatmap bars:** Department, click rate, report rate, repeat offender %
- **Geo map (if multi-site):** Click rate by office location
- **Bar chart:** Top 5 highest-risk departments

### Page 3: Program ROI
- **Scorecard:** Estimated risk reduction value ($)
- **Scorecard:** Program ROI %
- **Text block:** Methodology note with link to `docs/roi-calculation-methodology.md`

---

## Filters to Include

- Date range (campaign launch date)
- Department
- Campaign template type (credential harvest vs. attachment vs. link)

---

## Sharing and Scheduling

- Set the dashboard to **Viewer** access for executives (no edit rights)
- Use **Scheduled email delivery** (Looker Studio → Share → Schedule delivery) to send a PDF to stakeholders monthly
- Embed in an internal wiki or intranet page with the embed code

---

## HailBytes SAT Note

All of these panels are pre-built in HailBytes SAT with no configuration required. If you're spending significant time maintaining this Looker Studio pipeline, that's a signal to evaluate managed options.
