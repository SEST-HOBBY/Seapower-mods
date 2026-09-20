# Second Screen — the tactical map and roster on monitor 2

`SEST_Second_Screen` moves the two biggest UI panels off the 3D view and onto your
second monitor. Built for the pair of 2560×1440 screens recorded in
`data/display-layout.json`; re-detect and rebuild if that changes.

## What this is, and what it is not

Sea Power draws its whole interface inside **one Unity window**. Nothing in the mod
data opens a second OS window, and no launch flag splits the HUD across displays —
that would take a code mod against the game's own UI classes (Anchor Chain territory),
not an `.ini`.

What the data *does* expose is where panels sit **inside** that window.
`ui/Default/Settings_UI_Tactical.ini` carries:

| Key | Section | Meaning |
|---|---|---|
| `MapSize` | `TacticalMap_Geometry` | tactical map, Horizontal,Vertical px |
| `MapPosition` | `TacticalMap_Geometry` | Left, **Bottom** — from the window's bottom-left |
| `DefaultSize` / `MinSize` / `MaxSize` | `FormationManager_Geometry` | roster window sizing |
| `WindowPosition` | `FormationManager_Geometry` | Left, **Top** — from the window's top-left |

So the second screen is reached the way flight sims reach it: make the game window
span both monitors, then park those panels in the half of the window that lies over
monitor 2.

**Moves:** the tactical map, the Formation Manager window.
**Does not move — the game exposes no geometry for it:**

- the bottom unit / weapons / sensors row, and the context menus that open off it
- right-click order menus (they open at the cursor, wherever that is)
- the event log and camera-control windows (`LeftShift+Q`, `LeftShift+K`) — **drag
  them across once by hand**; the game remembers their position per user, and that
  position is not mod data
- pause, options, briefing and mission-end screens

That is the honest ceiling of a data mod here. If you want the order menus themselves
on screen 2, that is a code mod, and it is not what this pack is.

## Step 1 — make the window span both monitors

Unity will not span monitors on its own. Two routes, in order of reliability:

**A. NVIDIA Surround / AMD Eyefinity (recommended).** Merge the two monitors into one
logical 5120×1440 display in the driver control panel. Windows then reports a single
display, the game goes fullscreen across both, and nothing has to be positioned by
hand. Afterwards run the detector with `-SplitSingleDisplay 2` so the pack still knows
where the seam is.

**B. Borderless window, via Steam launch options.** Right-click Sea Power → Properties
→ Launch Options:

```
-screen-fullscreen 0 -popupwindow -screen-width 5120 -screen-height 1440
```

These are stock Unity player arguments. Caveat: Unity centres the window on the primary
display, so a window wider than that monitor can start straddling the desktop edge —
move it to the top-left corner once (drag, `Win`+arrow, or a borderless-window utility)
and it stays put.

Route B is also the fallback when Surround refuses the pair (mixed refresh rates,
mixed resolutions).

## Step 2 — record the real desktop

On the gaming PC, from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\detect-displays.ps1          # dry run
powershell -ExecutionPolicy Bypass -File .\tools\detect-displays.ps1 -Write   # save it
```

It reads the live monitor layout, cross-checks it against the adapter's own resolution
(a mismatch means DPI scaling is lying to it), and writes `data/display-layout.json`.
Useful switches:

| Switch | Use |
|---|---|
| `-PanelSide left` | panels go on the left-hand monitor instead of the right |
| `-SplitSingleDisplay 2` | Surround/Eyefinity is on: split the one wide display into halves |
| `-Margin 24` | wider gap between the panels and the screen edges |

It never writes to `usersettings.ini`; it only reads it to print what resolution the
game is currently set to.

## Step 3 — build and deploy

```bash
python3 tools/build_all.py        # or: python tools\build_all.py on the PC
```
```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1
```

The load order does not change: this pack is consolidated into `SEST_Integration`
like every other, and tier 0 already sits at the top.

To preview the numbers without writing anything:

```bash
python3 integration/second-screen/build_pack.py --plan-only
```

For the recorded 2×2560×1440 desktop that prints:

```
MapSize=1416,1416  MapPosition=2572,12
DefaultSize=400,1200  MaxSize=400,1416  WindowPosition=4708,12
```

— a 1416px square map against the inner edge of screen 2, the roster right-aligned to
the outer edge, and the strip between them left free for the event log window you drag
over yourself.

Tuning flags: `--margin`, `--fm-width`, `--fm-height`, `--map-size`. The builder refuses
any combination that overflows the region or overlaps the two panels, rather than
letting you find out in-game.

## Going back to one monitor

**Do this before playing on a single screen.** The map is positioned at x=2572; in a
2560-wide window that is off-view, and the game gives no hint why the map vanished.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\detect-displays.ps1 -Write   # writes mode=single-screen
```
```bash
python3 tools/build_all.py
```

`mode: "single-screen"` makes the pack ship the vanilla geometry byte-for-byte — a
deliberate no-op rather than an absent file, so the consolidated pack always contains a
complete, valid UI file. You can also just edit the `mode` field by hand. Reinstall
after rebuilding.

## How it coexists with SEST TacMap Colors

Both packs override the same file, `ui/Default/Settings_UI_Tactical.ini` — colours in
one, geometry in the other — and the game takes the **whole** file from whichever mod
wins. `tools/consolidate_packs.py` therefore merges `ui/` files as *deltas against the
vanilla copy*: each pack's file is diffed against
`mods-source/_vanilla/original/ui/Default/Settings_UI_Tactical.ini`, only the keys it
actually changed count as claims, and those claims are rewritten into the vanilla text.
Comments and section order survive, and two packs claiming the same key differently is
a hard build error naming both.

That baseline matters: without it, `SEST_TacMap_Colors`' inherited `MaxSize=400,800`
would look like a conflict with the geometry `SEST_Second_Screen` deliberately set, and
the build would fail on a disagreement that does not exist.

## If the map does not appear where you expect

| Symptom | Cause | Fix |
|---|---|---|
| Map missing entirely | window is not spanning; the map is off-view | Step 1, or rebuild in single-screen mode |
| Map on the wrong screen | `-PanelSide` wrong, or Windows has the monitors the other way round | re-run the detector with the other side |
| Map correct, roster still top-left | Mod Manager is loading another mod's copy of the UI file above SEST | `python3 tools/check_load_order.py`, then `tools/fix-load-order.ps1` |
| Panels land half off-screen | detector saw DPI-scaled sizes | run it again from an elevated/unscaled shell; it warns when the adapter disagrees |
| Everything shifted by a constant | monitors not top-aligned in Windows | align them in display settings and re-detect (the detector refuses to record a non-rectangular desktop) |
