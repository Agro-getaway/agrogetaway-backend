from Models.models import Community, CommunityFollowers,CommunityMessages,Farmers
from fastapi import APIRouter, HTTPException
from Controllers.file_controllers import fetch_farm_images
from fastapi import UploadFile
from typing import List
from sqlalchemy.orm import Session
from hashing import Harsher
from upload import FirebaseUpload
import secrets
import smtplib
import requests
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def create_community(db: Session, community_data):
    file_to_upload: UploadFile = community_data["file"]
    file_content = file_to_upload.file.read()
    files = {'file': (file_to_upload.filename, file_content, file_to_upload.content_type)}
    upload_url = 'https://ettaka-lyo-backend.onrender.com/api/users/upload-image'
    response = requests.post(upload_url, files=files)
    if response.status_code == 200:
        upload_results = response.json() 
        image_url = upload_results.get("data", {}).get("imageUrl", "")
    db_community = Community(name=community_data["name"], profile_picture=image_url, created_by=community_data["created_by"])
    db.add(db_community)
    db.commit()
    db.refresh(db_community)

    owner = CommunityFollowers.create_community_owner(db, db_community.id, community_data["created_by"])
    db.add(owner)
    db.commit()
    db.refresh(owner)
    return {"message": "Community created successfully", "community_id": db_community.id}

def add_community_follower(db: Session, community_id: int, follower_id: int):
    db_follower = CommunityFollowers(community_id=community_id, follower_id=follower_id, role="follower")
    db.add(db_follower)
    db.commit()
    db.refresh(db_follower)
    return db_follower

def create_community_message(db: Session, community_id: int, sender_id: int, message: str):
    db_message = CommunityMessages(community_id=community_id, sender_id=sender_id, message=message)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def community_messages_with_sender_info(db_session: Session, community_id: int):
    messages = db_session.query(
        CommunityMessages,
        Farmers.firstname,
        Farmers.lastname,
        Farmers.email
    ).join(
        Farmers, Farmers.id == CommunityMessages.sender_id
    ).filter(
        CommunityMessages.community_id == community_id
    ).all()

    return [
        {
            "message_id": message.CommunityMessages.id,
            "user_id": message.CommunityMessages.sender_id,
            "message": message.CommunityMessages.message,
            "sent_at": message.CommunityMessages.sent_at,
            "sender_firstname": message.firstname,
            "sender_lastname": message.lastname,
            "sender_email": message.email
        }
        for message in messages
    ]

def get_communities_for_user_controller(db: Session, user_id: int):
    communities = db.query(Community, Farmers).join(CommunityFollowers, CommunityFollowers.community_id == Community.id).join(Farmers, Farmers.id == Community.created_by).filter(CommunityFollowers.follower_id == user_id).all()
    
    return [
        {
            "community_id": community.id,
            "name": community.name,
            "profile_picture": community.profile_picture,
            "created_by": {
                "id": creator.id,
                "name": creator.firstname + " " + creator.lastname, # Assuming you have firstname and lastname fields
                "email": creator.email
            },
            "created_at": community.created_at,
        }
        for community, creator in communities
    ]

def get_communities_not_for_user_controller(db: Session, user_id: int):
    user_communities_subquery = db.query(CommunityFollowers.community_id).filter(CommunityFollowers.follower_id == user_id).subquery()
    
    communities = db.query(Community, Farmers).join(Farmers, Farmers.id == Community.created_by).filter(~Community.id.in_(user_communities_subquery)).all()
    
    return [
        {
            "community_id": community.id,
            "name": community.name,
            "profile_picture": community.profile_picture,
            "created_by": {
                "id": creator.id,
                "name": creator.firstname + " " + creator.lastname,
                "email": creator.email
            },
            "created_at": community.created_at,
        }
        for community, creator in communities
    ]