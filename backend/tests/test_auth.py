from app.utils.security import get_password_hash, verify_password, create_access_token, decode_token

def test_password_hashing():
    password = "PVCPilot@2025"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_jwt_tokens():
    user_id = "60c72b2f9b1d8b2d18c12345"
    token = create_access_token(subject=user_id, role="factory_owner", email="owner@pvcpilot.com")
    assert token is not None
    
    payload = decode_token(token)
    assert payload.get("sub") == user_id
    assert payload.get("role") == "factory_owner"
    assert payload.get("email") == "owner@pvcpilot.com"
