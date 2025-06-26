from fastapi import FastAPI

app = FastAPI(
    title="ChatAI SaaS Chatbot Service",
    description="A SaaS platform for businesses to create and embed chatbots.",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to ChatAI SaaS Chatbot Service!"} 