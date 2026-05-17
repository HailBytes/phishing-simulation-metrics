#!/usr/bin/env python3
"""
department-variance.py
Identify high-risk departments in GoPhish campaign data.

Calculates click rate, report rate, repeat offender %, and risk score
per department (using the "position" field in GoPhish recipient data).

Usage:
    python department-variance.py --data campaigns.json
    python department-variance.py --data campaigns.json --output variance-report.json
    python department-variance.py --data campaigns.json --threshold 10  # flag depts above 10% click rate

Requirements:
    pip install tabulate
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def load_campaigns(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def extract_department(recipient: dict) -> str:
    """Infer department from position field. Adjust for your GoPhish setup."""
    position = recipient.get("position", "").strip()
    if not position:
        return "Unknown"
    # If position contains dept|role (common GoPhish convention), split on |
    if "|" in position:
        return position.split("|")[0].strip()
    return position


def analyze_departments(campaigns: list[dict], window_days: int = 90) -> dict:
    """
    Aggregate per-recipient metrics across all campaigns.
    Returns a dict keyed by department with aggregated stats.
    """
    def _empty_dept() -> dict:
        return {
            "total_sends": 0,
            "clicks": 0,
            "reports": 0,
            "employees_seen": set(),
            "employee_click_counts": defaultdict(int),
            "report_times_seconds": [],
        }

    dept_stats: dict[str, dict] = defaultdict(_empty_dept)

    # Track click timestamps per employee for repeat offender window calc
    employee_clicks: dict[str, list[str]] = defaultdict(list)

    for campaign in campaigns:
        launch_date = campaign.get("launch_date", "")
        for r in campaign.get("recipients", []):
            dept = extract_department(r)
            email = r.get("email", "unknown")

            dept_stats[dept]["total_sends"] += 1
            dept_stats[dept]["employees_seen"].add(email)

            if r.get("status") in ("Clicked Link", "Submitted Data"):
                dept_stats[dept]["clicks"] += 1
                dept_stats[dept]["employee_click_counts"][email] += 1
                if r.get("click_time"):
                    employee_clicks[email].append(r["click_time"])

            if r.get("reported"):
                dept_stats[dept]["reports"] += 1
                if r.get("click_time") and r.get("report_time"):
                    try:
                        click_dt = datetime.fromisoformat(r["click_time"].rstrip("Z"))
                        report_dt = datetime.fromisoformat(r["report_time"].rstrip("Z"))
                        delta = (report_dt - click_dt).total_seconds()
                        if 0 < delta < 86400:  # Exclude outliers > 24h
                            dept_stats[dept]["report_times_seconds"].append(delta)
                    except (ValueError, TypeError):
                        pass

    # Compute repeat offenders within any 90-day window (simplified: across all campaigns)
    results = {}
    company_total_sends = sum(v["total_sends"] for v in dept_stats.values())
    company_total_clicks = sum(v["clicks"] for v in dept_stats.values())
    company_avg_click_rate = (company_total_clicks / company_total_sends * 100) if company_total_sends else 0

    for dept, stats in dept_stats.items():
        total = stats["total_sends"]
        clicks = stats["clicks"]
        reports = stats["reports"]
        employees = len(stats["employees_seen"])

        click_rate = round(clicks / total * 100, 2) if total else 0
        report_rate = round(reports / total * 100, 2) if total else 0

        # Repeat offenders: employees with 2+ clicks across all campaigns
        repeat_offenders = sum(1 for count in stats["employee_click_counts"].values() if count >= 2)
        repeat_offender_pct = round(repeat_offenders / employees * 100, 1) if employees else 0

        # Median time-to-report
        times = sorted(stats["report_times_seconds"])
        median_time_min = round(times[len(times) // 2] / 60, 1) if times else None

        # Risk variance vs. company average
        variance = round(click_rate - company_avg_click_rate, 2)
        risk_level = (
            "CRITICAL" if click_rate > company_avg_click_rate * 1.5
            else "HIGH" if click_rate > company_avg_click_rate * 1.2
            else "AVERAGE" if abs(variance) <= company_avg_click_rate * 0.1
            else "LOW"
        )

        results[dept] = {
            "department": dept,
            "employees": employees,
            "total_sends": total,
            "clicks": clicks,
            "click_rate_pct": click_rate,
            "reports": reports,
            "report_rate_pct": report_rate,
            "repeat_offenders": repeat_offenders,
            "repeat_offender_pct": repeat_offender_pct,
            "median_time_to_report_min": median_time_min,
            "variance_from_avg_pp": variance,
            "risk_level": risk_level,
        }

    return {
        "company_avg_click_rate_pct": round(company_avg_click_rate, 2),
        "total_campaigns_analyzed": len(campaigns),
        "departments": dict(sorted(results.items(), key=lambda x: x[1]["click_rate_pct"], reverse=True)),
    }


def print_table(analysis: dict, threshold: Optional[float] = None):
    print(f"\nCompany average click rate: {analysis['company_avg_click_rate_pct']}%")
    print(f"Campaigns analyzed: {analysis['total_campaigns_analyzed']}\n")

    rows = []
    for dept, stats in analysis["departments"].items():
        if threshold and stats["click_rate_pct"] < threshold:
            continue
        flag = "🚨" if stats["risk_level"] == "CRITICAL" else "⚠️ " if stats["risk_level"] == "HIGH" else "  "
        rows.append([
            f"{flag} {dept}",
            stats["employees"],
            f"{stats['click_rate_pct']}%",
            f"{stats['report_rate_pct']}%",
            f"{stats['repeat_offender_pct']}%",
            f"{stats['median_time_to_report_min']} min" if stats["median_time_to_report_min"] else "—",
            f"{'+' if stats['variance_from_avg_pp'] >= 0 else ''}{stats['variance_from_avg_pp']}pp",
            stats["risk_level"],
        ])

    headers = ["Department", "Employees", "Click Rate", "Report Rate", "Repeat Offenders", "Median TTR", "vs Avg", "Risk"]

    if HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    else:
        # Fallback: simple formatting
        print("  ".join(f"{h:<18}" for h in headers))
        print("─" * 120)
        for row in rows:
            print("  ".join(f"{str(v):<18}" for v in row))

    # Flag departments requiring intervention
    critical = [d for d, s in analysis["departments"].items() if s["risk_level"] == "CRITICAL"]
    high_repeat = [d for d, s in analysis["departments"].items() if s["repeat_offender_pct"] > 8]

    if critical:
        print(f"\n🚨 CRITICAL departments (>1.5x avg): {', '.join(critical)}")
        print("   Recommended: Direct manager outreach + targeted training")
    if high_repeat:
        print(f"\n⚠️  High repeat offenders (>8%): {', '.join(high_repeat)}")
        print("   Recommended: 1:1 security coaching, not additional e-learning")


def main():
    parser = argparse.ArgumentParser(description="Department-level phishing risk variance analysis")
    parser.add_argument("--data", required=True, help="Path to campaigns.json from gophish-export.py")
    parser.add_argument("--output", help="Save full analysis to JSON file")
    parser.add_argument("--threshold", type=float, help="Only show departments above this click rate %%")
    args = parser.parse_args()

    campaigns = load_campaigns(args.data)
    print(f"Analyzing {len(campaigns)} campaign(s)...")

    analysis = analyze_departments(campaigns)

    print_table(analysis, threshold=args.threshold)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(analysis, f, indent=2)
        print(f"\nFull analysis saved to {args.output}")


if __name__ == "__main__":
    main()
