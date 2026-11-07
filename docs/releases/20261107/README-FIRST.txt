SEST WORKSHOP UPDATE CANDIDATE — 7 NOVEMBER 2026

Workshop item: 3812461539 (update this item; do not create a second item)
Release branch: release/workshop-20261107
Base: merged PR #56, 72129cb45d3ec49d145ab323f16111089d868edb
Latest author configuration capture integrated: 3 November 2026.
Status: build checked; the final PC gameplay checks below remain.

PREPARE THE UPLOAD

This delivery contains a local Git bundle. The release branch has not been
pushed to GitHub. Extract the complete toolkit ZIP into a fresh folder.
The bundle uses merged PR #56 as its prerequisite; fetch that public base,
then import the prepared release locally. This does not change Steam's
selected game branch or your installed beta repair.

Close Sea Power. In PowerShell:

  cd C:\Users\rolyl\Seapower-mods
  git status --short

Keep any local edits before changing branch. With a clean tree, replace
C:\PATH\TO\TOOLKIT below with the extracted toolkit folder:

  git fetch origin sest-dev/jolly-ride-rptj4t
  git bundle verify "C:\PATH\TO\TOOLKIT\SEST-Workshop-20261107.bundle"
  git fetch "C:\PATH\TO\TOOLKIT\SEST-Workshop-20261107.bundle" release/workshop-20261107
  git switch -c release/workshop-20261107 FETCH_HEAD
  powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1 -CheckUpdates
  powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\prepare-workshop-upload.ps1

Stop if a git command fails. If that branch already exists, switch to it
and use git merge --ff-only FETCH_HEAD instead of creating it again.
Read the CheckUpdates report: a changed author configuration needs a new
capture before upload; its successful script exit alone does not mean
there was no drift. The preparation script verifies all canonical files,
then prints a fresh Downloads upload folder. Only the inner SEST_Integration
folder is uploaded. It does not alter the installed game, current beta
repair, load order, Steam branch, subscriptions or saves. No rebuild is
needed on the PC.

WHAT CHANGED

- The merged November configuration refresh, campaign dependency fixes,
  pricing corrections and SETUP fixes from PR #56 are retained.
- The beta tactical map's 32 missing settings and Redback helicopter
  night-vision declarations are included; stable CIWS tuning is retained.
- Stable UI Follow-up 1.4.5 supports the captured Pop-Out Windows 1.1.3
  through an exact-hash and reflected-contract check. Runtime 1.5.0 is
  unchanged. Unknown author builds leave the affected bridge inactive.
- The upload manifest prevents accidental publication of the installed
  beta test DLLs in place of the canonical stable payload.

FINAL GAMEPLAY CHECKS

Stable Build 261021: run SETUP; check the F11 current/campaign/last-game
cost windows and AGR-30 quantities, debrief, preparation into a second
mission, Contacts and formation pop-out/return, and compass on the unit
camera. The 1.4.5 log must include:
  stable Pop-Out Windows 1.1.3 bridge compatibility installed
  native window bridge attached to Pop-Out Windows 1.1.3 (stable companion)
Any inactive bridge or rendering failure needs its log captured before
the new pop-out change is published. The actual 1.1.3 DLL was not available
to the build environment, so this installed-version check is still needed.

Beta Build 261026: remain on beta for your R6 test. Use the separate
SEST-Beta-Repair-R6-20261107.zip; run Repair-Beta-Startup.cmd, play the
checks in its README-FIRST.txt, then Capture-Repair-Results.cmd.
Do not copy its payload/ DLLs into this upload folder. R6 has recorded
managed/fixture checks, not a completed gameplay check. It is not part of
the ordinary Workshop installation. Clipped tabs and the Global Hawk
comparison remain unresolved; do not advertise either as fixed.

Before upload, take a new Workshop capture if Steam updated an author mod
after 3 November. Use the existing capture-all-mod-updates.ps1 workflow;
do not assume that a newer Pop-Out DLL will match the inspected pin.

STEAM REQUIREMENTS AND UPLOAD

The load order contains 204 entries: SEST plus 203 Workshop dependencies.
Make the item Required Items match data/load-order.tokens.txt and the
collection contain those 203 dependencies plus SEST. The live collection
checked on 7 November contains Contact Log, Topographic Map and Pop-Out
Windows, but no B-21 entry. Add B-21 Raider 3821992229 and check all four
are also Required Items before Submit:
  Contact Log       3819427362
  Topographic Map   3826122523
  Pop-Out Windows   3826396311
  B-21 Raider       3821992229

Item: https://steamcommunity.com/sharedfiles/filedetails/?id=3812461539
Collection: https://steamcommunity.com/sharedfiles/filedetails/?id=3812390790

In Sea Power: Mod Manager > Create Mod > Update Existing > item
3812461539 > Pick Folder > the verified SEST_Integration folder > Submit.
Keep Public visibility and the dependency list. Paste STEAM-CHANGE-NOTE.txt
after the gameplay checks pass. Confirm m_eResult: k_EResultOK in Player.log
and verify the item timestamp, nonzero size and Required Items afterwards.

Nothing in this package publishes to Steam automatically.
