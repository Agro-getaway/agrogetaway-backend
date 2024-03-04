from fastapi import APIRouter, Depends,UploadFile, File, Form
from sqlalchemy.orm import Session
from Connections.connections import SessionLocal  
from datetime import datetime

from Controllers.event_controllers import (
    create_event,
    get_events_for_farm, 
    update_event,
    get_all_events,
    get_approved_events,
    approve_event,
    get_pending_events,
    get_pending_events_count,
    get_events_for_auser
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
    return {"Events" : "Hello World"}

@router.post("/create_event/")
def create_event_route(
    name : str = Form(...),
    description : str = Form(...),
    start_time : datetime = Form(...),
    end_time : datetime = Form(...),
    file: UploadFile = File(...),
    added_by: int = File(...),
    db: Session = Depends(get_db)):

    event_data = {
        "name" : name,
        "description" : description,
        "start_time" : start_time,
        "end_time" : end_time,
        "added_by": added_by,
        "file" : file
    }
    try:
        event_response = create_event(db=db, event_data=event_data)
        return event_response
    except Exception as e:
        return {"error" : str(e)}

# @router.get("/get_events/")
# def get_events_for_farm_route(farm_id: int, db: Session = Depends(get_db)):
#     return get_events_for_farm(db=db, farm_id=farm_id)

@router.get("/get_all_events/")
def get_all_events_route(db: Session = Depends(get_db)):
    return get_all_events(db=db)

@router.put("/update_events/")
def update_event_route(event_id: int, update_data: dict, db: Session = Depends(get_db)):
    return update_event(db=db, event_id=event_id, update_data=update_data)

@router.get("/get_approved_events/")
def get_approved_events_route(db: Session = Depends(get_db)):
    return get_approved_events(db=db)

@router.put("/approve_event/")
def approve_event_route(event_data: dict, db: Session = Depends(get_db)):
    event_id = event_data["event_id"]
    admin_id = event_data["admin_id"]
    return approve_event(db=db, event_id=event_id, admin_id=admin_id)

@router.get("/get_pending_events/")
def get_pending_events_route(db: Session = Depends(get_db)):
    return get_pending_events(db=db)

@router.get("/get_pending_events_count/")
def get_pending_events_count_route(db: Session = Depends(get_db)):
    return get_pending_events_count(db=db)

@router.get("/get_events_for_a_user/")
def get_events_for_a_user(user_id: int, db: Session = Depends(get_db)):
    return get_events_for_auser(db, user_id)