# Grafana Dashboard for GoPhish — Phishing Simulation Metrics

This dashboard requires:
- **Grafana** 9.x or later
- **GoPhish** with the API enabled
- The **JSON API** or **Infinity** data source plugin (for polling GoPhish API directly), OR
- A Prometheus exporter writing GoPhish metrics (see `/scripts/gophish-export.py` + a cron job)

## Import Instructions

1. In Grafana, go to **Dashboards → Import**
2. Upload `grafana-gophish.json` or paste its contents
3. Select your data source when prompted
4. Update the `gophish_host` and `api_key` variables in the dashboard settings

## Dashboard Panels

The JSON dashboard includes the following panels:

| Panel | Type | Description |
|---|---|---|
| Click Rate Trend | Time series | Click rate % per campaign over time |
| Report Rate Trend | Time series | Report rate % per campaign over time |
| Click vs. Report Rate | Bar chart | Side-by-side comparison per campaign |
| Department Risk Heatmap | Heatmap | Click rate by dept × campaign |
| Repeat Offenders | Stat | % of employees with 2+ clicks (rolling 90d) |
| Median Time-to-Report | Gauge | P50 time-to-report in minutes |
| Top 5 High-Risk Departments | Table | Sorted by click rate, with variance column |
| Campaign Summary | Table | All campaigns with key metrics |

## Data Source Setup (Infinity Plugin)

Install the Infinity plugin:
```
grafana-cli plugins install yesoreyeram-infinity-datasource
```

Then configure a datasource pointing at your GoPhish API:
- Base URL: `https://your-gophish-host:3333`
- Auth: Bearer token → your API key

## Alternative: Prometheus + Cron Export

If you prefer pull-based metrics:

```bash
# Add to crontab — runs every hour, appends to Prometheus text file
0 * * * * python /opt/gophish-metrics/gophish-export.py \
  --api-key $GOPHISH_API_KEY \
  --output /var/lib/node_exporter/gophish.json
```

Then use a JSON-to-Prometheus bridge or write a custom exporter.

## Notes

- GoPhish's API returns campaign data at rest (not streaming). Refresh interval of 1h is sufficient for most programs.
- For real-time reporting metrics, use a webhook in GoPhish to push events to a time-series DB.
