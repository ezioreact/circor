
import time
import json
import re
from src.multi_agent.prompts import instruction
from openai import OpenAI
from src.multi_agent.convert_string import triplet_to_string
from src.multi_agent.url_config import gpu_server_url
from src.multi_agent.url_config import client
from src.multi_agent.llm_json_repair import json_parse_repairing

# url = f"http://{gpu_server_url}/v1"

# client = OpenAI(
#     base_url=url,
#     api_key="mysecret32123123"
# )
async def safe_json_loads(content):
    try:
        return json.loads(content)

    except Exception:
        # Step 1: Extract JSON array
        match = re.search(r"\[.*\]", content, re.DOTALL)
        
        if match:
            extracted = match.group(0)

            try:
                return json.loads(extracted)
            except Exception:
                # Step 2: Repair extracted JSON
                try:
                    return await json_parse_repairing(json_docs=extracted)
                except Exception:
                    print(" Invalid JSON after extraction:\n", extracted)
                    return []

        # Step 3: Repair full content
        try:
            return await json_parse_repairing(json_docs=content)
        except Exception:
            print(" Invalid JSON:\n", content)
            return []
        


# async def call_llm_model_infer(json_doc):

#     # print("LLM input:", json_doc)

#     prompt = instruction.user_context.format(json_doc=json_doc)
 
#     response = client.chat.completions.create(
#         model="Qwen/Qwen3-VL-8B-Instruct",   #FIXED Qwen/Qwen3-VL-8B-Instruct
#         messages=[
#             {"role": "system", "content": instruction.system_instruction},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0,
#         timeout=300
#     )

#     print("Call llm model infer: ",response)
#     content = response.choices[0].message.content

#     if not content or content.strip() == "":
#         print("Empty response")
#         return []

#     triplets = await safe_json_loads(content)

#     return await triplet_to_string(triplets)
"""comment above for to avoide the openai timeout error in mid way. so 
will hit request lib insteead of openai."""


import httpx
import json
import re
import asyncio
from src.multi_agent.prompts import instruction
from src.multi_agent.convert_string import triplet_to_string
from src.multi_agent.url_config import url
from src.multi_agent.llm_json_repair import json_parse_repairing

# Configuration
API_KEY = "new_secret_key"
URL = url+"/chat/completions"

async def call_llm_model_infer(json_doc):
    prompt = instruction.user_context.format(json_doc=json_doc)
    
    # Headers for the request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Payload matching OpenAI format
    payload = {
        "model": "Qwen/Qwen3-VL-8B-Instruct",
        "messages": [
            {"role": "system", "content": instruction.system_instruction},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }

    try:
        # Use httpx for async requests
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(URL, headers=headers, json=payload)
            
            # Catch 401 specifically to debug auth issues
            if response.status_code == 401:
                print(f"[!] Authentication Error (401): Check your API Key. Response: {response.text}")
                return []
            
            response.raise_for_status()
            result_json = response.json()
            
            content = result_json['choices'][0]['message']['content']
            print("[+]LLM [knowledge graph] Response received from GPU server.")

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        print(f"Request failed: {e}")
        return []

    if not content or content.strip() == "":
        print("Empty response")
        return []

    triplets = await safe_json_loads(content)
    return await triplet_to_string(triplets)




# LLM= {
#   "documentMetadata": {
#     "TD-201": "Rev No.00",
#     "Form No.": "",
#     "PRODUCT STANDARD": "HYDERABAD",
#     "TC": "65132",
#     "Rev No.": "03",
#     "Page": "14 of 28",
#     "COPYRIGHT AND CONFIDENTIAL": "The information on this document is the property of BHARAT HEAVY ELECTRICALS LIMITED. It must not be used directly or indirectly in any way detrimental to the interest of the company.",
#     "Ref.": "",
#     "Doc": ""
#   },
#   "mainSection": {
#     "e)": "Actuator spring shall be manufactured out of corrosion resistant steel and shall be nickel-plated. Alternately vendor standard coating is also acceptable. The spring shall be enclosed in the actuator casing.",
#     "f)": "Each desuperheater actuator and valve actuator shall be provided with stem position indicator with scale calibrated from 0 to 100% in steps of 10%.",
#     "g)": "While sizing the actuator, vendor must ensure that the sizing factors indicated below are fully complied. Higher sizing factor may be considered if found necessary by vendor.",
#     "i)": "For leakage class IV and below, the actuator shall be sized considering actuator thrust more than 1.3 times the total force induced by shut-off conditions specified in the data sheet and the force required to overcome packing friction. Vendor shall utilize this factor as 1.5 in case the desuperheater/PRDS is operating between 80% to 90% or 10% to 20% in any of the specified conditions.",
#     "ii)": "For leakage class V and above, the actuator shall be sized considering actual thrust more than 1.7 times the total force induced by specified shut-off conditions in the purchaser's data sheet and the force required to overcome packing friction.",
#     "h)": "The stroke time with positioner for open / close shall be equal to valve body size in seconds.",
#     "j)": "The actuator shall be designed to move the valve to the failure position specified in the datasheet / variant table.",
#     "k)": "Actuator casing shall be made of pressed steel. Non-metallic actuator casings shall not be offered.",
#     "l)": "Springs shall be corrosion-resistant and shall be cadmium or nickel-plated. Alternately vendor standard coating shall also be acceptable if accepted by customer. These shall be of the enclosed type. The compression of the springs shall be adjustable.",
#     "m)": "In general, an actuator operating range of 0.2-to 1.0 kg/cm2g is preferred. However, when vendor standard actuator model is not able to meet the specified shutoff pressure, higher actuator operating range may be offered.",
#     "n)": "In general, spring opposed diaphragms type actuators shall be used. Only when this type of actuator becomes extremely unwieldy, based on the data specified in the datasheet / variant table, should a piston and cylinder type of actuator be considered.",
#     "o)": "Whenever piston and cylinder actuator is considered, single acting spring return type shall be used.",
#     "p)": "Whenever double acting spring less type of actuator is unavoidable, all accessories like pilot valves, booster relays, non-return valve, pressure gauge, volume tank etc. shall be provided to ensure desired action on air failure. The volume tank shall be sized considering full stroking of the valve for THREE complete cycles. The volume tank shall be of carbon steel, epoxy painted or stainless steel construction (refer datasheet) and sized as per ASME Section VIII with design pressure of 10.5 kg/cm2g gas a minimum. Accessories like pressure relief valves, pressure gauge and tubing shall be of 316/316L Stainless"
#   }
# }


# call_llm_model_infer(LLM)