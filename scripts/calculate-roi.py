#!/usr/bin/env python3
"""
calculate-roi.py
Calculate ROI of a phishing simulation + security awareness training program.

Given click rate reduction data and breach cost assumptions, this script outputs
a structured ROI calculation suitable for executive and board reporting.

Usage:
    python calculate-roi.py --data campaigns.json
    python calculate-roi.py --manual  # walk through assumptions interactively

Methodology based on:
- Ponemon Institute "Cost of a Data Breach" annual report
- SANS Security Awareness ROI framework
- Verizon DBIR phishing incident cost data

Full methodology: ../docs/roi-calculation-methodology.md
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────────
# Default breach cost assumptions (override with --breach-cost and related flags)
# Source: IBM/Ponemon Cost of a Data Breach Report 2023
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_ASSUMPTIONS = {
    "avg_breach_cost_usd": 4_450_000,       # Global average breach cost (2023)
    "phishing_breach_probability": 0.36,    # % of breaches that start with phishing (DBIR 2023)
    "credential_compromise_rate": 0.68,     # % of phishing clicks that lead to credential entry
    "detection_containment_factor": 0.30,   # Reduction in cost if detected early (SOC maturity)
    "employees": 500,                        # Override with --employees
    "program_annual_cost_usd": 50_000,      # Override with --program-cost
}


def load_campaigns(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def get_click_rate_trend(campaigns: list[dict]) -> tuple[float, float]:
    """Return (baseline_click_rate, current_click_rate) from campaign data."""
    if not campaigns:
        return 0.0, 0.0

    # Sort by launch date
    sorted_campaigns = sorted(
        [c for c in campaigns if c.get("launch_date")],
        key=lambda c: c["launch_date"]
    )

    if len(sorted_campaigns) < 2:
        rate = sorted_campaigns[0]["click_rate"] if sorted_campaigns else 0.0
        return rate, rate

    baseline = sorted_campaigns[0]["click_rate"]
    current = sorted_campaigns[-1]["click_rate"]
    return baseline, current


def calculate_roi(
    baseline_click_rate: float,
    current_click_rate: float,
    employees: int,
    program_annual_cost: float,
    breach_cost: float,
    phishing_breach_prob: float,
    credential_rate: float,
    detection_factor: float,
) -> dict:
    """Core ROI calculation."""

    # Risk reduction
    absolute_reduction = baseline_click_rate - current_click_rate  # percentage points
    relative_reduction = (absolute_reduction / baseline_click_rate * 100) if baseline_click_rate else 0

    # Expected credential compromises per campaign at baseline vs. current
    baseline_compromises = employees * (baseline_click_rate / 100) * credential_rate
    current_compromises = employees * (current_click_rate / 100) * credential_rate
    compromise_reduction = baseline_compromises - current_compromises

    # Expected breach probability reduction
    # Simplified: each credential compromise has P(breach) based on DBIR data
    breach_prob_per_compromise = phishing_breach_prob / max(baseline_compromises, 1)
    baseline_annual_breach_prob = min(baseline_compromises * breach_prob_per_compromise, 1.0)
    current_annual_breach_prob = min(current_compromises * breach_prob_per_compromise, 1.0)

    # Expected loss (annualized)
    baseline_expected_loss = baseline_annual_breach_prob * breach_cost * (1 - detection_factor)
    current_expected_loss = current_annual_breach_prob * breach_cost * (1 - detection_factor)
    risk_reduction_value = baseline_expected_loss - current_expected_loss

    # ROI
    net_benefit = risk_reduction_value - program_annual_cost
    roi_pct = (net_benefit / program_annual_cost * 100) if program_annual_cost else 0
    payback_months = (program_annual_cost / risk_reduction_value * 12) if risk_reduction_value > 0 else float("inf")

    return {
        "inputs": {
            "employees": employees,
            "baseline_click_rate_pct": baseline_click_rate,
            "current_click_rate_pct": current_click_rate,
            "program_annual_cost_usd": program_annual_cost,
            "assumed_breach_cost_usd": breach_cost,
        },
        "click_rate_reduction": {
            "absolute_pp": round(absolute_reduction, 2),
            "relative_pct": round(relative_reduction, 1),
        },
        "risk_model": {
            "baseline_credential_compromises_per_campaign": round(baseline_compromises, 1),
            "current_credential_compromises_per_campaign": round(current_compromises, 1),
            "compromise_reduction": round(compromise_reduction, 1),
            "baseline_annual_breach_probability_pct": round(baseline_annual_breach_prob * 100, 2),
            "current_annual_breach_probability_pct": round(current_annual_breach_prob * 100, 2),
        },
        "financials": {
            "baseline_annualized_expected_loss_usd": round(baseline_expected_loss),
            "current_annualized_expected_loss_usd": round(current_expected_loss),
            "risk_reduction_value_usd": round(risk_reduction_value),
            "program_annual_cost_usd": round(program_annual_cost),
            "net_annual_benefit_usd": round(net_benefit),
            "roi_pct": round(roi_pct, 1),
            "payback_months": round(payback_months, 1) if payback_months != float("inf") else "N/A",
        },
    }


def print_report(result: dict):
    i = result["inputs"]
    cr = result["click_rate_reduction"]
    rm = result["risk_model"]
    fin = result["financials"]

    print("\n" + "═" * 60)
    print("  PHISHING SIMULATION PROGRAM ROI ANALYSIS")
    print("═" * 60)
    print(f"\nOrg size:          {i['employees']:,} employees")
    print(f"Program cost:      ${i['program_annual_cost_usd']:,.0f}/year")
    print(f"Breach assumption: ${i['assumed_breach_cost_usd']:,.0f} (IBM/Ponemon 2023)")

    print(f"\n{'CLICK RATE REDUCTION':─<50}")
    print(f"  Baseline:  {i['baseline_click_rate_pct']}%")
    print(f"  Current:   {i['current_click_rate_pct']}%")
    print(f"  Reduction: {cr['absolute_pp']} pp ({cr['relative_pct']}% relative)")

    print(f"\n{'RISK MODEL':─<50}")
    print(f"  Credential compromises avoided per campaign: {rm['compromise_reduction']:.0f}")
    print(f"  Annual breach probability before: {rm['baseline_annual_breach_probability_pct']}%")
    print(f"  Annual breach probability after:  {rm['current_annual_breach_probability_pct']}%")

    print(f"\n{'FINANCIAL IMPACT':─<50}")
    print(f"  Risk reduction value:  ${fin['risk_reduction_value_usd']:>12,.0f}/year")
    print(f"  Program cost:          ${fin['program_annual_cost_usd']:>12,.0f}/year")
    print(f"  Net benefit:           ${fin['net_annual_benefit_usd']:>12,.0f}/year")
    print(f"  ROI:                   {fin['roi_pct']}%")
    print(f"  Payback period:        {fin['payback_months']} months")
    print("\n" + "═" * 60)
    print("NOTE: This model uses industry averages. Actual breach costs")
    print("vary significantly by industry, org size, and IR maturity.")
    print("See docs/roi-calculation-methodology.md for full methodology.")
    print("═" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Calculate phishing simulation program ROI")
    parser.add_argument("--data", help="Path to campaigns.json from gophish-export.py")
    parser.add_argument("--baseline-click-rate", type=float, help="Baseline click rate %% (override)")
    parser.add_argument("--current-click-rate", type=float, help="Current click rate %% (override)")
    parser.add_argument("--employees", type=int, default=DEFAULT_ASSUMPTIONS["employees"])
    parser.add_argument("--program-cost", type=float, default=DEFAULT_ASSUMPTIONS["program_annual_cost_usd"],
                        help="Annual program cost in USD")
    parser.add_argument("--breach-cost", type=float, default=DEFAULT_ASSUMPTIONS["avg_breach_cost_usd"],
                        help="Assumed breach cost in USD (default: IBM/Ponemon 2023 average)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted report")
    args = parser.parse_args()

    if args.data:
        campaigns = load_campaigns(args.data)
        baseline, current = get_click_rate_trend(campaigns)
        print(f"Loaded {len(campaigns)} campaign(s) from {args.data}")
    elif args.baseline_click_rate is not None and args.current_click_rate is not None:
        baseline = args.baseline_click_rate
        current = args.current_click_rate
    else:
        parser.error("Provide --data OR both --baseline-click-rate and --current-click-rate")
        sys.exit(1)

    if args.baseline_click_rate:
        baseline = args.baseline_click_rate
    if args.current_click_rate:
        current = args.current_click_rate

    result = calculate_roi(
        baseline_click_rate=baseline,
        current_click_rate=current,
        employees=args.employees,
        program_annual_cost=args.program_cost,
        breach_cost=args.breach_cost,
        phishing_breach_prob=DEFAULT_ASSUMPTIONS["phishing_breach_probability"],
        credential_rate=DEFAULT_ASSUMPTIONS["credential_compromise_rate"],
        detection_factor=DEFAULT_ASSUMPTIONS["detection_containment_factor"],
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
