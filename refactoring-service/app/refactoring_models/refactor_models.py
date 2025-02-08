from pydantic import BaseModel
from typing import List, Dict, Union, Optional, Any, Tuple, Literal

class Weight(BaseModel):
    name: str
    type: str
    alias: Optional[str] = None
    source: Literal['Exporting', 'Importing']

class Dependency(BaseModel):
    name: str
    valid: bool
    fileContent: str
    weight: List[Weight]

class RefactorRequest(BaseModel):
    code: str      
    refactor_type: str
    refactor_details: Dict[str, Any] 


class UnusedVariablesRefactorRequest(BaseModel):
    code: str
    unused_variables: List[str]
    dependencies: Optional[List[Dependency]] = None


class MagicNumbersDetails(BaseModel):
    magic_number: int | float
    line_number: int

class MagicNumberRefactorRequest(BaseModel):
    code: str
    magic_numbers: List[MagicNumbersDetails] = None
    dependencies: Optional[List[Dependency]] = None
    
    
    
class InconsistentNamingRefactorRequest(BaseModel):
    code: str
    target_convention: str
    naming_convention: str
    dependencies: Optional[List[Dependency]] = None

class UnreachableCodeRequest (BaseModel):
    code: str
    unreachable_code_lines: List[int]
    dependencies: Optional[List[Dependency]] = None

class DeadCodeRefactorRequest(BaseModel):
    code: str
    entity_name: str
    entity_type: str
    dependencies: Optional[List[Dependency]] = None
        

class RefactorResponse(BaseModel):
    refactored_code: str
    dependencies: Optional[List[Dependency]] = None
    success: bool = True
    error: Optional[str] = None 
    
