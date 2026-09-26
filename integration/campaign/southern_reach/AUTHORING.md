# Authoring a Southern Reach mission module

Read this whole file before writing a mission. It is the contract between a
mission module and the builder that turns it into a Sea Power file, and every
rule in it is enforced by `build_pack.py` - a mission that breaks one does not
build. The design of each mission is in
`docs/campaigns/southern-reach/campaign-bible.md` (§6-§7); this file is how to
turn a card there into a module here.

## The one command

    SR_ALLOW_MISSING=1 python3 integration/campaign/build_pack.py --dry-run --campaign southern-reach --only SR03

Dry-run: nothing is written. `--only` takes mission codes (`SR03,TS10A`).
`SR_ALLOW_MISSING=1` lets the package load while other modules are still
unwritten. Read every line the builder prints for your mission: the
`gap`/`reach` figures, the "position(s) proved against the coastline" list,
the recovery notes, the closure notes, and any `geometry failed:` block.

Never run it without `--dry-run`. Never edit anything but your own module(s):
not `tables.py`, `lore.py`, `__init__.py`, `build_pack.py`, `coast.py`,
`campaign_data.py` or another author's module. If a builder gate is wrong,
say so in your report; do not work around it.

To check a coordinate before you commit to it:

    python3 -c "import sys; sys.path.insert(0,'integration/campaign'); from coast import coast; c=coast(); print(c.check(-43.12, 147.62))"

`(False, 3.1)` means on water, 3.1 NM from the nearest coast.

## The module

`integration/campaign/southern_reach/<code>_<slug>.py` - the file name is in
`tables.MODULES`; use exactly that name. It exports one dict, `MISSION`.
`sr01_southern_departure.py` is the worked example; copy its shape.

```python
from campaign_data import U, F, S, HELO, RECON, CAP, STRIKE

MISSION = dict(
    code="SR03", series="Southern Reach", seq="SOUTHERN REACH  ·  MISSION 3",
    group="core", num="03", key="Search Datum", place="The southern route",
    ...
)
```

Chapter B modules use `series="Tasman Shield"`, `seq="TASMAN SHIELD  ·  MISSION n"`,
codes `TS01`..`TS12`; the optional pair uses `group="optional"`, `num="10A"`/`"10B"`,
`seq="TASMAN SHIELD  ·  OPTIONAL"`, `expires_after="Approaches"` and `special=`
(see below). `date`, `points`, `generation` and `anchor` come from
`tables.CALENDAR` and are checked: write them in your module exactly as the
calendar has them (the package fills them in either way).

### Keys, in the order the example uses them

| key | what it is |
|---|---|
| `code`, `series`, `seq`, `group`, `num`, `key`, `place` | identity. `key` is the title; `place` the subtitle (a sea area, "Storm Bay, Tasmania") |
| `intro` | one or two sentences on the campaign map card |
| `sender` | who signs the briefing (bible §2 cast) |
| `intent` | commander's intent, in that person's voice, 3-6 sentences |
| `date`, `time`, `sea`, `clouds`, `wind` | `time=(h, m)` local; `sea` 0-8 (Southern Ocean 4-6; coastal 2-4); `clouds` one of `Clear`, `Scattered_1`, `Scattered_2`, `Broken_2`, `Broken_3`, `Overcast`; `wind` a compass point |
| `difficulty` | 1-5, the mission panel's stars |
| `minutes` | the clock. The main objective fails when it runs out |
| `centre` | `(lat, lon)`; every unit's position is relative to it. Keep every unit within ~250 NM of it except far bases |
| `blue_nation`, `red_nation` | `"Australia"`, `"China"` or `"Russia"` |
| `brief` | the situation, 3-4 paragraphs separated by `"\\n\\n"` (the two-character escape, as in the example). Explain the assigned forces, assessed threats and orders. Describe a vessel's operational role; document substitute models in build notes rather than contact names or dialogue |
| `forces` | one paragraph: own, allocated, neutral, opposing |
| `objectives` | list of `(id, text, "completed,failed,StatusAtEnd[,Main][,Hidden]")`. The main objective carries `,Main`; `Fail` at end only on an objective something can complete (the victory, a classify/arrive/destroy resolver); protect/neutral objectives end `Complete`; an optional task is `"n,0,None"` |
| `victory` | see below |
| `fatal` | list of `F(objective, [station refs], minimum)` - losses that end the mission and fail that objective. `F("Cargo")` with no units takes them from a protect/survive resolver |
| `neutral_objective` | the objective the neutral-loss rule fails (destroying any neutral ends the mission) |
| `win`, `lose`, `timeout` | the three end texts |
| `stations` | `name: S(lat, lon, label, heading=, alt=)`; a coastal station is `dict(S(...), coastal=True)` |
| `units` | list of `U(...)` |
| `resolve` | every objective id -> its predicate (below) |
| `declares` | campaign variables this mission WRITES |
| `window` | the service window and air tasking rows (below) |
| `role` | the escalation budget: `opening`, `patrol`, `recon`, `escort`, `logistics`, `strike`, `fleet` |
| optional | `special` (a note on the campaign map), `reveal_if`, `reveals`, `flags`, `support_loss`, `discoveries`, `detached`, `force_loss`, `neutral_limit`, `expires_after`, `snap_limit` |

### Units: `U(side, mod, type, station, **kw)`

`side` is `"blue"`, `"red"` or `"neutral"`. `mod` is the catalog id of the mod
the unit is there to exercise - take it from the table at the end of this
file; the builder refuses a unit whose stated mod the game would not read.
`type` is the unit id. Keyword arguments:

- `name="..."` - the NameOverride the player sees. Never on the anchor ship
  (it is the player's own hull) and never on a slot-tagged aircraft.
- `variant="VariantN"`, `squadron="SquadronN"`, `loadout="Fit"` - must exist in
  the winning file (the table lists them). A P-8 with no `loadout` flies ASW
  because the file offers no Default; say `loadout="ASW"` or `"AntiShip"`.
- `weapons="Tight"|"Hold"|"Free"` (default Free). Merchants and auxiliaries
  that carry guns (`ran_ms_*`, `anl_*`) are always `Hold`. An identification
  mission's player units are `Tight`.
- `alt=feet` for aircraft (overrides the station's); `depth="belowlayer"|"periscope"|"shallow"|0` for submarines and the whale.
- `route=[(lat, lon, alt_or_depth), ...]`, `telegraph=1..5` (2 slow, 3 cruise; 1 is a damaged hull). Every waypoint of a vessel or submarine is checked against the coastline.
- `loop=True` on a routed aircraft flies the route until the clock runs out (`|Loop` after the last waypoint, stock's own form). Without it an aircraft that reaches its last waypoint circles there: a racetrack written as its two ends three times over is half an hour of a Poseidon's cruise. A patrol, a barrier or an AEW orbit that must last the mission loops; a ship, an unrouted aircraft or an airliner may not.
- `radars="False"` starts a unit with its radars off. Every submarine in the stock missions starts that way; a boat whose mission is not to be classified must.
- `snap="sea"` on a LandUnit that belongs in water (a rig). `coastal=True` on a station puts each hull there through the per-unit sea check instead of the 2 NM offshore rule (an anchorage, a port).
- `slot="HeloRecon"|"Recon"|"CAP"|"Attack"` - an air-tasking cockpit (below).
- `spawn_if=("Variable", "IsFalse")` - the unit exists only when the variable was never set. `IsFalse` is the only attested form.
- `nation="australia"` on RAAF bases, `nation="NewZealand"` on RNZAF bases and New Zealand airfields - the game's own key, no space (`language_en/nations.ini`); "New Zealand" with a space shows no flag.
- `no_neutral_penalty=True` exempts a neutral from the neutral-loss rule (a range target). Do not use it here.
- `independent=True` on a player hull that sails unescorted on purpose: the closure gate does not measure its distance to an escort (below).

### Stations and geometry - the coastline gate

Every mission here is `geography="coast"` (the package sets it). The builder
proves each position against `geo/southern_theatre_coast.json`:

- an offshore station must be on water **2 NM or more** from any coast;
- a `coastal=True` station, and a `snap="sea"` unit, must be on water (any distance);
- a land unit must be ashore at its authored coordinates - use the real ones (list below);
- every route waypoint of a ship or boat must be on water 0.5 NM or more from the coast;
- every trigger area centre (the arrival box, a stage area, an `arrive` resolver) must be on water 1 NM or more from the coast.

Hulls at one offshore station form line abreast 0.6 NM apart on the station's
beam; at a coastal station 0.4 NM apart. Aircraft at one station stack 3 NM
apart. Give every dissimilar aircraft its own station (a helicopter at 500 ft
does not fly in a Vic with a Poseidon at 15,000).

### Victory

```python
victory=dict(kind="arrive", station="convoy", min_units=3, objective="Convoy",
             transit=12,                      # the slowest hull's knots, if below 18
             also=[dict(units=["convoy#1"], min_units=1)],   # AND this one
             after=dict(kind="classify", units="shadow", min_units=1, sets="SRnnVar",
                        intel="...")),        # a stage that must fire first
             sets="SRnnVar")                  # a variable the win writes
MISSION["victory"]["bearing"], MISSION["victory"]["radius"] = 170, 12
```

- `kind="arrive"` with `bearing`/`radius`: the builder solves the box on that
  bearing at a distance the named units can reach in 75% of the clock at a
  conservative speed (18 kn ships, or `transit=`; 10 kn submarines; 120 kn
  helicopters; 300 kn aircraft), and none of `min_units` may start inside it.
  With `at=(lat, lon)` instead of a bearing the box is where you put it (an
  anchorage, a port approach) and the same reachability check applies.
- Two groups that must share one box (Tasman Crossing) cannot sail in line
  ahead: the trailing group can never reach a box the leading group can in
  the clock. Put them abeam of the track, 15 NM either side, and author the
  box 20 NM ahead of the escort; each group is then 25 NM from it.
- `kind="destroy"` with `stations=["red_sub"]`, `min_units=1`.
- `also=` terms are ANDed onto the win condition, each one of three kinds:
  `dict(units=[...], min_units=n)` - those units in the box too (`at=`,
  `radius=` for a box of their own); `dict(after_minutes=n)` - not before
  minute n; `dict(kind="destroyed", units=[...], min_units=n)` - and those
  units are gone. A kind, or a key the term's kind does not read, stops the
  build; so does a term no win can meet - no units, a `min_units` above the
  count, a minute at or past the mission's clock, or `destroyed` on the
  player's own units.
- `after=` stages: `kind="classify"` (UnitClassified on those units) or
  `kind="area"` with `at=`/`at_unit=`, `radius=`, `min_units=`, and optionally
  `after_minutes=N` (the units must be inside the area when the clock reaches
  N minutes - the service-window shape). `sets=` writes a variable when the
  stage fires; `intel=` is the message.
- A station reference is `"name"` (every unit there) or `"name#2"` (the second
  unit placed there, in `units` order).

### Resolvers

```python
resolve={"Convoy": "victory",                   # completed by the victory trigger
         "Neutrals": "neutral",                 # failed by the neutral-loss trigger
         "Flagship": ("protect", "escort"),     # fails when any unit at the station is lost
         "Group": ("survive", "jmsdf"),         # fails when ALL are lost
         "Restraint": ("spare", "tender"),      # fails if the player destroys any of these
         "Boat": ("destroy", "red_sub", 1),     # completes on n destroyed
         "Lift": ("arrive", "lift", (lat, lon), radius, n),
         "Identify": ("classify", "shadow", 1, "SR01ShadowNamed"),  # completes on classify; 4th item writes a variable
         "Unseen": ("unseen", "boat")}          # fails if the ENEMY classifies any of these player units
```

Every objective needs one. `unseen` is stock's `UnitClassified` with
`Condition_Taskforce=Taskforce2` on the player's own units (Operation Polar
Fury 1985 Trigger5). It measures classification, not detection, and only
ever fails, so its objective ends `Complete`. It names stations only and
fails on the first unit classified; there is no count. `F("Unseen",
kind="unseen")` ends the mission on it; a fatal entry of that kind takes its
units from the `unseen` resolver, as a loss takes them from `protect`, and
its `minimum=` runs from 1 to the number it watches. A `classify` resolver's station may also be a
list of refs (`["network#1", "network#4", "network#5"]`) when the objective
names particular hulls inside a larger formation. `declares=[...]` must list every variable the
mission writes (in a resolver, a stage `sets`, a victory `sets`, a `flags`
entry or a `support_loss` `sets`).

### Consequences

- `reveal_if=[dict(variable="SR01ShadowNamed", units=["shadow"], level="Classify"|"Identify", intel="...")]` - reveals those units at start if the variable was set (VariableCheck).
- `flags=[dict(name="SR07AkulaSunk", units=["red_sub"], intel="...")]` - sets the variable when the unit is destroyed.
- `support_loss=[dict(asset="Derwent Spirit", units=["convoy#2"], objective="Tanker", sets="SR09TankerLost", intel="...")]` - an intel line (and a fail, and a variable) when a support asset is lost.
- `reveals={"Picture": dict(units=[...], level="Identify", seconds=-1, intel="...")}` - the pay-off of a classify objective: reveal what it was screening.

### The window and Air Tasking

```python
window=dict(buy=True, repair=True, rearm=True,
            allow=["ran_ffh_anzac", "ran_ddg_hobart", "usn_mh-60r", "usn_p8", "raaf_mq-4c_triton"],
            flights=[HELO, RECON], situation="...", detachment=True,
            rearm_if=("SR04ServiceHeld", "IsTrue"), airbase_prep=True)
```

Use the bible's §4 table for each mission's buy/repair/rearm and rows. `allow`
names roster units (`tables.ROSTER`); the variants are taken from the roster.
Blank-generation missions (SR02, SR05, TS05) have `window=dict()` and no slots.

A row needs a cockpit: one **unnamed** unit per row with `slot=` set to the
row's label, placed where the purchased aircraft should start. The builder
counts the cockpits into the row. The rows and what fills them:

| row | label | filter | cockpit unit | put the cockpit... |
|---|---|---|---|---|
| `HELO` | HeloRecon | SAR | `usn_mh-60r` (mod `us-navy-2027`) | beside the anchor ship, 500-2,000 ft, within 150 NM of a deck |
| `RECON` | Recon | MPA/ASW/ESM/AEW | `usn_p8` (`p-8-poseidon`, `loadout="ASW"`) | at a patrol station; every roster aircraft the filter matches (P-8, Wedgetail, Triton **and the MH-60R**, which is ASW/MPA) must have a compatible field or deck within its own radius - so keep the Recon cockpit within ~150 NM of the anchor ship's deck and within 1,080 NM of a field |
| `CAP` | CAP | Fighter | two `raaf_f-35a` (`SEST_RAAF_F-35A_JATM`) | a CAP station within 547 NM of a placed RAAF field (F-35A), 506 NM (F/A-18F, EA-18G) |
| `STRIKE` | Attack | Bomber/SEAD | two `usn_fa-18f_blk3` or `usn_ea-18g` (`SEST_Growler_NGJ_MALICE`) | within 506 NM of a field; the P-8 matches this filter too (1,080) |

A slot-tagged unit may not be named by any objective, trigger or `fatal`.
Aircraft an objective depends on are fixed, named units instead.

Every player aircraft - fixed or cockpit - must have a compatible blue field
or deck within 40% of its range, or the build fails and says which. Place the
field as a blue land unit at its real coordinates (below). A helicopter takes
the anchor's deck. Red and neutral aircraft with no field fly on unlimited
fuel (the engine's rule) and the briefing should say why they can.

### Roles and the reach gate

| role | red combat units | red may not start closer than | red must be able to reach blue |
|---|---|---|---|
| opening | ≤ 3 | 12 NM | yes |
| patrol | ≤ 4 | 8 NM | no |
| recon | ≤ 5 | 10 NM | yes |
| escort | ≤ 6 | 6 NM | yes |
| logistics | ≤ 6 | 5 NM | yes |
| strike | ≤ 8 | 6 NM | yes |
| fleet | ≥ 8 | 15 NM | yes |

"Combat" is the unit's own `[AI] Role` - an AEW helicopter, a collector, a
tender or a transport does not count. "Reach" is the longest round it carries
plus what it can move in the clock (24 kn ships, 300 kn aircraft): the
mission fails the gate if the closest red unit still cannot touch the nearest
blue one. A `destroy` victory fails the build if nothing blue can reach the
target even after steaming. The standoff distance does not apply to a red
unit at `weapons="Hold"` whose every role is a known non-combat one (an armed
coaster in company, `Role=Spy`; the list is the builder's `NONCOMBAT_HINT`):
it will not open the engagement. A role the list does not name counts as one
that fights - `usn_ssgn_ohio` declares only `SSGN`.

The closure check also refuses a protected hull further from its nearest
armed escort than the escort can steam in the clock (24 kn for a ship, 10 kn
for an armed submarine, which counts as an escort), and *reports* (does not
fail) a neutral more than 35 NM from the protected ships and pointed away, or
a red unit with no route pointed away outside its reach - set dressing. Route
the traffic; point the threat. A player hull that sails unescorted on purpose
takes `independent=True` and is not measured.

### Writing

The voice is Southern Watch's: short, concrete, Australian, with the rule of
engagement said plainly. Player-facing prose and contact names do not carry
fiction banners, stand-in tags, point prices or development terminology.
Technical limitations and substitute models belong in the build notes.
Intelligence reports distinguish the source, observation age, assessed identity
and current contact. Satellite imagery cues a search; do not describe it as
continuous tracking or as a submerged-submarine firing solution. A saved
classification can support correlation without proving the contact's present
course or depth. Match every outcome line to the predicate that displays it.
Every neutral
has an origin and a destination and a route that shows it. No real company
names; fictional ship names with a New Zealand or Tasmanian flavour where the
water is theirs. Callsigns: Bluefin (RAAF P-8), Kiwi (RNZAF P-8), Sentry
(Triton), Wedgetail, Vigilant (F-35A). Contact names: red submarines VICTOR
(Akula), SIERRA-TWO (Yasen), ROMEO (093B), TANGO (039C), KILO (Kilo); the collector is
*Nan Hai 27*, the AMS tender *MV Austral Compliance*, the Russian tender *RV
Akademik Fersman*, the cargo/research ship *RSV Southern Endeavour*,
Santos's ship *MV Coral Pioneer*, the coaster *MT Derwent
Spirit*.

## Verified coordinates

Land units (blue fields; `nation=` as shown):

| unit | name | lat, lon |
|---|---|---|
| `airbase_raaf_edinburgh` | RAAF Base Edinburgh | −34.703, 138.622 (`nation="australia"`) |
| `airbase_raaf_east_sale` | RAAF Base East Sale | −38.099, 147.149 |
| `airbase_raaf_williamtown` | RAAF Base Williamtown | −32.795, 151.834 |
| `airbase_rnzaf_ohakea` | RNZAF Base Ohakea | −40.206, 175.388 (`nation="NewZealand"`) |
| `airbase_rnzaf_auckland` | RNZAF Base Auckland (Whenuapai) | −36.788, 174.630 (`nation="NewZealand"`) |
| `airfield_small_1` | Hobart Airport | −42.836, 147.510 |
| `airfield_small_1` | Christchurch International | −43.489, 172.532 |
| `airfield_small_1` | Invercargill Airport | −46.412, 168.313 |
| `civ_radiostation` | Macquarie Island station (neutral) | −54.499, 158.937 |

Mission centres (all on water; distance to the nearest coast in brackets):
SR02 −50.3, 162.8 (122) · SR03 −52.0, 140.0 (open) · SR04 −54.3, 158.3 (24; Buckles Bay anchorage −54.50, 158.99, 1 NM, `coastal=True`; withdrawal line −54.05, 158.50) · SR05 −56.0, 148.0 (open) · SR06 −51.5, 165.0 (51) · SR07 −57.5, 152.0 (275) · SR08 −43.7, 173.5 (17; Lyttelton approach −43.55, 172.90, 4 NM; Pegasus Bay −43.40, 173.10) · SR09 −48.5, 137.0 (open) · SR10 −60.0, 118.0 (375) · SR11 −55.5, 128.0 (open) · SR12 −40.5, 151.5 (138) · TS01 −46.1, 165.9 (25; Puysegur −46.30, 166.40) · TS02 −41.55, 174.45 (12.6; Cloudy Bay −41.50, 174.25; off Oteranga −41.35, 174.55; Cape Campbell −41.70, 174.50; Wellington approach −41.42, 174.75 needs checking) · TS03 −44.0, 178.3 (190; nothing east of 179.9) · TS04 −38.5, 158.5 (open) · TS05 −36.5, 160.5 (300) · TS06 −39.3, 147.0 (18; rigs −38.55, 148.20 and −38.60, 147.85; Wilsons Promontory south −39.35, 146.45; west of Flinders −39.90, 147.50) · TS07 −36.0, 152.5 (98; Sydney Heads approach −33.85, 151.55) · TS08 −35.5, 132.5 (139) · TS09 −38.6, 140.5 (33; Portland approach −38.6, 141.6) · TS10A −36.45, 175.05 (7; Colville Channel −36.20, 175.25; Tiritiri −36.60, 174.95; Rangitoto approach −36.72, 174.90 needs checking) · TS10B −35.15, 137.9 (7; Backstairs Passage −35.70, 138.10; Outer Harbor approach −34.75, 138.35) · TS11 −39.5, 151.0 (124) · TS12 −40.5, 155.5 (310).

## Units and the mod to attribute them to

The `mod` column is what goes in `U()`. "(SW)" means Southern Watch already
places it with that attribution; the rest were resolved from the winning
files on 24 September 2026. Range is the airframe's; radius 40% of it.

| unit | type | mod for `U()` | notes |
|---|---|---|---|
| `ran_ffh_anzac` | Vessel | `SEST_RAN_Fleet` | deck 1; Variant2 Arunta, 3 Warramunga, 4 Stuart, 5 Parramatta, 6 Ballarat, 7 Toowoomba, 8 Perth |
| `ran_ddg_hobart` | Vessel | `SEST_RAN_Fleet` | Variant1 Hobart, 2 Brisbane, 3 Sydney |
| `ran_opv_arafura` | Vessel | `SEST_RAN_Fleet` | Variant1 Arafura, 2 Eyre, 3 Pilbara, 4 Gippsland; fits Containers/AntiShip/AntiAir |
| `ran_ssg_collins` | Submarine | `SEST_RAN_Fleet` | Variant1 Collins, 2 Farncomb; `depth="periscope"` |
| `ran_aor_supply` | Vessel | `SEST_RAN_Fleet` | Variant1 Supply, 2 Stalwart; `loadout` Default; a working supplier (0.5 nmi, 12 kn, nothing dearer than 8000 points: passes NSM, Tomahawk, SM-6, torpedoes) |
| `usn_mh-60r` | Helicopter | `us-navy-2027` | range 520; fits ASW, ASWLongRange, ASWPatrol, Anti-shipLate; a Seahawk on an Australian side, or with its own `nation=` Australian, flies Squadron20 (816 Squadron RAN) unless told otherwise; on any other side it keeps the file's default |
| `usn_p8` | Aircraft | `p-8-poseidon` | range 2,700; fits ASW, AntiShip; Squadron3 RAAF, Squadron6 RNZAF |
| `E7A_Wedgetail` | Aircraft | `e-7a-wedgetail` | range 2,700; no fits; Squadron1 |
| `raaf_mq-4c_triton` | Aircraft | `SEST_ADF_Persistent_ISR` | range 9,430; unarmed, `weapons="Hold"` |
| `raaf_f-35a` | Aircraft | `SEST_RAAF_F-35A_JATM` | range 1,367; Squadron1/2; fits AirToAir, AirToAirStealth, AntiShip, StrikeLongRangeStealth |
| `usn_fa-18f_blk3` | Aircraft | `SEST_Growler_NGJ_MALICE` | Squadron8; MurderHornetCAP, MurderHornetAntiShip, MH_LRASM |
| `usn_ea-18g` | Aircraft | `SEST_Growler_NGJ_MALICE` | Squadron6; SEST_SEAD120D (the only fit the rows offer; every Growler fit carries both wing tanks and a full outboard pair) |
| `civ_a320`, `civ_a330` | Aircraft | `civil-aircraft-airbus` | airliners; blue for a charter, neutral for a service |
| `civ_ms_freighter_d` | Vessel | `re-power-resupply` | Southern Endeavour's stand-in |
| `civ_ms_freighter_a`, `civ_ms_freighter_b`, `civ_ms_amra`, `civ_ms_andizhan`, `civ_ms_irkutsk`, `civ_ms_slavyansk` | Vessel | `re-power-resupply` | unarmed merchants |
| `civ_ms_sealift_pacific` (tanker) | Vessel | `SEST_Replenishment` | unarmed; the game reads her from SEST Replenishment At Sea, which gives her a small supply system (0.5 nmi, nothing dearer than 2000 points) |
| `civ_ms_mairangi_bay` | Vessel | `merchants-expanded` | Coral Pioneer |
| `anl_ms_bulk` | Vessel | `auxilliary-merchant-pack` | bulker (unarmed) |
| `ran_ms_roro_a`, `ran_ms_super_p`, `ran_ms_jeparit` | Vessel | `auxilliary-merchant-pack` | ARMED auxiliaries - always `weapons="Hold"` |
| `civ_ms_ivan_franko` (liner), `civ_ms_ritina` (tanker), `civ_ms_roro_a/b/c` (ferries), `civ_ms_bulk`, `civ_ms_car_carrier_a`, `civ_ms_encounter`, `civ_ms_kommunist`, `civ_ms_mercur`, `civ_ms_act_1` | Vessel | `_vanilla` | |
| `civ_fv_okean`, `civ_fv_sterntrawler_a`..`_d`, `civ_fv_sidetrawler`, `civ_fv_crabboat`, `civ_fv_fishingboat_a/b` | Vessel | `_vanilla` | fishing |
| `civ_humpback` | Submarine | `humpback-whale` | `depth="shallow"`, neutral |
| `civ_spar_rig` | LandUnit | `_vanilla` | unarmed platform; `snap="sea"`; neutral |
| `wp_agi_okean` | Vessel | `_vanilla` | the collector *Nan Hai 27*; `weapons="Hold"` |
| `wp_ms_mercur_decoy` | Vessel | `_vanilla` | a merchant radiating a warship's radars; `loadout` Default/Udaloy/... |
| `plan_aor_type901` | Vessel | `SEST_Replenishment` | the Liaoning group's Type 901 AOE (Variant1 Hulunhu, Variant2 Chaganhu); a working supplier |
| `plan_aor_type903a` | Vessel | `SEST_Replenishment` | the protection group's Type 903A AOR (Variant1-4: Taihu, Chaohu, Honghu, Luomahu); unarmed, a working supplier |
| `wp_vt_boris_chilikin` | Vessel | `SEST_Replenishment` | Russian oiler; a working supplier that can rearm the red ships near her (nothing dearer than 13000 points) |
| `plan_type_001` | Vessel | `liaoning-type-001` | Liaoning; deck 36 |
| `plan_j-15`, `plan_j-15d` | Aircraft | `type-003-004-maneuverwarfare` | range 1,864; `loadout="AntiShip"` (156 NM) or `"AirToAir"` |
| `plan_ka-31` | Helicopter | `modern-plan-systems` | AEW; `loadout="AEW"`, Hold |
| `plan_z-18f` | Helicopter | `chinese-navy-plan` | ASW dipper; `loadout="ASW"` |
| `plan_z-9c` | Helicopter | `modern-plan-systems` | the 054A/052D/056A deck helicopter; `loadout="ASWKiller"` |
| `plan_type_054a_p5` | Vessel | `modern-plan-systems` | frigate, reach 85; supports Z-9 |
| `plan_type_056a` | Vessel | `modern-plan-systems` | corvette, reach 85; `loadout` Default/AntiShip/ASW |
| `plan_type_052d_p3` | Vessel | `modern-plan-systems` | flagship, reach 1,050 - TS09, TS11 only |
| `plan_ssn_type_093b` | Submarine | `plan-submarines` | ROMEO; reach 350 |
| `plan_ss_type_039c` | Submarine | `plan-submarines` | TANGO in chapter B (surfaced in TS03: `depth=0`) |
| `plan_ss_kilo` | Submarine | `chinese-navy-plan` | KILO; reach 20 (torpedoes) |
| `wp_ssn_akula` | Submarine | `russian-submarines` | VICTOR |
| `wp_ssgn_yasen` | Submarine | `russian-submarines` | SIERRA-TWO |
| `wp_bpk_udaloy` | Vessel | `_vanilla` | Marshal Shaposhnikov; reach 27; deck 2 (Ka-27) |
| `wp_ka-27` | Helicopter | `_vanilla` | the Udaloy's flight; `loadout="ASW"` |
| `wp_tu-142m` | Aircraft | `_vanilla` | Bear-F; `loadout="ASW"`, red, Hold |
| `wp_tu-95rt` | Aircraft | `_vanilla` | Bear-D; no fits; red, Hold |
| `wp_il-78` | Aircraft | `il-78` | Midas; `loadout="Empty"`, Hold |
| `usn_ForpostR705` | Aircraft | `small-medium-uav-series` | a ship-launched UAV spotter, range 250 |
| `airbase_raaf_*`, `airbase_rnzaf_*` | LandUnit | `SEST_RAAF_Bases` | capacity 200 |
| `airfield_small_1` | LandUnit | `_vanilla` | capacity 48 |
| `civ_radiostation` | LandUnit | `_vanilla` | a station ashore (neutral) |

## Report back

When your module builds clean, report: the builder's summary line for the
mission (units, red combat, gap/reach), any closure or recovery notes it
printed and why they are acceptable, every stand-in you named, every variable
you declare or read, and anything in the bible's card you could not build as
written and what you did instead.
