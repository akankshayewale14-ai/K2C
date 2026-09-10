from app.core.config import get_settings
from app.providers.ai.base import IdentificationResult, MaterialIdentificationProvider


class UnconfiguredAIProvider(MaterialIdentificationProvider):
    def identify(self, filename: str, content_type: str) -> IdentificationResult:
        return IdentificationResult(
            available=False,
            material_slug=None,
            confidence=None,
            condition=None,
            provider="none",
            message="Automatic identification is currently unavailable. Select the material manually.",
            metadata=None,
        )


def get_identification_provider() -> MaterialIdentificationProvider:
    settings = get_settings()
    if settings.AI_API_KEY and settings.AI_PROVIDER not in ("", "none"):
        # Real provider adapters are added here when credentials are supplied.
        return UnconfiguredAIProvider()
    return UnconfiguredAIProvider()
