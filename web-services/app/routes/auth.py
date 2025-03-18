from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse, RedirectResponse
from cryptography.fernet import Fernet
from app.models.auth import User


# Load environment variables
load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())  # Generate key if not set
print(f"Using encryption key: {ENCRYPTION_KEY}")
fernet = Fernet(ENCRYPTION_KEY.encode())

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
        print(f"Token data received: {token_data}")
        access_token = token_data.get("access_token") if "access_token" in token_data else None
        print(f"Access token: {access_token}")
        
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
        print("User info received from GitHub:", user_info)
        github_id = user_info.get("id")
        username = user_info.get("login")
        email = user_info.get("email") if "email" in user_info else None
        split_name = user_info.get("name", "").split()
        first_name = split_name[0] if len(split_name) > 0 else None
        last_name = split_name[1] if len(split_name) > 1 else None
        encrypted_access_token = fernet.encrypt(access_token.encode()).decode()
        
        existing_user = User.objects(github_id=github_id).first()
        
        if existing_user:
            # Update existing user with new access token
            existing_user.encrypted_access_token = encrypted_access_token
            existing_user.save()
        else:
            # Create a new user
            new_user = User(
                username=username,
                email=email,
                github_id=github_id,
                encrypted_access_token=encrypted_access_token,
                first_name=first_name,
                last_name=last_name
            )
            new_user.save()
        
        return {
            "msg": "GitHub OAuth success",
            "access_token": access_token,
            "user": user_info, 
        }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
