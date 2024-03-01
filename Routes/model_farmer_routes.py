from fastapi import APIRouter, HTTPException, Depends
import asyncio
from sqlalchemy.orm import Session
from  Connections.connections import session
from Models.models import AdminSignUpToken
from Connections.connections import SessionLocal
from Controllers.model_farmers_controllers import (
    create_user, 
    send_password_reset,
    reset_user_password
)
from Controllers.admin_controllers import generate_signup_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def read_root():
    return {"Model Farmers" : "Hello World"}

@router.post("/generate_signup_token")
async def generate_signup_token_for_admin(emailbody: dict):
    email = emailbody["email"]
    admin_id = emailbody["admin_id"]
    try:
        token = await generate_signup_token(email,admin_id,"ModelFarmer")
        if token:
            return {"email": email, "token": token}
        else:
            raise HTTPException(status_code=400, detail="Unable to generate token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/model_farmer")
async def create_model_farmer_route(new_model_farmer: dict,db: Session = Depends(get_db)):
    email = new_model_farmer["email"]
    signup_token = new_model_farmer["token"]
    try:
        if not AdminSignUpToken.validate_token(session, email, signup_token):
            raise Exception("Invalid token")
    except Exception as e:
        print(f"Error occurred during token validation: {e}")
        return {"message": str(e), "status": 400} 
    try:
        
        user = create_user(db,new_model_farmer)
        return user 
    
    except Exception as e:
        print(f"Error occurred during model farmer creation: {e}")
        return {"message": "Failed to create model farmer", "status": 400}

        
@router.post("/request_password_reset")
async def request_password_reset(credentials: dict,db: Session = Depends(get_db)):
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
    
