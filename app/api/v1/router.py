from fastapi import APIRouter

from app.api.v1.endpoints import health
from app.api.v1.endpoints import users
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.patients import router as patients_router
from app.api.v1.endpoints.services import router as services_router
from app.api.v1.endpoints.appointments import router as appointments_router

api_router = APIRouter()

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)   

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)   

api_router.include_router(
    patients_router,
    prefix="/patients",
    tags=["Patients"],
)   

api_router.include_router(
    services_router,
    prefix="/services",
    tags=["Services"],
)   

api_router.include_router(
    appointments_router,
    prefix="/appointments",
    tags=["Appointments"],
)   
