# R12: include the UI feature code in the Steam update

The canonical Workshop tree now contains the R11 feature code and its setup
workflow. The five reviewed beta DLLs are in beta-support/SEST-Beta-Features.zip,
with a pinned archive/entry manifest. Normal SETUP invokes the feature installer
on the inspected game hash; normal-release active plugins remain in plugins/.
Extraction is outside Workshop/game directories. This avoids duplicate active
assembly names while distributing the new features in the same Steam item.

A new installation uses the existing stage/menu-probe/enable workflow. An
existing enabled installation is repaired in one run. The repair recognises
only an exact canonical Steam refresh of Runtime/UI with the previously
journalled loader/bootstrap and a retained or originally-added missing shim.
It preserves the original restore journal/backups. Unknown installed code and
changed native/author references are refused. Copy failure restores the observed
files and journal, including absence of a shim. No native saves are edited.

The subscriber fixture covers unsupported-build no-op, tampered archive,
protected cache path, first install, menu probe, Identify migration, Steam
refresh, injected-copy rollback, unknown code rejection and full restore.
Normal SETUP's existing fixture also checks the game/library/player path
handoff. Native rendering and gameplay still need PC acceptance.

The PC toolkit also records successful preparation before Upload-PC can stage
a fresh top-level StreamingAssets publishing copy. Both source and copy are
verified. Finish-Upload copies all observed content out, verifies that copy,
then removes only the recorded temporary folder. The publisher fixture checks
missing preparation, direct picker placement, inclusion of the feature bundle,
duplicate refusal, preservation of uploader changes, unrelated-file preservation,
idempotent cleanup and changed canonical payload rejection (10 assertions).

Verification for this revision: 350 campaign tests; 339 tools tests (17 skipped);
15 managed/installer groups; all 4,337 canonical files hash-checked. Native game
acceptance and Steam submission remain pending.

## 9 November configuration refresh

The 17:33 capture contains three changed upstream text files: BetterTacMap's
settings file gained eight hotkey documentation blocks without changing any
setting values, and the English/German Pop-Out Windows files gained menu and
Back labels. The captured bytes, export byte totals and all-mod fingerprint
baseline are now reconciled. The author-update check is retained.

All 331 supplied reference files match their capture hashes. All 15 recorded
R12 build references match this capture. The existing R12 loader already
recognises the captured Topographic Map 1.6.0 globe/flat images and the runtime
already recognises Pop-Out Windows 1.2.0 by exact hash. The five beta payload
DLLs and the canonical Workshop upload bytes are unchanged.

The captured logs describe the older Topography 1.5.1 / Pop-Out 1.1.3 session,
with pre-R12 runtime hash `2fdc0251…`; they do not validate this candidate.
The DCM salvo-hold error is a pre-R12 finding addressed by R12's existing
adapter. One campaign AI pause recovered after 7.4 seconds. Fresh PC gameplay,
world/battle return, save/load, F11 and second-monitor checks remain pending.

Detailed evidence is in `r12-refresh-reference-review.json`. The toolkit's
refresh validation distinguishes checks rerun here from the original R12
managed/installer results retained for the unchanged binaries.
