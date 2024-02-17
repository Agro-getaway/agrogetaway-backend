from fastapi import FastAPI,Depends
from fastapi.middleware.cors import CORSMiddleware
from Controllers.booking_controllers import start_reminder_scheduler
from Routes import (
    user_routes,
    admin_routes,
    model_farmer_routes,
    Tourist_routes,
    booking_routes
)

import asyncio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.on_event("startup")
async def startup_event():
    start_reminder_scheduler()
    

app.include_router(user_routes.router, prefix="/user")# understanding tags=["User"], dependencies=[Depends(get_token_header)]
app.include_router(admin_routes.router, prefix="/admin")
app.include_router(model_farmer_routes.router, prefix="/farm")
app.include_router(Tourist_routes.router, prefix="/tourist")
app.include_router(booking_routes.router, prefix="/booking")

if __name__ == "__main__":
    import uvicorn
    from watchgod import watch
    uvicorn.run("main:app", host = "127.0.0.1", port = 8002,reload=True, workers=2)
