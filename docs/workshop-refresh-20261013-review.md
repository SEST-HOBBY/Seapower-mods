# Workshop refresh, 13 Oct 2026 - review

The review of the two captures on `chore/workshop-refresh-20261013`:
`0b0d137b` (15:34) and `e7e918e2` (15:45, Red Storm Arsenal's "small missile
fix"). The facts are in `data/install-snapshot/workshop-refresh-summary.txt`;
this page judges them. The previous capture is `af56cf74` (10 Oct 23:12), the
previous export `33cb8a88` (11 Oct). Times are PC time (UTC+10).

How it was checked: twelve areas each read by one reviewer and re-derived by a
second, then a completeness pass; a trial rebuild of all 22 packs at
`0b0d137b`; the checks of the capture brief. **verified** means seen in a file
or a command's output; **inferred** means reasoned from those. Nothing SEST
ships was changed on this branch.

## 1. What the game is running - high

- **verified** Sea Power loads SEST from the Workshop copy, item 3812461539, at
  position 1 of the live list (`load-order.live.txt:6`). The local
  `StreamingAssets\SEST_Integration` (3578 files on 10 Oct) is gone
  (`streaming-assets.txt`: "SEST folders present: 0"), and the menu film plays
  from the Workshop folder (`player.log:30`).
- **verified** The copy's `SEST.MenuBackground.dll` (sha256 `43bb0d1d...`,
  written 11 Oct 03:24) is byte-identical to the plugin committed in
  `a94d9939` (10 Oct 23:29), so the copy is a 10 Oct-or-later upload. The DLL
  has not changed since, so it cannot tell the 10 Oct evening build
  (`034e8595`, 3578 files, still has the Briefing Room) from the deploy head
  (`596b0867`, 3575 files).
- **verified** The loose user missions on the PC match the deploy head byte for
  byte (land units on firm ground), installed after 11 Oct 00:20.
- **inferred** Most likely the deploy head was synced, uploaded, and the
  subscriber test in `docs/campaigns/southern-watch/publishing.md` run without
  its last step (unsubscribe, sync). An upload of the older local build fits
  the facts too. Only a look at the Workshop folder settles it (section 13).
- **verified, from the scripts** SETUP refuses to run with both copies present.
  `set-mod-order.ps1 -AddMissing` (also the last step of `sync-sest.ps1`) knows
  only the token `SEST_Integration`: with the local folder gone it would skip
  it AND drop 3812461539 as a stale Workshop entry (`set-mod-order.ps1:173-211`),
  leaving no SEST entry in the list (the in-game effect is inferred).
  `sync-sest.ps1` recreates the local folder but never looks for the Workshop
  copy. **So no new mod may be placed until SEST is back on its local folder.**
- **verified** No Workshop update can be made either: the upload picks the local
  folder, which is gone.

## 2. Checks (brief section 15), at `e7e918e2`

| check | result | why |
|---|---|---|
| check_inventory | FAILED | the 5 new mods are in neither the catalog nor the order; 4 mods (3775128499, 3776340577, 3780118683, 3781062859) short by one byte per line - not upstream updates: their repo copies were committed 23-24 Aug with CR stripped, before `mods-source` was pinned `-text` (fix on the PC with `git add --renormalize`) |
| check_load_order | pass | it checks the canonical order, not the live one |
| check_dependencies | FAILED | SEST_Replenishment's stale `usn_ffg_constellation` (AN/SPY-6(V)3-FCR, removed by Red Storm Arsenal) and `usn_ddg_arleigh_concept` (UYK-20, replaced by Modern US Navy); both clear on rebuild |
| check_pack_fidelity | FAILED, 38 files | 34 Modern US Navy hulls, 2 Red Storm Arsenal, `ko_ddg-995` (Korea), and `plan_ffg_krivak2`, which no mod ships now. Upstream moved; the rebuild re-forks them and SEST's one line (`ReloadableWithoutMagazine`) still applies |
| check_game_version | FAILED | every pack says 0.8.4, the game is 0.8.5. Repo policy: the game only warns when MAJOR.MINOR differ (`check_game_version.py:5-10`), so players see no warning (inferred) |
| check_vanilla_drift | pass | the game files did not change in this capture; 0.8.5 arrived 10 Oct |
| check_alias_bases, campaign_coverage, scenarios, stale_phrases | pass | |

## 3. Trial rebuild - high

At `0b0d137b`, 4 of 22 packs fail: SEST_Collection_Fixes, SEST_RAAF_Bases,
SEST_Replenishment, SEST_Campaign.

- **verified** Collection Fixes stops first: Euromod Main Pack deleted
  `ammunition/usn_rim-174c.ini` (SM-6 Block IB), the donor of
  `build_patch.py:644-648` (LOFT_ANGLE). `build_all.py` then writes no dist.
- **inferred** The other three follow from it (RAAF Bases and Campaign want
  the `usn_mh-60r` Squadron20 Collection Fixes adds; Replenishment wants the
  priced `usn_cal_40mm` Collection Fixes restores). A theory until a rebuild
  passes.
- **verified** Once SEST stops shipping its SM-6 IB, the game reads U.S. Navy
  2027's `usn_rim-174c` instead (live #14): Mass 705 against Euromod's 1900,
  LandAttackCapability=All against ShoreTargetsOnly, CIWSDefenceBonus 50. A
  decision (section 12).
- Rebuild from `e7e918e2`, not `0b0d137b`, or the Constellation fails fidelity
  again.

## 4. Updated mods

**Euromod - Modern US Navy (3390330875)**, 73 files. Burke, Virginia, Los
Angeles, Wasp, LCS, OHP MLU, Zumwalt reworked; UYK-20 replaced by a Euromod
system; the OHP MLU's combat system is now CMS_Multirole_MLU. No hull removed
or renamed; STALE_OVERWRITES still holds. 34 SEST forks re-fork on rebuild.

**Red Storm Arsenal (3413868677)**, 200 files over the two captures.
- Removed: `usn_qh_50e` (+ squadrons), `plan_ffg_krivak2` (+ variants).
  SEST's SULU SEA OFFENSIVE still puts two QH-50E on the Nimitz 2000s, and so
  do three of the player's own missions (INDO PAC SOUTH CHINA SEA OFFENSIVE,
  NEWEST clean small mission, SULU SEA OFFENSIVE); `check_scenarios` did not
  flag it. SEST's stale Constellation also embarks one. SEST still ships an
  orphan `plan_ffg_krivak2.ini` (no variants file), which the rebuild drops.
  The SEST Gallery lists both.
- Removed the SPY-6 fire-control radar from the Constellation, and the radar
  the forward ESSM launcher on USS Tripoli and the Fuso uses - those launchers
  probably cannot fire now, with or without SEST (inferred; an in-game check).
- The shared `[NSM]` launcher went from 4 rounds per container to 1; RSA
  rebuilt the Morris and Constellation launchers as 4x1, totals unchanged.
- 13 Oct, the author's note "small missile fix": the Constellation's
  `NumberOfAnimationReferences` 1 -> 3, so its NSM launcher and Mk 41 VLS
  animations are read (`workshop-change-notes.txt`).
- Eight RSA hulls are now dated 2029-2032 (Constellation, James Madison,
  Trump, United States late, three Burke variants, DDG(X)) - the world
  campaign is October 2028.

**Euromod - Main Pack (3629144864)**: deleted `usn_rim-174c` (above) and
`rn_mark8_mod4` (vanilla id; RADF and Royal Navy still ship it). New
LaunchGroups overwrites space Mk 41 launches 1 s apart on Burkes, Bunker Hill
and the OHP MLU (every target checked, SEST's copies included). Firing rates
for RAM/SeaRAM (42), Mk 57 reload 1.5 -> 2 s, the Zumwalt launcher 30 -> 20.
New Australian combat systems, unused so far.

**US Naval Aviation (3737267013)**: the GBU-12D seeker 10 -> 90 degrees, like
the game's own laser bombs. SEST ships its own copy (old 10 degrees), so the
fix reaches the game only after the rebuild (Collection Fixes must build
first). F-35B now has two squadrons, Squadron1 is VMFA-121 (the Wasp's
F-35Bs change livery; the world-campaign notes saying VMFA-211 is the only
squadron are stale). The rest is cosmetic.

**Euromod - South Korea Navy (3789208859)**: section 7.

**YF-23 (3796349767)**: lights plugin, smaller liveries, mission text. Its
AIM-424 file is byte-identical, so the guards on
`feature/aim424-usn2027-flight-model` pass and its effect is unchanged.

**FQ-44 Fury (3804868806)**: light materials and a lights DLL. It also has a
fifth AIM-424, `fury_aim424`, which the AIM-424 branch does not cover (this
capture only added SoundMode=1 to it).

**U.S. Navy 2027 (3606774881)**: unchanged, `usn_aim-424` included.
**Identify Expanded (3790594162)**: nothing new (its 125-file removal was
captured on 11 Oct; the SEST Gallery still lists the seven removed units).
**Flight Deck Ops (3373960386)**: decks of seven carriers and assault ships
(America, Forrestal, Kitty Hawk, Enterprise, Nimitz, Tarawa, Kiev), America
now flies SH-3H, HH-3 carrier-capable. SEST forks none of them.

**Others** - Italian Navy, Buildings and Objectives (government building),
Saronic Corsair, V-22 (new SV-22 ASW tiltrotor with Mk 54 and sonobuoys; title
changed, so the catalog title is stale), MV-75 (Copperhead loadout), EC-2,
Charles De Gaulle (Lafayette Sadral rework, E-2C/E-2D), French Air Force
(A330/A400M tanker lines), India (ins_d-66): none removed or renamed a unit;
SEST ships no whole-file copy of any changed file.

**Not updated**: Anchor Chain (1.1.0), Euromod Anchorchain Expansion
(EnhancedDecoyMod 0.5.2, MissileControlMod 0.1.15, MultiStageMissiles 1.7.4,
EnhancedUIMod 0.1.1). An update seen on Steam after 15:45 needs a new capture.

## 5. Plugins (brief section 12) - all 46 loaded, none failed

BepInEx 5.4.23.2, AnchorChain.Preloader 1.0.0, Anchor Chain 1.1.0, Identify
Expanded 1.0.0, Automatic SAR 1.0.0, Coordinated Strike Tool 1.3.1, Dynamic
Campaign Mod 0.24.3, the Euromod set above, SEST.MenuBackground. No resupply
plugin exists (RE-power ships no DLL). Changed since 10 Oct: AlpineSeaPower
0.3.0 -> 0.3.1, SaronicCorsairStrikeUSV 4.12.0 -> 4.12.1, EC2CommsJamming
1.0.0 -> 1.0.1, BellSystemsFixtureTilt 0.5.0 -> 0.5.1, DCM 0.24.2 -> 0.24.3,
new light DLLs for the Fury, EC-2 and YF-23, both Osprey DLLs rewritten
(version 0.0.0.0, change unreadable).

- The session before the first capture logged two exceptions in
  `ObjectBase.SpawnPilot`, each right after an FQ-44 Fury was lost. The stack
  runs through Harmony-patched methods, so a plugin is on the path; which one
  is not known.
- The menu film's "Unexpected timestamp values" and "Color primaries 0"
  warnings are harmless (the game's own clip logs the first).
- DCM's code loads although DCM is not in the Mod Manager list: Anchor Chain
  loads DLLs from every subscribed folder. It refuses a second copy of the
  same plugin id (`AlpineSeaPower.dll` ships in both the YF-23 and the Fury).

## 6. Dynamic Campaign Mod (brief section 10)

- **verified** 0.24.3 (`DynamicCampaignMod.dll`, 2,836,480 bytes, sha256
  `74149fc6...0fc0d2a`). The repo never recorded a 0.24.2 hash; the only
  stored hash is the reviewed 0.24.0. `_info.ini` unchanged (needs BepInEx
  and Anchor Chain in its text; game 0.8.3 to below 0.9.0).
- **verified** The example campaign changed in one way: a new optional
  top-level `yardChoices`. Nothing the world campaign writes was removed or
  renamed.
- **verified** One feature is off on game 0.8.5: `ObjectBase._geoPosition` is
  missing, so AI bombers inside their missiles' minimum range are not sent out
  of it.
- **verified** Not in the live Mod Manager list because the deploy branch
  lacks `d0f268e3`, which only this branch has.
- **inferred, high** The world campaign would be refused today: both the
  branch draft and the copy installed on the PC (the 10 Oct build, 129 bases)
  offer `usn_qh_50e` and `plan_ffg_krivak2` in the buy list, and on 10 Oct
  0.24.2 refused it over six missing units. Do not start the installed copy.
- **fixed** The SSBN patrols carried `"hold": true` on the force; the sample
  puts it on the patrol entry. Fixed on the world-campaign branch
  (`395c8b18`), with a validator rule for any key the sample never uses.

## 7. Korea (brief section 11)

| unit | status |
|---|---|
| `rok_kuh1` KUH-1 Surion | loads now (top-level file). Unarmed. Its main rotor paint points at `aircraft/rok_uh60/ko_mat.ini`, which no mod ships |
| `rok_fa50` FA-50 | loads now. Default loadout 2x AIM-9M + gun. Marked CarrierCapable |
| `rok_kf21` KF-21 | loads now. Default loadout 4x `fr_meteor`, which only Ultimate Missile Workshop or French Air Force supply. Marked CarrierCapable |
| KSS-I/II/III `ko_SS-I/II/III` | file in an ignored place (`vessels/non/`), untouched, and placeholders: UnitType=Vessel copies of a frigate/destroyer. The world campaign is right to keep them UNUSABLE |

Also new and loadable: `rok_f15k`, `rok_f35a`, `rok_f4e`, `rok_f5e`,
`rok_kf16`, `rok_p-3c`, `rok_mh60`; six show internal codes as names. A stray
`usaf_f-16c_blk40` is broken (no rounds, model or names). No Korean submarine
hull name exists in any name file. The author moved the Jeongjo the Great
(`ko_ddg-995`) from the Lynx to the new `rok_mh60`; SEST's copy still has the
Lynx until the rebuild. `rok_mh60`'s paint folder is misspelt upstream.

## 8. The five new mods - compatibility plan

None is in the live list, the canonical order or the catalog yet.

| mod | what it adds | warheads | proposed slot | use in SEST |
|---|---|---|---|---|
| BUK-M3 3564792549 | Buk-M3 battery: TELAR `wp_buk-m3`, launcher `wp_bukslave`, radar `wp_m3-radar`, round `wp_9m317ma` | conventional, Power 25 | below S-350 Vityaz (tokens line 142) | land-defence modern Russian medium layer; world campaign Russia air defence (TELAR only) - after an in-game check |
| ISKANDER-K 3569219326 | an older copy of THE REDFOR MOD's Iskander-K, same ids (`wp_iskander`, `wp_r-500`) | conventional, Power 64 | directly below REDFOR (line 180), where it changes nothing - or unsubscribe | none; REDFOR's fuller copy wins |
| ICBM silos 3556629790 | US Minuteman III and Soviet RT-23 silo fields, six missiles each | Power 10000, nuclear-scale | after Type 12 SSM-ER (line 173) | none: no nuclear weapons in campaign magazines (`campaign-bible.md:327`) - mission editor only |
| Road Mobile ICBMs 3571718093 | Topol-M and DF-41 launcher trucks | Power 10000, nuclear-scale | with the silos | none, as above |
| Prithvi TBM 3731931836 | Indian TEL `ina_prithvi_tel`, Prithvi II (55-165 NM) and III (55-324 NM) | conventional, Power 170 | below Fattah-2 (or alphabetical, line 137) | Range Week or scenarios; India has no world-campaign nation |

Defects and notes:
- BUK-M3 shares `[SA-26]` in `systems/weapons.ini` with four aircraft mods
  (KC-135, Su-24M, Su-30SM2, Tu-95MS) that set ReloadTime=0; BUK-M3 sets 120.
  Below them the Buk-M3 reloads at once. `check_mod_conflicts` does not see
  merged-section clashes. Its launcher names a radar nothing defines; its
  radar declares 3 sensors and defines 2; its variants files declare 1 of 4;
  its names are Cyrillic (SEST_Name_Fixes transliterates them, so placing it
  changes the pack).
- The ICBM trucks ask for `ICBM_Launcher`; the mod defines `ICBM_Launchers`.
  Whether they fire is untested. The silos read "AShM Site" in the editor.
- Prithvi borrows the PLA Land Unit Pack's (3733719765) df-15b debris model.
  Its Chinese title is lost only in `workshop-updates.txt` (the PowerShell pipe).
- Every accepted mod needs a token, a catalog entry and a coverage excuse in
  one change, or `check_campaign_coverage` goes red (tried in a scratch copy).
  Placing the mods is a PC step after the order lands (section 13).

## 9. Stock pictures at startup, between menus and in the Mod Manager

- **verified** None of these can be replaced by a file in the pack: a file
  wins only where the game looks a picture up by name through its file manager
  (loading_screen_N.png on mission loads, campaign backgrounds, loading tips),
  and SEST already does all three.
- **inferred** Startup / first load: the game's LoadScreen view, whose
  background binds to "BackgroundImage" and draws the one built-in picture
  `ui/loading/background1` (resources.assets) or reads the stock folder
  `/original/ui/backgrounds` directly.
- **inferred** Between pages: a still bound to "BackgroundImage" in the main
  menu's background pane, beside the film. The game also rebuilds the film
  player between pages, outside the plugin's watch windows (10 minutes after
  start, 30 s after a scene load), so the stock film can show too.
- **inferred** Mod Manager: it reloads the game when the order changes
  (`ui.ini:141`), so its stock picture may be the startup screen again.
- Plan: widen `scan-ui-assets.ps1` (it lists only 400 of 796 code names and
  drops runs over 120 characters); a logging pass in the menu plugin that
  records every on-screen picture and its binding; then the swap, using the
  pack's 29 credited photographs. The plugin changing UI pictures is a step
  beyond today's film-only scope - a decision.

## 10. Game version

0.8.5 Build 261008 (8 Oct) reached the PC 10 Oct 07:47. Its real changes sit
under 0.8.4 Build 261007 in the changelog (camera shake, bombing accuracy,
aircraft stuck climbing, destroyed units returning in campaigns, MOSS
torpedo tube, translations, crash reporting); none touches unit keys,
systems, airbases, loading screens or mod loading. The bump is
`check_game_version.py --bump 0.8.5` and a rebuild. Not covered by the bump:
`docs/FEATURES.md:10` and `integration/gallery/steam_art/cards.json:154`
("Built for Sea Power 0.8.4", rendered into a Steam image). The world-campaign
builder writes no ApproximateVersion and needs its own fix before it merges.

## 11. The four inventories (brief section 13)

A Steam-tracked 196 = B folders 196. C canonical 190, all in A. D catalog
installed 190 = C. A minus C: the five new mods and 3812461539 (SEST's own).
Live list 192 = 189 of C + 3812461539 + ACConfigs (off) + sest-world-sandbox;
C minus live: DCM and the local SEST_Integration. Nothing canonical is
missing from disk; nothing was removed. `check_inventory` counts 195 because
it skips SEST's own item.

## 12. Decisions for the player

1. SEST on this PC: the local build (the documented setup; unsubscribe from
   3812461539) or the Workshop copy.
2. SM-6 Block IB (`usn_rim-174c`): let U.S. Navy 2027's round take over, or
   keep shipping Euromod's last version from SEST.
3. Which of the five new mods to keep, and BUK-M3's reload time and missile
   (its own active-radar 9M317MA or Euromod's semi-active `wp_sa-27`).
4. Dynamic Campaign Mod required for every pack user (`d0f268e3`)?
5. SULU SEA OFFENSIVE's two QH-50E: drop them or retarget to the game's QH-50D.
6. Red Storm Arsenal's broken sensor names on hulls SEST forks: repair in SEST
   or report upstream.
7. The world campaign's 2029-2032 RSA hulls; the new Korean aircraft for
   South Korea; the Wasp's F-35B squadron.
8. The AIM-424: the Fury's `fury_aim424` joins the decision on hold.
9. The menu plugin swapping UI pictures, and which photographs.
10. Ship the 0.8.5 bump in the 13 Oct update or later.

## 13. PC steps, in this order (game closed)

1. Date the Workshop copy, read-only:
   `$w='C:\Program Files (x86)\Steam\steamapps\workshop\content\1286220\3812461539'`;
   `(Get-ChildItem $w -Recurse -File).Count` (3575 deploy head, 3578 the 10 Oct
   evening build); `Test-Path "$w\missions\SEST Briefing Room"` (False =
   deploy head).
2. If the local build is chosen: unsubscribe from 3812461539, wait until its
   folder is gone, `git checkout sest-dev/loving-bell-3cnvvw`, run
   `tools\sync-sest.ps1` (it should end "IN LINE ... 596b0867"), start the
   game once, check the first Mod Manager entry is the local pack.
3. Do not start the installed world campaign.
4. Restore the four CR-stripped mods: on the deploy branch,
   `git add --renormalize` their four folders, check
   `git diff --cached --ignore-cr-at-eol --numstat` shows no real change,
   commit, push.
5. Only after the repo change for the new mods lands: SETUP or
   `set-mod-order.ps1 -AddMissing`.

## 14. Repo work for the next pass, in order

1. Collection Fixes: replace the `usn_rim-174c` donor (decision 2); rebuild
   from `e7e918e2` with the 0.8.5 bump; every gate and both test suites. This
   re-forks the 38 stale files, ships the GBU-12D seeker and the DDG-995 MH-60,
   and drops the orphan Krivak II.
2. SULU SEA OFFENSIVE's QH-50E; a check that flags rostered aircraft no mod
   defines.
3. World campaign: rebuild on this export (drops `usn_qh_50e` and
   `plan_ffg_krivak2`), record DCM 0.24.3 and its hash, fix the 0.24.0/0.24.2
   labels and the VMFA-211 wording.
4. The accepted new mods: tokens, catalog entries, coverage excuses, rebuild.
5. Catalog: V-22 title and notes, the Korean mod, Iskander-M's REDFOR note.
6. Tooling: `sync-sest.ps1` stops when the Workshop copy is on disk;
   `set-mod-order.ps1` recognises 3812461539; the capture's "updated" date
   is the folder's last-write time and misses updates (read Steam's
   timeupdated); regenerate `data/mod-fingerprints.json` after this capture;
   skip SEST's own item in `-CheckUpdates` and write its report as UTF-8; keep
   the whole BepInEx log; raise the 200-file Workshop picture cap;
   `check_mod_conflicts` to report merged-section clashes;
   `check_load_order` to read the live order too.
7. The stock pictures: wider scan, plugin logging pass, then the swap.
8. Then the 13 Oct Workshop update: Steam artwork and page text written
   against the green build.
