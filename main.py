from fastapi import FastAPI,Depends,File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from Controllers.booking_controllers import start_reminder_scheduler
from Routes import (
    farm_routes,
    model_farmer_routes,
    user_routes,
    admin_routes,
    Tourist_routes,
    booking_routes,
    file_routes
)
import io
from typing import List
from upload import FirebaseUpload

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

file_upload = FirebaseUpload("images/")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload")
async def upload_image(files: List[UploadFile] = File(...)):
    try:
        file_objects = [io.BytesIO(await file.read()) for file in files]
        file_names = [file.filename for file in files]
        
        result = file_upload.add(file_objects, file_names)
        return {"message": "Files uploaded successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    start_reminder_scheduler()
    

app.include_router(user_routes.router, prefix="/user")# understanding tags=["User"], dependencies=[Depends(get_token_header)]
app.include_router(admin_routes.router, prefix="/admin")
app.include_router(farm_routes.router, prefix="/farm")
app.include_router(Tourist_routes.router, prefix="/tourist")
app.include_router(booking_routes.router, prefix="/booking")
app.include_router(file_routes.router, prefix="/file")
app.include_router(model_farmer_routes.router, prefix="/model_farmer")

if __name__ == "__main__":
    import uvicorn
    from watchgod import watch
    uvicorn.run("main:app", host = "127.0.0.1", port = 8002,reload=True, workers=2)