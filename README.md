# 🧠 Recollect AI — Persistent Memory RAG Assistant
🚀 **Live Demo:** https://recollect-ai-nine.vercel.app/
Recollect AI is a full-stack Retrieval-Augmented Generation (RAG) application designed to act as a personal AI assistant with persistent long-term memory.  
Unlike traditional chatbots that forget everything between sessions, Recollect AI extracts, stores, and retrieves user-specific facts across conversations using a vector database.

---

## 🚀 Key Features

### 🧩 Persistent Long-Term Memory
- Extracts personal facts such as name, age, hobbies, preferences, and education from conversations
- Stores extracted facts in a dedicated Pinecone namespace for long-term retrieval
- Enables the assistant to answer questions like “What is my name?” or “Which game do I love?” across sessions

### 📄 Context-Aware PDF Chat
- Upload and chat with multiple PDFs independently
- Uses metadata filtering ($eq) to ensure information from one document never leaks into another
- Ideal for resumes, research papers, or study material

### 🧠 Smart Chat Core
- Centralized chatbot logic handles:
  - General chat
  - PDF-based queries
  - Website ingestion
  - Memory lookups
- Automatically decides when to retrieve memory vs when to answer directly

### 🌐 Dynamic Environment Detection
- Automatically detects whether the app is running on:
  - localhost
  - Render / Vercel (production)
- Routes API calls accordingly without manual changes

### 🔢 Token-Optimized Processing
- Uses tiktoken for accurate token counting
- Splits long documents into optimal chunks with overlap
- Prevents context window overflow while maintaining answer quality

---

## 🛠️ Tech Stack

Frontend
- HTML5
- CSS3
- Vanilla JavaScript

Backend
- Python 3.8+
- FastAPI

LLM
- OpenAI GPT-4o-mini (Chat Completions & Embeddings)

Vector Database
- Pinecone (Serverless)

---

## ⚙️ Setup & Installation

### 1️⃣ Prerequisites
- Python 3.8 or higher
- OpenAI API Key
- Pinecone API Key & Index

### 2️⃣ Environment Variables
Create a `.env` file inside the `backend/` directory:

OPENAI_API_KEY=your_openai_api_key  
PINECONE_API_KEY=your_pinecone_api_key  
INDEX_NAME=recollect-ai  
PINECONE_REGION=us-west-2  

### 3️⃣ Install Dependencies
pip install -r requirements.txt


## 📂 Project Structure

```text
PREDUSK TECHNOLOGY
├── backend/
│   ├── api/                  # API endpoints and route definitions
│   │   └── routes.py         # Main router for chat and file handling
│   ├── config/               # System-level configuration
│   │   └── settings.py       # Environment variable management
│   ├── core/                 # Core RAG processing logic
│   │   └── ingest.py         # Document ingestion and fact extraction
│   ├── llm/                  # OpenAI client configuration
│   │   └── openai_client.py
│   ├── utils/                # Non-business logic helper functions
│   ├── vectorstore/          # Pinecone integration and metadata filters
│   │   └── pinecone_store.py
│   ├── .env                  # Local environment secrets
│   ├── app.py                # Primary application entry point
│   └── main.py               # Chatbot core (handles websites & general queries)
│
└── frontend/
    ├── index.html             # UI structure
    ├── script.js              # Client-side logic and API communication
    └── style.css              # Application styling
```

### 4️⃣ Run the Application

Backend:
python -m uvicorn backend.app:app --reload

Frontend:
Serve the `frontend/` directory using VS Code Live Server or any static file server

---

## 🤖 How It Works

### 🔁 Chat Flow
1. User sends a query
2. Query is converted into embeddings
3. Pinecone performs semantic search on:
   - Memory namespace
   - Document namespace
4. Relevant context is assembled
5. Final prompt is sent to the LLM
6. Response is returned to the user

### 🧠 Memory Extraction
- Uses rule-based logic to detect personal facts
- Stores extracted facts as vectors
- Can be upgraded to LLM-based extraction



## 📧 Contact
Swastik 
GitHub: https://github.com/SwastiksGautam
Linkdin: https://www.linkedin.com/in/swastiksharma1/
