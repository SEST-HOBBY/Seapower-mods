# Aligning the gaming PC with this branch — and with the other sessions

This is the procedure for bringing a Sea Power install up to a build that
carries **both campaigns** (Southern Watch and Southern Reach) together with
every fix the other sessions have pushed to the deploy branch. It replaces
the counts in `../southern-watch/install-alignment.md`; the checks and the
failure story there still hold and are not repeated.

Two facts shape it:

- **The PC deploys from one branch**, the one `data\deploy-branch.txt` names:
  `sest-dev/loving-bell-3cnvvw`. `sync-sest.ps1` refuses to run from any
  other branch, on purpose — the last time it ran on the wrong one it reported
  `IN LINE` against a build with none of the campaign in it.
- **Sessions work on their own branches.** This session's work is on
  `claude/campaign-missions-lore-td653z`. That branch already contains the
  deploy branch's latest commit (the two were merged here, the three
  conflicts resolved and every pack rebuilt from scratch on the result), so
  bringing it into the deploy branch is a fast-forward: nothing to resolve.

Close Sea Power before any of it. It rewrites `usersettings.ini` on exit and
throws away a load-order change made while it is running.

## Already aligned once? The short version for later rounds

After the first alignment both `sest-dev/loving-bell-3cnvvw` and
`feature/northern-front-iii-export` sat on `9715f990` (the merge of pull
request #13). Everything this session has pushed since builds straight on
that commit, so a later round is the same fast-forward and one sync:

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
its airway, so it stops circling. The two campaigns are rebuilt in the repo
and need no flag. If `--ff-only` refuses, stop and report it, as in step 2.

The round after the first alignment brought: New Zealand flags (the game's
key is `NewZealand`), airliners that fly their airway in Southern Reach and in
the loose missions, both campaigns' in-game descriptions without the SAR
instructions or fiction tags, rewritten opening pages, a reformatted deck
log, and a proofread of every briefing, card and story page in both
campaigns. The installed file count is still 691.

---

## 0 — where things stand (read this first)

| Branch | What it is | State |
|---|---|---|
| `sest-dev/loving-bell-3cnvvw` | the deploy branch the PC tracks | 56 commits ahead of the repo's default branch; carries every other session's merged work: the helicopter sections, the RAN Seahawk squadron, the ESSM fix, the Banda vignettes, the airliner routes |
| `claude/campaign-missions-lore-td653z` | this session: Southern Reach, the multi-campaign builder, the coastline proof, the RNZAF bases | contains the deploy branch's head; every pack rebuilt from scratch on the merged tree; the four gates pass |
| `feature/northern-front-iii-export` | the repo's default branch on GitHub | behind the deploy branch by 56 commits and contains no campaign; do not deploy from it |
| the other `sest-dev/*`, `fix/*`, `feature/*`, `chore/*` branches | earlier sessions | see §5: surveyed, none needed for this install |

So "aligned to this session and the other sessions" means: the deploy branch
fast-forwarded to this session's branch, then the normal sync.

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
`feature/northern-front-iii-export`, which is 56 commits behind the deploy
branch and has no campaign in it. Either:

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
Test-Path integration\dist\SEST_Integration\campaigns\sest-southern-reach\campaign.ini   # True
```

The last line is the one that says the merge brought the second campaign.
`False` means step 2 did not take.

## 3 — let the build check itself (optional on the PC, done here)

The committed packs are the builders' own output, rebuilt from scratch on the
merged tree in this session with a clean `git status` afterwards, and the four
gates were run on that tree:

```
python tools\build_all.py --from-scratch      # 17 packs, clean git status after
python tools\check_campaign_coverage.py       # both campaigns, 1394 placed references, 159/159 mods
python tools\check_load_order.py
python tools\check_dependencies.py
python tools\preflight.py "Tasman Shield 09 - The Southern Convoy"
```

Running them again on the PC proves the PC's Python sees the same tree; it
does not change what gets installed. Skip it if you are short of time; do not
skip step 2's checks.

## 4 — install and order, one command

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1
```

What to read in its output:

| Line | Means | If it is wrong |
|---|---|---|
| `IN LINE: all N installed files match this commit (hash)` | the deployed bytes equal the commit | the hash must be step 2's; a different one means the pull did not take. **N is 690** for this build — the pack now carries two campaigns (see below) |
| `1 of 1` installed | the consolidated pack copied | `canonical pack not installed` means the copy failed; nothing below matters |
| `dropped stale workshop entry` | a subscription the repo has not catalogued | none expected. An id it names is a new subscription: export it (`export-mod-configs.ps1`) and push, as the Southern Watch procedure describes |
| `purged SEST_…` | an old per-pack folder removed | only on a machine that still had the per-pack layout |

Why the count changed from Southern Watch's 388: the pack now ships
`campaigns\sest-southern-reach\` (25 missions with their briefing folders and
charts, 66 pieces of art, `campaign.ini`, roster, commander settings and a
`REQUIRED-MODS.txt`), the browser copies under `missions\Southern Reach\` and
`missions\Tasman Shield\`, a `REQUIRED-MODS.txt` for Southern Watch's own
folder, and the two RNZAF base files in the land units.

## 5 — confirm both campaigns arrived

```powershell
$sa = "<…>\Sea Power_Data\StreamingAssets\SEST_Integration"
Get-ChildItem "$sa\campaigns" -Directory | Select-Object Name        # sest-southern-reach, sest-southern-watch
(Get-ChildItem "$sa\campaigns\sest-southern-reach\art\*.png").Count   # 66
(Get-ChildItem "$sa\campaigns\sest-southern-reach\missions\*.ini").Count   # 25
Test-Path "$sa\land_units\airbase_rnzaf_ohakea.ini"                   # True
Get-ChildItem "$sa\missions" -Directory | Select-Object Name          # …, Southern Reach, Tasman Shield, Southern Watch, …
```

Then in game, in this order:

1. **Mod Manager** — `SEST Integration Pack` at the top, enabled; its
   description now ends "Southern Watch - Southern Reach".
2. **Campaign list** — two entries: `Southern Watch (Royal Australian Navy)`
   and `Southern Reach - Tasman Shield (Royal Australian Navy)`, 44 entries
   in the second, a dark chart 29–66°S behind it.
3. **Mission browser** — folders `Southern Reach` (12) and `Tasman Shield`
   (13) beside the Southern Watch ones. If the campaign list shows one
   campaign but the browser has both folders, the Mod Manager is not reading
   the second `campaigns\` folder; that difference is the diagnosis.

## 6 — the other sessions' branches

Seven other branches on GitHub are not in the deploy branch. They were
surveyed one by one for what they hold that the deploy branch lacks, in
substance rather than in files. The short answer is that **none of them is
needed for this install**; the long answer is in the table below and in the
build notes. Nothing was merged from them; if one of them holds work you want
back, say which and it becomes a session's job, not a PC step.

| Branch | Last commit | What it holds that the deploy branch lacks | Verdict |
|---|---|---|---|
| `sest-dev/peaceful-gauss-e1zvfq` | 23 Sep | a two-item Workshop staging script and guide; a one-line fix to the catalog generator | Everything else on it was ported to the deploy branch by its own session (briefing maps, Viper Zero, the three new mods). The generator fix is **applied in this merge**. The two-item Workshop design was replaced by the one-pack design; leave it |
| `sest-dev/kind-faraday-ctr5h0` (contains `beautiful-cerf-i7fqei`, `fix/banda-front-lean-finalize` and `affectionate-volta-3xqkx6`) | 20 Sep | the SEST Aegis BMD pack (its SM-3 seeker and handover values since ported into SEST Collection Fixes; its floor, range and loft edits superseded by the deploy branch's own SM-3 work) and the SEST Intercept Model pack (since ported, with the Korean K-SAM II added to its fixes); the Banda Front Lean and Living Seas missions, Indo-Pacific Land Assets and a land-defence site builder (all three since ported); an editor-crash sweep over 31 older missions; its own AIM-260 seating | **Not merged, and not safe to merge whole.** It forked on 31 August. Its mod list is older than the PC's (it lacks the Anzac, Automatic SAR, the Korean Navy and the MV-22B that the deploy branch catalogues), it withheld one of its own changes (the Nimitz CVN-70 variant) as the suspect for a stuck load, and the SM-3 repair it carries exists on the deploy branch in another form. What is not marked ported is real work that needs a porting session of its own |
| `feature/ras-integration`, `chore/workshop-inventory-20260916`, `…-notes` | 14–16 Sep | the SEST Replenishment (since ported and rebuilt against today's export, with its launcher fix and HMAS Supply's supply system applied in the sibling packs and its metering tags in SEST Collection Fixes and SEST Intercept Model), A-10C+ (since ported, rebuilt against today's export, with its infrared-head and squadron repairs applied to the standard A-10C in SEST Allied Fixes and the new unit flying in D8), YF-23 MALICE and Zumwalt CPS packs; an AIM-424 respec; a 137-mod inventory snapshot | **Not merged.** Forked on 26 August, the oldest base of all; each pack would have to be rebuilt against today's export before it could load correctly. What is not marked ported needs a porting session of its own |
| `feature/northern-front-iii-export`, `sest-dev/quirky-noether-fq5i98`, `claude/repo-cleanup-interoperability-hleer5` | ≤ 20 Sep | nothing | already inside the deploy branch |

The practical meaning: after this procedure the PC has everything any session
put on the deploy branch, plus this session's campaign. What it will **not**
have is the work stranded on the two older lines above. Replenishment has
since been ported: SEST Replenishment At Sea arrives through the deploy
branch like everything else, inside `SEST_Integration`. So have the Banda
Front missions: Lean v2, Living Seas and the
rest of their line are in `integration/missions/` and install like any other
mission (see its README).

## 7 — then play

Southern Watch's card (`../southern-watch/test-card.md`) has new rows from
the other sessions (side operations carrying losses, helicopters flying as
helicopters, red aircraft that were briefed to come). Southern Reach's
(`test-card.md`) starts where this document stops: the coastline first,
because that is the claim this build makes that no earlier one did.

---

## When something is wrong

| Symptom | The command that answers it |
|---|---|
| `git merge --ff-only` refuses | `git log --oneline origin/sest-dev/loving-bell-3cnvvw -5` — whatever is there and not on this session's branch was pushed after the merge here; report it |
| sync refuses on the branch guard | you are not on `sest-dev/loving-bell-3cnvvw`; go back to step 1 rather than passing `-AnyBranch` |
| the second campaign is missing in game but present on disk | `Get-ChildItem "$sa\campaigns\sest-southern-reach"` shows the files; the browser copies are your route in, and the difference is the report |
| a Southern Reach unit is missing in a mission | the unit names its mod: `campaigns\sest-southern-reach\REQUIRED-MODS.txt` lists the 26 hard-required Workshop mods for this campaign; `.\tools\show-load-order.ps1` shows which are enabled |
| a ship is ashore or a route crosses land | the coastline extract disagrees with the game there; note the mission and the hull, that is the first row of the test card |
