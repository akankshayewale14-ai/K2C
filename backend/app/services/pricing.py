from datetime import datetime

from sqlalchemy.orm import Session

from app.models.entities import DataType, Material, MaterialPrice
from app.providers.pricing.aggregator import PriceAggregator


def price_payload(db: Session, slug: str, location: str, timestamp: datetime | None = None) -> dict | None:
    material = db.query(Material).filter(Material.slug == slug).first()
    if not material:
        return None
    result = PriceAggregator(db).get_price(slug, location, timestamp)
    if not result:
        return None
    row = (
        db.query(MaterialPrice)
        .filter(
            MaterialPrice.material_id == material.id,
            MaterialPrice.location == location,
            MaterialPrice.neighborhood.is_(None),
        )
        .order_by(MaterialPrice.retrieved_at.desc())
        .first()
    )
    neighborhoods = (
        db.query(MaterialPrice)
        .filter(
            MaterialPrice.material_id == material.id,
            MaterialPrice.location == location,
            MaterialPrice.neighborhood.isnot(None),
        )
        .order_by(MaterialPrice.neighborhood.asc())
        .all()
    )
    return {
        "material": material.slug,
        "material_name": material.name,
        "location": result.location,
        "unit": result.unit,
        "low": result.low,
        "high": result.high,
        "average": result.average,
        "recommended": row.recommended if row else result.average,
        "currency": result.currency,
        "source": result.source,
        "source_url": result.source_url,
        "retrieved_at": result.retrieved_at,
        "data_type": row.data_type if row else DataType.DEMO,
        "is_live": result.is_live,
        "confidence": result.confidence,
        "chart_points": row.chart_points if row and row.chart_points else [],
        "neighborhoods": [
            {"area": n.neighborhood, "price": n.average, "data_type": n.data_type} for n in neighborhoods
        ],
    }
