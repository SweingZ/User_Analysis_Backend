from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(data: dict):
    """Creates a JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    """Validates a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
async def admin_verification(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if not is_admin(payload):
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
    return payload

def is_admin(payload: dict) -> bool:
    role = payload.get("role")
    return role == "ADMIN"

async def super_admin_verification(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if not is_super_admin(payload):
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
    return payload

def is_super_admin(payload: dict) -> bool:
    role = payload.get("role")
    return role == "SUPERADMIN"


