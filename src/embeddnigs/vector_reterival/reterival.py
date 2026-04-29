import re
import json
import chromadb
import asyncio
from typing import List, Dict, Optional
from fastapi import HTTPException
from .load_embeding_model import EmbeddingService
from src.configuration.env_key import EnvironKey
from src.multi_agent.embeddings import chroma_client

config_ = EnvironKey.setting()
vector_embedding = EmbeddingService()
client = chroma_client()

import chromadb
from typing import List, Dict, Any, Optional
from src.embeddnigs.vector_creation.load_embeding_model import EmbeddingService
from backend_logs import get_logger
from src.embeddnigs.vector_creation.create_vector import sanitize_collection_name
from src.configuration.env_key import EnvironKey

logger = get_logger("reterival Logs")
config_ = EnvironKey.setting()



class QueryEmbedder:
    """
    Step 1: Embed field descriptions for semantic search.
    """
    
    def __init__(self):
        self.embed_service = EmbeddingService()
        self.client = chromadb.PersistentClient(path='./chroma_db')
    
    async def embed_query(self, field_description: str) -> List[float]:
        """
        Embed a field description into vector.
        """
        vectors = await self.embed_service.encoding(texts=[field_description])
        query_vector = vectors[0]#vectors.tolist()[0]
        return query_vector
    
    async def search_by_description(
        self,
        field_description: str,
        collection_name: str,
        doc_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Full flow: Embed description + search in ChromaDB.
        """
        # Step 1: Embed the field description
        query_vector = await self.embed_query(field_description)
        
        # Step 2: Get collection
        collection = self.client.get_collection(name=collection_name)
        
        # Step 3: Build filter if needed
        where_filter = {}
        if doc_id:
            where_filter["doc_id"] = doc_id
        
        # Step 4: Semantic search
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,  # ✅ MODIFIED (use dynamic top_k)
            where=where_filter if where_filter else None,  # ✅ MODIFIED
            include=['documents', 'metadatas', 'distances']
        )

        # Step 5: Format results
        context_chunks = []

        documents = results.get("documents", [[]])[0]  # ✅ MODIFIED (safe access)
        metadatas = results.get("metadatas", [[]])[0]  # ✅ MODIFIED
        distances = results.get("distances", [[]])[0]  # ✅ MODIFIED

        # 👉 Pick best match (lowest distance)
        if documents and distances:  # ✅ MODIFIED (safe check)
            best_index = distances.index(min(distances))  # ✅ MODIFIED

            metadata = metadatas[best_index] if metadatas else {}  # ✅ MODIFIED
            distance = distances[best_index]

            # Get exact page number
            page = metadata.get("page")
            if page is None:
                pages = metadata.get("pages", [1])
                page = pages[0] if isinstance(pages, list) else pages
            
            context_chunks.append({
                "text": documents[best_index],
                "page": page,
                "content_type": metadata.get("content_type", "Text"),
                "distance": distance,
                "doc_id": metadata.get("doc_id")
            })

        return context_chunks

    """comment above code becuase chunk return only 4 line of reterived data . so below code filter and return only one chunk, which one is get high accuracy"""
    # async def search_by_description(
    #     self,
    #     field_description: str,
    #     collection_name: str,
    #     doc_id: Optional[str] = None,
    #     top_k: int = 5
    # ) -> List[Dict[str, Any]]:
    #     """
    #     Full flow: Embed description + search in ChromaDB.
    #     """
    #     # Step 1: Embed the field description
    #     query_vector = await self.embed_query(field_description)
        

    #     # print("Collection name: resrival: ",collection_name)
    #     # Step 2: Get collection
    #     collection = self.client.get_collection(name=collection_name)
        
    #     # Step 3: Build filter if needed
    #     where_filter = {}
    #     if doc_id:
    #         where_filter["doc_id"] = doc_id
        
    #     # Step 4: Semantic search
    #     results = collection.query(
    #         query_embeddings=[query_vector],
    #         n_results=config_['vector_db']['top_k'],
    #         include=['documents', 'metadatas', 'distances']
    #     )
        
    #     # Step 5: Format results
    #     context_chunks = []
    #     for i in range(len(results["documents"][0])):
    #         metadata = results["metadatas"][0][i]
            
    #         # Get exact page number
    #         page = metadata.get("page")
    #         if page is None:
    #             pages = metadata.get("pages", [1])
    #             page = pages[0] if isinstance(pages, list) else pages
            
    #         context_chunks.append({
    #             "text": results["documents"][0][i],
    #             "page": page,
    #             "content_type": metadata.get("content_type", "Text"),
    #             "distance": results["distances"][0][i],
    #             "doc_id": metadata.get("doc_id")
    #         })
        
    #     return context_chunks


def chunk_list(data: List[str], batch_size: int):
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]


from src.s3.downloader import s3_file_name,s3_downloader
from pathlib import Path
from src.multi_agent.embeddings import TenderRAG


async def vector_retrieval_function(user_query: List[str], reterive_collection_name: str,   top_k_value: Optional[int] = None) -> Dict:
    """
    user_query: List of questions
    return: {question: [chunks]}
    """

    # print("user_query: ",user_query)
    # print("leng: ",len(user_query))
    collection = await sanitize_collection_name(name=reterive_collection_name)
    rag_engine = TenderRAG(collection_name=collection)

    print("COLLECTION_NAME:",collection)
    reterive_result = []
    for query in user_query:
        result = await rag_engine.query(question=query)
        reterive_result.append(result)
    
    return reterive_result
    # embedder = QueryEmbedder()

    # all_results = {}

    # # Configurable batch size
    # batch_size = config_['vector_reterival']['batch_size']
    # top_k = max(1, top_k_value if top_k_value else config_['vector_reterival']['batch_size'])


    # logger.info(f"Total Queries: {len(user_query)} | Batch Size: {batch_size}")
    # for batch in chunk_list(user_query, batch_size):
    #     logger.info(f"Processing batch of size {len(batch)}")

    #     # Async function per query
    #     async def process_query(query):
    #         if not query or not isinstance(query, str):
    #             return None

    #         query = query.strip()

    #         try:
    #             chunks = await embedder.search_by_description(
    #                 field_description=query,
    #                 collection_name=collection,
    #                 top_k=top_k
    #             )
    #             return query, chunks

    #         except Exception as e:
    #             logger.error(f"Error processing query '{query}': {str(e)}",exc_info=True)
    #             raise HTTPException(
    #                 status_code=500,
    #                 detail=f"Failed to process query: {str(query)} | ERROR: {str(e)}"
    #             )

    #     tasks = [process_query(q) for q in batch]
    #     results = await asyncio.gather(*tasks)

    #     # Store results
    #     for res in results:
    #         if res:
    #             query, chunks = res
    #             all_results[query] = chunks

    # logger.info(f"Vector reterival completed!")
    # return all_results
