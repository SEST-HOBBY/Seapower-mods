"""SL06 - The Aborlan Battery. Off Aborlan, Palawan, 16 November 2028.

The second fire mission, against something that fires back. Meridian
contractors have landed two truck-mounted Silkworm launchers, a fire-control
radar and two anti-aircraft guns on the Aborlan coast, south of Puerto
Princesa, and closed the island road: no convoy sails for Balabac while the
battery is there. The task group runs in under its twenty-five-mile umbrella and
destroys both launchers, by gun, by helicopter or with the FA-50s.

The third and last window that sells supply ships is before this mission.
If Sulu Provider survived Service at Sea she is at the convoy anchorage with
what is left in her (SL04SupplierLost keeps her out if not).
"""
from campaign_data import U, F, S
from .tables import HELO, ATTACK, HULLS, PARTNERS, RAN, SUPPLY

MISSION = dict(
    code="SL06", series="Sulu Line", seq="SULU LINE  ·  MISSION 6",
    group="core", num="06", key="The Aborlan Battery", place="Palawan",
    intro=(
        "Two Silkworm launchers on the Aborlan coast have closed the island road. Destroy "
        "them, under their own umbrella."
    ),
    sender="Naval Forces West",
    intent=((
        "Both launchers destroyed opens the road. The radar and the guns are there to make "
        "that expensive; they do not have to be destroyed. Run in fast, or blind them first,"
        " or let the FA-50s go in - but the convoy at the anchorage is inside the "
        "launchers' range too, and it has to be there when you are done."
    )),
    date=(2028, 11, 16), time=(10, 0), sea=2, clouds="Scattered_1", wind="NE",
    difficulty=4, minutes=110, centre=(9.0, 118.6),
    blue_nation="Philippines", red_nation="China",
    brief=(
        (
            "OFF ABORLAN, 1000. Two nights ago a Meridian landing craft put two "
            "truck-mounted Silkworm launchers ashore on the Aborlan coast, thirty miles "
            "south of Puerto Princesa, with a fire-control radar and two anti-aircraft "
            "guns. Yesterday the battery fired on a coaster off Narra and missed. Nothing "
            "has sailed for Balabac since.\\n\\nThe launchers reach about twenty-five miles. "
            "Your ships are thirty-eight miles south of them, outside that range, and the "
            "Balabac convoy is held at the Narra anchorage, twenty miles from them and "
            "inside their reach.\\n\\nDestroy both launchers. A 76 mm gun reaches them from eight miles; "
            "a helicopter or an FA-50 from wherever the guns let it. The battery will "
            "fire at what its radar finds. Every round you fire comes back only from a "
            "supply ship, and this is the last window that sells them."
        )),
    forces=(
        "Your task group, its aircraft and any supply ships you own. At the anchorage: the "
        "Balabac convoy and, if she survived the rendezvous, MV Sulu Provider. Ashore: two "
        "Silkworm launchers, a fire-control radar, two anti-aircraft guns. Neutral: bancas."
    ),
    special=(
        "A fire mission against a battery that fires back. Both launchers destroyed wins "
        "it. The last supply-ship sale is before this mission."
    ),
    objectives=[
        ("Battery", "Destroy both Silkworm launchers", "35,-35,Fail,Main"),
        ("Convoy", "Keep the Balabac convoy afloat", "20,-30,Complete"),
        ("Gunline", "Keep the lead ship afloat", "10,-30,Complete"),
        ("Radar", "Destroy the fire-control radar", "10,0,None"),
        ("Traffic", "Harm no banca", "0,-30,Complete"),
    ],
    victory=dict(kind="destroy", stations=["battery#1", "battery#2"], min_units=2,
                 objective="Battery"),
    fatal=[F("Gunline", ["gunline#1"]), F("Convoy", ["convoy#1", "convoy#2"], 2)],
    neutral_objective="Traffic",
    win=(
        "Both launchers are burning on the Aborlan beach. The convoy has weighed anchor for "
        "Balabac, and Naval Forces West has a Marine company on its way to the site."
    ),
    lose=(
        "The battery still holds the road. The convoy is going back to Puerto Princesa, and "
        "Balabac goes on rationed fuel."
    ),
    timeout="{deadline_clock}, and the launchers are still firing. The convoy will not sail "
            "tonight.",
    stations={
        "gunline": S(8.72, 118.33, "Gun line", heading=20),
        "flight": S(8.73, 118.36, "Ship's flight", heading=20, alt=500),
        "strike": S(9.70, 118.80, "Strike flight", heading=210, alt=3000),
        "battery": dict(S(9.34, 118.50, "Aborlan battery"), coastal=True),
        "convoy": S(9.02, 118.60, "Convoy anchorage", heading=270),
        "charter": S(8.88, 118.42, "Sulu Provider", heading=270),
        "bancas": S(9.15, 118.62, "Bancas", heading=300),
        "home": S(9.74, 118.75, "Puerto Princesa"),
    },
    units=[
        U("blue", "euromod-philippines", "pn_ffg-150", "gunline", variant="Variant1"),
        U("blue", "philippines-luzon-line", "phl_h-76", "flight", squadron="Squadron1",
          alt=500, loadout="CAS", slot="HeloRecon"),
        U("blue", "philippines-luzon-line", "rok_f-50_ph", "strike", squadron="Squadron1",
          alt=3000, loadout="CAS", slot="Attack"),
        U("blue", "philippines-luzon-line", "rok_f-50_ph", "strike", squadron="Squadron1",
          alt=3000, loadout="CAS", slot="Attack"),
        U("blue", "_vanilla", "civ_ms_roro_c", "convoy", name="MV Palawan Pioneer",
          nation="Philippines", weapons="Hold"),
        U("blue", "_vanilla", "civ_ms_ritina", "convoy", name="MT Princesa Star",
          nation="Philippines", weapons="Hold"),
        # Only if she came through Service at Sea; never named in a trigger
        # that ends the mission (an unspawned unit's standing is unproven).
        U("blue", "_vanilla", "civ_ms_c8", "charter", variant="Variant1",
          name="MV Sulu Provider (MSC charter)", weapons="Hold",
          spawn_if=("SL04SupplierLost", "IsFalse")),
        U("blue", "_vanilla", "airfield_small_1", "home",
          name="Puerto Princesa (Antonio Bautista Air Base)", nation="Philippines",
          weapons="Hold"),
        U("red", "_vanilla", "wp_silkworm_launcher", "battery", name="Launcher ONE",
          nation="Panama"),
        U("red", "_vanilla", "wp_silkworm_launcher", "battery", name="Launcher TWO",
          nation="Panama"),
        U("red", "_vanilla", "wp_son-9", "battery", name="Fire-control radar",
          nation="Panama"),
        U("red", "_vanilla", "pla_aaa_type55", "battery", name="AA gun north",
          nation="Panama"),
        U("red", "_vanilla", "pla_spaag_type63", "battery", name="AA gun south",
          nation="Panama"),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "bancas",
          name="Banca Lady Narra", route=[(9.00, 118.80, 0)], telegraph=2),
    ],
    resolve={"Battery": "victory", "Traffic": "neutral",
             "Convoy": ("protect", "convoy#1", "convoy#2", 2),
             "Gunline": ("protect", "gunline#1"),
             "Radar": ("destroy", "battery#3", 1)},
    declares=[],
    window=dict(buy=True, repair=True, allow=SUPPLY + HULLS + PARTNERS + RAN,
                flights=[HELO, ATTACK],
                situation=(
                    "The last of the three supply-ship sales. Whatever supply ships the "
                    "group owns after this window are all it will have for the rest of the "
                    "campaign. Nothing is rearmed here; repairs are available."
                )),
    role="strike",
)
