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
