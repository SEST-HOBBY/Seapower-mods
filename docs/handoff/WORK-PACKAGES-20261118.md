# Work packages, 18 November 2026

SEST-DEV. Branch `feature/r15-sea-power-093` at `89b9b4649`. Base: R14 at `62b8c2c71`.

This file lists every work package that follows from the six repository scopes of 17 November
(refuelling, rename and posting, world expansion, Coordinated Strike, ribbons, gallery), the
multi-base scope, the four R15 reviews, the owner's next-release checklist of 17 November and the
design package of 18 November (`gmo1118`: README-FIRST, integration, GPT and Gemini handoffs, master
dossier, registry draft). Full briefs for the two outside assistants are in
`HANDOFF-GPT-SUPPLEMENT-20261118.md` and `HANDOFF-GEMINI-SUPPLEMENT-20261118.md`. Section 6 lists
what in the `gmo1118` package the repository work contradicts or could not confirm.

Nothing in this file is a statement that a feature exists. A package is done when its acceptance
checks pass, and for anything the player sees, when the owner has seen it on the PC.

## 1. State today

- **Live on Steam:** R14, Workshop item 3812461539, built for Sea Power 0.9.2. On 0.9.3 its code
  stays off by design (`uploads/refs1117b/reports/BepInEx.log:19`, "Beta safe loader INACTIVE").
  The data still loads.
- **R15:** a PC test build for the 0.9.3 Build 261116 **public beta** file only
  (`Seapower-Scripts.dll` aae79728). Compiled, 17 managed and installer checks pass, the upgrade
  from R14 passes in a fixture. It has not run in the game. Its first PC run is the next step.
- **Public-release file:** the normal 0.9.3 is a different file from the public beta. No capture
  of it exists. R15 stays off on it. The owner wants the next posting to work on both; that needs
  a reference capture taken with Steam's Betas setting on None and a code change so the loader
  accepts a short list of checked game files. Until both exist this is open.
- **Dynamic Campaign Mod on 0.9.3:** not established. The first 0.9.3 log shows two plugins and
  no mention of it. Every world-campaign PC check depends on it.
- **Owner decisions of 18 November** (they override the scopes and the `gmo1118` package where
  they differ):
  1. The mod is reposted as a **new Workshop item named "Modern Naval Operations"**, all in one
     item, built cleanly. Item 3812461539 is marked deprecated and later removed. Saves and old
     ids need not carry over.
  2. The new item supports both the 0.9.3 public-release file and the public-beta file.
  3. Left behind: the two 0.8.7 plugins, the twenty-build repair chain, SETUP branches for old
     game builds, the legacy world entry.
  4. The small weapon packs stay until a loadout-function enhancement replaces them.
  5. The required-mods list is revised: lean, expansive options kept, mods nothing uses listed
     for the owner's review.

## 2. Order of work

Proposed order. It follows the delivery order in the owner's checklist and puts anything that
needs the PC behind the R15 first run.

1. R15 first PC run (BA-01, PC-01).
2. Public-release capture and the two-file loader (PC-02, BA-02).
3. Checklist defects, P1 first: GMO-04 Start Preparation, GMO-03 per-save ribbons, SCN-01 start
   positions, TF-01 replay; then GMO-06, UI-01, GMO-02, GEN-01, GEN-02, GMO-01, GMO-05 (BA-03).
4. R15 data review findings (BA-04).
5. Clean new item: naming, ids, tooling, leave-behinds, required-mods list (BA-05, BA-06).
6. Refuelling audit and fixes (BA-07, PC-03).
7. Gallery made correct for the 17 November mods (BA-12).
8. Ribbons information (BA-11).
9. Coordinated Strike stages 0 to 3, then 4 and 5 if the owner wants them (BA-10).
10. World campaign multi-base data step (BA-08).
11. World expansion Phase A inside current bounds (BA-09).
12. Polar probe, and Phase B only if it passes (PC-05, BA-09b).
13. Regional Watch from the `gmo1118` package (BA-13). Not scoped in the repository yet.
14. Posting of the new item (BA-14). The owner uploads; no assistant does.

Outside-assistant packages run in parallel from now. None blocks step 1.

## 3. Packages for Gemini (research: long documents and large tables)

| Id | Package | Inputs | Outputs | Depends on | Scope |
|---|---|---|---|---|---|
| GM-01 | Site and force research, India | `inputs/region-template.json`, `inputs/gmo-bases-89b9b4649.csv`, `inputs/units-by-nation-regions.csv`, GPT report `region-expansion-research.pdf` | `GM-01-india.json`, `GM-01-NOTES.md` | none | world-expansion |
| GM-02 | Site and force research, Africa | as GM-01 | `GM-02-africa.json`, notes | owner decision on South Africa's side | world-expansion |
| GM-03 | Site and force research, South America | as GM-01 | `GM-03-south-america.json`, notes | owner decision on Argentina's side | world-expansion |
| GM-04 | Sub-Antarctic sites and Antarctic station table | as GM-01 | `GM-04-antarctica.json`, `GM-04-stations.csv`, notes | none; Phase B data waits on PC-05 | world-expansion |
| GM-05 | Real order of battle mapped to unit ids | `inputs/units-by-nation-regions.csv` | `GM-05-oob-map.csv`, notes | none | world-expansion |
| GM-06 | Workshop search for missing units | list of missing classes in the brief | `GM-06-workshop-candidates.csv` | none | world-expansion |
| GM-07 | Cost research backlog | `docs/combat-costs/not-yet-confirmed.md`, `docs/combat-costs/cost-list.csv` | `GM-07-costs.csv`, notes | none | gallery (C3), combat costs |
| GM-08 | Photo sourcing for units with no picture | `inputs/gallery-nopic-batch1.csv`, later batches from BA-12 | `GM-08-photos-batchN.csv` | later batches: BA-12 step A1/A2 | gallery |
| GM-09 | Credit tracing and licence audit | `integration/gallery/added-photo-credits.csv`, asset table export from BA-12 | `GM-09-credits.csv`, `GM-09-licence-audit.csv` | audit part: BA-12 export | gallery |
| GM-10 | Air refuelling fits and replenishment ship capacities | type and hull lists in the brief | `GM-10-aar.csv`, `GM-10-ras-ships.csv`, `GM-10-procedures.md` | none | refuelling |
| GM-11 | Real national awards | `integration/campaign/setup/RIBBONS.txt`, REAL table extract from `service_awards.py:561-905` | `GM-11-awards.csv`, `GM-11-awards.md` | none | ribbons, gallery |
| GM-12 | Steam Workshop mechanics and name check | brief only | `GM-12-workshop-mechanics.md`, `GM-12-name-check.csv` | none | rename-and-post |
| GM-13 | Air-launched weapon table and strike timing | weapon id list from BA-10 | `GM-13-weapons.csv`, `GM-13-doctrine.md` | weapon list export | coordinated-strike |
| GM-14 | Required-mods page status | mod list from BA-06 | `GM-14-mod-status.csv` | BA-06 usage export | owner decision 5 |

## 4. Packages for GPT (structured drafting and review)

| Id | Package | Inputs | Outputs | Depends on | Scope |
|---|---|---|---|---|---|
| GP-01 | Briefing consistency: tankers and replenishment | briefing extract from BA-07, compatibility table from BA-07 | `GP-01-briefings.csv` | BA-07 step 1 | refuelling |
| GP-02 | Ribbon labels, hints and citation text | `inputs/world-awards-25.csv`, `service_awards.py` extracts, `RIBBONS.txt` | `GP-02-world-awards.csv`, `GP-02-campaign-ribbons.csv`, `GP-02-ribbons-txt.md` | owner answers on ribbons questions 1, 2, 6 | ribbons |
| GP-03 | PC test cards | test lists in the brief, `docs/campaigns/red-line/test-card.md` as pattern | `GP-03-<set>-test-card.md` (five files) | none | all scopes |
| GP-04 | Steam texts for the new item | four `docs/releases/20261107/STEAM-*.txt`, fact sheet in the brief | four `STEAM-*.txt`, deprecation notice, FAQ | wording freeze after PC-01; drafts can start now | rename-and-post |
| GP-05 | Coordinated Strike design review and UI copy | `native-strike-final-plan.txt`, panel strings extract from BA-10 | `GP-05-plan-review.md`, `GP-05-ui-copy.csv`, `GP-05-launch-point.md`, `GP-05-author-message.txt` | strings extract for the copy part | coordinated-strike |
| GP-06 | Ribbon presentation review | ribbons brief, `gmo1118` dossier section 8, Gemini's `Gemini-Award-Visibility-States.md` when it exists | `GP-06-ribbon-presentation.md` | none | ribbons |
| GP-07 | Document consistency review | `docs/replenishment-in-play.md`, `integration/replenishment/README.md`, fact sheet | `GP-07-replenishment-review.csv`, `GP-07-changelog-digest.csv` | none | refuelling |
| GP-08 | Player-facing guides | fact sheets from BA-07 and BA-09 after PC results | `GP-08-refuelling-guide.md`, `GP-08-region-text.md`, register prose | PC-03; GM-01..04 accepted | refuelling, world-expansion |
| GP-09 | Old-name wording review | CSV export of player-visible "SEST" lines from BA-05 | same CSV with two columns added | BA-05 export | rename-and-post |
| GP-10 | Independent check of region data | accepted `GM-0x-*.json`, their source lists, GPT's own report | `GP-10-region-check.csv` | GM-01..04 | world-expansion |
| GP-11 | Naming consistency after the rebuild | README, runbook, packaging guide, FEATURES, pack root .txt files from BA-05 | `GP-11-naming-consistency.csv` | BA-05 | rename-and-post |

## 5. Packages that stay with the build assistant, and PC sessions

These need the repository's builders, tests, the game's code listing or the owner's PC.

| Id | Package | Main files | Outputs | Depends on | Scope |
|---|---|---|---|---|---|
| BA-01 | R15 first-run support | `docs/releases/20261107/README-FIRST.txt`, PC toolkit R15 | run record, fixes if the run shows a fault | PC-01 | reviews |
| BA-02 | Loader accepts a short list of checked game files | `integration/beta-anchorchain`, `beta-feature-parity`, `sest-setup.ps1`, `sest-workshop-features.ps1` | build covering beta and public-release files; tests | PC-02 capture | owner decision 2 |
| BA-03 | Checklist defects GMO-01..06, UI-01, SCN-01, TF-01, GEN-01, GEN-02 | runtime, campaign builders | one small change per item, each with its PC check | PC-01 | owner checklist 17 Nov |
| BA-04 | R15 data review findings | `integration/replenishment/build_patch.py` (two SAM forks dropped: plan_hhq-9b, plan_48n6e1), Liaoning Variant1 in nine missions, no old-save alias for the Liaoning rename in the world campaign, three Tomahawk whole-file copies frozen at 0.9.2 values, generic cost proxies beside priced siblings, stale records (mod catalog, campaign bible, gallery index) | fixes and record updates | none | reviews r15-data, data-mods |
| BA-05 | Clean new item "Modern Naval Operations" | every place in the rename scope's inventory: `_info.ini`, `build_pack.py`, `consolidate_packs.py`, `tools/lib/common.ps1`, about 20 tools, plugin display names, `upload-manifest.json`, `prepare-workshop-upload.ps1`, `verify-live-workshop-item.ps1`, `sest-workshop-features.ps1`, `SestMenuBackground.cs`, 18 id-pinning tests; removal of the 0.8.7 plugins, repair chain, old-build SETUP branches, legacy world entry | new pack folder and item manifest with no item id until Steam issues one; `docs/naming-and-identifiers.md`; exports for GP-09 and GP-11 | owner answers (section 7, 1 to 4) | rename-and-post, owner decisions 1, 3 |
| BA-06 | Required-mods revision | `integration/campaign/SEST_Campaign/REQUIRED-MODS.txt` (163 mods), `data/load-order.tokens.txt` (200), `tools/check_dependencies.py` | per-mod usage evidence, list of mods nothing uses, export for GM-14 | none | owner decision 5 |
| BA-07 | Refuelling audit and fixes | new `tools/check_refuelling.py`; IL reading left open by the scope; builder fixes for receiver and tanker declarations; wording fix in the replenishment docs; briefing extract and compatibility table for GP-01 | checker, tests, per-pack rebuilds, release-record section | owner answer on patching other authors' tanker files | refuelling |
| BA-08 | Multi-base step in the world campaign | `build_dynamic_campaign.py` (generate `yardChoices`, `aircraftYards`), `check_dynamic_campaign.py` (mirror the rules) | campaign.json with the two keys; validator rules; list of the nine blue nations that sell aircraft and have no depot | Dynamic Campaign Mod running on 0.9.3 for the PC check | multi-base |
| BA-09 | World expansion Phase A | `home_bases.py`, `regions-2028.json`, `world-operations-2028.json`, `build_dynamic_campaign.py` (NATION_WORDS, LANES, labels), `modern_world.py` THEATRES, `WorldServiceLedger.cs` Theatre(), four count-pinning tests | converted region data, theatre gaps closed, rebuild, validator | GM-01..05 accepted, GP-10, owner answers on sides | world-expansion |
| BA-09b | Phase B below 62S | `BOUNDS`, land mask south of 60S, ops-site land test | only if PC-05 passes | PC-05 | world-expansion |
| BA-10 | Coordinated Strike stages 1 to 5 | `CoordinatedStrikeRefinements.cs`, new `StrikeAirAdvice`, native window files, `RuntimeFixesMod.cs` switches | stage by stage, each behind an ini switch | PC-04 round per stage; owner answers on orders and the author | coordinated-strike |
| BA-11 | Ribbons Part 1, 2, 3 | `WorldServiceLedger.cs`, `CostReportLine.cs`, `WorldOperations.cs`, `NativeCostTypography.cs`, `build_pack.py:572-680`, `service_awards.py`, `RIBBONS.txt` | F11 Service rows, rules-page strips, optional campaign Service panel | GP-02 text; PC tests T1 to T3 for the unknowns | ribbons-info |
| BA-12 | Gallery fixes A1 to A11, ribbons page, reference pages | `integration/gallery/refresh_index.py`, `build_patch.py`, `profiles.tsv`, `source/` | correct index, build gate, generated numbers, exports for GM-08 and GM-09 | owner answer on the 21 uncredited photos; `tools/list-profiles.ps1` re-run on the PC | gallery-encyclopedia |
| BA-13 | Regional Watch (the `gmo1118` "RON") | proposed `integration/world-sandbox/regional-watch/`, proposed runtime files | not started; needs its own repository scope first | BA-09; Dynamic Campaign Mod on 0.9.3 | gmo1118 package |
| BA-14 | Posting preparation for the new item | release folder, Steam texts from GP-04, PC toolkit | toolkit and records; the owner uploads | all acceptance passes | rename-and-post |
| PC-01 | R15 first run | toolkit steps 0, 1, 1b | logs | none | reviews |
| PC-02 | Reference capture with Betas on None | capture tool | reference ZIP of the public-release file | none | owner decision 2 |
| PC-03 | Refuelling tests T1 to T10 | test cards from GP-03 | logs, pass/fail per test | BA-07, PC-01 | refuelling |
| PC-04 | Coordinated Strike P0 to P5 | test cards from GP-03 | logs, pass/fail | PC-01; BA-10 per stage | coordinated-strike |
| PC-05 | Polar probe: latMin -78, one Port at McMurdo | probe campaign from BA-09 | does it start, nav grid line, map, routing, battle terrain | Dynamic Campaign Mod on 0.9.3 | world-expansion |
| PC-06 | Ribbons T1 to T10 | test cards from GP-03 | screenshots, pass/fail | BA-11 | ribbons-info |
| PC-07 | New-item acceptance | fresh subscribe, SETUP, both game files | logs | BA-05, BA-02 | rename-and-post |

## 6. The `gmo1118` package against the repository

Checked at `89b9b4649` unless stated. "Scope" means the repository scoping of 17 November.

### 6.1 Superseded by the owner's later decisions

| Where | Package says | Now |
|---|---|---|
| Integration handoff section 5 "Brand/Steam"; dossier section 10; Gemini handoff E; GPT handoff (implicitly) | Keep item 3812461539, the name "SEST Integration Pack - Modernised Campaigns", collection 3812390790 and the saved campaign id; no rename or new post | New clean item "Modern Naval Operations". Old item deprecated, later removed. Saves and old ids need not carry over. A decision matrix on keeping the item is no longer needed. |
| Dossier decision statement, 1.2, 11.1 | No broken campaign id or save reset; campaign id `sest.world_sandbox_2028.regional` must remain unchanged | The owner has released this constraint for the new item. Whether the id changes is an open naming question (section 7), not a rule. |
| Dossier 10 naming hierarchy | Umbrella "SEST Integration Pack" | Product name is Modern Naval Operations; SEST-DEV remains the creator identity. |
| Owner checklist 17 Nov "RELEASE WORDING" and GCO-01 | Keep the current Workshop item; pivot identity to "GCO" | Superseded by the 18 November decision. |
| Dossier 11.1 | All 196 bases, 293 forces, 54 patrols preserved | Still the baseline, but a clean build with new saves makes regional additions (which change the counts and four pinned tests) simpler, not forbidden. |

### 6.2 Contradicted or sharpened by the scope and reviews

| # | Package claim | What the repository shows |
|---|---|---|
| 1 | Dossier 5.1: the campaign is built "via `build_regions.py`", sidecar by `modern_world.py` | Four layers in order: `build_dynamic_campaign.py` build() reads `docs/world-sandbox/register/packages.json`; `home_bases.py` and `submarines.py` add nations and bases; `build_regions.py` applies `regions-2028.json`; `modern_world.py` modernise() applies `world-operations-2028.json`, sets stages, re-tiers the buy list and writes `sest_operations.json`. Regional data must enter at the right layer; a nation exists only through `home_bases.py` BLUE_ADDED/RED_ADDED. |
| 2 | Dossier 2.4, 3.2: the 62S limit is an engine matter; extension to -80 is "a separate engine-expansion programme" | The bound is one SEST constant (`build_dynamic_campaign.py:161` BOUNDS). Dynamic Campaign Mod 0.25.0.1 reads the height data pole to pole and has no latitude limit in its bounds code (IL at `wf2/multi-base/dcm2.il`). What is unknown is behaviour, not permission: map drawing, routing, battle terrain. The repository's own land mask is wrong south of about 60S (ice shelves read as water, several stations as water), so static checks there cannot be trusted. One PC probe (PC-05) settles it. |
| 3 | Dossier 2.1 cites Dynamic Campaign Mod 0.24.0 evidence | The installed build read by the scope is 0.25.0.1. Whether it loads on game 0.9.3 is not established. |
| 4 | Dossier 6.1 item 3 and test SR-01: tactical ship replenishment covers "ammo and fuel" | The pack's replenishment is ammunition only. No file in the built pack sets FuelCapacity or FuelLoadSpeed on a supplier. "Fuel first - 2,000" is an ammunition-point tier. Whether a ship can receive fuel in a tactical mission is not established (refuelling test T8). |
| 5 | Dossier 6.1, 6.2: tanker compatibility framed as "RefuelSystem and receiver compatibility" with AR-01 (Voyager to Typhoon) as the lead case | The game's contract is narrower and was read from the 0.9.3 IL: a tanker needs a `RefuelSystem` supply system **and** an `[AerialRefueling]` section with `TankerSystems=`; a receiver needs `ReceiverSystems=`. By static reading the US tankers the campaigns place cannot pass fuel: `usaf_kc-46a_boom`/`_warp`, `usaf_stratotanker`, `usaf_kc-10a_extender` have no TankerSystems. `usaf_stratotanker` is also one of the four entries in the world campaign's `tankers` table. SEST's own `raaf_f-35a` drops the Boom receiver its upstream copy has. The Voyager/Typhoon pair was not re-checked. |
| 6 | Dossier 6.1: `aus_a330_mrtt` "absent from that strategic dictionary" is a gap | True that the `tankers` table has four entries without it. It is valued as a tanker in a different table (AIR_ROLE_OVERRIDE, `tools/tests/test_world_sandbox_kc30a.py`). What Dynamic Campaign Mod does with `tankers` at run time is not established, so "gap" is not yet shown. |
| 7 | Dossier 7.1, table row "F8 strike UI": aircraft package planning "not established"; Level A treats aircraft as new | The author's tool already accepts any airborne unit that carries a missile, ASROC or torpedo as a shooter (no unit-type test; `cst.il` 2458). What it lacks is planning of the flight to a launch point, fuel, parked aircraft, bombs and rockets. The scope's stages build on that. |
| 8 | Dossier 7.2 Level A/B: status "airborne/base/deck", roles strike, escort, SEAD, EW, AEW, ASW, tanker, recovery | Parked aircraft are not units the author's tool can see; a deck list is a separate, display-only stage (G). The scope plans one linked SEAD plan (stage E). Escort, EW, AEW, ASW, tanker and recovery roles are not scoped and must not be promised. |
| 9 | Dossier 7.1: SEST adds "integration to existing F11 cost presentation" | The code adds colours and a "SEST STRIKE SUMMARY" block (legs, planned rounds, notices, planned and remaining USD) inside the author's panel. Presentation only. |
| 10 | Dossier 8.2, Gemini handoff C: no dimmed ribbon before award; generic locked tile; no name | The scope's plan shows a dimmed strip, a progress figure and the name before award, and withholds citation, conditions and date. The two differ. This is an owner decision (ribbons questions 1 and 2), and GP-06 sets out both. |
| 11 | Dossier 8.3, Gemini C: "the exact same rules" in the native campaign Service Record and rules page | The native Service Record lays out awarded rows only and pads with empty slots (IL 918077-918200). The rules page has no commander state and cannot show held or not held. Progress in authored campaigns needs a SEST runtime panel (ribbons Part 3a); data alone cannot do it. |
| 12 | Dossier 8.2: world-campaign service awards "accumulate profile-scope across saves by the existing tested policy" | The owner's checklist of 17 November (GMO-03) asks the opposite: world ribbons belong to each save. The ledger today is one file under the player's settings folder (`world-service-v1.txt`), so it is profile-wide. No session log bears on it. This is a defect on the owner's list, not a policy to keep. |
| 13 | Dossier 8.3: one `ribbons.json` used by F11, campaigns and gallery | The 25 world awards exist only in C# (`WorldServiceLedger.cs:135-152`); the campaign awards are generated from `service_awards.py`. A shared file is possible but is code and test work (gallery scope B). |
| 14 | Dossier section 9, Gemini D: gallery "517 photos, 601 profile pictures, 190 mods" | The package correctly marks these as README claims. Actual: 555 photo assets, 732 profile pictures built from 831 rows, 200 mods in the load order; 165 index entries point at files that no longer exist; 367 unit files have no entry; 21 author photos have no credit. |
| 15 | Dossier 3.1 to 3.5, integration handoff 3: neutral or "context-only" ports and host sites | The engine has two sides and no neutral base. Every base is owned and garrisoned (a NavalBase or AirBase gets air-defence units and troops; a Port one each). "Context-only" can only be map labels, patrol waypoints and traffic lanes, or a Port with `notObjectiveFor`. Whether the garrison can be switched off for one base is not known. |
| 16 | Integration handoff 3, dossier 5.1: "Keep the six existing service theatre IDs ... untouched" | The ids can stay, but the boxes have two holes: no theatre for 55E-100E south of 5S (Diego Garcia today; Mauritius, Kerguelen) or for 25W-55E south of 40S (Marion, Crozet). Battles there earn no theatre credit. The boxes need widening in `modern_world.py` and `WorldServiceLedger.cs` Theatre(). |
| 17 | Dossier 3.3 to 3.5: existing Brazil, Chile, India anchors are "a reliable starting point" for full play | The bases exist (all 22 ids the package names were found in the built campaign). But the register reader has no pattern for India, Brazil, Chile, South Africa or Argentina (`build_dynamic_campaign.py:171`), South Africa has no unit of its own in the collection, Argentina's 36 ids are all 1982-era, and no icebreaker, research ship or ski aircraft exists in 2,330 unit ids. |
| 18 | README-FIRST of the package: "The user's external regional research is still to be supplied" | The folder also holds `region-expansion-research.pdf` (24 pages, a GPT research report). It states it inspected no repository file, gives rounded coordinates, names no unit ids and is not in the builders' template. It is useful as a source list and cross-check, not as data. |
| 19 | GPT handoff Track B: "Use exact base IDs and relevant unit files" from the branch | GPT's report says it could not see them. Base ids and unit ids are now provided as files in `docs/handoff/inputs/`. |
| 20 | Dossier and both handoffs do not mention moving forces between bases | Dynamic Campaign Mod already lets owned ships and squadrons move between friendly ports and fields, and has a purchase-time yard picker driven by `yardChoices` and `aircraftYards`, which the world campaign does not set (BA-08). |

### 6.3 Confirmed

Catalogue count: the built campaign has 1,642 entries; `docs/releases/20261107/validation.json:15`,
`README-FIRST.txt:596,612` and `STEAM-PAGE-DESCRIPTION.txt:24` say 1,636. The discrepancy is real;
its cause was not traced here. "16 checks" appears in the limitation text of
`docs/releases/20261107/validation.json`; the candidate's `validation.json` has 17 results and the
code review confirms 17, so the 16 is a wording fault. 196 bases, 293 forces, 54 patrols, 11
shipping lanes, bounds -62/74 and -100/258, the four `tankers` entries, six Djibouti nodes, Diego
Garcia as an AirBase supplied from Bahrain, `ops_ind_utkrosh` supplied from Mumbai, 25 world
awards, the F8 pop-out off by default with the "IMGUI repaint=False, clicks=False" record, the
three accepted author mods, Jose Rizal restored, about 27 mods updated, `dev` and `beta` at
`a0721c18`.

### 6.4 Could not be confirmed

- "R14's accepted set has 200 Workshop mods plus SEST (with 12 retired entries)": the load order
  has 200 tokens; the gallery index lists 5 mods no longer in the order. "12 retired" was not found.
- "older material says 1,586" catalogue entries: not looked for.
- `steam` branch at `0776fa50`: not visible in this worktree.
- "The main F8 interface passed earlier owner PC testing": owner-reported. No session log of 15 to
  17 November records F8 use, and nothing shows the author's tool working in a 0.9.3 mission.
- F11 tab indices 0 to 3: the tab labels are Overview, Forces, Combat Costs, Service
  (`WorldOperations.cs:501`); the indices were not traced.
- `WorldOperations` catch path setting `stopped = true` exists (`WorldOperations.cs:240`); whether
  it would take F11 Costs down with a Regional Watch fault was not traced.
- Dossier 2.2, supply model ("depots make stock; shipments carry it; airlifts move stores"): what
  Dynamic Campaign Mod does with the `tankers` and `replenishment` tables in play is not established.
- UK Voyager to RAF Typhoon missing receiver fit: recorded as missing in the older register; not
  re-checked against the 17 November files.
- Every statement in the package about real-world facilities, treaties and traffic: not checked by
  the repository work. GM-01 to GM-04 and GP-10 exist to check them.

## 7. Owner answers that packages wait on

1. New-item naming depth: display name only, or also folder name, campaign folders, world
   campaign id, ribbon ids, unit ids, save keys and settings folders? Saves need not carry over,
   so all are possible; each renamed layer is more builder and test work.
2. Prefix for ids and files in the new item, and whether the plugin ids `io.github.sest-hobby.*`
   stay (they carry the creator identity, not the product name).
3. Short name for console and log text.
4. In-fiction wording such as "SEST Scenario Awards Board": keep or reword.
5. Sides for South Africa and Argentina, or leave both out and use their ports as labels only.
6. Antarctic stations: labels and waypoints (recommended) or owned bases.
7. Ribbons before award: name shown or hidden; dimmed strip or blank tile; `RIBBONS.txt` kept as
   a marked full reference or cut down.
8. Coordinated Strike: advice only, or also an attack-waypoint button; whether to write to the
   author first.
9. May SEST add the missing tanker declarations to other authors' KC-46, KC-135 and KC-10A files.
10. The 21 photos with no credit: supply credits, replace, or withdraw.

## 8. Input files in `docs/handoff/inputs/`

Made on 17 November from committed files at `89b9b4649`; read-only extracts, no builder reads them.

| File | What it is | Made from |
|---|---|---|
| `region-template.json` | The fill-in template for region research; the union of what the four builder layers consume | world-expansion scope |
| `gmo-bases-89b9b4649.csv` | The 196 bases of the built world campaign: id, name, side, nation, kind, lat, lon (campaign value and east/west value), depot, yard, income, supplyFrom. 43 are depots | the committed `campaign.json` |
| `units-by-nation-regions.csv` | 729 rows: unit ids by operator nation for India, Brazil, Chile, Argentina, Peru, South Africa, Morocco, Algeria, Pakistan, UK, France, Australia, New Zealand, Egypt, Iran, Spain, plus US airlift and merchant hulls. A unit appears once per nation that operates it | the scope's inventory `wf2/world-expansion/units_by_nation.json`, which ran the builder's own operators() over the load order |
| `world-awards-25.csv` | The 25 world-campaign awards: id, name, required count, the counter in code, citation | `WorldServiceLedger.cs:135-152` and TheatreName() |
| `gallery-nopic-batch1.csv` | 11 unit ids added by the 17 November mod updates that have no picture | gallery scope |

Extracts the build assistant still has to make before the dependent package can be sent:
`briefings-tanker-ras.csv` and `aar-compatibility.csv` (GP-01), `new-item-fact-sheet.md` (GP-04),
`strike-panel-strings.txt` (GP-05), `sest-visible-lines.csv` (GP-09), `gallery-assets.csv`
(GM-09), `air-weapons.csv` (GM-13), `required-mods-usage.csv` (GM-14), later photo batches
(GM-08). `native-strike-final-plan.txt` (GP-05) is in the session scratchpad, not in the
repository, and must be copied in before it is attached.
