from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.invoke_openai import OpenAIAgent
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
openai_agent = OpenAIAgent()

class TranslationRequest(BaseModel):
    input_str: str

@app.post("/translate") 
async def translate(request: TranslationRequest):
    try:
        translated_text = openai_agent.translate_text(request.input_str)
        return {"translated_text": translated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
