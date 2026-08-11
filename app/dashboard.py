from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"
DASHBOARD_PATH = REPO_ROOT / "config" / "dashboard.yaml"


def load_records(path: Path = LOG_PATH) -> list[dict[str, Any]]:
    """Load valid JSON objects and ignore malformed lines for dashboard resilience."""
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            records.append(item)
    return records


def filter_recent(records: list[dict[str, Any]], minutes: int = 60) -> list[dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    result = []
    for record in records:
        try:
            timestamp = datetime.fromisoformat(str(record["ts"]).replace("Z", "+00:00"))
        except (KeyError, TypeError, ValueError):
            continue
        if timestamp >= cutoff:
            result.append(record)
    return result


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * p / 100
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    responses = [r for r in records if r.get("event") == "response_sent"]
    received = [r for r in records if r.get("event") == "request_received"]
    failed = [r for r in records if r.get("event") == "request_failed"]
    latencies = [float(r["latency_ms"]) for r in responses if isinstance(r.get("latency_ms"), (int, float))]
    costs = [float(r["cost_usd"]) for r in responses if isinstance(r.get("cost_usd"), (int, float))]
    quality = [float(r["quality_score"]) for r in responses if isinstance(r.get("quality_score"), (int, float))]
    return {
        "latency_ms": {f"p{p}": round(percentile(latencies, p), 2) for p in (50, 95, 99)},
        "traffic": {"count": len(received), "requests_per_minute": round(len(received) / 60, 2)},
        "errors": {"rate_pct": round(len(failed) / len(received) * 100, 2) if received else 0.0, "breakdown": dict(Counter(r.get("error_type", "unknown") for r in failed))},
        "cost": {"total_usd": round(sum(costs), 6)},
        "tokens": {"tokens_in": sum(int(r.get("tokens_in", 0)) for r in responses), "tokens_out": sum(int(r.get("tokens_out", 0)) for r in responses)},
        "quality": {"mean": round(sum(quality) / len(quality), 4) if quality else 0.0},
    }


def dashboard_html() -> str:
    config = yaml.safe_load(DASHBOARD_PATH.read_text(encoding="utf-8"))
    dashboard = config["dashboard"]
    summary = summarize(filter_recent(load_records(), dashboard["time_range_minutes"]))
    cards = []
    for panel in dashboard["panels"]:
        cards.append(f"<section><h2>{panel['title']}</h2><p>Unit: {panel['unit']} · Threshold: {panel['threshold']['operator']} {panel['threshold']['value']} ({panel['threshold']['aggregation']})</p><pre>{json.dumps(summary.get(panel['id'], {}), indent=2)}</pre></section>")
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>{dashboard['title']}</title><meta http-equiv='refresh' content='{dashboard['refresh_seconds']}'><style>body{{font-family:system-ui;max-width:1100px;margin:2rem auto;background:#f5f7fb;color:#172033}}main{{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}}section{{background:white;padding:1rem;border-radius:10px;box-shadow:0 1px 5px #ccd}}h1{{margin-bottom:.2rem}}pre{{white-space:pre-wrap}}</style></head><body><h1>{dashboard['title']}</h1><p>Time range: last {dashboard['time_range_minutes']} minutes · Refresh: {dashboard['refresh_seconds']} seconds · Source: data/logs.jsonl</p><main>{''.join(cards)}</main></body></html>"""
