from fastapi import APIRouter
from app.services.llm_service import llm_service

router = APIRouter(prefix="/llm", tags=["Local LLM (Ollama)"])

@router.get("/status")
async def get_ollama_status():
    status = await llm_service.check_ollama_status()
    return status
