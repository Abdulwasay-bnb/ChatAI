import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load .env file
load_dotenv()

# OpenAI API settings
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "<your OpenAI API key if not set as an env var>")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o")
DEVELOPER_MODEL = os.environ.get("DEVELOPER_MODEL", "True").lower() in ("true", "1", "yes")

# Database settings
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_Name", "chatai_db")
DB_ENGINE = os.environ.get("DB_ENGINE","mysql+pymysql")

SQLALCHEMY_DATABASE_URL = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

PIPE = None

IS_TESTING_MODE = os.environ.get("IS_TESTING_MODE", "False").lower() in ("true", "1", "yes")

if IS_TESTING_MODE:
    import requests
    def fastapi_llm_pipe(model, messages, max_new_tokens=5000, use_pipeline=False):
        url = "https://land-auckland-them-each.trycloudflare.com/chat"
        payload = {
            "messages": messages,
            "max_new_tokens": max_new_tokens,
            "use_pipeline": use_pipeline
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    PIPE = fastapi_llm_pipe
elif DEVELOPER_MODEL:
    from ollama import chat
    PIPE = chat
    LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.2:1B")
else:
    from openai import OpenAI
    CLIENT = OpenAI(api_key=OPENAI_API_KEY)
    PIPE = CLIENT.chat.completions.create 

FRONTEND_HOST = os.environ.get("FRONTEND_HOST", None) 