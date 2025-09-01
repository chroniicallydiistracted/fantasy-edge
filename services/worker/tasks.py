from .celery_app import celery
from fastapi import FastAPI
import uvicorn

@celery.task
def ping():
    return "pong"

# Create a simple FastAPI app for health checks
app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
