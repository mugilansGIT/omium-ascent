from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.database import get_supabase
from app.core.security import (
    verify_password, get_password_hash,
    create_access_token, get_current_user
)

router = APIRouter()


class RegisterRequest(BaseModel):
    employee_code: str
    full_name: str
    email: str
    password: str
    role: str
    join_date: str


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    supabase = get_supabase()

    emp = supabase.table("employees").select("*").eq(
        "email", form_data.username
    ).single().execute()

    if not emp.data:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify via Supabase auth
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": emp.data["auth_user_id"]})
    return {"access_token": token, "token_type": "bearer", "employee": emp.data}


@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    return current_user
