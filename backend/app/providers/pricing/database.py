from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.entities import DataType, Material, MaterialPrice
from app.providers.pricing.base import PriceProvider, PriceResult


class DatabasePriceProvider(PriceProvider):
    key = "database"

    def __init__(self, db: Session):
        self.db = db

    def is_configured(self) -> bool:
        return self.db.query(MaterialPrice).first() is not None

    def get_price(self, material: str, location: str, timestamp: datetime | None = None) -> Optional[PriceResult]:
        mat = self.db.query(Material).filter(Material.slug == material).first()
        if not mat:
            return None
        row = (
            self.db.query(MaterialPrice)
            .filter(MaterialPrice.material_id == mat.id, MaterialPrice.location == location, MaterialPrice.neighborhood.is_(None))
            .order_by(MaterialPrice.retrieved_at.desc())
            .first()
        )
        if not row:
            return None
        return PriceResult(
            material=mat.slug,
            location=row.location,
            neighborhood=row.neighborhood,
            low=row.low,
            high=row.high,
            average=row.average,
            currency=row.currency,
            unit=row.unit,
            source=row.source,
            source_url=row.source_url,
            retrieved_at=row.retrieved_at or datetime.now(timezone.utc),
            is_live=row.data_type == DataType.LIVE,
            confidence=row.confidence,
        )
