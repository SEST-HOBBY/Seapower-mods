"""Put a validated feature installer INSIDE the canonical Workshop pack.

Five own DLLs remain compressed in an inert archive until normal SETUP
installs the hash-reviewed code using its existing probe/restore workflow.
Never places a second active assembly in plugins/.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--package", type=Path, required=True)
a = p.parse_args()
expected = {"AnchorChain.dll", "SEST.BetaSafeBootstrap.dll", "SEST.RuntimeFixes.dll",
            "SEST.ContactsFix.dll", "SEST.IdentifyDataPaths.dll"}
raw = a.package.read_bytes()
with zipfile.ZipFile(a.package) as z:
    assert z.testzip() is None
    names = z.namelist()
    assert len(names) == len(set(n.lower() for n in names))
    assert {Path(n).name for n in names if n.endswith(".dll")} == expected
    assert not any(n.startswith("/") or ".." in Path(n).parts for n in names)
    receipt = json.loads(z.read("payload/build-receipt.json"))
    validation = json.loads(z.read("VALIDATION.json"))
    assert validation["tested_files"] == receipt["files"]
    assert all(r["exit_code"] == 0 for r in validation["results"])
    assert receipt["candidate_revision"].startswith("R12-")
    for name in expected:
        assert hashlib.sha256(z.read("payload/" + name)).hexdigest() == receipt["files"][name]
    manifest = {
        "format": 1, "workshop_item_id": "3812461539",
        "revision": receipt["candidate_revision"],
        "archive": "SEST-Beta-Features.zip",
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "target_game_sha256": receipt["target_game_sha256"],
        "files": {name: hashlib.sha256(z.read(name)).hexdigest() for name in sorted(names)},
        "features": ["World Operations", "world service ribbons", "Coordinated Strike styling and weapon estimates"],
    }
source = ROOT / "integration/campaign/setup/beta-support"
source.mkdir(parents=True, exist_ok=True)
(source / manifest["archive"]).write_bytes(raw)
(source / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
(source / "README.txt").write_text("""SEST WORKSHOP FEATURE UPDATE

The new F11 World Operations, service progress and Coordinated Strike
refinements are included in this Workshop item.

With Sea Power closed, run SETUP - double-click me.cmd at the pack root.
On the supported beta build, a fresh installation stages the features:
launch to the main menu, wait about ten seconds, quit, then run SETUP again.
An existing enabled installation is updated in one SETUP run. Run SETUP
again after Steam updates this item to reapply its bundled beta features.

The normal-release plugins remain in plugins/. This archive stays inactive
until SETUP recognises the supported build and verifies all required files.
SETUP does not change your Steam branch, native game DLLs or save files.
Existing restore backups and Identify data are retained.

Unknown game or author DLL versions are not forced. Keep any error for review.
Native rendering and gameplay still require PC acceptance testing.
""")
for pack in (ROOT / "integration/campaign/SEST_Campaign", ROOT / "integration/dist/SEST_Integration"):
    for setup_file in sorted((ROOT / "integration/campaign/setup").iterdir()):
        if setup_file.is_file():
            shutil.copyfile(setup_file, pack / setup_file.name)
    shutil.copytree(source, pack / "beta-support", dirs_exist_ok=True)
print("Workshop feature bundle included:", len(raw), "bytes; 5 owned DLLs; normal SETUP wired")
