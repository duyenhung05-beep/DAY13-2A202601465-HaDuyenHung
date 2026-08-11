# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: high_latency_p95
- Severity: warning
- SLI/SLO liên quan: latency_p95_ms, objective 3000 ms
- Điều kiện và thời gian duy trì: P95 > 3000 ms trong 5 phút.
- Ảnh hưởng tới người dùng: câu trả lời chậm, timeout có thể tăng.
- Ba bước kiểm tra đầu tiên: xem panel Latency; mở trace chậm nhất; truy log bằng correlation ID.
- Mitigation tạm thời: tắt incident/tool chậm hoặc chuyển sang prompt/local fallback; xác nhận P95 hồi phục.
- Owner: Hà Duyên Hùng

## Alert 2

- Tên: elevated_error_rate
- Severity: critical
- SLI/SLO liên quan: error_rate_pct, objective 2%
- Điều kiện và thời gian duy trì: request_failed/request_received > 2% trong 5 phút.
- Ảnh hưởng tới người dùng: request thất bại hoặc nhận HTTP 500.
- Ba bước kiểm tra đầu tiên: xem Error rate/breakdown; mở log request_failed; tìm trace và error_type tương ứng.
- Mitigation tạm thời: rollback prompt/feature thay đổi gần nhất và disable dependency lỗi; kiểm tra recovery.
- Owner: Hà Duyên Hùng

## Alert 3

- Tên: low_quality_proxy
- Severity: warning
- SLI/SLO liên quan: quality_score_avg, objective 0.75
- Điều kiện và thời gian duy trì: mean quality_score < 0.75 trong 10 phút.
- Ảnh hưởng tới người dùng: câu trả lời kém hữu ích hoặc thiếu ngữ cảnh.
- Ba bước kiểm tra đầu tiên: xem Quality; đối chiếu prompt version/label; kiểm tra docs và trace generation.
- Mitigation tạm thời: rollback production prompt về version đã biết tốt và giảm thay đổi đầu vào.
- Owner: Hà Duyên Hùng
