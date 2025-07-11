from fastapi import APIRouter, HTTPException
from app.refactoring_models.refactor_models import (
    MappingResponse,
    PartialMappingRequest,
    CompleteMappingRequest
)

from app.service.mapping_service import (
    map_class,
    map_function,
    map_orginal_code
)

mapping_router = APIRouter()

@mapping_router.post("/god_object", response_model=MappingResponse)
async def god_object(request: PartialMappingRequest):
    result = map_class(request.original_code, request.name, request.refactored_code)
    if result.get('success') is False:
        raise HTTPException(status_code=400, detail=result.get('error'))
    return result

@mapping_router.post("/long_function", response_model=MappingResponse)
async def long_function(request: PartialMappingRequest):
    result = map_function(request.original_code, request.name, request.refactored_code)
    if result.get('success') is False:
        raise HTTPException(status_code=400, detail=result.get('error'))
    return result

@mapping_router.post("/temporary_field", response_model=MappingResponse)
async def temporary_field(request: CompleteMappingRequest):
    result = map_orginal_code(request.refactored_code)
    if result.get('success') is False:
        print("ERROR: ", result.get('error'))
        raise HTTPException(status_code=400, detail=result.get('error'))
    return result

@mapping_router.post("/duplicate_code", response_model=MappingResponse)
async def duplicate_code(request: CompleteMappingRequest):
    result = map_orginal_code(request.refactored_code)
    if result.get('success') is False:
        raise HTTPException(status_code=400, detail=result.get('error'))
    return result

@mapping_router.post("/conditionals", response_model=MappingResponse)
async def conditionals(request: CompleteMappingRequest):
    result = map_orginal_code(request.refactored_code)
    if result.get('success') is False:
        raise HTTPException(status_code=400, detail=result.get('error'))
    return result

@mapping_router.post("/global_conflict", response_model=MappingResponse)
async def global_conflict(request: CompleteMappingRequest):
    result = map_orginal_code(request.refactored_code)
    if result.get('success') is False:
        raise HTTPException(status_code=400, detail=result.get('error'))
    return result


@mapping_router.post("/feature_envy", response_model=MappingResponse)
async def feature_envy(request: PartialMappingRequest):
    result = map_function(request.original_code, request.name, request.refactored_code)
    if result.get('success') is False:
        raise HTTPException(status_code=400, detail=result.get('error'))
    return result

@mapping_router.post("/switch_statement_abuser", response_model=MappingResponse)
async def switch_statement(request: PartialMappingRequest):
    result = map_function(request.original_code, request.name, request.refactored_code)
    if result.get('success') is False:
        raise HTTPException(status_code=400, detail=result.get('error'))
    return result

@mapping_router.post("/excessive_flags", response_model=MappingResponse)
async def excessive_flags(request: PartialMappingRequest):
    result = map_function(request.original_code, request.name, request.refactored_code)
    if result.get('success') is False:
        raise HTTPException(status_code=400, detail=result.get('error'))
    return result

@mapping_router.post("/long_parameter_list", response_model=MappingResponse)
async def long_parameter(request: PartialMappingRequest):
    result = map_function(request.original_code, request.name, request.refactored_code)
    if result.get('success') is False:
        raise HTTPException(status_code=400, detail=result.get('error'))
    return result