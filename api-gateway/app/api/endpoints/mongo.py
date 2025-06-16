import httpx
import json
import ast
from fastapi import APIRouter, HTTPException, Request
from app.mongo_models.Project import InitProjectRequest, express_respone
from app.mongo_models.Detection import DetectionData
from app.mongo_models.Refactor import RefactorData
from app.mongo_models.DependencyGraph import GraphIn
from app.mongo_models.Rulesets import InitRulesetRequest
from app.mongo_models.Project import UpdateFileDataRequest
from app.service.endpoints_url import EXPRESS_URL

logging_gateway_router = APIRouter()

    
def ast_to_string(node):
    """Convert AST node to string representation with complete fidelity"""
    if isinstance(node, ast.AST):
        return ast.dump(node, indent=2, include_attributes=True)
    else:
        return str(node)


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

@logging_gateway_router.post("/update_file_data", response_model=express_respone)
async def gateway_update_file_data(request: UpdateFileDataRequest, req: Request):
    
    headers = {}
    if "Authorization" in req.headers:
        headers["Authorization"] = req.headers["Authorization"]
    else:
        print("No Authorization header")
    try:
        # Convert to dict for serialization
        serialized_data = {}
        for file_name, file_data in request.fileData.items():
            serialized_data[file_name] = file_data.model_dump()
        
        request.fileData = serialized_data
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Serialization error: {str(e)}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{EXPRESS_URL}/file-data/update", 
                json=request.model_dump(), 
                headers=headers
            )
    
        if response.status_code != 200:
            print(f"EXPRESS SERVER ERROR: {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        return response.json()
        
    except httpx.RequestError as e:
        print(f"HTTP REQUEST ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        print(f"UNEXPECTED ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
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
        print("uauth", headers["Authorization"])
    async with httpx.AsyncClient(timeout=30.0) as client:
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