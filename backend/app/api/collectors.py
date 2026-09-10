from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, require_roles
from app.core.errors import not_found
from app.db.session import get_db
from app.models.entities import CollectorProfile, PickupAssignment, PickupRequest, PickupStatus, Role, User
from app.services.pickup import batch_route
from app.services.serializers import verification_label

router = APIRouter(prefix="/api/collectors", tags=["collectors"])


def _out(c: CollectorProfile) -> dict:
    v = c.verification
    return {
        "id": c.id,
        "name": c.user.full_name if c.user else "Collector",
        "vehicle_type": c.vehicle_type,
        "service_areas": c.service_areas or [],
        "rating": c.rating,
        "completed_pickups": c.completed_pickups,
        "verification": verification_label(v.status if v else None, "collector"),
        "lat": c.lat,
        "lng": c.lng,
    }


@router.get("")
def list_collectors(db: Session = Depends(get_db)):
    rows = db.query(CollectorProfile).options(joinedload(CollectorProfile.user), joinedload(CollectorProfile.verification)).all()
    return [_out(c) for c in rows]


@router.get("/me/dashboard")
def dashboard(user: User = Depends(require_roles(Role.COLLECTOR)), db: Session = Depends(get_db)):
    profile = db.query(CollectorProfile).filter(CollectorProfile.user_id == user.id).first()
    if not profile:
        raise not_found("Collector profile not found")
    jobs = (
        db.query(PickupRequest)
        .join(PickupAssignment)
        .filter(PickupAssignment.collector_id == profile.id)
        .all()
    )
    open_jobs = [j for j in jobs if j.status not in (PickupStatus.COMPLETED, PickupStatus.CANCELLED)]
    expected = 0.0
    for job in open_jobs:
        listing = job.listing_id
        from app.models.entities import ScrapListing

        listing = db.get(ScrapListing, job.listing_id)
        if listing and listing.estimated_low:
            expected += listing.estimated_low * profile.payout_rate
    return {
        "name": user.full_name,
        "available_pickups": len(open_jobs),
        "expected_earnings": round(expected, 2),
        "completed_pickups": profile.completed_pickups,
        "rating": profile.rating,
        "verification": verification_label(profile.verification.status if profile.verification else None, "collector"),
        "jobs": [
            {
                "id": j.id,
                "status": j.status,
                "area": j.area,
                "eta_minutes": j.assignment.eta_minutes if j.assignment else None,
            }
            for j in open_jobs
        ],
    }


@router.post("/me/route")
def optimize_route(user: User = Depends(require_roles(Role.COLLECTOR)), db: Session = Depends(get_db)):
    profile = db.query(CollectorProfile).filter(CollectorProfile.user_id == user.id).first()
    if not profile:
        raise not_found("Collector profile not found")
    route = batch_route(db, profile)
    db.commit()
    return {
        "pickup_ids": route.pickup_ids,
        "coordinates": route.coordinates,
        "total_distance_km": route.total_distance_km,
        "estimated_minutes": route.estimated_minutes,
        "estimated_earnings": route.estimated_earnings,
        "method": route.method,
        "data_note": "Batched with haversine estimates. Not an AI optimizer.",
    }
