# Workshop refresh, 14 Oct 2026 - review

The review of the capture on `chore/workshop-refresh-20261014`: `73515fc6`
(16:58 PC time, UTC+10), taken after the player's playtest of the 13 Oct build
and before the game was started again, so `player.log` is the playtest's own.
The facts are in `data/install-snapshot/workshop-refresh-summary.txt`; this
page judges them. The previous capture is `24734251` (13 Oct 20:43), the
previous export `0b0d137b` (13 Oct 15:34).

How it was checked: four readers, one per mod group, each working from
`git diff f6172148 73515fc6 -- mods-source/<id>` and the SEST files that fork,
extend, name, place or fix anything from that mod; the export checks run at
`73515fc6` before any rebuild; then the rebuild on this branch. **verified**
means seen in a file or a command's output; **inferred** means reasoned from
those. Nothing SEST ships was changed on the capture branch.

## 1. What the game is running

- **verified** Sea Power 0.8.5 Build 261008, Steam build 25806545, Unity
  6000.0.67f1 (unchanged since 13 Oct).
- **verified** The game loads SEST from the Workshop copy, item 3812461539,
  at position 1 of the live list; there is no local
  `StreamingAssets\SEST_Integration` ("local SEST folders: 0"). The player
  uploaded the 13 Oct build before 7 am on 14 Oct and plays it as a
  subscriber. The sync and SETUP scripts do not yet notice the Workshop copy;
  that tooling change is in this pass's work list.
- **verified** 197 Steam-tracked subscriptions, 197 folders on disk: the 195
  of 13 Oct plus SEST's own item and one new mod, Anduril Maritime Drones
  (3819522350). Nothing pending, nothing removed.

## 2. Export checks at `73515fc6`, before the rebuild

| check | result | why |
|---|---|---|
| check_vanilla_drift --since 7739076c | pass | the game's own files did not change |
| check_inventory | FAILED | 3819522350 in neither catalog nor order (placed in this pass); the four CR-stripped mods (3775128499, 3776340577, 3780118683, 3781062859), the PC-side `git add --renormalize` still owed |
| check_pack_fidelity | FAILED, 5 files | SEST Replenishment's forks of jmsdf_dd_asahi, jmsdf_ddg_atago, jmsdf_ddg_maya (Euromod JMSDF v36) and usn_lhd_wasp, usn_lhd_wasp_early (Modern US Navy v614) were stale; all five re-fork on rebuild |
| check_dependencies | pass | it still listed the Richard Morris's UMS-4249 sonar as defined nowhere; repaired in this pass |
| check_game_version | pass | every pack 0.8.5 |
| check_alias_bases | pass | one pre-existing round with no base (3755769170's aces_aim-9m_stdm) |

## 3. Updated mods

**Euromod - Modern US Navy (3390330875)**, v611 -> v614, 16 files. New
`usn_mh-60r_p2`, an MH-60R (Phase II) ASW helicopter with its own model folder,
19 HSM squadrons dated 2026 and its own names, rostered two per ship on every
Wasp variant with an 80-round AirTorpedo deck stock; the Wasp's deck park
grows from 368 to 822 sections; the early Wasp moves from the late AH-1W to
`usmc_ah-1w`; the vanilla `usn_ssq-62` DICASS is overridden and named; the OHP
longhull LAMPS-3 alias gains hull-dimension keys. The Phase II's Hellfire,
Penguin and tank rounds are shipped only by US Naval Aviation, a dependency
the mod does not declare (recorded in the catalog). SEST: the two Wasp forks
re-fork; SEST Cross-Deck adds the Phase II to its Seahawk family, so allied
decks that fly a Seahawk take it too.

**US Naval Aviation (3737267013)**, v91 -> v92, 6 files. The SH-60B and SH-60F
drop the vanilla SSQ-53/62/77 sonobuoys for the lettered rounds; the MH-60R's
ASWPatrol takes `usn_ssq-77c`, which does not reach the game while U.S. Navy
2027 wins `usn_mh-60r` above it; AGM-158B-2 and AGM-158C-3 MaxLaunchRange
800 -> 538 and 521 NM. Nothing in SEST forks these; Collection Fixes' donors
from this mod were unchanged.

**Euromod JMSDF Modern navy (3695809489)**, v35 -> v36, 6 files. The Asahi,
Atago and Maya move both Phalanx mounts from MK15C to Euromod Main's
`eu_MK15C` (Automatic=True) and their CIWS magazines to `usn_cal_20mm_apds`;
the SH-60J/K sonobuoys move to Euromod Main's lettered rounds, so the Euromod
Main dependency is now verified rather than inferred. Upstream defect: the
SH-60K's ASW Long Range (Late) loadout names `usn_ssq-53e`, which nothing
defines (no SEST mission selects it). SEST: the three forks re-fork and follow
Euromod's own Phalanx tune (SEST's MK15C retune was retired on 9 Oct); the
Cross-Deck stubs were unchanged.

**THE REDFOR MOD (3732654992)**, 16 files. New Tu-95K-22 (`wp_tu95k`, the
game's Tu-142M mesh with the Tu-95MS mod's material, three Kh-22, an SPS-151
jammer it defines itself) and a Grisha IV (`wp_mpk_grisha4`,
HideIn=MissionEditor, the Grisha III hull with SA-N-4 and kitbash parts whose
material no export ships); the late Slavas, late Kara and Grisha MU move to the
game's own SA-N-4C; R-500 TerminalDiveDistance 0.5 -> 0.1 NM; the S-400
5P85TE2's search radius 0.5 -> 1 NM. No SEST pack forks a REDFOR file; every
SEST S-400 placement uses the SA-21 mod's ids; Collection Fixes' sensors.ini
shares no section with the mod's. The world campaign's Russian buy list takes
the Tu-95K-22 on rebuild; the Grisha IV is left out by a new rule (a unit its
author hides from the editor is not for sale).

**RC-135V/W Rivet Joint (3808882954)**, 44 files. The author renamed both
aircraft: `boeing-rc135` -> `boeing_rc135` (ServiceDate 2005, eleven liveries
as Squadron1-11, the RAF ones Nation=UK) and `boeing-rc135_early` ->
`boeing_rc135_early` (1968, seven liveries); gear and flight-control
animations (the two gear files absent from the export); a Callsigns line; its
own loadout name "SIGINT / ELINT Reconnaissance". Without a change the
campaign build stops: Red Line 03 and Tasman Shield 11 placed the old id. Both
now place `boeing_rc135` (Squadron2 is the 62-4125 tail), the world-campaign
register follows, and SEST Collection Fixes no longer supplies the SIGINT
name, a retired fix the author adopted.

**Red Storm Arsenal (3413868677)**: no change since the author's 13 Oct "small
missile fix"; the summary lists `usn_ffg_constellation` only because it
compares with the 13 Oct first export (a tooling nit, section 8). SEST's
Constellation fork is current. The Richard Morris fork gains SEST's own
repairs (section 5).

**Saronic Corsair ASV, Identify Expanded, YF-23 Black Widow II, Anduril FQ-44
Fury, MV-75 Cheyenne II, EC-2 Stand Off Jammer**: five of the six changed only
`_info.ini` (ApproximateVersion -> 0.8.5); Identify Expanded rewrote its
advisory strings, dropped `[Vars] CampaignMode=true`, and ships a changed DLL
and new runtime DLLs. Checked for the AIM-424 work: `yf23_aim424_internal`
and `fury_aim424` are byte-identical to the 13 Oct export (both Mass=680.4).
Nothing in SEST follows any of these by hand; the catalog carries a dated
sentence for each.

## 4. The new mod: Anduril Maritime Drones (3819522350)

119 files, RSG (maintainer AlpineStatic), the Corsair's licence (no forking).
Ten uncrewed variants, all US: Dive-LD (survey, mine countermeasures, two
Copperhead-100M), Dive-XL (four Copperhead-500M or 24 Copperhead-100M),
Copperhead-100 and -500 survey vehicles, and the K5 KRAKEN surface boat
(reconnaissance, strike, one-way attack). The UUVs are UnitType=Submarine, the
K5 a Vessel. Three rounds, ten weapon and sensor sections under
`systems/weapons/` and `systems/sensors/` (subfolders; whether the game reads
them is not yet seen, and SEST's checkers glob `systems/*.ini` only), four
scenarios. `check_mod_conflicts`: no whole-file collision, no merged section
shared, 24 files nothing else ships. `language_en/anduril_maritime_ui.ini` sets
`YearsFromStart=85`, which is how its README's "Mission Editor includes years
through 2031" is done: a collection-wide side effect on the editor's year
list. With it enabled the Corsair's Mk 46 cradle and US Mk 32 tubes can load
the Copperhead-100M.

Placed directly below Saronic Corsair ASV (position 60), catalogued, and
excused from campaign coverage as the Corsair is (no 2028 SEST mission has an
uncrewed-vehicle role). Armed variants carry no reloads and the UUVs cannot
recharge, so nothing here is for SEST Replenishment. The world campaign's
arsenal takes the variants the register's nations operate on rebuild.

## 5. What the pack follows, in this pass

- Re-forked on rebuild: the three JMSDF hulls and the two Wasps (Replenishment);
  every Cross-Deck stub re-read (the Maya's list unchanged); the Phase II
  Seahawk added to the Seahawk family.
- RC-135: ids renamed in Red Line 03, Tasman Shield 11 and the world-campaign
  register; the SIGINT loadout name retired from Collection Fixes.
- Three upstream defects repaired at the player's call (the 13 Oct review's
  open items): the Richard Morris's VDS named after its definition (CAPTAS-4)
  and its NSM launcher animations listed (`HULL_REPAIRS`, SEST Replenishment);
  the Buk-M3 on a launcher section of its own with the author's 120 s reload
  (`LAND_UNIT_REPAIRS` and `ADDED_LAUNCHERS`, SEST Collection Fixes); the
  Topol-M and DF-41 trucks pointed at `[ICBM_Launchers]`.
- The world campaign no longer sells a unit its author hides from the editor
  (REDFOR's Grisha IV).
- The player's decisions of 14 Oct, in this pass as well: every AIM-424 in
  the collection on SEST's flight model and model block (SEST Collection
  Fixes' `ammunition_overwrite/` stubs, `build_aim424`, one per id:
  `usn_aim-424`, `yf23_aim424_internal`, `fury_aim424`; needs the Anchor
  Chain preloader; `docs/conflicts-and-load-order.md`, "Four AIM-424s");
  the Rivet Joint's briefing photo back under its new ids
  (`integration/gallery/profiles.tsv`); a box for every playable unit; the
  three briefs; the deployment boxes kept 5 NM clear of every arrival circle
  (section 9 of `docs/campaigns/southern-watch/build-notes.md`'s zones
  entry, "No box into an objective"); the local scenarios cleaned (section
  9 below); the tooling list (section 8); and three author reports drafted
  under `docs/author-reports/`, not posted.
- Catalog: dated sentences for every updated mod, the new entry, the verified
  JMSDF and inferred Modern US Navy dependencies, Red Storm Arsenal's author
  name; `data/mod-fingerprints.json` regenerated.

## 6. Decisions for the player

Taken on 14 Oct and done in this pass: (1) SEST's AIM-424 flight model and
model on every AIM-424; (2) the stock-pictures logging pass (menu plugin
1.1.0); (3) the PC runs the Workshop copy, so the tooling follows it; (4)
the Buk-M3 reload, (5) the Richard Morris sonar and hatches, (6) the
Topol-M/DF-41 launcher name; (7) a box for every playable unit, and then no
box into an objective - the 22 escorts waiting within 5 NM of their convoy's
circle excepted, since the game lets any ship into any box that admits
ships; (8) the local scenarios cleaned. Still open:

1. The uncrewed vehicles in the world campaign's US arsenal: kept (the rule
   excludes only units their author hides); say if they should go.
2. The SH-60K's `usn_ssq-53e` sonobuoy, defined nowhere: report to Euromod
   JMSDF's author, or leave (no SEST mission selects that loadout).
3. Modern US Navy's undeclared dependency on US Naval Aviation for the Phase
   II's rounds: worth a line to its author.
4. The three author reports under `docs/author-reports/`: post them, or not.
5. `integration/missions/newest 0.7 updated mods v2.ini`: delete, or name the
   mod it needs (section 9).

## 7. PC steps, in this order (game closed)

1. After the push and the fast-forward: `git checkout sest-dev/loving-bell-3cnvvw`
   and `tools\sync-sest.ps1`. It now carries the Workshop-copy guard: while
   3812461539 is on disk it stops before pulling and says the two ways out
   (unsubscribe and re-run, or `-SkipInstall` to pull and set the order
   without installing, the Workshop copy kept at position 1). To upload this
   build, take the first way.
2. Upload the new build to the Workshop item with the change notes, from the
   local `StreamingAssets\SEST_Integration` the sync recreates (unsubscribe
   first, or the upload picks nothing).
3. For the stock-pictures pass: start the game, visit the main menu, a mission
   briefing, the Mod Manager, quit, and run `tools\capture-context.ps1`; the
   log lines `[SEST Pictures]` in `Player.log` are what the swap will be
   designed from. Run `tools\scan-ui-assets.ps1 -Force` once, so
   `ui-assets.txt` carries the full 796 code names.
4. The four CR-stripped mods: `git add --renormalize` their folders on the
   deploy branch, as the 13 Oct review said.

## 8. Tooling nits seen in this review

- `tools/workshop_refresh_summary.py` compares "exported files changed" with
  the previous export, not the previous capture, so a change already reviewed
  (Red Storm Arsenal's 13 Oct fix) is listed again; print both baselines.
- SEST's dependency checkers glob `systems/*.ini` only; the Anduril mod puts
  its sections in `systems/weapons/` and `systems/sensors/`. Widen the glob
  once the game is seen to read subfolders.

The 13 Oct review's tooling list (its section 14, item 6) was done in this
pass: the sync script's Workshop-copy guard (`-SkipInstall` is the second
way out; both copies on disk is refused whatever the switches);
`set-mod-order.ps1` treating 3812461539 and the local `SEST_Integration`
folder as one entry, never both; the capture's "updated" column read from
Steam's `timeupdated` in `appworkshop_1286220.acf` with the folder time
beside it, and `workshop_refresh_summary.py` reading both formats;
`-CheckUpdates` skipping SEST's own item and writing `workshop-updates.txt`
itself as UTF-8 without a byte-order mark; the whole BepInEx log, head and
tail past 50 MB; the Workshop picture cap raised to 2,000 with a per-mod
count, loadout icons no longer matched; `check_mod_conflicts.py` naming
merged sections and keys two mods both define, with who wins;
`check_load_order.py` reading the captured live order too (a live-order
problem is reported and fails the check only with `--strict-live`, so a
stale capture cannot block a build). Nine tests cover them
(`tools/tests/test_*.ps1` through `test_powershell_scripts.py`, and three
Python tests); every PowerShell run was pwsh 7 on Linux against stand-in
folders, and nothing has run on the PC or under Windows PowerShell 5.1 yet.

## 9. The local scenarios (`integration/missions`): cleanup and tweaks

The player's own editor missions and the pack's products that live beside
them (the Banda vignettes, the NF3 carves) are installed into the game's
`user_missions` by the installer and were never gated. Done in this pass,
every change recorded in `scratchpad/scenario_fix_log.json` while it existed
and summarised here:

- **Deleted**: `SULU SEA OFFENSIVE much smaller`, `smaller` and `smaller v2`,
  the three middle cuts; the full `SULU SEA OFFENSIVE ` and `smaller v3` stay.
  The installer never deletes a mission from the game, so the three stay in
  `user_missions` on the PC until removed by hand.
- **Units no mod ships any more** (the 1986-94 fleet ids of an unsubscribed
  mod, `cn_`-prefixed PLAN hulls their mod renamed, four dated USN ids):
  27 `Type=` swaps to the undated or renamed unit of the same class across
  AUS DEF, AUS INDO-PAC ESCAv2, DARWIN US SUPPLY, NEWEST NORTHERN AUS CH
  DEFENCE, SULU SEA OFFENSIVE (both), 0 Prologue, chapters 2-5; carrier and
  destroyer air groups `usn_mh-60r_26` -> `usn_mh-60r_p2`, `usn_mh-60r_2027`
  -> `usn_mh-60r`, `usn_sh-3j_89` -> `usn_sh-3j`. Each swap is a one-line
  change and is listed in the fix log; a swapped hull keeps its name, so
  these are stand-ins of the same class, not the retired id.
- **Loadouts the winning file does not offer**: the 039B's `Silent` ->
  `Late`, the Block III Super Hornets' `AntishipLongRange` -> `MH_LRASM`
  (SEST's own), the Burkes' `MST`/`AA`/`MSTBF` -> the `≥125_`/`≥119_` names
  U.S. Navy 2027 uses, the P-3C's `ASuW` -> `AntiShip`, two `Empty` fits ->
  `Strike`/`Default`; variants outside the winning file clamped (OHP
  Variant44 -> 25, the (2000s) Nimitz 3 -> 2, the fishing boat 6 -> 5).
- **The fair opening** (the campaign's `check_opening`, run over every file):
  the Tu-95 flight in the three NORTHERN FRONT files held back to minute 5
  (Disabled, one join trigger each; the files had no triggers before); the
  player's Virginia nudged 5 NM off the Gorshkov's 25 NM ring; the Seawolf
  in SULU SEA OFFENSIVE and the 039B in `smaller v3` likewise; and the
  player's ISR and support aircraft that started inside an enemy SAM
  umbrella (Tritons, the E-3G, the AC-130J, F-22 and tanker formations, the
  MQ-9s) moved to the nearest point outside every umbrella, 10 to 260 NM.
  `NORTHERN FRONT III FINAL NEWEST` moved five Tritons; the mod's HHQ-9B
  (260 NM) and 40N6 (250 NM) reach as written is what decides it.
- **The Banda vignettes**: the builder (`build_banda_vignettes.py`) now takes
  a red unit's `WeaponStatus` and `_enter=<minute>` (written Disabled with a
  "Joins at minute N" trigger, the campaign's own pattern). Fury Wingmen's
  and Black Widow Debut's fighter pairs and Triton's Picture's J-16s join at
  minute 5; Triton's Picture's drone starts 274 NM south of the 052D, outside
  her 260 NM reach, instead of 81 NM; Mogami's Corner's 093B is Tight (a
  boat gone quiet does not shoot first; she fires when found). The Biak
  Regiment's Growlers start 49 NM from the S-400 by design (the brief says
  the HARM shot comes from inside its envelope): the one opening the survey
  still lists, on purpose.
- **The NF3 carves** (`make_scenarios.py`): a carve now carries the parent's
  join triggers for the held-back units it takes, renumbered, and writes a
  carried unit enabled when its trigger did not come along. All 11
  regenerated; `check_scenarios.py` passes.
- **Left for the player**: `newest 0.7 updated mods v2.ini`, a 0.7-era test
  with 22 units and air groups no mod ships (`preflight --all` lists them);
  delete it or say which mod it needs. The five Banda Front variants
  (`EDITED`, `Lean`, `Lean v2`, `Living Seas`, `Front`) are kept as they are.

After the pass: `preflight --all` lists nothing but that file; `check_scenarios`
passes; the opening survey over all 50 files lists only the Biak Regiment.
