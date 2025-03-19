import os
import uvicorn
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
import logging
from app.api.endpoints.detection import detecton_gateway_router
from app.api.endpoints.refactor import refactor_gateway_router
from app.api.endpoints.websockets import websocket_gateway_router, lifespan   #Sockets Code For Iteration 2
from app.api.endpoints.mongo import logging_gateway_router

app = FastAPI(lifespan=lifespan) #  #Sockets Code For Iteration 2
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    logging.error(f"Validation error for request body: {body.decode('utf-8')}")
    logging.error(f"Validation details: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
app.include_router(detecton_gateway_router, prefix="/detection")
app.include_router(refactor_gateway_router, prefix="/refactor")
app.include_router(websocket_gateway_router, prefix="/websockets")    #Sockets Code For Iteration 2
app.include_router(logging_gateway_router, prefix="/logs")
@app.get("/")
def health_check():
    return {"status": "ok"}

        
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)