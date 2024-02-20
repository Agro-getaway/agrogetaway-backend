from fastapi import APIRouter, Depends, HTTPException
from Connections.connections import SessionLocal
from sqlalchemy.orm import Session
from typing import List

from Controllers.file_controllers import (
    fetch_farm_images
)   

router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/farm_images/", response_model=List[str])
async def get_farm_images(farm_id: int, db: Session = Depends(get_db)):
    try:
        images = fetch_farm_images(db, farm_id)
        return images
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
