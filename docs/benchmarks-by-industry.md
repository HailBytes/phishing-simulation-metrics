# Industry Phishing Benchmarks

Reference benchmarks for contextualizing your organization's phishing simulation metrics. Use these to set targets and frame board reporting.

> ⚠️ **Methodology note:** Benchmark comparability is limited. Vendors use different simulation templates, difficulty levels, and employee populations. Use these as directional reference points, not precise targets.

---

## Click Rate Benchmarks by Industry

### Proofpoint "State of the Phish" 2024
*Source: https://www.proofpoint.com/us/resources/threat-reports/state-of-phish*

| Industry | Avg Click Rate | Notes |
|---|---|---|
| Healthcare | 22% | Highest-risk sector; time pressure, low security literacy |
| Finance | 14% | Regulated; training investment higher |
| Education | 25% | Large, diverse user base; personal devices |
| Government | 18% | Legacy systems; budget-constrained training |
| Technology | 8% | Higher baseline security awareness |
| Retail | 19% | High turnover; seasonal workforce |
| Manufacturing | 17% | OT/IT convergence; less digitally native workforce |
| Legal | 16% | High-value targets; small IT teams |

### Verizon DBIR 2024 (Phishing as Initial Access)
*Source: https://www.verizon.com/business/resources/reports/dbir/*

- **36% of breaches** involved phishing as the initial access vector (2024)
- Median time for a user to click a phishing link: **21 seconds** after delivery
- Organizations with formal SAT programs: **~50% lower click rate** vs. untrained orgs

### KnowBe4 Phishing Industry Benchmarks 2023
*Source: https://www.knowbe4.com/phishing-industry-benchmarks*

| Org Size | Baseline Phish-Prone % | After 12 months training |
|---|---|---|
| 1–249 | 33.2% | 18.5% |
| 250–999 | 28.6% | 14.4% |
| 1,000–9,999 | 29.3% | 12.1% |
| 10,000+ | 25.2% | 10.7% |

**Key finding:** Most click rate reduction happens in the first 90 days. The difference between month 3 and month 12 is much smaller than baseline → month 3.

### SANS Security Awareness Report 2024
*Source: https://www.sans.org/security-awareness-training/resources/reports/*

- **70% of organizations** still use phishing simulation as primary measurement method
- Only **28%** track report rate as a primary metric
- Organizations that track report rate have **measurably better incident response outcomes**

---

## Report Rate Benchmarks

Industry-wide benchmarks for report rate are less commonly published than click rate. Available data:

| Source | Typical Report Rate | Notes |
|---|---|---|
| Proofpoint 2024 | 2–13% | Wide range; depends heavily on reporting button availability |
| KnowBe4 2023 | 10–22% (mature programs) | After 12+ months with a phish alert button |
| Tessian 2023 | 7% median | Email gateway vendor; may undersample smaller orgs |

**The benchmark that matters:** Your report rate should exceed your click rate within 12 months. If you're at a 6% click rate and 4% report rate after a year of training, the program is underperforming.

---

## Time-to-Report Benchmarks

No authoritative industry study tracks this metric at scale. Based on vendor data and published incident response research:

| Maturity Level | Median Time-to-Report |
|---|---|
| Immature (no reporting button) | 4–24 hours |
| Developing (button deployed, <6 months) | 60–120 minutes |
| Mature (button + reinforcement) | 15–45 minutes |
| Leading (culture of reporting) | <15 minutes |

**SOC value:** Every minute faster reduces the blast radius. A 15-minute median TTR in a 500-person org can prevent dozens of additional compromises before the SOC can pull the phishing email.

---

## Repeat Offender Benchmarks

No authoritative published benchmarks exist for repeat offender rates. Internal benchmarks from practitioners:

- **<5%** repeat offender rate (90-day window): Program is working
- **5–10%:** Investigate specific departments and roles
- **>10%:** Training modality mismatch — consider role-based interventions

---

## Setting Your Targets

Suggested targets for a mature program (12–18 months in):

| Metric | Conservative Target | Aggressive Target |
|---|---|---|
| Click rate | <10% | <5% |
| Report rate | >click rate | 2× click rate |
| Median time-to-report | <60 min | <20 min |
| Repeat offender % | <8% | <4% |
| High-risk dept variance | <5pp above avg | <2pp above avg |

---

## Caveats on Benchmark Use

1. **Template difficulty matters more than org size.** A simulated credential-harvest landing page will always have higher click rates than a simple link-in-email test. Don't compare cross-vendor without normalizing difficulty.

2. **Benchmarks measure the wrong thing.** The goal isn't to have the lowest click rate in your industry — it's to have a trending improvement and a high report rate. A 6% click rate that's been flat for 18 months is worse than a 14% click rate that's down from 28%.

3. **Self-reported data is biased.** KnowBe4 and Proofpoint data reflects their customer base, which skews toward organizations that have already bought security training. Real-world rates in untrained orgs are likely higher.
