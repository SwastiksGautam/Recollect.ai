
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.vectorstore.pinecone_store import delete_all_vectors

app = FastAPI(title="Universal AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://recollect-ai-nine.vercel.app", 
        "http://127.0.0.1:5500",               
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
# def clear_vector_db():
#     delete_all_vectors()
#     print(" Pinecone vector DB cleared on startup")

app.include_router(router)

@app.get("/")
def health():
    return {"status": "Backend running"}


