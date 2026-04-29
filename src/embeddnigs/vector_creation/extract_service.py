import pdfplumber
import json
import io
from langdetect import detect, LangDetectException
import re
import pandas as pd


class PDF_Proccessing:
    def __init__(self):
        pass
    
    @staticmethod
    def extract_excel_data(excel_file: str) -> dict:
        xls = pd.ExcelFile(excel_file)

        # Check if sheet-2 exists
        sheet_index = 1 if len(xls.sheet_names) > 1 else 0

        df = pd.read_excel(xls, sheet_name=sheet_index)

        documents = []
        metadatas = []
        ids = []

        for i, row in df.iterrows():
            text = f"""
            Topic: {row.get('topic', '')}
            Question: {row.get('questions', '')}
            Answer: {row.get('answer', '')}
            """

            documents.append(text)

            metadatas.append({
                "topic": row.get("topic"),
                "page": row.get("page_num")
            })

            ids.append(str(i))
        print("metadata: ",metadatas)
        return {
            'question_answer': documents,
            'metadata': metadatas,
            "ids": ids
        }

    # @staticmethod
    # def extract_excel_data(excel_file:str) -> dict: 
    #     df = pd.read_excel(excel_file)

    #     documents = []
    #     metadatas = []
    #     ids = []

    #     for i, row in df.iterrows():
    #         print("Row: ",row)
    #         text = f"""
    #         Topic: {row['topic']}
    #         Question: {row['questions']}
    #         Answer: {row['answer']}
    #         """

    #         documents.append(text)

    #         metadatas.append({
    #             "topic": row["topic"],
    #             "page": row["page_num"],
    #             "source": row["source_text"]
    #         })

    #         ids.append(str(i))

    #     return{'question_answer':documents,'metadata':metadatas,"ids":ids}


    @staticmethod
    def _clean_repeated_chars(text: str) -> str:
        """
        Removes character repetition artifacts from PDF extraction.
        Converts 'AAA' -> 'A', 'Reeeevvvv' -> 'Rev', etc.
        """
        if not text:
            return ""
        
        # Pattern: same char repeated 2+ times (case-insensitive for vowels)
        # Keep max 2 repetitions to preserve legitimate words like "book", "feel"
        cleaned = re.sub(r'(.)\1{2,}', r'\1\1', text)  # 3+ repeats -> 2
        cleaned = re.sub(r'([A-Za-z])\1{1,}', r'\1', cleaned)  # 2+ of same letter -> 1
        return cleaned

    @staticmethod
    def _is_english_text(text: str) -> bool:
        """
        Detects if the given text is in English.
        Returns True if English, False otherwise.
        """
        if not text or not text.strip():
            return False
        
        # First clean repeated characters
        cleaned =  PDF_Proccessing._clean_repeated_chars(text)
        
        # Remove numbers, special chars for detection
        cleaned = re.sub(r'[^\w\s]', '', cleaned).strip()
        
        if len(cleaned) < 3:
            return True  # Assume English for very short text
        
        try:
            lang = detect(cleaned)
            return lang == 'en'
        except LangDetectException:
            return False

    @staticmethod
    def _filter_english_only(text: str) -> str:
        """
        Filters out non-English sentences from text.
        Returns only English portions.
        """
        if not text:
            return ""
        
        # First clean the entire text of repetition artifacts
        text =  PDF_Proccessing._clean_repeated_chars(text)
        
        # Split into lines/paragraphs instead of sentences for technical docs
        lines = text.split('\n')
        english_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line is English
            if  PDF_Proccessing._is_english_text(line):
                english_lines.append(line)
        
        return " ".join(english_lines)

    @staticmethod
    async def _raw_pdf_(pdf_path):
        """
        Extracts text and tables from a PDF page by page.
        Returns a clean JSON-structured list with ONLY English content.
        """
        results = []

        if hasattr(pdf_path, 'read'):
            file_bytes = await pdf_path.read()
            pdf_file = io.BytesIO(file_bytes)
        else:
            pdf_file = pdf_path

        with pdfplumber.open(pdf_file) as pdf:
            for i, page in enumerate(pdf.pages):
                raw_text = page.extract_text() or ""
                
                # Filter to English only (includes cleaning of repeated chars)
                english_text = PDF_Proccessing._filter_english_only(raw_text)
                clean_text = " ".join(english_text.split()) if english_text else ""
                
                # Process tables
                tables_data = []
                tables = page.extract_tables()

                for table in tables:
                    if table and len(table) > 0:
                        header = []
                        for cell in table[0]:
                            if cell:        
                                cell_text = str(cell).strip()
                                # Clean repeated chars from table cells too
                                cell_text =  PDF_Proccessing._clean_repeated_chars(cell_text)
                                english_cell =  PDF_Proccessing._filter_english_only(cell_text)
                                header.append(english_cell if english_cell else "")
                            else:
                                header.append("")

                        rows = []
                        for row in table[1:]:
                            row_data = []
                            for cell in row:
                                if cell:
                                    cell_text = str(cell).strip()
                                    cell_text =  PDF_Proccessing._clean_repeated_chars(cell_text)
                                    english_cell =  PDF_Proccessing._filter_english_only(cell_text)
                                    row_data.append(english_cell if english_cell else "")
                                else:
                                    row_data.append("")
                            
                            if any(cell.strip() for cell in row_data):
                                rows.append(row_data)
                        
                        if any(h.strip() for h in header) or rows:
                            tables_data.append({
                                "header": header,
                                "rows": rows
                            })

                if clean_text or tables_data:
                    results.append({
                        "page": i + 1,
                        "page_content": clean_text,
                        "Table_content": tables_data
                    })

        return results

