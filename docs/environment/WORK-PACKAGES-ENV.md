# Environment track ENV-00..ENV-09 against the work packages of 18 November

Supplement to `docs/handoff/WORK-PACKAGES-20261118.md`; it does not change that file's order
of work. The ENV track runs beside it and waits on the same PC gates. Nothing here edits a
BA or PC package's files.

| ENV | Content | Depends on (existing ids) | Touches existing files? |
|---|---|---|---|
| ENV-00 | Map render targets | PC-01 (R15 runs), PC-02 (public-release capture), a DCM-on-0.9.3 capture | No; read-only capture via existing `tools/capture-beta-references.ps1` |
| ENV-01 | Weather Lab mission | none for building; PC session for the in-game check (proposed **PC-08**) | No |
| ENV-02 | Static overlay + Layers control | ENV-00; DCM on 0.9.3 (blocks all GCO PC checks, as for BA-08) | Later: a new runtime folder and one ini switch beside `RuntimeFixesMod.cs` switches (BA-10 pattern); no change to F8/F11 code |
| ENV-03 | Animated time layers | ENV-02 | as ENV-02 |
| ENV-04 | Snapshot format, cache, ingest tools | none | No |
| ENV-05 | Campaign clock, per-save sidecar, forecast | DCM on 0.9.3; shares the per-save requirement of GMO-03 (BA-03, BA-11 ribbons per save) - the sidecar pattern can serve both | No (a sidecar beside saves, not `world-service-v1.txt`) |
| ENV-06 | Native weather in GCO battles | ENV-01 PC result; DCM `MissionWriter.Text` on 0.25.0.1 | Later: one postfix, behind the ENV switch |
| ENV-07 | Sea ice, shelves, icebergs | BA-09 regions; **PC-05** before anything south of -62; GM-04 for stations (labels, owner answer 6) | No |
| ENV-08 | Logistics consequences, authored weather operations | BA-08 multi-base, BA-09, PC-05; GM-10 for replenishment capacities | Later, behind the switch |
| ENV-09 | Packaging into the new MNO item | BA-05 (naming), BA-14; PC-07 | Only when gates pass |

Proposed new PC session: **PC-08 Weather Lab** (`docs/environment/ENV-PC-PLAYTEST.md`), after
PC-01, about 10 minutes with `-Quick` (45 for the full card), independent of DCM.

Order relative to section 2 of the work packages: ENV-01's PC-08 can follow step 1 (R15 first
run). Everything GCO-side follows step 1 and the DCM question. ENV-04 and the Python reference
work need no PC and do not compete with BA items for PC time.
