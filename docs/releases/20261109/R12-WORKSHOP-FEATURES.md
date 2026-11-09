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
