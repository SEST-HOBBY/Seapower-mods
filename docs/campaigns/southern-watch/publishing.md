# Publishing Southern Watch to the Steam Workshop

Read this after the test card passes, not before. A Workshop item that goes up
broken is harder to fix than one that goes up late: subscribers get the broken
version, and the comments arrive before the patch does.

## What the game actually provides

Everything below about the Mod Manager is read out of the game's own UI
strings in `mods-source/_vanilla/original/language_en/ui.ini`, section
`[ModMenu]` and `[MainMenu]`. Nobody here has watched the upload run, so treat
the *order* of the steps as informed and the *existence* of each control as
established.

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

`[ModMenu]` also has `OpenFolder`, which is how you confirm *which* folder is
about to be published, and the tag dimensions the game sorts by:
`TimeLocation` (Timeframe and Location), `ModType`, `ObjectType`, `Alignment`.

## The dependency problem solves itself

This is the important part, and it is why a 133-mod campaign is a publishable
thing at all.

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

Nothing in any mod's `_info.ini` declares a dependency — 226 of them in this
collection and the only keys are `Name`, `Description` and `[Compatibility]`
version bounds. So the dependency list does not live in the mod. It lives on
the **Steam Workshop item**, in Steam's own *Required Items* field.

**Therefore: set all 134 mods as Required Items on the published item.** A
subscriber then presses Sync and the game does the rest. Without it, you are
asking a stranger to subscribe 134 times by hand, which nobody will do.

`docs/campaigns/southern-watch/required-mods-urls.txt` is the list, generated
by `build_pack.py` from the same coverage rows the pack's own
`REQUIRED-MODS.txt` uses, in canonical load order, one Workshop URL per line.
It cannot name a mod the campaign does not reach, and it cannot miss one the
campaign does.

One item on it is not in the collection and has no id here: **SeaLifter**,
which B-2 Spirit declares as its own requirement. Find its id and add it
before publishing, or drop the B-2 from the campaign. Do not publish with that
gap unresolved — it is the one dependency most likely to break a subscriber's
install, and it needs a manual preloader step on top of subscribing.

## Before you press Submit

1. **The test card passed.** Not "mission one loads" — the card, including
   section 1A on the art and section 2 on Task Force Mode, which has never
   been run.
2. **A clean-install check, if you can face it.** Everything verified so far
   was verified on the machine that built it, where all 139 mods happen to be
   present. The one thing nobody has done is subscribe to exactly the required
   set on a clean profile and see whether the campaign runs. If a second
   machine or a second Steam account is available, that is the highest-value
   hour available before release.
3. **Publish Unlisted or Friends Only first.** Set the Required Items, press
   Sync from a different account, and watch the dependency subscribe actually
   happen. Flip to Public once it does. The visibility enum exists precisely
   so you can do this.
4. **`git status` is clean and the four gates pass.** The folder you are about
   to upload is build output; if the tree is dirty it is not the reviewed
   build.

## The upload itself

Game closed for the build, game open for the upload.

1. Run the install procedure in `install-alignment.md` so
   `StreamingAssets\SEST_Integration` is exactly the committed build.
2. Launch Sea Power → **Mod Manager**.
3. Use **Open Folder** on `SEST Integration Pack` and confirm it opens
   `…\Sea Power_Data\StreamingAssets\SEST_Integration`, and that
   `REQUIRED-MODS.txt`, `LOAD-ORDER.txt` and `CREDITS.txt` are sitting in it.
   That is the folder that goes up.
4. **Create Mod**.
5. Fill it from `docs/campaigns/southern-watch/workshop-listing.md` — that
   file is paste-ready copy for Name, Description and the screenshot order.
6. **Tags**: the dimensions the game sorts on are Timeframe and Location, Mod
   Type, Object Type and Alignment. This is a modern (2028) Western Pacific /
   Australian campaign; pick the closest available in each, and take
   `Campaign`/`Missions` if a content-type tag exists.
7. **Visibility**: `Unlisted` for the first pass. See step 3 above.
8. **Submit Mod**.
9. On the Workshop page, add every URL from `required-mods-urls.txt` to
   **Required Items**, and upload the screenshots.
10. Sync-test from another account, then set Public.

## Updating it afterwards

The same Create Mod flow republishes an existing item; `ChangeLog` is the
per-update field. The loop is:

```powershell
git pull origin <branch>
python tools\build_all.py --from-scratch    # git status must be clean
powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1
```

then Mod Manager → publish, with a changelog entry. The pack is build output,
so the Workshop item and the repo cannot drift as long as the install is IN
LINE with the commit before you upload.

**Re-check Required Items on every update.** `required-mods-urls.txt` is
regenerated on every build; if the campaign gains or loses a donor mod, that
file changes and the Workshop item needs to match. Nothing on Steam's side
will tell you it has fallen behind.

## What to expect in the comments

- **"Mission X won't load."** Almost always a missing or mis-ordered mod. Ask
  for their Mod Manager screenshot and compare against `LOAD-ORDER.txt`.
- **"Unit Y is missing / wrong model."** That is the donor mod's asset, not
  this pack's — this pack ships `.ini` files only. `CREDITS.txt` names which
  mod supplies what.
- **Balance complaints.** Take them seriously; no mission here has been played
  to completion by its author, and the listing says so.
- **An author objecting to a copied file.** `CREDITS.txt` lists all 79 and
  invites exactly this. The game supports `#!alias` for the cases where
  nothing needed to change, and three of the 79 are byte-identical, so that
  offer is real and cheap to honour.
