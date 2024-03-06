from fastapi import APIRouter, HTTPException
from fastapi import UploadFile
from Models.models import Event,Admin
import requests
from sqlalchemy.orm import Session
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
from Connections.token_and_keys import (
    EMAIL,
    EMAIL_PASSWORD,
)

def create_event(db : Session, event_data):
    # print(event_data)
    try:
        event_data['added_by'] = int(event_data['added_by'])
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid added_by. Must be an integer.")
    
    file_to_upload: UploadFile = event_data["file"]
    file_content = file_to_upload.file.read()
    files = {'file': (file_to_upload.filename, file_content, file_to_upload.content_type)}
    upload_url = 'https://ettaka-lyo-backend.onrender.com/api/users/upload-image'
    response = requests.post(upload_url, files=files)
    if response.status_code == 200:
        upload_results = response.json() 
        image_url = upload_results.get("data", {}).get("imageUrl", "")
    new_event_data = {
        "name": event_data["name"],
        "description": event_data["description"],
        "start_time": event_data["start_time"],
        "end_time": event_data["end_time"],
        "image_url": image_url,
        "added_by" : event_data["added_by"]
    }
    db_event = Event(**new_event_data)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    send_event_approval_email_to_admins(db, db_event.name)
    return {"message": "Event created successfully", "status": 200, "event_data": new_event_data}

def send_event_approval_email_to_admins(db: Session, event_name):
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
        msg['Subject'] = "New Event Approval Needed"

        # approval_link = f"http://frontendsite.com/approve_farm/{farm_id}"  

        html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <p>Dear Admin,</p>
                <br />
                <p>A new event, {event_name}, has just registered and requires your approval.</p>
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
    
def get_all_events(db : Session):
    return db.query(Event).all()

def get_events_for_auser(db: Session, id ):
    return Event.get_event_for_a_user(db, id)

def get_events_for_farm(db : Session, farm_id):
    return db.query(Event).filter(Event.farm_id == farm_id).all()

def update_event(db : Session, event_id, update_data):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if db_event:
        for key, value in update_data.items():
            setattr(db_event, key, value)
        db.commit()
        return db_event
    else:
        return None
    
def approve_event(db : Session, event_id, admin_id):
    try: 
        event = Event.approving_an_event(db, event_id,admin_id)
        return {"message": "Event approved successfully", "status": 200, 'data': event}
    except Exception as e:
        return {"message": str(e), "status": 400}
    
def get_pending_events(db : Session):
    try:
        events = Event.displaying_pending_events(db)
        return events
    
    except Exception as e:
        return {"message": str(e), "status": 400}
    
def get_pending_events_count(db : Session):
    try:
        events = Event.get_pending_count(db)
        return {"count_value" : events}
    except Exception as e:
        return {"message": str(e), "status": 400}
    
def get_approved_events(db : Session):
    try:
        events = Event.displaying_approved_events(db)
        return events
    except Exception as e:
        return {"message": str(e), "status": 400}
    