from __future__ import annotations

from pathlib import Path

from app.config import Settings


def prepare_runtime_files(settings: Settings) -> None:
    storage_state_path = Path(settings.kwork_storage_state_path)
    storage_state_path.parent.mkdir(parents=True, exist_ok=True)

    if settings.kwork_storage_state_json:
        storage_state_path.write_text(settings.kwork_storage_state_json, encoding="utf-8")

    Path("data").mkdir(exist_ok=True)
