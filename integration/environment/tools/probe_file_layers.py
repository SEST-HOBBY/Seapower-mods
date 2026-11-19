"""Probe Sea Power 0.9.x file layers: what can override a game file, where, and how files merge. BUILD-TESTED.

Nothing here is in-game tested. The probes decide whether a per-mission environment.ini [Sonar]
override can ever reach the game (docs/environment/SENSOR-PC-TESTS.md rows A-E). Standard library only.

    probe_file_layers.py scan-dll <Seapower-Scripts.dll | Assembly-CSharp.dll> [--out report.json]
        Reads the assembly's .NET metadata without loading it: type, field and method names
        about layers, overrides, mounts and missions, and every literal string ("user strings")
        that mentions them. That is where the folder names a layer uses are written.
    probe_file_layers.py scan-mods <folder> [--original <StreamingAssets/original>]
        Lists every overrides/ folder below <folder> (mods, Workshop content, StreamingAssets) and,
        per INI file, which sections and keys it adds, changes or leaves out against the original.
    probe_file_layers.py capture-env <StreamingAssets> [--out env.json]
        Records the installed environment.ini [Sonar] keys and the file's SHA-256 (the base for
        any later [Sonar] override, and the rollback check).
    probe_file_layers.py install <probe> --streaming-assets <SA> [--mission <mission.ini>] [--template T]
    probe_file_layers.py uninstall <probe|all> --streaming-assets <SA>
    probe_file_layers.py status --streaming-assets <SA>

Probes, in the order to try them (each installs a few files; uninstall removes exactly those, and
only if their SHA-256 still matches):
    A-mod     a local mod folder MNO_LayerProbe with overrides/language_en/aircraft_names.ini that
              renames the F-14A to "F-14A MNO-PROBE-A". Enable it in the Mod Manager. Shows that a
              mod layer works and whether language files merge by key (every other aircraft keeps
              its name) or are replaced whole (other aircraft lose their names).
    A-user1   the same sentinel ("MNO-PROBE-U1") in StreamingAssets/user/overrides/...
    A-user2   the same sentinel ("MNO-PROBE-U2") in StreamingAssets/user/language_en/... (a user layer
              without an overrides folder).
    A2        a local mod MNO_LayerProbeEnv with overrides/environment.ini holding ONLY [Sonar]
              BaseAmbientOceanNoise=90 (game value 60): GLOBAL, every mission. Passive detection
              ranges collapse if it is read; night lighting, sky and fog must look normal (key merge)
              or they break (whole-file replace: disable the mod at once).
    B1 B2 B3  per-mission candidates beside a mission file (--mission): the mission's first player
              ship class renamed "... MNO-PROBE-Bn" in a language file under
              B1 <dir>/<mission>/overrides/, B2 <dir>/<mission>_overrides/, B3 <dir>/overrides/<mission>/.
              --template overrides the location with a pattern from scan-dll ({dir}, {stem}).
    C         per-mission environment.ini with only [Sonar] BaseAmbientOceanNoise=90, at the location a
              B probe proved (--template, or --from B1/B2/B3).
    D         the same location, a full copy of the installed environment.ini with that one value changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE_DIR = HERE.parent / "out" / "layer-probes"
MANIFEST = "manifest.json"
FILTER = re.compile(r"overrid|layer|mount|mod[s]?folder|user[/\\]|missions?[/\\_]|\.ini|streamingassets|filemanager|openmission",
                    re.IGNORECASE)
TYPE_FILTER = re.compile(r"layer|override|mount|filemanager|modifier|inihandler|filesystem", re.IGNORECASE)


# ----------------------------------------------------------------------------- .NET metadata
class ClrMetadata:
    """Minimal ECMA-335 reader: streams, the #Strings and #US heaps, and the Module, TypeRef,
    TypeDef, Field and MethodDef tables (enough for type, enum-member and method names)."""

    def __init__(self, data: bytes):
        self.d = data
        if data[:2] != b"MZ":
            raise ValueError("not a PE file")
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        if data[pe:pe + 4] != b"PE\0\0":
            raise ValueError("no PE signature")
        nsec, opt_size = struct.unpack_from("<H", data, pe + 6)[0], struct.unpack_from("<H", data, pe + 20)[0]
        opt = pe + 24
        magic = struct.unpack_from("<H", data, opt)[0]
        dd = opt + (96 if magic == 0x10B else 112)
        cli_rva = struct.unpack_from("<I", data, dd + 14 * 8)[0]
        if not cli_rva:
            raise ValueError("not a .NET assembly (no CLI header)")
        self.sections = []
        sec = opt + opt_size
        for k in range(nsec):
            vsize, va, rsize, rptr = struct.unpack_from("<IIII", data, sec + k * 40 + 8)
            self.sections.append((va, max(vsize, rsize), rptr))
        cli = self.off(cli_rva)
        md_rva = struct.unpack_from("<I", data, cli + 8)[0]
        md = self.off(md_rva)
        if struct.unpack_from("<I", data, md)[0] != 0x424A5342:
            raise ValueError("bad metadata signature")
        vlen = struct.unpack_from("<I", data, md + 12)[0]
        p = md + 16 + vlen
        nstreams = struct.unpack_from("<H", data, p + 2)[0]
        p += 4
        self.streams = {}
        for _ in range(nstreams):
            off, size = struct.unpack_from("<II", data, p)
            p += 8
            end = data.index(b"\0", p)
            name = data[p:end].decode("ascii")
            p = (end + 4) & ~3
            self.streams[name] = (md + off, size)
        self._tables()

    def off(self, rva: int) -> int:
        for va, size, raw in self.sections:
            if va <= rva < va + size:
                return rva - va + raw
        raise ValueError(f"RVA {rva:#x} outside every section")

    def string(self, idx: int) -> str:
        base, _ = self.streams["#Strings"]
        end = self.d.index(b"\0", base + idx)
        return self.d[base + idx:end].decode("utf-8", "replace")

    def user_strings(self) -> list[str]:
        if "#US" not in self.streams:
            return []
        base, size = self.streams["#US"]
        out, p = [], base + 1
        while p < base + size:
            b0 = self.d[p]
            if b0 & 0x80 == 0:
                n, h = b0, 1
            elif b0 & 0xC0 == 0x80:
                n, h = ((b0 & 0x3F) << 8) | self.d[p + 1], 2
            else:
                n, h = ((b0 & 0x1F) << 24) | (self.d[p + 1] << 16) | (self.d[p + 2] << 8) | self.d[p + 3], 4
            if n == 0:
                p += h
                continue
            raw = self.d[p + h:p + h + n - 1]
            out.append(raw.decode("utf-16-le", "replace"))
            p += h + n
        return out

    def _tables(self):
        base, _ = self.streams.get("#~") or self.streams["#-"]
        d = self.d
        heap = d[base + 6]
        valid = struct.unpack_from("<Q", d, base + 8)[0]
        p = base + 24
        rows = {}
        for t in range(64):
            if valid >> t & 1:
                rows[t] = struct.unpack_from("<I", d, p)[0]
                p += 4
        self.rows = rows
        s = 4 if heap & 1 else 2
        g = 4 if heap & 2 else 2
        b = 4 if heap & 4 else 2

        def idx(t):
            return 2 if rows.get(t, 0) < 1 << 16 else 4

        def coded(tables, bits):
            return 2 if max(rows.get(t, 0) for t in tables) < 1 << (16 - bits) else 4
        rs = coded([0x00, 0x1A, 0x23, 0x01], 2)
        tdor = coded([0x02, 0x01, 0x1B], 2)
        sizes = {0x00: 2 + s + 3 * g, 0x01: rs + 2 * s, 0x02: 4 + 2 * s + tdor + idx(0x04) + idx(0x06),
                 0x03: idx(0x04), 0x04: 2 + s + b, 0x05: idx(0x06), 0x06: 4 + 2 + 2 + s + b + idx(0x08)}
        self.layout = {"s": s, "tdor": tdor, "field_idx": idx(0x04), "method_idx": idx(0x06)}
        starts = {}
        for t in sorted(rows):
            if t > 0x06:
                break
            starts[t] = p
            p += sizes[t] * rows[t]
        self.starts, self.sizes = starts, sizes

    def _u(self, p, n):
        return struct.unpack_from("<H" if n == 2 else "<I", self.d, p)[0]

    def types(self) -> list[dict]:
        """Every TypeDef with its namespace, field names and method names."""
        L, s = self.layout, self.layout["s"]
        n = self.rows.get(0x02, 0)
        recs = []
        for k in range(n):
            p = self.starts[0x02] + k * self.sizes[0x02]
            name = self.string(self._u(p + 4, s))
            ns = self.string(self._u(p + 4 + s, s))
            q = p + 4 + 2 * s + L["tdor"]
            fl = self._u(q, L["field_idx"])
            ml = self._u(q + L["field_idx"], L["method_idx"])
            recs.append([ns, name, fl, ml])
        nf, nm = self.rows.get(0x04, 0), self.rows.get(0x06, 0)
        out = []
        for k, (ns, name, fl, ml) in enumerate(recs):
            fe = recs[k + 1][2] if k + 1 < len(recs) else nf + 1
            me = recs[k + 1][3] if k + 1 < len(recs) else nm + 1
            fields = [self.string(self._u(self.starts[0x04] + (i - 1) * self.sizes[0x04] + 2, s)) for i in range(fl, fe) if 0 < i <= nf]
            methods = [self.string(self._u(self.starts[0x06] + (i - 1) * self.sizes[0x06] + 8, s)) for i in range(ml, me) if 0 < i <= nm]
            out.append({"namespace": ns, "name": name, "fields": fields, "methods": methods})
        return out


def scan_dll(path: Path) -> dict:
    meta = ClrMetadata(path.read_bytes())
    types = [t for t in meta.types() if TYPE_FILTER.search(t["name"])]
    strings = sorted({u for u in meta.user_strings() if FILTER.search(u) and len(u) < 300})
    return {"assembly": str(path), "sha256": sha256_file(path), "types": types, "user_strings": strings,
            "note": "Names and literals only, read from metadata without running the assembly. Enum members are the "
                    "field names of a type such as LayerKind (value__ is the storage field)."}


# ----------------------------------------------------------------------------- INI helpers
def parse_ini(text: str) -> dict:
    out, sec = {}, None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith((";", "#", "//")):
            continue
        m = re.match(r"\[([^\]]+)\]", line)
        if m:
            sec = m.group(1).strip()
            out.setdefault(sec, {})
            continue
        if sec is not None and "=" in line:
            k, v = line.split("=", 1)
            out[sec][k.strip()] = v.split("//")[0].strip()
    return out


def sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def scan_mods(root: Path, original: Path | None) -> list[dict]:
    found = []
    for dirpath, dirnames, _files in os.walk(root):
        if Path(dirpath).name.lower() == "overrides":
            dirnames[:] = []
            for f in sorted(Path(dirpath).rglob("*")):
                if not f.is_file():
                    continue
                rel = f.relative_to(dirpath).as_posix()
                rec = {"layer": str(Path(dirpath)), "file": rel, "bytes": f.stat().st_size}
                if f.suffix.lower() == ".ini":
                    mine = parse_ini(f.read_text(encoding="utf-8", errors="replace"))
                    rec["sections"] = len(mine)
                    if original and (original / rel).is_file():
                        base = parse_ini((original / rel).read_text(encoding="utf-8", errors="replace"))
                        added = changed = 0
                        for sec, kv in mine.items():
                            for k, v in kv.items():
                                if k not in base.get(sec, {}):
                                    added += 1
                                elif base[sec][k] != v:
                                    changed += 1
                        rec.update({"keys_added": added, "keys_changed": changed,
                                    "original_sections_left_out": sum(1 for s in base if s not in mine),
                                    "partial": len(mine) < len(base)})
                found.append(rec)
    return found


def capture_env(sa: Path) -> dict:
    env = sa / "original" / "environment.ini"
    sec = parse_ini(env.read_text(encoding="utf-8", errors="replace"))
    return {"file": str(env), "sha256": sha256_file(env), "sections": list(sec), "sonar": sec.get("Sonar", {})}


# ----------------------------------------------------------------------------- probes
def _replace_name(line_value: str, tag: str) -> str:
    first, _, rest = line_value.partition(",")
    return f"{first} {tag}" + (f",{rest}" if rest else "")


def _mission_ship(mission: Path) -> tuple[str, str | None]:
    sec = parse_ini(mission.read_text(encoding="utf-8", errors="replace"))
    for name in ("Taskforce1Vessel1", "Taskforce1Vessel2"):
        if name in sec and "Type" in sec[name]:
            return sec[name]["Type"], sec[name].get("VariantReference")
    raise ValueError(f"{mission.name}: no Taskforce1Vessel1 Type to rename")


def _language_patch(sa: Path, file: str, section: str, keys: list[str], tag: str) -> str:
    base = parse_ini((sa / "original" / "language_en" / file).read_text(encoding="utf-8", errors="replace"))
    if section not in base:
        raise ValueError(f"[{section}] not in original/language_en/{file}")
    lines = [f"; MNO layer probe ({tag}). Remove with probe_file_layers.py uninstall.", f"[{section}]"]
    for k in keys:
        if k in base[section]:
            lines.append(f"{k}={_replace_name(base[section][k], tag)}")
    return "\n".join(lines) + "\n"


def _info(name: str) -> str:
    return (f"[Language_en]\nName={name}\nDescription=MNO file-layer probe. Test only: disable and delete after the test.\n\n"
            "[Compatibility]\nApproximateVersion=0.9.0\n")


SONAR_SENTINEL = "; MNO layer probe: [Sonar] sentinel. Remove with probe_file_layers.py uninstall.\n[Sonar]\nBaseAmbientOceanNoise=90\n"


def probe_files(name: str, sa: Path, mission: Path | None, template: str | None) -> dict:
    """Relative path (to StreamingAssets, or absolute for per-mission probes) -> file text."""
    if name == "A-mod":
        return {"MNO_LayerProbe/_info.ini": _info("MNO Layer Probe A"),
                "MNO_LayerProbe/overrides/language_en/aircraft_names.ini":
                    _language_patch(sa, "aircraft_names.ini", "usn_f-14a", ["Default"], "MNO-PROBE-A")}
    if name == "A-user1":
        return {"user/overrides/language_en/aircraft_names.ini": _language_patch(sa, "aircraft_names.ini", "usn_f-14a", ["Default"], "MNO-PROBE-U1")}
    if name == "A-user2":
        return {"user/language_en/aircraft_names.ini": _language_patch(sa, "aircraft_names.ini", "usn_f-14a", ["Default"], "MNO-PROBE-U2")}
    if name == "A2":
        return {"MNO_LayerProbeEnv/_info.ini": _info("MNO Layer Probe Env (GLOBAL sonar sentinel)"),
                "MNO_LayerProbeEnv/overrides/environment.ini": SONAR_SENTINEL}
    if name in ("B1", "B2", "B3", "C", "D"):
        if mission is None:
            raise ValueError(f"{name} needs --mission <the mission .ini>")
        tmpl = template or {"B1": "{dir}/{stem}/overrides", "B2": "{dir}/{stem}_overrides", "B3": "{dir}/overrides/{stem}"}.get(name)
        if tmpl is None:
            raise ValueError(f"{name} needs --template (the location a B probe proved) or --from B1/B2/B3")
        root = tmpl.format(dir=str(mission.parent).replace("\\", "/"), stem=mission.stem)
        if name.startswith("B"):
            typ, variant = _mission_ship(mission)
            keys = ["Default"] + ([variant] if variant else [])
            return {f"{root}/language_en/vessel_names.ini": _language_patch(sa, "vessel_names.ini", typ, keys, f"MNO-PROBE-{name}")}
        if name == "C":
            return {f"{root}/environment.ini": SONAR_SENTINEL}
        full = (sa / "original" / "environment.ini").read_text(encoding="utf-8", errors="replace")
        new, n = re.subn(r"(?m)^(BaseAmbientOceanNoise\s*=\s*)[0-9.]+", r"\g<1>90", full, count=1)
        if n != 1:
            raise ValueError("installed environment.ini has no BaseAmbientOceanNoise line")
        return {f"{root}/environment.ini": "; MNO layer probe D: full copy, BaseAmbientOceanNoise=90.\n" + new}
    raise ValueError(f"unknown probe {name!r}")


LOOK_FOR = {
    "A-mod": "Enable 'MNO Layer Probe A' in the Mod Manager. In the Mission Editor the F-14A shows as 'F-14A MNO-PROBE-A'. "
             "Check other aircraft still have their names (key merge) - if names went blank, layers replace whole files.",
    "A-user1": "F-14A shows 'F-14A MNO-PROBE-U1' (no Mod Manager step). Other aircraft names must be intact.",
    "A-user2": "F-14A shows 'F-14A MNO-PROBE-U2'. Other aircraft names must be intact.",
    "A2": "Enable 'MNO Layer Probe Env' in the Mod Manager. GLOBAL: in any deep-water mission passive detection ranges collapse "
          "(+30 dB ambient). Night lighting, sky and fog must look normal; if they do not, the file replaced environment.ini whole: "
          "disable the mod at once and uninstall.",
    "B": "Start the mission: its first player ship class shows '... MNO-PROBE-Bn'. Then load a vanilla mission in the same session: "
         "the name must be normal there (no leak).",
    "C": "In the mission, passive detection ranges collapse (+30 dB). Check Player.log for errors first; check night, sky and fog.",
    "D": "As C, with a full copy of environment.ini.",
}


def _state(sa: Path) -> tuple[Path, dict]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    mf = STATE_DIR / MANIFEST
    doc = json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else {"streaming_assets": str(sa), "probes": {}}
    return mf, doc


def install(name: str, sa: Path, mission: Path | None, template: str | None) -> dict:
    files = probe_files(name, sa, mission, template)
    targets = {(Path(rel) if Path(rel).is_absolute() else sa / rel): text for rel, text in files.items()}
    clash = [str(t) for t in targets if t.exists()]
    if clash:
        raise SystemExit("refused: these files already exist, nothing was written:\n  " + "\n  ".join(clash))
    mf, doc = _state(sa)
    if name in doc["probes"]:
        raise SystemExit(f"refused: probe {name} is already installed; uninstall it first")
    made_dirs, rec = [], []
    for t, text in targets.items():
        missing = []
        d = t.parent
        while not d.exists():
            missing.append(d)
            d = d.parent
        t.parent.mkdir(parents=True, exist_ok=True)
        made_dirs += [str(x) for x in reversed(missing)]
        t.write_text(text, encoding="utf-8")
        rec.append({"path": str(t), "sha256": sha256_file(t)})
    doc["probes"][name] = {"files": rec, "made_dirs": made_dirs, "look_for": LOOK_FOR.get(name[:1] if name[0] in "B" else name, "")}
    mf.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return doc["probes"][name]


def uninstall(name: str, sa: Path) -> list[str]:
    mf, doc = _state(sa)
    names = list(doc["probes"]) if name == "all" else [name]
    report, dirs = [], []
    for n in names:
        p = doc["probes"].get(n)
        if not p:
            report.append(f"{n}: not installed")
            continue
        ok = True
        for f in p["files"]:
            path = Path(f["path"])
            if not path.exists():
                report.append(f"{n}: already gone {path}")
            elif sha256_file(path) != f["sha256"]:
                ok = False
                report.append(f"{n}: REFUSED to delete {path}: it changed since install (check it by hand)")
            else:
                path.unlink()
                report.append(f"{n}: deleted {path}")
        dirs += [(n, d) for d in p["made_dirs"]]
        if ok:
            del doc["probes"][n]
    # folders last, deepest first, across every probe removed (two probes can share a parent)
    for n, d in sorted(dirs, key=lambda x: len(x[1]), reverse=True):
        dp = Path(d)
        if dp.exists() and dp.is_dir() and not any(dp.iterdir()):
            dp.rmdir()
            report.append(f"{n}: removed empty folder {dp}")
    mf.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return report


def status(sa: Path) -> list[str]:
    _, doc = _state(sa)
    if not doc["probes"]:
        return ["no probe installed"]
    out = []
    for n, p in doc["probes"].items():
        for f in p["files"]:
            path = Path(f["path"])
            st = "missing" if not path.exists() else ("ok" if sha256_file(path) == f["sha256"] else "CHANGED")
            out.append(f"{n}: {st}  {path}")
        out.append(f"{n}: look for: {p['look_for']}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("scan-dll")
    a.add_argument("dll", type=Path)
    a.add_argument("--out", type=Path)
    a = sub.add_parser("scan-mods")
    a.add_argument("folder", type=Path)
    a.add_argument("--original", type=Path)
    a.add_argument("--out", type=Path)
    a = sub.add_parser("capture-env")
    a.add_argument("streaming_assets", type=Path)
    a.add_argument("--out", type=Path)
    for c in ("install", "uninstall"):
        a = sub.add_parser(c)
        a.add_argument("probe")
        a.add_argument("--streaming-assets", type=Path, required=True)
        if c == "install":
            a.add_argument("--mission", type=Path)
            a.add_argument("--template")
            a.add_argument("--from", dest="from_probe", choices=["B1", "B2", "B3"])
    a = sub.add_parser("status")
    a.add_argument("--streaming-assets", type=Path, required=True)
    args = ap.parse_args(argv)

    def emit(obj, out):
        text = json.dumps(obj, indent=1, ensure_ascii=False)
        if out:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
            print(f"wrote {out}")
        else:
            print(text)
    if args.cmd == "scan-dll":
        emit(scan_dll(args.dll), args.out)
    elif args.cmd == "scan-mods":
        emit(scan_mods(args.folder, args.original), args.out)
    elif args.cmd == "capture-env":
        emit(capture_env(args.streaming_assets), args.out)
    elif args.cmd == "install":
        tmpl = args.template
        if args.from_probe and not tmpl:
            tmpl = {"B1": "{dir}/{stem}/overrides", "B2": "{dir}/{stem}_overrides", "B3": "{dir}/overrides/{stem}"}[args.from_probe]
        rec = install(args.probe, args.streaming_assets, args.mission, tmpl)
        for f in rec["files"]:
            print(f"installed {f['path']}")
        print("look for:", rec["look_for"])
    elif args.cmd == "uninstall":
        print("\n".join(uninstall(args.probe, args.streaming_assets)))
    else:
        print("\n".join(status(args.streaming_assets)))


if __name__ == "__main__":
    sys.exit(main())
