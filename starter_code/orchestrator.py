import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file (e.g., GEMINI_API_KEY)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Robust path handling
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "raw_data")

# Import role-specific modules
from schema import UnifiedDocument
from process_pdf import extract_pdf_data
from process_transcript import clean_transcript
from process_html import parse_html_catalog
from process_csv import process_sales_csv
from process_legacy_code import extract_logic_from_code
from quality_check import run_quality_gate

# ==========================================
# ROLE 4: DEVOPS & INTEGRATION SPECIALIST
# ==========================================
# Task: Orchestrate the ingestion pipeline and handle errors/SLA.

def _add_to_kb(final_kb: list, raw_doc, source_label: str):
    """Helper: Validate a doc (or list of docs) through quality gate and append to KB."""
    if raw_doc is None:
        print(f"  [SKIP] {source_label}: extractor returned None.")
        return

    # Some extractors return a list (CSV, HTML), others return a single dict
    docs = raw_doc if isinstance(raw_doc, list) else [raw_doc]
    
    accepted = 0
    for doc_dict in docs:
        if not doc_dict:
            continue
        try:
            # Validate against the Pydantic schema first
            validated = UnifiedDocument(**doc_dict)
            # Then run semantic quality gate
            if run_quality_gate(doc_dict):
                # Serialize to dict using pydantic (handles datetime -> string)
                final_kb.append(validated.model_dump(mode='json'))
                accepted += 1
        except Exception as e:
            doc_id = doc_dict.get("document_id", "unknown")
            print(f"  [ERROR] {source_label} doc_id='{doc_id}': {e}")
            
    print(f"  [OK] {source_label}: {accepted}/{len(docs)} document(s) passed quality gate.")

def main():
    start_time = time.time()
    final_kb = []
    
    # --- FILE PATH SETUP ---
    pdf_path   = os.path.join(RAW_DATA_DIR, "lecture_notes.pdf")
    trans_path = os.path.join(RAW_DATA_DIR, "demo_transcript.txt")
    html_path  = os.path.join(RAW_DATA_DIR, "product_catalog.html")
    csv_path   = os.path.join(RAW_DATA_DIR, "sales_records.csv")
    code_path  = os.path.join(RAW_DATA_DIR, "legacy_pipeline.py")
    output_path = os.path.join(os.path.dirname(SCRIPT_DIR), "processed_knowledge_base.json")
    # ----------------------

    print("=" * 50)
    print("  STARTING DATA PIPELINE")
    print(f"  RAW_DATA_DIR: {RAW_DATA_DIR}")
    print("=" * 50)

    # --- DAG: Execute each extractor node ---
    print("\n[1/5] Processing PDF (Gemini API)...")
    _add_to_kb(final_kb, extract_pdf_data(pdf_path), "PDF")

    print("\n[2/5] Processing Transcript (Regex)...")
    _add_to_kb(final_kb, clean_transcript(trans_path), "Transcript")

    print("\n[3/5] Processing HTML Catalog (BeautifulSoup)...")
    _add_to_kb(final_kb, parse_html_catalog(html_path), "HTML")

    print("\n[4/5] Processing Sales CSV (Pandas)...")
    _add_to_kb(final_kb, process_sales_csv(csv_path), "CSV")

    print("\n[5/5] Processing Legacy Code (AST)...")
    _add_to_kb(final_kb, extract_logic_from_code(code_path), "Code")

    # --- Save final Knowledge Base to JSON ---
    print(f"\n[OUTPUT] Saving {len(final_kb)} documents to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_kb, f, ensure_ascii=False, indent=2)

    end_time = time.time()
    elapsed = end_time - start_time
    print("\n" + "=" * 50)
    print(f"  Pipeline finished in {elapsed:.2f} seconds.")
    print(f"  Total valid documents stored: {len(final_kb)}")
    # SLA warning
    if elapsed > 60:
        print(f"  [WARNING] SLA breached: pipeline took {elapsed:.2f}s (limit: 60s)")
    print("=" * 50)


if __name__ == "__main__":
    main()
