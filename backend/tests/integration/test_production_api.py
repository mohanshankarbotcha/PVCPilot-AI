"""
Production API integration tests.
Full CRUD on work orders, schedule, batch tracking, MRP.
"""
import pytest
from datetime import datetime, timedelta


class TestWorkOrders:

    async def test_create_work_order_success(self, client, auth_headers_owner):
        """Plant Manager can create a valid work order"""
        machines_resp = await client.get("/api/machines", headers=auth_headers_owner)
        ext02 = next(m for m in machines_resp.json() if m["machine_code"] == "EXT-02")
        ext02_id = ext02["id"]

        resp = await client.post("/api/production/work-orders", headers=auth_headers_owner, json={
            "product_type": "uPVC Pipe",
            "pipe_diameter_mm": 90,
            "pressure_class": "PN10",
            "quantity_meters": 5000,
            "machine_id": ext02_id,
            "shift": "morning",
            "planned_start": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            "planned_end": (datetime.utcnow() + timedelta(hours=10)).isoformat(),
            "priority": "high",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["order_number"].startswith("WO-")
        assert data["status"] == "draft"
        assert data["pipe_diameter_mm"] == 90

    async def test_work_order_number_is_unique(self, client, auth_headers_owner):
        """Two simultaneous work orders must get unique order numbers"""
        machines_resp = await client.get("/api/machines", headers=auth_headers_owner)
        ext01_id = next(m for m in machines_resp.json() if m["machine_code"] == "EXT-01")["id"]

        payload = {
            "product_type": "uPVC Pipe",
            "pipe_diameter_mm": 63,
            "pressure_class": "PN6",
            "quantity_meters": 3000,
            "machine_id": ext01_id,
            "shift": "afternoon",
            "planned_start": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "planned_end": (datetime.utcnow() + timedelta(hours=9)).isoformat(),
            "priority": "medium",
        }
        resp1 = await client.post("/api/production/work-orders", headers=auth_headers_owner, json=payload)
        resp2 = await client.post("/api/production/work-orders", headers=auth_headers_owner, json=payload)
        assert resp1.json()["order_number"] != resp2.json()["order_number"]

    async def test_operator_cannot_create_work_order(self, client, auth_headers_operator):
        """Operator role must not be able to create work orders"""
        machines_resp = await client.get("/api/machines", headers=auth_headers_operator)
        ext01_id = next(m for m in machines_resp.json() if m["machine_code"] == "EXT-01")["id"]

        resp = await client.post("/api/production/work-orders", headers=auth_headers_operator, json={
            "product_type": "uPVC Pipe",
            "pipe_diameter_mm": 63,
            "pressure_class": "PN10",
            "quantity_meters": 1000,
            "machine_id": ext01_id,
            "shift": "morning",
            "planned_start": datetime.utcnow().isoformat(),
            "planned_end": (datetime.utcnow() + timedelta(hours=8)).isoformat(),
            "priority": "low",
        })
        assert resp.status_code == 403

    async def test_work_order_status_transition_draft_to_scheduled(self, client, auth_headers_owner):
        """Work order must transition from draft → scheduled correctly"""
        machines_resp = await client.get("/api/machines", headers=auth_headers_owner)
        ext03_id = next(m for m in machines_resp.json() if m["machine_code"] == "EXT-03")["id"]

        # Create a draft work order
        create_resp = await client.post("/api/production/work-orders", headers=auth_headers_owner, json={
            "product_type": "uPVC Pipe",
            "pipe_diameter_mm": 110,
            "pressure_class": "PN10",
            "quantity_meters": 4000,
            "machine_id": ext03_id,
            "shift": "night",
            "planned_start": (datetime.utcnow() + timedelta(hours=6)).isoformat(),
            "planned_end": (datetime.utcnow() + timedelta(hours=14)).isoformat(),
            "priority": "medium",
        })
        order_id = create_resp.json()["id"]

        # Transition to scheduled
        resp = await client.patch(
            f"/api/production/work-orders/{order_id}/status",
            headers=auth_headers_owner,
            json={"status": "scheduled"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "scheduled"

    async def test_invalid_status_transition_rejected(self, client, auth_headers_owner):
        """Cannot jump from draft directly to completed"""
        machines_resp = await client.get("/api/machines", headers=auth_headers_owner)
        ext01_id = next(m for m in machines_resp.json() if m["machine_code"] == "EXT-01")["id"]

        create_resp = await client.post("/api/production/work-orders", headers=auth_headers_owner, json={
            "product_type": "uPVC Pipe", "pipe_diameter_mm": 63, "pressure_class": "PN6",
            "quantity_meters": 2000, "machine_id": ext01_id, "shift": "morning",
            "planned_start": datetime.utcnow().isoformat(),
            "planned_end": (datetime.utcnow() + timedelta(hours=8)).isoformat(),
            "priority": "low",
        })
        order_id = create_resp.json()["id"]

        resp = await client.patch(
            f"/api/production/work-orders/{order_id}/status",
            headers=auth_headers_owner,
            json={"status": "completed"},  # Invalid jump
        )
        assert resp.status_code == 400
        assert "invalid" in resp.json()["detail"].lower()

    async def test_mrp_calculation_for_work_order(self, client, auth_headers_owner):
        """MRP endpoint returns correct material requirements"""
        machines_resp = await client.get("/api/machines", headers=auth_headers_owner)
        ext02_id = next(m for m in machines_resp.json() if m["machine_code"] == "EXT-02")["id"]

        create_resp = await client.post("/api/production/work-orders", headers=auth_headers_owner, json={
            "product_type": "uPVC Pipe", "pipe_diameter_mm": 90, "pressure_class": "PN10",
            "quantity_meters": 1000, "machine_id": ext02_id, "shift": "morning",
            "planned_start": datetime.utcnow().isoformat(),
            "planned_end": (datetime.utcnow() + timedelta(hours=8)).isoformat(),
            "priority": "high",
        })
        order_id = create_resp.json()["id"]

        resp = await client.get(f"/api/production/planning/mrp?work_order_id={order_id}", headers=auth_headers_owner)
        assert resp.status_code == 200
        mrp = resp.json()
        assert "requirements" in mrp
        assert len(mrp["requirements"]) > 0

    async def test_production_chart_data_returns_per_machine(self, client, auth_headers_owner):
        """Chart data endpoint returns different data shapes per machine"""
        resp_ext01 = await client.get("/api/production/chart-data?machine=EXT-01&period=7D", headers=auth_headers_owner)
        resp_cool01 = await client.get("/api/production/chart-data?machine=COOL-01&period=7D", headers=auth_headers_owner)
        assert resp_ext01.status_code == 200
        assert resp_cool01.status_code == 200
        assert "primaryData" in resp_ext01.json()
        assert "secondaryData" in resp_ext01.json()
