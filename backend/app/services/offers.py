from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.core.errors import bad_request, forbidden, not_found
from app.models.entities import (
    ListingStatus,
    Material,
    Offer,
    OfferStatus,
    ScrapListing,
    VerificationStatus,
)
from app.services.matching import generate_offers
from app.services.system import audit, notify


def listing_offers(db: Session, listing_id: UUID, user_id: UUID) -> list[Offer]:
    listing = db.get(ScrapListing, listing_id)
    if not listing:
        raise not_found("Listing not found")
    if listing.user_id != user_id:
        raise forbidden("You do not own this listing")
    existing = (
        db.query(Offer)
        .options(
            joinedload(Offer.collector),
            joinedload(Offer.recycler),
        )
        .filter(Offer.listing_id == listing_id)
        .all()
    )
    if existing:
        return sorted(existing, key=lambda o: o.score, reverse=True)
    material = db.get(Material, listing.material_id) if listing.material_id else None
    offers = generate_offers(db, listing, material)
    for offer in offers:
        db.add(offer)
    db.flush()
    if offers:
        notify(db, user_id, "Offers ready", f"{len(offers)} buyers are available for your listing.")
    return offers


def accept_offer(db: Session, offer_id: UUID, user_id: UUID) -> Offer:
    offer = (
        db.query(Offer)
        .options(joinedload(Offer.collector), joinedload(Offer.recycler), joinedload(Offer.listing))
        .filter(Offer.id == offer_id)
        .first()
    )
    if not offer:
        raise not_found("Offer not found")
    listing = offer.listing
    if listing.user_id != user_id:
        raise forbidden("You do not own this listing")
    if offer.status != OfferStatus.ACTIVE:
        raise bad_request("Offer is no longer active")
    if listing.status not in (ListingStatus.ACTIVE, ListingStatus.DRAFT):
        raise bad_request("Listing is not open for matching")
    if offer.collector:
        v = offer.collector.verification
        if v and v.status in (VerificationStatus.SUSPENDED, VerificationStatus.REJECTED, VerificationStatus.EXPIRED):
            raise bad_request("Collector is not eligible")
        if offer.collector.accepted_materials and listing.material_id:
            material = db.get(Material, listing.material_id)
            if material and material.slug not in offer.collector.accepted_materials:
                raise bad_request("Collector does not accept this material")
    if offer.recycler:
        v = offer.recycler.verification
        if v and v.status in (VerificationStatus.SUSPENDED, VerificationStatus.REJECTED):
            raise bad_request("Recycler is not eligible")
        if not offer.recycler.pickup_available:
            raise bad_request("Recycler pickup is not available")
    for other in db.query(Offer).filter(Offer.listing_id == listing.id, Offer.id != offer.id):
        other.status = OfferStatus.REJECTED
    offer.status = OfferStatus.ACCEPTED
    listing.status = ListingStatus.MATCHED
    buyer_user = offer.collector.user_id if offer.collector else offer.recycler.user_id
    notify(db, buyer_user, "Offer accepted", "A consumer selected your offer.")
    notify(db, user_id, "Buyer selected", "You accepted an offer. Schedule pickup next.")
    audit(db, "offer.accept", "offer", str(offer.id), user_id)
    return offer
