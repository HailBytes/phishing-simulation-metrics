# Phishing Simulation Metrics

> Open-source dashboards, scripts, and frameworks for measuring phishing simulation program effectiveness.

Most security awareness programs generate reports that look busy but don't answer the question a CFO or CISO actually asks: **"Is this working, and is it worth the money?"**

This repo gives you the measurement layer to answer that question — whether you're running GoPhish self-hosted or evaluating managed platforms.

---

## The Five Metrics That Actually Matter

### 1. Click Rate (and trend over time)
**Definition:** Percentage of recipients who clicked a simulated phishing link in a campaign.

The raw number is almost meaningless. A 14% click rate at month 1 vs. a 14% click rate at month 12 are completely different problems. What matters is the **trajectory** — is it declining? How fast? Segment by department and tenure to find where it's stuck.

**Good signal:** Click rate declining 3–5% per quarter across the org.  
**Red flag:** Flat or increasing click rate after 6+ months of training.

---

### 2. Report Rate (the one that actually matters)
**Definition:** Percentage of recipients who *reported* a phishing simulation to security rather than just ignoring it or clicking.

This is the metric most programs ignore and the one that best predicts real-world resilience. An employee who reports a phish — even one they almost clicked — is doing exactly what you want. Employees who correctly ignore it but never report it are silent risk.

**Target:** Report rate should exceed click rate within 12 months of a mature program.  
**Formula:** `(Phish Reports / Total Recipients) × 100`

---

### 3. Time-to-Report
**Definition:** Median time between phishing email delivery and a security report being filed.

Fast time-to-report is operationally valuable. If an employee reports within 15 minutes, your SOC has time to pull the email from inboxes before others click. If reports trickle in after 4 hours, the damage is done.

**Target:** Median < 30 minutes for mature programs.  
**Track:** P50, P75, P90 — not just the mean (outliers skew it badly).

---

### 4. Repeat Offender Percentage
**Definition:** Percentage of employees who clicked in 2+ campaigns within a rolling 90-day window.

Single clicks happen. Repeated clicks identify employees who aren't retaining training — whether due to role, cognitive load, or disengagement. These individuals need a different intervention, not more click-through modules.

**Formula:** `(Employees with 2+ clicks in 90 days / Total Employees) × 100`  
**Action threshold:** Any department above 8% repeat offenders warrants a targeted response.

---

### 5. Department-Level Risk Variance
**Definition:** Standard deviation of click rates across departments, normalized against company average.

This surfaces organizational risk concentration. A company-average 6% click rate looks fine until you see that Finance is at 18% and Engineering is at 2%. The aggregate hides the risk.

**Use this for:** Board reporting, targeted training investment, insurance risk assessments.  
**Visualization:** Heat map by department × campaign type.

---

## Metrics That Don't Matter (and Why)

| Metric | Why It's Misleading |
|---|---|
| **Training completion rate** | Tells you who clicked "Next." Tells you nothing about retention or behavior change. |
| **Quiz scores** | Gameable, momentary. Correlation with real-world behavior is weak. |
| **Email open rate** | Not a security metric. Also increasingly unreliable due to email client pre-fetching. |
| **Campaign volume** | More simulations ≠ better outcomes. Quality and spacing matter more than frequency. |
| **Average click rate (no segmentation)** | Organizational averages hide the departments that need help. Always segment. |

---

## Repository Structure

```
/dashboards/       - Importable Grafana, Looker Studio, Metabase configs
/scripts/          - Python scripts for GoPhish data export, ROI calculation, variance analysis
/docs/             - Benchmarks, methodology, executive reporting templates
/templates/        - Quarterly review and board deck markdown templates
```

---

## HailBytes SAT Integration

All five of the metrics above — click rate trend, report rate, time-to-report, repeat offenders, and department variance — are tracked automatically in **[HailBytes SAT](https://hailbytes.com)**, with pre-built dashboards and board-ready export.

**This repo helps you build them yourself if you're self-hosting GoPhish.** The scripts here pull from the GoPhish API and calculate the same metrics. The dashboard templates work with open-source BI tools.

If you reach the point where maintaining the measurement infrastructure costs more than the program itself, that's typically when teams move to a managed platform.

---

## Quick Start

```bash
# 1. Export your GoPhish data
python scripts/gophish-export.py --api-key YOUR_KEY --output campaigns.json

# 2. Calculate ROI
python scripts/calculate-roi.py --data campaigns.json

# 3. Identify high-risk departments
python scripts/department-variance.py --data campaigns.json
```

See [`/scripts/`](scripts/) for full documentation on each script.

---

## Contributing

PRs welcome. If you have industry benchmark data, GoPhish dashboard configs, or ROI calculation methodologies to share, open an issue or submit directly.

---

## License

MIT
