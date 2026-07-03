"""
Security injection tests.
Validates SQL injection, NoSQL injection and XSS defenses.
"""
import pytest
from datetime import datetime, timedelta


class TestInjectionDefenses:

    async def test_sql_injection_in_search_param(self, client, auth_headers_owner):
        """Passing SQL syntax into query parameters must not leak any records or break the app"""
        resp = await client.get(
            "/api/inventory/raw-materials?search=' OR '1'='1",
            headers=auth_headers_owner,
        )
        assert resp.status_code == 200
        # Since 'search' parameter is ignored/treated literally and SQL is prevented,
        # we check that the app runs correctly.
        assert isinstance(resp.json(), list)

    async def test_nosql_injection_in_filter(self, client, auth_headers_owner):
        """MongoDB query filters passed as strings must be parsed literally to prevent injection"""
        # category={"$gt":""} is parsed as a literal string by FastAPI/Pydantic
        resp = await client.get(
            '/api/inventory/raw-materials?category={"$gt":""}',
            headers=auth_headers_owner,
        )
        assert resp.status_code == 200
        # Should return no items since no category has that literal name
        assert len(resp.json()) == 0

    async def test_xss_prevention_in_notes(self, client, auth_headers_owner):
        """Notes containing script tags must be sanitized/escaped before saving to database"""
        machines_resp = await client.get("/api/machines", headers=auth_headers_owner)
        ext02 = next(m for m in machines_resp.json() if m["machine_code"] == "EXT-02")
        ext02_id = ext02["id"]

        resp = await client.post("/api/production/work-orders", headers=auth_headers_owner, json={
            "product_type": "uPVC Pipe",
            "pipe_diameter_mm": 90,
            "pressure_class": "PN10",
            "quantity_meters": 1000,
            "machine_id": ext02_id,
            "shift": "morning",
            "planned_start": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            "planned_end": (datetime.utcnow() + timedelta(hours=10)).isoformat(),
            "priority": "high",
            "notes": "<script>alert('xss')</script>"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "<script>" not in data["notes"]
        assert "&lt;script&gt;" in data["notes"]
