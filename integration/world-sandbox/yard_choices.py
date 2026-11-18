"""Where a bought ship or aircraft may be delivered in the world campaign.

Dynamic Campaign Mod offers a yard picker in its shipyard when campaign.json
gives a unit two or more yards under "yardChoices" (unit id -> base ids), and
for aircraft when "aircraftYards" (nation -> base ids) names two or more. It
keeps only bases that are supply depots the side still holds; an aircraft
arrives at the airfield the mod derives from the chosen depot.

The owner's rule of 18 Nov 2026, in three tiers by hull:
  large   carriers, cruisers, battleships, big amphibious ships: hand-picked
          home ports only
  medium  destroyers, frigates, submarines, supply ships and the rest: every
          naval depot of the unit's own nation
  small   patrol craft, corvettes, mine warfare, littoral and unmanned craft:
          own depots plus the allied depots listed in HOSTS
Aircraft take their nation's medium list. Air-base depots (Sigonella, Olenya)
are never offered to ships. A nation with one depot has no choice to offer in
the large and medium tiers, so nothing is written for it there.
"""
import re

LARGE_HULLS = {"cv", "cvn", "cva", "cvl", "cvh", "cvs", "lha", "lhd", "cg", "cgn", "ca", "bb", "bbg"}
SMALL_HULLS = {"pc", "pcc", "pb", "pt", "ptg", "pg", "pgg", "pgm", "ptf", "pf", "pcf", "fs", "fsg",
               "opv", "mcm", "mhc", "mso", "msc", "lcs", "asv", "usv", "uuv", "phm", "wpb", "wpc",
               "lcu", "lcm", "lcac"}
# Hulls whose id carries no type token.
LARGE_IDS = re.compile(r"(liaoning|type_00[1-4]|type_075|type_055|kuznetsov|kirov|slava|izumo|hyuga"
                       r"|queen_elizabeth|cavour|trieste|juan_carlos|canberra|mistral|charles_de_gaulle)")
SMALL_IDS = re.compile(r"(type_056|type_022|peykaap|corvette)")

# Large ships: the home ports chosen by hand. A nation not listed uses its
# depots that are also shipyards (its one home port in every present case).
LARGE_PORTS = {
    "US": ["usa_norfolk_naval_station_norfolk", "usp_sandiego_naval_base_san_diego", "wpac_yokosuka_naval_base"],
    "UK": ["home_uk_portsmouth"],
    "China": ["chn_zhejiang_ningbo_naval_base", "home_chn_zhanjiang"],
    "Russia": ["home_rus_severomorsk", "home_rus_vladivostok"],
}
_MED = ["France", "Italy", "Spain", "Greece", "Turkey"]
_NORTH = ["Germany", "Netherlands", "Denmark", "Norway", "Sweden"]
# Small ships: allied depots that host them, beside their own. A group
# member is hosted at every other member's depots.
HOST_PORTS = {
    "US": ["home_phl_subic", "aus_stirling_hmas_stirling", "home_tha_sattahip", "home_kor_jinhae",
           "home_isr_haifa", "home_ita_taranto"],
    "UK": ["me_bahrain_nsa_bahrain", "aus_stirling_hmas_stirling"],
    "Australia": ["home_phl_subic", "wpac_guam_naval_base_apra_harbor"],
    "Japan": ["wpac_guam_naval_base_apra_harbor", "home_phl_subic"],
    "South_Korea": ["wpac_yokosuka_naval_base"],
    "China": ["home_pak_karachi", "home_irn_bandar_abbas"],
    "Russia": ["home_vnm_cam_ranh", "home_irn_bandar_abbas"],
}
HOST_GROUPS = [_MED, _NORTH, ["Philippines", "Thailand"], ["Brazil", "Chile"], ["Iran", "Pakistan"]]


def tier_of(unit, displacement=None, submarine=False):
    """'large', 'medium' or 'small' for a ship's unit id."""
    u = unit.lower()
    tokens = set(u.split("_"))
    if submarine:
        return "medium"
    if tokens & LARGE_HULLS or LARGE_IDS.search(u):
        return "large"
    if tokens & SMALL_HULLS or SMALL_IDS.search(u):
        return "small"
    return "medium"


def build(bases, catalogue, is_submarine=lambda unit: False):
    """-> (yardChoices, aircraftYards, report) for campaign.json."""
    naval = [b for b in bases if b.get("depot") and b["kind"] != "AirBase"]
    side_of = {b["id"]: b["side"] for b in bases}
    own = {}
    for b in naval:
        own.setdefault(b["nation"], []).append(b["id"])
    # The home yard first: the picker opens on it.
    for nation, ids in own.items():
        ids.sort(key=lambda i: not next(b for b in naval if b["id"] == i).get("shipyard"))
    yards = {b["id"] for b in naval if b.get("shipyard")}

    def hosts(nation, side):
        out = list(HOST_PORTS.get(nation, []))
        for group in HOST_GROUPS:
            if nation in group:
                out += [i for other in group if other != nation for i in own.get(other, [])]
        return [i for i in dict.fromkeys(out) if side_of.get(i) == side]

    def ports(nation, side, tier):
        mine = own.get(nation, [])
        if not mine:
            return []
        if tier == "large":
            picked = LARGE_PORTS.get(nation) or [i for i in mine if i in yards] or mine[:1]
            return [i for i in picked if i in mine]
        if tier == "small":
            return mine + [i for i in hosts(nation, side) if i not in mine]
        return mine

    choices, counts = {}, {"large": 0, "medium": 0, "small": 0}
    for e in catalogue:
        if e.get("aircraft"):
            continue
        tier = tier_of(e["unit"], submarine=is_submarine(e["unit"]))
        ids = ports(e["nation"], e["side"], tier)
        if len(ids) >= 2:
            choices[e["unit"]] = ", ".join(ids)
            counts[tier] += 1
    air = {nation: ", ".join(ids) for nation, ids in sorted(own.items()) if len(ids) >= 2}
    return choices, air, {"ships_with_a_choice": counts, "aircraft_nations": sorted(air)}
