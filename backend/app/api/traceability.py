from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.core.errors import not_found
from app.db.session import get_db
from app.models.entities import DataType, RecyclingLot
from app.schemas.main import TraceabilityOut

router = APIRouter(prefix="/api/traceability", tags=["traceability"])


@router.get("/{lot_id}", response_model=TraceabilityOut)
def get_lot(lot_id: str, db: Session = Depends(get_db)):
    lot = (
        db.query(RecyclingLot)
        .options(joinedload(RecyclingLot.events))
        .filter(RecyclingLot.lot_id == lot_id)
        .first()
    )
    if not lot:
        raise not_found("Lot not found")
    return {
        "lot_id": lot.lot_id,
        "current_status": lot.current_status,
        "initial_weight": lot.initial_weight,
        "current_weight": lot.current_weight,
        "data_type": DataType.DEMO,
        "events": [
            {
                "event_type": e.event_type,
                "timestamp": e.timestamp,
                "location": e.location,
                "weight": e.weight,
                "notes": e.notes,
            }
            for e in lot.events
        ],
    }
