from pydantic import BaseModel
from typing import List, Dict, Union, Optional

class CodeRequest(BaseModel):
    code: str

class GlobalVariable(BaseModel):
    variable_name: str
    variable_type: str
    class_or_function_name: str = None

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
    class_details: List[Dict[str, Union[str, List[str]]]]
    global_variables: List[GlobalVariable]
    imports: Dict[str, List[Import]]
    
class DeadCodeResponse(BaseModel):
    function_names: Optional[List[str]]
    class_details: Optional[List[Dict[str, Union[str, List[str]]]]]
    global_variables: Optional[List[GlobalVariable]]
    imports : Optional[Dict[str, List[Import]]]
    success: bool = True
    error: Optional[str] = None
