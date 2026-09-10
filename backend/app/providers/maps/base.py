from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class MapConfig:
    tile_url: str
    attribution: str
    provider_configured: bool
    note: str


class MapProvider(ABC):
    @abstractmethod
    def public_config(self) -> MapConfig: ...
