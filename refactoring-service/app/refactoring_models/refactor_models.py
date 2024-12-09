from pydantic import BaseModel
from typing import List, Dict, Union, Optional, Any, Tuple


class RefactorRequest(BaseModel):
    code: str
    refactor_type: str
    refactor_details: Dict[str, Any] 


class UnusedVariablesRefactorRequest(BaseModel):
    code: str
    unused_variables: List[str]


class MagicNumbersDetails(BaseModel):
    magic_number: int | float
    line_number: int

class MagicNumberRefactorRequest(BaseModel):
    code: str
    magic_numbers: List[MagicNumbersDetails] = None
    
    
class InconsistentNamingRefactorRequest(BaseModel):
    code: str
    target_convention: str
    naming_convention: str

class UnreachableCodeRequest (BaseModel):
    code: str
    unreachable_code_lines: List[int]

class DeadCodeRefactorRequest(BaseModel):
    code: str
    entity_name: str
    entity_type: str
        

class RefactorResponse(BaseModel):
    refactored_code: str
    success: bool = True
    error: Optional[str] = None
    
