from bs4 import BeautifulSoup
import os

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract product data from the HTML table, ignoring boilerplate.

def parse_html_catalog(file_path):
    # --- FILE READING (Handled for students) ---
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    # ------------------------------------------
    
    # Use BeautifulSoup to find the table with id 'main-catalog'
    table = soup.find('table', id='main-catalog')
    if not table:
        return []
        
    documents = []
    rows = table.find_all('tr')
    
    # Extract rows, handling 'N/A' or 'Liên hệ' in the price column.
    # Table columns: Mã SP | Tên sản phẩm | Danh mục | Giá niêm yết | Tồn kho | Đánh giá
    for i, row in enumerate(rows[1:]):  # Skip header
        cols = row.find_all(['td', 'th'])
        if len(cols) < 4:
            continue
        
        product_id   = cols[0].get_text(strip=True)   # e.g. SP-001
        product_name = cols[1].get_text(strip=True)   # e.g. VinAI Laptop Pro 14"
        category     = cols[2].get_text(strip=True)   # e.g. Laptop
        price_str    = cols[3].get_text(strip=True).lower()
        stock        = cols[4].get_text(strip=True) if len(cols) > 4 else "N/A"
        rating       = cols[5].get_text(strip=True) if len(cols) > 5 else "N/A"
        
        # Enrich content so it passes quality gate (>20 chars)
        content = f"[{product_id}] {product_name} - Danh mục: {category}"
        
        price = 0.0
        if price_str not in ['n/a', 'liên hệ', 'contact', '']:
            # Extract digits only (remove VND, commas, dots used as thousands sep)
            clean_str = ''.join(c for c in price_str if c.isdigit())
            try:
                price = float(clean_str) if clean_str else 0.0
            except ValueError:
                price = 0.0
                
        documents.append({
            "document_id": f"html_{product_id}",
            "content": content,
            "source_type": "HTML",
            "author": "Catalog System",
            "metadata": {
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "price": price,
                "original_price_str": cols[3].get_text(strip=True),
                "stock": stock,
                "rating": rating
            }
        })
        
    return documents

