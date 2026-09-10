from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt
from typing import Optional

from app.core.config import get_settings


@dataclass
class RouteEstimate:
    distance_km: float
    duration_min: int
    coordinates: list[list[float]]
    method: str
    provider_configured: bool


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = radians(a[0]), radians(a[1])
    lat2, lon2 = radians(b[0]), radians(b[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371 * 2 * atan2(sqrt(h), sqrt(1 - h))


class RoutingProvider(ABC):
    @abstractmethod
    def estimate(self, points: list[tuple[float, float]]) -> Optional[RouteEstimate]: ...


class HaversineRoutingProvider(RoutingProvider):
    def estimate(self, points: list[tuple[float, float]]) -> Optional[RouteEstimate]:
        if len(points) < 2:
            return None
        dist = 0.0
        for i in range(len(points) - 1):
            dist += haversine_km(points[i], points[i + 1])
        minutes = max(8, int(dist / 22 * 60))
        return RouteEstimate(
            distance_km=round(dist, 1),
            duration_min=minutes,
            coordinates=[[p[0], p[1]] for p in points],
            method="haversine",
            provider_configured=bool(get_settings().ROUTING_API_KEY),
        )


def get_routing_provider() -> RoutingProvider:
    return HaversineRoutingProvider()
