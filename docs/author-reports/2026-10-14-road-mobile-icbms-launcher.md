# Road Mobile ICBMs (3571718093): the two trucks name a launcher section the mod does not define

Drafted 14 Oct 2026 for the SEST author to post on the mod's Workshop page. Not posted by the repo.

**Seen on:** Sea Power 0.8.5 Build 261008, mod export of 14 Oct 2026 (`_info.ini` ApproximateVersion=0.8.0). Read from the files; not seen in game.

**What happens.** Both launcher trucks point their weapon mount at a launcher called `ICBM_Launcher`:

- `land_units/wp_ss-27_tel.ini`, line 76: `SystemName=ICBM_Launcher`
- `land_units/pla_df-41_tel.ini`, line 76: `SystemName=ICBM_Launcher`

The mod's own `systems/weapons.ini` defines the section as `[ICBM_Launchers]` (line 2, plural). No other mod in a 196-mod load order defines `[ICBM_Launcher]`, so the mount resolves to nothing and the Topol-M and DF-41 cannot fire.

**One-line fix.** Either rename the section in `systems/weapons.ini` to `[ICBM_Launcher]`, or change the two `SystemName=` lines to `ICBM_Launchers`. The second keeps the section every other reference already uses.

**What SEST does meanwhile.** The SEST Integration Pack ships a copy of each truck file with `SystemName=ICBM_Launchers` (SEST Collection Fixes, `LAND_UNIT_REPAIRS`). The copy is retired automatically the day the mod ships the fix.

---
Draft text for the Workshop comment:

> Hi, thanks for the mod. One thing I noticed in the files (0.8.5, 14 Oct export): both TELs (`wp_ss-27_tel.ini` and `pla_df-41_tel.ini`, line 76) use `SystemName=ICBM_Launcher`, but `systems/weapons.ini` defines the section as `[ICBM_Launchers]`. Nothing else in my load order defines `[ICBM_Launcher]`, so the mount has no launcher and the trucks can't fire. Renaming either side to match fixes it. Happy to test a build.
