from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel


def model_hash(model: BaseModel) -> str:
    canonical = json.dumps(model.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
