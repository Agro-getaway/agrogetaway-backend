from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Connections.connections import SessionLocal  
from Controllers.event_controllers import (
    create_event,
    get_events_for_farm, 
    update_event
    )
router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/farms/{farm_id}/events/")
def create_event_route(farm_id: int, event_data: dict, db: Session = Depends(get_db)):
    event_data["farm_id"] = farm_id
    return create_event(db_session=db, event_data=event_data)

@router.get("/farms/{farm_id}/events/")
def get_events_for_farm_route(farm_id: int, db: Session = Depends(get_db)):
    return get_events_for_farm(db_session=db, farm_id=farm_id)

@router.put("/events/{event_id}/")
def update_event_route(event_id: int, update_data: dict, db: Session = Depends(get_db)):
    return update_event(db_session=db, event_id=event_id, update_data=update_data)
