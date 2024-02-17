from fastapi import APIRouter, HTTPException
from Models.models import Booking
from Connections.connections import session
import secrets
import random
import smtplib

from Controllers.booking_controllers import(
    create_booking_controller,
    get_booking_for_farmer,
    get_booking_for_farmer_by_status,
    accept_booking_controller
)

router = APIRouter()


@router.get("/")
async def read_root():
    return {"Booking" : "Hello World"}

@router.post("/create_booking")
async def create_booking_route(new_booking: dict):
    try:
        booking = create_booking_controller(new_booking)
        return booking
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.get("/farmer_bookings/")  
async def get_bookings_for_farmer(farmer_id: int):
    try:
        bookings = get_booking_for_farmer(farmer_id)
        return bookings
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
# geting all pending bookings 
@router.get("/pending_bookings/")
async def get_pending_bookings(farmer_id: int):
    status = "Requesting"
    try:
        bookings = get_booking_for_farmer_by_status(farmer_id, status)
        return bookings
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.post("/accept/{booking_id}")
async def accept_booking(booking_id: int):
    result = accept_booking_controller(booking_id)
    if result["status"] != 200:
        raise HTTPException(status_code=result["status"], detail=result["message"])
    return result

# @router.post("/{booking_id}/cancel")
# def cancel_booking_endpoint(booking_id: int, db: Session = Depends(get_db)):
#     try:
#         cancel_booking(booking_id, db)
#         return {"message": "Booking cancelled successfully"}
#     except HTTPException as e:
#         raise e

# @router.post("/{booking_id}/reschedule")
# def reschedule_booking_endpoint(booking_id: int, new_start_datetime: datetime, new_end_datetime: datetime, db: Session = Depends(get_db)):
#     try:
#         reschedule_booking(booking_id, new_start_datetime, new_end_datetime, db)
#         return {"message": "Booking rescheduled successfully"}
#     except HTTPException as e:
#         raise e

    