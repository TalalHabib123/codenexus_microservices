from fastapi import APIRouter, HTTPException
from app.models.ast_models import CodeRequest, CodeResponse
from app.service.ast_service import generate_ast

router = APIRouter()

@router.post("/analyze-ast", response_model=CodeResponse)
async def analyze_ast(request: CodeRequest):
    result = generate_ast(request.code)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result


