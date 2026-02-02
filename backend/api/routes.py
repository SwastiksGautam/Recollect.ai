# backend/api/routes.py
from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from backend.core.ingest import ingest_pdf, answer_smart

router = APIRouter()

class ChatRequest(BaseModel):
    input: str
    current_file: str | None = None
    session_id: str

class ClearRequest(BaseModel):
    session_id: str

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), initial_query: str = Form(None), session_id: str = Form(...)):
    import tempfile, os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    result = ingest_pdf(tmp_path, filename=file.filename, session_id=session_id)
    os.remove(tmp_path)
    return {"answer": f"✅ PDF processed successfully for session {session_id}"}

@router.post("/chat")
def chat_handler(request: ChatRequest):
    user_input = request.input.strip()
    
    from backend.vectorstore.pinecone_store import store_chunks
    store_chunks(
        [f"User previously asked: {user_input}"], 
        namespace=f"user_{request.session_id}"
    )
    
    from backend.core.ingest import extract_and_store_facts
    extract_and_store_facts(user_input, session_id=request.session_id)
    
    answer = answer_smart(
        user_input, 
        current_file=request.current_file, 
        session_id=request.session_id
    )
    return {"answer": answer}

@router.post("/clear-memory")
def clear_memory(request: ClearRequest): 
    from backend.vectorstore.pinecone_store import delete_all_vectors
    delete_all_vectors() 
    return {"answer": f"Memory cleared for session {request.session_id}!"}