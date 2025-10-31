from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class Storage(ABC):
    @abstractmethod
    def save_bytes(self, relative_path: str, data: bytes) -> Path:
        """Persist bytes to storage and return absolute file path."""
        raise NotImplementedError


