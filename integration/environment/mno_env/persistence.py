"""MnoEnvPersistence: one environment sidecar per GCO save. BUILD-TESTED (offline).

The Dynamic Campaign Mod's save format is not ours to extend, so the environment lives in a
sidecar file named after the save's own id, in a folder MNO owns:

    <root>/<campaign id>/<save id>.mno-env.json

It is written atomically (temp file, flush, fsync, replace) and carries its own SHA-256. A
missing sidecar is normal for a save made before the feature existed: the save stays
playable and gets a deterministic default derived from its ids. A corrupt sidecar is never
silently overwritten: it is kept as is, the load reports a warning, and the same
deterministic default is used until the player saves again.

How a save id is obtained from DCM at run time is BLOCKED (needs the DCM 0.25.0.1 listing on
0.9.3); this module takes it as a string.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import RULES_VERSION

SCHEMA = "mno.environment.save.v1"
SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,96}$")


@dataclass
class EnvSaveState:
    campaign_id: str
    save_id: str
    seed: str
    mode: str = "procedural"            # procedural | historical_analogue | current_analogue | synthetic_demo
    dataset_id: str | None = None       # snapshot_id of a cached dataset, when not procedural
    dataset_sha256: str | None = None
    offset_seconds: int = 0
    campaign_seconds: int = 0           # last campaign UTC the environment was evaluated at
    last_source_time_utc: str | None = None
    rules_version: str = RULES_VERSION
    forecast: dict = field(default_factory=dict)   # per-side intelligence state (forecast.py)
    events: list = field(default_factory=list)     # environment events already resolved in this save

    def body(self) -> dict:
        return asdict(self)


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def default_state(campaign_id: str, save_id: str, campaign_seconds: int = 0) -> EnvSaveState:
    seed = hashlib.sha256(f"mno-env|{campaign_id}|{save_id}".encode()).hexdigest()[:16]
    return EnvSaveState(campaign_id=campaign_id, save_id=save_id, seed=seed, campaign_seconds=campaign_seconds)


class MnoEnvPersistence:
    def __init__(self, root: Path):
        self.root = Path(root)

    def path(self, campaign_id: str, save_id: str) -> Path:
        for v in (campaign_id, save_id):
            if not SAFE_ID.match(v):
                raise ValueError(f"unsafe id {v!r}: ids become file names")
        return self.root / campaign_id / f"{save_id}.mno-env.json"

    def save(self, state: EnvSaveState) -> Path:
        body = state.body()
        doc = {"schema": SCHEMA, "body": body, "sha256": hashlib.sha256(_canon(body)).hexdigest()}
        path = self.path(state.campaign_id, state.save_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        with open(tmp, "wb") as fh:
            fh.write(json.dumps(doc, sort_keys=True, indent=1).encode("utf-8"))
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
        return path

    def load(self, campaign_id: str, save_id: str, campaign_seconds: int = 0) -> tuple[EnvSaveState, str | None]:
        """Return (state, warning). warning is None for a clean load."""
        path = self.path(campaign_id, save_id)
        if not path.exists():
            return default_state(campaign_id, save_id, campaign_seconds), "no environment sidecar for this save; using its deterministic default"
        try:
            doc = json.loads(path.read_bytes().decode("utf-8"))
            body = doc["body"]
            if doc.get("schema") != SCHEMA:
                raise ValueError(f"schema {doc.get('schema')!r}")
            if hashlib.sha256(_canon(body)).hexdigest() != doc.get("sha256"):
                raise ValueError("checksum mismatch")
            if body.get("campaign_id") != campaign_id or body.get("save_id") != save_id:
                raise ValueError("sidecar belongs to another save")
            state = EnvSaveState(**body)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            return default_state(campaign_id, save_id, campaign_seconds), f"environment sidecar unreadable ({exc}); kept untouched, using the deterministic default"
        warning = None
        if state.rules_version != RULES_VERSION:
            warning = f"sidecar written under {state.rules_version}; current rules {RULES_VERSION}"
        return state, warning

    def save_as(self, state: EnvSaveState, new_save_id: str) -> EnvSaveState:
        """A copy for a new save slot. The seed stays (same weather history), the id changes."""
        copy = EnvSaveState(**{**state.body(), "save_id": new_save_id})
        self.save(copy)
        return copy

    def delete(self, campaign_id: str, save_id: str) -> bool:
        path = self.path(campaign_id, save_id)
        if path.exists():
            path.unlink()
            return True
        return False
