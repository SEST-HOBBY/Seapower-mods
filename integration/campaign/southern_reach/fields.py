"""The civil airports Southern Reach uses as detachment fields.

Hobart, Invercargill and Christchurch are placed as the game's small airfield
(airfield_small_1), and two faults were reported in SR06 on 10 Oct 2026:

  Old aircraft. Without a CustomAirGroup the field launches the stock file's
  air group - F-4D/E, RA-5C, EA-6B, E-3A, P-3C, SH-3H, CH-46 - into a 2028
  mission. Every field now carries the detachment its briefing names and
  nothing else: RAAF P-8A (Squadron3, Australia), RNZAF P-8A (Squadron6,
  New Zealand), or none at a civil airport.

  Part of the field over the sea. The station helper's default heading is 90,
  so every field lay east-west. The model's runway runs along its heading -
  about 1.6 km at 100 m per model unit (touchdown z -9.8, take-off hold
  z +5.9) - with buildings up to 350 m to its right. Stations now follow each
  real runway's true bearing, from the published threshold coordinates,
  with the anchor 195 m along it from the runway's midpoint so the model's
  runway sits on the real one, and the buildings on the inland side. The
  GSHHS full-resolution coastline puts the New River estuary 1.7 km
  south-east of Invercargill's old anchor; the game's coast there is coarser,
  which is how the field's south-east corner got wet. Invercargill moves 1 km
  north on its runway line.

  Clearance from the field's footprint to GSHHS water, old -> new:
    Invercargill   750 m -> 2,000 m (runway 065/245 true, buildings north-west)
    Hobart         750 m -> 1,000 m (runway 136/316 true, buildings south-west;
                   1,500 m would need a 3 km move)
    Christchurch   more than 8 km either way (runway 040/220 true)
"""
from campaign_data import S

FIELDS = {
    "invercargill": S(-46.4060, 168.3110, "Invercargill Airport", heading=245),
    "hobart": S(-42.8370, 147.5130, "Hobart Airport", heading=136),
    "christchurch": S(-43.4850, 172.5370, "Christchurch International", heading=40),
}

RAAF_P8 = "Squadron3"     # Nation=Australia in the winning usn_p8 squadrons file
RNZAF_P8 = "Squadron6"    # Nation=NewZealand


def detachment(**aircraft):
    """The extra keys that give a placed airfield its own air group: the
    aircraft named, nothing else. No aircraft: an empty group, as the game's
    own editor saves a field whose air group was cleared."""
    extra = {"CustomAirGroup": "True"}
    extra.update(aircraft)
    return extra
