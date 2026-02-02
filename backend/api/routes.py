from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from backend.core.ingest import ingest_pdf, answer_smart
import tempfile, os
import time

router = APIRouter()

class ChatRequest(BaseModel):
    input: str
    current_file: str | None = None
    session_id: str

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), initial_query: str = Form(None)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    result = ingest_pdf(tmp_path, filename=file.filename)
    os.remove(tmp_path)

    if initial_query:
        time.sleep(2) 
        answer = answer_smart(initial_query, current_file=file.filename)
        return {"answer": answer, "info": result}

    return {"answer": f"✅ PDF processed successfully\n{result}"}

@router.post("/chat")
def chat_handler(request: ChatRequest):
    user_input = request.input.strip()
    
    # Pass sessionId to extraction and answering logic
    from backend.core.ingest import extract_and_store_facts, answer_smart
    extract_and_store_facts(user_input, session_id=request.session_id)
    
    answer = answer_smart(user_input, 
                          current_file=request.current_file, 
                          session_id=request.session_id)
    return {"answer": answer}

@router.post("/clear-memory")
def clear_memory():
    from backend.vectorstore.pinecone_store import delete_all_vectors
    delete_all_vectors()
    return {"answer": "Memory cleared!"}