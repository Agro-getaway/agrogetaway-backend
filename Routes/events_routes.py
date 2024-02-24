from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Connections.connections import SessionLocal  
from Controllers.event_controllers import (
    create_event,
    get_events_for_farm, 
    update_event,
    get_all_events
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
def create_event_route(event_data: dict, db: Session = Depends(get_db)):
    return create_event(db=db, event_data=event_data)

# @router.get("/get_events/")
# def get_events_for_farm_route(farm_id: int, db: Session = Depends(get_db)):
#     return get_events_for_farm(db=db, farm_id=farm_id)

@router.get("/get_all_events/")
def get_all_events_route(db: Session = Depends(get_db)):
    return get_all_events(db=db)

@router.put("/update_events/")
def update_event_route(event_id: int, update_data: dict, db: Session = Depends(get_db)):
    return update_event(db=db, event_id=event_id, update_data=update_data)
