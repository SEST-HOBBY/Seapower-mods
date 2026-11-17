"""MnoEnvDataProvider: local snapshot cache with a manifest, and offline fallback. BUILD-TESTED.

The game side only ever reads this folder. Downloads and conversions are separate tools
(integration/environment/tools/*), never run from a render or update loop.

    <cache>/manifest.json          {"schema": "mno.environment.cache.v1", "snapshots": [...]}
    <cache>/<snapshot_id>.json.gz  one sealed mno.environment.snapshot.v1 each

resolve() never raises for a data problem: a missing, corrupt or invalid snapshot yields
the seeded procedural field and a reason, so a campaign always loads.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from . import procedural, snapshot

CACHE_SCHEMA = "mno.environment.cache.v1"


class CacheError(Exception):
    pass


@dataclass(frozen=True)
class Resolved:
    snapshot: dict
    source: str          # "cache" | "procedural-fallback"
    reason: str | None   # why the fallback was used


class MnoEnvDataProvider:
    def __init__(self, root: Path):
        self.root = Path(root)

    @property
    def manifest_path(self) -> Path:
        return self.root / "manifest.json"

    def manifest(self) -> dict:
        if not self.manifest_path.exists():
            return {"schema": CACHE_SCHEMA, "snapshots": []}
        try:
            m = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise CacheError(f"manifest unreadable: {exc}") from None
        if m.get("schema") != CACHE_SCHEMA or not isinstance(m.get("snapshots"), list):
            raise CacheError("manifest has the wrong schema")
        return m

    def add(self, snap: dict) -> dict:
        errors = snapshot.validate(snap)
        if errors:
            raise CacheError("refusing an invalid snapshot: " + "; ".join(errors[:5]))
        sid = snap["snapshot_id"]
        if not all(c.isalnum() or c in "-_.:" for c in sid):
            raise CacheError(f"snapshot id {sid!r} is not file-name safe")
        name = sid.replace(":", "") + ".json.gz"
        digest = snapshot.write(snap, self.root / name)
        m = self.manifest()
        m["snapshots"] = [e for e in m["snapshots"] if e["snapshot_id"] != sid]
        m["snapshots"].append({"snapshot_id": sid, "file": name, "sha256": digest, "bytes": (self.root / name).stat().st_size,
                               "data_class": snap["data_class"], "provider": snap["provenance"]["provider"],
                               "product": snap["provenance"]["product"], "licence": snap["provenance"]["licence"],
                               "first_valid_utc": snap["times"][0]["valid_utc"], "last_valid_utc": snap["times"][-1]["valid_utc"],
                               "payload_sha256": snap["integrity"]["payload_sha256"]})
        m["snapshots"].sort(key=lambda e: e["snapshot_id"])
        tmp = self.manifest_path.with_name("manifest.json.tmp")
        tmp.write_text(json.dumps(m, indent=1, sort_keys=True), encoding="utf-8")
        tmp.replace(self.manifest_path)
        return m

    def load(self, snapshot_id: str, expect_sha256: str | None = None) -> dict:
        entry = next((e for e in self.manifest()["snapshots"] if e["snapshot_id"] == snapshot_id), None)
        if entry is None:
            raise CacheError(f"{snapshot_id} not in the cache manifest")
        path = self.root / entry["file"]
        if not path.exists():
            raise CacheError(f"{entry['file']} listed but missing")
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != entry["sha256"]:
            raise CacheError(f"{entry['file']} is corrupt (sha256 {digest[:12]} != manifest {entry['sha256'][:12]})")
        if expect_sha256 and digest != expect_sha256:
            raise CacheError(f"{entry['file']} is not the version this save was made with")
        snap = snapshot.read(path)
        errors = snapshot.validate(snap)
        if errors:
            raise CacheError(f"{entry['file']} fails validation: {errors[0]}")
        return snap

    def resolve(self, snapshot_id: str | None, expect_sha256: str | None, seed: str, campaign_start: dt.datetime,
                hours: int = 72) -> Resolved:
        if snapshot_id:
            try:
                return Resolved(self.load(snapshot_id, expect_sha256), "cache", None)
            except CacheError as exc:
                reason = str(exc)
        else:
            reason = "no dataset selected for this save"
        start = campaign_start.replace(minute=0, second=0, microsecond=0)
        start -= dt.timedelta(hours=start.hour % 6)
        return Resolved(procedural.generate(seed, start, hours=hours), "procedural-fallback", reason)
