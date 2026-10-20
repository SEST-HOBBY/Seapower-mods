# Combat Cost Tracker 0.6.0

Requires **AnchorChain**. Independent of AC Pack and DryDock.
Install `Weapon Costs` in `Sea Power_Data/StreamingAssets`, enable it in the mod manager, and restart.

**F11** toggles the translucent panel at the upper right. Player is left, Enemy right. Each side shows weapon expenditure, vessels lost by type, and a bold grand total. Ally and Neutral appear when used. F11 is reserved for the game's terrain redraw while its developer menu is open. F8 remains available for DryDock.

## Price settings

Edit `systems/combatcosts/config.ini`:

```ini
[Costs]
UseCurrentYearCosts=False
CurrentYear=2026-08
```

- `False`: use `WeaponCosts`, the rounded IOC-era USD estimate.
- `True`: use the explicit `CurrentYearCost` value, without automatic inflation. Prefer a comparable recent fitted-unit purchase price; otherwise use a documented replacement estimate, then CPI conversion as a fallback. Record the source year and method. Current prices may be lower than historical prices.
- Existing CPI-based entries remain purchasing-power estimates, not current procurement quotes; they have not all been replaced with market prices.
- `CurrentYear` labels the dollar period. Changing the label does not recalculate prices.
- Blank or invalid prices remain unknown. Zero explicitly means free.
- Missing current prices never fall back to historical prices.

The catalog is grouped **Euromod -> PLAN -> Basegame -> Other**. All populated values are approximate; family proxies and CPI backcasts are used where documented. All currently configured SAM and ASM references now have a price, using explicit comparison estimates where needed. All 62 catalog AIM-9/AIM-120 references also have prices; see [AAM-PRICE-UPDATE.md](AAM-PRICE-UPDATE.md). See [PRICE-SOURCES.md](PRICE-SOURCES.md) for coverage and sources. Inflation conversion is not a current procurement quote.

## Add or override prices

Create an INI in another enabled mod, for example `systems/my_weapon_costs.ini`:

```ini
#!extend systems/weaponcosts.ini
[my_missile]
Category=SAM
WeaponCosts=500000
CurrentYearCost=1200000
```

These are example values. Section names are ammunition filenames without `.ini`. Native mod order and INI precedence apply. Restart after editing.

Alternatively, add `WeaponCosts`, `CurrentYearCost` and `WeaponCostCategory` to the missile INI's `[General]` section. Inline values take precedence over the central list by default, independently for each price and category. Missing inline keys fall back to the list. See the priority switches below.

Categories are independent of `ammunition_names.ini`: `SAM`, `ASM`, `AAM`, `ARM`, `Land Attack`, `ASW`, `Ballistic`, `ATGM`, `Bomb`, `Gun`, `Decoy`, or another English label up to 20 characters. `Ignore` excludes a weapon. A multi-role missile uses one configured category regardless of its actual target.

`[WeaponCategories] Order` in `config.ini` sets both weapon row order and visibility. Categories omitted from this list are hidden, but their costs remain in totals. An empty `Order=` hides all category rows. All zero-value rows and subtotals are hidden independently for each side. `AlwaysShow` is retained for old configurations but no longer forces empty rows. Unknown values remain visible as `?`. Only `Grand total` is always shown. The catalog now includes 192 gun-ammunition references. Add `Gun` to `Order` if you want a separate visible row; omitted rows still enter totals. Torpedoes and unguided bombs remain incomplete.

## Price priority switches

Put optional switches in the central INI (`weaponcosts.ini`, `vesselcosts.ini` or `aircraftcosts.ini`). Each list is independent. Inline `[General]` values win by default. `#!extend` can change these switches and prices as usual.

```ini
[Costs]
OverrideInline=True

[civ_fv_sampan]
OverrideInline=False
OverrideCurrentYearCost=True
CurrentYearCost=1000
```

This makes the list override inline values generally, lets the Sampan use inline values, but forces its listed current price to USD1000. To override just one complete entry, set `OverrideInline=True` in that entry while leaving the list default False.

Optional per-entry switches: `OverrideWeaponCosts`, `OverrideVesselCosts` or `OverrideAircraftCosts` for the historical price; `OverrideCurrentYearCost` for the current price; `OverrideCategory` for weapon/vessel classification. Each accepts `True` or `False`.

Precedence: **field switch > entry OverrideInline > list [Costs] OverrideInline > False**. `True` prefers the list, `False` prefers inline. A missing preferred value falls back to the other source for that field only. An explicit blank or invalid preferred price remains unknown; zero means free. Categories use their existing native fallback when the selected category is blank. Current prices never fall back to historical prices.

## Currency and economy displays

Four separate files under `systems/combatcosts/`:

- `config.ini`: price mode, overlay, category visibility and display defaults.
- `currencies.ini`: annual-average currency units per USD, by support year.
- `economies.ini`: nominal annual GDP in USD, by country/economy and support year.
- `misc.ini`: USD per comparison unit, by support year (Bitcoin, gold, oil and other comparisons).

All cost catalogs and inline equipment prices remain in USD. The currency dropdown has two columns: **Currencies** on the left and **Misc** on the right, with a shared search and independent scrolling. Currency defaults to USD. The mode button switches between the selected currency/Misc comparison and the independently selected economy. Currency mode multiplies USD by the selected exchange rate. Misc divides USD by the selected unit price. Economy mode divides USD by the selected GDP: USD10 million / USD100 million = `0.1 x GDP`. Currency amounts are rounded to whole units; tiny positive amounts show `<1`. All fractional displays use plain decimals.

```ini
[Display]
Mode=Currency
Currency=USD
Misc=
Economy=USA
ReferenceYear=Auto
ReferenceYears=1960,1970,1980,1990,2000,2010,2020,2025
```

`ReferenceYear=Auto` uses the newest service-entry year of an initial mission unit's actual variant, across all sides. Entry years above 2050 are ignored for year selection only; those units' costs are still tracked. The closest listed support year is selected, rounding ties upward: 1984 -> 1980, 1985/1987 -> 1990. Dates outside the series use its nearest endpoint. Alternatively set `ReferenceYear=1980` (or another listed year). The same year applies to currency and GDP. The panel displays the reference year and initial service year.

The automatic year is fixed once, after the initial mission finishes loading, and saved with the mission. Reinforcements and losses never change it. Use the Year dropdown to select a data year manually or return to the fixed Auto year. Manual selections are saved too. Older saves use their saved observed maximum and remaining units once. No detectable service year means unavailable conversion data until a manual reference year is chosen; USD still works. GDP amounts are multiples, for example `0.1 x GDP` or `243 x GDP`. GDP values use plain decimal notation, rounded to the first nonzero fractional place: `0.101` becomes `0.1`, `0.001113` becomes `0.001`, and `8.5` stays `8.5`. Whole numbers have no decimal suffix. If a unit has no ServiceDate in its selected variant or Default section, it cannot supply an automatic service year; choose the reference year manually if none of the initial units has a valid date.

Missing data for the selected country/currency/Misc item and exact year shows `?` and `unavailable`; the corresponding years are greyed out in the Year dropdown. The mod never substitutes a different country, year, zero, or predecessor currency. EUR is unavailable before 1999. DEM, FRF and ITL cover pre-euro support years. All display modes use the selected IOC/current cost basis as supplied; they do not inflate prices to the reference year. This is a rough game comparison, not an estimate of government spending capacity. See [ECONOMY-SOURCES.md](ECONOMY-SOURCES.md) for coverage and sources.

Set `Misc=RTX5090` (or another Misc identifier) for a persistent comparison default; leave it blank for the configured Currency. Selecting a real currency in the dropdown clears the active Misc selection. The mode button retains the last currency/Misc selection while showing GDP.

Every Misc item uses the same `PriceYYYY` fields. Gold, oil, Bitcoin, Big Macs, beer and US working years have yearly values. Beer before 2000 is estimated from the beer producer-price index; US work-years use the SSA national average wage series, including a marked 2025 estimate. Fixed benchmarks such as RTX 5090 repeat the same price in every support year, so they also work before the product existed. To add or override an item:

```ini
#!extend systems/combatcosts/misc.ini
[Misc_RTX5090]
Name=RTX 5090
ShortName=5090
Unit=RTX 5090s
DecimalPlaces=0
Basis=fixed 2025 launch MSRP
Price1960=1999
Price1970=1999
Price1980=1999
Price1990=1999
Price2000=1999
Price2010=1999
Price2020=1999
Price2025=1999
```

Prices are USD per one displayed unit, using a decimal point and no thousands separators. `DecimalPlaces=0` displays whole items rounded down; positive fractions below one show `<1`. Values 1-8 allow fractional units. Missing, zero or invalid prices mean unavailable. No item-specific year restrictions exist in code. Sources, dates and explicit author benchmarks are documented in [MISC-SOURCES.md](MISC-SOURCES.md).

Other mods can extend each file, for example:

```ini
#!extend systems/combatcosts/currencies.ini
[Currency_EUR]
Rate1980=
Rate2020=0.8755
```

```ini
#!extend systems/combatcosts/economies.ini
[Economy_USA]
Name=United States
GDP1980=2857307000000
```

These demonstrate the schema; use your desired researched values. Add support years to `ReferenceYears` when adding another year. Historical countries need their own identifiers and data; Russia is not an alias for the Soviet Union.

`[Overlay] ShowRatios=True` shows Player : Enemy ratios beside weapon, vessel, aircraft and grand totals. The grand ratio is bold. Ratios use unrounded totals; common currency/GDP conversion cancels out. Incomplete prices or unavailable display data show `?`. Both sides zero hides the ratio; one side zero gives `0:1` or `1:0`. A hidden subtotal remains hidden on that side while its opposite total stays aligned.

## Overlay

Under `[Overlay]` in `config.ini`: `ToggleKey=F11`, `VisibleOnStart=True`, `BackgroundAlpha=0.38`, `Top=110`, `Right=16`, `Scale=1`. Positions are pixels at scale 1; scale range is 0.6-2. Increase `Top` to move below the time controls. The panel fits smaller screens. Its header buttons open searchable currency/economy dropdowns; the mode button switches the display. Dropdown choices last for this session; edit `[Display]` for persistent defaults.

Missing prices show `?` or `+ ?`, with `(incomplete: 3x SAM unpriced)` below the affected total. Only known prices enter totals. Exact missing ammunition references are logged once per mission.

Counts come from the game's existing weapons-spent report, grouped by mission side. They include retained native save/load statistics and refresh twice per second while visible. Native reporting limits, including modded submunitions, still apply.

## Vessel losses

Edit `systems/vesselcosts.ini`, or extend it from another mod:

```ini
#!extend systems/vesselcosts.ini
[my_destroyer]
Category=DDG
VesselCosts=300000000
CurrentYearCost=900000000
```

Example values only. Use the vessel filename without `.ini`. Alternatively, add `VesselCosts`, `CurrentYearCost` and `VesselCostCategory=DDG` under `[General]` in its vessel INI. Inline values take precedence by default; missing keys fall back to the central list. The priority switches below can force list values.

Use USD for the fitted ship, **excluding loaded ammunition and embarked aircraft**. The shared `UseCurrentYearCosts` switch in `systems/combatcosts/config.ini` applies to all three catalogs. Categories such as `DDG`, `CVN` and `SSN` are configured in `vesselcosts.ini`; `[Categories] Order` controls their order and visibility. Only used and listed vessel categories appear; omitted categories still enter totals. Filename classification is the fallback for unlisted ships; runtime classification does not depend on language files.

- **Weapon total:** ammunition already expended.
- **Aircraft (onboard):** lost helicopters and airplanes still aboard, with their count and combined airframe value.
- **Vessel total:** lost ships plus ammunition and aircraft remaining aboard when they were registered as destroyed.
- **Grand total:** Weapon total + Vessel total. Surviving ships are excluded.

The mod captures inventories even when the overlay is hidden, and adds `WeaponCostsLostStoresV1` to each taskforce's save section. Native statistics remain unchanged. Older saves retain their recorded hull losses but cannot recover already-lost inventories; these show `(incomplete: ... inventories unavailable)`. Restart after changing prices or installing the mod.

Losses follow the game's destroyed-unit report, which can register a ship before its wreck physically sinks. Crew, fuel and repair costs are outside this total. Flight-deck stores represented by ammunition points or pooled categories cannot be assigned exact rounds and show `air-group stores unavailable`. Known launcher/magazine ammunition is still included. Missing prices and inventories never silently become free.

The vessel catalog is grouped Euromod, PLAN, Basegame, Other. It prices 936 of 941 references, including all major combatant categories, all other hulls at least 80 m long, and all 218 Russian/Soviet/PLAN references. `model estimate` marks an author comparison with another class; it is not a published price for that ship. Concept ships use a donor/reference year. Rounded estimates and sources are listed in [VESSEL-PRICE-SOURCES.md](VESSEL-PRICE-SOURCES.md). Remaining blank entries are unknown.

## Onboard aircraft

Edit `systems/aircraftcosts.ini`, or extend it:

```ini
#!extend systems/aircraftcosts.ini
[my_helicopter]
AircraftCosts=5000000
CurrentYearCost=15000000
```

Example values only. Use the aircraft filename without `.ini`. Alternatively put `AircraftCosts` and `CurrentYearCost` under `[General]` in its aircraft INI. Inline values take precedence by default; missing keys fall back to the central list. The same priority switches apply. Use airframe and installed equipment cost, excluding loaded weapons. The shared price toggle applies.

The mod counts aircraft in the hangar, awaiting launch, cooling down after recovery, and non-airborne machines in launch/recovery tasks. Already flying aircraft are excluded. This row only covers machines lost with a ship, not aircraft shot down separately. Captured counts survive saving and loading; saves from before 0.4 cannot reconstruct aircraft already lost and show an incomplete-inventory note.

The catalog prices 340 of 696 aircraft references, including common naval helicopters and carrier airplanes. Most values are coarse model estimates; see [AIRCRAFT-PRICE-SOURCES.md](AIRCRAFT-PRICE-SOURCES.md). Unknown prices retain the aircraft count and mark the subtotal incomplete.

One DLL uses runtime capability detection. Release and the available stable-beta snapshot were checked offline; gameplay in both builds has not yet been tested.

## Price expansion (24 September 2026)

The catalogs contain 259 priced SAM references, 293 ASM references and 192 gun-ammunition references. Your existing categories and display settings are retained. Many new prices are coarse author comparison estimates, explicitly labeled in the INIs. Gun prices are per fired round, with separate models for guided and programmable ammunition. Laser/test effects and the nuclear 3BV3 shell remain unpriced.

See [WEAPON-PRICE-EXPANSION.md](WEAPON-PRICE-EXPANSION.md) and [VESSEL-PRICE-EXPANSION.md](VESSEL-PRICE-EXPANSION.md) for new sources and estimate bases. Published anchors include Navy ammunition budgets, UK/French parliamentary ship figures, CRS submarine/carrier estimates and MP-IDSA missile estimates. Estimates are not confirmed class-specific contract prices.

## Aircraft losses in flight

Aircraft lost while flying appear under `Aircraft lost (in flight)`, split into `Planes` and `Helicopters`. `Aircraft total` includes the airframe and its remaining individually counted ammunition. It uses `systems/aircraftcosts.ini` or inline `AircraftCosts` / `CurrentYearCost` in `[General]`, just like onboard aircraft. Surviving aircraft have no loss cost. Aircraft lost aboard a sinking vessel stay in `Aircraft (onboard)` and `Vessel total`; they are not added again as airborne losses.

Grand total = expended weapons + vessel loss total + airborne aircraft loss total. Air losses are captured even while the overlay is hidden and saved with the mission. Earlier saves cannot reliably distinguish losses in flight from losses on deck; unclassified earlier losses are marked incomplete rather than assigned invented costs. Start a new mission for complete capture.

Version 0.5.0 was checked offline against the installed release and available stable-beta assembly snapshot using the same DLL. It has not been tested in a running mission in this update.

Version 0.5.1 uses `CombatCosts.dll` and the overlay title `COMBAT COSTS`. Remove the old `WeaponCosts.dll` when updating; keep only one runtime DLL. Configuration filenames and save data remain unchanged.

Civilian fishing boats, the Sampan and remaining merchant entries now have estimates. See [CIVILIAN-PRICE-SOURCES.md](CIVILIAN-PRICE-SOURCES.md) for reference years, comparison sources and limitations.

## Additional price coverage (24 September 2026)

684 previously unpriced references now have researched reference prices or marked family estimates. Existing prices and category edits are retained; this update performs no inflation calculation. See [PRICE-GAPS-20260924.md](PRICE-GAPS-20260924.md) for scope, source years and remaining gaps.

## Number formatting

The overlay uses English number formatting: `157,600,000 USD`, `1,234.5 US work-years` and `0.000001 x GDP`. Commas group thousands; dots separate decimals, regardless of system language. INI prices still use a decimal point without thousands separators.
