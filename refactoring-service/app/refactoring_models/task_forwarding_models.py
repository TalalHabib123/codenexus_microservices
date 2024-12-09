from pydantic import BaseModel

class ForwardTaskRequest(BaseModel):
    task_type: str
    task_data: dict  # Expecting a dict with file paths as keys and code as values
    task_job: str
    correlation_id: str  

class ForwardTaskResponse(BaseModel):
    status: str
    correlation_id: str