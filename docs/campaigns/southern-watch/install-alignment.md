# Aligning a Sea Power install with this branch

The procedure below exists because of one specific failure. On the last run
the install reported

```
IN LINE: all 122 installed files match this commit (d2547151).
```

which looks like success and is not. `d2547151` is on
`feature/northern-front-iii-export` and contains **zero** Southern Watch
files. The install was internally consistent with the wrong build. "IN LINE"
answers *do the deployed bytes match the repo?* — it does not answer *is the
repo on the branch you meant?*

So step 1 is the branch, and every step afterwards has a check that would
catch the failure it is capable of producing.

Close Sea Power first. It rewrites `usersettings.ini` when it exits, so any
load-order change made while it is running is thrown away silently.

---

## 1 — point the repo at this branch

```powershell
cd <repo>
git fetch origin sest-dev/loving-bell-3cnvvw
git checkout sest-dev/loving-bell-3cnvvw
git pull origin sest-dev/loving-bell-3cnvvw
```

Check, and do not skip this:

```powershell
git branch --show-current          # sest-dev/loving-bell-3cnvvw
git log --oneline -1               # note the short hash
Get-Content data\deploy-branch.txt # sest-dev/loving-bell-3cnvvw
```

`data\deploy-branch.txt` is what `sync-sest.ps1` refuses to run against a
mismatch on. It used to name `feature/northern-front-iii-export`; it now names
this branch, which is why the guard did not fire last time. If those three do
not agree, stop — nothing further is meaningful.

## 2 — build, then let the build check itself

```powershell
python tools\build_all.py --from-scratch
git status --short
```

`git status` must be **clean**. That is the regression test: the committed
packs are the builders' own output, so a diff means either `mods-source` or a
builder changed since the commit and what you are about to install is not what
was reviewed. A dirty tree here is a stop, not a warning.

Then the four gates, which check different things and all have to pass:

```powershell
python tools\check_campaign_coverage.py   # 510 placed references, all resolve
python tools\check_load_order.py          # every SEST pack outranks what it overrides
python tools\check_dependencies.py        # every pack's upstream mods present
python tools\preflight.py                 # units, air groups, loadouts, pylon stores
```

## 3 — install and order, one command

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1
```

This pulls, copies `integration\dist\SEST_Integration` into StreamingAssets,
rewrites `[LoadOrder]` from `data\load-order.tokens.txt` inserting the pack
enabled and in position, and then hashes every deployed file back against the
build.

What to read in its output:

| Line | Means | If it is wrong |
|---|---|---|
| the commit named in `IN LINE` | what you actually deployed | must equal step 1's short hash — if it does not, the pull did not take |
| `1 of 1` installed | the consolidated pack copied | `canonical pack not installed` means the copy failed; nothing below matters |
| `purged SEST_…` | an old per-pack folder removed | expected once, after the switch to the consolidated pack |
| `appended (not canonical)` | a mod you subscribed to that the repo has never seen | expected for **Automatic SAR** and the **Euromod South Korean Navy** — see step 5 |

The file count should now be **278**, not 122. It changed in this branch: the
campaign gained 32 generated PNGs plus `REQUIRED-MODS.txt` and
`LOAD-ORDER.txt`.

If `sync-sest.ps1` refuses because of the branch guard, it is doing its job —
go back to step 1 rather than reaching for `-AnyBranch`.

## 4 — confirm the campaign's own files arrived

```powershell
$sa = "<…>\Sea Power_Data\StreamingAssets\SEST_Integration"
Get-ChildItem "$sa\campaigns\sest-southern-watch\art\*.png" | Measure-Object   # 32
Test-Path "$sa\campaigns\sest-southern-watch\art\00_campaign_background.png"   # True
Test-Path "$sa\REQUIRED-MODS.txt"                                              # True
```

The three things to look at in game, in this order, because each one tells you
something the next cannot:

1. **Mod Manager** — `SEST Integration Pack` at the top of the list, enabled.
   Its description should read like a mod description, not like a repo note.
   If it still says "Built by the Seapower-mods repo", you are on the old build.
2. **Campaign list** — `Southern Watch (Royal Australian Navy)`, 23 entries,
   with the chart backdrop behind it and a mission card on each tile.
3. **Mission browser** — `Southern Watch 01 - White Water` under
   `Southern Watch`. The missions ship twice on purpose, so if the campaign
   layer does not surface but the browser entries do, that difference is
   itself the diagnosis.

## 5 — the two mods the repo has not catalogued

**Automatic SAR** and the **Euromod South Korean Navy** were subscribed after
the last catalog export, so they are not in `data\load-order.tokens.txt`.
`set-mod-order.ps1` never invents a position for a mod it does not know: it
appends them at the **bottom** of the order, below everything, and warns.

That is safe but not free. Bottom of the list means *lowest* priority, so any
file either of them shares with a mod above it is simply not read. Nothing in
Southern Watch names a unit from either — the campaign is built and checked
against the 147-entry canonical order, and both are additions to it, not
substitutions in it. Automatic SAR in particular is a behaviour mod: it will
apply, and it costs nothing to leave where it is.

If you want them catalogued and placed deliberately rather than appended,
re-run the export and say so:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1
powershell -ExecutionPolicy Bypass -File .\tools\capture-context.ps1 -IncludeSaves
```

and push the result — the catalog, the order and the coverage report are all
regenerated from that export.

## 6 — then play the card

`docs/campaigns/southern-watch/test-card.md` is the play test, ordered
riskiest-claim-first. It starts where this document stops.

---

## When something is wrong

| Symptom | The command that answers it |
|---|---|
| campaign absent from the list | `Get-ChildItem "$sa\campaigns\sest-southern-watch"` — if the folder is missing the install did not take; if it is there, the Mod Manager is not reading mod-supplied campaigns and the browser copies are your route in |
| a mission loads with units missing | the missing unit names its mod — check that mod is subscribed and enabled: `.\tools\show-load-order.ps1` |
| a texture or model fails | that is the donor mod's asset, not this pack's — the SEST packs ship `.ini` files only, no models, no textures |
| the order looks wrong | `.\tools\show-load-order.ps1` prints live order beside canonical; `.\tools\fix-load-order.ps1` reconciles |
| you are not sure what the game actually has | `.\tools\capture-context.ps1 -IncludeSaves` writes a full snapshot into `data\install-snapshot` — logs, live load order, subscriptions, build number and campaign saves |

## What this cannot tell you

That the campaign *plays* well. Every gate in step 2 checks that a file
resolves, not that a mission is winnable, fair, or paced — no mission in this
campaign has been played to completion. The test card is where that starts.
