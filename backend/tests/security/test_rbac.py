"""
Role-Based Access Control security tests.
Verify that every role sees only what it's permitted to see.
"""
import pytest


class TestRBAC:

    @pytest.mark.parametrize("role_email,method,route,expected_status", [
        # Operator cannot access admin routes
        ("operator@pvcpilot.com", "GET", "/api/admin/users", 403),
        # Operator cannot create work orders
        ("operator@pvcpilot.com", "POST", "/api/production/work-orders", 403),
        # Quality engineer cannot approve purchase orders
        ("quality@pvcpilot.com", "PATCH", "/api/procurement/purchase-orders/65b111111111111111111111/approve", 403),
        # Sales manager cannot access admin
        ("sales@pvcpilot.com", "GET", "/api/admin/users", 403),
        # Factory owner can access everything (200 or 404, not 403)
        ("owner@pvcpilot.com", "GET", "/api/admin/users", 200),
    ])
    async def test_role_access_control(self, client, role_email, method, route, expected_status):
        login_resp = await client.post("/api/auth/login", json={
            "email": role_email, "password": "PVCPilot@2025",
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        if method == "POST":
            resp = await client.post(route, headers=headers, json={})
        elif method == "PATCH":
            resp = await client.patch(route, headers=headers, json={})
        else:
            resp = await client.get(route, headers=headers)

        assert resp.status_code == expected_status, \
            f"Role {role_email} on {method} {route}: expected {expected_status}, got {resp.status_code}"
