from src.ai_chatbot.chat_ai_model import chat_model
from src.multi_agent.embeddings import TenderRAG
from src.rounting_pipeline.rag_llm_connector import sanitize_collection_name
from pathlib import Path

chat_model_obj = chat_model()


async def wrong_answer_correction(api_request_body):
    #sanirize collection name from s3 url
    collecion_ = await sanitize_collection_name(name=Path(api_request_body.document_url).name)

    print(f"[+]Collection name [{collecion_}] for Wrong answer correction funtion!")

    obj_ = TenderRAG(collection_name=collecion_)

    response = await obj_.chat_query(question=api_request_body.query,correction=True)
    # rag_object, collections_name = await chat_model_obj.get_rag_engine(s3_link=api_request_body.document_url)
    print("[+]wrong answer collection: ",collecion_)
    
    return response