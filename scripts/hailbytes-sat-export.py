#!/usr/bin/env python3
"""
hailbytes-sat-export.py
Export campaign data from HailBytes SAT to the campaigns.json format used by
calculate-roi.py and department-variance.py.

HailBytes SAT exposes a GoPhish-compatible REST API, so this script uses the
same endpoints as gophish-export.py. The output format is identical, making
all downstream analysis scripts (calculate-roi.py, department-variance.py)
and dashboard configs directly compatible.

Usage:
    # Recommended — set API key in environment:
    export SAT_API_KEY=your_key_here
    python hailbytes-sat-export.py --host https://your-sat-instance.example.com

    # Or pass via flag (visible in process list):
    python hailbytes-sat-export.py --host https://your-sat.example.com --api-key YOUR_KEY

    # Export a single campaign:
    python hailbytes-sat-export.py --host https://your-sat.example.com --campaign-id 42

Finding your API key in HailBytes SAT:
    Log in as an admin → Settings → API → copy the API key shown there.
    The key has full read access to campaigns and results.

Department field convention:
    SAT populates the "position" field in target groups. If you use the
    "Dept|Role" format (e.g., "Finance|Manager"), department-variance.py
    splits on "|" automatically. Consistent formatting across target groups
    is required for accurate department-level analysis.

Requirements:
    pip install requests
"""

import argparse
import json
import os
import sys
import urllib3
from datetime import datetime

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# HailBytes SAT uses the same GoPhish-compatible timeline message strings.
CLICK_EVENT = "Clicked Link"
REPORT_EVENT = "Email Reported"
OPEN_EVENT = "Email Opened"


def get_campaigns(host: str, api_key: str, verify_ssl: bool = True) -> list[dict]:
    """Fetch all campaigns from the SAT API."""
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{host.rstrip('/')}/api/campaigns/"

    try:
        resp = requests.get(url, headers=headers, verify=verify_ssl, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Could not connect to HailBytes SAT at {host}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status == 401:
            print("ERROR: Unauthorized — check your API key (Settings → API in the SAT admin UI)", file=sys.stderr)
        else:
            print(f"ERROR: API returned {status}", file=sys.stderr)
        sys.exit(1)


def get_campaign_results(host: str, api_key: str, campaign_id: int, verify_ssl: bool = True) -> dict:
    """Fetch detailed results for a single campaign."""
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{host.rstrip('/')}/api/campaigns/{campaign_id}/results"

    try:
        resp = requests.get(url, headers=headers, verify=verify_ssl, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(f"Connection failed: {e}") from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP {e.response.status_code}") from e


def normalize_campaign(campaign: dict, results: dict) -> dict:
    """
    Flatten campaign + results into the standard campaigns.json structure.

    The output schema is identical to gophish-export.py so that
    calculate-roi.py and department-variance.py work without modification.
    """
    timeline = results.get("timeline", [])

    clicks = [e for e in timeline if e.get("message") == CLICK_EVENT]
    reports = [e for e in timeline if e.get("message") == REPORT_EVENT]
    opens = [e for e in timeline if e.get("message") == OPEN_EVENT]

    recipients = results.get("results", [])
    total = len(recipients)

    return {
        "id": campaign["id"],
        "name": campaign["name"],
        "status": campaign["status"],
        "launch_date": campaign.get("launch_date"),
        "completed_date": campaign.get("completed_date"),
        "template": campaign.get("template", {}).get("name"),
        "total_recipients": total,
        "clicks": len(clicks),
        "reports": len(reports),
        "opens": len(opens),
        "click_rate": round(len(clicks) / total * 100, 2) if total else 0,
        "report_rate": round(len(reports) / total * 100, 2) if total else 0,
        "open_rate": round(len(opens) / total * 100, 2) if total else 0,
        # Per-recipient detail for repeat offender + dept variance analysis.
        # click_time and report_time are ISO 8601 strings (UTC, "Z"-suffixed).
        # report_time is set even when the recipient never clicked — reporters
        # who correctly identified the simulation without clicking are included.
        "recipients": [
            {
                "email": r.get("email"),
                "first_name": r.get("first_name"),
                "last_name": r.get("last_name"),
                "position": r.get("position"),
                "status": r.get("status"),
                "reported": any(
                    e.get("email") == r.get("email") and e.get("message") == REPORT_EVENT
                    for e in timeline
                ),
                "click_time": next(
                    (e.get("time") for e in timeline
                     if e.get("email") == r.get("email") and e.get("message") == CLICK_EVENT),
                    None,
                ),
                "report_time": next(
                    (e.get("time") for e in timeline
                     if e.get("email") == r.get("email") and e.get("message") == REPORT_EVENT),
                    None,
                ),
            }
            for r in recipients
        ],
        "raw_timeline": timeline,
    }


def resolve_api_key(flag_value: str | None) -> str:
    """Return the API key from --api-key flag or SAT_API_KEY env var."""
    if flag_value:
        return flag_value
    key = os.environ.get("SAT_API_KEY", "").strip()
    if not key:
        print(
            "ERROR: No API key provided. Set SAT_API_KEY environment variable "
            "or pass --api-key.\n"
            "Find your API key in the SAT admin UI under Settings → API.",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def main():
    parser = argparse.ArgumentParser(
        description="Export HailBytes SAT campaign data to campaigns.json"
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="SAT API key (default: SAT_API_KEY env var)",
    )
    parser.add_argument(
        "--host",
        required=True,
        help="HailBytes SAT host URL (e.g. https://sat.yourcompany.com)",
    )
    parser.add_argument("--output", default="campaigns.json", help="Output file path")
    parser.add_argument(
        "--no-ssl-verify",
        action="store_true",
        help="Disable SSL verification (only for local/dev SAT instances)",
    )
    parser.add_argument("--campaign-id", type=int, help="Export a single campaign by ID")
    args = parser.parse_args()

    api_key = resolve_api_key(args.api_key)
    verify = not args.no_ssl_verify

    print(f"Connecting to HailBytes SAT at {args.host}...")
    campaigns = get_campaigns(args.host, api_key, verify)

    if args.campaign_id:
        campaigns = [c for c in campaigns if c["id"] == args.campaign_id]
        if not campaigns:
            print(f"ERROR: Campaign {args.campaign_id} not found", file=sys.stderr)
            sys.exit(1)

    print(f"Found {len(campaigns)} campaign(s). Fetching results...")

    output = []
    for i, campaign in enumerate(campaigns, 1):
        print(f"  [{i}/{len(campaigns)}] {campaign['name']}", end="", flush=True)
        try:
            results = get_campaign_results(args.host, api_key, campaign["id"], verify)
            normalized = normalize_campaign(campaign, results)
            output.append(normalized)
            print(f" ✓  ({normalized['total_recipients']} recipients, "
                  f"{normalized['click_rate']}% click rate)")
        except Exception as e:
            print(f" ✗  ({e})")

    with open(args.output, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nExported {len(output)} campaign(s) to {args.output}")
    total_recipients = sum(c["total_recipients"] for c in output)
    avg_click = sum(c["click_rate"] for c in output) / len(output) if output else 0
    avg_report = sum(c["report_rate"] for c in output) / len(output) if output else 0
    print(f"Summary: {total_recipients} total recipients | "
          f"{avg_click:.1f}% avg click rate | {avg_report:.1f}% avg report rate")
    print(f"\nNext steps:")
    print(f"  python calculate-roi.py --data {args.output}")
    print(f"  python department-variance.py --data {args.output}")


if __name__ == "__main__":
    main()
