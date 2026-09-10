from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class IdentificationResult:
    available: bool
    material_slug: Optional[str]
    confidence: Optional[float]
    condition: Optional[str]
    provider: str
    message: Optional[str]
    metadata: Optional[dict]


class MaterialIdentificationProvider(ABC):
    @abstractmethod
    def identify(self, filename: str, content_type: str) -> IdentificationResult: ...
