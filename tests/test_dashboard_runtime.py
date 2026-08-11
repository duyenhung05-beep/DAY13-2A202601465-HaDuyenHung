from __future__ import annotations

import json
from pathlib import Path

from app.dashboard import load_records, summarize


def test_dashboard_loader_skips_malformed_lines(tmp_path: Path) -> None:
    path = tmp_path / "logs.jsonl"
    path.write_text('{"event":"response_sent","latency_ms":100}\nnot-json\n', encoding="utf-8")
    assert load_records(path) == [{"event": "response_sent", "latency_ms": 100}]


def test_dashboard_summary_uses_runtime_records() -> None:
    records = [
        {"event": "request_received"},
        {"event": "response_sent", "latency_ms": 100, "cost_usd": 0.1, "tokens_in": 4, "tokens_out": 6, "quality_score": 0.8},
        {"event": "request_failed", "error_type": "TimeoutError"},
    ]
    summary = summarize(records)
    assert summary["latency_ms"]["p95"] == 100.0
    assert summary["cost"]["total_usd"] == 0.1
    assert summary["errors"]["breakdown"] == {"TimeoutError": 1}
