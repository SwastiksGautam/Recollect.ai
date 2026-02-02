import tiktoken
from PyPDF2 import PdfReader

from backend.vectorstore.pinecone_store import store_chunks, retrieve_chunks
from backend.llm.openai_client import chat_response, create_embedding
from backend.config.settings import CHAT_MODEL
import re
# 🔹 Max tokens for context to avoid exceeding model limits
MAX_TOKENS_CONTEXT = 1500  # Safe margin below model max

# 🔹 Count tokens for any text
def count_tokens(text: str) -> int:
    # This encoding is compatible with gpt-4o, gpt-4o-mini, and gpt-4
    enc = tiktoken.get_encoding("cl100k_base") 
    return len(enc.encode(text))



# 🔹 Token-based chunking
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

# 🔹 Store raw text content in Pinecone
def store_content(text: str, chunk_size: int = 500, overlap: int = 50):
    chunks = chunk_text_by_tokens(text, max_tokens=chunk_size, overlap=overlap)
    store_chunks(chunks)
    return f"{len(chunks)} chunks stored successfully."


def ingest_pdf(file_path: str, chunk_size: int = 500, overlap: int = 50):
    reader = PdfReader(file_path)
    full_text = ""
    
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            # CLEANING: Remove null bytes and excessive whitespace
            clean_text = page_text.replace('\x00', '').strip()
            # Check if we actually got text or just binary artifacts
            if len(clean_text) > 5: 
                full_text += clean_text + "\n"

    if not full_text.strip():
        return "Error: No readable text found in PDF. It might be an image-based PDF."

    chunks = chunk_text_by_tokens(full_text, max_tokens=chunk_size, overlap=overlap)
    store_chunks(chunks)
    return f"{len(chunks)} chunks from PDF stored successfully."

# 🔹 Token-safe smart QA
def answer_smart(query: str, top_k: int = 3):
    chunks = retrieve_chunks(query, top_k=top_k)

    context_chunks = []
    tokens_so_far = count_tokens(query)

    for chunk in chunks:
        chunk_tokens = count_tokens(chunk)

        # hard clamp
        if tokens_so_far + chunk_tokens > MAX_TOKENS_CONTEXT:
            break

        context_chunks.append(chunk)
        tokens_so_far += chunk_tokens

    context = "\n\n".join(context_chunks)

    return chat_response(context, query)


def extract_and_store_facts(user_input: str):
    facts = []

    # Name
    match = re.search(r"(i am|i'm|my name is)\s+([A-Za-z]+)", user_input, re.I)
    if match:
        facts.append(f"User name is {match.group(2)}")

    # Age
    match = re.search(r"(\d{1,3})\s*(years|year|yrs)", user_input, re.I)
    if match:
        facts.append(f"User age is {match.group(1)}")

    # City
    if "rampur" in user_input.lower():
        facts.append("User city is Rampur Bushahr")

    # State
    if "hp" in user_input.lower() or "himachal" in user_input.lower():
        facts.append("User state is Himachal Pradesh")

    if facts:
        # Retrieve existing facts to prevent duplicates
        existing_facts = retrieve_chunks("user facts", top_k=50)
        new_facts = [f for f in facts if f"[USER FACT]\n{f}" not in existing_facts]
        if new_facts:
            store_chunks([f"[USER FACT]\n{fact}" for fact in new_facts], namespace="user_facts")
