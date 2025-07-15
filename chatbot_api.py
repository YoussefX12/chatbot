from fastapi import FastAPI, Request
from pydantic import BaseModel
from chatbot import ask_openrouter, fetch_all_data

app = FastAPI()
context_data = fetch_all_data()

class ChatInput(BaseModel):
    question: str

@app.post("/chat")
def chat(input: ChatInput):
    answer = ask_openrouter(input.question, context_data)
    return {"reply": answer}
