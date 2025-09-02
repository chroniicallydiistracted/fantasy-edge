from app.deps import SessionLocal
from app.models import User

def test_user_crud():
    with SessionLocal() as s:
        u = User(email="test@example.com")
        s.add(u)
        s.commit()
        s.refresh(u)
        assert u.id is not None
