from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import bad_request
from app.models.entities import PickupStatus, PickupStatusHistory

ALLOWED = {
    PickupStatus.REQUESTED: {PickupStatus.ASSIGNED, PickupStatus.CANCELLED},
    PickupStatus.ASSIGNED: {PickupStatus.CONFIRMED, PickupStatus.CANCELLED},
    PickupStatus.CONFIRMED: {PickupStatus.ON_THE_WAY, PickupStatus.CANCELLED},
    PickupStatus.ON_THE_WAY: {PickupStatus.ARRIVED, PickupStatus.CANCELLED},
    PickupStatus.ARRIVED: {PickupStatus.COLLECTED, PickupStatus.CANCELLED},
    PickupStatus.COLLECTED: {PickupStatus.COMPLETED},
    PickupStatus.CANCELLED: set(),
    PickupStatus.COMPLETED: set(),
}


def transition(db: Session, pickup, new_status: PickupStatus, actor_id: UUID | None):
    current = pickup.status
    if new_status not in ALLOWED[current]:
        raise bad_request(f"Cannot change pickup from {current.value} to {new_status.value}")
    db.add(PickupStatusHistory(pickup_id=pickup.id, from_status=current.value, to_status=new_status.value, actor_id=actor_id))
    pickup.status = new_status
    return pickup
