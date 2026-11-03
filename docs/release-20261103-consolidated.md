# The consolidated release branch, 3 Nov 2026

`release/consolidated-20261103` is the next Workshop upload of the SEST
Integration Pack (item 3812461539). It brings two lines of work on the same
28 Oct 2026 capture into one branch. This note replaces GPT's
`docs/release-20261101-dual-build.md` (PR #55), which is not carried. Nothing
on this branch has been uploaded, installed on the PC or seen in game.

## What this branch is

**The capture review.** `24b4b8f5` reviews the 28 Oct 2026 Workshop refresh
(`docs/workshop-refresh-20261028-review.md`). The owner's decisions of 30 Oct
2026 are recorded there as taken.

**The lead's reviewed fixes.** Eleven commits on top of the review, each built
and checked on its own branch and then by a second reader:

- Collection Fixes declines the SM-3 IIA and IIB ExtendedGuidance keys
- Collection Fixes supplies the Charles de Gaulle's EOMS-NG sensor
- Allied Fixes hangs the RAN Seahawk's Redback pod on Euromod's new Penguin
  station
- Cross-Deck spells a stub's file name in ASCII
- Catalogue and order the four new subscriptions of the 28 Oct export
- Catalog notes for the mods the 28 Oct export updated
- Price the B-21 Raider and its five rounds
- Fingerprint the 28 Oct export
- World Sandbox values the KC-30A as a tanker whichever copy of its file wins
- Cost models price the Aliaca as a small UAV, not a fighter
- Vanilla export stays at Build 261021: the pack targets the stable game

**GPT's pieces, ported.** GPT's line (PR #54, branch
`fix/beta-261026-safe-anchorchain`, and PR #55, branch
`release/sest-workshop-20261101`, pushed 31 Oct to 1 Nov 2026) added work the
lead's line lacks. Those pieces are ported by cherry-pick with `-x` where
the commit applied as it was, so the ported commit names GPT's source commit
(the capture pieces), or reworked by hand where it mixed wanted and unwanted
changes (the beta pieces, which carry no cherry-pick line). Either way the
subjects are in plain English. Items 3, 7 and 8 below were not carried by any
unit when this note was written; they are listed so the lead can port them or
leave them out. Before combining, check each piece against the final branch
log. GPT's own subjects, by piece:

1. **The bounded Anchor Chain fork and the inert beta bootstrap**
   (`integration/beta-anchorchain/`), from PR #54: `25606fd8` "fix(beta):
   bound Anchor Chain plugin load and prevent failed plugin retries",
   `727d41a0` "legal(beta): retain Anchor Chain MIT licence for source fork",
   `ce03ec16` "feat(beta): inert-first safe bootstrap to load bounded Anchor
   Chain once", `bd4d8ba3` "fix(beta): require exact explicit enable flag
   content before plugin initialization", `69d9d201` "test(beta): add
   staged-inert two-phase loader test with guarded rollback", `480cc805`
   "build(beta): compile inert-first bootstrap and record both DLL hashes",
   `234cda19` "fix(beta): build both Anchor Chain fork and bootstrap via .NET
   SDK", `cb94e3f5` "test(beta): assert bounded loader and inert staging
   source contracts", `3a2cec7c` "fix(beta): use unambiguous separate
   file/hash conditions in stage and rollback tester", and their build and
   test follow-ups. On PR #55 the same tree came in as `c8180901`
   "feat(release): carry beta Anchor Chain source and tests alongside stable
   pack; deployment gated".
2. **The game profile in SETUP** (`integration/campaign/setup/sest-profile.ps1`,
   `SEST-PROFILES.txt`): `79f9ce09` "feat(release): detect beta and stable
   profiles by exact game SHA without swapping plugins", `55f8d646`
   "feat(release): gate SETUP on exact beta/stable game profile before
   changing settings" and `77692e8e` "fix(release): permit safe data-only
   SETUP fallback after new Steam beta updates". Reworked here: SETUP names
   the detected game build by the hash of `Seapower-Scripts.dll` (stable
   `eab2297b`, beta `3005bc6d`) and warns when the game's last launch loaded
   no code mod. It warns, without stopping, when the discontinued PR #53
   `SEST.BetaAnchorBootstrap.dll` is installed, and reports an unknown build
   as data only. It stops only where SETUP already stopped.
3. **The beta's vanilla export** (`data/game-baselines/beta-261026/`, 5,387
   files): `f8637c91` "build(release): retain beta 261026 vanilla snapshot
   while restoring stable 261021 source inputs". Not ported yet. It would be
   reference data for the beta work. The pack still builds from `mods-source/_vanilla`, Build 261021.
4. **The one-command capture** (`tools/capture-all-mod-updates.ps1`):
   `04443995` "feat(release): capture every installed Workshop mod and export
   today's changes in one step", `dc8fd88f` "feat(release): include guarded
   beta compile diagnostics in the one-command all-mod capture", `cdf7c620`
   "fix(release): use fetchable remote Oct 28 baseline for Workshop delta",
   `b7220990` "fix(capture): preserve a review ZIP and independent Workshop
   export if a diagnostic stage fails" and `870fca77` "fix(capture): handle
   newly subscribed Steam IDs and singleton exporter results on Windows
   PowerShell".
5. **`capture-context.ps1` and `export-mod-configs.ps1` under Windows
   PowerShell StrictMode, with tests**: `81c99cf8` "fix(capture): normalise
   empty and single-item pipeline results under StrictMode", `16bf0471`
   "fix(capture): avoid null replacement tokens when snapshot is redacted",
   `7ba78efe` "fix(capture): keep DLL enumerator as array even for empty game
   plugin folders", `89521ff5`, `8550cab3`, `9f290618`, `f9471530` and
   `2a481b63` (the tests).
6. **The GitHub Actions workflow** (`.github/workflows/sest-release-gates.yml`):
   `6aa291bc`, `707dd147`, `a7c94c35`, `9e7d736a`, `bf4949d2`, `a2448cdf`
   and `9a36e6d5` ("ci(release)" and "ci(capture)"). A green run is a build
   check, not a game test.
7. **The Hyundai-Hanwha rename**: `19319c44` "catalog(release): reconcile
   Hyundai-Hanwha Steam Workshop rename with legacy Philippine item ID". Not
   ported yet: it retitles `euromod-philippines` (3812454152) in
   `data/mod-catalog.json` and notes the rename, keeping the old slug until
   the updated content is exported.
8. **The Chilean JvH cost id**: `bb249223` "fix(release): remove obsolete
   Chilean JvH cost ID; retain renamed vessel mapping". Not ported yet: it
   drops the `ch_ffg_jvh` mapping from `integration/combat-costs/mappings.json`
   and keeps `ch_ffg_jacob_van_heemskerck`.

The final hashes and subjects of the ported commits are in the branch log;
the lead's merge record lists them.

**Not ported, because the lead's reviewed versions stand:** GPT's SM-3 and
EOMS-NG fix (`8e415b25`), the Seahawk retarget and its test (`18a80e89`,
`9fe6e88a`), the four new mods in the catalog, the order and the campaign
excuses (`fa88f4a8`, `f34f3749`, `dd36afd9`), the KC-30A (`788c3985`) and the
B-21 and Aliaca cost proxies (`e8fe7253`). Also not carried: GPT's release
notes (`04f836bf`, `b556c002`). Their "beta-first" framing contradicts the
owner's decision of 30 Oct 2026 that the pack targets Build 261021. Three of
their points stand and are kept here: a green CI run is not gameplay
validation, the discontinued PR #53 bootstrap DLL must not be on a PC that
runs SETUP (SETUP now warns about it), and the previous stable build stays reproducible from its commit
for a rollback.

## What this branch is not

- No beta DLL is shipped or installed. The bounded fork and the bootstrap are
  source-only test candidates; the pack's builders do not copy them, and
  nothing installs them on the PC.
- Runtime 1.5.0 (`7ba6d6d9`) is unchanged and stays the shipped binary, with
  UI Follow-up 1.4.2 beside it. Their hash checks are unchanged: both stay
  off on any build but 261021.
- It is not a beta release. On the public beta (Build 261026) no code mod
  loads, SEST's or anyone else's; the pack's data does.
- Nothing is published by code. The Steam steps below are the owner's.

## The release gates, in order

1. **The owner's Steam alignment.** Now: add Contact Log (3819427362), Sea
   Power Topographic Map (3826122523) and Sea Power Pop-Out Windows
   (3826396311) to the collection 3812390790 and to the item's Required
   Items. The 26 Oct upload's `LOAD-ORDER.txt` already names them, so every
   subscriber without them has had a SETUP that stops
   (`docs/campaigns/southern-watch/publishing.md`, *Correcting the 26 Oct
   upload*). Before Submit: add B-21 Raider (3821992229) to both, so that
   both match this build's 204-entry `LOAD-ORDER.txt` (203 Workshop mods and
   the pack).
2. **The from-scratch build and the 18 gates.** `python3 tools/build_all.py
   --from-scratch` on the final head, one Rebuild commit, then the 18-step
   gate script and both test suites. The tree must be clean afterwards.
3. **The stable smoke test.** On Build 261021 (Steam's public branch), with
   Runtime 1.5.0 and UI Follow-up 1.4.2: SETUP runs to the end and names
   Build 261021; Player.log shows Runtime's three `correction installed`
   lines and `[SEST UI Follow-up] 1.4.2 input fix installed`. With Pop-Out
   Windows 1.0.2, `inactive` lines from Runtime's pop-out bridge and from UI
   Follow-up's Contacts pop-out surface fix, Formation UI mode switch and
   camera compass are expected (both plugins are pinned to 1.0.1). Then one
   mission in a campaign, F11 in the mission and in the Task Force menu, and
   the debrief.
4. **The upload.** To the existing item 3812461539 only (Create Mod, Update
   Existing), by the procedure in `publishing.md`, with the 28 Oct change
   log and Description from `workshop-listing.md`.

## Open

- **The beta repairs R2, R3 and R4.** R3 is on `beta/r3-20261102`, off this
  branch and not shipped: its source is `8ef1dfc6` (a later bounded Anchor
  Chain fork with assembly adapters, the bootstrap, and Runtime 1.5.1 beta and
  UI Follow-up 1.4.3 beta sources), and `7e61be6d` holds the candidates as the
  owner's PC ran them on 2 Nov 2026. R2 and R4 are not in the repository. The
  beta branch for the game's 11 Nov 2026 release takes them up with the rest
  of the beta work. (The lead to confirm this R3 wording.)
- **The 1 Nov 2026 PC capture.** It has not reached the repository. This
  branch is built on the 28 Oct capture; the next capture may bring more
  author updates.
- **Runtime 1.5.0's source.** Being reconstructed on
  `feature/runtime-150-source`: 7 commits so far. The core and F11 areas
  match the shipped binary; the rest is open. Until it is complete, Runtime
  cannot be re-pinned to Pop-Out Windows 1.0.2 or to a new game build.
- **The pop-out parts.** Runtime's pop-out bridges and UI Follow-up's pop-out
  parts stay off with Pop-Out Windows 1.0.2 until both are re-pinned.
- **Quick Load.** UI Follow-up moves plain F9 to Ctrl+F9 for every Contact
  Log 1.0.1 player. The load order names Contact Log since the 28 Oct capture,
  and the collection will carry it once the owner adds it. The owner
  decides before the upload whether to ship the plugin as it is
  (`docs/integration-20261028-review.md`, open item 2).
- **The beta itself.** The PR #54 fork and bootstrap carried on this branch
  have not been run on the beta. R3's later versions of them ran on the
  owner's PC on 2 Nov 2026; their results belong to the beta branch. Their test plan
  is in `integration/beta-anchorchain/README.md`.
