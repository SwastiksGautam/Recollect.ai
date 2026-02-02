from fastapi import APIRouter
from pydantic import BaseModel
from backend.main import (
    process_website,
    answer_from_text,
    answer_from_knowledge_base
)

router = APIRouter()


class ChatRequest(BaseModel):
    input: str
    query: str | None = None


@router.post("/chat")
def chat_handler(request: ChatRequest):
    user_input = request.input.strip()

    # 1️⃣ WEBSITE URL
    if user_input.startswith(("http://", "https://")):
        process_website(user_input)
        return {"answer": "Website processed. Ask your question now."}

    # 2️⃣ DIRECT TEXT QA (ChatGPT-like)
    if request.query:
        return {
            "answer": answer_from_text(user_input, request.query)
        }

    # 3️⃣ RAG QA (after website/pdf ingestion)
    return {
        "answer": answer_from_knowledge_base(user_input)
    }

