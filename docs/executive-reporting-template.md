# Executive Reporting Template — Phishing Simulation Program

Use this template to communicate program performance to CISOs, CFOs, and boards. The goal is to answer three questions a non-technical executive actually cares about:

1. Is the program working?
2. Are we at risk right now?
3. Is it worth the money?

---

## Quarterly Email Summary (CISO → C-Suite)

**Subject:** Security Awareness Training — Q[X] Update

---

**Program Status:** [On Track / Needs Attention / Critical]

**This Quarter in 3 Numbers:**

| Metric | Q[X] | Q[X-1] | Trend |
|---|---|---|---|
| Click rate | [X]% | [X]% | ↓ [X]pp |
| Report rate | [X]% | [X]% | ↑ [X]pp |
| Median time-to-report | [X] min | [X] min | ↓ [X] min |

**Highlight:** [One sentence on the most notable change. E.g., "Finance department click rate dropped from 22% to 11% following targeted training in October."]

**Concern:** [One sentence on the biggest remaining risk. E.g., "Customer Support remains at 19% click rate and needs role-specific intervention."]

**Recommended Action:** [One thing you're asking for. E.g., "Approval to run mandatory re-training for repeat offenders — 37 employees, ~2h each."]

---

## Board-Level Slide Talking Points

### Slide 1: Why This Matters
- 36% of all breaches start with a phishing email (Verizon DBIR 2024)
- Average cost of a breach: $4.45M (IBM 2023)
- Our program directly reduces the probability of this initial access vector

### Slide 2: Our Numbers
- Present the trend chart — click rate from program start to today
- Frame it as: "Here's where we started. Here's where we are. Here's the trajectory."
- Avoid showing a single-quarter snapshot without context — trend is the story

### Slide 3: Risk Concentration
- Department variance heat map
- Identify the 2–3 departments with elevated risk by name
- Show what specific action is being taken for each

### Slide 4: ROI
- Use output from `calculate-roi.py`
- Frame: "We invested $[X]. Our estimated risk reduction is worth $[Y]. ROI is [Z]%."
- Acknowledge assumptions explicitly — this builds credibility with financially literate audiences

### Slide 5: What's Next
- Q[X+1] campaign schedule
- Specific interventions for high-risk departments
- Any tooling or budget asks

---

## Red Flags to Flag to the Board

These metrics, if present, should be explicitly surfaced — not buried:

| Condition | What to Say |
|---|---|
| Click rate flat for 2+ quarters | "Training modality isn't working. We need a different approach." |
| Report rate < click rate after 12 months | "Employees don't know how to report. This is a process gap, not a training gap." |
| Any department >1.5× company average | "We have a concentrated risk pocket. Here's the plan." |
| Repeat offender rate >10% | "We have employees who are not retaining training. We need targeted intervention." |
| Time-to-report >2 hours | "Even employees who recognize a phish aren't reporting in time for us to act." |

---

## What Not to Put in Executive Reports

- Raw GoPhish campaign IDs or technical configuration details
- Email open rates (not a security metric)
- Completion rates without behavioral outcomes
- Comparisons to vendor benchmarks without caveat about methodology
- Individual employee names (aggregate only, except in HR-routed repeat offender cases)
