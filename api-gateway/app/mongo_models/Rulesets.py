from pydantic import BaseModel
from typing import List, Dict, Union, Optional, Any, Tuple

class FileSmell(BaseModel):
    path: str
    smells: List[str]

class Ruleset(BaseModel):
    refactorSmells: List[str]
    detectSmells: List[str]
    includeFiles: List[FileSmell | str]
    excludeFiles: List[str | FileSmell]

class InitRulesetRequest(BaseModel):
    title: str
    ruleset: Ruleset