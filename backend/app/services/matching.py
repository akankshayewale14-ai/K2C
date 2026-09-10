from math import inf

from sqlalchemy.orm import Session

from app.models.entities import CollectorProfile, Material, Offer, OfferStatus, RecyclerProfile, VerificationStatus
from app.providers.routing.factory import haversine_km


BENGALURU = (12.9716, 77.5946)


def _verified_collector(c: CollectorProfile) -> bool:
    return bool(c.verification and c.verification.status == VerificationStatus.VERIFIED)


def _verified_recycler(r: RecyclerProfile) -> bool:
    return bool(r.verification and r.verification.status == VerificationStatus.VERIFIED)


def generate_offers(db: Session, listing, material: Material | None) -> list[Offer]:
    origin = (listing.lat or BENGALURU[0], listing.lng or BENGALURU[1])
    slug = material.slug if material else None
    offers: list[Offer] = []

    for collector in db.query(CollectorProfile).all():
        if slug and collector.accepted_materials and slug not in collector.accepted_materials:
            continue
        dest = (collector.lat or BENGALURU[0], collector.lng or BENGALURU[1])
        dist = round(haversine_km(origin, dest), 1)
        verified = _verified_collector(collector)
        price_base = listing.estimated_low or 0
        price = round((price_base / max(listing.quantity or 1, 0.01)) * collector.payout_rate, 2) if listing.quantity else round(100 * collector.payout_rate, 2)
        if listing.estimated_low and listing.quantity:
            price = round((listing.estimated_low / listing.quantity) * collector.payout_rate, 2)
        eta = max(15, int(dist * 6 + 12))
        score = (price * 0.35) + ((20 - min(dist, 20)) * 4) + ((90 - min(eta, 90)) * 0.3) + (25 if verified else 0) + 10
        offers.append(
            Offer(
                listing_id=listing.id,
                collector_id=collector.id,
                price_per_unit=price,
                distance_km=dist,
                eta_minutes=eta,
                score=round(score, 2),
                status=OfferStatus.ACTIVE,
            )
        )

    for recycler in db.query(RecyclerProfile).all():
        if not recycler.pickup_available:
            continue
        accepted = [m.material_id for m in recycler.materials]
        if material and accepted and material.id not in accepted:
            continue
        dest = (recycler.lat or BENGALURU[0], recycler.lng or BENGALURU[1])
        dist = round(haversine_km(origin, dest), 1)
        verified = _verified_recycler(recycler)
        bid = next((m.price_per_unit for m in recycler.materials if material and m.material_id == material.id and m.price_per_unit), None)
        price = bid or (listing.estimated_high / listing.quantity if listing.estimated_high and listing.quantity else 0)
        eta_days = recycler.pickup_lead_days
        score = (float(price or 0) * 0.4) + ((25 - min(dist, 25)) * 3) + (20 if verified else 0)
        offers.append(
            Offer(
                listing_id=listing.id,
                recycler_id=recycler.id,
                price_per_unit=round(float(price or 0), 2),
                distance_km=dist,
                eta_minutes=eta_days * 24 * 60,
                score=round(score, 2),
                status=OfferStatus.ACTIVE,
            )
        )

    offers.sort(key=lambda o: o.score, reverse=True)
    return offers
