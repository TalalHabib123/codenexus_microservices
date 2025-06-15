from fastapi import APIRouter, HTTPException
from app.refactoring_models.refactor_models import (
    MappingResponse,
    PartialMappingRequest
)

from app.service.mapping_service import (
    apply_llm_patch
)

calls_router = APIRouter()

@calls_router.post("/long_parameter_list", response_model=MappingResponse)
async def long_parameter(request: PartialMappingRequest):
    result = apply_llm_patch(
        request.original_code,
        request.refactored_code,
        request.name
    )
    if result.get('success') is False:
        raise HTTPException(status_code=400, detail=result.get('error'))
    print(f"Refactored code: {result.get('refactored_code')}")
    return result