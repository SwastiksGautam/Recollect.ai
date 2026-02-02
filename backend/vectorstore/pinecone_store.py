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



def store_chunks(chunks: list, namespace: str = "default"):
    index = get_index()
    for chunk in chunks:
        vec = create_embedding(chunk)
        index.upsert([{
            "id": str(uuid.uuid4()), # Unique ID prevents overwriting
            "values": vec,
            "metadata": {"text": chunk}
        }], namespace=namespace)

def retrieve_chunks(query: str, top_k=5):
    index = get_index()
    embedding = create_embedding(query)

    # 1. Search in user_facts namespace
    fact_results = index.query(
        vector=embedding,
        top_k=3,
        include_metadata=True,
        namespace="user_facts" # <--- Look here!
    )

    # 2. Search in default namespace (PDFs/Websites)
    doc_results = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True,
        namespace="default" 
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
        # Happens when no namespace exists yet
        print("ℹ️ Pinecone index empty — nothing to delete")

