import json
from src.ai_bom.prompts import instruction
from src.ai_bom.llm import client
from src.ai_chatbot.chat_ai_model import chat_model
from backend_logs import get_logger
from typing import Optional


logger = get_logger("summary-model")
call_chat_ai_class = chat_model()



async def clean_json_string(raw_str):
    if "{" in raw_str:
        raw_str = raw_str[raw_str.find("{"):raw_str.rfind("}")+1]
    cleaned = raw_str.replace('\n', '\\n').replace('\r', '\\r')
    return cleaned



async def call_summary_model(Human_input:str, summary_size:str, s3_url, modify: Optional[bool] = False, general_summary: Optional[str] = None ):

    if modify: #True
        reterived_data = await call_chat_ai_class.retrival_data(s3_link=s3_url,user_chat=Human_input)
        # reterived_data = reterived_data["documents"][0]
        # print("document:",reterived_data)
        # chunks = reterived_data["documents"][0]

        all_results = []

        for chunk in reterived_data:
            try: 
                # response = client.chat.completions.create(
                #     model="/home/ubuntu/circor_qwen_model/model",
                #     messages=[
                #         {
                #             "role": "system", 
                #             "content": instruction.summary_sys_prompt.format(TARGET_TOKENS=str(summary_size))
                #         },
                #         {
                #             "role": "user", 
                #             "content": instruction.summary_user_prompt.format(TEXT=str(reterived_data), 
                #                                                               TARGET_TOKENS=str(summary_size),
                #                                                               USER_INSTRUCTION=str(Human_input))
                #         }
                #     ],
                #     temperature=0,
                #     response_format={ "type": "json_object" } 
                # )


                """above is working but old one. below is vlmm model"""
                user_prompt = instruction.summary_user_prompt.format(TEXT=str(chunk), 
                                                                            TARGET_TOKENS=str(summary_size),
                                                                            USER_INSTRUCTION=str(Human_input))
                system_prompt = instruction.summary_sys_prompt.format(TARGET_TOKENS=str(summary_size))
                # print("user_prompt: ",user_prompt)

                # print("/nsystem prompt: ",system_prompt)
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
                    logger.error(f"Raw model response ERROR:{str(E)}")
                    logger.error(f"model raw response: {raw_content}")

                try:
                    try:
                        data = json.loads(raw_content)
                    except json.JSONDecodeError:
                        cleaned_response = await clean_json_string(raw_content)
                        data = json.loads(cleaned_response)
                except Exception as E:
                    logger.error(f"Model output JSON Parsing Issue: {str(E)}")
                    logger.error(f"try to convert JSON: {raw_content}")
                all_results.append(data)

            except Exception as e:
                logger.error(f"Extraction failed: {str(e)}")
                return None

        return all_results

    else:
        if not general_summary:
            logger.error("general_summary is required when modify=False")
            raise ValueError("general_summary is required when modify=False")

        reterived_data = general_summary
        
        try: 
            print("retetive data: ",reterived_data)
            """above is working but old one. below is vlmm model"""
            user_prompt = instruction.summary_user_prompt.format(TEXT=str(reterived_data), 
                                                                        TARGET_TOKENS=str(summary_size),
                                                                        USER_INSTRUCTION=str(Human_input))
            system_prompt = instruction.summary_sys_prompt.format(TARGET_TOKENS=str(summary_size))
            print("user_prompt: ",user_prompt)

            print("/nsystem prompt: ",system_prompt)
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
                logger.error(f"Raw model response ERROR:{str(E)}")
                logger.error(f"model raw response: {raw_content}")

            try:
                try:
                    data = json.loads(raw_content)
                except json.JSONDecodeError:
                    cleaned_response = await clean_json_string(raw_content)
                    data = json.loads(cleaned_response)
            except Exception as E:
                logger.error(f"Model output JSON Parsing Issue: {str(E)}")
                logger.error(f"try to convert JSON: {raw_content}")
            return data

        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            return None

