# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.vectorstore.pinecone_store import delete_all_vectors

app = FastAPI(title="Universal AI Assistant")

# 🌍 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 CLEAR VECTOR DB ON EVERY RESTART
@app.on_event("startup")
def clear_vector_db():
    delete_all_vectors()
    print("✅ Pinecone vector DB cleared on startup")

# 🧠 Routes
app.include_router(router)

@app.get("/")
def health():
    return {"status": "Backend running"}
