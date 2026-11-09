# R11: one modernised world and coordinated UI refinements

The original World Sandbox and complete Regional Expansion form one new-game
entry, **SEST Modernised Worldwide Campaign 2028**. Every original base,
force, patrol and catalogue entry is retained. The combined definition has
156 bases, 293 forces, 54 patrols and 1,586 catalogue entries. It keeps
`sest.world_sandbox_2028.regional`, the identity used in the latest PC capture.
The original definition is archived outside `dynamic_campaigns`, with a
reversible helper for original-world saves. Native saves are not converted.
New content requires a new campaign.

## Delivered behavior

| Area | R11 behavior | Validation boundary |
|---|---|---|
| World map | Existing continuous longitude bounds retained; full original/regional content combined | JSON, unit, patrol, water and rebuild checks; new definition needs PC playtest |
| Native ribbons | Four fictional final-mission awards with original stripe artwork and citations | Definitions, image paths and final-mission placement checked; native Service Record needs PC check |
| World Operations | F11 Overview, Forces, Costs and Service; movable/resizable native window with tabs | Native bindings and model checked; Noesis rendering, input and pop-outs need PC check |
| World economy | Native credits shown separately from USD estimates; sources, basis and unknowns displayed | Existing pricing/history policy plus current factory cache and row tests |
| World service | Atomic versioned profile ledger; manual battle reports; global and evidenced theatre progress | Persistence, duplicate loads, auto-resolves, unknown formats, scope separation and coordinates tested |
| Battle history | Latest cost record for the same completed engagement; missing older evidence not invented | Pure report-selection test and preserved history policy |
| Coordinated Strike | Shared colours and planned/remaining weapon estimate beneath original planner | Exact author style/field bindings checked; original scheduling/launch code retained; PC layout check pending |
| DCM salvo hold | Harmony target and its Works lookup moved to the inspected beta auto-fire blocker | Author anti-ship-only predicate/postfix retained; metadata and native signature checks |
| Topography | Author 1.5.1 option fallback retained, remaining shoreline constant corrected; 1.5.0 recipe retained | Both captured versions checked, including all 65,536 DEM values; current PC capture already shows author map use |
| Pop-outs | Current captured Pop-Out image admitted alongside the older inspected version | Bindings and existing bridge tests; second monitor needs PC check |

World service is a profile record for a campaign/coalition across saves. It
does not write native commander or campaign saves. Meridian Accord requires
three completed manual battles; Iron Meridian requires ten. Theatre ribbons
require two battles with a position observed during battle and matching the
completed report. DCM's inspected `Scoring.Report` copies `Engagement.At` into
`BattleReport.At`; this is the timestamp used to match the observed position.
Older reports without position evidence count towards global service only.
Auto-resolves never earn manual service. Duplicate report keys do not add
progress. Unknown ledger formats remain read-only and are preserved.

Costs are catalogue estimates, not campaign-budget deductions. Fleet/shore
roster values exclude embarked aircraft, ground units, stores and cargo.
Combat totals retain the existing expenditure, destroyed-platform and lost-
store model. Completed reports without itemised SEST history remain visible
as missing coverage. Price gaps are marked rather than valued at zero.

## Next UI work

The strike tool currently uses its author's IMGUI window. R11 refines that
presentation and adds a summary; it is not a full Noesis migration. The next
coordinated UI pass should use the existing author timing/readiness model for:

1. A timing view that makes launch windows and arrival spread easier to read.
2. Clearer readiness and weapon/guidance notices beside each strike leg.
3. A shared cost/readiness summary across planner and campaign screens.
4. Logistics and replenishment status with verified quantities and units.
5. A unified battle debrief linking actual expenditure, losses and citations.

ROE, logistics, ASW, air-defence and strategic-airlift performance awards need
additional gameplay evidence. R11 does not infer those achievements from USD
spending or award them as a side effect of opening a panel.

## Release boundary

The private beta payload targets the 9 November 13:50 Brisbane capture of
0.8.7-261107, native SHA `499675cd…`; Runtime 1.6.0 and UI 1.4.9 are paired.
The canonical Workshop tree retains stable code and receives campaign/ribbon
data. The new Operations and strike code is a separate beta payload. No Steam
submission or GitHub push is included. Native rendering, save/load progression,
second-monitor behavior and stable-game acceptance remain PC checks.
