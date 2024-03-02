from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from Models.models import AdminSignUpToken
from  Connections.connections import session
from Connections.connections import SessionLocal
from Controllers.admin_controllers import (
    generate_signup_token,
    send_signup_token_email
)
from Controllers.agent_controllers import create_agent_controller, get_agent

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
async def read_root():
    return {"Agents": "Hello World"}


@router.post("/generate_signup_token")
async def generate_signup_token_for_admin(emailbody: dict):
    email = emailbody["email"]
    admin_id = emailbody["admin_id"]
    try:
        token_info = await generate_signup_token(email, admin_id, "Agent")
        if token_info:
            token = token_info['token'] 
            send_signup_token_email(email, token, "agent") 
            return token_info
        else:
            raise HTTPException(status_code=400, detail="Unable to generate token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create_agent")
async def create_agent_route(new_agent: dict, db: Session = Depends(get_db)):

    email = new_agent["email"]
    signup_token = new_agent["token"]
    try:
        if not AdminSignUpToken.validate_token(session, email, signup_token):
            raise Exception("Invalid token")
    except Exception as e:
        print(f"Error occurred during token validation: {e}")
        return {"message": str(e), "status": 400} 
    
    try:
        admin = await create_agent_controller(db, new_agent)
        return admin
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


@router.get("/get_agent_by_email/")
async def get_agent_by_email(email: str, db: Session = Depends(get_db)):
    try:
        agent = get_agent(db, email)
        return agent
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
