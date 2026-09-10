from app.core.config import get_settings
from app.providers.maps.base import MapConfig, MapProvider


class OpenStreetMapProvider(MapProvider):
    def public_config(self) -> MapConfig:
        settings = get_settings()
        configured = bool(settings.MAP_API_KEY)
        return MapConfig(
            tile_url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            attribution="© OpenStreetMap contributors",
            provider_configured=configured,
            note="Using OpenStreetMap tiles. Set MAP_API_KEY to switch to a commercial map provider.",
        )


def get_map_provider() -> MapProvider:
    return OpenStreetMapProvider()
