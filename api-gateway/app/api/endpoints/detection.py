import httpx
from fastapi import APIRouter, HTTPException
from app.models.detection_models import (
    DeadClassRequest,
    DeadClassResponse,
    DeadCodeRequest,
    DeadCodeResponse,
    AnalysisRequest,
    AnalysisResponse,
    CodeRequest,
    CodeResponse,
    VariableConflictRequest,
    VariableConflictResponse,
    TemporaryVariableResponse,
    UnreachableResponse,
    ComplexConditonalResponse,
    MagicNumbersResponse,
    LongParameterListResponse
)

detecton_gateway_router = APIRouter()

DETECTION_SERVICE_URL = "http://127.0.0.1:8001"

# Route for overly complex conditionals detection
@detecton_gateway_router.post("/overly-complex-conditionals", response_model=ComplexConditonalResponse)
async def gateway_overly_complex_conditionals(request: AnalysisRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{DETECTION_SERVICE_URL}/overly-complex-conditionals", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Route for unreachable code detection
@detecton_gateway_router.post("/unreachable-code", response_model=UnreachableResponse)
async def gateway_unreachable_code(request: AnalysisRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{DETECTION_SERVICE_URL}/unreachable-code", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Route for temporary field detection
@detecton_gateway_router.post("/temporary-field", response_model=TemporaryVariableResponse)
async def gateway_temporary_field(request: AnalysisRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{DETECTION_SERVICE_URL}/temporary-field", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Route for AST analysis
@detecton_gateway_router.post("/analyze-ast", response_model=CodeResponse)
async def gateway_analyze_ast(request: CodeRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{DETECTION_SERVICE_URL}/analyze-ast", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Route for dead code detection
@detecton_gateway_router.post("/dead-code", response_model=DeadCodeResponse)
async def gateway_dead_code(request: DeadCodeRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{DETECTION_SERVICE_URL}/dead-code", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Route for dead class detection
@detecton_gateway_router.post("/dead-class", response_model=DeadClassResponse)
async def gateway_dead_class(request: DeadClassRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{DETECTION_SERVICE_URL}/dead-class", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Route for magic numbers detection
@detecton_gateway_router.post("/magic-numbers", response_model=MagicNumbersResponse)
async def gateway_magic_numbers(request: AnalysisRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{DETECTION_SERVICE_URL}/magic-numbers", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Route for unused variables detection
@detecton_gateway_router.post("/unused-variables", response_model=AnalysisResponse)
async def gateway_unused_variables(request: AnalysisRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{DETECTION_SERVICE_URL}/unused-variables", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Route for naming convention detection
@detecton_gateway_router.post("/naming-convention", response_model=AnalysisResponse)
async def gateway_naming_convention(request: AnalysisRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{DETECTION_SERVICE_URL}/naming-convention", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Route for duplicated code detection
@detecton_gateway_router.post("/duplicated-code", response_model=AnalysisResponse)
async def gateway_duplicated_code(request: AnalysisRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{DETECTION_SERVICE_URL}/duplicated-code", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Route for parameter list detection
@detecton_gateway_router.post("/parameter-list", response_model=LongParameterListResponse)
async def gateway_parameter_list(request: AnalysisRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{DETECTION_SERVICE_URL}/parameter-list", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@detecton_gateway_router.post("/global-conflict", response_model=VariableConflictResponse)
async def gateway_global_conflict(request: VariableConflictRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{DETECTION_SERVICE_URL}/global-conflict", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()