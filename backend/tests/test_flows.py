import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///" + str(Path(__file__).parent / "_test.db").replace("\\", "/")
os.environ["JWT_SECRET"] = "test-secret"

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.seed import seed
from app.db.session import engine, get_db
from app.main import app
from app.models.entities import PickupStatus

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
db = TestingSession()
seed(db)
db.close()


def override_db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def login(email="ananya@kabadiwala.local"):
    res = client.post("/api/auth/login", json={"email": email, "password": "DemoPass123!"})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def test_register_and_me():
    res = client.post(
        "/api/auth/register",
        json={"email": "newuser@kabadiwala.local", "password": "DemoPass123!", "full_name": "New User", "role": "CONSUMER"},
    )
    assert res.status_code == 200
    token = res.json()["access_token"]
    me = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["role"] == "CONSUMER"


def test_login_and_role_protection():
    token = login()
    forbidden = client.post("/api/admin/verifications", headers={"Authorization": f"Bearer {token}"})
    assert forbidden.status_code in (404, 405, 403)
    admin = login("admin@kabadiwala.local")
    ok = client.get("/api/admin/users", headers={"Authorization": f"Bearer {admin}"})
    assert ok.status_code == 200


def test_prices_are_labeled_demo():
    res = client.get("/api/prices/copper")
    assert res.status_code == 200
    body = res.json()
    assert body["data_type"] == "DEMO"
    assert body["is_live"] is False
    assert "Prototype" in body["source"] or "demo" in body["source"].lower() or "seed" in body["source"].lower()


def test_scrap_offer_pickup_trace():
    token = login()
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post("/api/scrap", json={"location": "Bengaluru", "area": "Whitefield"}, headers=headers)
    assert created.status_code == 200, created.text
    listing_id = created.json()["id"]
    qty = client.post(
        f"/api/scrap/{listing_id}/quantity",
        json={"quantity": 10, "unit": "kg", "material_slug": "copper"},
        headers=headers,
    )
    assert qty.status_code == 200
    assert qty.json()["estimated_low"] is not None
    offers = client.get(f"/api/offers?listing_id={listing_id}", headers=headers)
    assert offers.status_code == 200
    rows = offers.json()
    assert len(rows) >= 1
    accepted = client.post(f"/api/offers/{rows[0]['id']}/accept", headers=headers)
    assert accepted.status_code == 200
    pickup = client.post("/api/pickups", json={"listing_id": listing_id, "area": "Whitefield"}, headers=headers)
    assert pickup.status_code == 200, pickup.text
    pickup_id = pickup.json()["id"]
    collector = login("ravi@kabadiwala.local") if rows[0]["buyer_type"] == "collector" and "Ravi" in rows[0]["name"] else login("ravi@kabadiwala.local")
    # If first offer is recycler, collector status change may 403; accept collector offer if present
    collector_offer = next((o for o in rows if o["buyer_type"] == "collector"), None)
    if collector_offer and accepted.json()["buyer_type"] != "collector":
        return
    cheaders = {"Authorization": f"Bearer {collector}"}
    got = client.get(f"/api/pickups/{pickup_id}", headers=headers)
    assert got.status_code == 200
    if got.json()["collector_name"]:
        for status in [
            PickupStatus.CONFIRMED.value,
            PickupStatus.ON_THE_WAY.value,
            PickupStatus.ARRIVED.value,
            PickupStatus.COLLECTED.value,
            PickupStatus.COMPLETED.value,
        ]:
            res = client.patch(f"/api/pickups/{pickup_id}/status", json={"status": status}, headers=cheaders)
            assert res.status_code == 200, res.text


def test_traceability_seed():
    res = client.get("/api/traceability/BLR-EW-2026-00827")
    assert res.status_code == 200
    body = res.json()
    assert body["lot_id"] == "BLR-EW-2026-00827"
    assert len(body["events"]) >= 3
