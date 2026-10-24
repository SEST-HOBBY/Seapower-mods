# Complete SEST combat costs — private playtest, 24 October 2026

The owner's request is complete pricing coverage, including estimates. The final catalog prices every resolved collection and vanilla weapon, vessel, aircraft and land-platform reference in both price modes. It preserves Claude's checked prices through commit `374634bc`; the remaining fields use explicit SEST comparisons or replacement models. Coverage is not a claim that every figure has an independently verified procurement source.

| Kind | References | Historical known | Current known |
|---|---:|---:|---:|
| Weapons, expendables, pods and tanks | 2,170 | 2,170 | 2,170 |
| Surface vessels and submarines | 937 | 937 | 937 |
| Aircraft and helicopters | 756 | 756 | 756 |
| Land vehicles and installations | 502 | 502 | 502 |
| Total | 4,365 | 4,365 | 4,365 |

This is the resolved reference inventory, including vanilla, collection content and explicitly non-procured helpers. It is not a count of unique real-world designs or physical objects in a mission. New Workshop or game exports require another rebuild and coverage check.

## Where to inspect prices

- `cost-list.csv` and `cost-list.md`: all references, both USD values, categories, field methods and provenance.
- `coverage.json`: machine-readable coverage, extensions, model choices and receipts.
- `backlog-resolution.md`: installed prices for all 377 unique references in the original 381-row attachment. Four references appeared twice in that attachment.
- `integration/combat-costs/coverage-policy.json`: versioned models, sources, CPI assumptions and sensitivity bands.
- `integration/combat-costs/mappings.json`: Claude's checked mappings and researched estimates, retained as the conservative first stage.
- `not-yet-confirmed.md` and `integration/combat-costs/research.json`: original research decisions. Filling a gap with a model does not confirm a rejected or unchecked candidate.

## Pricing rules

Every previously usable selected price, including an explicit zero, is preserved. Existing author blanks and invalid values receive a labelled SEST estimate under the owner's later request. A per-field override is emitted only where an inline blank would otherwise mask the new price. There is no global switch forcing every author value to SEST's value.

Tracker 0.7.1 precedence is reproduced: `Override<Field>`, then the entry's `OverrideInline`, then `[Costs] OverrideInline`, then false. A missing preferred key falls back; a present blank or invalid value does not. Current prices never silently borrow historical values. Original reference years are retained for copied or checked prices. A model's historical value is a rounded CPI backcast to its configured service year where available; absent a year, it is explicitly a 2026 replacement proxy. The CPI 334.4 used for 2026 is a Q2-based estimate, not a completed annual observation. Sparse historical CPI anchors are interpolated.

The 92 models are broad gameplay material-replacement estimates. Typical sensitivity is half to twice the central estimate, and a quarter to four times for designated future/fictional designs. These bands are not statistical confidence intervals. Models are rounded to three significant digits and should not be read as invoice precision. Sonobuoy and launcher hardware models use indexed primary Navy/DoD budget excerpts as comparators; those figures are not item-specific contract confirmations for every exported variant. All model sources and limitations are in the policy.

A fitted platform excludes separately charged ammunition, embarked aircraft, removable pods, carried fuel and cargo. A pod estimate covers hardware; its rounds are separate. Drop tanks price the tank hardware, not fuel consumption. Visual/control effects, ejected people and transfer/spawn processes have explicit included/non-procured dispositions; personnel are never monetized. Physical equipment such as land-based infantry hardware has its own material estimate. No campaign acquisition points, flight-deck ammunition points or `ammo_prices.csv` scores are treated as USD.

## In the game

**F11: original Combat Cost Tracker.** SEST extends the author's weapon, ship and aircraft catalogs without modifying or redistributing its DLL. Chaff, flares, noisemakers, sonobuoys, tanks and pods receive explicit valid categories, so they are no longer silently discarded by the default `Ignore` category. The category list exposes Gun, Decoy, Sonobuoy, Fuel tank, Pod and Other rows; the existing currency, overlay position, hotkey and price-mode settings are retained. A device contributes when the game's expenditure or loss records report it; its mere presence on a unit is not an expenditure.

**F10: SEST material-loss summary.** The independent SEST plugin shows the current mission's weapon expenditure, lost ships, aircraft, land platforms and remaining itemized stores. It uses native task-force registers, including recorded aircraft losses on the ground/deck, and works for standalone missions too. Native player, enemy and neutral task forces appear when present. Closing the popup restores the prior pause and time-compression state. Change `CombatCostsKey` in `plugins/sest_runtime.ini` and restart to choose another key.

**Task-force campaign debrief:** additional Combat Cost rows show Player and Enemy weapons, ships, aircraft, land and lost stores, this mission, and completed-campaign totals. It reads the saved native debrief records and reprices their quantities with the currently selected price mode/catalogs. Completed missions count once. Reopening a debrief does not write a save, and replaying a completed mission retains its prior supplemental record. This is a completed-mission material-loss account, not a sum of every failed/retried attempt or a running operating budget. The campaign map's Situation tab is unchanged.

The new SEST inventory module captures remaining itemized ammunition before a registered platform loss. It independently retains raw expenditure counters, including types omitted by the native saved weapon report. Mid-mission save/load and campaign completion write versioned SEST quantity keys alongside native data; no USD totals are stored. The native loss/weapon records remain authoritative and are not rewritten. Native tracker display failure does not uninstall this separate capture.

`+ ?` means a price or quantity is unavailable. Old saves can be repriced for their existing native records, but missing magazines cannot be reconstructed. Virtual flight-deck stock pools remain unknown because they are points rather than item counts. Stores represented only by such pools, cargo, operating fuel burn, crew, repair costs and damage-short-of-loss are outside the account. These are material limitations, not zero-cost claims. Land costs and parked-aircraft corrections appear in SEST's F10/debrief views; the original F11 overlay retains the tracker's own scope.

## Runtime and validation

The new module accepts only the previously inspected Sea Power 0.8.7 Build 261021 native assembly hash `eab2297ba92c6013958bdb2cf16d5794a4731330818ce353f89dc2241e16a3bd`. Anchor Chain, Combat Cost Tracker and SEST must be enabled before a full game restart. An unrecognized game build leaves the runtime plugin inactive with a log message; cost data remains installed.

The current workspace has the older 0.8.6 DLL plus the repository's 0.8.7 review. The expanded verifier passes a structural comparison of 62 signatures, 18 argument orders, 23 fields and 25 properties on that known 0.8.6 DLL. This is not a fresh 0.8.7 verification. New native inventory/modal hooks, external Unity/Noesis bindings and Harmony interaction still require the PC test card in `docs/playtests/complete-combat-costs-20261024.md`. The existing terrain/lost-hull fixes were previously seen loading on 0.8.7; that earlier observation does not prove these new features work in game.

Build with `SEST_MONO_PREFIX=<mono-prefix> python3 integration/runtime-fixes/build_plugin.py`, then `python3 tools/build_all.py --from-scratch`. The runtime builder runs 134 mocked assertions, including shared Python/C# price-precedence fixtures, actual loss acceptance, save/load, duplicate callbacks, replay preservation, repricing, unknown records and popup pause/close behavior. Python coverage checks preserve all known fields and validate all resolved references. See the dated review receipt for the full pack checks. PC acceptance remains pending.

## Earlier review

`tracker-review-20261024.md` records the original DLL review. The initial suspected decoy crash was refuted: missing categories defaulted to `Ignore`. The tracker still has a session-wide display-failure shutdown path; the new SEST capture and viewer are separate. `campaign-costs-design.md` retains the original read-only proposal, with an implementation update explaining the additional quantity capture.
