from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExternalVerificationResult:
    available: bool
    status: Optional[str]
    source: Optional[str]
    message: str


class VerificationProvider(ABC):
    @abstractmethod
    def lookup(self, registration_number: str) -> ExternalVerificationResult: ...
