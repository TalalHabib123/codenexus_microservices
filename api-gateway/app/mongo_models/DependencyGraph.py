from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class SourceEnum(str, Enum):
    Exporting = "Exporting"
    Importing = "Importing"

class UtilizedEntity(BaseModel):
    name: str
    type: str
    alias: Optional[str] = None
    source: SourceEnum

class DependentNode(BaseModel):
    name: str
    alias: Optional[str] = None
    valid: bool
    weight: List[UtilizedEntity] = Field(default_factory=list)

class FileNode(BaseModel):
    name: str
    dependencies: List[DependentNode] = Field(default_factory=list)

class DependencyGraph(BaseModel):
    files: Dict[str, FileNode] = Field(default_factory=dict)

# Input model for API calls, using projectTitle to find or create the project.
class GraphIn(BaseModel):
    projectTitle: str
    graphData: DependencyGraph