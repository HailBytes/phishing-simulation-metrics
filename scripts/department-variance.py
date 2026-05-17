#!/usr/bin/env python3
"""
department-variance.py
Identify high-risk departments in GoPhish campaign data.

Calculates click rate, report rate, repeat offender %, and risk score
per department (using the "position" field in GoPhish recipient data).

Department field convention:
    This script reads the "position" field from each recipient. If you
    populate position as "Dept|Role" (e.g., "Finance|Manager"), the dept
    is extracted from the left side. Otherwise the full position value is
    used as-is. Set this consistently in your GoPhish target groups.

Usage:
    python department-variance.py --data campaigns.json
    python department-variance.py --data campaigns.json --output variance-report.json
    python department-variance.py --data campaigns.json --threshold 10  # flag depts above 10% click rate
    python department-variance.py --data campaigns.json --window 60     # 60-day repeat offender window

Requirements:
    pip install tabulate
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def load_campaigns(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def parse_ts(s: str | None) -> datetime | None:
    """Parse an ISO 8601 timestamp string (with or without Z suffix) to UTC datetime."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def extract_department(recipient: dict) -> str:
    """
    Infer department from position field.

    Supports two conventions:
      - "Finance"           → department is "Finance"
      - "Finance|Manager"   → department is "Finance" (role stripped)
    """
    position = recipient.get("position", "").strip()
    if not position:
        return "Unknown"
    if "|" in position:
        return position.split("|")[0].strip()
    return position


def _find_repeat_offenders(
    campaigns: list[dict], window_days: int
) -> set[str]:
    """
    Return the set of employee emails who clicked in 2+ campaigns within
    any rolling window of `window_days` days.
    """
    employee_click_timestamps: dict[str, list[datetime]] = defaultdict(list)

    for campaign in campaigns:
        for r in campaign.get("recipients", []):
            if r.get("status") not in ("Clicked Link", "Submitted Data"):
                continue
            ts = parse_ts(r.get("click_time"))
            if ts is None:
                # Fall back to campaign launch date when click_time is missing
                ts = parse_ts(campaign.get("launch_date"))
            if ts is not None:
                email = r.get("email", "unknown")
                employee_click_timestamps[email].append(ts)

    repeat_offenders: set[str] = set()
    cutoff = timedelta(days=window_days)

    for email, timestamps in employee_click_timestamps.items():
        if len(timestamps) < 2:
            continue
        for t in sorted(timestamps):
            window_clicks = sum(1 for other in timestamps if timedelta(0) <= other - t <= cutoff)
            if window_clicks >= 2:
                repeat_offenders.add(email)
                break

    return repeat_offenders


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
            "report_times_seconds": [],
        }

    dept_stats: dict[str, dict] = defaultdict(_empty_dept)

    repeat_offender_emails = _find_repeat_offenders(campaigns, window_days)

    for campaign in campaigns:
        launch_date = campaign.get("launch_date")
        for r in campaign.get("recipients", []):
            dept = extract_department(r)
            email = r.get("email", "unknown")

            dept_stats[dept]["total_sends"] += 1
            dept_stats[dept]["employees_seen"].add(email)

            if r.get("status") in ("Clicked Link", "Submitted Data"):
                dept_stats[dept]["clicks"] += 1

            if r.get("reported"):
                dept_stats[dept]["reports"] += 1

                report_ts = parse_ts(r.get("report_time"))
                if report_ts is not None:
                    # Use click_time as the reference when available (reporter
                    # clicked then reported). Fall back to campaign launch_date
                    # for reporters who identified the phish without clicking.
                    ref_ts = parse_ts(r.get("click_time")) or parse_ts(launch_date)
                    if ref_ts is not None:
                        delta = (report_ts - ref_ts).total_seconds()
                        if 0 < delta < 86400:  # Exclude outliers > 24h
                            dept_stats[dept]["report_times_seconds"].append(delta)

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

        repeat_offenders = sum(
            1 for email in stats["employees_seen"]
            if email in repeat_offender_emails
        )
        repeat_offender_pct = round(repeat_offenders / employees * 100, 1) if employees else 0

        times = sorted(stats["report_times_seconds"])
        median_time_min = round(times[len(times) // 2] / 60, 1) if times else None

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
        "repeat_offender_window_days": window_days,
        "total_campaigns_analyzed": len(campaigns),
        "departments": dict(sorted(results.items(), key=lambda x: x[1]["click_rate_pct"], reverse=True)),
    }


def print_table(analysis: dict, threshold: Optional[float] = None):
    window = analysis.get("repeat_offender_window_days", 90)
    print(f"\nCompany average click rate: {analysis['company_avg_click_rate_pct']}%")
    print(f"Campaigns analyzed: {analysis['total_campaigns_analyzed']} "
          f"(repeat offender window: {window} days)\n")

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
        print("  ".join(f"{h:<18}" for h in headers))
        print("─" * 120)
        for row in rows:
            print("  ".join(f"{str(v):<18}" for v in row))

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
    parser.add_argument(
        "--window",
        type=int,
        default=90,
        help="Rolling window in days for repeat offender detection (default: 90)",
    )
    args = parser.parse_args()

    campaigns = load_campaigns(args.data)
    print(f"Analyzing {len(campaigns)} campaign(s)...")

    analysis = analyze_departments(campaigns, window_days=args.window)

    print_table(analysis, threshold=args.threshold)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(analysis, f, indent=2)
        print(f"\nFull analysis saved to {args.output}")


if __name__ == "__main__":
    main()
