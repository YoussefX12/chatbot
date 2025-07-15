from fastapi import FastAPI, Request
from pydantic import BaseModel
from chatbot import ask_openrouter, fetch_all_data
API_KEY = "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"

app = FastAPI()
context_data = fetch_all_data()

class ChatInput(BaseModel):
    question: str

@app.post("/chat")
def chat(input: ChatInput):
    answer = ask_openrouter(input.question, context_data)
    return {"reply": answer}
