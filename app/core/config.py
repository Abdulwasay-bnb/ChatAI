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
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "password")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
MYSQL_DB = os.environ.get("MYSQL_DB", "chatai_db")

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

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

if DEVELOPER_MODEL:
    from ollama import chat
    PIPE = chat
    LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.2:1B")
else:
    from openai import OpenAI
    CLIENT = OpenAI(api_key=OPENAI_API_KEY)
    PIPE = CLIENT.chat.completions.create 