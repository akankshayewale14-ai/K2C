from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.providers.pricing.base import PriceProvider, PriceResult
from app.providers.pricing.database import DatabasePriceProvider


class PriceAggregator:
    def __init__(self, db: Session, extra: list[PriceProvider] | None = None):
        self.providers: list[PriceProvider] = [DatabasePriceProvider(db), *(extra or [])]

    def get_price(self, material: str, location: str, timestamp: datetime | None = None) -> Optional[PriceResult]:
        for provider in self.providers:
            if not provider.is_configured():
                continue
            result = provider.get_price(material, location, timestamp)
            if result:
                return result
        return None
