from pydantic import BaseModel
from typing import List, Dict, Union, Optional, Any

class CodeRequest(BaseModel):
    code: str

class GlobalVariable(BaseModel):
    variable_name: str
    variable_type: str
    class_or_function_name: Optional[str] = None

class Import(BaseModel):
    name: str
    alias: Optional[str]
    type: str 
    module: Optional[str] = None

class CodeResponse(BaseModel):
    ast: Optional[str]
    function_names: Optional[List[str]]
    class_details: Optional[List[Dict[str, Union[str, List[str]]]]]
    global_variables: Optional[List[GlobalVariable]]
    is_main_block_present: Optional[bool]
    imports: Optional[Dict[str, List[Import]]]
    is_standalone_file: Optional[bool]
    success: bool = True
    error: Optional[str] = None
    
class DeadCodeRequest(BaseModel):
    code: str
    function_names: List[str]
    global_variables: List[str]
    
class DeadCodeResponse(BaseModel):
    function_names: Optional[List[str]] = []
    class_details: Optional[List[Dict[str, Union[str, List[str]]]]] = []
    global_variables: Optional[List[str]] = []
    imports: Optional[Dict[str, List[Dict[str, Any]]]] = {"dead_imports": [], "unused_imports": []}
    success: bool = True
    error: Optional[str] = None

class AnalysisRequest(BaseModel):
    code: str

class AnalysisResponse(BaseModel):
    data: Optional[Any]
    sucess: bool = True
    error: Optional[str] = None
    
class DeadClassRequest(BaseModel):
    code: str
    class_name: str
    
class ClassDetails(BaseModel):
    methods: List[str]
    variables: List[str]
    
class DeadClassResponse(BaseModel):
    class_details: Optional[ClassDetails] = []
    success: bool = True
    error: Optional[str] = None