from pydantic import BaseModel, Field  
from typing import Optional, List, Any, Dict
from datetime import datetime

class SubDetectionResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    data: Optional[Any] = None

class UserTriggeredDetection(BaseModel):
    data: List[Any]
    time: datetime = Field(default_factory=datetime.now)
    analysis_type: str
    job_id: str
    outdated: bool = False
    success: bool
    error: Optional[str] = None

class DetectionResponse(BaseModel):
    magic_numbers: Optional[SubDetectionResponse] = None
    duplicated_code: Optional[SubDetectionResponse] = None
    unused_variables: Optional[SubDetectionResponse] = None
    long_parameter_list: Optional[SubDetectionResponse] = None
    naming_convention: Optional[SubDetectionResponse] = None
    dead_code: Optional[SubDetectionResponse] = None
    unreachable_code: Optional[SubDetectionResponse] = None
    temporary_field: Optional[SubDetectionResponse] = None
    overly_complex_condition: Optional[SubDetectionResponse] = None
    global_conflict: Optional[SubDetectionResponse] = None
    user_triggered_detection: Optional[List[UserTriggeredDetection]] = None
    success: bool
    error: Optional[str] = None
    
class DetectionData(BaseModel): 
    detectionData: Dict[str, 'DetectionResponse'] = None
    title: str = None
    scan_type: str = None
    scan_name: str = None