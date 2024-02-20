from Models.models import FarmImage
from typing import List
from sqlalchemy.orm import Session

def fetch_farm_images(db: Session, farm_id: int) -> List[str]:
    images = db.query(FarmImage.image_url).filter(FarmImage.farm_id == farm_id).all()
    return [image[0] for image in images]
