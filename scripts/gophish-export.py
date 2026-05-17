#!/usr/bin/env python3
"""
gophish-export.py
Export campaign data from GoPhish API to JSON for downstream analysis.

Usage:
    python gophish-export.py --api-key YOUR_KEY --host https://localhost:3333 --output campaigns.json

Requirements:
    pip install requests
"""

import argparse
import json
import sys
import urllib3
from datetime import datetime

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_campaigns(host: str, api_key: str, verify_ssl: bool = False) -> list[dict]:
    """Fetch all campaigns from GoPhish API."""
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{host.rstrip('/')}/api/campaigns/"

    try:
        resp = requests.get(url, headers=headers, verify=verify_ssl, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Could not connect to GoPhish at {host}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: API returned {e.response.status_code}", file=sys.stderr)
        sys.exit(1)


def get_campaign_results(host: str, api_key: str, campaign_id: int, verify_ssl: bool = False) -> dict:
    """Fetch detailed results for a single campaign."""
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{host.rstrip('/')}/api/campaigns/{campaign_id}/results"

    resp = requests.get(url, headers=headers, verify=verify_ssl, timeout=30)
    resp.raise_for_status()
    return resp.json()


def normalize_campaign(campaign: dict, results: dict) -> dict:
    """Flatten campaign + results into a clean analysis-ready structure."""
    timeline = results.get("timeline", [])

    clicks = [e for e in timeline if e.get("message") == "Clicked Link"]
    reports = [e for e in timeline if e.get("message") == "Email Reported"]
    opens = [e for e in timeline if e.get("message") == "Email Opened"]

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
        # Per-recipient detail for repeat offender + dept variance analysis
        "recipients": [
            {
                "email": r.get("email"),
                "first_name": r.get("first_name"),
                "last_name": r.get("last_name"),
                "position": r.get("position"),
                "status": r.get("status"),
                "reported": any(
                    e.get("email") == r.get("email") and e.get("message") == "Email Reported"
                    for e in timeline
                ),
                "click_time": next(
                    (e.get("time") for e in timeline
                     if e.get("email") == r.get("email") and e.get("message") == "Clicked Link"),
                    None,
                ),
                "report_time": next(
                    (e.get("time") for e in timeline
                     if e.get("email") == r.get("email") and e.get("message") == "Email Reported"),
                    None,
                ),
            }
            for r in recipients
        ],
        "raw_timeline": timeline,
    }


def main():
    parser = argparse.ArgumentParser(description="Export GoPhish campaign data to JSON")
    parser.add_argument("--api-key", required=True, help="GoPhish API key")
    parser.add_argument("--host", default="https://localhost:3333", help="GoPhish host URL")
    parser.add_argument("--output", default="campaigns.json", help="Output file path")
    parser.add_argument("--no-ssl-verify", action="store_true", help="Disable SSL verification (self-signed certs)")
    parser.add_argument("--campaign-id", type=int, help="Export a single campaign by ID")
    args = parser.parse_args()

    verify = not args.no_ssl_verify

    print(f"Connecting to GoPhish at {args.host}...")
    campaigns = get_campaigns(args.host, args.api_key, verify)

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
            results = get_campaign_results(args.host, args.api_key, campaign["id"], verify)
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


if __name__ == "__main__":
    main()
