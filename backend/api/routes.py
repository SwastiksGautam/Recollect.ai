from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from backend.core.ingest import ingest_pdf, answer_smart
import tempfile, os
import time

router = APIRouter()

class ChatRequest(BaseModel):
    input: str

@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...), 
    initial_query: str = Form(None) # <--- Added this
):
    """Upload a PDF, store it, and optionally answer a question immediately."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # 1. Process PDF
    result = ingest_pdf(tmp_path)
    os.remove(tmp_path)

    # 2. If a query was provided, answer it
    if initial_query:
        # Crucial: Wait 1-2 seconds for Pinecone to index the new vectors
        time.sleep(2) 
        answer = answer_smart(initial_query)
        return {"answer": answer, "info": result}

    return {"answer": f"✅ PDF processed successfully\n{result}"}

@router.post("/chat")
def chat_handler(request: ChatRequest):
    user_input = request.input.strip()
    # Your existing chat logic...
    answer = answer_smart(user_input)
    return {"answer": answer}


@router.post("/clear-memory")
def clear_memory():
    from backend.vectorstore.pinecone_store import delete_all_vectors
    delete_all_vectors()
    return {"answer": "Memory cleared! I'm ready for a fresh start."}
