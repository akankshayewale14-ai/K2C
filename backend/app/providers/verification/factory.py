from app.providers.verification.base import ExternalVerificationResult, VerificationProvider


class UnconfiguredVerificationProvider(VerificationProvider):
    def lookup(self, registration_number: str) -> ExternalVerificationResult:
        return ExternalVerificationResult(
            available=False,
            status=None,
            source=None,
            message="External verification lookup is not configured. Status is stored from submitted records only.",
        )


def get_verification_provider() -> VerificationProvider:
    return UnconfiguredVerificationProvider()
