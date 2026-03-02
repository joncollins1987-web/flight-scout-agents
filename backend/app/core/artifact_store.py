from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import settings


class ArtifactStore:
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        self.base_dir = settings.runs_dir / run_id
        self.evidence_dir = self.base_dir / "evidence"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.base_dir / "logs.ndjson"

    def write_json(self, filename: str, payload: Any) -> Path:
        path = self.base_dir / filename
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, default=str)
        return path

    def append_log(self, event: str, payload: dict[str, Any]) -> None:
        line = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "payload": payload,
        }
        with self.log_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(line, default=str) + "\n")

    def evidence_path(self, name: str) -> Path:
        return self.evidence_dir / name
