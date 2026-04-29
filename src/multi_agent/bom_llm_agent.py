import time
import json
import re
from src.multi_agent.prompts import instruction
from openai import OpenAI
from src.multi_agent.url_config import gpu_server_url
from src.multi_agent.llm_json_repair import json_parse_repairing
from src.multi_agent.url_config import client
import asyncio

# url = f"http://{gpu_server_url}/v1"

# client = OpenAI(
#     base_url=url,
#     api_key="mysecret32123123"
# )

async def safe_json_loads(content):
    try:
        return json.loads(content)
    except Exception:
        # match = re.search(r"\[.*\]", content, re.DOTALL)
        match = re.search(r"\{.*\}|\[.*\]", content, re.DOTALL)

        if match:
            json_str = match.group(0)
            json_str = json_str.replace("None", "null")

            try:
                return json.loads(json_str)
            except Exception as e:
                print("Still invalid JSON:", json_str)
                print("Error:", e)
                print("content: ",content)
                return await json_parse_repairing(content)
            
        else:
            print(" Invalid JSON:\n", content)
            return await json_parse_repairing(content)


import base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

import os 
# async def bom_agent_infer(json_doc,user_query, image_path=None):
#     user_prompt = instruction.bom_user_context.format(chunk="Please refer the input image as a Chunk", user_query=user_query)
    
#     content_list = [{"type": "text", "text": user_prompt}]
    
#     if image_path and os.path.exists(image_path):

#         try:
#             base64_image = encode_image(image_path)
#             content_list.append({
#                 "type": "image_url",
#                 "image_url": {"url": f"data:image/png;base64,{base64_image}"},
#                 "detail": "high"
#             })
#             # user_prompt = instruction.bom_user_context.format(chunk="Please refer the input image as a Chunk", user_query=user_query)

#             print("[+]user prompt: ",user_prompt)
                    
#         except Exception as e:
#             print(f"Error encoding image at {image_path}: {e}")

#     response = client.chat.completions.create(
#         model="Qwen/Qwen3-VL-8B-Instruct",   #FIXED
#         messages=[
#             {"role": "system", "content": instruction.bom_system_instruction},
#             {"role": "user", "content": content_list}
#         ],
#         temperature=0.7,
#         timeout=300
#     )
#     content = response.choices[0].message.content
    
#     if not content or content.strip() == "":
#         print("Empty response")
#         return []
    
#     response_safe =  await safe_json_loads(content)
#     return response_safe


async def bom_agent_infer(json_doc, user_query, image_path=None, switch_to_image=True):
    """
    Dynamic inference agent.
    switch_to_image: If True, uses image pixels. If False, uses json_doc text.
    """
    
    # 1. Determine the "Chunk" text based on the switch
    # We only tell the model to look at the image if we are actually sending one
    if switch_to_image and image_path and os.path.exists(image_path):
        display_chunk = "Please refer to the attached visual image as the primary data source."
        use_visuals = True
    else:
        display_chunk = json_doc
        use_visuals = False

    # 2. Format the user prompt
    user_prompt = instruction.bom_user_context.format(
        chunk=display_chunk, 
        user_query=user_query
    )
    
    # 3. Build the content list
    content_list = [{"type": "text", "text": user_prompt}]
    
    print("VLLM input image path: ",image_path)
    # print("[+]\n user prompt VLLM image passing: ",content_list)

    # input(".....")
    # 4. Add the image ONLY if switch is True and file exists
    if use_visuals:
        try:
            base64_image = encode_image(image_path)
            content_list.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}",
                    "detail": "high"
                }
            })
            print(f"[+] Multimodal Mode: Processing image for query: {user_query}")
        except Exception as e:
            print(f"[-] Encoding failed, falling back to text: {e}")
            # Fallback: rewrite prompt to use text since image failed
            content_list[0]["text"] = instruction.bom_user_context.format(
                chunk=json_doc, 
                user_query=user_query
            )

    # 5. Execute Inference
    try:
        response = client.chat.completions.create(
            model="Qwen/Qwen3-VL-8B-Instruct",
            messages=[
                {"role": "system", "content": instruction.bom_system_instruction},
                {"role": "user", "content": content_list}
            ],
            temperature=0.7,
            timeout=300
        )
        content = response.choices[0].message.content
    except Exception as e:
        print(f"--- [!] SERVER ERROR AT CHUNK ---")
        print(f"Error Details: {str(e)}")
        # Return a dummy result so the rest of the pages can still process
        return {
            "user_query": user_query,
            "status": "NotFound",
            "answer": f"Inference failed: {str(e)}"
        }
    
    if not content or content.strip() == "":
        print("Empty response from model")
        return []
    
    return await safe_json_loads(content)











# retrieved_docs = chunks["documents"][0]

# print(retrieved_docs)
# target_key = "Radiography examination (RT)"

# for i, doc_text in enumerate(retrieved_docs):
#     print(f"--- Processing Chunk {i+1} ---")
#     result = bom_agent_infer(json_doc=doc_text, user_query=target_key)
    # print("Result: ",result)



# async def connect_raginfer_boomllm(chunks, query):
#     retrieved_docs = chunks["documents"][0]
#     metas = chunks["metadatas"][0]

#     exact = []
#     partial = []
#     approximate = []
#     notfound = []


#     for i, doc_text in enumerate(retrieved_docs):
#         page_number = metas[i].get("page", None)
#         print(f"--- Processing Chunk {i+1} | page {page_number} ---")
#         doc_text = f" CHUNK: {i+1} | {doc_text}"
        

#         result = await bom_agent_infer(json_doc=doc_text, user_query=query)
#         print("result = ",result)
#         result["page_number"] = [page_number]
#         status = result.get("status", "NotFound")

#         if status == "Exact":
#             exact.append(result)
#         elif status == "Partial":
#             partial.append(result)
#         elif status == "Approximate":
#             approximate.append(result)
#         else:
#             notfound.append(result)


#     if exact:
#         return exact
#     elif partial:
#         return partial
#     elif approximate:
#         return approximate
#     else:
#         return notfound

"""above is working fine .comment for pass image url to the vllm """





async def connect_raginfer_boomllm(chunks, query, collections):
    retrieved_docs = chunks["documents"][0]
    metas = chunks["metadatas"][0]

    exact = []
    partial = []
    approximate = []
    notfound = []


    for i, doc_text in enumerate(retrieved_docs):
        page_number = metas[i].get("page", None)
        doc_text = f" CHUNK: {i+1} | {doc_text}"
        image_path = f"extracted_images/{collections}/page_{page_number}.png"
        print(f"--- Processing Chunk {i+1} | Page {page_number} | Image: {image_path} ---")

        result = await bom_agent_infer(json_doc=doc_text, user_query=query, image_path=image_path)
        # print("result = ",result)
        result["page_number"] = [page_number]
        status = result.get("status", "NotFound")

        await asyncio.sleep(2)
        if status == "Exact":
            exact.append(result)
        elif status == "Partial":
            partial.append(result)
        elif status == "Approximate":
            approximate.append(result)
        else:
            notfound.append(result)


    if exact:
        return exact
    elif partial:
        return partial
    elif approximate:
        return approximate
    else:
        return notfound

