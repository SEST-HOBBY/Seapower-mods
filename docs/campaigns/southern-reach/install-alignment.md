# Aligning the gaming PC with this branch — and with the other sessions

This is the procedure for bringing a Sea Power install up to a build that
carries **the three campaigns** (Southern Watch, Southern Reach and Red Line)
together with every fix the other sessions have pushed, and the work ported
from their older branches (§6). It replaces
the counts in `../southern-watch/install-alignment.md`; the checks and the
failure story there still hold and are not repeated.

Two facts shape it:

- **The PC deploys from one branch**, the one `data\deploy-branch.txt` names:
  `sest-dev/loving-bell-3cnvvw`. `sync-sest.ps1` refuses to run from any
  other branch, on purpose — the last time it ran on the wrong one it reported
  `IN LINE` against a build with none of the campaign in it.
- **Sessions work on their own branches.** This session's work is on
  `claude/campaign-missions-lore-td653z`. That branch is built on the deploy
  branch's latest commit, so bringing it into the deploy branch is a
  fast-forward: nothing to resolve.

Close Sea Power before any of it. It rewrites `usersettings.ini` on exit and
throws away a load-order change made while it is running.

## Already aligned once? The short version for later rounds

After the last round both `sest-dev/loving-bell-3cnvvw` and
`feature/northern-front-iii-export` sit on `d5468582` (the Tasman Shield
proofread and the ISR notes). Everything this session has pushed since builds
straight on that commit, so a later round is the same fast-forward and one
sync:

```powershell
cd C:\Users\<you>\Seapower-mods
git status --short                                   # must be EMPTY
git checkout sest-dev/loving-bell-3cnvvw
git fetch origin
git merge --ff-only origin/claude/campaign-missions-lore-td653z
git push origin sest-dev/loving-bell-3cnvvw
git push origin sest-dev/loving-bell-3cnvvw:feature/northern-front-iii-export
powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1 -RefreshMissions
```

Type each command on its own line: the sync command pasted twice on one line
is read as a file called `sync-sest.ps1powershell` and refused.
`-RefreshMissions` is what reaches the missions you imported from the game
yourself (the Northern Front files and the chapter missions): it gives any
airliner whose route ran out inside the mission clock one more waypoint along
its airway, so it stops circling. The campaigns are rebuilt in the repo
and need no flag. If `--ff-only` refuses, stop and report it, as in step 2.

### This round: Red Line and the ported work

This round adds a third campaign to the same pack, **Red Line — The Other
Watch**: six missions played from the Chinese side, with its own folder of
docs (`docs/campaigns/red-line/`). It also redraws nine Southern Watch and
Southern Reach mission cards whose objective ring ran off the chart, and it
brings eleven pieces of the other sessions' work (§6), among them three new
packs: SEST Replenishment At Sea, SEST A-10C+ and SEST Intercept Model. The
pack count is **20**.

The installed file count goes from 691 to **1189**:
`campaigns\sest-red-line\` (44 files: six missions with their briefing
folders, 16 art files - the four story pages and 12 images - `campaign.ini`,
roster, commander settings and a `REQUIRED-MODS.txt`) and the browser copies under `missions\Red Line\` (31),
plus 423 from the ports: 333 vessel files (Replenishment's reloadable
launchers and supply systems), 87 ammunition files and 3 aircraft files.
Nothing needs subscribing: every mod it places is one the canonical load
order already enables. Step 5 has its checks, and §6 has **four one-time
steps on the PC** that the ports need.

---

## 0 — where things stand (read this first)

| Branch | What it is | State |
|---|---|---|
| `sest-dev/loving-bell-3cnvvw` | the deploy branch the PC tracks | at `d5468582` after the last round's push |
| `claude/campaign-missions-lore-td653z` | this session: the three campaigns, the multi-campaign builder, the coastline proof, the RNZAF bases, and the ported work | `d5468582` plus this round; every pack rebuilt from scratch; the gates in step 3 pass |
| `feature/northern-front-iii-export` | the repo's default branch on GitHub | at `d5468582` with the deploy branch if the last round's second push was made; do not deploy from it |
| the other `sest-dev/*`, `fix/*`, `feature/*`, `chore/*` branches | earlier sessions | see §6: what was ported, and what was left and why |

So "aligned to this session and the other sessions" means: the deploy branch
fast-forwarded to this session's branch, then the normal sync, then §6's
one-time steps.

## 1 — on the PC: find the clone and get on the deploy branch

`<you>` is a placeholder for a real path, not something to type — PowerShell
reads `<` as a redirection operator.

```powershell
@("$env:USERPROFILE", "$env:USERPROFILE\Documents", "$env:USERPROFILE\source\repos",
  "$env:USERPROFILE\Desktop", "C:\", "D:\") |
  ForEach-Object { Get-ChildItem $_ -Directory -Filter Seapower-mods -ErrorAction SilentlyContinue } |
  Select-Object -ExpandProperty FullName
```

```powershell
cd C:\Users\<you>\Seapower-mods
git status --short                       # must be EMPTY - see below if not
git fetch origin
git checkout sest-dev/loving-bell-3cnvvw
git pull origin sest-dev/loving-bell-3cnvvw
```

If `git status --short` prints anything, the PC has local changes (usually a
mission you edited in game and imported). Do not lose them and do not carry
them into the merge blind: `git stash` before the checkout, and `git stash pop`
after step 2 only if you know what they are. A clean tree is the condition
for everything below.

## 2 — bring this session's branch into the deploy branch

```powershell
git fetch origin claude/campaign-missions-lore-td653z
git merge --ff-only origin/claude/campaign-missions-lore-td653z
```

`--ff-only` is the check. It succeeds silently if, and only if, this session's
branch already contains everything on the deploy branch — which it does as of
its last push. If it refuses (`Not possible to fast-forward`), somebody pushed
to the deploy branch after this session merged it; stop and say so rather than
doing a real merge on the PC. The fix is one more merge in a session, not a
hand merge on the gaming machine.

Then push the deploy branch so the PC and GitHub agree:

```powershell
git push origin sest-dev/loving-bell-3cnvvw
```

Then make GitHub show it. The repository's landing page (and every new
session, which starts from the default branch) reads
`feature/northern-front-iii-export`, which moves only when you push it.
Either:

- **GitHub → the repository → Settings → General → Default branch →**
  switch to `sest-dev/loving-bell-3cnvvw` (recommended: the page, the README
  and every new session then start from what the PC runs), or
- fast-forward the old default branch to match, from the PC:

```powershell
git push origin sest-dev/loving-bell-3cnvvw:feature/northern-front-iii-export
```

That push only succeeds as a fast-forward, which it is today; it cannot
overwrite anything.

Check, and do not skip:

```powershell
git branch --show-current            # sest-dev/loving-bell-3cnvvw
git log --oneline -1                 # note the short hash: the IN LINE line must name it
Get-Content data\deploy-branch.txt   # sest-dev/loving-bell-3cnvvw
Test-Path integration\dist\SEST_Integration\campaigns\sest-red-line\campaign.ini   # True
```

The last line is the one that says the merge brought this round.
`False` means step 2 did not take.

## 3 — let the build check itself (optional on the PC, done here)

The committed packs are the builders' own output, rebuilt from scratch on
this tree in this session with a clean `git status` afterwards, and the gates
were run on it:

```
python tools\build_all.py --from-scratch      # 20 packs, clean git status after
python tools\check_campaign_coverage.py       # three campaigns, 1524 placed references, 162/162 mods and packs
python tools\check_load_order.py
python tools\check_dependencies.py
python tools\check_weapon_employment.py
python tools\check_scenarios.py
python tools\preflight.py "Tasman Shield 09 - The Southern Convoy"
```

`check_inventory.py` is the one known red: it stays red until the PC runs
the mirrored export (§6, step 2). Running the rest again on the PC proves the
PC's Python sees the same tree; it does not change what gets installed. Skip
it if you are short of time; do not skip step 2's checks.

## 4 — install and order, one command

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1
```

What to read in its output:

| Line | Means | If it is wrong |
|---|---|---|
| `IN LINE: all N installed files match this commit (hash)` | the deployed bytes equal the commit | the hash must be step 2's; a different one means the pull did not take. **N is 1189** for this build |
| `1 of 1` installed | the consolidated pack copied | `canonical pack not installed` means the copy failed; nothing below matters |
| `dropped stale workshop entry` | a subscription the repo has not catalogued | none expected. An id it names is a new subscription: export it (`export-mod-configs.ps1`) and push, as the Southern Watch procedure describes |
| `purged SEST_…` | an old per-pack folder removed | only on a machine that still had the per-pack layout |

Where the count comes from, from Southern Watch's 388: the pack ships
`campaigns\sest-southern-reach\` (25 missions with their briefing folders and
charts, 66 art files, `campaign.ini`, roster, commander settings and a
`REQUIRED-MODS.txt`), the browser copies under `missions\Southern Reach\` and
`missions\Tasman Shield\`, a `REQUIRED-MODS.txt` for Southern Watch's own
folder and the two RNZAF base files (691 in all); then this round's Red Line
and ported files (1189).

## 5 — confirm the campaigns arrived

```powershell
$sa = "<…>\Sea Power_Data\StreamingAssets\SEST_Integration"
Get-ChildItem "$sa\campaigns" -Directory | Select-Object Name        # sest-red-line, sest-southern-reach, sest-southern-watch
(Get-ChildItem "$sa\campaigns\sest-southern-reach\art\*.png").Count   # 47
(Get-ChildItem "$sa\campaigns\sest-southern-reach\missions\*.ini").Count   # 25
(Get-ChildItem "$sa\campaigns\sest-red-line\art\*.png").Count         # 12
(Get-ChildItem "$sa\campaigns\sest-red-line\missions\*.ini").Count    # 6
Test-Path "$sa\land_units\airbase_rnzaf_ohakea.ini"                   # True
Test-Path "$sa\vessels\plan_aor_type901.ini"                          # True: Replenishment arrived
Get-ChildItem "$sa\missions" -Directory | Select-Object Name          # Red Line, Southern Reach, Southern Watch, Southern Watch - Dispatches, Tasman Shield
```

Then in game, in this order:

1. **Mod Manager** — `SEST Integration Pack` at the top, enabled; its
   description lists SEST A-10C+, SEST Intercept Model and SEST
   Replenishment At Sea among the packs and ends "Southern Watch - Southern
   Reach - Red Line".
2. **Campaign list** — three entries: `Southern Watch (Royal Australian
   Navy)`, `Southern Reach - Tasman Shield (Royal Australian Navy)` (44
   entries, a dark chart 29–66°S behind it) and `Red Line - The Other Watch
   (People's Liberation Army Navy)` (10 entries).
3. **Mission browser** — folders `Southern Reach` (12), `Tasman Shield`
   (13) and `Red Line` (6) beside the Southern Watch ones. If the campaign
   list is short but the browser has every folder, the Mod Manager is not
   reading one of the `campaigns\` folders; that difference is the diagnosis.

## 6 — the other sessions' branches: what was ported, what was not

Two older lines held work the deploy branch lacked: `sest-dev/kind-faraday-ctr5h0`
(with `beautiful-cerf-i7fqei`, `fix/banda-front-lean-finalize` and
`affectionate-volta-3xqkx6` inside it) and `feature/ras-integration` with
`chore/workshop-inventory-20260916` (the INV line). Neither was merged whole:
each forked in late August from a mod list older than the PC's. Instead,
eleven items were ported one by one, each rebuilt against today's export and
reviewed on its own before it landed here (merge `17df05a6`):

1. The JMSDF Seahawk rename (SW10, the Mogami pack, the Banda vignette, the
   Northern Front saves), the exporter's deletion mirror, and mission
   installs with no timestamped backups (`-PurgeBackups`).
2. The editor-crash sweep over every mission the installer deploys (32
   aircraft in nine files), `preflight --all` and `check_alias_bases`.
3. The land-defence site builder and the Indo-Pacific Land Assets showcase.
4. Banda Front Lean v2 and Living Seas as saved, `restore_roe`, and the
   generator chain behind them.
5. ARRW boost-glide, the Redback's seeker reach and the AIM-424 respec
   (680 kg).
6. The SM-3 overwrite's seeker and handover, folded into SEST Collection
   Fixes.
7. SEST Intercept Model: the global intercept table restored.
8. SEST A-10C+ and the standard A-10C's infrared head and squadron repairs; a
   second Warthog in D8.
9. `check_inventory`, `check_scenarios`, a stricter `check_dependencies`, and
   SW11's ghost Burke retargeted.
10. SEST Replenishment At Sea: working replenishment for the modern fleet,
    HMAS Supply and Stalwart real suppliers.
11. Eleven NF3 scenarios regenerated, with supply ships where the load order
    defines them.

Deliberately **not** ported:

| Item | Why not |
|---|---|
| SEST YF-23 MALICE pack | upstream now ships the fit: the restructured YF-23 mod carries its own AIM-424 intercept loadout, and the file the pack patched is gone |
| SEST Zumwalt CPS | retired on 20 Sep (`1233fd41`): Modern US Navy fixed both defects it existed for |
| the F-15EX AIM-260 seat lift | withdrawn (`afed87ce`) after an in-game report: the number was measured against a different missile mesh |
| the U.S. Navy 2027 retargets | not needed: the aliases resolve today, and `check_alias_bases.py` proves it after every export |
| the standalone SEST Aegis BMD pack | superseded: its SM-3 seeker and handover values are in SEST Collection Fixes (item 6), and its floor, range and loft were decided otherwise here |
| INV's `generate_load_order` and exporter rewrites | written on the 16 Sep base; the tools here have moved on since (the kind-faraday deletion mirror, unsubscribed mods dropped from the order), and the rewrites would undo that |
| peaceful-gauss's Workshop staging script | built for a two-item Workshop release that the one-pack design replaced |

The other branches (`feature/northern-front-iii-export`,
`sest-dev/quirky-noether-fq5i98`, `claude/repo-cleanup-interoperability-hleer5`)
hold nothing the deploy branch lacks.

### One-time steps on the PC for the ports

Game closed, after the sync in step 4:

1. **Clear the old backup missions.** Installs no longer write
   `* backup-<stamp>.ini` copies, but the old ones are still in the game's
   mission list. Preview, then purge:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1 -PurgeBackups -WhatIfOnly
   powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1 -PurgeBackups
   ```

   Only names ending ` backup-<digits>` are touched; a mission of your own
   called "Strait backup-plan" survives.
2. **Run the export once, now that it mirrors deletions.**

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1 -IncludeVanilla
   git status --short mods-source
   ```

   Expect deletions: the ghost files earlier exports left behind (about 200
   over 13 mods; `docs/packaging-and-recovery.md`, *Known red*, lists them).
   Review them, then commit and push. `python tools\check_inventory.py`
   should then go green; the same section says what to do if four mods stay
   red on line endings, and which pre-flight failure the deletions are
   expected to cause.
3. **Rebuild after that export, and after every export from now on.**
   SEST Replenishment At Sea freezes about 300 hulls at the export it was
   built from, so a pack older than the mods beside it puts last month's hull
   above this month's mod. `python tools\build_all.py --from-scratch`, commit
   the output with the export, push; or push the export alone and say so, and
   the next session rebuilds on it.
4. **Sync again** so the game carries the rebuilt pack.

## 7 — then play

Each test card now opens with a short *first things to fly after this round*
list: the in-game checks the ports added, pointing at where each is written
up. Southern Watch's (`../southern-watch/test-card.md`) has the most of them.
Southern Reach's (`test-card.md`) still starts with the coastline, and Red
Line's (`../red-line/test-card.md`) with its rules of engagement.

---

## When something is wrong

| Symptom | The command that answers it |
|---|---|
| `git merge --ff-only` refuses | `git log --oneline origin/sest-dev/loving-bell-3cnvvw -5` — whatever is there and not on this session's branch was pushed after the merge here; report it |
| sync refuses on the branch guard | you are not on `sest-dev/loving-bell-3cnvvw`; go back to step 1 rather than passing `-AnyBranch` |
| a campaign is missing in game but present on disk | `Get-ChildItem "$sa\campaigns\sest-southern-reach"` (or `sest-red-line`) shows the files; the browser copies are your route in, and the difference is the report |
| a Southern Reach unit is missing in a mission | the unit names its mod: `campaigns\sest-southern-reach\REQUIRED-MODS.txt` lists the 32 hard-required Workshop mods for this campaign; `.\tools\show-load-order.ps1` shows which are enabled |
| a Red Line unit is missing in a mission | `campaigns\sest-red-line\REQUIRED-MODS.txt` lists the 29 hard-required Workshop mods for that campaign |
| a ship is ashore or a route crosses land | the coastline extract disagrees with the game there; note the mission and the hull, that is the first row of the test card |
| `check_inventory.py` red after the export | read `docs/packaging-and-recovery.md`, *Known red*, before deleting or restoring anything |
| a code mod does nothing: Auto Time-on-Target's planner (Left Alt+G) does not open | Anchor Chain's preloader is not installed; subscribing is not enough. See below |

### Code mods do not load (Auto Time-on-Target)

Sourced from the Anchor Chain docs and the Auto Time-on-Target README. Game
closed.

1. Download `ACPreloader.zip` from the latest release at
   <https://github.com/SeaPower-Modders/AnchorChain/releases>.
2. Copy the contents of the folder in it that holds `winhttp.dll` into the
   Sea Power folder, beside `Sea Power.exe` (this needs admin rights). The
   Explorer route is equally good: Extract All, open the folder holding
   `winhttp.dll`, and copy its contents beside `Sea Power.exe`, leaving out
   any `changelog.txt` (the game has its own). Or save the
   zip into the Sea Power folder and paste this into PowerShell run as
   administrator (change `$g` if Steam lives elsewhere):

   ```powershell
   & {
   $ErrorActionPreference = 'Stop'
   $g   = 'C:\Program Files (x86)\Steam\steamapps\common\Sea Power'
   $zip = Join-Path $g 'ACPreloader.zip'
   if (-not (Test-Path -LiteralPath (Join-Path $g 'Sea Power.exe'))) { throw "Sea Power.exe not found in $g - stopping" }
   if (-not (Test-Path -LiteralPath $zip)) { throw "ACPreloader.zip not found in $g - stopping" }
   $tmp = Join-Path $env:TEMP ('ACPreloader-' + [guid]::NewGuid().ToString('N'))
   Expand-Archive -LiteralPath $zip -DestinationPath $tmp
   $hits = @(Get-ChildItem -LiteralPath $tmp -Recurse -Force -Filter winhttp.dll)
   if ($hits.Count -ne 1) { $hits.FullName; throw "Expected one winhttp.dll in the zip, found $($hits.Count) - stopping" }
   $src = $hits[0].DirectoryName
   foreach ($n in 'doorstop_config.ini', 'BepInEx') { if (-not (Test-Path -LiteralPath (Join-Path $src $n))) { throw "$n is not next to winhttp.dll in the zip - stopping" } }
   $items = @(Get-ChildItem -LiteralPath $src -Force | Where-Object Name -ne 'changelog.txt')
   $clash = @($items | Where-Object { Test-Path -LiteralPath (Join-Path $g $_.Name) })
   if ($clash.Count) { $clash.Name; throw 'These are already in the game folder - stopping so nothing is overwritten' }
   'Copying: ' + ($items.Name -join ', ')
   $items | Copy-Item -Destination $g -Recurse -Force
   foreach ($n in 'winhttp.dll', 'doorstop_config.ini', 'BepInEx') { '{0}: {1}' -f $n, (Test-Path -LiteralPath (Join-Path $g $n)) }
   }
   ```

   It checks every path before it copies anything and stops rather than
   overwrite. If the prompt still shows `>>` after pasting, press Enter once
   more.
3. Confirm `winhttp.dll`, `doorstop_config.ini` and `BepInEx\` are beside
   `Sea Power.exe`.
4. Enable Anchor Chain and Auto Time-on-Target in the Mods menu, exit the
   game fully and start it again.
5. `BepInEx\LogOutput.log` should have a line `Auto Time-on-Target v...
   loaded`. `BepInEx\config\com.seapowermods.autotot.cfg` holds `Enabled`,
   `ShowIndicator` and `PanelKey`: check it is enabled and which key opens
   the panel.
6. Press Left Alt+G inside a running mission.

One BepInEx only: the multiplayer launcher installs its own. If `BepInEx` is
already in the game folder, do not copy a second over it (the script above
stops there).
