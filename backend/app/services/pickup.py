from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.core.errors import bad_request, forbidden, not_found
from app.models.entities import (
    CollectorProfile,
    ListingStatus,
    Offer,
    OfferStatus,
    PickupAssignment,
    PickupRequest,
    PickupRoute,
    PickupStatus,
    RecyclingLot,
    ScrapListing,
    TraceabilityEvent,
    Transaction,
)
from app.providers.routing.factory import get_routing_provider
from app.services.pickup_fsm import transition
from app.services.system import audit, notify


def create_pickup(db: Session, user, data) -> PickupRequest:
    listing = db.get(ScrapListing, data.listing_id)
    if not listing:
        raise not_found("Listing not found")
    if listing.user_id != user.id:
        raise forbidden("You do not own this listing")
    if listing.status not in (ListingStatus.MATCHED, ListingStatus.ACTIVE):
        raise bad_request("Accept an offer before scheduling pickup")
    accepted = (
        db.query(Offer)
        .options(joinedload(Offer.collector))
        .filter(Offer.listing_id == listing.id, Offer.status == OfferStatus.ACCEPTED)
        .first()
    )
    pickup = PickupRequest(
        listing_id=listing.id,
        consumer_id=user.id,
        scheduled_at=data.scheduled_at,
        address=data.address,
        area=data.area or listing.area,
        lat=listing.lat,
        lng=listing.lng,
        status=PickupStatus.REQUESTED,
    )
    db.add(pickup)
    db.flush()
    if accepted and accepted.collector:
        db.add(
            PickupAssignment(
                pickup_id=pickup.id,
                collector_id=accepted.collector_id,
                eta_minutes=accepted.eta_minutes,
                vehicle_type=accepted.collector.vehicle_type,
            )
        )
        pickup.status = PickupStatus.ASSIGNED
        notify(db, accepted.collector.user_id, "Pickup assigned", "A new pickup is assigned to you.")
    listing.status = ListingStatus.PICKUP_SCHEDULED
    notify(db, user.id, "Pickup requested", "Your pickup request has been created.")
    audit(db, "pickup.create", "pickup_request", str(pickup.id), user.id)
    db.flush()
    return pickup


def get_pickup(db: Session, pickup_id: UUID, user) -> PickupRequest:
    pickup = (
        db.query(PickupRequest)
        .options(
            joinedload(PickupRequest.assignment).joinedload(PickupAssignment.collector),
            joinedload(PickupRequest.history),
        )
        .filter(PickupRequest.id == pickup_id)
        .first()
    )
    if not pickup:
        raise not_found("Pickup not found")
    collector_user_id = pickup.assignment.collector.user_id if pickup.assignment else None
    if user.role.value != "ADMIN" and pickup.consumer_id != user.id and collector_user_id != user.id:
        raise forbidden("Not allowed to view this pickup")
    return pickup


def pickup_route(db: Session, pickup: PickupRequest) -> list[list[float]] | None:
    assignment = pickup.assignment
    if not assignment or pickup.lat is None or pickup.lng is None:
        return None
    collector = assignment.collector
    points = [(collector.lat, collector.lng), (pickup.lat, pickup.lng)]
    if None in points[0] or None in points[1]:
        return None
    estimate = get_routing_provider().estimate(points)
    return estimate.coordinates if estimate else None


def change_status(db: Session, pickup: PickupRequest, new_status, actor):
    transition(db, pickup, new_status, actor.id)
    listing = db.get(ScrapListing, pickup.listing_id)
    if new_status == PickupStatus.ON_THE_WAY:
        notify(db, pickup.consumer_id, "Collector on the way", "Your collector is heading to the pickup location.")
    if new_status == PickupStatus.COLLECTED:
        listing.status = ListingStatus.COLLECTED
        notify(db, pickup.consumer_id, "Pickup collected", "Your scrap has been collected.")
        _open_lot(db, pickup, listing, actor.id)
    if new_status == PickupStatus.COMPLETED:
        listing.status = ListingStatus.COMPLETED
        notify(db, pickup.consumer_id, "Pickup completed", "This pickup is complete.")
        if pickup.assignment:
            pickup.assignment.collector.completed_pickups += 1
            amount = listing.estimated_low or 0
            db.add(
                Transaction(
                    listing_id=listing.id,
                    payer_id=pickup.consumer_id,
                    payee_id=pickup.assignment.collector.user_id,
                    amount=amount,
                    status="RECORDED",
                )
            )
    audit(db, "pickup.status", "pickup_request", str(pickup.id), actor.id, {"status": new_status.value})
    return pickup


def _open_lot(db: Session, pickup: PickupRequest, listing: ScrapListing, actor_id: UUID):
    existing = db.query(RecyclingLot).filter(RecyclingLot.scrap_listing_id == listing.id).first()
    if existing:
        return existing
    count = db.query(RecyclingLot).count() + 1
    lot = RecyclingLot(
        lot_id=f"BLR-LOT-{count:05d}",
        scrap_listing_id=listing.id,
        material_id=listing.material_id,
        initial_weight=listing.quantity,
        current_weight=listing.quantity,
        current_status="Collected",
    )
    db.add(lot)
    db.flush()
    db.add(
        TraceabilityEvent(
            lot_id=lot.id,
            event_type="Collected",
            location=listing.area or listing.location,
            weight=listing.quantity,
            actor_id=actor_id,
            notes="Material collected from consumer.",
        )
    )
    listing.status = ListingStatus.PROCESSING
    return lot


def batch_route(db: Session, collector: CollectorProfile) -> PickupRoute:
    pickups = (
        db.query(PickupRequest)
        .join(PickupAssignment)
        .filter(
            PickupAssignment.collector_id == collector.id,
            PickupRequest.status.in_([PickupStatus.ASSIGNED, PickupStatus.CONFIRMED, PickupStatus.ON_THE_WAY]),
        )
        .all()
    )
    origin = (collector.lat or 12.9716, collector.lng or 77.5946)
    points = [origin]
    ids = []
    earnings = 0.0
    for pickup in pickups:
        if pickup.lat is None or pickup.lng is None:
            continue
        points.append((pickup.lat, pickup.lng))
        ids.append(str(pickup.id))
        listing = db.get(ScrapListing, pickup.listing_id)
        if listing and listing.estimated_low:
            earnings += listing.estimated_low * collector.payout_rate
    estimate = get_routing_provider().estimate(points) if len(points) > 1 else None
    route = PickupRoute(
        collector_id=collector.id,
        pickup_ids=ids,
        coordinates=estimate.coordinates if estimate else [list(p) for p in points],
        total_distance_km=estimate.distance_km if estimate else 0,
        estimated_minutes=estimate.duration_min if estimate else 0,
        estimated_earnings=round(earnings, 2),
        method=estimate.method if estimate else "none",
    )
    db.add(route)
    db.flush()
    return route
