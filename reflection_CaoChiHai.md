# Báo cáo cá nhân — Cao Chí Hải (2A202600011)

**Họ và tên:** Cao Chí Hải  
**Vai trò:** Full-stack Data Pipeline Engineer (Phụ trách tất cả các Role 1, 2, 3, 4)  
**Dự án:** Multi-Modal Minefield Data Pipeline

---

## 1. Phụ trách

Tôi đã tự mình triển khai toàn bộ vòng đời của Data Pipeline trong bài Lab này, bao gồm:
- **Role 1 (Architect):** Thiết kế `schema.py` với Pydantic để chuẩn hóa dữ liệu đa nguồn.
- **Role 2 (ETL Builder):** Triển khai 5 extractor cho PDF, CSV, HTML, Transcript và Legacy Code. Đặc biệt là giải quyết vấn đề Rate Limit của Gemini bằng cách chuyển đổi sang GPT-4o Vision.
- **Role 3 (QA Engineer):** Xây dựng `quality_check.py` với các bộ lọc ngữ nghĩa (Semantic Gates).
- **Role 4 (DevOps):** Điều phối toàn bộ luồng công việc (Orchestration) và đảm bảo tính Idempotency của Pipeline.

---

## 2. Quyết định kỹ thuật

- **Sử dụng GPT-4o cho PDF:** Khi Gemini API bị lỗi 429 (Resource Exhausted), tôi đã chủ động thay đổi giải pháp kỹ thuật sang OpenAI GPT-4o Vision. Tôi đã dùng thư viện `PyMuPDF` để render PDF thành ảnh, giúp model hiểu được cấu trúc bảng biểu phức tạp trong `lecture_notes.pdf` mà không cần OCR thủ công.
- **Stale Data & Policy Detection:** Tôi đã triển khai thêm logic trong Quality Gate để tự động phát hiện và loại bỏ các dữ liệu "lỗi thời" (Stale Data). Ví dụ: Hệ thống sẽ tự động reject các văn bản chứa chính sách hoàn tiền cũ (14 ngày) vì chính sách hiện hành là 7 ngày. Điều này giúp ngăn chặn hiện tượng "mô hình trả lời sai do dữ liệu cũ" (Hallucination from stale data).
- **Halt vs Warn:** Đối với các sai lệch logic như thuế suất (8% vs 10%), tôi thiết lập cơ chế **Halt** (ngừng xử lý bản ghi đó) để đảm bảo dữ liệu trong Knowledge Base luôn đạt độ tin cậy cao nhất.

---

## 3. Sự cố / Thử thách & Giải pháp

- **Lỗi trích xuất HTML:** Ban đầu dữ liệu bị loại bỏ vì content quá ngắn (<20 ký tự). Giải pháp là làm giàu dữ liệu bằng cách kết hợp `product_id`, `product_name` và `category` vào content thay vì chỉ lấy tên sản phẩm.
- **Dữ liệu CSV hỗn loạn:** Giải quyết vấn đề ID trùng lặp bằng cách sử dụng `drop_duplicates` trong Pandas và xử lý tiền tệ đa dạng ($ vs VND) bằng Regex thông minh.
- **Tính ổn định (SLA):** Tối ưu hóa pipeline để hoàn thành trong vòng dưới 10 giây (thực tế đạt 7.12 giây), đáp ứng yêu cầu SLA < 60 giây của hệ thống.

---

## 4. Kết quả (Before/After)

- **Trước khi xử lý:** Dữ liệu PDF bị bỏ qua do lỗi API, HTML bị lọc mất, CSV chứa nhiều rác và ID ảo. Điểm Forensic chỉ đạt ~1/3.
- **Sau khi xử lý:** 
    - Toàn bộ 28 bản ghi (bao gồm cả PDF) được trích xuất thành công.
    - Điểm Forensic Agent đạt **3/3 ✅**.
    - Vượt qua các câu hỏi chấm điểm về nội dung (Refund policy, SLA, HR Policy).

---

## 5. Tự đánh giá & Cải tiến

Tôi đã hoàn thành 100% khối lượng công việc của cả 4 vai trò. 
**Cải tiến đề xuất:** Triển khai thêm bước **Vector Pruning**. Khi chính sách thay đổi (ví dụ: Refund policy từ 14 ngày về 7 ngày), hệ thống cần tự động so sánh batch mới với batch cũ để xóa bỏ các bản ghi đã hết hạn (stale records) trong cơ sở dữ liệu vector, tránh hiện tượng mô hình AI trả về thông tin cũ đã bị thay thế.
