from fastapi import APIRouter, HTTPException
from Models.models import Booking, Farms
from Connections.connections import session
from sqlalchemy.orm import Session
from Controllers.tourist_controllers import get_tourist_by_id
from Controllers.user_controllers import get_user_by_id
from apscheduler.schedulers.background import BackgroundScheduler
import secrets
import smtplib
from Connections.token_and_keys import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    EMAIL,
    EMAIL_PASSWORD,
    ACCOUNT_SID,
    AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
)
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def create_booking_controller(db:Session,new_booking: dict):
    booking = Booking.create_booking(
        new_booking["farm_id"],
        new_booking["tourist_id"],
        new_booking["status"],
        new_booking["start_datetime"],
        new_booking["end_datetime"],
        new_booking["payment_status"],
        new_booking["payment_amount"],
    )
    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)
        send_booking_email(new_booking)
        return {"message": "Booking created successfully", "status": 200}

    except Exception as e:
        print(f"Error occured: {e}")
        db.rollback()
        return {"message": "An error occured", "status": 500}


def send_booking_email(booking_data):
    sender_email = EMAIL
    sender_password = EMAIL_PASSWORD

    farm_id = booking_data["farm_id"]
    approval_link = f"http://frontendsite.com/approve_booking/{farm_id}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    try:
        server.login(sender_email, sender_password)
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        return {"message": "Failed to send email", "status": 500}

    tourist = get_tourist_by_id(booking_data["tourist_id"])
    if not tourist:
        return {"message": "Tourist not found", "status": 404}
    tourist_name = tourist.Name
    tourist_email = tourist.Email

    farm = Farms.get_farm_data_by_id(session, farm_id)
    if not farm:
        return {"message": "Farm not found", "status": 404}
    farmer_id = farm.farmer_id
    farmer = get_user_by_id(farmer_id)
    if not farmer:
        return {"message": "Farmer not found", "status": 404}
    farm_name = f"{farmer.firstname} {farmer.lastname}"  # Assuming farmer object has attributes firstname and lastname
    farm_email = farmer.email  # Assuming farmer object has attribute email

    # Send email to the tourist
    msg_to_tourist = MIMEMultipart("related")
    msg_to_tourist["From"] = sender_email
    msg_to_tourist["To"] = tourist_email
    msg_to_tourist["Subject"] = "Booking Request Sent"
    message_to_tourist = f"""<p>Dear {tourist_name},</p>
    <p>Your booking request has been sent. You will be contacted by the farm owner, {farm_name}, shortly.</p>
    <p>If you have any questions or require further information, please do not hesitate to contact the support team.</p>
    <p>Best Regards,</p>
    <p>Agrogetaway Team</p>
    """
    msg_to_tourist.attach(MIMEText(message_to_tourist, "html"))
    server.send_message(msg_to_tourist)

    # Send email to the farmer
    msg_to_farmer = MIMEMultipart("related")
    msg_to_farmer["From"] = sender_email
    msg_to_farmer["To"] = farm_email
    msg_to_farmer["Subject"] = "New Booking Request"
    message_to_farmer = f"""<p>Dear {farm_name},</p>
    <p>A booking has been requested. 
    <p>Please review the submission and approve or reject as necessary.</p>
    <br />
    <p><a href="{approval_link}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none;">Approve Booking</a></p>
    <br />
    Please contact the tourist, {tourist_name}, shortly.</p>
    <p>If you have any questions or require further information, please do not hesitate to contact the support team.</p>
    <p>Best Regards,</p>
    <p>Agrogetaway Team</p>
    """
    msg_to_farmer.attach(MIMEText(message_to_farmer, "html"))
    server.send_message(msg_to_farmer)

    server.quit()
    return {"message": "Emails sent successfully", "status": 200}


def approve_booking_controller(booking_dict):
    booking_id = booking_dict["booking_id"]
    booking = Booking.update_booking_data(session, booking_id,"approved")
    return {"message": "Booking approved successfully", "status": 200}

def reject_booking_controller(booking_dict):

    booking_id = booking_dict["booking_id"]
    booking = Booking.update_booking_data(session, booking_id, "rejected")
    return {"message": "Booking rejected successfully", "status": 200}


# getting appoinments for a specific farmer
def get_booking_for_farmer(db:Session,farmer_id):
    try:
        farms = (
            db.query(Farms).filter(Farms.farmer_id == farmer_id).all()
        )
        if not farms:
            db.rollback()
            raise HTTPException(status_code=404, detail="Farmer has no farms")

        farm_ids = [farm.id for farm in farms]
        bookings = Booking.get_bookings_for_farm(db, farm_ids)
        return bookings
    except Exception as e:
        db.rollback()
        print(f"Error while fetching appointments for farmer {farmer_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    ## getting booking by status


def get_booking_for_farmer_by_status(db:Session,farmer_id, status):
    try:
        farms = (
            db.query(Farms).filter(Farms.farmer_id == farmer_id).all()
        )
        if not farms:
            db.rollback()
            raise HTTPException(status_code=404, detail="Farmer has no farms")

        farm_ids = [farm.id for farm in farms]
        pending_bookings = (
            db.query(Booking)
            .filter(Booking.Farmid.in_(farm_ids), Booking.status == status)
            .all()
        )
        return pending_bookings
    except Exception as e:
        db.rollback()
        print(f"Error while fetching pending appointments for farmer {farmer_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def accept_booking_controller(db:Session,booking_id: int):
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return {"message": "Booking not found", "status": 404}

        booking.status = "Accepted"
        db.commit()

        return {"message": "Booking accepted successfully", "status": 200}
    except Exception as e:
        db.rollback()
        print(f"Error accepting booking: {e}")
        return {"message": "An error occurred", "status": 500}


def get_upcoming_bookings():
    now = datetime.utcnow()
    reminder_threshold = now + timedelta(days=1)

    upcoming_bookings = (
        session.query(Booking)
        .filter(
            Booking.start_datetime >= now,
            Booking.start_datetime <= reminder_threshold,
            Booking.status == "Accepted",
        )
        .all()
    )

    return upcoming_bookings


def send_reminder(booking):
    # send_email_to_tourist(booking.tourist_id, booking.start_datetime)
    # send_email_to_farmer(booking.farm_id, booking.start_datetime)
    pass


def start_reminder_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        get_upcoming_bookings_and_send_reminders, "interval", hours=24
    )  # Run daily
    scheduler.start()


def get_upcoming_bookings_and_send_reminders():
    bookings = get_upcoming_bookings()
    for booking in bookings:
        send_reminder(booking)


def cancel_booking(booking_id, db_session):
    booking = db_session.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        db_session.rollback()
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.is_cancelled = True
    booking.status = "Cancelled"

    # booking.cancellation_fee = calculate_cancellation_fee(booking)
    # db_session.commit()
    # send_cancellation_notifications(booking)


def reschedule_booking(booking_id, new_start_datetime, new_end_datetime, db_session):
    booking = db_session.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        db_session.rollback()
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.start_datetime = new_start_datetime
    booking.end_datetime = new_end_datetime
    booking.status = "Rescheduled"
    booking.rescheduled_to = new_start_datetime
    db_session.commit()
    # send_rescheduling_notifications(booking)
