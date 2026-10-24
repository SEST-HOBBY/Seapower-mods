# Combat Cost Tracker compatibility — 20 October 2026

Updated 23 October 2026: SEST researched estimates, 31 more reviewed mappings
and the generated cost list (see "Researched estimates and the cost list").

Updated 24 October 2026: a second checked batch ships 66 more reviewed
mappings and 34 more researched estimates, and the research record now covers
every item that batch left unknown, including land units (see "Second batch").

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

New entries use one of three methods:

- An unambiguous existing catalog reference with the same basename and
  punctuation-normalized spelling. Variant letters, numbers and suffixes are
  retained; conflicting candidates are left unknown.
- An explicitly reviewed family/reference mapping in
  `integration/combat-costs/mappings.json`. Each output section names its
  source and explains the comparison. The source's two USD values are copied
  exactly, including blanks. A family comparison is an estimate, not a new
  class-specific contract price.
- A SEST researched estimate, also in `mappings.json`, for a unit the author
  catalog cannot price. It is SEST's own figure, not the author's, and its
  catalog section is preceded by comments naming the method, the year and
  every source (see below).

Examples include the actual RAN MH-60R, Australian Super Hornet, S-70B-2,
Apache, A-10C+, B-52H variants, conventional ARRW, selected Tomahawks,
Ticonderoga/Burke/Virginia fits and the Canberra/Juan Carlos design family.
No invented modernization surcharge is added. Historical reference years
remain the donor estimate's years, even when a scenario variant is newer.

The compiled `COST-COMPATIBILITY.txt` lists every emitted mapping, every
researched estimate with its method, year and sources, and the remaining SEST
gaps. `coverage.json` records static reference coverage for
historical and current modes separately. Carried stores are included in that
reference audit; it is not a count of objects the native expenditure report
will actually charge during a mission.

## Researched estimates and the cost list (23 October 2026)

The owner asked for a combat cost list covering everything in SEST. 104
unpriced items were researched and each figure was then checked
adversarially. Only rows the check confirmed or corrected are shipped: 31
become reviewed mappings and 25 become researched estimates. Refuted rows and
rows the check left unknown are not shipped. Neither is a mapping onto a
blank author entry (the J-36), because it would add nothing. Some sources
could not be read, because this environment's network policy blocked them
(proxy 403, DNS failures). No shipped price rests on such a page.

**The estimate form.** An entry in `mappings.json` with an `estimate` object
instead of a `source`:

```json
{
  "target": "tha_cvl_chakri_naruebet",
  "category": "CVL",
  "basis": "HTMS Chakri Naruebet: published ship cost US$285M (1993; ...)",
  "estimate": {
    "historical": "285000000", "historical_year": "1993",
    "historical_method": "published price",
    "current": "660000000", "current_year": "1993",
    "current_method": "CPI conversion",
    "note": "Current: 285,000,000 x 334.4 / 144.5 = 659,543,253, rounded"
  },
  "sources": [{"title": "HTMS Chakri Naruebet - Wikipedia", "url": "https://..."}]
}
```

`costs.estimate_fields` rejects an estimate unless all of the following hold:

- Every price it gives parses as positive USD, with no separators or
  exponents.
- Each given price has a four-digit year and a method. The methods are
  `published price`, `comparable recent purchase`, `documented replacement
  estimate`, `CPI conversion` and `model estimate`.
- It has a basis and at least one source with a title and a URL.
- It names no `source` catalog section. A figure copied from the catalog is a
  reviewed mapping and must stay one.
- A weapon or vessel estimate has a category of at most 20 characters.
- Every text field is one line, because it is rendered into INI comments.

One price may be left out, and it then stays unknown. The A320 and A330 ship
only a current price, because no service-entry price could be read. The
historical value follows the tracker's convention: rounded service-entry-era
USD, with the reference year recorded. The current value is explicit 2026
USD. The order of preference is a comparable recent purchase, then a
documented replacement estimate, then a CPI conversion; the source year and
method are recorded either way. Ships are priced fitted, without ammunition
or embarked aircraft.

**Provenance rules.**

- An author entry still wins. An estimate whose target later gains an
  author section is not emitted, even if that section is blank.
- A model estimate is a comparison, never a published price. The Redback,
  the KVLS-II HGV, the naval L-SAM and the Kraken K5 are model estimates.
- Purchase points and `ammo_prices.csv` scores are never USD.
- Each catalog section is preceded by `; SEST researched estimate, not a
  tracker author price: <basis>`, one line each for the historical and
  current method and year, a `; Note:` line with the working, and one
  `; Source:` line per page.

Researched items that are not shipped are kept in
`integration/combat-costs/research.json`, with the candidate figure, the
decision and why it was not shipped, and their sources.

**The list.** `docs/combat-costs/cost-list.md`, and `cost-list.csv` beside
it, are generated from the cost builder. Do not edit them. They cover:

- every weapon, vessel and aircraft SEST ships (winning owner `SEST_*`);
- every vessel and aircraft SEST_Campaign's missions and rosters field, read
  from the campaign pack's own output, not the dist;
- for each of these, the historical and current USD, the category, and
  where the price comes from: tracker catalog, inline in the unit file, SEST
  mapping, SEST researched estimate, or unknown with the reason;
- the land units SEST ships, marked "not priced: the tracker does not price
  land platforms";
- the gaps: what is still unknown and whether it was researched, then each
  researched but unshipped item with its candidate figures, why it was not
  shipped, and its sources;
- the next batch: every weapon that a fielded unit's file can load, in any
  of its offered fits, and every round inside a carried pod, that lacks a
  price. These are grouped as missiles, bombs, torpedoes, guns and
  projectiles, and rockets, then fuel tanks, containers, chaff, noisemakers
  and sonobuoys, with counts first.

SEST_Campaign builds after this pack, so `tools/build_all.py` writes the list
once every pack is built (`build_pack.py --list`). Run alone, `build_pack.py`
also writes it when the campaign's output exists. On 23 October 2026 the list
held 138 SEST weapons (129 priced), 339 SEST vessels (320), 37 SEST aircraft
(35), 163 fielded vessels (146), 139 fielded aircraft (116 with both prices,
2 more with a current price only), 27 land units, and 339 carried weapons
without a price.

### Second batch (24 October 2026)

A second batch of 102 weapons, ships and aircraft that SEST's campaigns carry
or field was researched and checked the same way. 100 rows ship:

- 66 reviewed mappings: 62 weapons, 2 vessels and 2 aircraft. One sets its own
  category: `plaaf_ls-500` is a guided bomb, so it takes `Bomb`, not its
  source's `Land Attack`.
- 34 researched estimates: 33 weapons (mostly torpedoes and Paveway bombs)
  and the Italian AV-8B Plus. The Mk 44 and Mk 46 family, the Sting Ray Mod 0
  and the Yu-6, Yu-9 and Yu-10 family ship a current price only.

The A320 and A330 rows are left out. They repeat the 23 October estimates and
add no historical price. No row's source entry was blank, and no row replaces
an author entry.

`research.json` now holds 377 items: every item the second check left
unknown, each with its candidate figure and the reason. 323 of them carry a
`rerun` note, because their research stopped when this session's web search
allowance ran out or a source host was blocked. They can be re-run. 89 items
are land units (kind `land`). They are kept for reference only, because the
tracker does not price land platforms; the cost list shows them under Gaps.

On 24 October 2026 the list held 138 SEST weapons (129 priced), 339 SEST
vessels (320), 37 SEST aircraft (35), 163 fielded vessels (148), 139 fielded
aircraft (119 with both prices, 2 more with a current price only), 27 land
units, and 256 carried weapons with a missing price (12 of them have a
current price only).

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

SEST MALICE retains the author's unknown AIM-424 prices. The fictional
Redback (`sest_agr-30`) carries a labelled model estimate since 23 October
2026: the AGM-114L Longbow Hellfire's catalog pair, 70,000 / 150,000, as a
seeker and role comparison, not a published price. Modern Supply and Anzac
are not priced from the old HMAS Supply and Battle-class Anzac entries.
Collins, Arafura and the Bay-class Choules also remain unpriced where no
defensible catalog match exists. A borrowed visual model alone is
insufficient evidence for a ship's cost.

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
neither setting, and the builder performs no inflation calculation: a
researched estimate's CPI conversion was done once, in the research, and is
recorded in its note. Currency/economy selection, overlay scale, position,
category order and visibility are retained.
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
5. Test MALICE: its unknown price should show as incomplete, rather than
   zero. Check the RAN frigate's FFG category if it is lost. A Redback shot
   should now add USD 70,000 (historical mode), its model estimate.
6. Change price mode only for a separate fresh comparison. A missing current
   value must remain unknown rather than borrow the historical estimate.

The Linux build can validate mappings, precedence, catalog syntax and source
fidelity. It cannot run Sea Power or establish the plugin's in-mission loss,
save/load or native `#!extend` behavior. Those acceptance checks remain on PC.
