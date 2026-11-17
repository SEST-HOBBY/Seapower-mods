# Imported prototype, 18 November 2026

This folder is the supplied `MNO_GCO_Environment_Prototype_20261118.zip`
(SHA-256 `d37759446f2fea1dd0dcf0dc2b62cc3a17cc77fb113f58bafd3fafcaa34f775a`) with its
sources kept unchanged. Three generated or binary files are not committed because the
generator reproduces them:

| File in the ZIP | Why it is not here | Check |
|---|---|---|
| `data/demo_environment.json` (1,793,135 bytes) | `tools/build_demo.py` regenerates it | `integration/environment/tests/test_prototype_import.py` rebuilds it and compares with the SHA-256 in `MANIFEST.json` (`f266be84...`) |
| `web/MNO_GCO_ENV_VIEWER.html` (1,893,581 bytes) | `tools/build_demo.py` embeds the demo JSON and coastlines into `web/template.html` | run the builder, open the file offline |
| `web/screenshot-*.png` (three, about 1.1 MB) | screenshots of the viewer, not inputs | kept in the owner's ZIP |

Everything here is a **SYNTHETIC DEMONSTRATION, NOT REAL WEATHER**. The maintained code is
in `integration/environment/mno_env/`; this folder is the reference it was built from.
The coastline file is Natural Earth low-resolution (public domain).
