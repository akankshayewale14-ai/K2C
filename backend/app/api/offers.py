from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.entities import CollectorProfile, Offer, RecyclerProfile, User
from app.schemas.main import OfferOut
from app.services.offers import accept_offer, listing_offers
from app.services.serializers import offer_out

router = APIRouter(prefix="/api/offers", tags=["offers"])


@router.get("", response_model=list[OfferOut])
def list_offers(
    listing_id: UUID = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    offers = listing_offers(db, listing_id, user.id)
    db.commit()
    hydrated = (
        db.query(Offer)
        .options(
            joinedload(Offer.collector).joinedload(CollectorProfile.user),
            joinedload(Offer.collector).joinedload(CollectorProfile.verification),
            joinedload(Offer.recycler).joinedload(RecyclerProfile.verification),
        )
        .filter(Offer.listing_id == listing_id)
        .all()
    )
    return [offer_out(o) for o in sorted(hydrated, key=lambda x: x.score, reverse=True)]


@router.post("/{offer_id}/accept", response_model=OfferOut)
def accept(offer_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    offer = accept_offer(db, offer_id, user.id)
    db.commit()
    db.refresh(offer)
    return offer_out(offer)
