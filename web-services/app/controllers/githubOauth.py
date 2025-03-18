import os
import requests
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from app.models.auth import User

# Load environment variables
load_dotenv()

# Setup encryption
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("Missing ENCRYPTION_KEY in environment variables")

fernet = Fernet(ENCRYPTION_KEY.encode())

class GithubAuthController:
    
    @staticmethod
    def get_github_oauth_url():
        """Returns GitHub OAuth URL for frontend to redirect to"""
        client_id = os.getenv("CLIENT_ID")
        redirect_uri = os.getenv("REDIRECT_URI")
        scope = "user:email,repo"

        if not client_id or not redirect_uri:
            raise ValueError("CLIENT_ID or REDIRECT_URI missing from environment variables")

        return f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"

    @staticmethod
    def exchange_github_code(code: str):
        """Exchanges GitHub code for an access token and manages user data"""
        response = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": os.getenv("CLIENT_ID"),
                "client_secret": os.getenv("CLIENT_SECRET"),
                "code": code
            }
        )
        
        token_data = response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return {"error": "Failed to obtain access token", "github_response": token_data}

        # Fetch user data from GitHub
        user_info = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        github_id = user_info.get("id")
        username = user_info.get("login")
        email = user_info.get("email")
        split_name = user_info.get("name", "").split()
        first_name = split_name[0] if len(split_name) > 0 else None
        last_name = split_name[1] if len(split_name) > 1 else None
        encrypted_access_token = fernet.encrypt(access_token.encode()).decode()

        # Check if user exists
        existing_user = User.objects(github_id=github_id).first()
        new_user = None
        if existing_user:
            existing_user.encrypted_access_token = encrypted_access_token
            existing_user.save()
        else:
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
            "new_user": new_user.to_dict() if new_user else existing_user.to_dict()
        }
