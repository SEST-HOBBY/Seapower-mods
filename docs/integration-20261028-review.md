# Integration of the owner's PC state, 28 Oct 2026

The working state on the owner's PC (GPT's 27 Oct handoff, PRs #47 to #51)
is now built from the repository's own sources on `sest-dev/jolly-ride-rptj4t`,
so a `tools/build_all.py --from-scratch` reproduces it instead of reverting
it. Nothing here has been uploaded to the Workshop, and none of it has been
seen in game beyond what the owner's PC already ran.

The review behind this is the owner's document *SEST review: GPT's 27 Oct
work and PRs #47 to #51* (27 Oct 2026). Each piece below was built and
gated on its own branch, then checked by a second reviewer, before being
combined.

## What landed, and where it lives now

| Piece | Source location | On the PC before | Seen in game |
| --- | --- | --- | --- |
| Runtime 1.5.0 (`7ba6d6d9`) | `integration/runtime-fixes/` as a captured binary; `build_plugin.py` refuses to replace it | Yes, hand-installed | On the PC only |
| SEST UI Follow-up 1.4.2 (`SEST.ContactsFix.dll`, `51b56f5e`) | `integration/ui-followup/` (source, DLL, manifest); `build_pack.write_contacts_fix` ships it | Yes, hand-installed | On the PC only |
| SETUP version rule | `integration/campaign/setup/sest-setup.ps1` | No (GPT's REDFOR-only script) | No |
| Contact Log key unbinding | `integration/campaign/setup/sest-ui-keys.ps1` | GPT's version, which also remapped Topographic Map | No |
| Sulu Line airfields, H-76, MH-60R, deck fits | `integration/campaign/sulu_line/`, `integration/cross-deck/build_pack.py` | Hand-edited files | No |
| World Sandbox P-8As as real Poseidons (PR #47) | `integration/world-sandbox/build_dynamic_campaign.py` | No | No |
| World Sandbox builds twice in a row | same | n/a (a build bug of 25 Oct) | n/a |
| P-8 Harpoon guidance link | `integration/allied-fixes/build_patch.py` | Hand-edited files | No |
| Globe beta audit (PR #49, reworked) | `tools/audit_beta_map_geometry.py` | n/a (developer tool) | n/a |

## Not taken from PRs #50 and #51, and why

- **99 of PR #50's files** with no source behind them: 19 SEST files from
  before 9 Oct with stale values (Fujian's frontal area 207 against the
  upstream mod's 2022), 22 with another mod's section pasted in, 11 area-value
  changes, and builder output from mods the repo has not captured.
- **The Modern US Navy v626 and Italian FREMM hand merges.** A Workshop
  refresh capture and a rebuild reproduce them, except the OHP long hull,
  where GPT's merge reverted three of the author's changes.
- **The 203-entry mod list** with Contact Log, Topographic Map and Pop-Out
  Windows. They are not in the collection, and SETUP refuses to run while a
  listed mod is missing, so shipping that list would stop SETUP for other
  subscribers.
- **GPT's REDFOR script** (hash-pinned, a false warning for everyone else)
  and **its Topographic Map remap** to F7, the game's own previous-aircraft
  key.

## Decisions taken by default (the owner's to change)

- Debrief: Runtime 1.5.0's 3 rows; PR #48 is superseded.
- In-mission F11: 1.5.0's native window.
- Contact Log, Topographic Map and Pop-Out Windows stay off the collection.
- Mods made for a newer game patch are named and left alone; only THE REDFOR
  MOD, reviewed, is marked, and only while its folder holds no code.
- Topographic Map keeps its own keys.
- Sulu: the placed H-76 no longer names an airfield as home in the seven
  generated missions (the frigate is the nearer deck).
- The OHP long hull follows the author's v626 once the refresh is in.
- Commits carry no AI attribution lines (`docs/world-sandbox/README.md`).

## Open

1. **Runtime 1.5.0's source.** Not in any branch, PR or tag. With the original
   project, the same compiler and the same reference files, the exact file
   can be rebuilt; without them, any rebuild has a new hash and needs UI
   Follow-up rebuilt too. After the next game update 1.5.0 turns itself off
   and cannot be re-gated until then.
2. **Quick Load.** UI Follow-up moves the game's plain-F9 Quick Load to
   Ctrl+F9 for every Contact Log 1.0.1 player, though only the owner's PC
   binds F9 to Contacts. Options > Accept saves it. Documented in
   `plugins/README.txt`; the owner decides before the upload.
3. **The Workshop refresh capture** (`chore/workshop-refresh-20261027`), run
   on the PC, then integrated and rebuilt. Expected with it: the USN v626 and
   FREMM files, the S-55 (with a $30M rough price and a World Sandbox entry),
   and the French Floréal and Aliaca, two more World Sandbox buy-list
   entries (PR #47's tests no longer hard-code the count).
4. **The 27 Oct crash** with both plugins on: no stack yet. The test plan is in
   the owner's review document.
5. **The owner's PC** still has GPT's Topographic Map remap (toggle F7) if
   GPT's script ran there; SETUP no longer touches that file.
6. **In game, still to see:** Sulu Line test card 8.2 to 8.5 (empty fields,
   deck fits, the H-76 without a home field, the AW109E livery), Southern
   Watch 05's P-8 firing its Harpoons, the World Sandbox Poseidons
   (`docs/playtests/world-p8-20261026.md`), SETUP's messages on the PC.
7. **GitHub:** PRs #47 and #49 are carried here in reworked form, #48 is
   superseded by 1.5.0, and #50 and #51 stay as a record of the PC; the owner
   closes them.
