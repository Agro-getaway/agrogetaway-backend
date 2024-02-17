from fastapi import APIRouter, HTTPException
import asyncio
from Models.models import UsernameChangeRequest
from Controllers.admin_controllers import (
    create_admin_controller,
    change_username,
    send_password_reset,
    reset_user_password
)
router = APIRouter()

@router.get("/")
async def read_root():
    return {"Admins" : "Hello World"}

@router.post("/create_admin")
async def create_admin_route(new_admin: dict):
    try:
        admin = await create_admin_controller(new_admin)
        return admin
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


@router.post("/change_username")
async def change_username_endpoint(request: UsernameChangeRequest):
    try:
        response = change_username(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/request_password_reset")
async def request_password_reset(credentials: dict):
    employee_access = credentials["employee_access"]
    try:
        send_password_reset(employee_access)
        return {"message": "Reset link sent to your email address"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/reset_password")
async def reset_password_endpoint(token_and_password: dict):
    token = token_and_password["token"]
    new_password = token_and_password["new_password"]
    try:
        reset_user_password(token, new_password)
        return {"message": "Password reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/change_username")
async def change_username_endpoint(request: UsernameChangeRequest):
    try:
        response = change_username(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))