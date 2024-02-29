from fastapi import APIRouter, HTTPException, Depends
from Models.models import Booking
from sqlalchemy.orm import Session
from Connections.connections import SessionLocal
from Connections.connections import session

from Controllers.booking_controllers import(
    create_booking_controller,
    get_booking_for_farmer,
    get_booking_for_farmer_by_status,
    accept_booking_controller
)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def read_root():
    return {"Booking" : "Hello World"}

@router.post("/create_booking")
async def create_booking_route(new_booking: dict,db: Session = Depends(get_db)):
    try:
        booking = create_booking_controller(db,new_booking)
        return booking
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.get("/farmer_bookings/")  
async def get_bookings_for_farmer(farmer_id: int, db: Session = Depends(get_db)):
    try:
        bookings = get_booking_for_farmer(db,farmer_id)
        return bookings
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
# geting all pending bookings 
@router.get("/pending_bookings/")
async def get_pending_bookings(farmer_id: int, db: Session = Depends(get_db)):
    status = "requesting"
    try:
        bookings = get_booking_for_farmer_by_status(db,farmer_id, status)
        return bookings
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.post("/accept/{booking_id}")
async def accept_booking(booking_id: int, db: Session = Depends(get_db)):
    result = accept_booking_controller(db,booking_id)
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

    