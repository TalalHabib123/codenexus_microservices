from fastapi import APIRouter, HTTPException
from app.models.ast_models import (
    DeadCodeRequest, 
    DeadCodeResponse, 
    AnalysisRequest, 
    AnalysisResponse,
    DeadClassRequest,
    DeadClassResponse,
    VariableConflictRequest,
    VariableConflictResponse,
    TemporaryVariableResponse,
    UnreachableResponse,
    ComplexConditonalResponse,
    MagicNumbersResponse,
    LongParameterListResponse,
    UnusedVariablesResponse
)

from app.service.ast_service import (
    deadcode_analysis,
    magic_num_analysis,
    unused_variables_analysis,
    naming_convention_analysis,
    duplicated_code_analysis,
    parameter_list_analysis,
    dead_class_analysis,
    global_variable_analysis,
    overly_complex_conditionals_analysis,
    unreachable_code_check,
    check_temporary_field
)

router = APIRouter()

@router.post("/overly-complex-conditionals", response_model=ComplexConditonalResponse)
async def overly_complex_conditionals(request: AnalysisRequest):
    result = overly_complex_conditionals_analysis(request.code)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result

@router.post("/unreachable-code", response_model=UnreachableResponse)
async def unreachable_code(request: AnalysisRequest):
    result = unreachable_code_check(request.code)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result

@router.post("/temporary-field", response_model=TemporaryVariableResponse)
async def temporary_field(request: AnalysisRequest):
    result = check_temporary_field(request.code)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result

@router.post("/dead-code", response_model=DeadCodeResponse)
async def dead_code(request: DeadCodeRequest):
    result = deadcode_analysis(request.code, request.function_names, request.global_variables)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result   

@router.post("/dead-class", response_model=DeadClassResponse)
async def dead_class(request: DeadClassRequest):
    result = dead_class_analysis(request.code, request.class_name)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result 
    

@router.post("/magic-numbers", response_model=MagicNumbersResponse)
async def magic_numbers(request: AnalysisRequest):
    result = magic_num_analysis(request.code)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    print(result)
    return result
    
@router.post("/unused-variables", response_model=UnusedVariablesResponse)
async def unused_variables(request: AnalysisRequest):
    result = unused_variables_analysis(request.code)  
    
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    print(result)
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

@router.post("/parameter-list", response_model=LongParameterListResponse)
async def parameter_list(request: AnalysisRequest):
    result = parameter_list_analysis(request.code)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result

@router.post("/global-conflict", response_model=VariableConflictResponse)
async def global_conflict(request: VariableConflictRequest):
    result = global_variable_analysis(request.code, request.global_variables)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result