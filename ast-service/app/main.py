from fastapi import FastAPI
from app.api.endpoints import ast_gen, ast_analysis, task_forwarding

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

app.include_router(ast_gen.gen_router)
app.include_router(ast_analysis.analysis_router)
app.include_router(task_forwarding.forwarding_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
