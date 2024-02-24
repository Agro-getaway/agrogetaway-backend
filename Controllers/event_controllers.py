from fastapi import APIRouter, HTTPException
from Models.models import Event
from sqlalchemy.orm import Session

def create_event(db : Session, event_data):
    db_event = Event(**event_data)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

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
