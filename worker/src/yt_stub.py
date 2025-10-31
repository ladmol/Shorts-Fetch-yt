from __future__ import annotations

from datetime import datetime, timezone


def generate_test_bytes(task_id: str | None = None) -> tuple[str, bytes]:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = task_id or "test"
    filename = f"{name}_{ts}.txt"
    content = f"test file generated at {ts} for task {name}\n".encode("utf-8")
    return filename, content


