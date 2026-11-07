import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_click_rate_trend_uses_earliest_and_latest(roi):
    campaigns = [
        {"launch_date": "2024-03-01", "click_rate": 10.0},
        {"launch_date": "2024-01-01", "click_rate": 30.0},
        {"launch_date": "2024-02-01", "click_rate": 20.0},
    ]
    assert roi.get_click_rate_trend(campaigns) == (30.0, 10.0)
    assert roi.get_click_rate_trend([]) == (0.0, 0.0)


def test_calculate_roi_positive_when_click_rate_drops(roi):
    r = roi.calculate_roi(30.0, 10.0, 500, 50_000, 4_450_000, 0.36, 0.68, 0.30)
    assert r["click_rate_reduction"]["absolute_pp"] == 20.0
    assert r["click_rate_reduction"]["relative_pct"] == pytest.approx(66.7)
    assert r["financials"]["risk_reduction_value_usd"] > 0
    assert r["financials"]["roi_pct"] > 0


def test_calculate_roi_no_improvement_has_no_payback(roi):
    r = roi.calculate_roi(20.0, 20.0, 500, 50_000, 4_450_000, 0.36, 0.68, 0.30)
    assert r["financials"]["risk_reduction_value_usd"] == 0
    assert r["financials"]["payback_months"] == "N/A"


def test_extract_department(variance):
    assert variance.extract_department({"position": "Finance|Manager"}) == "Finance"
    assert variance.extract_department({"position": " HR "}) == "HR"
    assert variance.extract_department({}) == "Unknown"


def test_parse_ts(variance):
    assert variance.parse_ts("2024-01-01T00:00:00Z").tzinfo is not None
    assert variance.parse_ts("garbage") is None
    assert variance.parse_ts(None) is None


def test_normalize_campaign_rates(gophish):
    campaign = {"id": 1, "name": "Q1", "status": "Completed", "template": {"name": "T"}}
    results = {
        "results": [{"email": "a@x"}, {"email": "b@x"}, {"email": "c@x"}, {"email": "d@x"}],
        "timeline": [
            {"email": "a@x", "message": "Clicked Link", "time": "t1"},
            {"email": "b@x", "message": "Email Reported", "time": "t2"},
        ],
    }
    n = gophish.normalize_campaign(campaign, results)
    assert n["click_rate"] == 25.0 and n["report_rate"] == 25.0
    by_email = {r["email"]: r for r in n["recipients"]}
    assert by_email["a@x"]["click_time"] == "t1"
    assert by_email["b@x"]["reported"] is True


def test_resolve_api_key_requires_key(gophish, monkeypatch):
    monkeypatch.delenv("GOPHISH_API_KEY", raising=False)
    assert gophish.resolve_api_key("flag") == "flag"
    with pytest.raises(SystemExit):
        gophish.resolve_api_key(None)


def test_grafana_dashboard_is_valid_json():
    data = json.loads((ROOT / "dashboards" / "grafana-gophish.json").read_text(encoding="utf-8"))
    assert "panels" in data or "dashboard" in data
