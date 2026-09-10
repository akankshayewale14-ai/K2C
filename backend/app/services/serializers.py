from app.models.entities import Offer, PickupRequest, ScrapListing, VerificationStatus


def verification_label(status: VerificationStatus | None, kind: str) -> str:
    if status == VerificationStatus.VERIFIED:
        return "Verified Collector" if kind == "collector" else "Authorization Verified"
    if status is None:
        return "Verification not submitted"
    return f"Authorization Not Verified ({status.value})" if kind == "recycler" else f"Unverified ({status.value})"


def offer_out(offer: Offer) -> dict:
    if offer.collector:
        user = offer.collector.user
        v = offer.collector.verification
        return {
            "id": offer.id,
            "listing_id": offer.listing_id,
            "buyer_type": "collector",
            "name": user.full_name if user else "Collector",
            "verification": verification_label(v.status if v else None, "collector"),
            "distance_km": offer.distance_km,
            "eta_label": f"{offer.eta_minutes} min" if offer.eta_minutes is not None else "ETA unavailable",
            "price_per_unit": offer.price_per_unit,
            "score": offer.score,
            "status": offer.status,
            "data_type": offer.data_type,
        }
    recycler = offer.recycler
    v = recycler.verification if recycler else None
    days = recycler.pickup_lead_days if recycler else None
    return {
        "id": offer.id,
        "listing_id": offer.listing_id,
        "buyer_type": "recycler",
        "name": recycler.organization_name if recycler else "Recycler",
        "verification": verification_label(v.status if v else None, "recycler"),
        "distance_km": offer.distance_km,
        "eta_label": f"{days} day lead" if days is not None else "Schedule on request",
        "price_per_unit": offer.price_per_unit,
        "score": offer.score,
        "status": offer.status,
        "data_type": offer.data_type,
    }


def scrap_out(listing: ScrapListing) -> dict:
    ident = listing.identification
    return {
        "id": listing.id,
        "status": listing.status,
        "material_id": listing.material_id,
        "quantity": listing.quantity,
        "unit": listing.unit,
        "location": listing.location,
        "area": listing.area,
        "estimated_low": listing.estimated_low,
        "estimated_high": listing.estimated_high,
        "identification_available": ident.available if ident else None,
        "identification_message": None,
    }


def pickup_out(pickup: PickupRequest, route: list[list[float]] | None = None) -> dict:
    assignment = pickup.assignment
    collector_name = None
    vehicle = None
    eta = None
    if assignment and assignment.collector:
        collector_name = assignment.collector.user.full_name if assignment.collector.user else None
        vehicle = assignment.vehicle_type or assignment.collector.vehicle_type
        eta = assignment.eta_minutes
    return {
        "id": pickup.id,
        "listing_id": pickup.listing_id,
        "status": pickup.status,
        "collector_name": collector_name,
        "vehicle_type": vehicle,
        "eta_minutes": eta,
        "area": pickup.area,
        "lat": pickup.lat,
        "lng": pickup.lng,
        "route": route,
        "data_note": "Route uses haversine estimates unless a routing API key is configured.",
    }
