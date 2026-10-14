# Red Storm Arsenal (3413868677): USS Richard Morris names a sonar that is not defined and leaves her NSM hatch animations unlisted

Drafted 14 Oct 2026 for the SEST author to post on the mod's Workshop page. Not posted by the repo.

**Seen on:** Sea Power 0.8.5 Build 261008, mod export of 14 Oct 2026 (the mod's 13 Oct "small missile fix" build). Read from the files; not seen in game.

**1. The variable-depth sonar.** `vessels/usn_ddg_richard_morris.ini`, line 305:

```
#SQS-35
Type=Sonar
SystemName=UMS-4249
Mount=SQS-35
```

No `systems/sensors.ini` in the collection defines `[UMS-4249]`, and nothing else in the export names it. The mod's own `sensors.ini` defines the VDS the Constellation uses, `[CAPTAS-4]` (line 1604, commented `#VDS`). As shipped, the Richard Morris's towed sonar resolves to nothing.

One-line fix: `SystemName=CAPTAS-4`, or add a `[UMS-4249]` section to `systems/sensors.ini`.

**2. The NSM launcher hatches.** The ship lists two animation files (lines 57-60):

```
[Animations]
NumberOfAnimationReferences=2
AnimationFile_1=animations_usn_ddg_richard_morris
AnimationFile_2=animations_usn_mk_41_vls
```

Her NSM containers (lines 927-942 and on) name hatch animations `NSM_1_R1_Open`, `NSM_1_R1_Close`, `NSM_1_L2_Open` and so on. Those are defined in the mod's `animations/animations_NSM_launcher.ini`, which the Constellation lists and the Richard Morris does not. As shipped, the hatch animations the containers name are never loaded for her.

Fix: `NumberOfAnimationReferences=3` and `AnimationFile_3=animations_NSM_launcher`.

**What SEST does meanwhile.** The SEST Integration Pack's copy of the hull (SEST Replenishment, which forks her for reload-at-sea) carries both lines corrected (`HULL_REPAIRS`). The repair is checked against the mod's file on every build and retires itself the day the mod ships the fix.

---
Draft text for the Workshop comment:

> Hi, two small things in `usn_ddg_richard_morris.ini` (0.8.5, your 13 Oct build): (1) line 305 gives the VDS `SystemName=UMS-4249`, which no sensors.ini defines; your own `[CAPTAS-4]` is the VDS the Constellation uses. (2) The NSM containers name hatch animations (`NSM_1_R1_Open` etc.) from `animations_NSM_launcher.ini`, but the hull lists only two animation files and that one isn't among them; the Constellation lists it. `NumberOfAnimationReferences=3` plus `AnimationFile_3=animations_NSM_launcher` would fix it. Thanks for the ships.
