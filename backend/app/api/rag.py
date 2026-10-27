from fastapi import APIRouter, Body
from app.services.rag_service import rag_service

router = APIRouter(prefix="/rag", tags=["RAG Legal Assistant"])

@router.post("/ask")
def ask_rule_book(payload: dict = Body(...)):
    question = payload.get("question", "").strip()
    if not question:
        return {"error": "Question cannot be empty", "answer": "", "citations": []}
    
    result = rag_service.query(question)
    return result
