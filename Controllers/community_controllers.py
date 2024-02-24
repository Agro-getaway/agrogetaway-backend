from Models.models import Community, CommunityFollowers,CommunityMessages
from fastapi import APIRouter, HTTPException
from Controllers.file_controllers import fetch_farm_images
from fastapi import UploadFile
from typing import List
from sqlalchemy.orm import Session
from hashing import Harsher
from upload import FirebaseUpload
import secrets
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def create_community(db: Session, community_data):
    db_community = Community(name=community_data["name"], profile_picture=community_data["profile_picture"], created_by=community_data["created_by"])
    db.add(db_community)
    db.commit()
    db.refresh(db_community)
    return db_community

def add_community_follower(db: Session, community_id: int, follower_id: int, role: str):
    db_follower = CommunityFollowers(community_id=community_id, follower_id=follower_id, role=role)
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
