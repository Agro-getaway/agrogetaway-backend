from Models.models import Agents,AdminSignUpToken
from fastapi import APIRouter, HTTPException
from Connections.connections import session
from hashing import Harsher
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
# from Controllers.user_controllers import (
# generate_signup_token
# )
from Controllers.admin_controllers import send_signup_token_email
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

async def create_agent_controller(new_agent: dict):
    email = new_agent["email"]
    signup_token = new_agent["token"]

    try:
        if not AdminSignUpToken.validate_token(session, email, signup_token):
            raise Exception("Invalid token")
        
    except Exception as e:
        print(f"Error occurred during token validation: {e}")
        return {"message": str(e), "status": 400}  

    try:
        Agents.create_agent(new_agent["firstname"], new_agent["lastname"], email, new_agent["phone_number"], new_agent["password"], status="requesting")
        print("Token status updated")
        send_welcome_email(new_agent)
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

