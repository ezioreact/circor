import os
import json
from typing import List
from src.configuration.env_key import EnvironKey
from backend_logs import get_logger


logger = get_logger("default-summary-question")
config = EnvironKey.setting()
FILE_PATH = config['default_summary_question']['path_']


async def save_to_file(questions: List[str]) -> dict:
    try:
        os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
        data = {
            "questions": questions
        }

    except:
        data = {
            "questions": questions
        }

    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)


async def save_default_question(request_) -> dict:
    """
    request: request_ #Pydantic Body (should contain only questions)
    return : 200 response.
    """
    try:

        await save_to_file(request_.questions);logger.info("default Question Saved")
        return {
            'response': 'Questions Saved!',
            'status': '200',
            'questions': request_.questions
        }

    except Exception as E:
        logger.error(f"Error: {str(E)}")
        return {
            "response": f"Failed due to {str(E)}",
            "status": 500
        }


async def load_default_question():
    """
    request: None
    response: 
        {
        "questions": [
            "What is the scope of work, supply, and services?",
            "What are the technical requirements, design standards, and performance criteria?",
            "What are the quality, inspection, testing, and documentation requirements?",
            "What are the commercial terms, delivery conditions, and vendor qualifications?",
            "What are the installation, commissioning, and after-sales support requirements?"
        ]}
    """
    try:
        with open(FILE_PATH, "r") as f:
            data = json.load(f)
        logger.info("summary default question Loaded successfully.")
        return data
    except Exception as E:
        logger.info(f"summary default question Loading faild: {str(E)}")
        return {"respone":f"FILE_PATH Not Found!","Error":str(E),"status":500}