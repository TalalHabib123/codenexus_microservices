import httpx
import json
from fastapi import APIRouter, HTTPException, Request
from app.mongo_models.Project import InitProjectRequest, express_respone
from app.mongo_models.Detection import DetectionData
from app.mongo_models.Refactor import RefactorData
from app.mongo_models.DependencyGraph import GraphIn
from app.mongo_models.Rulesets import InitRulesetRequest
from app.service.endpoints_url import EXPRESS_URL

logging_gateway_router = APIRouter()


@logging_gateway_router.post("/init_project", response_model=express_respone)
async def gateway_init_project(request: InitProjectRequest, req: Request):
    headers = {}
    if "Authorization" in req.headers:
        headers["Authorization"] = req.headers["Authorization"]
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{EXPRESS_URL}/project/create", json=request.model_dump(), headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()



@logging_gateway_router.post("/detection", response_model=express_respone)
async def gateway_detection(request: DetectionData, req: Request):
    headers = {}
    if "Authorization" in req.headers:
        headers["Authorization"] = req.headers["Authorization"]
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{EXPRESS_URL}/scan/addDetection", json=request.model_dump(), headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@logging_gateway_router.post("/refactor", response_model=express_respone)
async def gateway_detection(request: RefactorData, req: Request):
    headers = {}
    if "Authorization" in req.headers:
        headers["Authorization"] = req.headers["Authorization"]
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(f"{EXPRESS_URL}/scan/addRefactor", json=request.model_dump(mode='json'), headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()



@logging_gateway_router.post("/graph/add-or-update", response_model=express_respone)
async def create_or_update_graph(graph_in: GraphIn, req: Request):
    headers = {}
    if "Authorization" in req.headers:
        headers["Authorization"] = req.headers["Authorization"]
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("jfksdfdfh")
        response = await client.post(
            f"{EXPRESS_URL}/graph/add-or-update", json=graph_in.model_dump()
        )
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@logging_gateway_router.get("/graph/get/{projectTitle}", response_model=express_respone)
async def get_graph(projectTitle: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{EXPRESS_URL}/graph/get/{projectTitle}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@logging_gateway_router.delete("/graph/delete/{projectTitle}")
async def delete_graph(projectTitle: str, req: Request):
    headers = {}
    if "Authorization" in req.headers:
        headers["Authorization"] = req.headers["Authorization"]
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.delete(f"{EXPRESS_URL}/graph/delete/{projectTitle}", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@logging_gateway_router.post("/ruleset/add-or-update", response_model=express_respone)
async def create_or_update_ruleset(ruleset: dict, req: Request):
    headers = {}
    if "Authorization" in req.headers:
        headers["Authorization"] = req.headers["Authorization"]
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{EXPRESS_URL}/ruleset/add-or-update", json=ruleset , headers=headers
        )
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()