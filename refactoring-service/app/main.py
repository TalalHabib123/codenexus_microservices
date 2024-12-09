from fastapi import FastAPI
from app.api.endpoints import endpoints

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

app.include_router(endpoints.refactor_router)
# app.include_router(task_forwarding.forwarding_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
