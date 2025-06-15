from pydantic import BaseModel
from typing import List, Dict, Union, Optional, Any, Tuple 

class InitProjectRequest(BaseModel):
    title: str
    description: str

class express_respone(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    
class FileData(BaseModel):
    code: Optional[str] = None
    ast: Optional[str] = None

class UpdateFileDataRequest(BaseModel):
    title: str
    fileData: Dict[str, FileData]