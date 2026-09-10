from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PriceResult:
    material: str
    location: str
    neighborhood: Optional[str]
    low: float
    high: float
    average: float
    currency: str
    unit: str
    source: str
    source_url: Optional[str]
    retrieved_at: datetime
    is_live: bool
    confidence: Optional[float]


class PriceProvider(ABC):
    key: str

    @abstractmethod
    def is_configured(self) -> bool: ...

    @abstractmethod
    def get_price(self, material: str, location: str, timestamp: datetime | None = None) -> Optional[PriceResult]: ...
