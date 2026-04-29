import json
from pathlib import Path
from src.ai_bom.prompts import instruction
from backend_logs import get_logger
from src.s3.downloader import s3_file_name,s3_downloader
from src.embeddnigs.vector_reterival.reterival import vector_retrieval_function
from src.embeddnigs.vector_creation.create_vector import create_vector_embedding
from src.multi_agent.embeddings import TenderRAG
from src.multi_agent.url_config import client

logger = get_logger("chat_ai_model")


class chat_model:
    def __init__(self):
        pass
    
    async def clean_json_string(self, raw_str):
        if "{" in raw_str:
            raw_str = raw_str[raw_str.find("{"):raw_str.rfind("}")+1]
        cleaned = raw_str.replace('\n', '\\n').replace('\r', '\\r')
        return cleaned


    async def retrival_data(self, s3_link:str, user_chat:str):

        collection_name_ = await s3_file_name(name=Path(s3_link).name)
        rag_engine = TenderRAG(collection_name=collection_name_)

        print("COLLECTION_NAME:",collection_name_)
        reterive_result = []
        for query in user_chat:
            result = await rag_engine.query(question=query)
            reterive_result.append(result)


        """Old"""
        # retrived_data= await vector_retrieval_function(user_query=[user_chat],
        #                                                reterive_collection_name=collection_name_,
        #                                                top_k_value=3)
        return reterive_result

    async def chat_pdf_retrival_data(self, s3_link:str, user_chat:str):

        collection_name_ = await s3_file_name(name=Path(s3_link).name)
        rag_engine = TenderRAG(collection_name=collection_name_)
        print("[+]Reteriving collection for chat PDF:",collection_name_)
        result = await rag_engine.query(question=user_chat)

        # print("[+]Reterive result: ",result)
        return result
    

    async def call_vector_creation(self,excel_link,user_query_):
        excel_downloaded_path = await s3_downloader(xlsx_s3_url=str(excel_link)) #Donwlode EXCL;
        
        await create_vector_embedding(input_pdf=excel_downloaded_path['xlsx'],
                                      document_id= Path(excel_downloaded_path["xlsx"]).name,
                                      doc_type="xlsx")
        
        excel_name = Path(excel_downloaded_path["xlsx"]).name
        vector_reterivd_data = await vector_retrieval_function(user_query=[user_query_],reterive_collection_name=excel_name)
        return vector_reterivd_data


    async def llm_chat_engine(self, S3buckt_link:str, user_chat_query, document_type):

        if document_type == "pdf":
            retrived_content = await self.chat_pdf_retrival_data(s3_link=S3buckt_link,
                                                    user_chat=user_chat_query)
        else:
            retrived_content = await self.call_vector_creation(S3buckt_link,user_chat_query)


        try:
            # response = client.chat.completions.create(
            #     model="/home/ubuntu/circor_qwen_model/model",
            #     messages=[
            #         {
            #             "role": "system", 
            #             "content": instruction.chatbot_system_prompt
            #         },
            #         {
            #             "role": "user", 
            #             "content": instruction.chatbot_user_prompt.format(question=user_chat_query,context=retrived_content)
            #         }
            #     ],
            #     temperature=0,
            #     response_format={ "type": "json_object" } #Forces JSON if your model supports it
            # )
            
            user_prompt = instruction.chatbot_user_prompt.format(question=user_chat_query,context=retrived_content["documents"][0])
            system_prompt = instruction.chatbot_system_prompt

            # print("/nsystem prompt: ",system_prompt)
            response = client.chat.completions.create(
            model="Qwen/Qwen3-VL-8B-Instruct",   #FIXED
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            timeout=300)
            try:
                # Accessing content is much cleaner
                raw_content = response.choices[0].message.content
                print("Raw_Contente from LLM:",raw_content)
            except Exception as E:
                logger.error(f"Chatbot Response ERROR:{str(E)}")
                logger.error(f"Faild chatbot Response: {raw_content}")

            try:
                # Usage
                try:
                    data = json.loads(raw_content)
                except json.JSONDecodeError:
                    cleaned_response = await self.clean_json_string(raw_content)
                    data = json.loads(cleaned_response)
            except Exception as E:
                logger.error(f"Chatboat Model output JSON Parsing Issue: {str(E)}")
                logger.error(f"try to convert chabot repsonse to JSON: {raw_content}")

            logger.info("chatbot response comepleted!")
            logger.info(f"chatbot api completed | status = 200 | api response = success")

            print("[+]Assistant data:",data)
            return {'assistant':data,"status":"200"}

        except Exception as e:
            logger.error(f"chatbot Response failed: {str(e)}")
            return {'assistant':"faild","status":"500","error":str(e)}


