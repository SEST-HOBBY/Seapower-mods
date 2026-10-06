# Publishing the SEST Integration Pack to the Steam Workshop

Open this before every upload. The pack is live and Public, so an update that
goes up broken reaches every subscriber at once, and the comments arrive
before the patch does.

## What is on the Workshop

- **The item.** *SEST Integration Pack - Modernised Campaigns*, Workshop id
  **3812461539**, Public. It is the `SEST_Integration` folder: one Mod Manager
  entry (*SEST Integration Pack*) carrying the 19 SEST fix packs and all three
  campaigns, Southern Watch, Southern Reach / Tasman Shield and Red Line. It
  carries the 4 Oct 2026 build (`d4fd1668` and `fa692245`), with SETUP in the
  pack. Every upload is an update to this item; there is no second item.
- **The collection.** *SEST - Modernised Campaign Collection*, Workshop id
  **3812390790**. Published with 149 items: the 148 Workshop mods the load
  order then held, plus the pack. This is how a subscriber gets the
  dependencies. Its banner reads "149 Workshop items, 3 campaigns, 19 fix
  packs". **Behind the repo since the October 2026 additions:** the load
  order now holds 190 Workshop mods, so the collection needs the 42 new ones
  (and its banner and counts redone) before the next upload of the pack -
  SETUP refuses to run while any mod in the pack's LOAD-ORDER.txt is missing.
- **Required Items: the load order's Workshop mods.** Set in October 2026, so
  that pressing Subscribe on the item offers every mod the pack needs in one
  click (about 24 GB). They must hold the same Workshop mods as the
  collection. The section after next says what that costs and how to keep
  them in step.
- **The page text.** The pack description, its change log, the collection
  description and a pinned "Read first" discussion were rewritten for the
  4 Oct update (SETUP's install steps, the 1.5x clock, Red Line's November
  2028 to February 2029 dates), and the collection banner and pack images
  were redone.

The counts come from the repo: `data/load-order.tokens.txt` has 191
non-comment entries, 190 Workshop ids and `SEST_Integration` (149 and 148
when the collection was published). The "135 mods"
and "133-mod" figures in older notes are out of date.

## What the game actually provides

Everything below about the Mod Manager is read out of the game's own UI
strings in `mods-source/_vanilla/original/language_en/ui.ini`, sections
`[ModMenu]` and `[MainMenu]`. The upload has since been run (4-5 Oct 2026),
to item 3812461539. The path that worked is Create Mod → Update Existing →
Pick Folder `StreamingAssets\SEST_Integration` → Submit, confirmed by
`m_eResult: k_EResultOK` in Player.log. *Update Existing*, *Pick Folder* and
the preview image picker are not in these strings; they are known from that
use.

The Mod Manager publishes directly — the game links Steamworks UGC, which the
literal Steamworks enum names in `ui.ini` prove:

```
[ERemoteStoragePublishedFileVisibility]
k_ERemoteStoragePublishedFileVisibilityPublic=Public
k_ERemoteStoragePublishedFileVisibilityFriendsOnly=Friends Only
k_ERemoteStoragePublishedFileVisibilityPrivate=Private
k_ERemoteStoragePublishedFileVisibilityUnlisted=Unlisted
```

The publish form's fields, from `[MainMenu]`:

| String | Field |
|---|---|
| `CreateMod=Create Mod` | starts the flow |
| `ModName=Mod Name` | title |
| `ModDescription=Mod Description` | the page body |
| `ChangeLog=Change Log` | per-update notes |
| `Manual=Manual` | a longer document |
| `ModCategory=Tags` | Workshop tags |
| `ModVisibility=Visibility` | the four values above |
| `SubmitMod=Submit Mod` | uploads |
| `ModDependencies=Required Workshop IDs` | the item's Required Items; for this pack, the load order's Workshop mods (see below) |

`[ModMenu]` also has `OpenFolder`, which is how you confirm *which* folder is
about to be published, and the tag dimensions the game sorts by:
`TimeLocation` (Timeframe and Location), `ModType`, `ObjectType`, `Alignment`.

## Dependencies: Required Items subscribe, SETUP orders

This is the important part, and it is why a pack that depends on 190 Workshop
mods is a publishable thing at all — and why the dependency list alone cannot
make it work.

`[ModMenu]` carries a `Sync` button and this sequence:

```
SyncingMods=Syncing mod dependencies from Steam workshop
SyncingIteration=Syncing dependencies, iteration:
DownloadingDependencies=Downloading ${num} dependencies
SubscribedCount=Subscribed to ${subscribed} new dependencies.
EnabledCount=Enabled ${enabled} installed dependencies.
```

Read that carefully. The game asks **Steam** for a mod's dependencies,
**subscribes** the player to the ones they do not have, **enables** the ones
they do, and **iterates** — so a dependency's own dependencies come too. It is
localised into all nine shipped languages, which is not what a dead WIP string
looks like.

Nothing in any mod's `_info.ini` declares a dependency — across this
collection the only keys are `Name`, `Description` and `[Compatibility]`
version bounds. So the dependency list does not live in the mod. It lives on
the **Steam Workshop item**, in Steam's own *Required Items* field (the Create
Mod form's *Required Workshop IDs*), and Sync walks it. For this pack it is
kept in two places that must name the same mods: the item's *Required Items*,
set in October 2026 to the Workshop mods of `data/load-order.tokens.txt`, so
that Subscribe on the item offers them all in one click, and the collection
*SEST - Modernised Campaign Collection* (3812390790: those mods plus the
pack), for anyone who starts from the collection.

The cost is in the same section of `ui.ini`, the check the Mod Manager runs
on that list:

```
DependencyIssuesHeader=This mod has dependency issues. Click for fixes.
DependencyMissing=Not installed: Workshop item ${mod}
DependencyOutOfOrder=Must load above this mod: ${mod}
FixDependencyOrder=Move dependencies above this mod
DownloadDependencies=Download missing dependencies (Sync)
```

A required item must load above the mod that requires it. This pack is
whole-file replacements of the Workshop mods' own files, and it works only
from the top of the order, above every Workshop mod — the one rule in its
`LOAD-ORDER.txt`. So by the rule those strings describe, the pack is always
out of order against its own Required Items: the Mod Manager may flag it
("This mod has dependency issues. Click for fixes.") and offer *Move
dependencies above this mod*, which would move every Workshop mod above the
pack and undo every fix in it. Nothing reverts the order by itself: SETUP
writes it into `usersettings.ini` and it holds until something changes it,
and running SETUP again puts it back. Sync, going by its strings, only
subscribes and enables; it does not reorder.

**Whether the prompt appears has not been seen.** The strings are in the
0.8.4 public release (2 Oct 2026), so it is not a beta-branch feature, but a
string in `ui.ini` does not prove the game shows it. The publisher has never
seen it, and could not on the gaming PC: `sync-sest.ps1` installs the pack as
a local folder, which has no Workshop item for the game to ask Steam about.
No subscriber has reported it. To settle it: with the game closed, move the
local `SEST_Integration` out of `StreamingAssets`, make sure the Workshop
copy of 3812461539 is downloaded, run SETUP from that copy's folder, then
start the game and look at the pack's row in the Mod Manager. Put the local
folder back afterwards (`sync-sest.ps1` does). Record the result here and
against test card H.16.

**Until then:** the item description tells subscribers to answer no if the
Mod Manager offers to move dependencies above the pack, and SETUP run again
repairs the order if someone said yes. Subscribers get the mods from the
item's Required Items or from the collection, then run `SETUP - double-click
me.cmd` with the game closed. The first version of this document said to set
every mod as a Required Item and let Sync do the rest; the second said to
leave Required Items empty because of the check above. The October 2026
choice keeps them for the one-click subscribe and leaves the order to
SETUP.

### SETUP, in the pack

The collection subscribes; it does not order, and order decides which copy of
a shared file the game reads. `SETUP - double-click me.cmd` and
`sest-setup.ps1` ship in the pack folder for that. A player opens the folder
(Mod Manager → Open Folder on the pack), quits the game and double-clicks the
`.cmd`. SETUP checks that every Workshop mod the campaigns were built against
is downloaded and names any that are not, with links; installs the Anchor
Chain preloader if it is missing (a UAC prompt only when neither `winhttp.dll`
nor BepInEx is in the game folder); turns off one mod's debug logging that can
freeze a mission; and writes the Mod Manager order: the pack first, the 180 in
`LOAD-ORDER.txt` order, the player's other mods at the bottom as they were. It
backs up the game's settings first and is safe to run again.

SETUP supersedes the earlier friend zip kit and the standalone
`sest-friend-setup.ps1`. Point people at SETUP, not at those.

### Keeping the collection and Required Items in step with the load order

The collection and the item's Required Items are the dependency list now,
and both are kept by hand. When a Workshop mod enters or leaves
`data/load-order.tokens.txt`:

1. Add it to, or remove it from, the collection 3812390790 and the item's
   Required Items (on the item page, or the Create Mod form's *Required
   Workshop IDs*), so both stay the load order's Workshop mods; the
   collection also holds the pack.
2. The banner's "149 Workshop items, 3 campaigns, 19 fix packs" is then
   stale: redo it. The fix-pack figure goes stale the same way when a SEST
   pack is added or retired; the pack's `_info.ini` *Includes* list names
   them.
3. Check the counts in the collection description, the pack description and
   the pinned "Read first" discussion.

One change of this kind already made: Dassault Rafale (3504168760) left the
collection, and French Air Force (3758943352) supplies the Rafale now. Nothing
on Steam's side will tell you the collection has fallen behind; the first sign
would be a subscriber's SETUP naming a mod that is not downloaded.

### `required-mods-urls.txt` is a reference list

`required-mods-urls.txt` (one per campaign, under `docs/campaigns/<campaign>/`)
is a reference list, generated by `build_pack.py` from the same coverage rows
the pack's own `REQUIRED-MODS.txt` uses: the Workshop mods that campaign's
missions reach, and any a reached mod says it needs, in canonical load order.
It is not the list for the item's
Required Items, which hold every Workshop mod in the load order, more than
any one campaign reaches. The authoritative dependency set is
`data/load-order.tokens.txt`, mirrored by the collection 3812390790 and the
item's Required Items.

The three lists together name 141 distinct mods. The collection's other seven
are the mods `REQUIRED-MODS.txt` lists as "also enabled while this was built":
no mission names them, but they stay in the order because removing one
changes which file wins.

### SeaLifter: still open

One dependency is in neither the load order nor the collection, and has no id
in this repo: **SeaLifter**, which B-2 Spirit declares as its own requirement.
`required-mods-urls.txt` lists it under NOT IN THE COLLECTION, and
`REQUIRED-MODS.txt` in the pack tells players to find it on the
Workshop and that it needs a manual install: subscribing alone is not enough.
It is not among the Required Items either, having no id here. Settling it
means finding its id, or dropping the B-2 from the campaigns; if it joins
the load order, the collection, its count and banner, and the Required Items
change with it. Until then
it is the one dependency most likely to break a subscriber's install.

## Before you press Submit

1. **The build is the one you mean.** The PC syncs from the deploy branch
   named in `data\deploy-branch.txt` (`sest-dev/loving-bell-3cnvvw`).
   `git status` is clean and `sync-sest.ps1` reports IN LINE with the commit
   you mean to publish. The folder you are about to upload is build output; if
   the tree is dirty it is not the reviewed build.
2. **What this update changed has been played.** Not "mission one loads": the
   test card rows that cover the change (for the 4 Oct changes, `test-card.md`
   6H, H.15-H.18, which have not yet been reported back), and anything a
   commenter reported against it.
3. **A fresh-install check, when SETUP, the load order or the collection
   changed.** Everything verified on the machine that built it is verified
   where all 190 Workshop mods of the load order happen to be present. The
   check that matters is to subscribe to the collection 3812390790 on a clean
   profile, run SETUP, and see whether the campaigns run. One friend's PC has
   done part of this (see *What has been verified so far*). If a second
   machine or a second Steam account is available, that is the highest-value
   hour before such an update.
4. **The Steam Cloud is under 1,000 files.** See below; this is what stopped
   the first uploads.
5. **The collection matches the load order**, if a mod came or went.
6. **Leave it Public, with its Required Items as they are.** Item 3812461539
   went Public on 4-5 Oct 2026. On an update, do not change visibility. The
   Required Items should still be the load order's Workshop mods; change
   them only when the load order changed (above).

## The upload

Game closed for the build and the sync, game open for the upload.

1. Bring the install IN LINE with the commit you mean to publish. The current
   procedure is `../southern-reach/install-alignment.md`; the loop is

   ```powershell
   git pull origin <branch>                    # the deploy branch in data\deploy-branch.txt
   python tools\build_all.py --from-scratch    # git status must be clean afterwards
   powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1
   ```

   and the sync must end `IN LINE: all N installed files match this commit`
   with that commit's hash. The pack is build output, so the Workshop item and
   the repo cannot drift as long as the install is IN LINE with the commit
   before you upload.
2. Check the Steam Cloud (below): `NEW MISSIONS CLEAN` must not be back under
   `StreamingAssets\user\missions`.
3. Launch Sea Power → **Mod Manager**.
4. Use **Open Folder** on `SEST Integration Pack` and confirm it opens
   `…\Sea Power_Data\StreamingAssets\SEST_Integration`, and that
   `REQUIRED-MODS.txt`, `LOAD-ORDER.txt`, `CREDITS.txt`, `SETUP - double-click
   me.cmd` and `sest-setup.ps1` are sitting in it. That is the folder that
   goes up.
5. **Create Mod** → **Update Existing** (item 3812461539, *SEST Integration
   Pack - Modernised Campaigns*) → **Pick Folder**
   `StreamingAssets\SEST_Integration`. Never publish the pack as a new item.
6. **Mod Name**: keep *SEST Integration Pack - Modernised Campaigns*. **Mod
   Description**: change it only where something it says has changed. The live
   text was rewritten on Steam for the 4 Oct update, and
   `workshop-listing.md` is kept by hand, so compare the two before pasting
   anything from the file.
7. **Preview image**: `StreamingAssets\SEST-preview.jpg` (124 KB). The Create
   Mod image picker only browses StreamingAssets, so the image has to live
   there; it is kept outside `SEST_Integration`, which the sync deletes and
   recopies from the build every time (`install-sest-packs.ps1`), and all of
   which goes up as the pack. The image is not in the repo.
8. **Tags**: the dimensions the game sorts on are Timeframe and Location, Mod
   Type, Object Type and Alignment. The item carries three modern (2028-2029)
   Western Pacific / Australian campaigns; pick the closest available in each,
   and take `Campaign`/`Missions` if a content-type tag exists. On an update,
   check the ones already set still fit.
9. **Visibility**: leave it `Public`. The item is live.
10. **Required Workshop IDs**: change it only when the load order changed.
    Whether submitting an update with this field empty clears the Required
    Items the item page already holds has not been tested, so check them
    after Submit (step 13).
11. **Change Log**: an entry for this update (below).
12. **Submit Mod**.
13. Confirm `m_eResult: k_EResultOK` in `Player.log` (in
    `%USERPROFILE%\AppData\LocalLow\Triassic Games\Sea Power\`, beside
    `usersettings.ini`), then check that the item page shows the new build
    and not 0 B, and that its Required Items are still listed.
    `k_EResultLimitExceeded` means the Steam Cloud is over its cap.
14. If the load order changed, bring the collection, its banner and the
    Required Items into line (above).

### The Steam Cloud's 1,000-file cap

The first uploads failed with `k_EResultLimitExceeded`, and the item showed
0 B. Sea Power's Steam Cloud was at its 1,000-file cap, almost all of it
`StreamingAssets\user\missions\NEW MISSIONS CLEAN` (804 files). That folder was
moved to `%USERPROFILE%\Documents\SeaPower-moved-out-of-cloud`, the cloud is
now about 180 files, and the uploads went through.

The rule that follows: keep Sea Power's Steam Cloud under 1,000 files. Do not
move `NEW MISSIONS CLEAN` back, and do not park large mission folders under
`StreamingAssets\user\missions`. If an upload fails with
`k_EResultLimitExceeded` again, look there first.

## The change log

`ChangeLog` is the per-update field. Write one entry for every update: what
changed, in terms a player would notice, and which report it answers. The
4 Oct rewrite of the change log, the description and the pinned discussion
covered SETUP's install steps, the 1.5x clock and Red Line's November 2028 to
February 2029 dates. When an update changes something the description, the
collection description or the pinned "Read first" discussion says (install
steps, counts, dates, the clock), change them in the same sitting.

## What has been verified so far

- **The upload path.** Once the Steam Cloud was back under its 1,000-file cap,
  the update path above ended `m_eResult: k_EResultOK`, and the item carries
  the 4 Oct build with SETUP in it.
- **A fresh install, in part.** A friend on a fresh PC subscribed to the
  collection and opened the pack folder from the Mod Manager. `SETUP -
  double-click me.cmd` was missing at first, appeared a minute or two after he
  quit the game, and then ran normally. Why it was late is not established:
  the publisher is sure the item showed as updated before he launched, and
  that the game was closed when it updated. His `Steam\logs\workshop_log.txt`
  lines for 3812461539, with his launch and quit times, would settle it. Not
  yet reported from that PC: whether the UAC elevation ran, whether the pack
  sits first with 191 entries, whether the campaigns are listed, and the
  yellow "Behind schedule" card in The Quiet Passenger at 45:00 — test card
  H.15-H.18.
- **Not yet shown in game.** The "Behind schedule" message has not been seen.
  `SEA_SPEED` is calibrated on one data point (H.18 re-checks it). The Task
  Force economy, helicopter recovery and replenishment are not proven in game.
  Trimming the 180-mod list is still to do; each mod it removes is a
  collection change.

## What to expect in the comments

- **"Mission X won't load."** Almost always a missing or mis-ordered mod. Ask
  whether they subscribed to the collection and ran SETUP, then for their Mod
  Manager screenshot, and compare it against `LOAD-ORDER.txt`.
- **"SETUP isn't in the folder."** Seen once, on the fresh PC above: it
  appeared a minute or two after the player quit. Ask for the
  `workshop_log.txt` lines for 3812461539 and their launch and quit times.
- **A "dependency issues" prompt on the pack.** Possible now that the item has
  Required Items, though not yet seen (see *Dependencies*, above). Tell them
  to leave the order as SETUP set it, and if they pressed *Move dependencies
  above this mod*, to close the game and run SETUP again. Ask for a
  screenshot: it would be the first sighting (test card H.16).
- **"Unit Y is missing / wrong model."** That is the donor mod's asset, not
  this pack's — this pack ships no models, textures or audio. `CREDITS.txt`
  names which mod supplies what.
- **"Why the deprecated mods?"** Anzac Class Frigate (3440622312), S-70B-2
  Seahawk (3403661005) and E-7A Wedgetail (3499239964) carry the
  `[DEPRECATED]` tag and are kept on purpose: each is the only source of units
  the campaigns use. Replacing them is not a priority. (strykerpsg asked.)
- **Balance and time limits.** Take them seriously: they come from play, which
  the build's checks (reach, closure, opening ranges) do not replace. Answered
  in the 4 Oct upload: MattS found Macquarie Passage unwinnable, HMAS Supply
  making about 7 kn at flank in sea state 5, and `d4fd1668` moved the
  withdrawal line from 20 to 16 NM, set `SEA_SPEED[5]` to 0.45 and moved the
  deadline that loses a mission to 1.5 times its planned window, with a
  "Behind schedule" message at the planned minute; that also answers Dat
  Guy's "every mission is time-limited". Dat Guy's other reports were enemies
  starting too close in White Water and Steel Highway, the bought ASW aircraft
  spawning far away, and Southern Cross unwinnable (a spotter drone plus an
  escort boat with Harpoons against an unarmed landing ship). They have been
  changed since, on the deploy branch, and not yet reported from play (check
  the item's change log for whether an upload has carried them): `9ed587e7`
  moves the White Water and Steel
  Highway openings and brings Steel Highway's P-8 from 48 NM to 10 NM from
  the datum, and `e062fb3c` makes Southern Cross winnable and adds a build gate
  on opening ranges (test card 6H, H.19-H.22).
- **Game behaviour, not the pack.** A fighter that "can't shoot" a drone on
  Weapons Tight: the F-15EX report was the drone not being classified hostile,
  and it resolved once it was. ECM that switches off after a second: Weapons
  Tight runs jammers defensively only.
- **An author objecting to a copied file.** `CREDITS.txt` lists all 465, from
  51 Workshop mods, and invites exactly this. The game supports `#!alias`,
  which inherits the author's file and carries only what changed, and 350 of
  the 465 are 99.5% or more alike (CREDITS rounds them to 100%), so that offer
  is real and cheap to honour.
