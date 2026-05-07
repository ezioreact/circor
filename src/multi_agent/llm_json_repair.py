Json_repair_prompt = """You are a JSON repair tool.
Your task:
- Fix invalid JSON.
- Do NOT add, remove, or infer any data.
- Preserve all keys and values exactly as given, EXCEPT for unit symbols.
- Only correct syntax issues (quotes, commas, brackets, nulls, etc.)

UNIT CONVERSION RULES:
- When encountering measurements, always convert symbols to full words. 
- Replace the double quote symbol (") within a value with 'inches'.
- Replace the single quote symbol (') within a value with 'feet'.
- Example: Change [1"] to [1 inches] and [5'] to [5 feet].

STRICT RULES:
- Output ONLY valid JSON.
- No explanation.
- No comments.
- No extra text.
- Do not wrap in markdown.
- Do not hallucinate missing values.
- If value is incomplete, keep it as is or set to null.

Ensure:
- Proper double quotes for keys and strings.
- Replace Python None/True/False → null/true/false.
- Fix trailing commas and close brackets properly.
"""


user_json_prompt = """
input_json: {json_data}
"""

import json
from openai import OpenAI
from src.multi_agent.url_config import gpu_server_url
from src.multi_agent.url_config import client


# url = f"http://{gpu_server_url}/v1"
# client = OpenAI(
#     base_url=url,
#     api_key="mysecret32123123"
# )

async def json_parse_repairing(json_docs):
    user_prompt = user_json_prompt.format(json_data=json_docs)

    response = client.chat.completions.create(
        model="Qwen/Qwen3-VL-8B-Instruct",   #FIXED
        messages=[
            {"role": "system", "content": Json_repair_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        timeout=300
    )
    content = response.choices[0].message.content
    
    if not content or content.strip() == "":
        print("Empty response")
        return []
    
    try:
        return json.loads(content)
    
    except Exception as E:
        print(f"Json repairng llm is faild: {str(E)} | input_content: {json_docs} \n llm json repaired content: {content}")
        return []
    

    