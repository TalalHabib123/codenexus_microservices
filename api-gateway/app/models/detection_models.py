from pydantic import BaseModel
from typing import List, Dict, Union, Optional, Any, Tuple

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
    class_details: Optional[List[Dict[str, Union[str, List[str], bool]]]] = []
    global_variables: Optional[List[str]] = []
    imports: Optional[Dict[str, List[Dict[str, Any]]]] = {"dead_imports": [], "unused_imports": []}
    success: bool = True
    error: Optional[str] = None

class AnalysisRequest(BaseModel):
    code: str

class AnalysisResponse(BaseModel):
    data: Optional[Any]
    success: bool = True
    error: Optional[str] = None
    
class MagicNumbersDetails(BaseModel):
    magic_number: int | float
    line_number: int

class MagicNumbersResponse(BaseModel):
    magic_numbers: Optional[List[MagicNumbersDetails]] = None
    success: bool
    error: Optional[str] = None
    
    
class ParameterListDetails(BaseModel):
    function_name: str 
    parameters: List[str] 
    long_parameter_count: int 
    long_parameter: bool 
    line_number: int

class LongParameterListResponse(BaseModel):
    long_parameter_list: Optional[List[ParameterListDetails]] = None 
    success: bool 
    error: Optional[str] = None  
    
class UnusedVariablesDetails(BaseModel):
    variable_name: str
    line_number: int

class UnusedVariablesResponse(BaseModel):
    unused_variables: Optional[List[UnusedVariablesDetails]] = None
    success: bool
    error: Optional[str] = None

class NamingConventionVars (BaseModel):
    variable: str
    line_number: int
    
    
class InconsistentNamingDetails(BaseModel):
    type: str
    total_count: int
    type_count: int
    vars: List[NamingConventionVars]

class InconsistentNamingResponse(BaseModel):
    inconsistent_naming: Optional[List[InconsistentNamingDetails]] = None
    success: bool
    error: Optional[str] = None

class Duplicates(BaseModel):
    code: str
    start_line: int
    end_line: int

class DuplicateCodeDetails(BaseModel):
    original_code: str
    start_line: int
    end_line: int
    duplicates: List[Duplicates]
    duplicate_count: int

class DuplicateCodeResponse(BaseModel):
    duplicate_code: Optional[List[DuplicateCodeDetails]] = None
    success: bool
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
    
class VariableConflictAnalysis(BaseModel):
    variable: str
    assignments: List[Tuple[str, int]] 
    local_assignments: List[Tuple[str, int]]  
    usages: List[Tuple[str, int]] 
    conflicts: List[str] 
    warnings: List[str] 

class VariableConflictRequest(BaseModel):
    code: str 
    global_variables: List[str] 

class VariableConflictResponse(BaseModel):
    conflicts_report: List[VariableConflictAnalysis]
    success: bool = True
    error: Optional[str] = None
    
class TemporaryVariableResponse(BaseModel):
    temporary_fields: Optional[List[str]] = []
    success: bool = True
    error: Optional[str] = None
    
class UnreachableResponse(BaseModel):
    unreachable_code: Optional[List[str]] = []
    success: bool = True
    error: Optional[str] = None
    
class ConditionDetails(BaseModel):
    line_range: Tuple[int, int]
    condition_code: str
    complexity_score: int
    code_block: str
    
class ComplexConditonalResponse(BaseModel):
    conditionals: Optional[List[ConditionDetails]] = []
    success: bool = True
    error: Optional[str] = None
    
    