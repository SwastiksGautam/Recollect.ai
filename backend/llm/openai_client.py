from openai import OpenAI
from backend.config.settings import OPENAI_API_KEY, CHAT_MODEL, EMBEDDING_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

def create_embedding(text: str):
    """Generates an embedding vector for the given text."""
    # Ensure text is stripped and not empty
    text = text.replace("\n", " ").strip()
    if not text:
        return [0.0] * 1536 # Return zero vector for empty text
        
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


def chat_response(context: str, query: str):
    """Generates a smart, hybrid response."""
    
    # We always use the same system prompt to keep the AI's identity stable
    system_prompt = (
    "You are a helpful AI assistant with long-term memory.\n"
    "The DOCUMENT CONTEXT may contain:\n"
    "- User facts (name, city, preferences)\n"
    "- Past conversation memory\n"
    "- Documents like PDFs or websites\n\n"
    "IMPORTANT RULES:\n"
    "1. If the context contains USER FACTS, treat them as TRUE.\n"
    "2. If the user asks about themselves, prioritize USER FACTS over general knowledge.\n"
    "3. Do NOT say you don't know if the answer exists in the context.\n"
    "4. Only say 'I don't have that information' if the context truly lacks it."
)


    # We combine context and query into one flow
    # If context is empty, we just pass an empty string so the LLM knows there's no data
    user_prompt = f"""
MEMORY CONTEXT (User facts are always true):
{context if context.strip() else "No specific document context found for this query."}

USER QUESTION:
{query}

INSTRUCTIONS:
1. Check the DOCUMENT CONTEXT first. If it contains the answer, use it.
2. If the answer is NOT in the context, answer the question naturally using your general knowledge.
3. If the user mentions a specific file or name (like 'the resume' or 'Swastik') and the context is empty, inform them you couldn't find those specific details in the database but offer what you know generally.
"""

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7 # Increased to 0.7 to allow for more 'natural' and creative general answers
    )
    
    return response.choices[0].message.content.strip()