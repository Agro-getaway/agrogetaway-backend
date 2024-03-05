from Models.models import Farms,Admin,FarmImage,ModelFarmers
from fastapi import APIRouter, HTTPException
from Controllers.file_controllers import fetch_farm_images
from fastapi import UploadFile
from typing import List
from sqlalchemy.orm import Session
from hashing import Harsher
from upload import FirebaseUpload
import secrets
import requests
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

def create_farm(db: Session, new_farm: dict, files: List[UploadFile]):
    upload_results = []
    farm = Farms.create_farm_data(new_farm['farmer_id'],new_farm['Location'],"requesting", new_farm['name'], new_farm['method'], new_farm['services'],new_farm['farm_description'],new_farm['method_description'])
    db.add(farm)
    db.commit()
    db.refresh(farm)
    # print("no error here")
    files_to_upload = [('files', (file.filename, file.file.read(), file.content_type)) for file in files]
    upload_url = 'https://ettaka-lyo-backend.onrender.com/uploadImages'
   
    response = requests.post(upload_url, files=files_to_upload)
    
    if response.status_code == 200:
        upload_results = response.json() 
        try:
            for image_url in upload_results:  
                new_farm_image = FarmImage(farm_id=farm.id, image_url=image_url, added_at=datetime.utcnow())
                db.add(new_farm_image)
            
            db.commit()
            db.refresh(farm)
        except Exception as e:
            print(f"Error updating farm image URL: {e}")
            db.rollback()
    else:
        print(f"Failed to upload images")
        
    farmer = ModelFarmers.get_model_farmer_by_id(db, new_farm['farmer_id'])
    full_name = f"{farmer.firstname} {farmer.lastname}"
    send_approval_email_to_admins(db, full_name, new_farm['Location'], farm.id)
    
    return {"message": "Farm created successfully", "status": 200, "farm_id": farm.id, "image_urls": upload_results}

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
                <p> Please login to the admin dashboard to perform the action.</p>
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
    
def approve_farm(db: Session, farm_dict):
    farm_id = farm_dict["farm_id"]
    admin_id = farm_dict["admin_id"]
    farm = Farms.update_farm_data(db, farm_id, "approved", admin_id)
    return {"message": "Farm approved successfully", "status": 200}

def reject_farm(db: Session, farm_dict):
    farm_id = farm_dict["farm_id"]
    admin_id = farm_dict["admin_id"]
    farm = Farms.update_farm_data(db, farm_id, "rejected", admin_id)
    return {"message": "Farm rejected successfully", "status": 200}

def get_all_approved_farms(db: Session,):
    farms = Farms.get_approved_farms(db)
    farms_data = [serialize_farm(farm) for farm in farms]
    return farms_data
def serialize_farm(farm):
    return {
        "id": farm.id,
        "name": farm.name,
        "location": farm.Location,
        "status": farm.status,
        "method": farm.method,
        "services": farm.services,
        "farm_description": farm.farm_description,
        "method_description": farm.method_description,
        "farmer": {
            "id": farm.modelfarmer.id,
            "firstname": farm.modelfarmer.firstname,
            "lastname": farm.modelfarmer.lastname,
            "email": farm.modelfarmer.email,
            "phone_number": farm.modelfarmer.phonenumber, 
            "experience": farm.modelfarmer.experience,
            "background": farm.modelfarmer.background,
            "role": farm.modelfarmer.role
        },
        "images": [image.image_url for image in farm.images]
    }

def pending_farms(db: Session,):
    farms = Farms.get_pending_farms(db)
    farms_data = [serialize_farm(farm) for farm in farms]

    return farms_data

def get_pending_farms_count(db: Session,):
    farms = Farms.get_pending_count(db)
    return {"count_value" : farms}

def get_approved_farms_count(db: Session,):
    farms = Farms.get_farm_count(db)
    return {"count_value" : farms}

def get_farm_data_for_farmer(db: Session, farmer_id):
    farms = Farms.get_farm_data(db, farmer_id)

    for farm in farms:
        farm_id = farm.id
        farm_images = fetch_farm_images(db, farm_id)
        farm.images = farm_images

    return farms

def update_farm_stored(db: Session, farm):
    farm = Farms.update_farm_stored_data(db, farm["id"], farm["location"], farm["name"], farm["method"], farm["services"],farm["farm_description"],farm["method_description"])
                #  update_farm_stored_data(db_session, id, Location, Name, Method, Services, farm_description, method_description):
    return {"message": "Farm updated successfully", "status": 200}

def delete_farm(db: Session,farm):
    farm_id = farm["farm_id"]
    
    farm = Farms.delete_farm_data(db, farm_id)
    return {"message": "Farm deleted successfully", "status": 200}

def get_farm_by_id(db: Session,farm_id):
    farm = Farms.get_farm_data_by_id(db, farm_id)
    farm_data = serialize_farm(farm)
    return farm_data