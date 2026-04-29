"""below code is for BAAI embedding model"""
import os
import chromadb
from sentence_transformers import SentenceTransformer
import uuid

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

