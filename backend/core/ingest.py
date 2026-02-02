import tiktoken
from PyPDF2 import PdfReader
from backend.llm.openai_client import client
from backend.vectorstore.pinecone_store import store_chunks, retrieve_chunks
from backend.llm.openai_client import chat_response, create_embedding
from backend.config.settings import CHAT_MODEL
import re

MAX_TOKENS_CONTEXT = 1500  

def count_tokens(text: str) -> int:
    enc = tiktoken.get_encoding("cl100k_base") 
    return len(enc.encode(text))



# Token-based chunking
def chunk_text_by_tokens(text: str, max_tokens=250, overlap=30):
    enc = tiktoken.get_encoding("cl100k_base") 
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunks.append(enc.decode(chunk_tokens))
        start += max_tokens - overlap
    return chunks


def store_content(text: str, chunk_size: int = 500, overlap: int = 50, filename: str = "unknown"):
    chunks = chunk_text_by_tokens(text, max_tokens=chunk_size, overlap=overlap)
    store_chunks(chunks, filename=filename) 
    return f"{len(chunks)} chunks stored."

def ingest_pdf(file_path: str, chunk_size: int = 500, overlap: int = 50, filename: str = "unknown"):
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            clean_text = page_text.replace('\x00', '').strip()
            if len(clean_text) > 5: 
                full_text += clean_text + "\n"

    if not full_text.strip():
        return "Error: No readable text found."

    chunks = chunk_text_by_tokens(full_text, max_tokens=chunk_size, overlap=overlap)
    from backend.vectorstore.pinecone_store import store_chunks
    store_chunks(chunks, filename=filename) 
    return f"{len(chunks)} chunks stored."


def answer_smart(query: str, top_k: int = 3, current_file: str = None):
    from backend.vectorstore.pinecone_store import retrieve_chunks
    
    chunks = retrieve_chunks(query, top_k=top_k, current_file=current_file)

    context_chunks = []
    tokens_so_far = count_tokens(query)
    for chunk in chunks:
        chunk_tokens = count_tokens(chunk)
        if tokens_so_far + chunk_tokens > MAX_TOKENS_CONTEXT:
            break
        context_chunks.append(chunk)
        tokens_so_far += chunk_tokens

    context = "\n\n".join(context_chunks)
    return chat_response(context, query)


def extract_and_store_facts(user_input: str):
    extraction_prompt = f"""
    Extract every single detail from this message, including:
    - Personal facts (Name, age, location)
    - Interests/Actions (Games played, hobbies)
    - Intent/Queries (What the user is currently asking about or interested in)

    USER MESSAGE: "{user_input}"

    Format: - User [detail]
    If no info exists, return: NO_FACTS
    """
    ai_response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "system", "content": "You are a fact extraction tool."},
                  {"role": "user", "content": extraction_prompt}]
    ).choices[0].message.content.strip()

    if "NO_FACTS" in ai_response:
        return

    facts = [f.strip() for f in ai_response.split("\n") if f.strip().startswith("User")]

    if facts:
        existing_facts = retrieve_chunks("user facts", top_k=20)
        
        new_facts = []
        for f in facts:
            fact_tagged = f"[USER FACT]\n{f}"
            if fact_tagged not in existing_facts:
                new_facts.append(fact_tagged)

        if new_facts:
            store_chunks(new_facts, namespace="user_facts")
            print(f" AI extracted and stored {len(new_facts)} new facts.")