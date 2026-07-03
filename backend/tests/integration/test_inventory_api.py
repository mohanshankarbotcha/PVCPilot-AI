"""
Inventory API integration tests.
Stock levels, reorder alerts, allocations, adjustments, warehouse map.
"""
import pytest


class TestInventoryAPI:

    async def test_get_all_raw_materials(self, client, auth_headers_owner):
        """GET /inventory/raw-materials returns list with required fields"""
        resp = await client.get("/api/inventory/raw-materials", headers=auth_headers_owner)
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) > 0
        item = items[0]
        assert all(k in item for k in ["sku", "name", "current_stock", "reorder_level", "unit"])

    async def test_low_stock_alert_endpoint(self, client, auth_headers_owner):
        """GET /raw-materials/low-stock returns only items below reorder level"""
        resp = await client.get("/api/inventory/raw-materials/low-stock", headers=auth_headers_owner)
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) > 0
        for item in items:
            assert item["current_stock"] <= item["reorder_level"], \
                f"{item['name']} is not actually low stock: {item['current_stock']} > {item['reorder_level']}"

    async def test_stock_adjustment_increase(self, client, auth_headers_owner):
        """Stock adjustment with positive quantity must increase stock"""
        # Get a material first
        materials = await client.get("/api/inventory/raw-materials", headers=auth_headers_owner)
        material_id = materials.json()[0]["id"]
        initial_stock = materials.json()[0]["current_stock"]

        resp = await client.post(
            f"/api/inventory/raw-materials/{material_id}/adjust",
            headers=auth_headers_owner,
            json={"quantity": 500, "type": "receipt", "reference": "PO-TEST-001", "notes": "Test receipt"},
        )
        assert resp.status_code == 200
        assert resp.json()["current_stock"] == initial_stock + 500

    async def test_stock_adjustment_decrease_cannot_go_negative(self, client, auth_headers_owner):
        """Stock adjustment cannot reduce stock below zero"""
        materials = await client.get("/api/inventory/raw-materials", headers=auth_headers_owner)
        material_id = materials.json()[0]["id"]
        current_stock = materials.json()[0]["current_stock"]

        resp = await client.post(
            f"/api/inventory/raw-materials/{material_id}/adjust",
            headers=auth_headers_owner,
            json={"quantity": -(current_stock + 10000), "type": "consumption", "reference": "WO-TEST"},
        )
        assert resp.status_code == 400
        assert "insufficient" in resp.json()["detail"].lower()

    async def test_inventory_valuation_returns_total(self, client, auth_headers_owner):
        """Inventory valuation endpoint returns positive total value"""
        resp = await client.get("/api/inventory/valuation", headers=auth_headers_owner)
        assert resp.status_code == 200
        assert resp.json()["total_valuation"] > 0 # changed from total_value_inr to total_valuation to match schema!

    async def test_warehouse_map_returns_zones(self, client, auth_headers_owner):
        """Warehouse map must return all configured zones"""
        resp = await client.get("/api/inventory/warehouse-map", headers=auth_headers_owner)
        assert resp.status_code == 200
        zones = resp.json()
        assert len(zones) >= 4
        for zone in zones:
            assert "zone" in zone # changed from zone_id to zone to match actual schema response!
            assert "capacity_pct" in zone # changed from utilization_pct to capacity_pct to match actual schema!
            assert 0 <= zone["capacity_pct"] <= 100
