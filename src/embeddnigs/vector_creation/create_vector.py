




import re
import chromadb
import json
from fastapi import APIRouter
from .extract_service import PDF_Proccessing
from .chunking_ import chunk_pages
from .load_embeding_model import EmbeddingService
from backend_logs import get_logger
from src.configuration.env_key import EnvironKey
from typing import Optional, Dict
from src.multi_agent.dev_final_Extraction import generate_embeddings, xlsx_embedding_creation
from src.multi_agent.embeddings import chroma_client

embedding_pipeline = APIRouter()
vector_embedding = EmbeddingService()
config_ = EnvironKey.setting()
logger = get_logger("RAG Logs")
client = chroma_client()

def store_chunks(collection, chunks: list[dict], doc_id: str):
    """
    Stores chunks using the enriched text already prepared in RAG_Engine.
    """
    debuging = []

    for ch in chunks:
        # Build metadata
        metadata = {
            "doc_id": doc_id,
            "page": ch["page"],
            "content_type": ch.get("content_type", "Text"),
            "char_count": len(ch["text"])
        }
        
        if ch.get("section_title"):
            metadata["section_title"] = ch["section_title"][:200]
        
        # We store 'ch["text"]' which was already enriched in RAG_Engine
        collection.add(
            ids=[f"{doc_id}_{ch['chunk_id']}"],
            documents=[ch["text"]], 
            embeddings=[ch["embedding"]],
            metadatas=[metadata]
        )

        debuging.append({
            "ids": [f"{doc_id}_{ch['chunk_id']}"],
            "document": [ch["text"]],
            "metadatas": [metadata]
        })
    
    return debuging

async def sanitize_collection_name(name: str):
    name = name.rsplit(".", 1)[0]
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    name = re.sub(r"^[^a-zA-Z0-9]+", "", name)
    name = re.sub(r"[^a-zA-Z0-9]+$", "", name)
    return name

async def create_vector_embedding(input_pdf, document_id, doc_type: Optional[str] = None):
    """
    RAG ingestion pipeline with Early Enrichment for high-accuracy technical retrieval.
    """

    logger.info(f"Emebeding input document_id: {document_id}")
    collection_name = await sanitize_collection_name(document_id)

    logger.info(f"sanitaized collection name: {collection_name}")   
    # 1. Handle Collection (Reset if needed for new model/logic)
    existing_collections = [c.name for c in client.list_collections()]
    if collection_name in existing_collections:
        collection = client.get_collection(name=collection_name)
        if collection.count() > 0:
            print("Collection already Found so skipping create collection :", collection_name)
            logger.info(f"Collection '{collection_name}' exists. Skipping.")
            return {"doc_id": document_id, "collection_name": collection_name, "status": "already_exists"}
    
    # else:
    #     collection = client.create_collection(
    #         name=collection_name, 
    #         metadata=config_['vector_db']['metadata']
    #     )


    if doc_type == "xlsx":
        extracted_data = PDF_Proccessing.extract_excel_data(excel_file=input_pdf)
        documents = extracted_data["question_answer"]
        metadatas = extracted_data["metadata"]
        ids = extracted_data["ids"]

        await xlsx_embedding_creation(document_url=input_pdf,
                                      collections_name=collection_name,
                                      scraped_data=extracted_data,
                                      document=documents,
                                      id_info=ids,
                                      meta_info=metadatas
                                      )

        # await generate_embeddings()
        

        # #Generate embeddings
        # vectors = await vector_embedding.encoding(texts=documents)

        # #Store in DB
        # collection.add(
        #     ids=ids,
        #     documents=documents,
        #     embeddings=[v.tolist() if hasattr(v, 'tolist') else v for v in vectors],
        #     metadatas=metadatas
        # )
        await generate_embeddings(document_url=input_pdf, collections_name=collection_name)

        logger.info(f"Excel ingestion complete for {document_id}")

        return {
            "doc_id": document_id,
            "records": "inprogress",#len(documents),
            "collection_name": collection_name,
            "status": "excel_ingested"
        }

    
    
    else:    

        await generate_embeddings(document_url=input_pdf, collections_name=collection_name)

        # Pdf_page = await PDF_Proccessing._raw_pdf_(pdf_path=input_pdf)
        # chunk_data = await chunk_pages(pages=Pdf_page)

        # # 3. EARLY ENRICHMENT (Crucial for Technical Retrieval)
        # # We build the Context string BEFORE embedding so the vector 'knows' the section.
        # enriched_texts = []
        # for c in chunk_data:
        #     # Fallback: if no section title, use the first line of the chunk
        #     header = c.get("section_title") or c["text"].strip().split('\n')[0][:80]
        #     full_context_text = f"Context: {header} | Content: {c['text']}"
            
        #     # Update the chunk object so it's ready for storage
        #     c["text"] = full_context_text 
        #     enriched_texts.append(full_context_text)

        # # 4. Generate Embeddings for the ENRICHED text
        # vectors = await vector_embedding.encoding(texts=enriched_texts)
        
        # # Attach embeddings
        # for chunk, vec in zip(chunk_data, vectors):
        #     chunk['embedding'] = vec.tolist() if hasattr(vec, 'tolist') else vec

        # # 5. Store in Vector DB
        # store_chunks(collection, chunk_data, doc_id=document_id)
        
        logger.info(f"Ingestion complete for {document_id}")
        return {
            "doc_id": document_id,
            "chunks": "inprogress",#len(chunk_data),
            "collection_name": collection_name,
            "status":"collection_created"
        }