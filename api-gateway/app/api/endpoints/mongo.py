import httpx
import json
from fastapi import APIRouter, HTTPException
from app.mongo_models.Project import InitProjectRequest, express_respone
from app.mongo_models.Detection import DetectionData

from app.service.endpoints_url import EXPRESS_URL

logging_gateway_router = APIRouter()


@logging_gateway_router.post("/init_project", response_model=express_respone)
async def gateway_init_project(request: InitProjectRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{EXPRESS_URL}/project/create", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()



@logging_gateway_router.post("/detection", response_model=express_respone)
async def gateway_detection(request: DetectionData):
    print("again")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{EXPRESS_URL}/scan/addDetection", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@logging_gateway_router.post("/refactor", response_model=express_respone)
async def gateway_detection(request: DetectionData):
    print("again")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{EXPRESS_URL}/scan/addRefactor", json=request.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()



