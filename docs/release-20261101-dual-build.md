# SEST Integration Pack — 1 November 2026 consolidated release

**One Steam Workshop item (3812461539), beta-first with normal/stable compatibility.** This is a release candidate, not yet published and not yet a fully validated beta release.

## Two game baselines, one mod

| Profile | Game | Inputs | Native runtime |
| --- | --- | --- | --- |
| Beta (primary target) | 0.8.7 Build 261026 | data/game-baselines/beta-261026 | 1.5.0/UI 1.4.2 intentionally inactive on beta; beta loader under test |
| Stable (maintained) | 0.8.7 Build 261021 | mods-source/_vanilla | Known-good Runtime 1.5.0 and UI 1.4.2 preserved and pinned |
| Newer/unknown | unverified | no trusted baseline | Data-only fallback; binary SHA gates unchanged |

Source and Workshop item are shared. Two GitHub Actions build jobs exercise both game definitions. They do not represent two public Workshop subscriptions or prove in-game behavior.

The bundled SETUP invokes sest-profile.ps1 and identifies the actual build using the Seapower-Scripts.dll SHA256 (semantic version is 0.8.7 on both branches). SETUP warns before making changes and blocks the discontinued PR #53 test DLL. It does not disable valid stable features or secretly enable the beta DLL.

## Integrated changes since 28 October

- Canonical order and catalog now include Contact Log 3819427362, Sea Power Topographic Map 3826122523, Pop-Out Windows 3826396311 and B-21 Raider 3821992229. There are **203 Workshop IDs plus SEST**, based on the 28 Oct capture; verify new subscriptions on the 1 Nov PC capture.
- Group Manager 0.2.17 retitled without changing its legacy catalog slug.
- SM-3 Block IIA/IIB optional ExtendedGuidance seeker values explicitly declined in Collection Fixes, rather than being folded into stock missile behavior.
- Charles de Gaulle EOMS-NG alias rebuilt from the current EOMS_NG sensor definition.
- RAN S-70B-2 AntiShip Redback retargeted to the AGM-119-derived station 10; regression updated.
- World Sandbox KC-30A scores 60 as a tanker, rather than 2 as an airliner.
- B-21 weapon families and aircraft cost proxies and small UAV Aliaca gameplay proxy labelled as estimates. Obsolete Chilean JvH cost ID removed, retaining renamed hull mapping.
- Bounded Anchor Chain source, inert-first beta bootstrap and guarded test/rollback scripts carried in source but not installed/published.
- tools/capture-all-mod-updates.ps1 captures Steam's local install, plugin DLL SHA256 values and changes, exports configurations, checks beta source/build without installing, and produces one dated ZIP.
- GitHub Actions runs source/inventory and full from-scratch stable and beta source builds. Build success is NOT gameplay validation.

## Release gates

1. Capture Steam downloads from 1 Nov on the gaming PC using the one-command capture script with the game closed; review the ZIP and integrate author updates.
2. Make both data builds and source/inventory/dependency checks pass, and regenerate consolidated output. Preserve original stable binary 1.5.0.
3. Verify stable game launch, campaign mission, F11 costs, preparation and UI with the original Runtime 1.5.0.
4. Verify beta launch without discontinued PR #53 code. Test staged inert bootstrap, then bounded Anchor Chain loader only in a controlled session with easy rollback; diagnose native Harmony compatibility before asserting runtime works.
5. Update the Steam item's Required Items and collection 3812390790 to match the canonical 203+ mod list. SETUP refuses missing subscribed IDs.
6. Upload only to existing SEST Workshop item; retain previous stable release for rollback.

## Known limitations

- The 1 November PC capture has not yet reached this branch.
- Beta native Runtime 1.5.0, F11, Noesis UI and debrief are not verified. A beta data-only fallback is not full beta support.
- The source for the shipped 1.5.0 binary remains unrecovered; rebuilding the older 1.2.0 project is a downgrade and prohibited.
- No Steam Workshop upload has occurred from these GitHub changes.

Do not label this release complete solely on a successful build or pull request.
