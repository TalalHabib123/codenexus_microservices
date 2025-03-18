from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse, RedirectResponse

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

# Define a model for the code exchange request
class GitHubCodeExchange(BaseModel):
    code: str

@router.get("/github/login")
async def github_login():
    """Provides GitHub OAuth URL for frontend to redirect to"""
    client_id = os.getenv("CLIENT_ID")
    redirect_uri = os.getenv("REDIRECT_URI")  
    scope = "user:email,repo"
    print(f"Redirecting to GitHub OAuth with client_id: {client_id}, redirect_uri: {redirect_uri}, scope: {scope}")
    
    github_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"
    return {"authorization_url": github_url}

@router.post("/github/exchange")
async def github_exchange_code(code_exchange: GitHubCodeExchange):
    """Exchange the code for an access token - called by frontend"""
    try:
        # Exchange code for access token
        response = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": os.getenv("CLIENT_ID"),
                "client_secret": os.getenv("CLIENT_SECRET"),
                "code": code_exchange.code
            }
        )
        
        token_data = response.json()
        print(code_exchange)
        print(token_data)
        access_token = token_data.get("access_token")
        
        if not access_token:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Failed to obtain access token", "github_response": token_data}
            )
        
        # Get user info from GitHub
        user_info = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        
        return {
            "msg": "GitHub OAuth success",
            "access_token": access_token,
            "user": user_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))