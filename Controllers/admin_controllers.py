from Models.models import Admin, UsernameChangeRequest, AdminSignUpToken
from fastapi import APIRouter, HTTPException
from Connections.connections import session
import secrets
import random
import smtplib
from hashing import Harsher
from jose import JWTError, jwt
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from Controllers.user_controllers import (
    create_access_token
    )
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

async def generate_signup_token(email):
    try: 
        token_info = AdminSignUpToken.create_token(session, email) 
        if token_info:
            token = token_info['token'] 
            send_signup_token_email(email, token) 
            return token 
        else:
            raise Exception("Token not created")
    except Exception as e:
        print(f"Error occurred: {e}")
        return False

# an email to the user with the token
def send_signup_token_email(email, token):
    sender_email = EMAIL
    sender_password = EMAIL_PASSWORD

    msg = MIMEMultipart('related')
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Admin Signup Email!"

    html_body = f"""
        <html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <p>Dear Admin,</p>
    <br /><br />
    Welcome to AgroGetaway! Please use the following token to complete your signup process:
    <br />
    <p><strong>{token}</strong></p>
    <p>If you have any questions or require assistance, our support team is always here to help.</p>
    <p>Thank you for stepping into this vital role within the AgroGetaway community. Together, we'll drive the future of farming.</p>
    <p>Warm regards,</p>
    <p>The AgroGetaway Team</p>
    <p><i>Note: This is an automated message, please do not reply to this email.</i></p>
</body>
</html>
    """

    msg.attach(MIMEText(html_body, 'html'))

    # firebase_url = 'https://firebasestorage.googleapis.com/v0/b/bfamproject-80d95.appspot.com/o/prod%2Fproducts%2F1705940735027_gen_visual.jpeg?alt=media&token=de7a990b-2238-455f-a6d2-1f0ba71f55d2'

    # response = requests.get(firebase_url)
    # if response.status_code == 200:
    #     img_data = response.content
    #     img = MIMEImage(img_data)
    #     img.add_header('Content-ID', '<company_logo>')
    #     msg.attach(img)
    # else:
    #     print("Failed to retrieve image from Firebase")

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    try:
        server.login(sender_email, sender_password)
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: The username or password you entered is not correct.")
        return

    server.send_message(msg)
    server.quit()
       
async def create_admin_controller(new_admin: dict):
    email = new_admin["email"]
    signup_token = new_admin["token"]

    try:
        if not AdminSignUpToken.validate_token(session, email, signup_token):
            raise Exception("Invalid token")
    except Exception as e:
        print(f"Error occurred during token validation: {e}")
        return {"message": str(e), "status": 400}  

    try:
        Admin.create_admin(session, new_admin["firstname"], new_admin["lastname"], email, new_admin["phone_number"], new_admin["password"])
        print("Token status updated")
        send_welcome_email(new_admin)
        return {"message": "Admin created successfully", "status": 200}
    except Exception as e:
        print(f"Error occurred during admin creation: {e}")

        return {"message": str(e), "status": 400}  

# async def create_password(length=4):
#     password = f"Changemenow@{random.randint(0, 9999):04d}"
#     return password

def send_welcome_email(user_details):
    sender_email = EMAIL
    sender_password = EMAIL_PASSWORD

    # Create the email
    msg = MIMEMultipart('related')
    msg['From'] = sender_email
    msg['To'] = user_details["email"]
    msg['Subject'] = "Welcome to AgroGetaway!"
    print(f"I am sending to {user_details['email']}")

    html_body = f"""
        <html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <p>Dear {user_details["firstname"]},</p>
    <br /><br />
    Welcome to the forefront of innovation in agriculture.
    <br />
    <p>Welcome to <strong>AgroGetaway</strong> - where we're redefining farming together. As a new administrator, your role is pivotal in shaping the future of sustainable agriculture and enhancing our community's experience.</p>
    <p>We're excited to have you join us in our mission to transform the landscape of farming through technology, knowledge sharing, and community engagement. Your expertise and leadership will be invaluable as we work together to support our network of farmers and enthusiasts.</p>

    <p>If you have any questions or require assistance, our support team is always here to help.</p>
    <p>Thank you for stepping into this vital role within the AgroGetaway community. Together, we'll drive the future of farming.</p>
    <p>Warm regards,</p>
    <p>The AgroGetaway Team</p>
    <p><i>Note: This is an automated message, please do not reply to this email.</i></p>
</body>
</html>
    """

    msg.attach(MIMEText(html_body, 'html'))

    # firebase_url = 'https://firebasestorage.googleapis.com/v0/b/bfamproject-80d95.appspot.com/o/prod%2Fproducts%2F1705940735027_gen_visual.jpeg?alt=media&token=de7a990b-2238-455f-a6d2-1f0ba71f55d2'

    # response = requests.get(firebase_url)
    # if response.status_code == 200:
    #     img_data = response.content
    #     img = MIMEImage(img_data)
    #     img.add_header('Content-ID', '<company_logo>')
    #     msg.attach(img)
    # else:
    #     print("Failed to retrieve image from Firebase")

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    try:
        server.login(sender_email, sender_password)
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: The username or password you entered is not correct.")
        return

    server.send_message(msg)
    server.quit()

def reset_admin_password(token, new_password):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        employee_access = payload.get("sub")
        if employee_access is None:
            raise Exception("Invalid token")
    except JWTError:
        raise Exception("Invalid token")

    admin = session.query(Admin).filter(Admin.employee_access == employee_access).first()
    if not admin:
        session.rollback()
        raise Exception("Admin not found")

    admin.update_password(new_password)
    try:
        session.commit()
        print("Password updated and committed")  
    except Exception as e:
        print(f"Error in commit: {e}")
        session.rollback()
        raise

    return True

# def change_username(request):
#     admin = session.query(Admin).filter(Admin.employee_access == request.current_username).first()

#     if not admin:
#         raise Exception("Admin not found")
    
#     new_employee_access = f"{request.new_username_prefix}@Agrogetaway"

#     if Admin.username_exists(session, new_employee_access):
#         raise Exception("This Employee access is already taken")
    
#     admin.employee_access = new_employee_access

#     try:
#         session.commit()
#         return {"message":"Employee access number updated successfully"}
#     except Exception as e:
#         print(f"Error in commit: {e}")
#         session.rollback()
#         raise

def send_password_reset(employee_access):
    user = session.query(Admin).filter(Admin.employee_access == employee_access).first()

    if not user:
        session.rollback()
        raise Exception("User not found")

    reset_token = create_access_token(data={"sub": employee_access}, expires_delta=timedelta(hours=1))
    reset_link = f"https://frontend-link.com/reset_password?token={reset_token}"
    send_reset_email(user.email, reset_link)
    return True

def send_reset_email(email: str, reset_link: str):
    sender_email = EMAIL
    sender_password = EMAIL_PASSWORD
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Agrogetaway Password Reset"

    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <!-- <center><img src="cid:company_logo" alt="Company Logo" style="width: 100px; height: auto; margin-bottom: 20px;"></center> -->
            <!-- <p>Dear ,<br><br> -->
            Password Reset <br><br>
             Please click on the link to reset your password:
            {reset_link}<br><br>
            The Agrogetaway Team<br><br>
            Note: This is an automated message. Please do not reply to this email.</p>
        </body>
    </html>
    """

    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()

def reset_user_password(token, new_password):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        employee_access = payload.get("sub")
        if employee_access is None:
            raise Exception("Invalid token")
    except JWTError:
        raise Exception("Invalid token")

    admin = session.query(Admin).filter(Admin.employee_access == employee_access).first()
    if not admin:
        session.rollback()
        raise Exception("Admin not found")

    admin.update_password(new_password)
    try:
        session.commit()
        print("Password updated and committed")  
    except Exception as e:
        print(f"Error in commit: {e}")
        session.rollback()
        raise

    return True

async def admin_login(credentials):
    employee_access = credentials["email"]
    input_password = credentials["password"]

    admin = Admin.get_admin(session, employee_access)
    
    if admin and Harsher.verify_password(input_password, admin.password):
        access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
        access_token = create_access_token(
            data={"sub": admin.employee_access}, 
            expires_delta=access_token_expires
        )
        admin_data = {
            "id": admin.id,
            "name": admin.firstname,
            "employee_access": admin.employee_access,
            "email": admin.email,
            "role": "admin"
        }
        return {"data": admin_data,"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid password.")
# else:
#     raise HTTPException(status_code=404, detail="Admin not found.")
    


