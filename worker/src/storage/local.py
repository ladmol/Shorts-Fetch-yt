from __future__ import annotations

from pathlib import Path

from .base import Storage


class LocalStorage(Storage):
    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_bytes(self, relative_path: str, data: bytes) -> Path:
        destination_path = self.base_dir / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_bytes(data)
        return destination_path.resolve()


