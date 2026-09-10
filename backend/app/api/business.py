from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.core.errors import forbidden, not_found
from app.db.session import get_db
from app.models.entities import BusinessBulkRequest, DataType, Material, RecyclerBid, Role, User
from app.schemas.main import BulkCreate, BulkOut
from app.services.pricing import price_payload
from app.services.system import audit

router = APIRouter(prefix="/api/business", tags=["business"])


def _estimate(db: Session, materials: list) -> tuple[float | None, float | None, DataType]:
    low = 0.0
    high = 0.0
    used = False
    dtype = DataType.DEMO
    for item in materials:
        slug = item.get("slug") or item.get("material")
        qty = float(item.get("quantity") or 0)
        payload = price_payload(db, slug, "Bengaluru") if slug else None
        if payload and qty:
            used = True
            low += payload["low"] * qty
            high += payload["high"] * qty
            dtype = payload["data_type"]
    if not used:
        return None, None, DataType.DEMO
    return round(low, 2), round(high, 2), dtype


@router.post("/bulk-requests", response_model=BulkOut)
def create_bulk(body: BulkCreate, user: User = Depends(require_roles(Role.BUSINESS, Role.ADMIN)), db: Session = Depends(get_db)):
    low, high, dtype = _estimate(db, body.materials)
    row = BusinessBulkRequest(
        user_id=user.id,
        organization_type=body.organization_type,
        materials=body.materials,
        pickup_location=body.pickup_location,
        preferred_schedule=body.preferred_schedule,
        description=body.description,
        estimated_low=low,
        estimated_high=high,
        data_type=dtype,
    )
    db.add(row)
    db.flush()
    audit(db, "bulk.create", "business_bulk_request", str(row.id), user.id)
    db.commit()
    db.refresh(row)
    return row


@router.get("/bulk-requests/{request_id}", response_model=BulkOut)
def get_bulk(request_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.get(BusinessBulkRequest, request_id)
    if not row:
        raise not_found("Bulk request not found")
    if row.user_id != user.id and user.role not in (Role.ADMIN, Role.RECYCLER):
        raise forbidden()
    return row


@router.get("/bulk-requests/{request_id}/offers")
def bulk_offers(request_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.get(BusinessBulkRequest, request_id)
    if not row:
        raise not_found("Bulk request not found")
    if row.user_id != user.id and user.role not in (Role.ADMIN, Role.RECYCLER):
        raise forbidden()
    bids = db.query(RecyclerBid).filter(RecyclerBid.bulk_request_id == request_id).all()
    return [{"id": b.id, "amount": b.amount, "notes": b.notes, "recycler_id": b.recycler_id} for b in bids]
