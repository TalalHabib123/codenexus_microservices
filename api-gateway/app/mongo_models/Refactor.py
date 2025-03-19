from pydantic import BaseModel, Field  
from typing import Optional, List, Any, Dict, Literal
from datetime import datetime


class Weight(BaseModel):
    name: str
    type: str
    alias: Optional[str] = None
    source: Literal["Exporting", "Importing"]

class Dependency(BaseModel):
    name: str
    valid: bool
    fileContent: str
    weight: List[Weight]
    
    
class RefactoringData(BaseModel):
    orginal_code: str
    refactored_code: Optional[str] = None
    refactoring_type: Optional[str] = None
    refactored_dependencies: Optional[List[Dependency]] = None
    time: datetime
    cascading_refactor: Optional[bool] = None
    job_id: Optional[str] = None
    ai_based: Optional[bool] = None
    files_affected: Optional[List[str]] = None
    outdated: Optional[bool] = None
    success: bool
    error: Optional[str] = None

class RefactorData(BaseModel):
    filePath: str
    refactorData: RefactoringData
    title: str = None