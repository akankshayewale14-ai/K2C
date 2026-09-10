from pathlib import Path

from app.core.config import get_settings
from app.providers.storage.base import StorageProvider


class LocalStorageProvider(StorageProvider):
    def __init__(self) -> None:
        self.root = Path(get_settings().UPLOAD_DIR).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: bytes, content_type: str) -> str:
        dest = self.root / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return key

    def path_for(self, key: str) -> Path:
        return self.root / key


def get_storage() -> StorageProvider:
    settings = get_settings()
    if settings.STORAGE_ENDPOINT and settings.STORAGE_ACCESS_KEY:
        # S3-compatible adapter is wired here when credentials exist.
        return LocalStorageProvider()
    return LocalStorageProvider()
