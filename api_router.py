import os
import json
from pathlib import Path
from live_logs import tail_log_file
from fastapi.responses import JSONResponse, StreamingResponse
from src.api_body.pydantic_structure import BOMRequest,BOMResponse,test_llm_request
from src.multi_agent.bom_correction_agent import wrong_answer_correction
from src.api_body.pydantic_structure import bom_correction_request
from src.embeddnigs.vector_reterival.reterival import vector_retrieval_function
from src.embeddnigs.vector_creation.create_vector import create_vector_embedding
from src.api_body.pydantic_structure import VectorRetrievalRequest, chat_ai_Request,chat_ai_Response, ExtrcationResult, bom_correction_response
from src.api_body.pydantic_structure import summary_request, summary_response
from src.api_body.pydantic_structure import question_request
from src.rounting_pipeline.rag_llm_connector import start_proccess
from src.ai_bom.llm import large_languge_model_infer
from fastapi import APIRouter,BackgroundTasks, UploadFile
from backend_logs import get_logger
from src.ai_chatbot.chat_ai_model import chat_model
from src.ai_summarizer.summmary_agent import summary_routing_agent
from default_question import save_default_question, load_default_question
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from src.api_body.pydantic_structure import ConfigUpdate

app = FastAPI()
CONFIG_PATH = r"src\configuration\model_config.yaml"


production_api = APIRouter()
developer_api = APIRouter()
chatbot_ai = chat_model()
logs_api = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
logger = get_logger("api_router.py")


######## Production API interface.
@production_api.post("/prod/bom_generation")
async def bom_generation_api(user_request: BOMRequest, backgroun_task: BackgroundTasks):
    """
    Working Flow:
        intitall
    """
    result = await start_proccess(api_request_body=user_request)
    response_data = {
        **user_request.model_dump(),
        "status": "success" if result['status_code'] == 200 else "failed",
        "aiBomResponse": result["uploaded_to_s3"]
    }
    
    logger.info(f"/bom_generation api completed | status = {result['status_code']} | api response = success")
    return JSONResponse(
        status_code=int(result['status_code']),
        content=json.loads(BOMResponse(**response_data).model_dump_json())
    )

@production_api.post("/prod/bom_correction")
async def bom_correction_api(correction_request:bom_correction_request):
    response = await wrong_answer_correction(correction_request)

    print("Bom correction response: ",json.dumps(response,indent=4))
    return [bom_correction_response(page=items.get("page",""),
                                    content=items.get("content",""),
                                    score=items.get("score",""),
                                    type=items.get("type","")
                                    )for items in response]

# @production_api.post("/prod/chatbot" , response_model=chat_ai_Response)
# async def Chatbot_api(user_chat_request:chat_ai_Request):
#     chatai_response_ = await chatbot_ai.llm_chat_engine(S3buckt_link=str(user_chat_request.document),
#                                                        user_chat_query=str(user_chat_request.query),
#                                                        document_type=user_chat_request.doc_type)
    
#     print("Chat ai response: ",json.dumps(chatai_response_,indent=4))

#     return chat_ai_Response(id=user_chat_request.id,
#                                          ai_response=[str(a["answer"]) for a in chatai_response_["assistant"]],
#                                          page=[str(p['page']) for p in chatai_response_["assistant"]])

@production_api.post("/prod/chatbot" , response_model=chat_ai_Response)
async def Chatbot_api(user_chat_request:chat_ai_Request):
    chatai_response_ = await chatbot_ai.llm_chat_engine(S3buckt_link=str(user_chat_request.document),
                                                       user_chat_query=str(user_chat_request.query),
                                                       document_type=user_chat_request.doc_type,
                                                       where=user_chat_request.filter
                                                       )
    
    print("Chat ai response: ",json.dumps(chatai_response_,indent=4))
    result = [
        ExtrcationResult(
            question=item.get("question",""),
            answer=item.get("answer",""),
            page=str(item.get("page","")),
            status=item.get("status", "unknown"),
            source=item.get("source","no s3 link available")
        )for item in chatai_response_["assistant"]
    ]
    return chat_ai_Response(id=user_chat_request.id,
                            ai_response=result,
                            filter="none"
                            )


@production_api.post("/prod/summary")
async def summary_api(request_body_:summary_request):
    return await summary_routing_agent(request_body=request_body_)


@production_api.post("/prod/default_summary_query")
async def custom_summary_query(user_req_qus:question_request):
    return await save_default_question(request_=user_req_qus)


@production_api.get("/prod/default_summary_query")
async def check_custom_summary_qurry():
    return await load_default_question()



# 1. GET API: Retrieve entire configuration
@production_api.get("/get-config")
async def get_config():
    if not os.path.exists(CONFIG_PATH):
        raise HTTPException(status_code=404, detail="Config file not found")
    
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    return config

# 2. POST API: Update URL and/or Deployment Port
@production_api.post("/update-settings")
async def update_settings(payload: ConfigUpdate):
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)

        # Update base_url if provided
        if payload.base_url:
            if 'local_model_base_url' not in config:
                config['local_model_base_url'] = {}
            config['local_model_base_url']['base_url'] = payload.base_url

        # Update deployment port if provided
        if payload.port:
            if 'deployment' not in config:
                config['deployment'] = {}
            config['deployment']['port'] = payload.port

        # Write back to file
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        return {"status": "success", "updated_values": payload.dict(exclude_none=True)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



####### DEVELOPER-API | inspect each pipeline |

@developer_api.post("/api_test/vector_creation") 
async def test_vector_creation_api(file:UploadFile):
    created_collections = await create_vector_embedding(input_pdf=file, document_id=file.filename)
    print(created_collections)
    return {'collection_name':created_collections['collection_name'], 'status':created_collections['status']}

@developer_api.post('/api_test/vector_retrieval')
async def test_Vector_Retrieval(request:VectorRetrievalRequest):
        return await vector_retrieval_function(
        request.query_schema,
        request.collection_name)


@developer_api.post("/api_test/llm")
async def test_llm_model(test_request:test_llm_request):
    return await large_languge_model_infer(key=str(test_request.key), chunk=str(test_request.chunk_))



####### Logs
@logs_api.get("/logs/live_log")
async def live_stream_logs():
    log_file = "logs/app.log"

    if not os.path.exists(log_file):
        open(log_file, "w").close()  

    return StreamingResponse(
        tail_log_file(log_file),
        media_type="text/event-stream",   
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",   
        },
    )


@logs_api.get("/logs/latest")
async def get_latest_logs(lines: int = 100):
    log_file = "logs/app.log"

    # Ensure file exists
    if not os.path.exists(log_file):
        open(log_file, "w").close()

    try:
        with open(log_file, "r") as f:
            all_lines = f.readlines()

        # Get last N lines
        latest_logs = all_lines[-lines:]

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "lines_requested": lines,
                "logs": latest_logs
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )

@logs_api.delete("/logs/clear")
async def clear_logs():
    log_file = "logs/app.log"

    try:
        if not os.path.exists(log_file):
            open(log_file, "w").close()

        with open(log_file, "w") as f:
            f.truncate(0)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Log file cleared successfully"
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )