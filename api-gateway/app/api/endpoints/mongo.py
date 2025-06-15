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

# def ast_to_dict(node):
#     """Convert AST node to JSON-serializable dictionary with complete fidelity"""
#     if isinstance(node, ast.AST):
#         result = {'_type': node.__class__.__name__}
        
#         # Handle all fields that ast.iter_fields() provides
#         for field, value in ast.iter_fields(node):
#             result[field] = _convert_value(value)
        
#         # Handle special attributes that may not be in iter_fields
#         # These include line numbers, column offsets, etc.
#         for attr in ['lineno', 'col_offset', 'end_lineno', 'end_col_offset']:
#             if hasattr(node, attr):
#                 result[attr] = getattr(node, attr)
        
#         # Handle type_comment attribute for Python 3.8+
#         if hasattr(node, 'type_comment') and node.type_comment is not None:
#             result['type_comment'] = node.type_comment
            
#         return result
#     else:
#         return _convert_value(node)

# def _convert_value(value):
#     """Helper function to convert various value types"""
#     if isinstance(value, ast.AST):
#         return ast_to_dict(value)
#     elif isinstance(value, list):
#         return [_convert_value(item) for item in value]
#     elif isinstance(value, tuple):
#         return [_convert_value(item) for item in value]  # Convert tuple to list for JSON
#     elif value is None:
#         return None
#     elif isinstance(value, (str, int, float, bool)):
#         return value
#     elif isinstance(value, complex):
#         return {'_complex': True, 'real': value.real, 'imag': value.imag}
#     elif isinstance(value, bytes):
#         return {'_bytes': True, 'data': value.decode('utf-8', errors='replace')}
#     else:
#         # For any other type, try to convert to string as fallback
#         return str(value)
    
    
    
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
        print(f"Authorization header present")
    else:
        print("No Authorization header")
    
    # Process each file
    for file_name, file_data in request.fileData.items():
        if file_data.code is not None: 
            try: 
                if file_data.ast is None:
                    print(f"Generating AST for {file_name}...")
                    # Parse the code string (not file path) and convert back to source
                    file_data.ast = ast.dump(ast.parse(file_data.code))
                    print(f"AST generated successfully for {file_name}")
                else:
                    print(f"Using existing AST for {file_name}")
            except SyntaxError as e:
              
                raise HTTPException(
                    status_code=400, 
                    detail=f"Syntax error in code for {file_name}: {str(e)}"
                )
            except Exception as e:
               
                raise HTTPException(
                    status_code=400, 
                    detail=f"Error parsing code for {file_name}: {str(e)}"
                )
        else:
            file_data.ast = None
    
    print(f"\n=== Converting to dict for serialization ===")
    try:
        # Convert to dict for serialization
        serialized_data = {}
        for file_name, file_data in request.fileData.items():
            serialized_data[file_name] = file_data.model_dump()
            print(f"Serialized {file_name}: keys = {list(serialized_data[file_name].keys())}")
        
        request.fileData = serialized_data
        
        # Print final request structure
        final_request = request.model_dump()
        print(f"Final request keys: {list(final_request.keys())}")
        print(f"Final fileData keys: {list(final_request['fileData'].keys())}")
        
    except Exception as e:
        print(f"ERROR during serialization: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Serialization error: {str(e)}")
    
    print(f"\n=== Sending to Express server ===")
    print(f"URL: {EXPRESS_URL}/file-data/update")
    print(f"Headers: {headers}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{EXPRESS_URL}/file-data/update", 
                json=request.model_dump(), 
                headers=headers
            )
        
        print(f"Express response status: {response.status_code}")
        print(f"Express response text: {response.text}")
        
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