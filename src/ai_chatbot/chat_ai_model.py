import json
from pathlib import Path
from src.ai_bom.prompts import instruction
from backend_logs import get_logger
from src.s3.downloader import s3_file_name,s3_downloader
from src.embeddnigs.vector_reterival.reterival import vector_retrieval_function
from src.embeddnigs.vector_creation.create_vector import create_vector_embedding
from src.multi_agent.embeddings import TenderRAG
from src.multi_agent.url_config import client
import base64
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os
import asyncio



load_dotenv()
logger = get_logger("chat_ai_model")
bucket_name = os.getenv("BUCKET_NAME")

# class chat_model:
#     def __init__(self):
#         pass
    
#     async def clean_json_string(self, raw_str):
#         if "{" in raw_str:
#             raw_str = raw_str[raw_str.find("{"):raw_str.rfind("}")+1]
#         cleaned = raw_str.replace('\n', '\\n').replace('\r', '\\r')
#         return cleaned


#     async def retrival_data(self, s3_link:str, user_chat:str):

#         collection_name_ = await s3_file_name(name=Path(s3_link).name)
#         rag_engine = TenderRAG(collection_name=collection_name_)

#         print("COLLECTION_NAME:",collection_name_)
#         reterive_result = []
#         for query in user_chat:
#             result = await rag_engine.query(question=query)
#             reterive_result.append(result)


#         """Old"""
#         # retrived_data= await vector_retrieval_function(user_query=[user_chat],
#         #                                                reterive_collection_name=collection_name_,
#         #                                                top_k_value=3)
#         return reterive_result

#     async def chat_pdf_retrival_data(self, s3_link:str, user_chat:str):

#         collection_name_ = await s3_file_name(name=Path(s3_link).name)
#         rag_engine = TenderRAG(collection_name=collection_name_)
#         print("[+]Reteriving collection for chat PDF:",collection_name_)
#         result = await rag_engine.query(question=user_chat)
#         return result, collection_name_
    

#     async def call_vector_creation(self,excel_link,user_query_):
#         excel_downloaded_path = await s3_downloader(xlsx_s3_url=str(excel_link)) #Donwlode EXCL;
        
#         await create_vector_embedding(input_pdf=excel_downloaded_path['xlsx'],
#                                       document_id= Path(excel_downloaded_path["xlsx"]).name,
#                                       doc_type="xlsx")
        
#         excel_name = Path(excel_downloaded_path["xlsx"]).name
#         vector_reterivd_data = await vector_retrieval_function(user_query=[user_query_],reterive_collection_name=excel_name)
#         return vector_reterivd_data

#     async def convert_base64(self, page_image):
#         """
#         Converts a file path string or a PageImage object to optimized JPEG Base64 string.
#         """
#         try:
#             buffer = BytesIO()
#             # Check if the input is a file path string
#             if isinstance(page_image, str):
#                 # Open the image from the local disk path
#                 rgb_image = Image.open(page_image).convert("RGB")
#             else:
#                 # Fallback for PageImage object (which has an .original attribute)
#                 rgb_image = page_image.original.convert("RGB") 
                
#             # Save and optimize
#             rgb_image.save(buffer, format="JPEG", quality=85, optimize=True)
#             return base64.b64encode(buffer.getvalue()).decode("utf-8")
            
#         except Exception as E:
#             print("[-][-]Base 64 conversion Error:", str(E))
#             return None
    
import os
import json
from pathlib import Path
from src.ai_bom.prompts import instruction
from backend_logs import get_logger
from src.s3.downloader import s3_file_name, s3_downloader
from src.embeddnigs.vector_reterival.reterival import vector_retrieval_function
from src.embeddnigs.vector_creation.create_vector import create_vector_embedding
from src.multi_agent.embeddings import TenderRAG
from src.multi_agent.url_config import client
from src.s3.uploade_to_s3 import get_s3_client
import httpx
from openai import APIConnectionError, APITimeoutError, InternalServerError


logger = get_logger("chat_ai_model")

RAG_REGISTRY = {}

class chat_model:
    def __init__(self):
        self.encoded_dir = "encoded_images"
    
    async def clean_json_string(self, raw_str):
        if "{" in raw_str:
            raw_str = raw_str[raw_str.find("{"):raw_str.rfind("}")+1]
        cleaned = raw_str.replace('\n', '\\n').replace('\r', '\\r')
        return cleaned

    async def get_rag_engine(self, s3_link: str) -> TenderRAG:
        """Dynamically retrieves or creates a RAG engine for a specific document."""
        collection_name = await s3_file_name(name=Path(s3_link).name)
        
        if collection_name not in RAG_REGISTRY:
            logger.info(f"Initializing new TenderRAG engine for: {collection_name}")
            # Initialize the engine once
            RAG_REGISTRY[collection_name] = TenderRAG(collection_name=collection_name)
        
        return RAG_REGISTRY[collection_name], collection_name


    async def retrival_data(self, s3_link:str, user_chat:str):
        rag_engine, collection_name = await self.get_rag_engine(s3_link)
        print(f"[+] Using active collection: {collection_name}")
        
        reterive_result = []
        for query in user_chat:
            result = await rag_engine.query(question=query)
            reterive_result.append(result)
        return reterive_result


        # collection_name_ = await s3_file_name(name=Path(s3_link).name)
        # rag_engine = TenderRAG(collection_name=collection_name_)

        # print("COLLECTION_NAME:", collection_name_)
        # reterive_result = []
        # for query in user_chat:
        #     result = await rag_engine.query(question=query)
        #     reterive_result.append(result)
        # return reterive_result


    async def chat_pdf_retrival_data(self, s3_link:str, user_chat:str, filter:str):
        rag_engine, collection_name = await self.get_rag_engine(s3_link)
        print(f"[+] Using active collection: {collection_name}")
        
        # This calls your high-n_results retrieval logic we discussed earlier
        result = await rag_engine.chat_query(question=user_chat,where_filter=filter)
        return result, collection_name


        # collection_name_ = await s3_file_name(name=Path(s3_link).name)
        # rag_engine = TenderRAG(collection_name=collection_name_)
        # print("[+]Reteriving collection for chat PDF:", collection_name_)
        # result = await rag_engine.chat_query(question=user_chat)
        # return result, collection_name_


    async def call_vector_creation(self, excel_link, user_query_):
        excel_downloaded_path = await s3_downloader(xlsx_s3_url=str(excel_link))
        
        await create_vector_embedding(input_pdf=excel_downloaded_path['xlsx'],
                                      document_id=Path(excel_downloaded_path["xlsx"]).name,
                                      doc_type="xlsx")
        
        excel_name = Path(excel_downloaded_path["xlsx"]).name
        vector_reterivd_data = await vector_retrieval_function(user_query=[user_query_], reterive_collection_name=excel_name)
        return vector_reterivd_data, excel_name


    async def get_s3_url(self, s3_key, expiration=3600):
        """Generates a presigned URL to retrieve a specific file from S3"""
        try:
            loop = asyncio.get_running_loop()
            url = await loop.run_in_executor(
                None,
                lambda: get_s3_client().generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': s3_key},
                    ExpiresIn=expiration
                )
            )
            return url
        except Exception as e:
            print("[-] S3 link reterive issue.:",str(e))
            logger.error(f"Error generating presigned URL: {e}")
            return None


    async def llm_chat_engine(self, S3buckt_link:str, user_chat_query, document_type, where):
        collection = ""
        if document_type == "pdf":
            retrived_content, collection = await self.chat_pdf_retrival_data(s3_link=S3buckt_link,
                                                                             user_chat=user_chat_query,
                                                                             filter=where)
        else:
            retrived_content, collection = await self.call_vector_creation(S3buckt_link, user_chat_query)
           
        try:

            # Match status buckets
            exact_matches = []
            partial_matches = []
            approx_matches = []
            not_found_matches = []

            # ------------------------------------------------------------------
            # Loop through each retrieved chunk individually (up to 5 chunks)
            # ------------------------------------------------------------------


            # print("[+]Reterived_content: ",retrived_content)
            documents = retrived_content.get("documents", [])
            metadatas = retrived_content.get("metadatas", [])

            print(f"[+] Processing {len(documents)} chunks individually through the LLM.")

            for doc, meta in zip(documents, metadatas):
                page_num = meta.get("page", 1)
                
                # Dynamic Base64 load for current chunk's page number
                image_base64 = None
                image_file_name = f"{collection}_page_{page_num}.txt"
                
                #retrieve from S3   
                
                cloud_link = ""

                image_path = os.path.join(self.encoded_dir, image_file_name)                
                if os.path.exists(image_path):
                    print(f"  [+] Found dynamic base64 image for Page {page_num}: {image_path}")
                    with open(image_path, "r", encoding="utf-8") as img_f:
                        image_base64 = img_f.read().strip()
                    specific_s3_key = f"ai-extracted-table-image/{collection}_page_{page_num}.png"
                    #specific_s3_key = f"ai-extracted-table-image/{collection}_page_{page_num}.png"
                    cloud_link = await self.get_s3_url(specific_s3_key)
                else:
                    print(f"[-] Base64 file not found for Page {page_num}: {image_path}")
                    print("[+]Doc: ",doc[:50],".......")
                    cloud_link = "This is from paragraph please find in PDF Document."

                # Prepare individual chunk context
                user_prompt = instruction.chatbot_user_prompt.format(question=user_chat_query)
                system_prompt = instruction.chatbot_system_prompt
                
                # Attach the base64 image if it exists for the page
                if image_base64:
                    user_message_content  = [{"type": "text", "text": user_prompt},{
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    }]

                else:
                    hybrid_prompt = (
                        f"Context from Page {page_num}:\n"
                        f"-------------------\n{doc}\n-------------------\n\n")
                    
                    user_message_content = [{"type": "text", "text": user_prompt},
                                            {"type": "text", "text": hybrid_prompt}]
  
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message_content}
                ]

                # Invoke the multimodal model for this chunk
                
                try:
                    response = client.chat.completions.create(
                        model="Qwen/Qwen3-VL-8B-Instruct",
                        messages=messages,
                        temperature=0.7,
                        timeout=300
                    )

                    raw_content = response.choices[0].message.content
                    print("[+] VLLM Model is LIVE")

                except APITimeoutError as e:
                    logger.error(f"[X] VLLM Timeout Error: {str(e)}")

                    return {
                        "assistant": "VLLM model timeout. GPU may be overloaded.",
                        "status": "503",
                        "error": str(e)
                    }

                except APIConnectionError as e:
                    logger.error(f"[X] VLLM Connection Error: {str(e)}")

                    return {
                        "assistant": "Unable to connect to VLLM server.",
                        "status": "503",
                        "error": str(e)
                    }

                except InternalServerError as e:
                    logger.error(f"[X] VLLM Internal Server Error: {str(e)}")

                    return {
                        "assistant": "VLLM internal server error. GPU/model may be unavailable.",
                        "status": "503",
                        "error": str(e)
                    }

                except httpx.ConnectError as e:
                    logger.error(f"[X] Network Connection Failed: {str(e)}")

                    return {
                        "assistant": "Network issue while connecting to GPU server.",
                        "status": "503",
                        "error": str(e)
                    }

                except Exception as e:
                    logger.error(f"[X] Unknown VLLM Failure: {str(e)}")

                    return {
                        "assistant": "VLLM model is unavailable.",
                        "status": "503",
                        "error": str(e)
                    }

                # Parse Chunk output to JSON
                try:
                    try:
                        data = json.loads(raw_content)
                        data['page'] = page_num
                        data['source'] = cloud_link
                    except json.JSONDecodeError:
                        cleaned_response = await self.clean_json_string(raw_content)
                        data = json.loads(cleaned_response)
                        data['page'] = page_num
                        data['source'] = cloud_link

                except Exception as E:
                    logger.error(f"JSON Parsing failed for chunk output. Raw: {raw_content[:100]}")
                    data = {"match_type": "not found", "content": raw_content}

                # Evaluate the type of matching dynamically
                # It evaluates raw_content or any 'match_type' key returned by your prompt

                # print("Response data :",data)
                match_type_str = str(data.get("status", "not found")).lower() if isinstance(data, dict) else "not found"
                # print("Match_st: ",match_type_str)
                if "exact" in match_type_str:
                    exact_matches.append(data)
                elif "partial" in match_type_str:
                    partial_matches.append(data)
                elif "approx" in match_type_str:
                    approx_matches.append(data)
                else:
                    not_found_matches.append(data)

            # ------------------------------------------------------------------
            # Return Tiered fallback evaluation list
            # ------------------------------------------------------------------
        
            
            if exact_matches:
                print(f"[+] Returning exact matches count: {len(exact_matches)}")
                return {
                    'assistant': exact_matches, 
                    'status': "200"
                }
            elif partial_matches:
                print(f"[+] Returning partial matches count: {len(partial_matches)}")
                return {
                    'assistant': partial_matches, 
                    'status': "200"  
                }
            elif approx_matches:
                print(f"[+] Returning approx matches count: {len(approx_matches)}")
                return {
                    'assistant': approx_matches, 
                    'status': "200"
                }
            else:
                print(f"[-] No matches found. Returning default fallback count: {len(not_found_matches)}")
                return {
                    'assistant': not_found_matches, 
                    'status': "200"
                }
        
        except Exception as E:
            print("Chat model function faild: ",str(E))