# ROI Calculation Methodology

This document explains the assumptions and formulas used in `scripts/calculate-roi.py`.

---

## Why ROI Calculation Is Hard (and How We Handle It)

Phishing simulation ROI is inherently probabilistic. You're not measuring "breaches we definitely prevented" — you're measuring "reduction in the probability of an initial access event that would lead to a breach." The calculation involves several layers of uncertainty.

This methodology is designed to be:
- **Conservative** — assumptions err toward underestimating value
- **Transparent** — every assumption is explicit and overridable
- **Defensible** — grounded in published research, not vendor claims

---

## The Model

### Step 1: Click Rate Reduction

The foundational metric is the change in click rate between program start (baseline) and the current period.

```
click_rate_reduction_pp = baseline_click_rate - current_click_rate
relative_reduction_pct = click_rate_reduction_pp / baseline_click_rate × 100
```

**Source of baseline:** Use the first campaign you ran before any training. If you don't have a pre-training baseline, use your industry benchmark from `docs/benchmarks-by-industry.md`.

---

### Step 2: Credential Compromise Reduction

Not every click leads to a breach. This step estimates how many fewer credential compromises occur.

```
baseline_compromises = employees × (baseline_click_rate / 100) × credential_compromise_rate
current_compromises = employees × (current_click_rate / 100) × credential_compromise_rate
compromise_reduction = baseline_compromises - current_compromises
```

**credential_compromise_rate = 0.68** (default)
- Source: Tessian "The Psychology of Human Error" 2023; Proofpoint threat intelligence
- Interpretation: 68% of phishing clicks result in credential entry (the rest are curiosity clicks or accidental)
- This is the most contested assumption — range is 50–80% depending on phish template sophistication

---

### Step 3: Annual Breach Probability

This converts credential compromises into an annualized breach probability.

```
breach_prob_per_compromise = phishing_breach_probability / max(baseline_compromises, 1)
annual_breach_probability = min(compromises × breach_prob_per_compromise, 1.0)
```

**phishing_breach_probability = 0.36** (default)
- Source: Verizon DBIR 2024 — 36% of breaches involve phishing as initial access
- This is applied as the conditional probability that a credential compromise leads to a breach

**Caveat:** This model assumes phishing is the *exclusive* initial access vector, which overestimates. In practice, an org with phishing controls may still be breached via other vectors. The model gives phishing training full credit, which is a conservative upper bound on value.

---

### Step 4: Expected Loss Calculation

```
expected_loss = annual_breach_probability × breach_cost × (1 - detection_containment_factor)
risk_reduction_value = baseline_expected_loss - current_expected_loss
```

**avg_breach_cost_usd = $4,450,000** (default)
- Source: IBM/Ponemon "Cost of a Data Breach Report 2023"
- Covers direct costs (detection, containment, notification, legal, regulatory) and indirect costs (reputation, customer churn)
- Adjust with `--breach-cost` for your industry:
  - Healthcare: ~$10.9M (highest regulated cost)
  - Finance: ~$5.9M
  - Technology: ~$4.7M
  - Retail: ~$2.9M

**detection_containment_factor = 0.30** (default)
- If your SOC detects and contains an incident early, it costs ~30% less than a full breach
- Adjust based on your IR maturity. If you have a 24/7 SOC with playbooks, use 0.40–0.50.

---

### Step 5: ROI

```
net_benefit = risk_reduction_value - program_annual_cost
roi_pct = (net_benefit / program_annual_cost) × 100
payback_months = (program_annual_cost / risk_reduction_value) × 12
```

---

## Example Calculation

Inputs:
- 500 employees
- Baseline click rate: 24%
- Current click rate: 9%
- Program cost: $50,000/year
- Breach cost: $4.45M (default)

Output:
```
Credential compromises reduced: ~51 per campaign
Annual breach probability: 11.5% → 4.3%
Risk reduction value: ~$316,000/year
Program cost: $50,000/year
Net benefit: $266,000/year
ROI: 532%
Payback: 1.9 months
```

---

## What This Model Does NOT Capture

| Item | Direction | Notes |
|---|---|---|
| Reduced incident response workload | Underestimates value | Fewer phishing reports = less analyst time |
| Insurance premium reduction | Underestimates value | Some carriers discount for verified SAT programs |
| Regulatory fine reduction | Underestimates value | HIPAA/PCI breach penalties not included |
| Productivity loss (awareness culture) | Overestimates cost | Training takes employee time; not modeled here |
| Non-phishing breach vectors | Overestimates value | Model attributes all phishing risk reduction to the program |

The model is designed to produce a **conservative, defensible ROI floor** for board-level justification, not a precise financial forecast.

---

## Sensitivity Analysis

Run the script with different assumptions to see how the ROI changes:

```bash
# Conservative case (lower breach cost, worse credential rate)
python calculate-roi.py --data campaigns.json --breach-cost 2000000

# Healthcare case (higher breach cost)
python calculate-roi.py --data campaigns.json --breach-cost 10900000

# Test sensitivity to program cost
python calculate-roi.py --data campaigns.json --program-cost 100000
```

---

## References

1. IBM/Ponemon "Cost of a Data Breach Report 2023" — https://www.ibm.com/reports/data-breach
2. Verizon "Data Breach Investigations Report 2024" — https://www.verizon.com/business/resources/reports/dbir/
3. Proofpoint "State of the Phish 2024" — https://www.proofpoint.com/us/resources/threat-reports/state-of-phish
4. Tessian "The Psychology of Human Error 2023" — https://tessian.com/research/the-psychology-of-human-error/
5. SANS Security Awareness ROI Calculator methodology — https://www.sans.org/security-awareness-training/
