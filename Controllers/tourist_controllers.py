from fastapi import APIRouter, HTTPException
from Models.models import Tourist
from Connections.connections import session
from hashing import Harsher
from sqlalchemy.orm import Session
import secrets
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
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

def create_tourist(db:Session,new_tourist: dict):
    tourist = Tourist.create_tourist_data(new_tourist['name'], new_tourist['email'], new_tourist['phonenumber'], new_tourist['number'], new_tourist['status'])
    try:   
        db.add(tourist)
        db.commit()
        db.refresh(tourist)
        create_welcome_email(new_tourist)
        return {"message":"Tourist created successfully","status":200}
    
    except Exception as e:
        print(f"Error occured: {e}")
        db.rollback()
        return {"message":"An error occured","status":500}
    
def create_welcome_email(tourist_data):
    sender_email = EMAIL
    sender_password = EMAIL_PASSWORD

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    try:
        server.login(sender_email, sender_password)
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        return {"message": "Failed to send email", "status": 500}

    msg = MIMEMultipart('related')
    msg['From'] = sender_email
    msg['To'] = tourist_data['email']
    msg['Subject'] = "Welcome to Agrogetaway!"
    message = f"""<p>Dear {tourist_data['name']},</p>
    <p>We are glad to have you on board. We hope you enjoy your stay with us.</p>
    <p>If you have any questions or require further information, please do not hesitate to contact the support team.</p>
    <p>Best Regards,</p>
    <p>Agrogetaway Team</p>
    """
    msg.attach(MIMEText(message, 'html'))
    server.sendmail(sender_email, tourist_data['email'], msg.as_string())
    server.quit()
   

def get_all_tourists(db:Session):
    tourists = Tourist.get_all_tourist_data(db)
    return tourists

def get_tourist_by_id(db:Session,id):
    tourist = Tourist.get_tourist_data(db, id)
    if tourist:
        return tourist
    else:
        raise HTTPException(status_code=404, detail="Tourist not found")
    
def update_tourist(db:Session,data):
    tourist = Tourist.update_tourist_data(db, data)
    if tourist:
        return tourist
    else:
        raise HTTPException(status_code=404, detail="Tourist not found")
    
def delete_tourist(db:Session,id_data):
    id = id_data['tourist_id']
    tourist = Tourist.delete_tourist_data(db, id)
    if tourist:
        return tourist
    else:
        raise HTTPException(status_code=404, detail="Tourist not found")
    
