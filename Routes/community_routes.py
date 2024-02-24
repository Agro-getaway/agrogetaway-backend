from fastapi import Depends,APIRouter, HTTPException, Depends, HTTPException, UploadFile, File, Form
from Connections.connections import SessionLocal
from sqlalchemy.orm import Session
from typing import List

from Controllers.community_controllers import (
    create_community,
    add_community_follower,
    create_community_message,
    community_messages_with_sender_info
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
    return {"Community" : "Hello World"}

@router.post("/create-communities/")
def create_community_route(community: dict, db: Session = Depends(get_db)):
    return create_community(db = db, community_data = community)

@router.post("/communities/followers/")
def add_follower_to_community(follower_data: dict, db: Session = Depends(get_db)):
    return add_community_follower(db=db, community_id=follower_data["community_id"], follower_id=follower_data["follower_id"])

@router.post("/communities/messages/")
def create_message_in_community(community_message: dict, db: Session = Depends(get_db)):
    return create_community_message(db=db, community_id=community_message["community_id"], sender_id=community_message["sender_id"], message=community_message["message"])

@router.get("/communities/messages/")
def read_community_messages(community_id: int, db: Session = Depends(get_db)):
    messages = community_messages_with_sender_info(db_session=db, community_id=community_id)
    return messages