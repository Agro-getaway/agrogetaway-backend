from fastapi import APIRouter, HTTPException, Depends
import asyncio
from sqlalchemy.orm import Session
from Connections.connections import SessionLocal
from Controllers.user_controllers import (
    create_user, 
    authenticate_user,
    send_password_reset,
    reset_user_password
)
from Controllers.admin_controllers import admin_login

router = APIRouter()
router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def read_root():
    return {"Üsers" : "Hello World"}

# @router.post("/create_user")
# async def create_user_route(new_user: dict):
#     try:
#         user = create_user(new_user)
#         return user
#     except Exception as e:
#         HTTPException(status_code=400, detail=str(e))

@router.post("/create_user")
async def create_user_route(new_user: dict, db: Session = Depends(get_db)):
    try:
        user = create_user(db,new_user)
        return user
    except Exception as e:
        return HTTPException(status_code=400, detail="failed to create user.")

@router.post("/login")
async def login_user_endpoint(user: dict, db: Session = Depends(get_db)):
    email = user.get("email", "")
    password = user.get("password", "")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required.")
    try:
        return await authenticate_user(db,user)  
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Login error: {str(e)}")
        
        raise HTTPException(status_code=400, detail="Invalid Username or Password")
        # return {"message": "Reset link sent to your email address"}
        
@router.post("/request_password_reset")
async def request_password_reset(credentials: dict, db: Session = Depends(get_db)):
    user_email = credentials["email"]
    try:
        send_password_reset(db,user_email)
        return {"message": "Reset link sent to your email address"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="password reset link not sent")
    
@router.post("/reset_password")
async def reset_password_endpoint(token_and_password: dict, db: Session = Depends(get_db)):
    token = token_and_password["token"]
    new_password = token_and_password["new_password"]
    try:
        reset_user_password(db,token, new_password)
        return {"message": "Password reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
