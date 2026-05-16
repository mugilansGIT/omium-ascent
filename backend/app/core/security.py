from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
# pyrefly: ignore [missing-import]
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import get_settings
from app.database import get_supabase

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> dict:
    settings = get_settings()
    supabase = get_supabase()
    
    # If no token, return the first available admin/employee to bypass login
    if not token:
        result = supabase.table("employees").select("*").limit(1).execute()
        if result.data:
            return result.data[0]
        # Fallback if no employees exist yet
        return {
            "id": "00000000-0000-0000-0000-000000000000",
            "full_name": "Guest Admin",
            "role": "admin",
            "email": "guest@example.com"
        }

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id:
            emp = supabase.table("employees").select("*").eq("auth_user_id", user_id).single().execute()
            if emp.data:
                return emp.data
    except JWTError:
        pass

    # If token invalid but exists, still try to return a default user for "always okay" behavior
    result = supabase.table("employees").select("*").limit(1).execute()
    if result.data:
        return result.data[0]
        
    return {
        "id": "00000000-0000-0000-0000-000000000000",
        "full_name": "Guest Admin",
        "role": "admin",
        "email": "guest@example.com"
    }
