from sqlalchemy.orm import Session
from app.models.chatbot import Chatbot
from app.schemas.chatbot import ChatbotCreate
from app.core import config
from fastapi import HTTPException
import json
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import openai
import tiktoken
import os

class ChatbotService:
    @staticmethod
    def create_chatbot(chatbot_data: ChatbotCreate, db: Session) -> Chatbot:
        db_chatbot = Chatbot(**chatbot_data.dict())
        db.add(db_chatbot)
        db.commit()
        db.refresh(db_chatbot)
        return db_chatbot

    @staticmethod
    def list_chatbots(business_profile_id: str = None, user_id: str = None, db: Session = None):
        query = db.query(Chatbot)
        if business_profile_id is not None:
            query = query.filter(Chatbot.business_profile_id == business_profile_id)
        if user_id is not None:
            query = query.filter(Chatbot.owner_id == user_id)
        return query.all()

    @staticmethod
    def get_chatbot(chatbot_id: str, db: Session) -> Chatbot:
        chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
        if not chatbot:
            raise HTTPException(status_code=404, detail="Chatbot not found")
        return chatbot

    @staticmethod
    def update_chatbot(chatbot_id: str, chatbot_data: ChatbotCreate, db: Session) -> Chatbot:
        db_chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
        if not db_chatbot:
            raise HTTPException(status_code=404, detail="Chatbot not found")
        for key, value in chatbot_data.dict().items():
            setattr(db_chatbot, key, value)
        db.commit()
        db.refresh(db_chatbot)
        return db_chatbot

    @staticmethod
    def delete_chatbot(chatbot_id: str, db: Session):
        db_chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
        if not db_chatbot:
            raise HTTPException(status_code=404, detail="Chatbot not found")
        db.delete(db_chatbot)
        db.commit()
        return {"msg": "Chatbot deleted"}

    @staticmethod
    def chat_with_bot(chatbot_id: str, user_prompt: str, user_id: str, db: Session):
        pipe = config.PIPE
        llm_model = config.LLM_MODEL
        chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
        if not chatbot:
            raise HTTPException(status_code=404, detail="Chatbot not found")
        # System role: define the bot's role and context
        system_message = chatbot.prompt or "You are a helpful AI assistant."
        # RAG: Retrieve relevant context chunks from Chroma
        context_chunks = retrieve_relevant_chunks(user_id, user_prompt, top_k=5)
        context_text = '\n---\n'.join(context_chunks) if context_chunks else ''
        # Compose messages with context
        messages = [
            {"role": "system", "content": system_message},
        ]
        if context_text:
            messages.append({"role": "system", "content": f"Relevant business info:\n{context_text}"})
        messages.append({"role": "user", "content": user_prompt})
        try:
            if config.IS_TESTING_MODE:
                response = pipe(
                    model=llm_model,
                    messages=messages,
                    max_new_tokens=100,
                    use_pipeline=False
                )
                # Assume response is already a dict with the answer
                return response
            else:
                response = pipe(
                    model=llm_model,
                    messages=messages
                )
                if hasattr(response, 'message') and hasattr(response.message, 'content'):
                    content = response.message.content
                elif isinstance(response, dict) and 'message' in response:
                    content = response['message']['content']
                else:
                    content = str(response)
                try:
                    return json.loads(content)
                except Exception:
                    return {"response": content}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

CHROMA_DIR = 'chroma_db'
chroma_client = chromadb.Client(Settings(persist_directory=CHROMA_DIR))

# Choose embedding function based on config
if config.DEVELOPER_MODEL:
    # Use local embedding (sentence-transformers or similar)
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
else:
    # Use OpenAI embedding if not in dev mode
    embedding_fn = embedding_functions.OpenAIEmbeddingFunction(api_key=os.getenv('OPENAI_API_KEY'))

def chunk_text(text, max_tokens=500):
    # Use tiktoken to count tokens if available, else fallback to words
    try:
        enc = tiktoken.encoding_for_model('gpt-3.5-turbo')
        tokens = enc.encode(text)
        chunks = []
        for i in range(0, len(tokens), max_tokens):
            chunk = enc.decode(tokens[i:i+max_tokens])
            chunks.append(chunk)
        return chunks
    except Exception:
        # Fallback: split by words
        words = text.split()
        return [' '.join(words[i:i+max_tokens]) for i in range(0, len(words), max_tokens)]

def process_and_store_document(doc, user_id):
    # doc: BusinessDocument instance
    # user_id: int
    # Only process if extracted_data has text or rows
    if doc.extracted_data.get('text'):
        chunks = chunk_text(doc.extracted_data['text'])
    elif doc.extracted_data.get('rows'):
        # Flatten CSV rows to text
        rows = doc.extracted_data['rows']
        text = '\n'.join([', '.join(row) for row in rows])
        chunks = chunk_text(text)
    else:
        return
    # Embed and store in Chroma
    collection_name = f'user_{user_id}_docs'
    collection = chroma_client.get_or_create_collection(collection_name, embedding_function=embedding_fn)
    metadatas = [{"user_id": user_id, "doc_id": doc.id, "chunk_id": i} for i in range(len(chunks))]
    ids = [f'doc{doc.id}_chunk{i}' for i in range(len(chunks))]
    collection.add(documents=chunks, metadatas=metadatas, ids=ids)

def retrieve_relevant_chunks(user_id, query, top_k=5):
    collection_name = f'user_{user_id}_docs'
    collection = chroma_client.get_or_create_collection(collection_name, embedding_function=embedding_fn)
    results = collection.query(query_texts=[query], n_results=top_k)
    # Return the most relevant chunks
    return [doc for doc in results['documents'][0]] 