from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"  # Points to backend/.env
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

INDEX_NAME = "website-chatbot"
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"

PINECONE_DIMENSION = 1536
PINECONE_REGION = "us-east-1"
PINECONE_CLOUD = "aws"
