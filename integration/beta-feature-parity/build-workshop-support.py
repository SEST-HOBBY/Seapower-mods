"""Put a validated feature installer INSIDE the canonical Workshop pack.

Five own DLLs remain compressed in an inert archive until normal SETUP
installs the hash-reviewed code using its existing probe/restore workflow.
Never places a second active assembly in plugins/.

Every check is explicit (it also runs under python -O), and the text files
are written as UTF-8 with LF line endings on every platform, so a run on
Windows produces the same bytes the upload manifest records.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# The candidate revisions a bundle may carry (R12 Final, then R13 onwards).
REVISIONS = ("R12-", "R13-")
# The game builds a bundle may target, as players read them in Player.log.
GAME_LABELS = {
    "499675cda59912054924ae42297bce7a82b12ca00957dabd684105a24aa353a9": "0.8.7-261107",
}
EXPECTED = {"AnchorChain.dll", "SEST.BetaSafeBootstrap.dll", "SEST.RuntimeFixes.dll",
            "SEST.ContactsFix.dll", "SEST.IdentifyDataPaths.dll"}
# The pack-root launchers SETUP's feature step names; they must ship.
LAUNCHERS = ("SETUP - double-click me.cmd", "SEST beta features - turn off.cmd",
             "SEST beta features - remove.cmd", "SEST beta features - turn on.cmd")


def check(ok, why):
    if not ok:
        raise SystemExit("build-workshop-support: " + why)


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--package", type=Path, required=True)
a = p.parse_args()
raw = a.package.read_bytes()
with zipfile.ZipFile(a.package) as z:
    check(z.testzip() is None, "the package ZIP is damaged")
    names = z.namelist()
    check(len(names) == len(set(n.lower() for n in names)), "the package has entries that differ only in case")
    check({Path(n).name for n in names if n.lower().endswith(".dll")} == EXPECTED,
          "the package's DLLs are not exactly the five SEST files")
    check(not any(n.startswith("/") or ".." in Path(n).parts for n in names), "the package has an unsafe entry name")
    for required in ("payload/build-receipt.json", "VALIDATION.json", "Install-SEST-Beta.ps1",
                     "Repair-SEST-Beta-Startup.ps1", "repair-receipt.json"):
        check(required in names, "the package has no " + required)
    receipt = json.loads(z.read("payload/build-receipt.json"))
    validation = json.loads(z.read("VALIDATION.json"))
    check(validation.get("tested_files") == receipt.get("files"), "VALIDATION.json belongs to different payload bytes")
    results = validation.get("results") or []
    check(bool(results) and all(r.get("exit_code") == 0 for r in results), "VALIDATION.json records a failed or missing check")
    check(any(r.get("name") == "workshop-setup-feature-step" for r in results),
          "VALIDATION.json has no workshop-setup-feature-step result (run verify.py from this source)")
    check(str(receipt.get("candidate_revision", "")).startswith(REVISIONS), "the receipt is not an R12 or R13 revision")
    for name in sorted(EXPECTED):
        check(hashlib.sha256(z.read("payload/" + name)).hexdigest() == receipt["files"][name],
              name + " differs from its build receipt")
    target = receipt.get("target_game_sha256", "")
    check(target in GAME_LABELS, "no player-facing label for target game " + target[:12] + "; add it to GAME_LABELS")
    manifest = {
        "format": 1, "workshop_item_id": "3812461539",
        "revision": receipt["candidate_revision"],
        "archive": "SEST-Beta-Features.zip",
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "target_game_sha256": target,
        "target_game_label": GAME_LABELS[target],
        "files": {name: hashlib.sha256(z.read(name)).hexdigest() for name in sorted(names)},
        "features": ["World Operations", "world service ribbons", "Coordinated Strike styling and weapon estimates"],
    }
setup_dir = ROOT / "integration/campaign/setup"
for launcher in LAUNCHERS:
    check((setup_dir / launcher).is_file(), "integration/campaign/setup has no " + launcher)
source = setup_dir / "beta-support"
source.mkdir(parents=True, exist_ok=True)
(source / manifest["archive"]).write_bytes(raw)
write_text(source / "manifest.json", json.dumps(manifest, indent=2) + "\n")
write_text(source / "README.txt", """SEST WORKSHOP FEATURE UPDATE

The F11 World Operations, service progress and Coordinated Strike
refinements are included in this Workshop item for the public beta
""" + manifest["target_game_label"] + """ only. The stable game uses the normal plugins in plugins/.

With Sea Power closed, run SETUP - double-click me.cmd at the pack root.
On that beta build a fresh installation stages the features: launch to the
main menu, wait about ten seconds, quit, then run SETUP again. An enabled
installation is updated in one SETUP run; run SETUP again after Steam
updates this item. On any other game build SETUP puts the normal SEST
plugins back if the beta files are installed.

What SETUP changes on that beta build: it adds SEST.BetaSafeBootstrap.dll to
BepInEx\\plugins and SEST's modified Anchor Chain to
BepInEx\\config\\SEST-BetaAnchorChain, replaces SEST's own plugins in this
item's plugins/ folder, rewrites the Mod Manager order without the local
IdentifyExpanded row (Identify Expanded and this pack stay on) and moves a
local StreamingAssets\\IdentifyExpanded folder to
%LOCALAPPDATA%\\SEST\\IdentifyExpanded. Everything is backed up first under
%LOCALAPPDATA%\\SEST\\BetaCompatibility. It does not change your Steam
branch, native game DLLs or saves, and it does not force unknown game or
author DLL versions: SETUP then says which file needs a SEST update.

To opt out, run one of these at the pack root (game closed); SETUP then
leaves the features off, also after Steam updates:
  SEST beta features - turn off.cmd   loader off, files kept
  SEST beta features - remove.cmd     normal SEST plugins back, beta files removed
  SEST beta features - turn on.cmd    on again (runs SETUP)
On this beta build Workshop code mods load only through SEST's beta loader,
so with the features off they stay off too; data mods and campaigns work.

Native rendering and gameplay still require PC acceptance testing.
""")
for pack in (ROOT / "integration/campaign/SEST_Campaign", ROOT / "integration/dist/SEST_Integration"):
    for setup_file in sorted(setup_dir.iterdir()):
        if setup_file.is_file():
            shutil.copyfile(setup_file, pack / setup_file.name)
    shutil.copytree(source, pack / "beta-support", dirs_exist_ok=True)
print("Workshop feature bundle included:", len(raw), "bytes; 5 owned DLLs; normal SETUP wired")
