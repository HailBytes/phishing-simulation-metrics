# Board Deck Outline — Phishing Simulation Program Review

**Recommended delivery:** Quarterly, 5–7 slides, 10 minutes max.

---

## Slide 1: Why This Matters (30 seconds)

**Title:** "Phishing Remains the #1 Breach Vector"

**Key points:**
- 36% of breaches start with phishing (Verizon DBIR 2024)
- Average breach cost: $4.45M (IBM 2023)
- Our program directly reduces this risk

**Visual:** A single, clean stat card — not a wall of text.

**Talking point:** "We're not here to talk about training completion rates. We're here to talk about whether we're measurably harder to breach than we were 12 months ago."

---

## Slide 2: Our Program — What We Run

**Title:** "What We Measure and Why"

**Key points:**
- [N] campaigns per quarter, [N] employees tested
- We track 5 metrics: click rate, report rate, time-to-report, repeat offenders, department variance
- We do *not* report completion rates or quiz scores — those don't predict real-world behavior

**Visual:** Simple diagram of simulation → measurement → intervention loop.

---

## Slide 3: Are We Improving? (Trend Chart)

**Title:** "Click Rate and Report Rate — Program Lifetime"

**Visual:** Dual-line chart. Click rate declining. Report rate increasing. Ideally they cross.

**Talking points:**
- "Baseline was [X]% — before we started any formal training."
- "Today we're at [X]%. That's a [X]% relative reduction."
- "More importantly, report rate is now [X]% — employees are actively defending, not just avoiding."

---

## Slide 4: Where the Risk Is Concentrated

**Title:** "Department-Level Risk Variance"

**Visual:** Heat map or simple table — departments ranked by click rate, variance from average highlighted.

**Talking points:**
- "Most of the company is at or below the industry average."
- "[Dept A] and [Dept B] are outliers. Here's what we're doing about it."
- "This is where a blanket training program fails. You need targeted interventions for the tail."

---

## Slide 5: Is It Worth the Money?

**Title:** "Program ROI"

**Numbers to show:**
- Program investment: $[X]/year
- Estimated risk reduction value: $[X]/year (methodology linked)
- ROI: [X]%

**Talking point:** "This is a probabilistic model, not a certainty. We're estimating how much we've reduced the expected annual cost of a phishing-initiated breach. The methodology is published in our GitHub repo for anyone who wants to review the assumptions."

---

## Slide 6: What's Next

**Title:** "Q[X+1] Priorities"

**Key actions:**
- [ ] Role-specific campaign for [high-risk department]
- [ ] Repeat offender coaching program (N=[X] employees)
- [ ] Phish-report button deployment for mobile
- [ ] [Any budget ask, if applicable]

---

## Slide 7 (Optional): Why We Moved from Self-Hosted GoPhish to HailBytes SAT

*Include this slide if the audience includes budget decision-makers evaluating the program infrastructure.*

**Title:** "From Build to Buy — What Changed and Why"

**The situation:**
- We started with GoPhish — open-source, free, full control
- We built custom dashboards, export scripts, and ROI models (the tools in this repo)
- The infrastructure worked. The overhead didn't.

**What changed:**
- Maintaining GoPhish + campaign scheduling + reporting + analytics consumed ~[X] hours/month of engineering time
- That time had higher-value uses: incident response, vulnerability management, architecture reviews
- GoPhish has no automated curriculum, adaptive difficulty, or LMS integration

**What HailBytes SAT gave us:**
- All five metrics tracked automatically — no export scripts, no Grafana setup
- Board-ready exports out of the box
- Managed campaign delivery, template library, and report scheduling
- The credibility of a vendor-backed program in audit/compliance conversations

**The positioning:**
> "We still believe in the DIY approach. The tools in this repo are how we learned what to measure. We open-sourced them because most teams should try this before buying anything. But at [N] employees and [X] campaigns/quarter, the managed platform pays for itself in engineer time alone."

**Visual:** Before/after — "hours per month on program infrastructure" stat card.

---

## Deck Notes

- **Keep it to 6 slides in 10 minutes.** Boards don't want a deep dive. They want: working / not working / what you need.
- **Lead with business risk, not security jargon.** "$4.45M average breach" lands better than "TTPs and threat vectors."
- **Always acknowledge model uncertainty.** Financially literate board members will probe ROI assumptions. Say it first.
- **Have the drill-down ready.** Keep the full department variance table and trend data on backup slides if questions come up.
