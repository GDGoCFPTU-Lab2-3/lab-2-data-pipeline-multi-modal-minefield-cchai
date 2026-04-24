[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23706931&assignment_repo_type=AssignmentRepo)

# 🏗️ Codelab 03: The Multi-Modal Minefield — Data Pipeline Lab

## 👤 Thông tin Sinh viên

| Thông tin | Chi tiết |
|---|---|
| **Họ và tên** | Cao Chí Hải |
| **Mã học viên** | 2A202600011 |
| **Email** | [caochihai1710@gmail.com](mailto:caochihai1710@gmail.com) |
| **GitHub Username** | [caochihai](https://github.com/caochihai) |
| **GitHub Repository** | [lab-2-data-pipeline-multi-modal-minefield-cchai](https://github.com/GDGoCFPTU-Lab2-3/lab-2-data-pipeline-multi-modal-minefield-cchai) |
| **Lab** | Codelab 03 v1 — Multi-Modal Minefield (Advanced Edition) |

---

## 🎯 Mô tả bài Lab

Xây dựng một **Data Pipeline** thực tế để thu nạp dữ liệu đa nguồn (Multi-Modal) vào một Knowledge Base thống nhất. Pipeline xử lý 5 loại nguồn dữ liệu khác nhau: PDF, CSV, HTML, Transcript (Video), và Legacy Python Code.

---

## 🏗️ Kiến trúc Pipeline

```
raw_data/
  ├── lecture_notes.pdf        → GPT-4o Vision (OCR + Structured Extraction)
  ├── demo_transcript.txt      → Regex (Noise/Timestamp Removal)
  ├── product_catalog.html     → BeautifulSoup (Table Scraping)
  ├── sales_records.csv        → Pandas (Dedup + Type Cleaning)
  └── legacy_pipeline.py       → AST (Docstring + Business Rule Extraction)
         ↓
starter_code/orchestrator.py   (DAG Orchestrator)
         ↓
quality_check.py               (3 Semantic Quality Gates)
         ↓
processed_knowledge_base.json  (Final Output)
```

---

## ⚙️ Cài đặt & Chạy

### 1. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 2. Cấu hình API Key
Tạo file `.env` ở thư mục gốc:
```
OPENAI_API_KEY=sk-proj-your_key_here
```

### 3. Chạy Pipeline
```bash
python starter_code/orchestrator.py
```

### 4. Kiểm tra kết quả
```bash
python forensic_agent/agent_forensic.py
```

---

## 📋 Các bước thực hiện

### Role 1 — Lead Data Architect (`schema.py`)
- Định nghĩa `UnifiedDocument` bằng Pydantic với đầy đủ các trường.
- Dùng `Literal` để validate chặt `source_type`.
- Thêm `schema_version = "v1"` để chuẩn bị cho Breaking Change.
- Thêm `@field_validator` tự động strip whitespace.

### Role 2 — ETL/ELT Builder (`process_*.py`)
- **PDF**: Dùng **OpenAI GPT-4o Vision** (PyMuPDF chuyển PDF → ảnh → base64 → GPT-4o).
- **CSV**: Pandas — xóa trùng theo `id`, chuẩn hóa giá (xử lý `$`, text số), chuẩn hóa ngày `YYYY-MM-DD`.
- **HTML**: BeautifulSoup — quét đúng `table#main-catalog`, xử lý giá trị rỗng "N/A" / "Liên hệ".
- **Transcript**: Regex `\[.*?\]` loại bỏ timestamp + noise, phát hiện giá tiền tiếng Việt "năm trăm nghìn" → 500000.
- **Legacy Code**: `ast.parse()` trích xuất docstring an toàn, Regex tìm `# Business Logic Rule`.

### Role 3 — QA Engineer (`quality_check.py`)
3 cổng kiểm soát chất lượng:
1. **Gate 1**: Từ chối content < 20 ký tự.
2. **Gate 2**: Từ chối chuỗi độc hại (`null pointer exception`, `traceback`, ...).
3. **Gate 3**: Phát hiện sai lệch logic (comment nói 8% nhưng code dùng 10%).

### Role 4 — DevOps Specialist (`orchestrator.py`)
- Auto-load `.env` qua `python-dotenv`.
- Gọi tuần tự 5 extractor theo DAG.
- Validate từng document qua Pydantic + Quality Gate.
- Lưu kết quả ra `processed_knowledge_base.json`.
- Theo dõi SLA: cảnh báo nếu pipeline chạy quá 60 giây.

---

## ✅ Kết quả Kiểm thử

### Chạy Pipeline
```
==================================================
  STARTING DATA PIPELINE
==================================================

[1/5] Processing PDF (GPT-4o Vision)...   → OK: 1/1
[2/5] Processing Transcript (Regex)...   → OK: 1/1
[3/5] Processing HTML Catalog...          → OK: 5/5
[4/5] Processing Sales CSV...             → OK: 20/20
[5/5] Processing Legacy Code...           → OK: 1/1

Total valid documents stored: 28
Pipeline finished in 7.12 seconds.
==================================================
```

### Forensic Agent Score
```
=== STARTING FORENSIC DEBRIEF ===
[PASS] No duplicate IDs in CSV processing.
[PASS] Correct price extracted from Vietnamese audio transcript.
[PASS] Quality gate successfully rejected corrupt content.

Final Forensic Score: 3/3 ✅
```

---

## 📦 Công nghệ sử dụng

| Thư viện | Mục đích |
|---|---|
| `pydantic` | Data schema validation |
| `openai` | GPT-4o Vision — PDF extraction |
| `pymupdf` | PDF → Image conversion |
| `pandas` | CSV processing |
| `beautifulsoup4` | HTML parsing |
| `python-dotenv` | Environment variable management |
| `ast` (built-in) | Safe Python code analysis |
| `re` (built-in) | Regex text cleaning |
