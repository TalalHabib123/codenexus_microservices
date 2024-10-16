from fastapi import APIRouter, HTTPException
import uuid
from app.models.task_forwarding_models import ForwardTaskRequest, ForwardTaskResponse
from app.service.forwarding_service import send_task_to_llm
forwarding_router = APIRouter()


@forwarding_router.post("/forward-task", response_model=ForwardTaskResponse)
async def forward_task(request: ForwardTaskRequest):
    correlation_id = request.correlation_id or str(uuid.uuid4())

    try:
        await send_task_to_llm(correlation_id, request.task_type, request.task_job, request.task_data)

        return {"status": "Task forwarded to LLM queue", "correlation_id": correlation_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task forwarding failed: {e}")