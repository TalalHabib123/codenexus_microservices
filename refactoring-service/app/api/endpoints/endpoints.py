from fastapi import APIRouter, HTTPException
from app.refactoring_models.refactor_models import (
    UnusedVariablesRefactorRequest,
    MagicNumberRefactorRequest,
    InconsistentNamingRefactorRequest,
    UnreachableCodeRequest,
    DeadCodeRefactorRequest,
    RefactorResponse
)


from app.service.refactor_service import (
    refactor_inconsistent_naming,
    refactor_magic_numbers,
    refactor_unreachable_code,
    refactor_unused_variables,
    refactor_dead_code
)

refactor_router = APIRouter()



@refactor_router.post("/unreachable-code", response_model=RefactorResponse)
async def unreachable_code(request: UnreachableCodeRequest):
    result = refactor_unreachable_code(request.unreachable_code_lines, request.code)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result
    

@refactor_router.post("/magic-numbers", response_model=RefactorResponse)
async def magic_numbers(request: MagicNumberRefactorRequest):
    result = refactor_magic_numbers(request.code, request.magic_numbers)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    print(result)
    return result
    
@refactor_router.post("/unused-variables", response_model=RefactorResponse)
async def unused_variables(request: UnusedVariablesRefactorRequest):
    result = refactor_unused_variables(request.unused_variables, request.code)
    
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    print(result)
    return result


@refactor_router.post("/naming-convention", response_model=RefactorResponse)
async def naming_convention(request: InconsistentNamingRefactorRequest):
    result = refactor_inconsistent_naming(request.code, request.target_convention)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result

@refactor_router.post("/dead-code", response_model=RefactorResponse)
async def dead_code(request: DeadCodeRefactorRequest):
    result = refactor_dead_code(request.entity_name, request.entity_type, request.code)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid code")
    elif result.get('success') is False:
        print(result.get('error'))
    return result   

# @refactor_router.post("/duplicated-code", response_model=DuplicateCodeResponse)
# async def duplicated_code(request: AnalysisRequest):
#     result = duplicated_code_analysis(request.code)
#     if result is None:
#         raise HTTPException(status_code=400, detail="Invalid code")
#     elif result.get('success') is False:
#         print(result.get('error'))
#     return result

# @refactor_router.post("/parameter-list", response_model=LongParameterListResponse)
# async def parameter_list(request: AnalysisRequest):
#     result = parameter_list_analysis(request.code)
#     if result is None:
#         raise HTTPException(status_code=400, detail="Invalid code")
#     elif result.get('success') is False:
#         print(result.get('error'))
#     return result

# @refactor_router.post("/global-conflict", response_model=VariableConflictResponse)
# async def global_conflict(request: VariableConflictRequest):
    
#     result = global_variable_analysis(request.code, request.global_variables)
#     print("result",result)
#     if result is None:
#         raise HTTPException(status_code=400, detail="Invalid code")
#     elif result.get('success') is False:
#         print(result.get('error'))
#     return result

# @refactor_router.post("/temporary-field", response_model=TemporaryVariableResponse)
# async def temporary_field(request: AnalysisRequest):
#     result = check_temporary_field(request.code)
#     if result is None:
#         raise HTTPException(status_code=400, detail="Invalid code")
#     elif result.get('success') is False:
#         print(result.get('error'))
#     return result



# @refactor_router.post("/dead-class", response_model=DeadClassResponse)
# async def dead_class(request: DeadClassRequest):
#     result = dead_class_analysis(request.code, request.class_name)
#     if result is None:
#         raise HTTPException(status_code=400, detail="Invalid code")
#     elif result.get('success') is False:
#         print(result.get('error'))
#     return result 

# @refactor_router.post("/overly-complex-conditionals", response_model=ComplexConditonalResponse)
# async def overly_complex_conditionals(request: AnalysisRequest):
#     result = overly_complex_conditionals_analysis(request.code)
#     if result is None:
#         raise HTTPException(status_code=400, detail="Invalid code")
#     elif result.get('success') is False:
#         print(result.get('error'))
#     return result