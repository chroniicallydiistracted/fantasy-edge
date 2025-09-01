from fastapi import APIRouter

router = APIRouter()

@router.get("/leagues")
def list_leagues():
    # Stub: will call Yahoo after OAuth is implemented
    return {"leagues": []}
