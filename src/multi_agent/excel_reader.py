import pandas as pd
from typing import List


async def read_excel_questions(file_path: str) -> List[str]:
    """
    Read only the Question column (Column B) from Excel
    """
    xls = pd.ExcelFile(file_path)
    if len(xls.sheet_names) > 1:
        sheet_index = 1  
    else:
        sheet_index = 0  

    df = pd.read_excel(file_path, sheet_name=sheet_index)
    questions = df.iloc[:, 1].dropna().tolist()    
    questions = [q.strip() for q in questions if isinstance(q, str) and q.strip()] 
    return questions