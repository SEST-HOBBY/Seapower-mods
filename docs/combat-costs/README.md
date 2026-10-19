# Combat Cost Tracker compatibility — 20 October 2026

This private revision starts from the PC-verified `71bd3004` playtest. It adds
the two newly installed plugins to the canonical order and builds
`SEST_Combat_Costs` into the existing consolidated pack. Equipment performance,
loadouts, mission forces and campaign purchase-point prices are unchanged.

## Captured evidence

The supplied `SEST-cost-review-20261020-030948.zip` passed its ZIP CRC and all
19,971 recorded file hashes. It contains CombatCosts **0.7.1.0** and Formation
Manager's SeaPowerSquadPanel **0.2.16.0**. Their assembly hashes and the capture
commit are recorded in `data/combat-cost-capture.json`. DLLs are reviewed from
the private capture, not redistributed or modified by this compatibility pack.

Both Workshop IDs are selected in the saved load order. The captured process
logged that Weapon Costs was not enabled at startup; later selection does not
prove that its mission accounting was active. The formation plugin logged its
successful load and map-threshold attachment. Its in-game name is **Group Manager**. A full restart and new mission
are required for the next cost test. No gameplay success is inferred from
these initialization messages.

Four existing Workshop exports also differ from the repository baseline. Their
IDs and changed-file counts are recorded for separate review. This pricing
revision imports only the two new plugin text exports. Static coverage refers
to those exports plus the repository's existing equipment baseline and SEST
outputs, rather than a claim that every upstream update has been rebased.

## What the extension does

Three uniquely named files under `systems/` use the documented native
`#!extend` mechanism to add sections to `weaponcosts.ini`, `vesselcosts.ini`
and `aircraftcosts.ini`. The existing author catalogs remain the base. No
existing section, including an explicitly unpriced section, is replaced.

New mappings use one of two methods:

- An unambiguous existing catalog reference with the same basename and
  punctuation-normalized spelling. Variant letters, numbers and suffixes are
  retained; conflicting candidates are left unknown.
- An explicitly reviewed family/reference mapping in
  `integration/combat-costs/mappings.json`. Each output section names its
  source and explains the comparison. The source's two USD values are copied
  exactly, including blanks. A family comparison is an estimate, not a new
  class-specific contract price.

Examples include the actual RAN MH-60R, Australian Super Hornet, S-70B-2,
Apache, A-10C+, B-52H variants, conventional ARRW, selected Tomahawks,
Ticonderoga/Burke/Virginia fits and the Canberra/Juan Carlos design family.
No invented modernization surcharge is added. Historical reference years
remain the donor estimate's years, even when a scenario variant is newer.

The compiled `COST-COMPATIBILITY.txt` lists every emitted mapping and the
remaining SEST gaps. `coverage.json` records static reference coverage for
historical and current modes separately. Carried stores are included in that
reference audit; it is not a count of objects the native expenditure report
will actually charge during a mission.

## Price precedence and unknowns

The installed README and the DLL's `CostRules.ResolveField` agree on the
current precedence, which differs from the earlier Workshop description:

1. A per-field switch, such as `OverrideCurrentYearCost`, takes priority.
2. Next comes the entry's `OverrideInline` switch.
3. Next comes the catalog's `[Costs] OverrideInline` switch.
4. The default is **False**, so an inline equipment value is preferred.

A missing preferred key falls back to the other source for that field only.
An explicitly blank or invalid preferred price remains unknown. Zero means
explicitly free. `CurrentYearCost` never falls back to the historical price.
The extension changes none of these switches. The regression tests exercise
these differences, including blank values, zero and conflicting spellings.

SEST MALICE retains the author's unknown AIM-424 prices. Redback has no
supported USD price. Modern Supply and Anzac are not priced from the old
HMAS Supply and Battle-class Anzac entries. Collins, Arafura and the Bay-class
Choules also remain unpriced where no defensible catalog match exists. A
borrowed visual model alone is insufficient evidence for a ship's cost.

Useful display categories are still supplied for these gaps: Anzac's `FFH`
prefix becomes the supported `FFG` cost category, and unrecognized `AOR`
prefixes become `AO`. Unknown subtotals should retain their counts and `?`.
No missing equipment is silently made free.

The local `cache/ammo_prices.csv` is not used as a USD source. Native Task
Force requisition points are also unrelated to these dollar estimates.
Ship and airframe source estimates exclude separately counted ammunition
and embarked aircraft; those remain the tracker's own loss-accounting work.
Ground-platform loss pricing is outside this plugin's documented scope.

## Preserved settings

The capture uses historical prices (`UseCurrentYearCosts=False`) and labels
the independent current-price series `2026-08`. This extension changes
neither setting and performs no inflation calculation. Currency/economy
selection, overlay scale, position, category order and visibility are retained.
The captured weapon row order omits `Gun`, `Decoy` and `Other`; hidden categories
still contribute to totals under the author's rules.

## PC acceptance

1. Install with Sea Power closed and confirm the new `IN LINE` result. Both
   plugins should be enabled, with SEST first and Anchor Chain above the plugins.
2. Fully restart the game. Start a fresh mission; use F11 to show the tracker.
   Confirm the startup-disabled message is absent from the new session log.
3. Fire one known priced round at a time. AIM-260 uses its existing author
   section; test an ARRW and a mapped JDAM separately. Check per-unit amounts
   against `COST-COMPATIBILITY.txt` and the selected historical/current mode.
4. In a disposable mission, check a mapped aircraft loss and a ship loss.
   Remaining ammunition and embarked aircraft must be counted once, under
   the plugin's existing rules. Then save/load and check retained totals.
5. Test MALICE or Redback: their unknown prices should show as incomplete,
   rather than zero. Check the RAN frigate's FFG category if it is lost.
6. Change price mode only for a separate fresh comparison. A missing current
   value must remain unknown rather than borrow the historical estimate.

The Linux build can validate mappings, precedence, catalog syntax and source
fidelity. It cannot run Sea Power or establish the plugin's in-mission loss,
save/load or native `#!extend` behavior. Those acceptance checks remain on PC.
