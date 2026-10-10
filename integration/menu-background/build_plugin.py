#!/usr/bin/env python3
"""Compile the SEST Menu Background plugin.

    python3 integration/menu-background/build_plugin.py

Writes integration/menu-background/SEST.MenuBackground.dll, which
integration/campaign/build_pack.py copies into the pack's plugins/ folder.
The DLL is committed, like the Briefing Room film: the regression gate wants
the pack byte-identical on every machine, and a compiler's output is not
(mcs stamps a fresh module id on every build). Rebuild it only when
SestMenuBackground.cs changes.

Needs Mono's C# compiler (apt-get install mono-mcs). References:
  - UnityEngine.CoreModule and UnityEngine.VideoModule from the
    UnityEngine.Modules 2021.3.33 package on nuget.org (reference copies of
    Unity's public API, the .NET 4.5 build so mcs can read them; every member
    the plugin calls exists unchanged in the game's Unity 6000.0), fetched
    once into ~/.cache/sest and checked against the hash below;
  - stubs/AnchorChain.cs, compiled first: Anchor Chain's ACPlugin attribute
    and IAnchorChainMod interface.
Nothing from the game, BepInEx or Anchor Chain's own binaries is used or
shipped.
"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "SEST.MenuBackground.dll"
UNITY_PKG = ("https://api.nuget.org/v3-flatcontainer/unityengine.modules/2021.3.33/"
             "unityengine.modules.2021.3.33.nupkg")
UNITY_SHA256 = "d32d34526d89958c63220d3a5ce26c5c44c11bfd411a2e1fbc3200088ef160c4"
UNITY_DLLS = ("UnityEngine.CoreModule.dll", "UnityEngine.VideoModule.dll")
CACHE = Path.home() / ".cache" / "sest"


def unity_refs():
    pkg = CACHE / "unityengine.modules.2021.3.33.nupkg"
    if not pkg.is_file():
        CACHE.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(UNITY_PKG, timeout=120) as r:
            pkg.write_bytes(r.read())
    digest = hashlib.sha256(pkg.read_bytes()).hexdigest()
    if digest != UNITY_SHA256:
        sys.exit(f"{pkg}: sha256 {digest}, expected {UNITY_SHA256} - not the package this was built against")
    refs = CACHE / "unity-2021.3.33-net45"
    refs.mkdir(exist_ok=True)
    with zipfile.ZipFile(pkg) as z:
        for name in UNITY_DLLS:
            (refs / name).write_bytes(z.read(f"lib/net45/{name}"))
    return [refs / n for n in UNITY_DLLS]


def mcs(args):
    run = subprocess.run(["mcs", "-nologo", "-langversion:7", "-optimize+",
                          "-warnaserror+", *args], capture_output=True, text=True)
    if run.returncode != 0:
        sys.exit("mcs failed:\n" + run.stdout + run.stderr)


def main():
    if not shutil.which("mcs"):
        sys.exit("mcs not found - apt-get install mono-mcs")
    core, video = unity_refs()
    with tempfile.TemporaryDirectory() as tmp:
        stub = Path(tmp) / "AnchorChain.dll"
        mcs(["-target:library", f"-out:{stub}", str(HERE / "stubs" / "AnchorChain.cs")])
        mcs(["-target:library", f"-out:{OUT}", f"-r:{core}", f"-r:{video}", f"-r:{stub}",
             str(HERE / "SestMenuBackground.cs")])
    print(f"{OUT.relative_to(HERE.parent.parent)}: {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
