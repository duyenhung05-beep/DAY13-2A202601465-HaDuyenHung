# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Cá nhân — Hà Duyên Hùng
- Repository URL: https://github.com/duyenhung05-beep/DAY13-2A202601465-HaDuyenHung
- Commit SHA cuối: `9c67f0c053eda37a152df12e11709b31fe70d118` (implementation/evidence checkpoint)
- Thành viên và vai trò: Hà Duyên Hùng — MSSV 2A202601465 — phụ trách toàn bộ bài Day 13: logging, PII, tracing, prompt versioning, metrics, dashboard, SLO, alert, incident investigation, report và submission.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100; 54 records, 29 correlation IDs, 0 PII leak.
- Tổng số traces: Langfuse disabled vì `.env` không có credentials; không tạo trace giả. Xem [langfuse_status.txt](evidence/langfuse_status.txt).
- Số PII leak còn lại: 0 theo validator và runtime log scan.
- Link/đường dẫn dashboard: endpoint runtime [GET /dashboard](http://127.0.0.1:8000/dashboard), source `data/logs.jsonl`; HTML evidence tại [dashboard_runtime.html](evidence/dashboard_runtime.html).

## 3. Logging và tracing

- Evidence correlation ID: [correlation_id_evidence.json](evidence/correlation_id_evidence.json). Ví dụ runtime `req-026d37ba` xuất hiện nhất quán ở request/response; response có `x-request-id` và `x-response-time-ms`.
- Evidence PII redaction: [pii_redaction_evidence.json](evidence/pii_redaction_evidence.json) và [final_validate_logs.txt](evidence/final_validate_logs.txt). Scrubber đệ quy xử lý dict/list trước JSON sink; email, phone, card và CCCD được thay bằng marker.
- Evidence trace waterfall: Không khả dụng vì Langfuse credentials chưa được cấu hình; [langfuse_status.txt](evidence/langfuse_status.txt) ghi rõ trạng thái này. Local runtime vẫn có request/response log và metrics thật.
- Giải thích một span đáng chú ý: Không có span managed để báo cáo. Luồng local đã xác minh là request → middleware tạo correlation ID → agent retrieve/generate → `response_sent`; practice/challenge cho thấy thời gian retrieve tăng khi `rag_slow` bật.

## 4. Prompt versioning

- Prompt name: `day13-chat` (local contract giữ `Feature={{feature}}`, `Docs={{docs}}`, `Question={{message}}`).
- Version/label baseline: Chưa thực hiện managed prompt vì Langfuse disabled.
- Version/label candidate: Chưa thực hiện managed prompt vì Langfuse disabled.
- Trace ID của mỗi version: Không có; không bịa trace ID.
- Bằng chứng đổi label hoặc rollback: Không khả dụng trong môi trường không có Langfuse credentials; xem [langfuse_status.txt](evidence/langfuse_status.txt). Manual evidence còn thiếu: tạo v1 `baseline`/`production`, v2 `candidate`, switch production sang v2 rồi rollback về v1 trên Langfuse UI/API.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ: 6/6 panel; xem [final_validate_dashboard.txt](evidence/final_validate_dashboard.txt).
- Evidence dashboard: [dashboard_runtime.html](evidence/dashboard_runtime.html) và [runtime_smoke_metrics_dashboard.txt](evidence/runtime_smoke_metrics_dashboard.txt). Runtime đọc JSONL, có 6 panel Latency/Traffic/Errors/Cost/Tokens/Quality, time range 60 phút, refresh 30 giây, unit và threshold từ contract.
- SLO đã chọn và lý do: P95 latency ≤ 3000 ms, error rate ≤ 2%, daily cost ≤ 2.5 USD, quality mean ≥ 0.75 theo `config/slo.yaml`; đây là các ngưỡng tương ứng trực tiếp với dashboard và bảo vệ trải nghiệm, độ tin cậy, chi phí và chất lượng.
- Alert rules và runbook: `config/alert_rules.yaml` có high latency, elevated errors và low quality; runbook actionable tại [docs/alerts.md](../docs/alerts.md), gồm panel/query, trace, correlation ID, mitigation, recovery và prevention.

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`; affected feature `refund`; official workflow dùng nguyên `config/challenge.json`.
- Triệu chứng từ metrics: 5 official responses có latency 2650–2651 ms, P95 2651 ms, vượt threshold 2000 ms; [challenge_metrics.json](evidence/challenge_metrics.json). Baseline practice P95 150 ms; khi `rag_slow` bật P95 2650.05 ms, xem [practice_baseline_metrics.json](evidence/practice_baseline_metrics.json) và [practice_incident_metrics.json](evidence/practice_incident_metrics.json).
- Trace ID liên quan: Không khả dụng vì Langfuse disabled; không bịa ID.
- Log line/correlation ID liên quan: `req-189903de` cho `k3-challenge-s02` có `request_received` và `response_sent` với latency 2650 ms; các ID khác gồm `req-af912947`, `req-11a269e5`, `req-ed6eba27`, `req-026d37ba`; xem [challenge_logs.txt](evidence/challenge_logs.txt).
- Root cause: official incident `rag_slow` được enable thật (`incident_enabled`, correlation `req-146ede18`); runtime `app.mock_rag.retrieve` sleep 2.5 giây trước generation, nên response latency tăng từ khoảng 150 ms lên khoảng 2650 ms. Đây là kết luận nối metrics → log/correlation ID → runtime behavior, không phải trace giả.
- Fix action: disable `rag_slow` bằng official control endpoint; recovery smoke sau đó trả `rag_slow: false` và `/chat` trả 200 với latency khoảng 150 ms, không xóa incident logs.
- Preventive measure: alert P95 > 3000 ms trong 5 phút; dashboard theo dõi P95/P99; runbook yêu cầu mở trace (khi Langfuse có), truy correlation ID/log và kiểm tra dependency RAG timeout/budget trước khi rollback hoặc disable feature.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Hà Duyên Hùng — 2A202601465 | Toàn bộ implementation và investigation: structured logging, correlation ID, PII redaction, metrics, tracing adapter, prompt contract, dashboard, SLO/alerts, practice và official challenge | `275eb4e`, `ac87729`, `9c67f0c` trên `main` | Structured logging cần scrub trước JSON sink; correlation ID nối request với log; percentile cần tính từ runtime data; Langfuse trace cần metadata và prompt version/label/rollback thật; dashboard phải đọc JSONL; SLO/alert phải gắn symptom; incident workflow là Metrics → Traces → Logs → root cause. |
