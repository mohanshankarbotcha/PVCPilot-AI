"""
Authentication API integration tests.
Covers: registration, login, token refresh, logout, role validation.
"""
import pytest
import pytest_asyncio


class TestAuthLogin:

    async def test_login_factory_owner_success(self, client):
        """Factory Owner can log in with correct credentials"""
        resp = await client.post("/api/auth/login", json={
            "email": "owner@pvcpilot.com",
            "password": "PVCPilot@2025",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["role"] == "factory_owner"

    async def test_login_wrong_password_returns_401(self, client):
        """Wrong password must return 401"""
        resp = await client.post("/api/auth/login", json={
            "email": "owner@pvcpilot.com",
            "password": "WrongPassword123",
        })
        assert resp.status_code == 401
        assert "incorrect" in resp.json()["detail"].lower()

    async def test_login_nonexistent_email_returns_401(self, client):
        """Non-registered email must return 401"""
        resp = await client.post("/api/auth/login", json={
            "email": "ghost@nobody.com",
            "password": "AnyPassword@123",
        })
        assert resp.status_code == 401

    async def test_login_returns_user_role_and_permissions(self, client):
        """Login response must include role and permissions list"""
        resp = await client.post("/api/auth/login", json={
            "email": "quality@pvcpilot.com",
            "password": "PVCPilot@2025",
        })
        data = resp.json()
        assert data["user"]["role"] == "quality_engineer"
        assert isinstance(data["user"]["permissions"], list)

    async def test_get_me_with_valid_token(self, client, auth_headers_owner):
        """GET /me with valid token returns current user info"""
        resp = await client.get("/api/auth/me", headers=auth_headers_owner)
        assert resp.status_code == 200
        assert resp.json()["email"] == "owner@pvcpilot.com"

    async def test_get_me_without_token_returns_401(self, client):
        """GET /me without token must return 401"""
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401

    async def test_get_me_with_expired_token_returns_401(self, client):
        """Expired JWT must be rejected"""
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NjYiLCJleHAiOjE2MDAwMDAwMDB9.fake"
        resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
        assert resp.status_code == 401

    async def test_register_new_user_success(self, client):
        """New user registration with valid data must succeed"""
        resp = await client.post("/api/auth/register", json={
            "email": "newuser@pvcpilot.com",
            "password": "SecurePass@2026",
            "full_name": "Test Engineer",
            "role": "quality_engineer",
            "department": "Quality",
            "company_name": "PVC Industries Ltd",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "newuser@pvcpilot.com"
        assert "password" not in data  # Password must never be returned

    async def test_register_duplicate_email_returns_400(self, client):
        """Registering with an existing email must return 400"""
        resp = await client.post("/api/auth/register", json={
            "email": "owner@pvcpilot.com",
            "password": "SecurePass@2026",
            "full_name": "Duplicate",
            "role": "operator",
            "department": "Production",
        })
        assert resp.status_code == 400
        assert "exists" in resp.json()["detail"].lower()

    async def test_register_weak_password_returns_422(self, client):
        """Password shorter than 8 characters must fail validation"""
        resp = await client.post("/api/auth/register", json={
            "email": "weakpass@test.com",
            "password": "abc123",
            "full_name": "Weak User",
            "role": "operator",
            "department": "Production",
        })
        assert resp.status_code == 422
