# import pdfplumber
# import re
# import pdfplumber
# from collections import Counter
# from src.multi_agent.vllm_model import call_vllm_model_infer
# from src.multi_agent.llm_model import call_llm_model_infer
# from src.multi_agent.embeddings import TenderRAG


# class PDFSmartProcessor:
#     def __init__(self):
#         self.noise_blacklist = set()

#     async def identify_repetitive_noise(self, file_path, sample_pages=4):
#         """
#         Dynamically learns headers, footers, and document IDs that repeat 
#         across pages so we don't have to hardcode them.
#         """
#         line_counts = Counter()
#         processed_pages = 0
        
#         with pdfplumber.open(file_path) as pdf:
#             pages_to_scan = pdf.pages[:sample_pages]
#             processed_pages = len(pages_to_scan)
            
#             for page in pages_to_scan:
#                 text = page.extract_text()
#                 if text:
#                     # Get unique lines from each page to check for repetition
#                     unique_lines = set(line.strip() for line in text.split('\n') if len(line.strip()) > 1)
#                     for line in unique_lines:
#                         line_counts[line] += 1
                        
#         # If a line appears in >80% of pages, it is flagged as noise (Header/Footer/Confidentiality tag)
#         self.noise_blacklist = {line for line, count in line_counts.items() if count >= (processed_pages * 0.8)}
#         print(f"--- [LEARNING] Identified {len(self.noise_blacklist)} repeating noise patterns ---")


#     async def clean_text(self, text):
#         """
#         Removes dynamic noise, TOC dot-trails, and preserves technical symbols.
#         """
#         if not text:
#             return ""

#         # 1. Technical Symbol Preservation & English Filter
#         # Keeps A-Z, 0-9, and symbols like degree (°), plus-minus (±), >=, <=
#         text = re.sub(r'[^\x00-\x7f\u00b0\u00b1\u2265\u2264]', r'', text)

#         lines = text.split('\n')
#         cleaned_lines = []
        
#         for line in lines:
#             stripped = line.strip()
            
#             # Skip if line is in the learned noise blacklist
#             if stripped in self.noise_blacklist:
#                 continue
            
#             # Skip standalone page numbers (matches "1", "Page 1", "1 of 20")
#             if re.match(r'^(Page\s+)?\d+(\s+of\s+\d+)?$', stripped, re.IGNORECASE):
#                 continue

#             # Remove Table of Contents dot trails (e.g., "7.2 Painting ... 34")
#             line = re.sub(r'\.{3,}\s*\d*', "", line)

#             # Fix multiple spaces
#             line = re.sub(r'\s+', ' ', line).strip()

#             if len(line) > 2: # Ignore tiny fragments
#                 cleaned_lines.append(line)

#         return "\n".join(cleaned_lines)


#     async def extract_table_json(self, images_to_process, batch_num):
#         """
#         Calls VLLM for a batch of images.
#         """
#         # Get the list of raw JSON strings from vLLM
#         vllm_responses = await call_vllm_model_infer(images_to_process, batch_num)
        
#         cleaned_responses = []
#         for raw_json in vllm_responses:
#             # Clean each JSON string individually using your LLM
#             cleaned = await call_llm_model_infer(raw_json)
#             cleaned_responses.append(cleaned)

#         return {"table_data": cleaned_responses, "status": "success"}


#     """ added batch proccessing with time stamp"""
#     import time
#     import pdfplumber

#     async def run_pipeline(self, file_path, batch_size=4):
#         """
#         input:
#             file_path = S3
#         """
        
#         await self.identify_repetitive_noise(file_path)
#         all_pages_data = []
        
#         # Metrics tracking initialization
#         metrics = {"text_extraction": 0.0, "rendering": 0.0, "vllm_inference": 0.0}

#         with pdfplumber.open(file_path) as pdf:
#             total_pages = len(pdf.pages)
            
#             # 1. Process in Chunks
#             for i in range(0, total_pages, batch_size):
#                 batch_images = []
#                 batch_metas = []
#                 current_batch_pages = pdf.pages[i : i + batch_size]
                
#                 for page in current_batch_pages:
#                     page_num = page.page_number
#                     p_bbox = page.bbox
                    
#                     # --- TIME: TABLE DETECTION ---
#                     t_detect = time.time()
#                     tables = page.find_tables()
#                     metrics["text_extraction"] += (time.time() - t_detect)

#                     if tables:
#                         # --- TIME: RENDERING ---
#                         t_render = time.time()
#                         # Dropped to 150 resolution for speed as discussed
#                         img = page.to_image(resolution=300) 
#                         batch_images.append(img)
#                         batch_metas.append(page_num)
#                         metrics["rendering"] += (time.time() - t_render)

#                         # Prepare text layer (excluding tables)
#                         text_layer = page
#                         for table in tables:
#                             t_bbox = table.bbox
#                             safe_bbox = (max(p_bbox[0], t_bbox[0]), max(p_bbox[1], t_bbox[1]), 
#                                         min(p_bbox[2], t_bbox[2]), min(p_bbox[3], t_bbox[3]))
#                             text_layer = text_layer.outside_bbox(safe_bbox)
#                     else:
#                         text_layer = page

#                     # --- TIME: TEXT CLEANING ---
#                     t_text = time.time()
#                     raw_text = text_layer.extract_text(x_tolerance=1.5, y_tolerance=3)
#                     cleaned_text = await self.clean_text(raw_text)
#                     metrics["text_extraction"] += (time.time() - t_text)
                    
#                     if cleaned_text:
#                         all_pages_data.append({
#                             "content": cleaned_text,
#                             "metadata": {"type": "paragraph", "page": page_num, "source": file_path}
#                         })

#                 # 2. --- TIME: BATCH VLLM INFERENCE ---
#                 if batch_images:
#                     batch_index = (i // batch_size) + 1  # Calculate batch number (1, 2, 3...)
#                     print(f"--- [BATCH] Sending {len(batch_images)} images to VLLM ---")
#                     t_vllm = time.time()
                    
#                     # IMPORTANT: Ensure call_vllm_model_infer returns a LIST of results
#                     batch_responses = await self.extract_table_json(batch_images,batch_index) 
                    
#                     metrics["vllm_inference"] += (time.time() - t_vllm)
                    
#                     # Unpack batch results
#                     # Assuming extract_table_json returns a list or you handle the response object
#                     # If your current function returns a single dict, you'll need to adjust how you loop here
#                     for meta, response in zip(batch_metas, batch_responses.get("table_data", [])):
#                         all_pages_data.append({
#                             "content": response,
#                             "metadata": {"type": "table", "page": meta, "source": file_path}
#                         })

#         # --- FINAL PERFORMANCE REPORT ---
#         print(f"\nRAW METRICS: {metrics} \n")
#         print("="*40)
#         print(" BATCHED PERFORMANCE BREAKDOWN")
#         print("="*40)
#         for key, val in metrics.items():
#             avg_time = val / total_pages if total_pages > 0 else 0
#             print(f"{key.upper():<20}: {val:>8.2f}s (Avg {avg_time:>6.2f}s/page)")
#         print("="*40)
        
#         return all_pages_data



# """ Debugging.... """
# import json
# import os
# import time

# async def save_for_debugging(data, file_path, execution_time, total_pages, output_path="debug_output.json"):
#     """
#     Saves the complete scraped data along with job metadata to a JSON file.
#     Includes formatted execution time (e.g., 1m 34.8s).
#     """
    
#     # Calculate formatted time: 1m 34.8s
#     minutes, seconds = divmod(execution_time, 60)
#     formatted_time = f"{int(minutes)}m {seconds:.1f}s" if minutes > 0 else f"{seconds:.1f}s"

#     # Create a wrapper object to hold both metadata and the actual data
#     debug_payload = {
#         "job_summary": {
#             "document_name": os.path.basename(file_path),
#             "full_path": file_path,
#             "total_pages_processed": total_pages,
#             "execution_time_raw": round(execution_time, 2),
#             "execution_time_formatted": formatted_time,
#             "total_chunks_extracted": len(data),
#             "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
#         },
#         "extracted_data": data
#     }

#     try:
#         with open(output_path, 'w', encoding='utf-8') as f:
#             json.dump(debug_payload, f, indent=4, ensure_ascii=False)
        
#         print(f"\n" + "="*50)
#         print(f"DEBUGGING FILE CREATED: {os.path.abspath(output_path)}")
#         print(f"File Name: {debug_payload['job_summary']['document_name']}")
#         print(f"Time Taken: {formatted_time}")
#         print("="*50)
#     except Exception as e:
#         print(f"Error saving debug file: {e}")


# # --- implemen RAG ---
# async def xlsx_embedding_creation(document_url, collections_name, scraped_data, document, id_info, meta_info):
#     """
#     document_url = local pdf
#     collection_name = "BHEL"
#     """

#     file_path = document_url #S3
#     collection_name_ = collections_name #collection name is for embed, reterive, json -> save file name
#     start_time = time.time()

#     print("[+]generating embeddings for collection:",collections_name)
    
#     # 1. Extraction & Cleaning
#     # processor = PDFSmartProcessor()
#     # scraped_data = await processor.run_pipeline(file_path)

#     stop_time = time.time()
#     duration = stop_time - start_time

#     # # 2. SAVE FOR DEBUGGING (Optional but helpful)
#     # with pdfplumber.open(file_path) as pdf:
#     #     total_pages = len(pdf.pages)

#     await save_for_debugging(
#         data=scraped_data, 
#         file_path=file_path, 
#         execution_time=duration, 
#         total_pages="inprogres", 
#         output_path=f"{collection_name_}.json"
#     )

#     # 3. START THE RAG PROCESS
#     print("\n--- [RAG] Initializing Vector Database & Ingesting Data ---")
    
#     # Initialize your RAG Class (ensure the class definition is above this block)
#     rag_system = TenderRAG(collection_name=collection_name_)
    
#     # Ingest the data directly from the pipeline output
#     # Note: We pass a dict that matches your ingest_data logic
#     await rag_system._add_to_db(text=document, ids=id_info, metadatas=meta_info) 


# # --- implemen RAG ---
# async def generate_embeddings(document_url, collections_name):
#     """
#     document_url = local pdf
#     collection_name = "BHEL"
#     """

#     file_path = document_url #S3
#     collection_name_ = collections_name #collection name is for embed, reterive, json -> save file name
#     start_time = time.time()

#     print("[+]generating embeddings for collection:",collections_name)
    
#     # 1. Extraction & Cleaning
#     processor = PDFSmartProcessor()
#     scraped_data = await processor.run_pipeline(file_path)

#     stop_time = time.time()
#     duration = stop_time - start_time

#     # 2. SAVE FOR DEBUGGING (Optional but helpful)
#     with pdfplumber.open(file_path) as pdf:
#         total_pages = len(pdf.pages)

#     await save_for_debugging(
#         data=scraped_data, 
#         file_path=file_path, 
#         execution_time=duration, 
#         total_pages=total_pages, 
#         output_path=f"{collection_name_}.json"
#     )

#     # 3. START THE RAG PROCESS
#     print("\n--- [RAG] Initializing Vector Database & Ingesting Data ---")
    
#     # Initialize your RAG Class (ensure the class definition is above this block)
#     rag_system = TenderRAG(collection_name=collection_name_)
    
#     # Ingest the data directly from the pipeline output
#     # Note: We pass a dict that matches your ingest_data logic
#     await rag_system.ingest_data({"extracted_data": scraped_data}) 

#     print("--- [RAG] Ingestion Complete! Vector Creation completed. ---")

#     # # 4. TEST QUERY
#     # test_query = "What are the requirements for the Authorised Signatory?"
#     # results = rag_system.query(test_query)
    
#     # print(f"\nQUERY: {test_query}")
#     # print(f"TOP RELEVANT CHUNK: \n{results['documents'][0][0]}")

#     # 709c6588-fcd5-4095-8a27-2bb4637cdf8a , 3308cbbb-e85c-441b-a5a9-b69bdd12521d [att6,att7]

"""above is working fine comment for pass image link to the vllm """

import pdfplumber
import re
import pdfplumber
from pathlib import Path
from collections import Counter
from src.multi_agent.vllm_model import call_vllm_model_infer
from src.multi_agent.llm_model import call_llm_model_infer
from src.multi_agent.embeddings import TenderRAG


class PDFSmartProcessor:
    def __init__(self):
        self.noise_blacklist = set()

    async def identify_repetitive_noise(self, file_path, sample_pages=4):
        """
        Dynamically learns headers, footers, and document IDs that repeat 
        across pages so we don't have to hardcode them.
        """
        line_counts = Counter()
        processed_pages = 0
        
        with pdfplumber.open(file_path) as pdf:
            pages_to_scan = pdf.pages[:sample_pages]
            processed_pages = len(pages_to_scan)
            
            for page in pages_to_scan:
                text = page.extract_text()
                if text:
                    # Get unique lines from each page to check for repetition
                    unique_lines = set(line.strip() for line in text.split('\n') if len(line.strip()) > 1)
                    for line in unique_lines:
                        line_counts[line] += 1
                        
        # If a line appears in >80% of pages, it is flagged as noise (Header/Footer/Confidentiality tag)
        self.noise_blacklist = {line for line, count in line_counts.items() if count >= (processed_pages * 0.8)}
        print(f"--- [LEARNING] Identified {len(self.noise_blacklist)} repeating noise patterns ---")


    async def clean_text(self, text):
        """
        Removes dynamic noise, TOC dot-trails, and preserves technical symbols.
        """
        if not text:
            return ""

        # 1. Technical Symbol Preservation & English Filter
        # Keeps A-Z, 0-9, and symbols like degree (°), plus-minus (±), >=, <=
        text = re.sub(r'[^\x00-\x7f\u00b0\u00b1\u2265\u2264]', r'', text)

        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Skip if line is in the learned noise blacklist
            if stripped in self.noise_blacklist:
                continue
            
            # Skip standalone page numbers (matches "1", "Page 1", "1 of 20")
            if re.match(r'^(Page\s+)?\d+(\s+of\s+\d+)?$', stripped, re.IGNORECASE):
                continue

            # Remove Table of Contents dot trails (e.g., "7.2 Painting ... 34")
            line = re.sub(r'\.{3,}\s*\d*', "", line)

            # Fix multiple spaces
            line = re.sub(r'\s+', ' ', line).strip()

            if len(line) > 2: # Ignore tiny fragments
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)


    async def extract_table_json(self, images_to_process, batch_num):
        """
        Calls VLLM for a batch of images.
        """
        # Get the list of raw JSON strings from vLLM
        vllm_responses = await call_vllm_model_infer(images_to_process, batch_num)
        
        cleaned_responses = []
        for raw_json in vllm_responses:
            # Clean each JSON string individually using your LLM
            cleaned = await call_llm_model_infer(raw_json)
            cleaned_responses.append(cleaned)

        return {"table_data": cleaned_responses, "status": "success"}


    """ added batch proccessing with time stamp"""
    import time
    import pdfplumber

    async def run_pipeline(self, file_path, collection_name, batch_size=4):
        """
        input:
            file_path = S3
        """
        output_dir = Path(f"extracted_images/{collection_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        print("Output dir: ",output_dir)
        await self.identify_repetitive_noise(file_path)
        all_pages_data = []
        
        # Metrics tracking initialization
        metrics = {"text_extraction": 0.0, "rendering": 0.0, "vllm_inference": 0.0}

        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            
            # 1. Process in Chunks
            for i in range(0, total_pages, batch_size):
                batch_images = []
                batch_metas = []
                current_batch_pages = pdf.pages[i : i + batch_size]
                
                for page in current_batch_pages:
                    page_num = page.page_number
                    p_bbox = page.bbox
                    
                    # --- TIME: TABLE DETECTION ---
                    t_detect = time.time()
                    tables = page.find_tables()
                    metrics["text_extraction"] += (time.time() - t_detect)

                    if tables:
                        # --- TIME: RENDERING ---
                        t_render = time.time()
                        # Dropped to 150 resolution for speed as discussed
                        img = page.to_image(resolution=300) 

                        #image save
                        image_filename = f"page_{page_num}.png"
                        image_save_path = output_dir / image_filename
                        img.save(str(image_save_path), format="PNG")
                        print("Imgae saved path: ",image_save_path)
                        batch_images.append(img)
                        batch_metas.append(page_num)
                        metrics["rendering"] += (time.time() - t_render)

                        # Prepare text layer (excluding tables)
                        text_layer = page
                        for table in tables:
                            t_bbox = table.bbox
                            safe_bbox = (max(p_bbox[0], t_bbox[0]), max(p_bbox[1], t_bbox[1]), 
                                        min(p_bbox[2], t_bbox[2]), min(p_bbox[3], t_bbox[3]))
                            text_layer = text_layer.outside_bbox(safe_bbox)
                    else:
                        text_layer = page

                    # --- TIME: TEXT CLEANING ---
                    t_text = time.time()
                    raw_text = text_layer.extract_text(x_tolerance=1.5, y_tolerance=3)
                    cleaned_text = await self.clean_text(raw_text)
                    metrics["text_extraction"] += (time.time() - t_text)
                    
                    if cleaned_text:
                        all_pages_data.append({
                            "content": cleaned_text,
                            "metadata": {"type": "paragraph", "page": page_num, "source": file_path}
                        })

                # 2. --- TIME: BATCH VLLM INFERENCE ---
                if batch_images:
                    batch_index = (i // batch_size) + 1  # Calculate batch number (1, 2, 3...)
                    print(f"--- [BATCH] Sending {len(batch_images)} images to VLLM ---")
                    t_vllm = time.time()
                    
                    # IMPORTANT: Ensure call_vllm_model_infer returns a LIST of results
                    batch_responses = await self.extract_table_json(batch_images,batch_index) 
                    
                    metrics["vllm_inference"] += (time.time() - t_vllm)
                    
                    # Unpack batch results
                    # Assuming extract_table_json returns a list or you handle the response object
                    # If your current function returns a single dict, you'll need to adjust how you loop here
                    for meta, response in zip(batch_metas, batch_responses.get("table_data", [])):
                        all_pages_data.append({
                            "content": response,
                            "metadata": {"type": "table", "page": meta, "source": file_path}
                        })

        # --- FINAL PERFORMANCE REPORT ---
        print(f"\nRAW METRICS: {metrics} \n")
        print("="*40)
        print(" BATCHED PERFORMANCE BREAKDOWN")
        print("="*40)
        for key, val in metrics.items():
            avg_time = val / total_pages if total_pages > 0 else 0
            print(f"{key.upper():<20}: {val:>8.2f}s (Avg {avg_time:>6.2f}s/page)")
        print("="*40)
        
        return all_pages_data



""" Debugging.... """
import json
import os
import time

async def save_for_debugging(data, file_path, execution_time, total_pages, output_path="debug_output.json"):
    """
    Saves the complete scraped data along with job metadata to a JSON file.
    Includes formatted execution time (e.g., 1m 34.8s).
    """
    
    # Calculate formatted time: 1m 34.8s
    minutes, seconds = divmod(execution_time, 60)
    formatted_time = f"{int(minutes)}m {seconds:.1f}s" if minutes > 0 else f"{seconds:.1f}s"

    # Create a wrapper object to hold both metadata and the actual data
    debug_payload = {
        "job_summary": {
            "document_name": os.path.basename(file_path),
            "full_path": file_path,
            "total_pages_processed": total_pages,
            "execution_time_raw": round(execution_time, 2),
            "execution_time_formatted": formatted_time,
            "total_chunks_extracted": len(data),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "extracted_data": data
    }

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(debug_payload, f, indent=4, ensure_ascii=False)
        
        print(f"\n" + "="*50)
        print(f"DEBUGGING FILE CREATED: {os.path.abspath(output_path)}")
        print(f"File Name: {debug_payload['job_summary']['document_name']}")
        print(f"Time Taken: {formatted_time}")
        print("="*50)
    except Exception as e:
        print(f"Error saving debug file: {e}")


# --- implemen RAG ---
async def xlsx_embedding_creation(document_url, collections_name, scraped_data, document, id_info, meta_info):
    """
    document_url = local pdf
    collection_name = "BHEL"
    """

    file_path = document_url #S3
    collection_name_ = collections_name #collection name is for embed, reterive, json -> save file name
    start_time = time.time()

    print("[+]generating embeddings for collection:",collections_name)
    
    # 1. Extraction & Cleaning
    # processor = PDFSmartProcessor()
    # scraped_data = await processor.run_pipeline(file_path)

    stop_time = time.time()
    duration = stop_time - start_time

    # # 2. SAVE FOR DEBUGGING (Optional but helpful)
    # with pdfplumber.open(file_path) as pdf:
    #     total_pages = len(pdf.pages)

    await save_for_debugging(
        data=scraped_data, 
        file_path=file_path, 
        execution_time=duration, 
        total_pages="inprogres", 
        output_path=f"{collection_name_}.json"
    )

    # 3. START THE RAG PROCESS
    print("\n--- [RAG] Initializing Vector Database & Ingesting Data ---")
    
    # Initialize your RAG Class (ensure the class definition is above this block)
    rag_system = TenderRAG(collection_name=collection_name_)
    
    # Ingest the data directly from the pipeline output
    # Note: We pass a dict that matches your ingest_data logic
    await rag_system.xlsx_add_to_db(text=document, ids=id_info, metadatas=meta_info) 


# --- implemen RAG ---
async def generate_embeddings(document_url, collections_name):
    """
    document_url = local pdf
    collection_name = "BHEL"
    """

    file_path = document_url #S3
    collection_name_ = collections_name #collection name is for embed, reterive, json -> save file name
    start_time = time.time()

    print("[+]generating embeddings for collection:",collections_name)
    
    # 1. Extraction & Cleaning
    processor = PDFSmartProcessor()
    scraped_data = await processor.run_pipeline(file_path, collections_name)

    stop_time = time.time()
    duration = stop_time - start_time

    # 2. SAVE FOR DEBUGGING (Optional but helpful)
    with pdfplumber.open(file_path) as pdf:
        total_pages = len(pdf.pages)

    await save_for_debugging(
        data=scraped_data, 
        file_path=file_path, 
        execution_time=duration, 
        total_pages=total_pages, 
        output_path=f"{collection_name_}.json"
    )

    # 3. START THE RAG PROCESS
    print("\n--- [RAG] Initializing Vector Database & Ingesting Data ---")
    
    # Initialize your RAG Class (ensure the class definition is above this block)
    rag_system = TenderRAG(collection_name=collection_name_)
    
    # Ingest the data directly from the pipeline output
    # Note: We pass a dict that matches your ingest_data logic
    await rag_system.ingest_data({"extracted_data": scraped_data}) 

    print("--- [RAG] Ingestion Complete! Vector Creation completed. ---")

    # # 4. TEST QUERY
    # test_query = "What are the requirements for the Authorised Signatory?"
    # results = rag_system.query(test_query)
    
    # print(f"\nQUERY: {test_query}")
    # print(f"TOP RELEVANT CHUNK: \n{results['documents'][0][0]}")

    # 709c6588-fcd5-4095-8a27-2bb4637cdf8a , 3308cbbb-e85c-441b-a5a9-b69bdd12521d [att6,att7]