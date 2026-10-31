# Beta 261026 plugin compatibility and recovery — 31 October 2026

**Target:** Sea Power 0.8.7 Build 261026. **Status:** original game launches after removing the experimental PR #53 bridge; no beta SEST runtime release validated.

Evidence: owner-provided private 31 October diagnostic ZIP (BepInEx.log, Player.log and Player-prev.log), plus the publicly auditable [AnchorChain 1.1.0 source](https://github.com/SeaPower-Modders/AnchorChain/blob/main/AnchorChain/Main.cs). Do not upload unredacted logs to public GitHub; they include local system paths.

## Confirmed sequence

1. An early AnchorChain.Preloader 1.0.0 attempt cannot find the Workshop chainloader.
2. PR #53's experimental bootstrap correctly identified the beta assembly and found AnchorChain.dll at Workshop item 3380210757; a later reflection revision allowed plugin initialization, but that test prevented a normal launch.
3. In the prior Unity Player-prev.log, the startup reached numerous native patches. Multiple code mods reported incompatible methods, some safely disabling themselves; others failed patching. The log ended with **351 occurrences** of the single line `[AutomaticSAR] Loaded.` and no normal shutdown.
4. The next log, after the old bridge was removed, shows the original preloader failure but orderly Unity shutdown. The owner confirmed the game opens again.

## Loader defect in upstream 1.1.0 (source inspection)

The upstream AnchorChainLoader.LoadPlugins() uses a pending set. On TriggerEntryPoint exceptions, it neither removes the failed plugin nor changes the set's progress. The no-progress error branch logs an abort without executing `break`. This is an unbounded retry loop. A failing plugin can therefore re-run partial initialization or Harmony patching repeatedly. It is consistent with the Automatic SAR flood, but the exact triggering plugin is **not proven** because the earlier BepInEx log was overwritten before capture.

The SEST beta fork is under integration/beta-anchorchain/source/Main.cs (MIT licence retained). It uses an entry guard, a failed-plugin set, a bounded loop and a true no-progress exit. Its separate inert-first bridge requires an explicit enable flag. Nothing in this source fork replaces the Workshop author's file.

## Native-code mod issues evidenced by Player-prev.log

| Plugin | Evidence / behavior on 261026 | Release disposition |
|---|---|---|
| EnhancedDecoyMod | Contact-constructor Harmony pattern missing; rollback logged | incompatible patch, upstream fix needed |
| MissileControlMod | steering limit hook signature changed; returns to native behavior | disabled for affected hook |
| MultiStageMissiles | Missing MissileSimulator.BuildAltitudeNodes | disabled; confirm weapon fallbacks |
| OptimalTargetDist | unrecognized shared-launch layout | native/name fallback, not fully functional |
| SubModelStabilization | target method resolution / Harmony failure | disabled |
| TestRange | missing SeaPower.ECM.CombinedJamUnit | disabled |
| WeaponLauncherEffects | target method / Harmony patch failure | disabled |
| LoadoutManager | void-method IL Compile Error | patch failed |
| BetterTacMap | missing GizmoLayerManager target method | patch failed |
| SEST Runtime 1.5.0 | rejects beta Seapower-Scripts SHA256 3005bc6d… | intentionally inactive |
| SEST UI Follow-up | reports owning pack disabled in capture | not validated on beta |
| Automatic SAR | 351 repeated Loaded lines in failure session | symptom of repeated initialization or another loop, not proven root |

**None of those native-method mismatches is corrected by the bounded Anchor Chain fork.**

## Release gates

- Do not install PR #53's old experimental bootstrap.
- Confirm source-only build and staged inactive probe before any activation.
- Confirm patched loader terminates with failed code plugins instead of looping and the game reaches its main menu.
- Confirm no duplicate Harmony patching across normal game launches and missions.
- Keep SEST Runtime 1.5.0 and UI pins inactive on uninspected beta native assemblies; do not replace the stable binary with the older source fork.
- Review mission/campaign compatibility and the 203 Workshop dependency list independently before any Workshop release.
- Preserve a clean stable release and stop/rollback if the beta fails to launch.

The test must distinguish **the game opens**, **Anchor Chain returns**, **mods initialize**, and **SEST gameplay features function**. Those are separate acceptance criteria.
