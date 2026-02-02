from backend.llm.openai_client import create_embedding
from pinecone.core.client.exceptions import NotFoundException
import uuid
import tiktoken
from backend.config.settings import (
    PINECONE_API_KEY,
    INDEX_NAME,
    PINECONE_DIMENSION,
    PINECONE_REGION,
    PINECONE_CLOUD,
)
from backend.utils.text_utils import chunk_text
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key=PINECONE_API_KEY)

def get_index():
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=PINECONE_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
        )
    return pc.Index(INDEX_NAME)



def store_chunks(chunks: list, namespace: str = "default", filename: str = "unknown"):
    index = get_index()
    for chunk in chunks:
        vec = create_embedding(chunk)
        index.upsert([{
            "id": str(uuid.uuid4()), 
            "values": vec,
            "metadata": {
                "text": chunk,
                "source": filename  
            }
        }], namespace=namespace)

def retrieve_chunks(query: str, top_k=5, current_file=None, session_id="default"): 
    index = get_index()
    embedding = create_embedding(query)

    # 🌟 ONLY search the namespace belonging to THIS session
    fact_results = index.query(
        vector=embedding,
        top_k=3,
        include_metadata=True,
        namespace=f"user_{session_id}" 
    )
    search_filter = {"source": {"$eq": current_file}} if current_file else None

    doc_results = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True,
        namespace="default",
        filter=search_filter  
    )

    facts = [m["metadata"]["text"] for m in fact_results["matches"]]
    docs = [m["metadata"]["text"] for m in doc_results["matches"]]

    return facts + docs


def delete_all_vectors():
    index = get_index()
    try:
        index.delete(delete_all=True)
        print("🔥 Pinecone index cleared")
    except NotFoundException:
        print(" Pinecone index empty — nothing to delete")

