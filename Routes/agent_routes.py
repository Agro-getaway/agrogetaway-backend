from fastapi import APIRouter, HTTPException
from Controllers.admin_controllers import (
    generate_signup_token
)
from Controllers.agent_controllers import create_agent_controller

router = APIRouter()

@router.get("/")
async def read_root():
    return {"Agents" : "Hello World"}

@router.post("/generate_signup_token")
async def generate_signup_token_for_admin(emailbody: dict):
    email = emailbody["email"]
    try:
        token = await generate_signup_token(email,"Agent")
        if token:
            return {"email": email, "token": token}
        else:
            raise HTTPException(status_code=400, detail="Unable to generate token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_agent")
async def create_agent_route(new_agent: dict):
    try:
        admin = await create_agent_controller(new_agent)
        return admin
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
