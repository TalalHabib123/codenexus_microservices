from fastapi import APIRouter, HTTPException
from app.models.ast_models import CodeRequest, CodeResponse
from app.service.ast_service import generate_ast

router = APIRouter()

@router.post("/analyze-ast", response_model=CodeResponse)
async def analyze_ast(request: CodeRequest):
    result = generate_ast(request.code)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result


