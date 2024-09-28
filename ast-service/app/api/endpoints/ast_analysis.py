from fastapi import APIRouter, HTTPException
from app.models.ast_models import DeadCodeRequest, DeadCodeResponse, AnalysisRequest, AnalysisResponse
from app.service.ast_service import (
    deadcode_analysis,
    magic_num_analysis,
    unused_variables_analysis,
    naming_convention_analysis,
    duplicated_code_analysis,
    parameter_list_analysis,
)

router = APIRouter()

@router.post("/dead-code", response_model=DeadCodeResponse)
async def dead_code(request: DeadCodeRequest):
    result = deadcode_analysis(request.code, request.function_names, request.global_variables)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result    
    
@router.post("/magic-numbers", response_model=AnalysisResponse)
async def magic_numbers(request: AnalysisRequest):
    result = magic_num_analysis(request.code)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    print(result)
    return result
    
@router.post("/unused-variables", response_model=AnalysisResponse)
async def unused_variables(request: AnalysisRequest):
    result = unused_variables_analysis(request.code)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result


@router.post("/naming-convention", response_model=AnalysisResponse)
async def naming_convention(request: AnalysisRequest):
    result = naming_convention_analysis(request.code)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result

@router.post("/duplicated-code", response_model=AnalysisResponse)
async def duplicated_code(request: AnalysisRequest):
    result = duplicated_code_analysis(request.code)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result

@router.post("/parameter-list", response_model=AnalysisResponse)
async def parameter_list(request: AnalysisRequest):
    result = parameter_list_analysis(request.code)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result