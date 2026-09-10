from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, require_roles
from app.core.errors import bad_request, not_found
from app.db.session import get_db
from app.models.entities import (
    Material,
    RecyclingLot,
    RecyclerBid,
    RecyclerMaterial,
    RecyclerProfile,
    Role,
    TraceabilityEvent,
    User,
    VerificationRecord,
    VerificationStatus,
)
from app.schemas.main import BidCreate, LotStatusIn, RecyclerCreate, VerificationSubmit
from app.services.serializers import verification_label
from app.services.system import audit

router = APIRouter(prefix="/api/recyclers", tags=["recyclers"])


def _out(r: RecyclerProfile) -> dict:
    v = r.verification
    names = []
    for rm in r.materials:
        if rm.material:
            names.append(rm.material.name)
    return {
        "id": r.id,
        "organization_name": r.organization_name,
        "location": r.location,
        "pickup_available": r.pickup_available,
        "materials": names,
        "verification": verification_label(v.status if v else None, "recycler"),
        "authority_name": r.authority_name,
        "verification_source": r.verification_source,
    }


@router.get("")
def list_recyclers(db: Session = Depends(get_db)):
    rows = (
        db.query(RecyclerProfile)
        .options(
            joinedload(RecyclerProfile.user),
            joinedload(RecyclerProfile.verification),
            joinedload(RecyclerProfile.materials).joinedload(RecyclerMaterial.material),
        )
        .all()
    )
    return [_out(r) for r in rows]


@router.post("")
def create_recycler(body: RecyclerCreate, user: User = Depends(require_roles(Role.RECYCLER)), db: Session = Depends(get_db)):
    existing = db.query(RecyclerProfile).filter(RecyclerProfile.user_id == user.id).first()
    if existing:
        existing.organization_name = body.organization_name
        existing.location = body.location
        existing.lat = body.lat
        existing.lng = body.lng
        existing.pickup_lead_days = body.pickup_lead_days
        db.commit()
        return {"id": existing.id}
    profile = RecyclerProfile(
        user_id=user.id,
        organization_name=body.organization_name,
        location=body.location,
        lat=body.lat,
        lng=body.lng,
        pickup_lead_days=body.pickup_lead_days,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"id": profile.id}


@router.post("/{recycler_id}/verification")
def submit_verification(
    recycler_id: UUID,
    body: VerificationSubmit,
    user: User = Depends(require_roles(Role.RECYCLER)),
    db: Session = Depends(get_db),
):
    profile = db.get(RecyclerProfile, recycler_id)
    if not profile or profile.user_id != user.id:
        raise not_found("Recycler not found")
    record = profile.verification or VerificationRecord(recycler_id=profile.id)
    record.status = VerificationStatus.UNDER_REVIEW
    record.authority_name = body.authority_name
    record.registration_number = body.registration_number
    record.verification_source = body.verification_source
    record.notes = body.notes
    profile.authority_name = body.authority_name
    profile.registration_number = body.registration_number
    profile.verification_source = body.verification_source
    db.add(record)
    audit(db, "recycler.verification.submit", "recycler", str(profile.id), user.id)
    db.commit()
    return {"status": record.status, "message": "Submitted for review. Not verified until an admin records a decision."}


@router.post("/{recycler_id}/bids")
def create_bid(
    recycler_id: UUID,
    body: BidCreate,
    user: User = Depends(require_roles(Role.RECYCLER)),
    db: Session = Depends(get_db),
):
    profile = db.get(RecyclerProfile, recycler_id)
    if not profile or profile.user_id != user.id:
        raise not_found("Recycler not found")
    if not body.listing_id and not body.bulk_request_id:
        raise bad_request("Provide listing_id or bulk_request_id")
    bid = RecyclerBid(
        recycler_id=profile.id,
        listing_id=body.listing_id,
        bulk_request_id=body.bulk_request_id,
        amount=body.amount,
        notes=body.notes,
    )
    db.add(bid)
    db.commit()
    db.refresh(bid)
    return {"id": bid.id, "amount": bid.amount}


@router.get("/me/lots")
def my_lots(user: User = Depends(require_roles(Role.RECYCLER)), db: Session = Depends(get_db)):
    lots = db.query(RecyclingLot).order_by(RecyclingLot.created_at.desc()).limit(50).all()
    return [
        {"lot_id": lot.lot_id, "status": lot.current_status, "weight": lot.current_weight, "id": lot.id}
        for lot in lots
    ]


@router.patch("/lots/{lot_pk}/status")
def update_lot(
    lot_pk: UUID,
    body: LotStatusIn,
    user: User = Depends(require_roles(Role.RECYCLER, Role.ADMIN)),
    db: Session = Depends(get_db),
):
    lot = db.get(RecyclingLot, lot_pk)
    if not lot:
        raise not_found("Lot not found")
    lot.current_status = body.status
    if body.weight is not None:
        lot.current_weight = body.weight
    db.add(
        TraceabilityEvent(
            lot_id=lot.id,
            event_type=body.status,
            location=body.location,
            weight=body.weight if body.weight is not None else lot.current_weight,
            actor_id=user.id,
            notes=body.notes,
        )
    )
    audit(db, "lot.status", "recycling_lot", lot.lot_id, user.id, {"status": body.status})
    db.commit()
    return {"lot_id": lot.lot_id, "status": lot.current_status}
