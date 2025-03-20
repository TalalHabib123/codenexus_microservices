from pydantic import BaseModel
from typing import List, Dict, Union, Optional, Any, Tuple 

class InitProjectRequest(BaseModel):
    title: str
    description: str

class express_respone(BaseModel):
    status: Optional[str]
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None