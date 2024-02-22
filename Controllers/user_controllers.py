from Models.models import Farmers,Admin
from fastapi import APIRouter, HTTPException
from twilio.rest import Client
from Connections.connections import session
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
import secrets
import requests
import smtplib
from hashing import Harsher
from jose import JWTError, jwt
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage 

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# def  create_user(new_user: dict):

#     existing_user = Farmers.get_user_by_email_or_phone(session, new_user.get('email'), new_user.get('phonenumber'))
#     if existing_user:
#         raise Exception("A user with this email or phone number already exists.")

#     user = Farmers.create_user(new_user['firstname'],new_user['lastname'],new_user['email'],new_user['role'],new_user['phonenumber'],new_user['password'])
#     session.add(user)
#     session.commit()
#     return {"message":"User created successfully","status":200}

def create_user(new_user: dict):
    email = new_user.get('email', None)
    phonenumber = new_user.get('phonenumber', None)

    if not email and not phonenumber:
        raise ValueError("Either email or phone number must be provided.")

    existing_user = Farmers.get_user_by_email_or_phone(session, email, phonenumber)
    if existing_user:
        raise Exception("A user with this email or phone number already exists.")

    user = Farmers.create_user(new_user['firstname'], new_user['lastname'], email, new_user['role'], phonenumber, new_user['password'])
    session.add(user)
    session.commit()
    # send_welcome_email(new_user)
    if email and phonenumber:
        send_welcome_email(new_user) 
        # send_sms(phonenumber)
    elif email:
        send_welcome_email(new_user)
    elif phonenumber:
        # send_sms(phonenumber)
        pass
    return {"message": "User created successfully", "status": 200}

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def send_welcome_email(user_details):
    sender_email = EMAIL
    sender_password = EMAIL_PASSWORD

    reset_token = secrets.token_urlsafe(20)

    # Create the email
    msg = MIMEMultipart('related')
    msg['From'] = sender_email
    msg['To'] = user_details["email"]
    msg['Subject'] = "Welcome to AgroGetaway!"

  
    user_name = user_details["firstname"]# if hasattr(user_details, 'firstname') else user_details.FirstName

    # Make access number flexible for accessnumber, access_no, Accessnumber, AccessNumber
    # access_no = user_details.access_no if hasattr(user_details, 'access_no') else user_details.accessnumber if hasattr(user_details, 'accessnumber') else user_details.AccessNumber if hasattr(user_details, 'AccessNumber') else user_details.Accessnumber

    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <p>Dear {user_name},</p>
            
            It's you we've been waiting for.
            <br />
            <p>Welcome to <strong>AgroGetaway</strong> -The place you belong. The place where FARMING is REDEFINED! </p>
            <p>We are thrilled to welcome you to our community of passionate farmers and farming enthusiasts dedicated to driving the future of agriculture through innovative techniques and top-notch model farms.</p>

            <br />
            <p>At Agrogetaway, we understand the vital role that modern farming plays in ensuring sustainable agriculture and food security. Our platform is designed to connect you with the leading model farms, providing you with a unique opportunity to explore, learn, and implement cutting-edge farming techniques.</p>
            
            <p>Should you have any questions, feel free to reach out to our support team.</p>
            <p>Thank you for choosing AgroGetaway.</p>
            <p>Warm regards,</p>
            <p>The AgroGetaway Team</p>
            <p><i>Note: This is an automated message, please do not reply to this email.</i></p>
        </body>
    </html>
    """

    msg.attach(MIMEText(html_body, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    try:
        server.login(sender_email, sender_password)
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: The username or password you entered is not correct.")
        return

    server.send_message(msg)
    server.quit()

def send_sms(phone_number):
    welcome_message = "Welcome to AgroGetaway! Explore, buy, and sell farm products on our platform. Enjoy your journey into agriculture."
    
    # Checking if phone number starts with '+'
    if not phone_number.startswith('+'):
        # Removing the leading '0' and replace it with '+256'
        phone_number = '+256' + phone_number[1:]

    try:
        message = client.messages.create(
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER,
            body=welcome_message
        )
        print(f"Message sent to {phone_number} with SID: {message.sid}")
    except Exception as e:
        print(f"Error sending message to {phone_number}: {str(e)}")
        raise Exception(f"Error sending message to {phone_number}: {str(e)}")

async def authenticate_user(credentials):
    email_or_phone = credentials['email']
    input_password = credentials['password']

    farmer = Farmers.get_user(session, email_or_phone)

    if farmer and Harsher.verify_password(input_password, farmer.password):
        access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

        access_token = create_access_token(
            data={"sub": farmer .email},
            expires_delta=access_token_expires
        ) 
        farmer_data = {
            "id": farmer.id,
            "email": farmer.email,
            "firstname": farmer.firstname,
            "lastname": farmer.lastname,
            "role": farmer.role
        }
        return {"data:": farmer_data,"access_token": access_token, "token_type": "bearer"}
    
    admin  = Admin.get_admin(session, email_or_phone)

    if admin  and Harsher.verify_password(input_password, admin.password):
        access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

        access_token = create_access_token(
            data={"sub": admin.email},
            expires_delta=access_token_expires
        ) 
        admin_data = {
            "id": admin.id,
            "email": admin.email,
            "firstname": admin.firstname,
            "lastname": admin.lastname,
            "role": admin.role
        }
        return {"data:": admin_data,"access_token": access_token, "token_type": "bearer"}
    else:
        raise Exception("Invalid Username or Password")
    
def send_password_reset(user_email):
    user = Farmers.get_user_by_email_or_phone(session, user_email, None)
    if not user:
        raise Exception("User not found")

    reset_token = secrets.token_urlsafe(20)
    payload = {"sub": user.email, "reset_token": reset_token}
    access_token = create_access_token(payload)
    reset_link = f"http://localhost:8000/reset_password?token={access_token}"
    send_reset_email(user.email, reset_link)

def send_reset_email(email, reset_link):
    sender_email = EMAIL
    sender_password = EMAIL_PASSWORD

    # Create the email
    msg = MIMEMultipart('related')
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Password Reset Request"

    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <p>Dear User,</p>
            <p>We received a request to reset your password. If you did not make this request, please ignore this email.</p>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_link}">Reset Password</a>
            <p>If you're having trouble clicking the link, copy and paste the URL below into your web browser:</p>
            <p>{reset_link}</p>
            <p>If you have any questions, feel free to reach out to our support team.</p>
            <p>Thank you for choosing AgroGetaway.</p>
            <p>Warm regards,</p>
            <p>The AgroGetaway Team</p>
            <p><i>Note: This is an automated message, please do not reply to this email.</i></p>
        </body>
    </html>
    """

    msg.attach(MIMEText(html_body, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()

def reset_user_password(token, new_password):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise Exception("Invalid token")
    except JWTError:
        raise Exception("Invalid token")

    user = Farmers.get_user_by_email_or_phone(session, email, None)
    if not user:
        raise Exception("User not found")

    user.update_password(new_password)
    try: 
        session.commit()
        print("Password updated and committed")  
    except Exception as e:
        print(f"Error in commit: {e}")
        session.rollback()
        raise

    return True

def get_user_by_id(id):
    user = Farmers.get_user_by_id(session, id)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")