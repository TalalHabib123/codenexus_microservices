import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router
from mongoengine import connect

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}

connect (         
    host="mongodb+srv://admin:K7DPmvaISNvWS1l1@codenexus.d0kap.mongodb.net/?retryWrites=true&w=majority&appName=codenexus", # The MongoDB URI
    alias="default"
)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8004"))
    uvicorn.run(app, host="0.0.0.0", port=port)