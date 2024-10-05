from fastapi import FastAPI
from app.api.endpoints import ast_gen, ast_analysis

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

app.include_router(ast_gen.router)
app.include_router(ast_analysis.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
