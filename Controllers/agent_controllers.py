from Models.models import Agents
from fastapi import APIRouter, HTTPException
from Connections.token_and_keys import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    EMAIL,
    EMAIL_PASSWORD,
    ACCOUNT_SID,
    AUTH_TOKEN,
    TWILIO_PHONE_NUMBER

)

def create_agent(new_agent: dict):
    try:
        agent = Agents.create_agent(new_agent['firstname'], new_agent['lastname'], new_agent['email'], new_agent['password'])
        return {"message": "Agent created successfully", "status": 200}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

