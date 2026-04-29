import re
from typing import List, Dict
from src.configuration.env_key import EnvironKey
from backend_logs import get_logger

config_data = EnvironKey.setting()
logger = get_logger()


def table_to_text(table: Dict) -> str:
    """
    Convert table dictionary to formatted text string.
    """
    if not table or not table.get("header"):
        return ""
    
    header = table.get("header", [])
    rows = table.get("rows", [])
    
    lines = []
    
    header_str = " | ".join(str(cell) for cell in header if cell)
    if header_str.strip():
        lines.append(f"TABLE HEADER: {header_str}")
        lines.append("-" * len(header_str))
    
    for row in rows:
        row_str = " | ".join(str(cell) for cell in row if cell)
        if row_str.strip():
            lines.append(row_str)
    
    return "\n".join(lines)


def detect_content_type(text: str) -> str:
    """
    Detect content type for proper rendering in UI.
    """
    text_stripped = text.strip()
    
    # Check for table content
    if "TABLE HEADER:" in text_stripped:
        return "Table"
    
    # Check for list items
    if re.match(r'^[\s]*[-•●■□▪▫]\s', text_stripped) or re.match(r'^[\s]*\d+[\.\)]\s', text_stripped):
        return "ListItem"
    
    # Title: short, often all caps or title case
    if len(text_stripped) < 100 and (text_stripped.isupper() or text_stripped.istitle()):
        return "Title"
    
    # Narrative text: longer with sentences
    if len(text_stripped) > 100 and '.' in text_stripped:
        return "NarrativeText"
    
    return "Text"


def chunk_by_tokens(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Simple token-aware chunking (1 token ≈ 4 chars).
    Tries to break at sentence boundaries.
    """
    chunk_size_chars = chunk_size * 4
    overlap_chars = overlap * 4
    
    if len(text) <= chunk_size_chars:
        return [text]
    
    chunks = []
    cursor = 0
    
    while cursor < len(text):
        end = min(cursor + chunk_size_chars, len(text))
        
        if end < len(text):
            search_start = max(cursor + chunk_size_chars // 2, end - 100)
            search_text = text[search_start:end + 100]
            
            sentence_end = -1
            for match in re.finditer(r'[.!?]\s+', search_text[:end - search_start]):
                sentence_end = match.end() + search_start
            
            if sentence_end > cursor + chunk_size_chars // 2:
                end = min(sentence_end, len(text))
        
        chunk_text = text[cursor:end].strip()
        if chunk_text:
            chunks.append(chunk_text)
        
        cursor = end - overlap_chars if end < len(text) else end
    
    return chunks


async def chunk_pages(pages: List[Dict], chunk_size: int = None,
                     overlap: int = None) -> List[Dict]:
    """
    Chunk pages with exact page tracking.
    
    INPUT FORMAT:
    [
        {
            "page": 1,
            "page_content": "text content...",
            "Table_content": [{"header": [...], "rows": [...]}]
        }
    ]
    
    Returns:
        List of chunk dicts with exact page number for PDF preview
    """
    if chunk_size is None:
        chunk_size = config_data['chunking']['chunk_size']
    if overlap is None:
        overlap = config_data['chunking']['chunk_overlap']
    
    all_chunks = []
    chunk_counter = 0
    
    for page_data in pages:
        page_num = page_data["page"]
        page_text = page_data.get("page_content", "")
        
        # Convert tables to text
        tables = page_data.get("Table_content", [])
        table_texts = []
        for table in tables:
            table_str = table_to_text(table)
            if table_str:
                table_texts.append(table_str)
        
        # Combine page content and tables
        full_text = page_text
        if table_texts:
            full_text += "\n\n" + "\n\n".join(table_texts)
        
        if not full_text.strip():
            continue
        
        # Chunk the combined text
        sub_chunks = chunk_by_tokens(full_text, chunk_size, overlap)
        
        for i, sub_text in enumerate(sub_chunks):
            chunk_id = f"p{page_num:04d}_c{i:03d}"
            
            all_chunks.append({
                "chunk_id": chunk_id,
                "text": sub_text,
                "page": page_num,
                "pages": [page_num],
                "content_type": detect_content_type(sub_text),
                "char_count": len(sub_text)
            })
            chunk_counter += 1
    
    logger.info(f"Created {chunk_counter} chunks from {len(pages)} pages")
    return all_chunks