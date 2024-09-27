from fastapi import APIRouter, HTTPException
from app.models.ast_models import DeadCodeRequest, DeadCodeResponse
from app.service.ast_service import deadcode_analysis

router = APIRouter()

@router.post("/dead-code", response_model=DeadCodeResponse)
async def dead_code(request: DeadCodeRequest):
    result = deadcode_analysis(request.code, request.function_names, request.global_variables)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result    
    