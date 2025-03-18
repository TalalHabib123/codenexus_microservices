from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.controllers.githubOauth import GithubAuthController

router = APIRouter(prefix="/auth", tags=["auth"])

# Request model for exchanging GitHub code
class GitHubCodeExchange(BaseModel):
    code: str

@router.get("/github/login")
async def github_login():
    """Provides GitHub OAuth URL for frontend to redirect to"""
    try:
        return {"authorization_url": GithubAuthController.get_github_oauth_url()}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/github/exchange")
async def github_exchange_code(code_exchange: GitHubCodeExchange):
    """Exchange GitHub code for access token"""
    try:
        response = GithubAuthController.exchange_github_code(code_exchange.code)
        if "error" in response:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response["error"])
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
