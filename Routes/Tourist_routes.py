from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from Connections.connections import SessionLocal
from Controllers.tourist_controllers import (
    create_tourist,
    get_all_tourists,
    get_tourist_by_id,
    update_tourist,
    delete_tourist
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
    return {"Tourists" : "Hello World"}

@router.post("/create_tourist")
async def create_tourist_route(new_tourist: dict,db: Session = Depends(get_db)):
    try:
        tourist = create_tourist(db,new_tourist)
        return tourist
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.get("/get_all_tourists")
async def get_all_tourists_route(db: Session = Depends(get_db)):
    try:
        tourists = get_all_tourists(db)
        return tourists
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.delete("/delete_tourist/")
async def delete_tourist_route(id: dict,db: Session = Depends(get_db)):
    try:
        tourist = delete_tourist(db,id)
        return tourist
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.put("/update_tourist")
async def update_tourist_route(tourist: dict,db: Session = Depends(get_db)):
    try:
        tourist = update_tourist(db,tourist)
        return tourist
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.get("/get_tourist_by_id/")
async def get_tourist_by_id_route(tourist_id: int, db: Session = Depends(get_db)):	
    try:
        tourist = get_tourist_by_id(db,tourist_id)
        return tourist
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))