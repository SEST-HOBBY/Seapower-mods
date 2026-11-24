# Changelog

## 1.0.1 - 2026-11-22 - shorter notice

- The notice about the Workshop item is shorter: one sentence and three bullets; it says Rigging is just a code library, and the buttons explain themselves.

## 1.0.0 - 2026-11-21 - the shared part of the R.A.T.S. mods as a library of its own

- First version: the skeleton every R.A.T.S. mod used to compile into its own DLL is now one DLL, `SeaPowerRigging.dll`, for the game's current main version.
- One object per mod (`RigMod`) holds a mod's log, settings, hooks, mission events, Options tab and host; nothing of a mod is shared with another.
- Mission start and end and the Options menu page are hooked once for every mod, not once per mod.
- A mod stays off when it is unticked in the game's Mod Manager, as before; the check now reads the mod's own folder.
- The map layer entry keeps only the 3D-globe path.
- A game message box tells players who run the mods on a built-in copy that the Workshop item exists, with "Get Rigging", "Not now" and a tick that keeps it quiet until the next Rigging update.
