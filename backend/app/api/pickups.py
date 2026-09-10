from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.entities import CollectorProfile, Role, User
from app.schemas.main import PickupCreate, PickupOut, PickupStatusIn
from app.services.pickup import change_status, create_pickup, get_pickup, pickup_route
from app.services.serializers import pickup_out

router = APIRouter(prefix="/api/pickups", tags=["pickups"])


@router.post("", response_model=PickupOut)
def create(body: PickupCreate, user: User = Depends(require_roles(Role.CONSUMER, Role.BUSINESS)), db: Session = Depends(get_db)):
    pickup = create_pickup(db, user, body)
    db.commit()
    pickup = get_pickup(db, pickup.id, user)
    return pickup_out(pickup, pickup_route(db, pickup))


@router.get("/{pickup_id}", response_model=PickupOut)
def get_one(pickup_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pickup = get_pickup(db, pickup_id, user)
    return pickup_out(pickup, pickup_route(db, pickup))


@router.patch("/{pickup_id}/status", response_model=PickupOut)
def patch_status(
    pickup_id: UUID,
    body: PickupStatusIn,
    user: User = Depends(require_roles(Role.COLLECTOR, Role.ADMIN)),
    db: Session = Depends(get_db),
):
    pickup = get_pickup(db, pickup_id, user)
    if user.role == Role.COLLECTOR:
        profile = db.query(CollectorProfile).filter(CollectorProfile.user_id == user.id).first()
        if not pickup.assignment or pickup.assignment.collector_id != profile.id:
            from app.core.errors import forbidden

            raise forbidden("Not assigned to this pickup")
    change_status(db, pickup, body.status, user)
    db.commit()
    pickup = get_pickup(db, pickup_id, user)
    return pickup_out(pickup, pickup_route(db, pickup))
