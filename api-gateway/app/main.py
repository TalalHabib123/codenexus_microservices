import os
import uvicorn
from fastapi import FastAPI
from app.api.endpoints.detection import detecton_gateway_router

app = FastAPI()

app.include_router(detecton_gateway_router, prefix="/detection")

@app.get("/")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)