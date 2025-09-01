from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health, auth, yahoo, optimize, players, waivers, streamers

app = FastAPI(title="Fantasy Edge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://misfits.westfam.media"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(yahoo.router, prefix="/yahoo", tags=["yahoo"])
app.include_router(optimize.router, prefix="/team", tags=["optimize"])
app.include_router(players.router, prefix="/players", tags=["players"])
app.include_router(waivers.router, prefix="/team", tags=["waivers"])
app.include_router(streamers.router, prefix="/streamers", tags=["streamers"])
