# SEST media pack: loading screens, menu, loading text

The 10 Oct 2026 media research report proposed replacing the game's loading
screens, menu background and loading-screen text with real photographs of
naval, airpower, ISR and command work, and the SEST quotation set. This page
records which parts the game lets a mod change and where each part stands.

## What the game exposes

| Part | Hook | Status |
|---|---|---|
| Loading-screen text | `language_en/loading_tips.ini`, `[LoadingTips]` Count/Header/Tip001.. - merges key by key, the SEST pack loads first | **Live.** The 26 quotations replace the game's 19 tips; Header reads QUOTATION |
| Loading-screen pictures | The loading screen fetches its backgrounds through the game's FileManager (changelog: "LoadScreen to use FileManager to get backgrounds"), so a mod file can stand in for one | **Folder not yet known.** The repo's copy of the game's files is text only. `tools/capture-context.ps1` now writes `data/install-snapshot/streaming-media.txt`, the game's own pictures by folder |
| Campaign backgrounds | `campaign.ini` `BackgroundImage=` (vanilla's linear campaign uses it; the SEST campaigns already set their own) | Available: candidates once the photographs are in |
| Main menu background | A film inside the game's Unity data (`sharedassets1.resource`, per the Player.log video warning) - not a file a mod can replace | **Plugin, awaiting the first in-game test.** `plugins/` in the pack: an Anchor Chain plugin swaps the menu's looping film for `sest_menu.mp4` (approved by the author 10 Oct 2026). See below |
| Mission browser film | `RightPane=` on a `Type=Tutorial` entry | Used by the SEST Briefing Room |

The pack's own field notes, which used to follow the game's tips on the
loading screen, are now in the Briefing Room entry's description
(`integration/common/field_notes.py`).

## The photographs

`integration/media-pack/sources.json` lists the report's 24 Commons items:
17 photographs to ship and 7 videos held for stage two. Commons cannot be
reached from the build container, so:

1. `tools/fetch-media-pack.ps1` (PC) downloads each photograph at up to
   3840 px, after reading its licence from its own Commons page. It refuses a
   file whose page gives a different licence from the report's, any
   NonCommercial or NoDerivatives licence, or a public-domain file the page
   marks copyrighted (the report's Virginia-class rule). The photographs land
   in `integration/media-pack/source/images/` and the record in
   `source/fetched.json`.
2. `integration/media-pack/build_media.py` (container) cuts 16:9 loading
   backgrounds at 1080p, 1440p and 2160p, never upscaling - a size the
   photograph cannot fill is not made. The SM-3 portrait goes full height on
   a dark panel. Menu candidates (CSpOC, CAOC, P-8A, E-2D, Lincoln CSG) also
   get a 30%-darkened version, and a solid `#0B1115` fallback is written at
   every size. `game_ready/` is rebuilt, not committed.
3. `media_manifest.csv` and `ATTRIBUTION.md` beside it are committed: one
   row per source with its status, and the credits for what ships.

Wiring `game_ready/loading/` into the pack waits on `streaming-media.txt`.

## The menu film and its plugin

`tools/make_menu_film.py` recuts the Briefing Room's eleven gallery
photographs as a menu background: no text, darkened 30%, a slow drift on
each shot, 1.5 s cross-fades, the last shot fading into the first so the
49.5 s loop has no join, no sound, 1280x720 (the photographs' own width).
A sharper 1080p cut can follow from the report's photographs once they are
fetched.

`integration/menu-background/` holds the plugin. Anchor Chain 1.1.0 (Workshop
3380210757, installed by SETUP) does not start BepInEx plugins: it loads every
DLL in every mod folder the game's FileManager knows - a pack in StreamingAssets
as well as on the Workshop - and starts each class marked `[ACPlugin]` that
implements `IAnchorChainMod`. The SEST class builds a component on a
GameObject kept across scenes; that component looks for Unity VideoPlayers
for ten minutes after start and half a minute after each scene load, and
swaps the first one that loops a clip from the game's data. A one-shot film
(an intro the game may wait on) and the mission browser's file-based films
are never touched; if Unity cannot play the SEST film the game's clip is put
back; `sest_menu.ini` can name the clip or turn the plugin off. Every
VideoPlayer it sees is logged to Player.log as `[SEST Menu]`.

Not yet known, and read from the first test's Player.log: which clip the
menu loops, and whether the menu's music is part of that film (if it is,
the swap silences it and the plugin needs to leave the audio alone).
