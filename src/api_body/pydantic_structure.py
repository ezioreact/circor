from pydantic import BaseModel, Field, HttpUrl
from bson import ObjectId
from typing import List, Optional, Dict, Any


class ObjectIdStr(str):
    """Custom type for MongoDB ObjectId"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

class LanguageConversion(BaseModel):
    source: str
    target: str

class Summary(BaseModel):
    version: int = 0
    status: str = "Original"

class bom_correction_request(BaseModel):
    id:str
    query:str
    wrong_answer:str
    document_url: str

# Data model for updates
class ConfigUpdate(BaseModel):
    base_url: Optional[str] = None
    port: Optional[int] = None

class BOMRequest(BaseModel):
    id:str
    projectId: str
    name: str
    description: str
    department: str
    documentType: str = "BOM"
    languageConversion: LanguageConversion
    tags: List[str] = []
    status: str = "In Progress"
    inputDocument: HttpUrl = Field(..., examples=["https://boomai-bucket.s3.ap-south-1.amazonaws.com/1774258127481-SOR- BMW-K34&K35 2.pdf"])
    outputDocument: HttpUrl = Field(..., examples=["https://boomai-bucket.s3.ap-south-1.amazonaws.com/1774266546936-bmw-test.xlsx"])
    summary: Summary = Field(default_factory=Summary)

class BOMResponse(BOMRequest):
    aiBomResponse: Optional[str] = None


class VectorRetrievalRequest(BaseModel):
    query_schema: List[str]
    collection_name: str
    doc_id: Optional[str] = None

class ChunkItem(BaseModel):
    text: str
    page: int
    content_type: str
    distance: float
    doc_id: str


class test_llm_request(BaseModel):
    key:str
    chunk_: dict

class chat_ai_Request(BaseModel):
    id: str
    query: str
    document: HttpUrl = Field(..., examples=["https://boomai-bucket.s3.ap-south-1.amazonaws.com/1774258127481-SOR- BMW-K34&K35 2.pdf"])
    doc_type: str =Field(..., examples=["xlsx | pdf"])
    filter: Optional[str] = Field(default=None, examples=[None])

class ExtrcationResult(BaseModel):
    question: str
    answer: str
    page: str
    status: str
    source : str


class bom_correction_response(BaseModel):
    page: str
    content: str
    score: str
    type: str

class chat_ai_Response(BaseModel):
    id: str
    ai_response: List[ExtrcationResult]
    

class summary_request(BaseModel):
    id:str
    query:str
    modify_ai:bool = Field(..., examples=[True, False])
    input_document:str = Field(..., examples=['https://boomai-bucket.s3.ap-south-1.amazonaws.com/1774258127481-SOR- BMW-K34&K35 2.pdf'])
    summary_length:str = Field(..., examples=["400"])


class summary_response(BaseModel):
    id:str
    query:str
    ai_response:str
    s3_url:str
    
class question_request(BaseModel):
    questions: List[str]

