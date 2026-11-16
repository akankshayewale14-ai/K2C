from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.entities import (
    CollectorProfile,
    ConsumerProfile,
    DataType,
    Material,
    MaterialPrice,
    PriceSource,
    RecyclerMaterial,
    RecyclerProfile,
    RecyclingLot,
    Role,
    TraceabilityEvent,
    User,
    VerificationRecord,
    VerificationStatus,
    BusinessProfile,
)

NOW = datetime.now(timezone.utc)

MATERIALS = [
    ("copper", "Copper", "metal"),
    ("aluminium", "Aluminium", "metal"),
    ("iron", "Iron", "metal"),
    ("cardboard", "Cardboard", "fibre"),
    ("ewaste", "E-Waste", "electronics"),
    ("plastic", "Plastic", "polymer"),
]

# Prototype seed ranges for Satara. data_type=DEMO. Not live market feeds.
CITY_PRICES = {
    "copper": (550, 610, 580, 585, 0.89, [540, 552, 568, 575, 580, 588, 585]),
    "aluminium": (145, 175, 160, 162, 0.84, [150, 154, 158, 161, 160, 163, 162]),
    "iron": (28, 38, 33, 34, 0.8, [30, 31, 32, 33, 33, 34, 34]),
    "cardboard": (8, 14, 11, 11.5, 0.76, [9, 10, 10.5, 11, 11, 11.5, 11.5]),
    "ewaste": (40, 95, 68, 70, 0.71, [55, 58, 62, 65, 68, 70, 70]),
    "plastic": (12, 22, 17, 17.5, 0.74, [14, 15, 16, 16.5, 17, 17.5, 17.5]),
}

NEIGHBORHOODS = {
    "copper": {"Whitefield": 588, "Electronic City": 572, "Peenya": 565, "Malleswaram": 580},
    "aluminium": {"Whitefield": 164, "Electronic City": 158, "Peenya": 155, "Malleswaram": 161},
}


def seed(db: Session) -> None:
    if db.query(Material).first():
        return
    mats = {}
    for slug, name, category in MATERIALS:
        m = Material(slug=slug, name=name, unit="kg", category=category)
        db.add(m)
        db.flush()
        mats[slug] = m

    db.add(PriceSource(name="Seeded Satara prototype table", source_url=None, provider_key="database", is_configured=True))

    for slug, (low, high, avg, rec, conf, chart) in CITY_PRICES.items():
        db.add(
            MaterialPrice(
                material_id=mats[slug].id,
                location="Satara",
                neighborhood=None,
                low=low,
                high=high,
                average=avg,
                recommended=rec,
                source="Prototype seed — Satara demo table",
                source_url=None,
                retrieved_at=NOW,
                data_type=DataType.DEMO,
                confidence=conf,
                chart_points=chart,
            )
        )
        for area, price in NEIGHBORHOODS.get(slug, {}).items():
            db.add(
                MaterialPrice(
                    material_id=mats[slug].id,
                    location="Satara",
                    neighborhood=area,
                    low=price - 8,
                    high=price + 8,
                    average=price,
                    recommended=price,
                    source="Prototype seed — neighborhood demo table",
                    retrieved_at=NOW,
                    data_type=DataType.DEMO,
                    confidence=None,
                    chart_points=[],
                )
            )

    password = hash_password("DemoPass123!")

    def user(email, name, role, phone=None):
        u = User(email=email, hashed_password=password, full_name=name, role=role, phone=phone)
        db.add(u)
        db.flush()
        return u

    consumer = user("ananya@kabadiwala.local", "Ananya Rao", Role.CONSUMER, "9000000001")
    db.add(ConsumerProfile(user_id=consumer.id, area="Whitefield", address="Whitefield, Satara", lat=12.9698, lng=77.7500))

    ravi = user("ravi@kabadiwala.local", "Ravi Kumar", Role.COLLECTOR, "9000000002")
    ravi_p = CollectorProfile(
        user_id=ravi.id,
        vehicle_type="Tempo",
        service_areas=["Whitefield", "Mahadevapura"],
        lat=12.9784,
        lng=77.7272,
        accepted_materials=["copper", "aluminium", "iron", "cardboard", "plastic"],
        payout_rate=0.93,
        rating=4.7,
        completed_pickups=128,
    )
    db.add(ravi_p)
    db.flush()
    db.add(
        VerificationRecord(
            collector_id=ravi_p.id,
            status=VerificationStatus.VERIFIED,
            authority_name="Platform KYC",
            verification_source="Seeded verification record",
            verification_date=NOW - timedelta(days=40),
            notes="DEMO verification record",
        )
    )

    meera = user("meera@kabadiwala.local", "Meera N", Role.COLLECTOR, "9000000003")
    meera_p = CollectorProfile(
        user_id=meera.id,
        vehicle_type="Pickup van",
        service_areas=["Electronic City", "Bommanahalli"],
        lat=12.8458,
        lng=77.6651,
        accepted_materials=["ewaste", "copper", "aluminium"],
        payout_rate=0.91,
        rating=4.5,
        completed_pickups=76,
    )
    db.add(meera_p)
    db.flush()
    db.add(
        VerificationRecord(
            collector_id=meera_p.id,
            status=VerificationStatus.VERIFIED,
            authority_name="Platform KYC",
            verification_source="Seeded verification record",
            verification_date=NOW - timedelta(days=20),
        )
    )

    recycler_u = user("peenya@kabadiwala.local", "Peenya Metals Desk", Role.RECYCLER, "9000000004")
    rec = RecyclerProfile(
        user_id=recycler_u.id,
        organization_name="Peenya Metals",
        location="Peenya, Satara",
        lat=13.0285,
        lng=77.5197,
        pickup_lead_days=1,
        pickup_available=True,
        authority_name="KSPCB (record as submitted)",
        registration_number="KSPCB-DEMO-1044",
        verification_source="Seeded recycler file — not a government endorsement",
    )
    db.add(rec)
    db.flush()
    db.add(
        VerificationRecord(
            recycler_id=rec.id,
            status=VerificationStatus.VERIFIED,
            authority_name=rec.authority_name,
            registration_number=rec.registration_number,
            verification_source=rec.verification_source,
            verification_date=NOW - timedelta(days=90),
        )
    )
    for slug, price in [("copper", 575), ("aluminium", 168), ("iron", 35), ("ewaste", 72)]:
        db.add(RecyclerMaterial(recycler_id=rec.id, material_id=mats[slug].id, price_per_unit=price, min_quantity=5))

    biz = user("itpark@kabadiwala.local", "Whitefield IT Park Admin", Role.BUSINESS, "9000000005")
    db.add(BusinessProfile(user_id=biz.id, organization_name="Whitefield IT Park", organization_type="IT company", address="Whitefield"))

    user("admin@kabadiwala.local", "Platform Admin", Role.ADMIN, "9000000000")

    lot = RecyclingLot(
        lot_id="BLR-EW-2026-00827",
        scrap_listing_id=None,  # type: ignore
        material_id=mats["ewaste"].id,
        initial_weight=18,
        current_weight=17.2,
        current_status="Processing",
    )
    # scrap_listing_id is required FK - create a listing
    from app.models.entities import ScrapListing, ListingStatus

    listing = ScrapListing(
        user_id=consumer.id,
        material_id=mats["ewaste"].id,
        quantity=18,
        unit="kg",
        location="Satara",
        area="Whitefield",
        status=ListingStatus.PROCESSING,
        estimated_low=720,
        estimated_high=1710,
        lat=12.9698,
        lng=77.7500,
        description="DEMO seeded listing for traceability",
    )
    db.add(listing)
    db.flush()
    lot.scrap_listing_id = listing.id
    db.add(lot)
    db.flush()
    events = [
        ("Listed", NOW - timedelta(days=6), "Whitefield", 18, "Consumer listed e-waste. DEMO lot."),
        ("Collected", NOW - timedelta(days=5), "Whitefield", 18, "Collector pickup completed."),
        ("Received by recycler", NOW - timedelta(days=4), "Peenya", 17.6, "Weighed at recycler gate."),
        ("Processing", NOW - timedelta(days=2), "Peenya", 17.2, "Dismantling in progress."),
    ]
    for name, ts, loc, w, notes in events:
        db.add(TraceabilityEvent(lot_id=lot.id, event_type=name, timestamp=ts, location=loc, weight=w, notes=notes))
    db.commit()
