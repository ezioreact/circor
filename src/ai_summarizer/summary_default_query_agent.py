"""
This module provides functionality to generate a summary based on five pre-defined custom question 

Workflow:
    - For each question, the system reterives the top 3 relevant chunks
    - These reterived chunks are then passed to the AI model
    - AI model generate a summary using the selected chunks.

Purpose:
    To ensure focused and contextually relevatn summarization by leveraging targeted reterival for each question.
"""
import json
from backend_logs import get_logger
from src.ai_bom.llm import client
from src.ai_bom.prompts import instruction
from default_question import load_default_question
from src.ai_bom.prompts import instruction
from src.ai_chatbot.chat_ai_model import chat_model

logger = get_logger('summary agent')
call_chat_model_class = chat_model()

async def clean_json_string(raw_str):
    if "{" in raw_str:
        raw_str = raw_str[raw_str.find("{"):raw_str.rfind("}")+1]
    cleaned = raw_str.replace('\n', '\\n').replace('\r', '\\r')
    return cleaned

#reterival:


async def generate_default_summary(summary_size:200):
    total_summary = []
    default_question = await load_default_question()

    for Question in default_question['questions']:
        # reterived_data = await call_chat_model_class.retrival_data(s3_link=s3_url,user_chat=Question)
        print("[+]Default summary question: ",Question)
        try: 
            # response = client.chat.completions.create(
            #     model="/home/ubuntu/circor_qwen_model/model",
            #     messages=[
            #         {
            #             "role": "system", 
            #             "content": instruction.default_summary_sys_prmpt.format(default_question=str(Question))
            #         },
            #         {
            #             "role": "user", 
            #             "content": instruction.default_summary_user_prompt.format(TEXT=str(reterived_data), 
            #                                                             TARGET_TOKENS=str(summary_size),
            #                                                             default_question=str(default_question))
            #         }
            #     ],
            #     temperature=0,
            #     response_format={ "type": "json_object" } 
            # )
            
            user_prompt = instruction.default_summary_user_prompt.format(TEXT=str(Question), 
                                                                        TARGET_TOKENS=str(summary_size),
                                                                        default_question=str(default_question))
            system_prompt = instruction.default_summary_sys_prmpt.format(default_question=str(Question))
            
            response = client.chat.completions.create(
            model="Qwen/Qwen3-VL-8B-Instruct",   #FIXED
            
            messages=[
                {"role": "system", "content": user_prompt},
                {"role": "user", "content": system_prompt}
            ],
            temperature=0,
            timeout=300)

            try:
                raw_content = response.choices[0].message.content
            except Exception as E:
                logger.error(f"summary agent response ERROR:{str(E)}")
                logger.error(f"summary agent raw response: {raw_content}")

            try:
                try:
                    data = json.loads(raw_content)
                except json.JSONDecodeError:
                    cleaned_response = await clean_json_string(raw_content)
                    data = json.loads(cleaned_response)
            except Exception as E:
                logger.error(f"summary agent output JSON Parsing Issue: {str(E)}")
                logger.error(f"try to convert JSON: {raw_content}")
            
            total_summary.append(data)

        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            return None
    return " ".join([item.get("summary", "").strip() for item in total_summary])