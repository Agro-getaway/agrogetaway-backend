from fastapi import Depends,APIRouter, HTTPException
from Connections.connections import SessionLocal
from sqlalchemy.orm import Session
from Controllers.model_farmers_controllers import (
    create_farmer,
    approve_farm,
    reject_farm,
    get_all_approved_farms,
    get_pending_farms_count,
    pending_farms,
    get_approved_farms_count,
    get_farm_data_for_farmer,
    update_farm_stored,
    delete_farm
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
    return {"Farmers" : "Hello World"}

@router.post("/create_farm")
async def create_farmer_route(new_farmer: dict, db: Session = Depends(get_db)):
    try:
        farmer = create_farmer(db, new_farmer)
        return farmer
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.put("/approve_farm")
async def approve_farm_route(farm: dict, db: Session = Depends(get_db)):
    try:
        return approve_farm(db, farm)
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.put("/reject_farm")
async def reject_farm_route(farm: dict, db: Session = Depends(get_db)):
    try:
        return reject_farm(db, farm)
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.get("/get_all_approved_farms")
async def get_all_approved_farms_route(db: Session = Depends(get_db)):
    try:
        return get_all_approved_farms(db)
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.get("/get_all_pending_farms")
async def get_all_pending_farms_route(db: Session = Depends(get_db)):
    try:
        return pending_farms(db)
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.get("/get_pending_count")
async def get_pending_farms_count_route(db: Session = Depends(get_db)):
    try:
        return get_pending_farms_count(db)
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.get("/get_approved_count")
async def get_approved_farms_count_route(db: Session = Depends(get_db)):
    try:
        return get_approved_farms_count(db)
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.get("/get_farm_data_for_farmer/")
async def get_farm_data_for_farmer_route(farmer_id: int):
    try:
        return get_farm_data_for_farmer(farmer_id)
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.put("/update_farm_stored")
async def update_farm_stored_route(farm: dict, db: Session = Depends(get_db)):
    print(f"farm : {farm}")
    try:
        return update_farm_stored(db, farm)
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.delete("/delete_farm")
async def delete_farm_route(farm_id: int, db: Session = Depends(get_db)):
    try:
        return delete_farm(db, farm_id)
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))