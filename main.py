from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import Base, engine
from routers.user import router as users_router
from routers.driver import router as drivers_router
from routers.cab_booking import router as cab_bookings_router
from routers.driver_booking import router as driver_booking_router
from routers.vehicle import router as vehicle_router
from routers.vehicle_rental import router as vehicle_rentals_router
 
# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RideDo API",
    description="Backend API for RideDo cab, driver and rental services",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ridedo-backend-4o1g.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# include routers

app.include_router(users_router)
app.include_router(drivers_router)
app.include_router(cab_bookings_router)
app.include_router(driver_booking_router)
app.include_router(vehicle_router)
app.include_router(vehicle_rentals_router)

 
 



 