# Workshop playtest, 16 October 2026

The user played from the Workshop copy of the pack (3812461539, build
c4b9eaf7, the only SEST folder installed, position 1): one stand-alone mission,
then Southern Watch from a new save ("SOUTHERN WATCH TEST RUN 1"), mission 01
White Water, Exit from the debrief, back to the campaign map, then the main
menu. Capture `6b54d384` on `chore/capture-playtest-20261016`. Three things
were reported; each was diagnosed from the log and the code and checked by a
second reviewer trying to refute it.

## 1. The stock film on the main menu after the campaign

SEST's menu plugin (1.2.0) looked for the menu's video player only for ten
minutes after start and half a minute after each scene load. The game builds
that player anew every time the main menu comes back, and coming back from a
mission or a campaign loads no scene (the main-menu scene stays loaded
underneath). In the log the film was swapped at start-up and on the return
from the first mission (both inside ten minutes); the campaign mission loaded
at about 910 s and ended near 1,780 s, and after it there is no `[SEST Menu]`
line at all. Fixed in plugin 1.2.1: it looks every half second for the whole
session, never takes its own sound player for the menu's, looks again at a
player found before it has a clip, and caps the log lines for other players
at fifty. On the next session each return to the main menu should log a
`[SEST Menu] video player 'MediaPlayer' ...` / `menu film now` pair.

## 2. The NullReferenceException on the campaign map

`player.log` 5154-5193: on Exit from the debrief the game's scene-unloaded
handler (`RefreshAfterMissionReturn`) recentres the map on the next mission
while the mission scene is still unloading. One line earlier the game logs
`[Singleton<SeaPower.ResourceLoader>] Instance will not be created because
the mission scene is unloading`, and the tile renderer then fails in
`SeapowerTileMap.RenderTileFromHeightmap`, called from a Harmony-patched
`LoadTiles` (the DMD frame). About 25-30 earlier campaign returns in the
captured logs, without the Dynamic Campaign Mod or with 0.24.2/0.24.3, never
did this; between the last clean one and this session the only code mod that
changed is the Dynamic Campaign Mod (0.24.3 -> 0.25.0, same game build), the
only mod whose log has named `SeapowerTileMap`. SEST is not involved: its
plugin patches no game code, and its backdrop painter touched only
`ui/backgrounds` loading screens in that session. Not fixable in SEST; a report
for DCM's author is drafted. The dialog is safe to dismiss: Noesis caught the
exception and the campaign save was written.

## 3. Southern Watch's enemy order of battle

The window is the game's own Situation screen, fed by
`campaigns/sest-southern-watch/enemy_theater_roster.ini` (not the Dynamic
Campaign Mod).

| What the screen showed | Cause | Change |
|---|---|---|
| A `pirates` tab | The narco-submarine mod (3413868677) registers `Nation=pirates`; the roster used the raw key as its label and the window shows labels raw | `ROSTER_NATION` maps it to `Pirates`; test |
| `j10` | The J-10C mod (3481228992) names it `j10,j10` | Name Fixes: `J-10C Vigorous Dragon,J-10C` |
| `JH7A` with the `?` flag | The JH-7A mod (3526982088) names it `JH7A`, and its squadron table declares seven squadrons and defines none; the roster names `Squadron1`, so the row found no nation | Name Fixes: `JH-7A Flying Leopard,JH-7A`; Collection Fixes adds `[Squadron1] Nation=China` (count 1); the roster builder now stops on a squadron the winning file does not define; test |
| The J-20A's 3D render | The gallery skipped units the real-photos mod (3796706214) pictures without checking that its picture wins; for the J-20A 3591563716 ranks above it | `write_profiles` now skips only where the real-photos mod's picture wins at load order: 61 units, the J-20A among them, get SEST's real class photo |
| Same text in both columns | Stock behaviour: aircraft are reusable with no individual names, and the PLAN block carries stock's `ShowOnlyClassName=True` | None |
| Blurred side bars on the photos | SEST Gallery's own 768x232 strip, the photo over a darkened blurred copy | None (design; a centred crop is the alternative) |

Not changed, unconfirmed: the Pirates row's flag may still show `?` if the
game matches `Nation=pirates` against the flag table's `Pirates` case by
case; nothing in the repo shows either way.

Other log lines: Identify Expanded still cannot find its language file under
StreamingAssets (known, the author's); the HarmonyX "Could not find field /
property" warnings are other code mods probing member names, as in earlier
captures.

## Checks

Gates 11 of 12 (`check_inventory`, the four CR-stripped mods as before);
campaign tests 198, tool tests 105.
