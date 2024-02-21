from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from Connections.connections import SessionLocal
from sqlalchemy.orm import Session
from Models.models import FarmImage
from typing import List
from upload import FirebaseUpload
from typing import Any

from Controllers.file_controllers import (
    fetch_farm_images,
    update_farm_image,
    
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

@router.get("/farm_images/", response_model=List[str])
async def get_farm_images(farm_id: int, db: Session = Depends(get_db)):
    try:
        images = fetch_farm_images(db, farm_id)
        return images
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.put("/update_image/{image_id}", response_model=str)
async def update_image_route(image_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        new_image_url = update_farm_image(db, image_id, file.file)
        return new_image_url
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# @router.delete("/delete_image/", response_model=dict)
# async def delete_image(image_id: int, db: Session = Depends(get_db)):
#     try:
#         farm_image = db.query(FarmImage).filter(FarmImage.id == image_id).first()
#         if not farm_image:
#             raise HTTPException(status_code=404, detail="Image not found")
    
#         file_upload = FirebaseUpload("farms/")
#         file_upload.delete(farm_image.image_url)  

#         # Delete the database record
#         db.delete(farm_image)
#         db.commit()
        
#         return {"message": "Image deleted successfully"}
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_image/", response_model=dict)
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    try:
        farm_image = db.query(FarmImage).filter(FarmImage.id == image_id).first()
        if not farm_image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        db.delete(farm_image)
        db.commit() 
        
        return {"message": "Image deleted successfully"}
    except Exception as e:
    
        db.rollback()
       
        raise HTTPException(status_code=500, detail=str(e))