import uuid
import asyncio
from pathlib import Path
from src.s3.downloader import s3_downloader
from src.embeddnigs.vector_creation.create_vector import create_vector_embedding
from src.embeddnigs.vector_reterival.reterival import vector_retrieval_function
from src.s3.excel_reader import read_excel_questions
from src.ai_bom.llm import large_languge_model_infer
from src.s3.excel_writer import write_results_to_excel
from src.s3.uploade_to_s3 import s3_uploader
from src.ai_bom.ai_query_rephrase import re_phrase_ai
from backend_logs import get_logger
from src.multi_agent.embeddings import chroma_client

logger = get_logger("rag_llm_connecter.py")


# async def start_proccess(api_request_body):
#     request_dict = api_request_body.model_dump()

#     # Downloade PDF & XLSX file -> s3/client_documents
#     files_path = await s3_downloader(pdf_s3_url=str(request_dict['inputDocument']),xlsx_s3_url=str(request_dict['outputDocument']))

#     #Vector_creation
#     await create_vector_embedding(input_pdf=files_path['pdf'], document_id= Path(files_path["pdf"]).name)

#     ##EXCEL will read Here.
#     Excel_Question = await read_excel_questions(file_path=files_path['xlsx'])

#     logger.info(f"Exce Question:{Excel_Question[:5]}....")
    
#     # -> LLM model [re-phrase Question] - 1
#     # AI_re_phrased_Query = await re_phrase_ai(user_query=Excel_Question)  
    
#     # question_map = dict(zip(Excel_Question, AI_re_phrased_Query))

#     #vector reterival -3
#     question_map = {q: q for q in Excel_Question}

#     pdf_name = Path(files_path["pdf"]).name
#     logger.info(f"reteriving collection name: {pdf_name}")
#     retrived_data= await vector_retrieval_function(user_query=list(question_map.values()),reterive_collection_name=pdf_name)


#     # tasks = [] 
#     # logger.info(f"llm Answer generation Loop started! total Loop {len(question_map)}...")
#     # for original_q, rephrased_q in question_map.items():
#     #     chunk = retrived_data.get(rephrased_q, [])
#     #     tasks.append(large_languge_model_infer(key=original_q, chunk=chunk))
#     # results = await asyncio.gather(*tasks)
#     # all_results = dict(zip(question_map.keys(), results))
#     # logger.info(f"LLM generated Result: {len(all_results)}")

#     tasks = []
#     logger.info(f"llm Answer generation Loop started! total Loop {len(question_map)}...")
    
#     for original_q, query_ in question_map.items():
#         chunk = retrived_data.get(query_, [])
#         tasks.append(large_languge_model_infer(key=original_q, chunk=chunk))
         
#     results = await asyncio.gather(*tasks)
#     all_results = dict(zip(question_map.keys(), results))
#     logger.info(f"LLM generated Result: {len(all_results)}")


#     #writtening excel sheet
#     file_path_ = await write_results_to_excel(file_path=files_path['xlsx'], all_results=all_results)

#     #uploade to s3
#     original_name = Path(files_path['xlsx']).stem    
#     random_suffix = uuid.uuid4().hex[:6]      
#     new_filename = f"{original_name}-ai-bom-{random_suffix}-response.xlsx"
    
#     upload_response = await s3_uploader(
#         local_file_path=file_path_,
#         s3_key=f"outputs/{new_filename}"
#     )

#     if upload_response.get("status") == "uploaded":
#         return {
#             "status": "success",
#             "uploaded_to_s3": upload_response["url"],
#             "status_code": 200
#         }
#     else:
#         return {
#             "status": "failed",
#             "uploaded_to_s3": None, 
#             "error": upload_response.get("error"),
#             "status_code": 500
#         }
"""commented above for low accuracy in Circir Demo -1.
    implemented new agent logic included vllm - table extraction,
    llm-Quer triplet , llm for extract technical answers.
    
    commenly used only one model for [vllm, llm query, llm extract]- Qwen/Qwen3-VL-8B-Instruct
"""

from src.multi_agent.dev_final_Extraction import generate_embeddings
from src.multi_agent.rag_reterival import reterive_list_of_query
from src.multi_agent.excel_reader import read_excel_questions
from src.s3.excel_writer import write_results_to_excel
import pandas as pd
import time
import re 


# Save to EXCEL data
async def save_to_excel(all_results, filename=None):
    if not filename:
        filename = f"rag_output_{int(time.time())}.xlsx"

    cleaned_data = []

    for query, results in all_results.items():
        for item in results:

            print("item: ",item)
            cleaned_data.append({
                "Query": query.strip(),
                "Answer": item.get("answer", ""),
                "Page": ", ".join(map(str, item.get("page_number") or [])),
                "Status": item.get("status", "")
            })
    df = pd.DataFrame(cleaned_data)

    # Optional: sort by Query + Status priority
    priority = {"Exact": 0, "Partial": 1, "Approximate": 2}
    df["priority"] = df["Status"].map(priority).fillna(99)
    df = df.sort_values(by=["Query", "priority"]).drop(columns=["priority"])

    df.to_excel(filename, index=False)
    print(f"\n Saved to {filename}")

async def sanitize_collection_name(name: str):
    name = name.rsplit(".", 1)[0]
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    name = re.sub(r"^[^a-zA-Z0-9]+", "", name)
    name = re.sub(r"[^a-zA-Z0-9]+$", "", name)
    return name


async def start_proccess(api_request_body):
    request_dict = api_request_body.model_dump()
    # Downloade PDF & XLSX file -> s3/client_documents
    files_path = await s3_downloader(pdf_s3_url=str(request_dict['inputDocument']),xlsx_s3_url=str(request_dict['outputDocument']))
    ##EXCEL will read Here.
    Excel_Question = await read_excel_questions(file_path=files_path['xlsx'])
    valid_collection_name = await sanitize_collection_name(name=Path(files_path["pdf"]).name)
    logger.info(f"Exce Question:{Excel_Question[:5]}....")
    

    #functino start to create the embeddings 1st. Nothing will return 
    print("File path: ",files_path)
    client = chroma_client()

    existing_collections = [c.name for c in client.list_collections()]
    if valid_collection_name in existing_collections:
        collection = client.get_collection(name=valid_collection_name)
        if collection.count() > 0:
            logger.info(f"Collection '{valid_collection_name}' exists. Skipping embedding generation.")
        else:
            logger.info(f"Collection '{valid_collection_name}' exists but empty. Generating embeddings.")
            await generate_embeddings(document_url=files_path["pdf"], collections_name=valid_collection_name)
    else:
        logger.info(f"Collection '{valid_collection_name}' does not exist. Creating and generating embeddings.")
        await generate_embeddings(document_url=files_path["pdf"], collections_name=valid_collection_name)

         
    list_of_questions = await read_excel_questions(file_path=files_path["xlsx"]) #Read the Question in Excel sheet
    # list_of_questions = ["What is the spray water size?"] 
    final_result = await reterive_list_of_query(list_of_query=list_of_questions, collections_name=valid_collection_name)
    
    saved_file_path = await write_results_to_excel(file_path=files_path["xlsx"], all_results=final_result)
    # await save_to_excel(final_result)
    print("saved excel path:",saved_file_path)

    #uploade to s3
    original_name = Path(files_path['xlsx']).stem    
    random_suffix = uuid.uuid4().hex[:6]      
    new_filename = f"{original_name}-ai-bom-{random_suffix}-response.xlsx"
    
    upload_response = await s3_uploader(
        local_file_path=saved_file_path,
        s3_key=f"outputs/{new_filename}"
    )

    if upload_response.get("status") == "uploaded":
        return {
            "status": "success",
            "uploaded_to_s3": upload_response["url"],
            "status_code": 200
        }
    else:
        return {
            "status": "failed",
            "uploaded_to_s3": None, 
            "error": upload_response.get("error"),
            "status_code": 500
        }



    # # -> LLM model [re-phrase Question] - 1
    # # AI_re_phrased_Query = await re_phrase_ai(user_query=Excel_Question)  
    
    # # question_map = dict(zip(Excel_Question, AI_re_phrased_Query))

    # #vector reterival -3
    # question_map = {q: q for q in Excel_Question}

    # pdf_name = Path(files_path["pdf"]).name
    # logger.info(f"reteriving collection name: {pdf_name}")
    # retrived_data= await vector_retrieval_function(user_query=list(question_map.values()),reterive_collection_name=pdf_name)


    # # tasks = [] 
    # # logger.info(f"llm Answer generation Loop started! total Loop {len(question_map)}...")
    # # for original_q, rephrased_q in question_map.items():
    # #     chunk = retrived_data.get(rephrased_q, [])
    # #     tasks.append(large_languge_model_infer(key=original_q, chunk=chunk))
    # # results = await asyncio.gather(*tasks)
    # # all_results = dict(zip(question_map.keys(), results))
    # # logger.info(f"LLM generated Result: {len(all_results)}")

    # tasks = []
    # logger.info(f"llm Answer generation Loop started! total Loop {len(question_map)}...")
    
    # for original_q, query_ in question_map.items():
    #     chunk = retrived_data.get(query_, [])
    #     tasks.append(large_languge_model_infer(key=original_q, chunk=chunk))
         
    # results = await asyncio.gather(*tasks)
    # all_results = dict(zip(question_map.keys(), results))
    # logger.info(f"LLM generated Result: {len(all_results)}")


    #writtening excel sheet
    # file_path_ = await write_results_to_excel(file_path=files_path['xlsx'], all_results=all_results)

    # #uploade to s3
    # original_name = Path(files_path['xlsx']).stem    
    # random_suffix = uuid.uuid4().hex[:6]      
    # new_filename = f"{original_name}-ai-bom-{random_suffix}-response.xlsx"
    
    # upload_response = await s3_uploader(
    #     local_file_path=file_path_,
    #     s3_key=f"outputs/{new_filename}"
    # )

    # if upload_response.get("status") == "uploaded":
    #     return {
    #         "status": "success",
    #         "uploaded_to_s3": upload_response["url"],
    #         "status_code": 200
    #     }
    # else:
    #     return {
    #         "status": "failed",
    #         "uploaded_to_s3": None, 
    #         "error": upload_response.get("error"),
    #         "status_code": 500
    #     }

    

    