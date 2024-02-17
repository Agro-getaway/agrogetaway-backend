from Models.models import Farms,Admin,Farmers
from fastapi import APIRouter, HTTPException
# from Connections.connections import session
from sqlalchemy.orm import Session
from hashing import Harsher
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

def create_farmer(db: Session, new_farmer: dict):
    farm = Farms.create_farm_data(new_farmer['Location'], new_farmer['Details'], new_farmer['Description'], new_farmer['Image_url'], new_farmer['farmer_id'], new_farmer['status'])
    farm_id = farm.id
    try:   
        db.add(farm)
        db.commit()
        db.refresh(farm)

        farmer = Farmers.get_user_by_id(db, new_farmer['farmer_id'])
        full_name = f"{farmer.firstname} {farmer.lastname}"
        # print(full_name)
        send_approval_email_to_admins(db,full_name, new_farmer['Location'], farm_id)
        return {"message":"Farmer created successfully","status":200}
    
    except Exception as e:
        print(f"Error occured: {e}")
        db.rollback()
        return {"message":"An error occured","status":500}

def send_approval_email_to_admins(db: Session, farmer_name, location, farm_id):
    sender_email = EMAIL
    sender_password = EMAIL_PASSWORD
    

    admin_emails = [admin.email for admin in Admin.get_all_admins_email(db)]

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    try:
        server.login(sender_email, sender_password)
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        return {"message": "Failed to send email", "status": 500}


    for admin_email in admin_emails:
        msg = MIMEMultipart('related')
        msg['From'] = sender_email
        msg['To'] = admin_email
        msg['Subject'] = "New Farm Approval Needed"

        approval_link = f"http://frontendsite.com/approve_farm/{farm_id}"  

        html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <p>Dear Admin,</p>
                <br />
                <p>A new farm in {location} has just registered by {farmer_name} and requires your approval.</p>
                <p>Please review the submission and approve or reject as necessary.</p>
                <br />
                <p><a href="{approval_link}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none;">Approve Farmer</a></p>
                <br />
                <p>If you have any questions or require further information, please do not hesitate to contact the support team.</p>
                <br />
                <p>Best Regards,</p>
                <p>Your Team</p>
            </body>
            </html>
            """

        msg.attach(MIMEText(html_body, 'html'))

        try:
            server.send_message(msg)
        except Exception as e:
            print(f"Failed to send email to {admin_email}: {e}")

    server.quit()
    
def approve_farm(db: Session,farm_dict):
    farm_id = farm_dict["farm_id"]
    
    farm = Farms.update_farm_data(db, farm_id,"Approved")
    
    return {"message": "Farm approved successfully", "status": 200}

def reject_farm(db: Session,farm_dict):
    farm_id = farm_dict["farm_id"]
    
    farm = Farms.update_farm_data(db, farm_id,"Rejected")
    return {"message": "Farm rejected successfully", "status": 200}

def get_all_approved_farms(db: Session,):
    farms = Farms.get_approved_farms(db)
    return farms

def pending_farms(db: Session,):
    
    farms = Farms.get_pending_farms(db)
    return farms

def get_pending_farms_count(db: Session,):
    farms = Farms.get_pending_count(db)
    return {"count_value" : farms}

def get_approved_farms_count(db: Session,):
    farms = Farms.get_farm_count(db)
    return {"count_value" : farms}

def get_farm_data_for_farmer(db: Session,farmer_id):
    farms = Farms.get_farm_data(db, farmer_id)
    return farms

def update_farm_stored(db: Session,farm_dict):
    farm = Farms.update_farm_stored_data(db, farm_dict["id"], farm_dict["Location"], farm_dict["Details"], farm_dict["Description"], farm_dict["Image_url"])
    return {"message": "Farm updated successfully", "status": 200}

def delete_farm(db: Session,farm_dict):
    farm_id = farm_dict["farm_id"]
    
    farm = Farms.delete_farm_data(db, farm_id)
    return {"message": "Farm deleted successfully", "status": 200}

def get_farm_by_id(db: Session,farm_id):
    farm = Farms.get_farm_data_by_id(db, farm_id)
    return farm