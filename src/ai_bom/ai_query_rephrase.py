import re
import json
from openai import OpenAI
from src.ai_bom.llm import client
from src.ai_bom.prompts import instruction
from backend_logs import get_logger

logger = get_logger("ai_query_rephrase")


async def clean_json_string(raw_str):
    # Remove potential lead-in text from the LLM (like "Here is the JSON:")
    if "{" in raw_str:
        raw_str = raw_str[raw_str.find("{"):raw_str.rfind("}")+1]
    
    # Replace raw newlines inside strings with escaped newlines
    # This is often what causes 'Unterminated string'
    cleaned = raw_str.replace('\n', '\\n').replace('\r', '\\r')
    return cleaned

async def re_phrase_ai(user_query:list):
    Rephrased_Query=[]
    logger.info(f"Rephrase - ai engine Started...")
    for Query_Keyword in user_query:
        ai_model_response = client.chat.completions.create(
                model="/home/ubuntu/circor_qwen_model/model",
                messages=[
                    {
                        "role": "system", 
                        "content": instruction.re_phrase_system_prompt.format(user_input_question=Query_Keyword)
                    },
                    {
                        "role": "user", 
                        "content": instruction.re_phrase_user_prompt.format(keyword=Query_Keyword)
                    }
                ],
                temperature=0,
                response_format={ "type": "json_object" } #Forces JSON if your model supports it
            )        
        
        generated_query = ai_model_response.choices[0].message.content
        try:
            data = json.loads(generated_query)
        except json.JSONDecodeError:
            cleaned_response = await clean_json_string(generated_query)
            data = json.loads(cleaned_response)
        
        Rephrased_Query.append(data['question'])
    logger.info(f"No of [{len(Rephrased_Query)}] User Queries Re-Phrased")
    return Rephrased_Query




# import asyncio
# asyncio.run(re_phrase_ai(user_query=["Trim","Approvals","LD Clause"]))
