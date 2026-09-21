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
python tools\preflight.py "Southern Watch 01 - White Water"
```

`preflight.py` with no argument checks whatever `data\active-mission.txt`
names, which is a Northern Front III mission — useful, but not this campaign.
Name a mission to check this one. `check_campaign_coverage.py` above already
walks all 22 Southern Watch missions, so the named preflight is a second
opinion rather than the only coverage.

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

The file count should now be **257**, not 122. It changed in this branch: the
campaign gained 24 generated PNGs plus `REQUIRED-MODS.txt` and
`LOAD-ORDER.txt`, and lost the fourteen `_info.ini` files it used to write into
briefing folders under `campaigns/`, where the vanilla campaigns have none.

If `sync-sest.ps1` refuses because of the branch guard, it is doing its job —
go back to step 1 rather than reaching for `-AnyBranch`.

## 4 — confirm the campaign's own files arrived

```powershell
$sa = "<…>\Sea Power_Data\StreamingAssets\SEST_Integration"
Get-ChildItem "$sa\campaigns\sest-southern-watch\art\*.png" | Measure-Object   # 24
Test-Path "$sa\campaigns\sest-southern-watch\art\00_campaign_background.png"   # True
Test-Path "$sa\REQUIRED-MODS.txt"                                              # True
Test-Path "$sa\CREDITS.txt"                                                    # True
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

I had this backwards in the first version of this document, and it matters.
`set-mod-order.ps1` does not append an unknown mod at the bottom — that is
only what it does with a *non-numeric* token. A **workshop id** it does not
recognise is **removed** from `[LoadOrder]`, with a warning, because an
unsubscribed leftover left enabled is what kept the phantom KJ-500 alive as
entry 144. The script's own help text said "appended … rather than dropped"
for all three cases; it says what it actually does now, and so does
`fix-load-order.ps1`'s warning.

So each time you run the sync, those two are dropped, and the game re-adds
them on the next launch at a position it chooses. Nothing breaks — the
campaign names no unit from either, and Automatic SAR is a behaviour mod that
applies wherever it sits — but neither has a stable position, and you will see
a `dropped stale workshop entry` warning naming both on every run. That
warning is expected and is not a problem with the install.

To give them fixed positions they have to be catalogued, which means an
export from your machine:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1
powershell -ExecutionPolicy Bypass -File .\tools\capture-context.ps1 -IncludeSaves
```

Push the result and the catalog, the canonical order and the coverage report
are all regenerated from it. Until then the drop-and-re-add cycle is the
expected behaviour, not a fault.

## 6 — then play the card

`docs/campaigns/southern-watch/test-card.md` is the play test, ordered
riskiest-claim-first. It starts where this document stops.

---

## When something is wrong

| Symptom | The command that answers it |
|---|---|
| campaign absent from the list | `Get-ChildItem "$sa\campaigns\sest-southern-watch"` — if the folder is missing the install did not take; if it is there, the Mod Manager is not reading mod-supplied campaigns and the browser copies are your route in |
| a mission loads with units missing | the missing unit names its mod — check that mod is subscribed and enabled: `.\tools\show-load-order.ps1` |
| a texture or model fails | the pack ships 24 PNGs and they are all campaign art — the mission cards, the story sheets and the backdrop. Any unit texture or model belongs to the donor mod, so that failure names the mod to check, not this pack |
| the order looks wrong | `.\tools\show-load-order.ps1` prints live order beside canonical; `.\tools\fix-load-order.ps1` reconciles |
| you are not sure what the game actually has | `.\tools\capture-context.ps1 -IncludeSaves` writes a full snapshot into `data\install-snapshot` — logs, live load order, subscriptions, build number and campaign saves |

## What this cannot tell you

That the campaign *plays* well. Every gate in step 2 checks that a file
resolves, not that a mission is winnable, fair, or paced — no mission in this
campaign has been played to completion. The test card is where that starts.
