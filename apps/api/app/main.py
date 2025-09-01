from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .settings import settings
from .routers import health, auth, yahoo, optimize
from .deps import get_db

app = FastAPI(title="Fantasy Edge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://misfits.westfam.media"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(yahoo.router, prefix="/yahoo", tags=["yahoo"])
app.include_router(optimize.router, prefix="/team", tags=["optimize"])
