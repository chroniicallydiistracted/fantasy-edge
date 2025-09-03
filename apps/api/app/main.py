from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import (
    health, auth, yahoo, optimize, players, waivers, streamers, 
    live, leagues, team, events, preferences
)
from .logging import configure_logging
from .settings import settings

configure_logging()

app = FastAPI(title="Fantasy Edge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(yahoo.router, prefix="/yahoo", tags=["yahoo"])
app.include_router(optimize.router, prefix="/team", tags=["optimize"])
app.include_router(players.router, prefix="/players", tags=["players"])
app.include_router(waivers.router, prefix="/team", tags=["waivers"])
app.include_router(streamers.router, prefix="/streamers", tags=["streamers"])
app.include_router(live.router, prefix="/live", tags=["live"])
app.include_router(leagues.router, prefix="/leagues", tags=["leagues"])
app.include_router(team.router, prefix="/team", tags=["team"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(preferences.router, prefix="/user/preferences", tags=["preferences"])
