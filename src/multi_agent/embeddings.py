# """below code is for BAAI embedding model"""
# import os
# import chromadb
# from sentence_transformers import SentenceTransformer
# import uuid

# base_dir = os.path.dirname(os.path.abspath(__file__))
# db_path = os.path.join(base_dir, "chroma_db")

# def chroma_client():
#     client = chromadb.PersistentClient(path=db_path)
#     return client
    
# class TenderRAG:
#     def __init__(self, collection_name):

#         # # FIX: se a fixed path relative to the script, not the terminal's CD
#         # base_dir = os.path.dirname(os.path.abspath(__file__))
#         # db_path = os.path.join(base_dir, "chroma_db")
   
#         # self.client = chromadb.PersistentClient(path=db_path)
#         """comment becuase written function sepreatly"""

#         self.client = chroma_client()

#         self.model = SentenceTransformer('BAAI/bge-m3')
#         self.collection_name_ref = collection_name # purpose to print in console once collection is added successfully

#         collections = self.client.list_collections()

#         print("\n--- AVAILABLE COLLECTIONS ---")
#         if not collections:
#             print("[-]No collections found!")
#         # else:
#         #     for col in collections:
#         #         print(f"- {col.name}")

#         for col in self.client.list_collections():
#             c = self.client.get_collection(col.name)
#             print("[+] available connection: ",col.name, "==>", c.count())

#         self.collection = self.client.get_or_create_collection(
#             name=collection_name,
#             metadata={"hnsw:space": "cosine"}
#         )

#         # DIAGNOSTIC: Print count on startup

#         count = self.collection.count()
#         print(f"--- Connected to DB at: {db_path} ---")
#         print(f"--- Current collection have '{collection_name}': {count} successfully found!---")


#     """proper working gives 80% accuracy. below one"""
#     async def ingest_data(self, final_data):
#         # Track if we have already saved the document identity/metadat
#         metadata_ingested = False

#         for entry in final_data['extracted_data']:
#             doc_type = entry['metadata']['type']
#             page = entry['metadata']['page']
#             source = entry['metadata'].get('source', "Unknown")

#             if doc_type == "table":
#                 content = entry['content']
            
#                 # If content is a list of strings (triplets)
#                 if isinstance(content, list):
#                     technical_triplets = []
#                     header_triplets = []

#                     for item in content:
#                         # Dynamically check if the triplet looks like metadata
#                         if any(word in item.lower() for word in ["metadata", "header", "revision", "document id","DOCUMENT_HEADER_INFO","document_header_info"]):
#                             header_triplets.append(item)
#                         else:
#                             technical_triplets.append(item)

                   

#                     # LOGIC: Only ingest header triplets on Page 1
#                     to_embed = []
#                     if page == 1:
#                         to_embed.extend(header_triplets)
#                     to_embed.extend(technical_triplets)

                
#                     if to_embed:
#                         text_to_embed = f"Context: {source} | Page {page} | " + " ".join(to_embed)
#                         print("-" * 50)
#                         print(f"[IF CONDITION]")
#                         print(f"DEBUG - PAGE: {page}")
#                         print(f"DEBUG - TYPE: {doc_type}")
#                         print(f"DEBUG - SOURCE: {source.split('\\')[-1]}") # Print only filename for clarity
#                         print(f"DEBUG - TEXT TO EMBED (First 200 chars): {text_to_embed[:900]}...")
#                         print("-" * 50)
#                         # input("..Enter to add to th
#                         # e db >>> ")
#                         await self._add_to_db(text_to_embed, doc_type, page, source)

#             else:
#                 # Paragraph handling remains standard
#                 text_to_embed = entry['content']
#                 if text_to_embed and len(text_to_embed.strip()) > 10:
#                     print(f"DEBUG - PAGE: {page} | TYPE: paragraph | TEXT: {text_to_embed[:900]}...")
#                     print(f"[else - CONDITION]")
#                     # input("...enter to add db....")
#                     await self._add_to_db(text_to_embed, doc_type, page, source)


#     async def xlsx_add_to_db(self, text, ids, metadatas):
#         embedding = self.model.encode(text, normalize_embeddings=True).tolist()
#         self.collection.add(
#             ids=[ids],
#             embeddings=[embedding],
#             documents=[text],
#             metadatas=[metadatas]
#         )
#         print("[+]Collection Created SUccssfully | Collection name",self.collection_name_ref)



#     async def _add_to_db(self, text, doc_type, page, source):
#         embedding = self.model.encode(text, normalize_embeddings=True).tolist()
#         self.collection.add(
#             ids=[str(uuid.uuid4())],
#             embeddings=[embedding],
#             documents=[text],
#             metadatas=[{"type": doc_type, "page": page, "source": source}]
#         )
#         print("[+]Collection Created SUccssfully | Collection name",self.collection_name_ref)



#     async def query(self, question, n_results=5):
#         # If the collection is empty, don't even try to query

#         print(f"\nCollection {self.collection.name} Connected.")
#         print("[DEBUG] COLLECTION COUNT:", self.collection.count())

#         if self.collection.count() == 0:
#             print("WARNING: Querying an empty collection!")
#             return None

#         query_embeddings = self.model.encode(question, normalize_embeddings=True).tolist()
#         results = self.collection.query(
#             query_embeddings=[query_embeddings],
#             n_results=n_results
#         )

#         return results

"""above code is working comment for implement re raker below for chatbot"""


# """below code is for BAAI embedding model"""
# import os
# import chromadb
# from sentence_transformers import SentenceTransformer, CrossEncoder
# import uuid

# base_dir = os.path.dirname(os.path.abspath(__file__))
# db_path = os.path.join(base_dir, "chroma_db")

# def chroma_client():
#     client = chromadb.PersistentClient(path=db_path)
#     return client
    
# class TenderRAG:
#     def __init__(self, collection_name):

#         # # FIX: se a fixed path relative to the script, not the terminal's CD
#         # base_dir = os.path.dirname(os.path.abspath(__file__))
#         # db_path = os.path.join(base_dir, "chroma_db")
   
#         # self.client = chromadb.PersistentClient(path=db_path)
#         """comment becuase written function sepreatly"""

#         self.client = chroma_client()

#         self.model = SentenceTransformer('BAAI/bge-m3')
#         self.reranker = CrossEncoder('BAAI/bge-reranker-base')

#         self.collection_name_ref = collection_name # purpose to print in console once collection is added successfully

#         collections = self.client.list_collections()

#         print("\n--- AVAILABLE COLLECTIONS ---")
#         if not collections:
#             print("[-]No collections found!")
#         # else:
#         #     for col in collections:
#         #         print(f"- {col.name}")


#         for col in self.client.list_collections():
#             c = self.client.get_collection(col.name)
#             print("[+] available connection: ",col.name, "==>", c.count())

#         self.collection = self.client.get_or_create_collection(
#             name=collection_name,
#             metadata={"hnsw:space": "cosine"}
#         )

#         # DIAGNOSTIC: Print count on startup

#         count = self.collection.count()
#         print(f"--- Connected to DB at: {db_path} ---")
#         print(f"--- Current collection have '{collection_name}': {count} successfully found!---")


#     """proper working gives 80% accuracy. below one"""
#     async def ingest_data(self, final_data):
#         # Track if we have already saved the document identity/metadat
#         metadata_ingested = False

#         for entry in final_data['extracted_data']:
#             doc_type = entry['metadata']['type']
#             page = entry['metadata']['page']
#             source = entry['metadata'].get('source', "Unknown")

#             if doc_type == "table":
#                 content = entry['content']
            
#                 # If content is a list of strings (triplets)
#                 if isinstance(content, list):
#                     technical_triplets = []
#                     header_triplets = []

#                     for item in content:
#                         # Dynamically check if the triplet looks like metadata
#                         if any(word in item.lower() for word in ["metadata", "header", "revision", "document id","DOCUMENT_HEADER_INFO","document_header_info"]):
#                             header_triplets.append(item)
#                         else:
#                             technical_triplets.append(item)

                   

#                     # LOGIC: Only ingest header triplets on Page 1
#                     to_embed = []
#                     if page == 1:
#                         to_embed.extend(header_triplets)
#                     to_embed.extend(technical_triplets)

                
#                     if to_embed:
#                         text_to_embed = f"Context: {source} | Page {page} | " + " ".join(to_embed)
#                         print("-" * 50)
#                         print(f"[IF CONDITION]")
#                         print(f"DEBUG - PAGE: {page}")
#                         print(f"DEBUG - TYPE: {doc_type}")
#                         print(f"DEBUG - SOURCE: {source.split('\\')[-1]}") # Print only filename for clarity
#                         print(f"DEBUG - TEXT TO EMBED (First 200 chars): {text_to_embed[:900]}...")
#                         print("-" * 50)
#                         # input("..Enter to add to th
#                         # e db >>> ")
#                         await self._add_to_db(text_to_embed, doc_type, page, source)

#             else:
#                 # Paragraph handling remains standard
#                 text_to_embed = entry['content']
#                 if text_to_embed and len(text_to_embed.strip()) > 10:
#                     print(f"DEBUG - PAGE: {page} | TYPE: paragraph | TEXT: {text_to_embed[:900]}...")
#                     print(f"[else - CONDITION]")
#                     # input("...enter to add db....")
#                     await self._add_to_db(text_to_embed, doc_type, page, source)


#     async def xlsx_add_to_db(self, text, ids, metadatas):
#         embedding = self.model.encode(text, normalize_embeddings=True).tolist()
#         self.collection.add(
#             ids=[ids],
#             embeddings=[embedding],
#             documents=[text],
#             metadatas=[metadatas]
#         )
#         print("[+]Collection Created SUccssfully | Collection name",self.collection_name_ref)



#     async def _add_to_db(self, text, doc_type, page, source):
#         embedding = self.model.encode(text, normalize_embeddings=True).tolist()
#         self.collection.add(
#             ids=[str(uuid.uuid4())],
#             embeddings=[embedding],
#             documents=[text],
#             metadatas=[{"type": doc_type, "page": page, "source": source}]
#         )
#         print("[+]Collection Created SUccssfully | Collection name",self.collection_name_ref)

#     async def query(self, question, n_results=35, top_k=5):
#             """
#             Enhanced query with Re-ranking logic.
#             1. Fetch n_results (e.g., 15) using vector search.
#             2. Re-rank those 15 to find the best top_k (e.g., 5).
#             """
#             print(f"\nCollection {self.collection.name} Connected.")
#             if self.collection.count() == 0:
#                 print("Querying an empty collection!")
#                 return None

#             # Step 1: Initial Retrieval (Broad search)
#             query_embeddings = self.model.encode(question, normalize_embeddings=True).tolist()
#             initial_results = self.collection.query(
#                 query_embeddings=[query_embeddings],
#                 n_results=n_results
#                 )#  where={"page":33}

#             documents = initial_results['documents'][0]
#             metadatas = initial_results['metadatas'][0]
#             import json
#             print("[++]intial reterived metadata: ",json.dumps(metadatas, indent=4))
#             if not documents:
#                 return initial_results

#             # Step 2: Re-ranking (Deep analysis)
#             # We pair the question with each retrieved document
#             pairs = [[question, doc] for doc in documents]
#             scores = self.reranker.predict(pairs)

#             # Step 3: Sort by Re-ranker scores
#             scored_results = sorted(
#                 zip(scores, documents, metadatas), 
#                 key=lambda x: x[0], 
#                 reverse=True
#             )

#             # Step 4: Return formatted results for the top_k
#             final_top_k = scored_results[:top_k]
#             # print("final top k",final_top_k)
#             return {
#                 "documents": [[item[1] for item in final_top_k]],
#                 "metadatas": [[item[2] for item in final_top_k]],
#                 "scores": [[float(item[0]) for item in final_top_k]]
#             }
"""above is perfectly working fine from re- ranker and where filter """



import os
import chromadb
import json
from sentence_transformers import SentenceTransformer, CrossEncoder
import uuid
from rank_bm25 import BM25Okapi
import numpy as np
import time 
import torch

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "chroma_db")

def chroma_client():
    client = chromadb.PersistentClient(path=db_path)
    return client
    
class TenderRAG:
    def __init__(self, collection_name):

        # # FIX: se a fixed path relative to the script, not the terminal's CD
        # base_dir = os.path.dirname(os.path.abspath(__file__))
        # db_path = os.path.join(base_dir, "chroma_db")
   
        # self.client = chromadb.PersistentClient(path=db_path)
        """comment becuase written function sepreatly"""

        self.client = chroma_client()

        self.model = SentenceTransformer('BAAI/bge-m3')
        self.reranker = CrossEncoder('BAAI/bge-reranker-base')

        self.collection_name_ref = collection_name # purpose to print in console once collection is added successfully

        collections = self.client.list_collections()

        print("\n--- AVAILABLE COLLECTIONS ---")
        if not collections:
            print("[-]No collections found!")
        # else:
        #     for col in collections:
        #         print(f"- {col.name}")


        for col in self.client.list_collections():
            c = self.client.get_collection(col.name)
            print("[+] available connection: ",col.name, "==>", c.count())

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # DIAGNOSTIC: Print count on startup

        count = self.collection.count()
        print(f"--- Connected to DB at: {db_path} ---")
        print(f"--- Current collection have '{collection_name}': {count} successfully found!---")


    """proper working gives 80% accuracy. below one"""
    async def ingest_data(self, final_data):
        # Track if we have already saved the document identity/metadat
        metadata_ingested = False

        for entry in final_data['extracted_data']:
            doc_type = entry['metadata']['type']
            page = entry['metadata']['page']
            source = entry['metadata'].get('source', "Unknown")

            if doc_type == "table":
                content = entry['content']
            
                # If content is a list of strings (triplets)
                if isinstance(content, list):
                    technical_triplets = []
                    header_triplets = []

                    for item in content:
                        # Dynamically check if the triplet looks like metadata
                        if any(word in item.lower() for word in ["metadata", "header", "revision", "document id","DOCUMENT_HEADER_INFO","document_header_info"]):
                            header_triplets.append(item)
                        else:
                            technical_triplets.append(item)

                   

                    # LOGIC: Only ingest header triplets on Page 1
                    to_embed = []
                    if page == 1:
                        to_embed.extend(header_triplets)
                    to_embed.extend(technical_triplets)

                
                    if to_embed:
                        text_to_embed = f"Context: {source} | Page {page} | " + " ".join(to_embed)
                        print("-" * 50)
                        print(f"[IF CONDITION]")
                        print(f"DEBUG - PAGE: {page}")
                        print(f"DEBUG - TYPE: {doc_type}")
                        print(f"DEBUG - SOURCE: {source.split('\\')[-1]}") # Print only filename for clarity
                        print(f"DEBUG - TEXT TO EMBED (First 200 chars): {text_to_embed[:900]}...")
                        print("-" * 50)
                        # input("..Enter to add to th
                        # e db >>> ")
                        await self._add_to_db(text_to_embed, doc_type, page, source)

            else:
                # Paragraph handling remains standard
                text_to_embed = entry['content']
                if text_to_embed and len(text_to_embed.strip()) > 10:
                    print(f"DEBUG - PAGE: {page} | TYPE: paragraph | TEXT: {text_to_embed[:900]}...")
                    print(f"[else - CONDITION]")
                    # input("...enter to add db....")
                    await self._add_to_db(text_to_embed, doc_type, page, source)


    async def xlsx_add_to_db(self, text, ids, metadatas):
        embedding = self.model.encode(text, normalize_embeddings=True).tolist()
        self.collection.add(
            ids=[ids],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadatas]
        )
        print("[+]Collection Created SUccssfully | Collection name",self.collection_name_ref)



    async def _add_to_db(self, text, doc_type, page, source):
        embedding = self.model.encode(text, normalize_embeddings=True).tolist()
        self.collection.add(
            ids=[str(uuid.uuid4())],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"type": doc_type, "page": page, "source": source}]
        )
        print("[+]Collection Created SUccssfully | Collection name",self.collection_name_ref)

    

    async def query(self, question, n_results=5):
        # If the collection is empty, don't even try to query

        print(f"\nCollection {self.collection.name} Connected.")
        print("[DEBUG] COLLECTION COUNT:", self.collection.count())

        if self.collection.count() == 0:
            print("WARNING: Querying an empty collection!")
            return None

        query_embeddings = self.model.encode(question, normalize_embeddings=True).tolist()
        results = self.collection.query(
            query_embeddings=[query_embeddings],
            n_results=n_results
        )

        return results
    # async def query(self, question, n_results=35, top_k=5):
    #     """
    #     Hybrid Search with Metadata tracking for BM25 and Re-ranker.
    #     """
    #     print(f"\nCollection {self.collection.name} Connected.")
        
    #     # 1. Vector Search (Semantic)
    #     query_embeddings = self.model.encode(question, normalize_embeddings=True).tolist()
    #     vector_results = self.collection.query(
    #         query_embeddings=[query_embeddings],
    #         n_results=n_results
    #     )
        
    #     v_docs = vector_results['documents'][0]
    #     v_metas = vector_results['metadatas'][0]

    #     print("[++] Initial Vector Retrieved Metadata: ", json.dumps(v_metas, indent=4))

    #     # 2. BM25 Search    
    #     # We tokenize the documents retrieved by the vector search to re-rank/filter them 
    #     tokenized_corpus = [doc.split(" ") for doc in v_docs] 
    #     bm25 = BM25Okapi(tokenized_corpus) 
        
    #     tokenized_query = question.split(" ")
        
    #     # We need the scores to associate them with the original indices
    #     bm25_scores = bm25.get_scores(tokenized_query)
        
    #     # Sort indices by BM25 score to see what BM25 liked most
    #     top_bm25_indices = np.argsort(bm25_scores)[::-1][:10]
    #     bm25_metadata_preview = [v_metas[i] for i in top_bm25_indices]
        
    #     print("[++] BM25 Top 10 Preferred Metadata: ", json.dumps(bm25_metadata_preview, indent=4))

    #     # 3. Combine & De-duplicate while preserving Metadata
    #     # We use a dictionary to de-duplicate based on document content
    #     combined_data = {}
    #     for doc, meta in zip(v_docs, v_metas):
    #         combined_data[doc] = meta
            
    #     # If BM25 was searching a larger corpus (self.all_texts), you'd add those here too.
    #     # Currently, it's re-ranking the vector results.
        
    #     docs_for_rerank = list(combined_data.keys())
    #     metas_for_rerank = list(combined_data.values())

    #     # 4. Re-ranking (Deep Analysis)
    #     pairs = [[question, doc] for doc in docs_for_rerank]
    #     rerank_scores = self.reranker.predict(pairs)

    #     # 5. Final Sort (Mapping scores back to docs and metas)
    #     scored_results = sorted(
    #         zip(rerank_scores, docs_for_rerank, metas_for_rerank), 
    #         key=lambda x: x[0], 
    #         reverse=True
    #     )
        
    #     final_top_k = scored_results[:top_k]
        
    #     # Print Final Re-ranker Metadata
    #     final_metadata = [item[2] for item in final_top_k]
    #     print("[++] Final Re-ranked Top K Metadata: ", json.dumps(final_metadata, indent=4))

    #     return {
    #         "documents": [item[1] for item in final_top_k],
    #         "metadatas": final_metadata,
    #         "scores": [float(item[0]) for item in final_top_k]
    #     }
  
  
    """ above is working fine for comeplx question. BM and reterival fine but re-ranker kill the valide pages """
    async def chat_query(self, question, n_results=100, top_k=5,where_filter=None):
            start = time.time()
            if torch.cuda.is_available():
                device = "cuda"

            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"

            else:
                device = "cpu"
                # Set CPU thread count for parallel processing if on CPU
                core_ = os.cpu_count() or 4

                torch.set_num_threads(core_) 
                print("[+] System CPU | CPU CORE: ",core_)


            # Ensure your models are moved to the detected device
            # (Usually done in __init__, but good to verify)
            if hasattr(self.reranker, 'model'):
                self.reranker.model.to(device)

            print(f"\n[+] Processing on: {device.upper()}")
            print(f"\n[+]chat query Collection {self.collection.name} Connected.\n [+]where Filter: {where_filter}")
            
            # # 1. Vector Search
            # query_embeddings = self.model.encode(question, normalize_embeddings=True).tolist()
            # vector_results = self.collection.query(
            #     query_embeddings=[query_embeddings],
            #     n_results=n_results,
            #     where={"type":"table"}
            # )

            # 1. Vector Search

            v_start = time.time()
            query_embeddings = self.model.encode(question, normalize_embeddings=True).tolist()
            
            if where_filter is not None:
                vector_results = self.collection.query(
                    query_embeddings=[query_embeddings],
                    n_results=n_results,
                    where={"type": where_filter}
                )
            else:
                vector_results = self.collection.query(
                query_embeddings=[query_embeddings],
                n_results=n_results)                  
           
           
            v_docs = vector_results['documents'][0]
            v_metas = vector_results['metadatas'][0]
            v_end = time.time()
            v_lat = v_end-v_start


            print("[++]initial vector retrievel: ",json.dumps(v_metas, indent=4))
            
            # 2. BM25 Search
            bm_start = time.time()
            tokenized_corpus = [doc.split(" ") for doc in v_docs] 
            bm25 = BM25Okapi(tokenized_corpus) 
            tokenized_query = question.split(" ")
            bm25_scores = bm25.get_scores(tokenized_query)

            # FIX: Convert ndarray to list for JSON printing
            # print("\n[++] b25 scores: ", json.dumps(bm25_scores.tolist(), indent=4))
            
            # 3. Normalize BM25 scores (0 to 1 range) to match Re-ranker scales
            # This prevents BM25 from "bullyng" the re-ranker scores

            """[#] Normalizer """
            max_bm25 = np.max(bm25_scores) if np.max(bm25_scores) > 0 else 1
            norm_bm25_scores = bm25_scores / max_bm25

            combined_data = []
            print(f"[+]bm25 Looping started reterived data collecting.....")
            for i, (doc, meta) in enumerate(zip(v_docs, v_metas)):
                combined_data.append({
                    "doc": doc,
                    "meta": meta,
                    "norm_bm25": norm_bm25_scores[i]
                })
            
            bm_end = time.time()
            bm_lat = bm_end - bm_start

            # Manually check why Page 32 is low-ranked
            # debug_results = self.collection.get(where={"page": 32})
            # print(f"Content of Page 32: {debug_results['documents']}")

            # # Check the score for Page 32 specifically
            # pairs = [[question, debug_results['documents'][0]]]
            # print(f"Re-ranker score for Page 32: {self.reranker.predict(pairs)}")

            """ # 4. Re-ranking """
            re_start = time.time()
            docs_for_rerank = [item["doc"] for item in combined_data]
            pairs = [[question, doc] for doc in docs_for_rerank]
            rerank_scores = self.reranker.predict(
                pairs,
                batch_size=32 if device == "cuda" else 4,
                show_progress_bar=False)
            re_end = time.time()
            re_lat = re_end - re_start
            
            
            # --- DEBUG PRINT: RE-RANKER RAW RANKINGS ---
            print(f"\n{'='*10} RE-RANKER RAW TOP RANKINGS {'='*10}")
            print(f"{'Page':<10} | {'Re-ranker Score':<15}")
            print("-" * 30)

           
            debug_rerank = []
            for i in range(len(combined_data)):
                debug_rerank.append({"page": combined_data[i]["meta"].get("page"), "score": rerank_scores[i]})

            debug_rerank = sorted(debug_rerank, key=lambda x: x["score"], reverse=True)
         
         
            for item in debug_rerank[:15]:
                print(f"[+]Re-ranke :{str(item['page']):<10} | {item['score']:.4f}")
            # -------------------------------------------


            # 5. Hybrid Final Score
            h_start = time.time()
            final_results = []
            for i in range(len(combined_data)):
                # Weighting: 70% Re-ranker, 30% BM25
                hybrid_score = (rerank_scores[i] * 0.7) + (combined_data[i]["norm_bm25"] * 0.3) 

                
                final_results.append({
                    "score": float(hybrid_score),
                    "doc": combined_data[i]["doc"],
                    "meta": combined_data[i]["meta"],
                    "norm_bm25": combined_data[i]["norm_bm25"]  # <--- ADD THIS LINE remobe after debug
                })

            final_results = sorted(final_results, key=lambda x: x["score"], reverse=True)
            final_top_k = final_results[:top_k]

            h_end = time.time()
            h_lat = h_end - h_start

            end=time.time()


            for item in final_results:
                print(f"[+][+]BM25: {str(item['meta'].get('page')):<10} | {'-':<12} | {item['norm_bm25']:.4f}") 

            final_metadata = [item["meta"] for item in final_top_k]
            print(f"[++] Final Hybrid Top {top_k} Metadata: ", json.dumps(final_metadata, indent=4))

    # --- LATENCY REPORT ---
            print(f"\n{'='*15} LATENCY REPORT {'='*15}")
            print(f"1. Vector Search (Top {n_results})  : {v_lat:.4f}s")
            print(f"2. BM25 Scoring (Top 25)    : {bm_lat:.4f}s")
            print(f"3. Re-ranking (Top 25)       : {re_lat:.4f}s")
            print(f"4. Hybrid Merge & Sort       : {h_lat:.4f}s")
            print(f"{'-'*46}")
            print(f"TOTAL RETRIEVAL TIME         : {end - start:.4f}s")
            print(f"{'='*46}\n")
            return {"chat_response":{
                "documents": [item["doc"] for item in final_top_k],
                "metadatas": final_metadata,
                "scores": [item["score"] for item in final_top_k]
            },
            "list_of_answers":[
                    {
                        "page": str(item["meta"].get("page")),
                        "content": str(item["doc"][:200] + "..."), # Snippet for UI performance
                        "score": str(item["score"]),
                        "type": str(item["meta"].get("type"))
                    } for item in final_results
                ]
            }


""" please re hit the api and monitor the output page finds donebut naswer qill not in api output"""