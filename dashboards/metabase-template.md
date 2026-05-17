# Metabase Dashboard for GoPhish Phishing Metrics

Metabase is a good choice if your org already runs it for BI, or if you want a self-hosted open-source option with better SQL querying than Looker Studio.

## Prerequisites

- Metabase (open source or cloud) — https://www.metabase.com
- A database containing your GoPhish export data (PostgreSQL, MySQL, or SQLite)

## Loading Data

### SQLite (quickest setup)

```bash
# Install sqlite-utils
pip install sqlite-utils

# Load your JSON export into SQLite
sqlite-utils insert gophish.db campaigns campaigns.json --alter
sqlite-utils insert gophish.db recipients <(python -c "
import json, sys
data = json.load(open('campaigns.json'))
for c in data:
    for r in c.get('recipients', []):
        r['campaign_id'] = c['id']
        r['campaign_name'] = c['name']
        r['launch_date'] = c.get('launch_date')
        print(json.dumps(r))
") --alter
```

Then point Metabase at the SQLite file.

### PostgreSQL

```sql
CREATE TABLE campaigns (
    id INTEGER PRIMARY KEY,
    name TEXT,
    status TEXT,
    launch_date TIMESTAMPTZ,
    completed_date TIMESTAMPTZ,
    template TEXT,
    total_recipients INTEGER,
    clicks INTEGER,
    reports INTEGER,
    click_rate FLOAT,
    report_rate FLOAT
);

CREATE TABLE recipients (
    campaign_id INTEGER,
    campaign_name TEXT,
    email TEXT,
    first_name TEXT,
    last_name TEXT,
    position TEXT,
    status TEXT,
    reported BOOLEAN,
    click_time TIMESTAMPTZ,
    report_time TIMESTAMPTZ
);
```

## Recommended Questions (Save as a Collection)

### Click Rate Trend
```sql
SELECT
    launch_date::date AS date,
    name AS campaign,
    click_rate
FROM campaigns
ORDER BY launch_date;
```

### Department Variance
```sql
SELECT
    position AS department,
    COUNT(*) AS total_recipients,
    SUM(CASE WHEN status IN ('Clicked Link', 'Submitted Data') THEN 1 ELSE 0 END) AS clicks,
    ROUND(
        100.0 * SUM(CASE WHEN status IN ('Clicked Link', 'Submitted Data') THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS click_rate_pct,
    SUM(CASE WHEN reported = true THEN 1 ELSE 0 END) AS reports
FROM recipients
GROUP BY position
ORDER BY click_rate_pct DESC;
```

### Repeat Offenders (90-day window)
```sql
SELECT
    email,
    position AS department,
    COUNT(DISTINCT campaign_id) AS campaigns_clicked
FROM recipients
WHERE status IN ('Clicked Link', 'Submitted Data')
  AND click_time > NOW() - INTERVAL '90 days'
GROUP BY email, position
HAVING COUNT(DISTINCT campaign_id) >= 2
ORDER BY campaigns_clicked DESC;
```

### Median Time-to-Report
```sql
SELECT
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY EXTRACT(EPOCH FROM (report_time - click_time)) / 60
    ) AS median_minutes
FROM recipients
WHERE reported = true
  AND click_time IS NOT NULL
  AND report_time IS NOT NULL
  AND report_time > click_time;
```

## Dashboard Layout

Create a Metabase dashboard with:
1. **Line chart** — Click rate over time (from click rate trend query)
2. **Table with row conditional formatting** — Department variance (red if >1.5x avg)
3. **Number card** — Company-wide repeat offender %
4. **Number card** — Median time-to-report
5. **Scatter plot** — Click rate vs. report rate per department

Set the dashboard to auto-refresh every 24 hours and share via a public link for leadership.
