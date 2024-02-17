from fastapi import APIRouter, HTTPException
from Controllers.tourist_controllers import (
    create_tourist,
    get_all_tourists,
    get_tourist_by_id,
    update_tourist,
    delete_tourist
)

router = APIRouter()

@router.get("/")
async def read_root():
    return {"Tourists" : "Hello World"}

@router.post("/create_tourist")
async def create_tourist_route(new_tourist: dict):
    try:
        tourist = create_tourist(new_tourist)
        return tourist
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.get("/get_all_tourists")
async def get_all_tourists_route():
    try:
        tourists = get_all_tourists()
        return tourists
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.delete("/delete_tourist/")
async def delete_tourist_route(id: dict):
    try:
        tourist = delete_tourist(id)
        return tourist
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.put("/update_tourist")
async def update_tourist_route(tourist: dict):
    try:
        tourist = update_tourist(tourist)
        return tourist
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
@router.get("/get_tourist_by_id/")
async def get_tourist_by_id_route(tourist_id: int):
    try:
        tourist = get_tourist_by_id(tourist_id)
        return tourist
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))