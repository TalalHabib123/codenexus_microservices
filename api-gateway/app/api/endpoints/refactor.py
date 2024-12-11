import httpx
import json
from fastapi import APIRouter, HTTPException
from app.models.refactoring_models import (
    RefactorResponse, 
    DeadCodeRefactorRequest,
    UnusedVariablesRefactorRequest,
    MagicNumberRefactorRequest,
    InconsistentNamingRefactorRequest,
    UnreachableCodeRequest
)

from app.service.refactor_url import REFACTOR_SERVICE_URL

refactor_gateway_router = APIRouter()



# Route for overly complex conditionals refactor
# @detecton_gateway_router.post("/overly-complex-conditionals", response_model=ComplexConditonalResponse)
# async def gateway_overly_complex_conditionals(request: AnalysisRequest):
#     async with httpx.AsyncClient(timeout=30.0) as client:
#         response = await client.post(f"{REFACTOR_SERVICE_URL}/overly-complex-conditionals", json=request.model_dump())
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail=response.text)
#     return response.json()

# Route for unreachable code refactor
@refactor_gateway_router.post("/unreachable-code", response_model=RefactorResponse)
async def gateway_unreachable_code(request: UnreachableCodeRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{REFACTOR_SERVICE_URL}/unreachable-code", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# # Route for temporary field refactor
# @refactor_gateway_router.post("/temporary-field", response_model=TemporaryVariableResponse)
# async def gateway_temporary_field(request: AnalysisRequest):
#     async with httpx.AsyncClient(timeout=30.0) as client:
#         response = await client.post(f"{REFACTOR_SERVICE_URL}/temporary-field", json=request.model_dump())
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail=response.text)
#     return response.json()

# Route for dead code refactor
@refactor_gateway_router.post("/dead-code", response_model=RefactorResponse)
async def gateway_dead_code(request: DeadCodeRefactorRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{REFACTOR_SERVICE_URL}/dead-code", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# # Route for dead class refactor
# @refactor_gateway_router.post("/dead-class", response_model=DeadClassResponse)
# async def gateway_dead_class(request: DeadClassRequest):
#     async with httpx.AsyncClient(timeout=30.0) as client:
#         response = await client.post(f"{REFACTOR_SERVICE_URL}/dead-class", json=request.model_dump())
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail=response.text)
#     return response.json()

# Route for magic numbers refactor
@refactor_gateway_router.post("/magic-numbers", response_model=RefactorResponse)
async def gateway_magic_numbers(request: MagicNumberRefactorRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{REFACTOR_SERVICE_URL}/magic-numbers", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Route for unused variables refactor
@refactor_gateway_router.post("/unused-variables", response_model=RefactorResponse)
async def gateway_unused_variables(request: UnusedVariablesRefactorRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{REFACTOR_SERVICE_URL}/unused-variables", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    print(response.json())
    return response.json()

# Route for naming convention refactor
@refactor_gateway_router.post("/naming-convention", response_model=RefactorResponse)
async def gateway_naming_convention(request: InconsistentNamingRefactorRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{REFACTOR_SERVICE_URL}/naming-convention", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Route for duplicated code refactor
# @refactor_gateway_router.post("/duplicated-code", response_model=DuplicateCodeResponse)
# async def gateway_duplicated_code(request: AnalysisRequest):
#     async with httpx.AsyncClient(timeout=30.0) as client:
#         response = await client.post(f"{REFACTOR_SERVICE_URL}/duplicated-code", json=request.model_dump())
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail=response.text)
#     return response.json()

# # Route for parameter list refactor
# @refactor_gateway_router.post("/parameter-list", response_model=LongParameterListResponse)
# async def gateway_parameter_list(request: AnalysisRequest):
#     async with httpx.AsyncClient(timeout=30.0) as client:
#         response = await client.post(f"{REFACTOR_SERVICE_URL}/parameter-list", json=request.model_dump())
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail=response.text)
#     return response.json()

# @refactor_gateway_router.post("/global-conflict", response_model=VariableConflictResponse)
# async def gateway_global_conflict(request: VariableConflictRequest):
#     async with httpx.AsyncClient(timeout=30.0) as client:
#         response = await client.post(f"{REFACTOR_SERVICE_URL}/global-conflict", json=request.model_dump())
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail=response.text)
#     return response.json()