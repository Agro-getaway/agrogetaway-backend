from Models.models import FarmImage
from typing import List,Any
from sqlalchemy.orm import Session
from upload import FirebaseUpload

def fetch_farm_images(db: Session, farm_id: int) -> List[str]:
    images = db.query(FarmImage.image_url).filter(FarmImage.farm_id == farm_id).all()
    return [image[0] for image in images]

def update_farm_image(db: Session, image_id: int, new_file: Any) -> str:
    farm_image = db.query(FarmImage).filter(FarmImage.id == image_id).first()
    if not farm_image:
        db.rollback()
        raise Exception("Image not found")

    file_upload = FirebaseUpload("farms/")
    new_image_url = file_upload.update(new_file, farm_image.image_url) 

    farm_image.image_url = new_image_url
    db.commit()
    return new_image_url

def delete_farm_image(db: Session, image_id: int) -> None:
    farm_image = db.query(FarmImage).filter(FarmImage.id == image_id).first()
    if not farm_image:
        db.rollback()
        raise Exception("Image not found")

    file_upload = FirebaseUpload("farms/")
    file_upload.delete(farm_image.image_url)  

    db.delete(farm_image)
    db.commit()
