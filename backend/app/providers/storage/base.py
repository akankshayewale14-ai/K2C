from abc import ABC, abstractmethod
from pathlib import Path


class StorageProvider(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes, content_type: str) -> str: ...

    @abstractmethod
    def path_for(self, key: str) -> Path: ...
