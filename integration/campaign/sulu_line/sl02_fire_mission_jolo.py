"""SL02 - Fire Mission Jolo. Off Jolo, Sulu, 19 October 2028.

Naval gunfire support. The Marines' battalion landing team on Jolo is pinned
below a ridge the Meridian network has armed: two drone launch rails, two
gun trucks and a Sosna air-defence vehicle that has already turned back the
Air Force's helicopters once. The task group runs in from the north and puts
its guns on the positions. Three of the five destroyed is the fire mission.

The first mission where the no-rearm rule bites: every 76 mm round fired
here is gone until a supply ship gives it back. The Meridian boat out of
Basilan is the second thing that wants ammunition.
"""
from campaign_data import U, F, S
from .tables import HELO, ATTACK, PARTNERS

MISSION = dict(
    code="SL02", series="Sulu Line", seq="SULU LINE  ·  MISSION 2",
    group="core", num="02", key="Fire Mission Jolo", place="Jolo, Sulu",
    intro=(
        "The Marines on Jolo are pinned below an armed ridge. Run in from the north and put "
        "the guns on it."
    ),
    sender="Naval Forces West; Marine Battalion Landing Team 7 ashore",
    intent=((
        "Take the ridge's weapons off the Marines. Three of the five positions destroyed "
        "lets the battalion move. The guns are the right tool: they reach, and a gun round is"
        " the cheapest thing a supply ship carries. Keep enough back for the Meridian boat "
        "that will come out of Basilan when it hears the firing."
    )),
    date=(2028, 10, 19), time=(9, 30), sea=2, clouds="Scattered_1", wind="NE",
    difficulty=3, minutes=110, centre=(6.3, 121.2),
    blue_nation="Philippines", red_nation="China",
    brief=(
        (
            "OFF JOLO, 0930. Marine Battalion Landing Team 7 went ashore east of Jolo town "
            "two days ago to clear the coast road. It is pinned below the ridge above "
            "Patikul. The Meridian network has armed the ridge: two drone launch rails, "
            "two gun trucks and an air-defence vehicle that drove the Air Force's "
            "helicopters off yesterday afternoon.\\n\\nThe battalion has asked for naval "
            "gunfire. Your ships are twenty-five miles north of the coast. Close to gun "
            "range and destroy at least three of the five positions. The Marines' fire "
            "control party has them plotted and they are on your map.\\n\\nThe launch "
            "rails can put a drone on a ship as easily as on the Marines, and Meridian "
            "keeps a fast attack craft at Basilan. Nothing you fire today comes back except "
            "from your own supply ship. Bancas are working the coast."
        )),
    forces=(
        "Your task group, its helicopter and any FA-50s the Air Force has released, out of "
        "Zamboanga. Ashore, on the ridge: two drone launch rails, two gun trucks, a Sosna "
        "air-defence vehicle. At sea: one Meridian fast attack craft at Basilan. Neutral: "
        "bancas."
    ),
    special="A fire mission: three of the five positions on the ridge destroyed wins it.",
    objectives=[
        ("Fire", "Destroy three of the five positions on the ridge", "35,-35,Fail,Main"),
        ("Gunline", "Keep the lead ship afloat", "15,-30,Complete"),
        ("Raider", "Sink the Meridian boat if it comes out", "10,0,None"),
        ("Traffic", "Harm no banca", "0,-30,Complete"),
    ],
    victory=dict(kind="destroy", stations=["ridge"], min_units=3, objective="Fire"),
    fatal=[F("Gunline", ["gunline#1"])],
    neutral_objective="Traffic",
    win=(
        "The ridge is quiet. BLT 7 is moving on the coast road, and its fire control party "
        "has sent the ships its thanks and its new grid."
    ),
    lose=(
        "The gun line is broken and the ridge still holds. The battalion is back inside its "
        "perimeter, waiting for a gun that is not coming."
    ),
    timeout="{deadline_clock}, and the ridge is still firing. The Marines have pulled back to the "
            "beach for the night.",
    stations={
        # The gun line forms on the proven water 25 NM north of the coast
        # and runs in; the ridge is on the coast above Patikul.
        "gunline": S(6.50, 121.10, "Gun line", heading=180),
        "flight": S(6.48, 121.12, "Ship's flight", heading=180, alt=500),
        "strike": S(7.10, 122.15, "Strike flight", heading=240, alt=3000),
        "ridge": dict(S(6.05, 121.00, "Patikul ridge"), coastal=True),
        "raider": S(6.83, 121.90, "Basilan boat", heading=250),
        "bancas": S(6.58, 121.10, "Bancas", heading=90),
        "home": S(6.92, 122.06, "Zamboanga"),
    },
    units=[
        U("blue", "euromod-philippines", "pn_ffg-150", "gunline", variant="Variant1"),
        U("blue", "philippines-luzon-line", "phl_h-76", "flight", squadron="Squadron1",
          alt=500, loadout="CAS", slot="HeloRecon"),
        U("blue", "philippines-luzon-line", "rok_f-50_ph", "strike", squadron="Squadron1",
          alt=3000, loadout="CAS", slot="Attack"),
        U("blue", "philippines-luzon-line", "rok_f-50_ph", "strike", squadron="Squadron1",
          alt=3000, loadout="CAS", slot="Attack"),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Zamboanga (Edwin Andrews Air Base)", nation="Philippines", weapons="Hold"),
        U("red", "shahed-136-zero-two", "shahed_tel_black", "ridge",
          name="Launch rail NORTH", nation="Panama"),
        U("red", "shahed-136-zero-two", "shahed_tel_black", "ridge",
          name="Launch rail SOUTH", nation="Panama"),
        U("red", "pickup-truck-extension", "civ_car_pickup_1983_assault_civ", "ridge",
          name="Gun truck 1", nation="Panama"),
        U("red", "pickup-truck-extension", "civ_car_pickup_1983_assault_civ", "ridge",
          name="Gun truck 2", nation="Panama"),
        U("red", "ground-upgrade-spaa", "ru_spaa_mt-lb_sosna", "ridge",
          name="Sosna vehicle", nation="Panama"),
        U("red", "red-storm-arsenal", "ir_ptg_peykaap_3", "raider", name="Meridian Escort 14",
          nation="Panama", route=[(6.45, 121.20, 0)], telegraph=4),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "bancas",
          name="Banca Nur Jannah", route=[(6.40, 121.30, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_b", "bancas",
          name="Banca Sitti Aisa", route=[(6.55, 120.90, 0)], telegraph=2),
    ],
    resolve={"Fire": "victory", "Traffic": "neutral",
             "Gunline": ("protect", "gunline#1"),
             "Raider": ("destroy", "raider", 1)},
    declares=[],
    window=dict(buy=True, repair=True, allow=list(PARTNERS),
                flights=[HELO, ATTACK],
                situation=(
                    "The Royal Thai Navy's detachment is under task group command: HTMS "
                    "Naresuan or Taksin and their Seahawk are on offer, with the Air Force's "
                    "FA-50s out of Zamboanga. No supply ships are sold here, and nothing is "
                    "rearmed. Repairs are available."
                )),
    role="strike",
)
