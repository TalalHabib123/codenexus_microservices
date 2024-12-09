import os
import uvicorn
from fastapi import FastAPI
from app.api.endpoints.detection import detecton_gateway_router
from app.api.endpoints.refactor import refactor_gateway_router
# from app.api.endpoints.websockets import websocket_gateway_router, lifespan   #Sockets Code For Iteration 2


app = FastAPI() # lifespan=lifespan #Sockets Code For Iteration 2

app.include_router(detecton_gateway_router, prefix="/detection")
app.include_router(refactor_gateway_router, prefix="/refactor")
# app.include_router(websocket_gateway_router, prefix="/websockets")    #Sockets Code For Iteration 2

@app.get("/")
def health_check():
    return {"status": "ok"}

        
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)