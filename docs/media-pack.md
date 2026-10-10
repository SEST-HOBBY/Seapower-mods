# SEST media pack: loading screens, menu, loading text

The 10 Oct 2026 media research report proposed replacing the game's loading
screens, menu background and loading-screen text with real photographs of
naval, airpower, ISR and command work, and the SEST quotation set. This page
records which parts the game lets a mod change and where each part stands.

## What the game exposes

| Part | Hook | Status |
|---|---|---|
| Loading-screen text | `language_en/loading_tips.ini`, `[LoadingTips]` Count/Header/Tip001.. - merges key by key, the SEST pack loads first | **Live.** The 26 quotations replace the game's 19 tips; Header reads QUOTATION |
| Loading-screen pictures | `ui/backgrounds/loading_screen_1.png` .. `_80.png`, fetched through the FileManager (`streaming-media.txt`, 10 Oct 2026); mod 3491248180 already overrides 30 that way | **Live** (seen in game, 10 Oct 2026). 29 photographs (the 17 report photographs, all licences confirmed on their Commons pages, and the 12 gallery backgrounds) fill all 80 slots in turn: `tools/make_loading_screens.py`, `write_loading_screens` in the campaign builder. JPEG data under the game's .png names |
| Campaign backgrounds | `campaign.ini` `BackgroundImage=` (vanilla's linear campaign uses it; the SEST campaigns already set their own) | Available: candidates once the photographs are in |
| Main menu background | A film inside the game's Unity data - the clip `main_menu` on 'MediaPlayer' in the 'background' scene, loop off, sound played from the film (Player.log, 10 Oct 2026) | **Live** (seen in game, 10 Oct 2026). The first test swapped nothing - the plugin only took looping films and this one is not; `ClipName=main_menu` now pins the clip. The clip has no sound track (`tracks=0`), so the menu music plays on, separately |
| Mission browser film | `RightPane=` on a `Type=Tutorial` entry | Not used. The SEST Briefing Room entry played a film there until 10 Oct 2026, when the player found it unnecessary; it and the pack's field notes, which had followed the game's tips on the loading screen, are gone |

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

The loading screens are in the pack (above); the report's 17 photographs all came down with the licence their Commons page states.

## The menu film and its plugin

`tools/make_menu_film.py` cuts the retired Briefing Room's eleven gallery
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

The first test (10 Oct 2026, game 0.8.5) answered the open questions from
Player.log: Anchor Chain loaded and started the plugin, which found the menu
player - clip `main_menu`, loop off, playing its sound itself - and, under
its looping-only rule, left it alone. The plugin now swaps the clip
`sest_menu.ini` names (`ClipName=main_menu`, shipped), keeps the clip's
sound track playing on a second player without a picture when it has one,
and puts the SEST film back if the game sets its clip again.
