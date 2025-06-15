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
    magic_number: Union[int, float]  # Changed from int | float to Union[int, float]
    line_number: int


class MagicNumberRefactorRequest(BaseModel):
    code: str
    magic_numbers: Optional[List[MagicNumbersDetails]] = None  # Changed to Optional
    dependencies: Optional[List[Dependency]] = None


class InconsistentNamingRefactorRequest(BaseModel):
    code: str
    target_convention: str
    naming_convention: str
    dependencies: Optional[List[Dependency]] = None


class UnreachableCodeRequest(BaseModel):
    code: str
    unreachable_code_lines: List[int]
    dependencies: Optional[List[Dependency]] = None


class DeadCodeRefactorRequest(BaseModel):
    code: str
    entity_name: str
    entity_type: str
    dependencies: Optional[List[Dependency]] = None


class RefactorResponse(BaseModel):
    refactored_code: Optional[str] = ""
    dependencies: Optional[List[Dependency]] = None
    success: bool = True
    error: Optional[str] = None


class PartialMappingRequest(BaseModel):
    original_code: str  # Note: typo in "original"
    refactored_code: str
    name: str | bool = False  # Changed from str to str | bool


class CompleteMappingRequest(BaseModel):
    original_code: str  # Note: typo in "original"
    refactored_code: str


class MappingResponse(BaseModel):
    refactored_code: Optional[str]
    success: bool = True
    error: Optional[str] = None