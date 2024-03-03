from fastapi import APIRouter, HTTPException, Depends
from Connections.connections import SessionLocal
from sqlalchemy.orm import Session
from Models.models import UsernameChangeRequest
from Controllers.admin_controllers import (
    create_admin_controller,
    # change_username,
    send_password_reset,
    reset_user_password,
    generate_signup_token,
    get_signup_token_added
)
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def read_root():
    return {"Admins" : "Hello World"}

@router.post("/generate_signup_token")
async def generate_signup_token_for_admin(emailbody: dict):
    email = emailbody["email"]
    admin_id = emailbody["admin_id"]
    try:
        return_data = await generate_signup_token(email,admin_id,"Admin")
        if return_data:
            return {
                "id": return_data["id"],
                "email": email, 
                "token": return_data["token"],
                "status": return_data["status"],
                "time": return_data["time"],
                "added_by": return_data["added_by"],
                }
        else:
            raise HTTPException(status_code=400, detail="Unable to generate token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create_admin")
async def create_admin_route(new_admin: dict,db: Session = Depends(get_db)):
    try:
        admin = await create_admin_controller(db, new_admin)
        return admin
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))

# @router.post("/change_username")
# async def change_username_endpoint(request: UsernameChangeRequest):
#     try:
#         response = change_username(request)
#         return response
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

@router.post("/request_password_reset")
async def request_password_reset(credentials: dict,db: Session = Depends(get_db)):
    email = credentials["email"]
    try:
        send_password_reset(db,email)
        return {"message": "Reset link sent to your email address"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/reset_password")
async def reset_password_endpoint(token_and_password: dict,db: Session = Depends(get_db)):
    token = token_and_password["token"]
    new_password = token_and_password["new_password"]
    try:
        reset_user_password(db,token, new_password)
        return {"message": "Password reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# @router.post("/change_username")
# async def change_username_endpoint(request: UsernameChangeRequest):
#     try:
#         response = change_username(request)
#         return response
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
# @router.put("/approve_farm")
# async def approve_farm_route(farm: dict):
#     try:
#         return approve_farm(db, farm)
#     except Exception as e:
#         return HTTPException(status_code=400, detail=str(e))
    
@router.get("/signup_token/")
async def get_signup_token_by_an_admin(id: int, db: Session = Depends(get_db)):  # Note the async here
    try:
        token = await get_signup_token_added(db, id)  # Correctly awaiting the function
        return token
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))