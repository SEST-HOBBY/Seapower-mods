# Euromod Combat Systems

Current configuration reference, updated 2026-10-01. Euromod supplies **54 combat-system profiles and 162 ship assignments**. Profile names describe system families, roles or upgrade levels. Values are gameplay tuning, not measured real-world performance.

See [Combat system assignments and profile descriptions](CombatSystems_assignments.md) for every installed ship override, all profile descriptions and the current values.

## Files and activation

Paths below are relative to `StreamingAssets/Euromod`:

- `systems/combatsystems.ini`: the 54 profile definitions.
- `vessels_overwrite/*_CombatSystems_OVWR.ini`: one native `#!extend` override per ship, assigning one combat system.
- `language_overwrite/CombatSystems_systemgroups_OVWR.ini`: display names targeting the nine language files (en, de, cn, es, fr, ja, ko, ru, vn). Technical names are shared across languages.

Enable Euromod and the relevant ship pack. Restart Sea Power after changing these files so cached definitions are reloaded. The overrides do not install missing ship models. The definitions now belong in Euromod; avoid a duplicate copy in `user/systems/combatsystems.ini`.

## Assigning a profile

Use the exact profile ID from the assignment reference. For example, the installed modernized multirole override contains:

```ini
#!extend vessels/usn_ffg_oliver_hazard_perry_mlu.ini

[CombatSystems]
NumberOfCombatSystems=1

[CombatSystem1]
SystemName=CMS_Multirole_MLU
```

The ship filename identifies the target; the reusable profile name stays neutral. Keep one assignment per ship. Existing additional or national combat-system sections require review when adding an override.

## Profile settings

These keys belong under the profile's section in `systems/combatsystems.ini`:

| Key | Values and intended meaning |
|---|---|
| `ReactionTime` | These profiles use the symbolic bands `Slow`, `Medium`, `Fast` and `VeryFast`; the game also has `VerySlow`. Bands resolve through `TargetAquisitionTime` in `systems/sensors.ini`. This is not the total time from detection to firing. |
| `DatalinkTier` | Integer tier from 0 to 5. Current Euromod profiles use 5 for fleet-network profiles and 1 for local profiles. Higher numbers are not extra network capabilities. |
| `DatalinkSource` | `True` or `False`: whether the unit may act as a datalink source, subject to the game's other conditions. |
| `SignalProcessingBonus` | Numeric modifier added to sensor signal processing. All 54 profiles use `0`, leaving the existing sensor processing bonus unchanged. |
| `CICSlots` | Integer nominal picture-management capacity. The previously inspected engine applies a lower bound of twice `TotalSolutionChannels()`, so this is not a hard track limit. |
| `EvaluationSlots` | Positive integer count of simultaneous evaluation processes. It does not add missile guidance or illumination channels. |

Example profile:

```ini
[CMS_Multirole_MLU]
ReactionTime=Fast
DatalinkTier=5
DatalinkSource=True
SignalProcessingBonus=0
CICSlots=48
EvaluationSlots=3
```

## Names and assignment intent

`CMS` means combat management system; `AAW` means anti-air warfare; `ASW` means anti-submarine warfare; `MLU` means mid-life upgrade; `MCM` means mine countermeasures; `OPV` means offshore patrol vessel; and `USV` means unmanned surface vessel. `BL` identifies an AEGIS baseline. `Compact`, `Integrated`, `Enhanced`, `Refit` and `Upgrade` are descriptive gameplay labels, not manufacturer revision numbers or universal performance grades.

AEGIS assignments follow the represented `eu_AEGIS_BL5`, `eu_AEGIS_BL9` or `eu_AEGIS_BL10` sensor fit, including inherited fits in the current Burke files. Those sensor IDs remain distinct from the combat-system IDs `AEGIS_BL5`, `AEGIS_BL9` and `AEGIS_BL10`. An assignment describes the mod's equipment, not the historical software baseline of every hull or year.

Other assignments follow the represented system family, equipment, role and modernization. The early Arleigh concept reuses the base-game `AEGIS_Mk7`; three Spruance fits reuse `NTDS_TAS`. Submarines use analog, digital or integrated local profiles. Small support craft and USVs also use local profiles. Local operation is a gameplay assumption, not a claim that the real platforms lack radio or datalink equipment.

## Limits and verification

Future and upgrade profiles include gameplay assumptions. These entries do not add radar coverage, CEC, BMD, missile guidance, torpedo guidance or remote-control functions. Existing sensors, weapons, crews and game options still determine their respective behavior. Combat-system changes may also affect the game's point calculation.

This documentation was checked against the installed INI files: all 54 definitions, 162 assignments, profile references and display-name keys agree. This update changes documentation only. It does not establish in-game validation or release/stable-beta compatibility; previous parser checks on an earlier package are not proof for the current installation.
