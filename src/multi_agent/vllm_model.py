""" below is for bas64"""
import os
import requests
import base64
import json
from io import BytesIO
from src.multi_agent.url_config import gpu_server_url


# server inference
url = f"http://{gpu_server_url}/v1/chat/completions"
headers = {"Content-Type": "application/json"}
os.makedirs("outputs", exist_ok=True)

"""comment above prompt for document metadata key is not enforced."""

prompts = """
Extract all table data from this image into JSON format. preserve exact structure: main section as top-level keys, subsection as nested objects,
and row labels as keys with their corresponding values. Group related columns, nested objects.
1. Create a top-level key named "DOCUMENT_HEADER_INFO" for document titles, IDs, revisions, dates, and page numbers.
2. Create a top-level key named "TECHNICAL_TABLE_DATA" for the actual activity rows, requirements, and inspection levels.
3. For the TECHNICAL_TABLE_DATA:
   - Use row labels as keys.
   - Expand inspection codes; example:  "H" to "Hold (H)", "W" to "Witness (W)", "P" to "Perform (P)", "R" to "Review (R)".
4.*should extract only the table data.ignore paragrapg,text. extract only the table content.
5. Return only the JSON format. No explanation
"""

"""above prompt is enforced the metadata key"""
import os
import requests
import base64
import json
import time
from io import BytesIO
from PIL import Image
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import requests
import base64
import json
import time
from io import BytesIO

async def convert_pageimage_to_base64(page_image):
    """
    Converts PageImage to optimized JPEG to reduce payload size.
    """
    buffer = BytesIO()
    rgb_image = page_image.original.convert("RGB") 
    rgb_image.save(buffer, format="JPEG", quality=85, optimize=True)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

async def call_vllm_model_infer(images: list, batch_num, collection_name, batch_meta):    
    # Standard headers with Authorization
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EMPTY" 
    }
    
    vllm_extracted_data = []
    output_dir = "vllm_output"
    os.makedirs(output_dir, exist_ok=True)
    
    #to save the image binary for chatbot vllm model.
    encoded_dir = "encoded_images"
    os.makedirs(encoded_dir, exist_ok=True)

    print(f"vLLM: Processing batch {batch_num} ({len(images)} images)")
    print("[+]Batch meta: ",batch_meta)
    for page_image, actual_page_num in zip(images, batch_meta):
        start_page = time.time()
        try:
            image_base64 = await convert_pageimage_to_base64(page_image)

            # --- Saving the Base64 string to file ---
            file_name = f"{collection_name}_page_{actual_page_num}.txt"
            save_path = os.path.join(encoded_dir, file_name)
            
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(image_base64)

            data = {
                "model": "Qwen/Qwen3-VL-8B-Instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompts},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                            }
                        ]
                    }
                ],
                "temperature": 0.01,
                "max_tokens": 18906 
            }

            # Standard request without session persistence or custom timeout
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status() 
            
            result = response.json()
            extracted_text = result["choices"][0]["message"]["content"]
            vllm_extracted_data.append(extracted_text)
            
            print(f"  - Page {actual_page_num} success ({time.time()-start_page:.2f}s)")

        except Exception as e:
            print(f"  - Error on Page {actual_page_num}: {str(e)}")
            vllm_extracted_data.append(f"ERROR: {e}")

    # Save results to JSON
    output_file = os.path.join(output_dir, f"vllm_{batch_num}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"batch_id": batch_num, "data": vllm_extracted_data}, f, indent=4)

    
    return vllm_extracted_data







# import asyncio
# asyncio.run(call_vllm_model_infer(images=r"C:\Users\Arvind\Downloads\ilovepdf_pages-to-jpg\BHEL Spec.-32-39_page-0006.jpg", batch_num=35))