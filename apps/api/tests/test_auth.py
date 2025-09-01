from fastapi.testclient import TestClient
from app.security import TokenEncryptionService
from app.session import SessionManager
from app.settings import settings


# Test the token encryption service
def test_token_encryption_roundtrip():
    # Create a test encryption service
    encryption_service = TokenEncryptionService("test-key-32-characters-long")

    # Test token
    test_token = "test-access-token-12345"

    # Encrypt the token
    encrypted = encryption_service.encrypt(test_token)
    assert encrypted != test_token

    # Decrypt the token
    decrypted = encryption_service.decrypt(encrypted)
    assert decrypted == test_token


# Test session management
def test_session_token_creation():
    # Create a test user ID
    user_id = 123

    # Create a token
    token = SessionManager.create_token(user_id)
    assert token is not None

    # Verify the token
    verified_user_id = SessionManager.verify_token(token)
    assert verified_user_id == user_id


def test_session_token_invalid():
    # Test with an invalid token
    invalid_token = "invalid.token.here"
    verified_user_id = SessionManager.verify_token(invalid_token)
    assert verified_user_id is None


# Test debug bypass functionality
def test_debug_bypass_disabled():
    # Temporarily disable debug user
    original_value = settings.allow_debug_user
    settings.allow_debug_user = False

    # Create a test client
    from app.main import app

    client = TestClient(app)

    # Try to access debug endpoint
    response = client.get("/auth/session/debug", headers={"X-Debug-User": "1"})
    assert response.status_code == 200
    assert response.json()["error"] == "Debug user not enabled"

    # Restore original value
    settings.allow_debug_user = original_value


def test_debug_bypass_enabled():
    # Temporarily enable debug user
    original_value = settings.allow_debug_user
    settings.allow_debug_user = True

    # Create a test client
    from app.main import app

    client = TestClient(app)

    # Try to access debug endpoint
    response = client.get("/auth/session/debug", headers={"X-Debug-User": "1"})
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert "user_id" in response.json()

    # Verify the cookie was set
    assert "set-cookie" in response.headers
    assert SessionManager.COOKIE_NAME in response.headers["set-cookie"]

    # Restore original value
    settings.allow_debug_user = original_value


def test_debug_bypass_invalid_header():
    # Temporarily enable debug user
    original_value = settings.allow_debug_user
    settings.allow_debug_user = True

    # Create a test client
    from app.main import app

    client = TestClient(app)

    # Try to access debug endpoint with invalid header
    response = client.get("/auth/session/debug", headers={"X-Debug-User": "invalid"})
    assert response.status_code == 200
    assert response.json()["error"] == "Invalid debug user header"

    # Restore original value
    settings.allow_debug_user = original_value
