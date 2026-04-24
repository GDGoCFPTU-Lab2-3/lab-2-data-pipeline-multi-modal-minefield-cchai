from openai import OpenAI
import os
import json
import time
import re
import base64
import fitz  # PyMuPDF

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Use OpenAI GPT-4o to extract structured data from lecture_notes.pdf

def _pdf_to_base64_images(file_path: str, max_pages: int = 5) -> list[str]:
    """Convert PDF pages to base64-encoded PNG images using PyMuPDF."""
    images = []
    doc = fitz.open(file_path)
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        # Render page at 150 DPI (good balance between quality and token cost)
        mat = fitz.Matrix(150 / 72, 150 / 72)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        images.append(base64.standard_b64encode(img_bytes).decode("utf-8"))
    doc.close()
    return images

def extract_pdf_data(file_path):
    # --- FILE CHECK (Handled for students) ---
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None
    # ------------------------------------------

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY environment variable not set. Skipping PDF.")
        return None

    client = OpenAI(api_key=api_key)

    try:
        print(f"Converting PDF to images: {file_path}...")
        images_b64 = _pdf_to_base64_images(file_path, max_pages=5)
        
        if not images_b64:
            print("Error: Could not convert PDF to images.")
            return None

        print(f"Sending {len(images_b64)} page(s) to GPT-4o Vision...")

        # Build content: text prompt + all page images
        content = [
            {
                "type": "text",
                "text": (
                    "Analyze these PDF page images and extract the following information. "
                    "Return the result STRICTLY as a JSON object with no markdown formatting or extra text. "
                    "The JSON must have these exact keys:\n"
                    '- "title": (string) The title of the document\n'
                    '- "author": (string) The author of the document\n'
                    '- "summary": (string) A 3-sentence summary of the main topics\n'
                    '- "tables": (list of dicts) Any tabular data found, each dict has "headers" and "rows"'
                )
            }
        ]
        for img_b64 in images_b64:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_b64}",
                    "detail": "high"
                }
            })

        # SLA: Exponential backoff for rate limit errors
        max_retries = 3
        base_delay = 2
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": content}],
                    max_tokens=1500,
                    temperature=0
                )

                raw_text = response.choices[0].message.content
                # Strip markdown code fences if present
                raw_text = re.sub(r'^```json\s*', '', raw_text.strip())
                raw_text = re.sub(r'```$', '', raw_text.strip()).strip()

                data = json.loads(raw_text)

                return {
                    "document_id": f"pdf_{os.path.basename(file_path)}",
                    "content": data.get("summary", ""),
                    "source_type": "PDF",
                    "author": data.get("author", "Unknown"),
                    "metadata": {
                        "title": data.get("title", ""),
                        "tables": data.get("tables", [])
                    },
                    "source_metadata": {
                        "title": data.get("title", ""),
                    }
                }
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    print(f"Rate limited (429). Retrying in {base_delay}s...")
                    time.sleep(base_delay)
                    base_delay *= 2
                else:
                    print(f"OpenAI API Error: {e}")
                    break
    except Exception as e:
        print(f"Error processing PDF: {e}")

    return None

