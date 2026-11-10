"""Presentation and compatibility contract for the combined fictional 2028 world.

The regional builder adds to the original; this layer never drops bases,
forces, patrols, catalogue entries, identities or the engine's unwrapped
longitude interval. DCM fields stay in campaign.json; SEST metadata lives in
a sibling file so native deserialisation remains independent of our UI.
"""
import copy
import json
from pathlib import Path

CAMPAIGN_ID = "sest.world_sandbox_2028.regional"
NAME = "Global Maritime Operations 2028"
SPEC = Path(__file__).with_name("world-operations-2028.json")
# Coalition command appointments, not a claim about any nation's promotion system.
STAGES = [("Task Unit Commander", 0), ("Escort Group Commander", 300),
          ("Task Group Commander", 800), ("Flotilla Commander", 1600),
          ("Force Commander", 2800), ("Joint Force Commander", 4500),
          ("Fleet Commander", 7000), ("Theatre Commander", 10500)]
PRICE_CAPS = (60, 120, 200, 300, 450, 650, 900, float("inf"))

THEATRES = [
    {"id": "europe", "name": "European Waters", "bounds": [30, 74, -25, 45]},
    {"id": "middle-east", "name": "Middle East and Indian Ocean", "bounds": [-5, 32, 30, 100]},
    {"id": "africa", "name": "African and Cape Routes", "bounds": [-40, 30, -25, 55]},
    {"id": "americas", "name": "Americas and Southern Ocean", "bounds": [-62, 74, -130, -25]},
    {"id": "southern", "name": "Allied Southern Flank", "bounds": [-62, -5, 100, 180]},
    {"id": "pacific", "name": "Pacific and East Asia", "bounds": [-5, 74, 100, 258]},
]


def modernise(expanded):
    world = copy.deepcopy(expanded)
    if world["id"] != CAMPAIGN_ID:
        raise ValueError("The combined world must retain the current expanded-save identity")
    world["name"] = NAME
    world["description"] = (
        "October 2028. Command a coalition maritime force across the Atlantic, Mediterranean, Indian Ocean "
        "and Pacific. Protect sea communications, maintain forward air cover and sustain deployed groups "
        "through a network of naval facilities and airfields. Intelligence is incomplete; losses and "
        "expenditure carry into subsequent operations.\n\n"
        "Earn renown through battle results and accepted Admiralty tasks: escort, area control, surveillance "
        "and multi-phase operations when offered. Eight command stages progressively open the recruitment "
        "catalogue. Keep fuel and ammunition moving by convoy, airlift and replenishment ship. F11 opens "
        "cumulative combat costs; Overview shows task rewards and the next command milestone.\n\n"
        "Hypothetical 2028 scenario. Coalition alignments, access, forces and stocks are design assumptions; "
        "public facility locations do not establish actual deployments or readiness. Requires the SEST "
        "collection and Dynamic Campaign Mod. Campaign credits and USD cost estimates are separate. "
        "Start a new campaign for the revised facilities and progression; existing saves retain their state."
    )
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    bases = {b["id"]: b for b in world["bases"]}
    def continuous(lon):
        lo, hi = world["bounds"]["lonMin"], world["bounds"]["lonMax"]
        while lon < lo: lon += 360
        while lon > hi: lon -= 360
        if not lo <= lon <= hi: raise ValueError("position outside world longitude interval")
        return lon
    for fix in spec["corrections"]:
        b = bases[fix["id"]]
        lat, lon = fix.get("placement", fix["point"])
        b["lat"], b["lon"] = lat, continuous(lon)
        b["field"].update(lat=b["lat"], lon=b["lon"], heading=fix["heading"])
    for bid, name in spec["display_names"].items():
        bases[bid]["name"] = name
    for site in spec["sites"]:
        b = copy.deepcopy(site["base"])
        if b["id"] in bases: raise ValueError("duplicate operations base: " + b["id"])
        depot = bases.get(b["supplyFrom"], {})
        if not depot.get("depot") or depot["side"] != b["side"]:
            raise ValueError("operations base needs a friendly production depot")
        b["lon"] = b["field"]["lon"] = continuous(b["lon"])
        world["bases"].append(b)
        bases[b["id"]] = b
    for side in world["sides"]:
        side["hq"] = "Coalition Maritime Headquarters"
        side["command"] = "Maritime Component Command"
        world["ranks"][side["id"]] = [{"name": n, "renown": r} for n, r in STAGES]
    # Keep every platform, price and delivery time. Split the recruitment bands
    # into eight reachable stages, equally for both coalitions.
    for row in world["catalogue"]:
        value = world["values"][row["unit"]]
        row["tier"] = next(i for i, cap in enumerate(PRICE_CAPS) if value <= cap)
    # Original tier five already gave the AI its complete catalogue at opening.
    world["ai"]["startTier"] = len(STAGES) - 1
    for side in ("blue", "red"):
        world["story"]["opening"][side] = {
            "situation": [
                "1 October 2028. Maritime confrontation has escalated across several theatres. "
                "Your coalition's dispersed forces must operate with incomplete contact information and finite stocks.",
                "Protect coalition bases and sea communications. Maintain freedom of movement for "
                "supply traffic and prevent hostile forces from isolating forward positions."],
            "enemy": ["Expect surface groups, submarines and land-based aviation. Intelligence reports "
                      "are estimates; establish identification before committing weapons. Civil traffic remains present."],
            "intent": [
                "Concentrate locally, retain a reserve and coordinate air cover with surface and "
                "submarine operations. Accept Admiralty assignments whose deadlines your force can meet.",
                "Check fuel, magazines and base stocks before sailing. Set supply priorities, "
                "escort exposed convoys and use airlift for urgent ammunition. Replenishment ships draw from port stocks.",
                "Renown records operational achievement and opens eight command stages. Escort, "
                "surveillance and area-control assignments can earn renown and credits without a fleet battle. "
                "Read the offered task's conditions and rewards; routine movement alone earns no task reward.",
                "Begin each engagement paused, prepare aircraft and issue initial orders, "
                "then unpause. To disengage, press Esc and choose End battle. Victory is not required; "
                "the campaign assesses survivors, losses and unresolved fighting on return."]}
    world["texts"] = dict(world.get("texts") or {},
        guideWar="October 2028. Coalition maritime operations span several theatres. Forces, access and alignments are hypothetical.",
        guideWarTask="Protect sea communications, sustain forward bases and accept achievable Admiralty assignments. F11 shows your next command milestone and current task rewards.",
        guideDepots="Production depots make fuel and ammunition. Choose supply sources and priorities in the supply panel; convoys carry stocks to forward facilities. Escort threatened routes.",
        guideReplen="Replenishment ships load from friendly port stocks and transfer stores to nearby groups at sea. Their capacities and remaining cargo are finite.",
        guideYards="Eight command stages open the recruitment catalogue using renown {ranks}. Each card shows its price and availability. These are coalition command appointments, not national promotion rules.",
        guideExampleSupply="Choose a forward base, review its shortage, set its supply priority and protect the delivery route. Airlift can move urgent ammunition; fuel still needs the native supply system.")
    return world


def operations_manifest(world):
    return {
        "schema": "sest.world-operations.v1",
        "campaign_id": world["id"],
        "display_name": world["name"],
        "combined_sources": ["original-world", "regional-expansion-2028", "world-operations-2028"],
        "legacy_original_id": "sest.world_sandbox_2028",
        "legacy_original_definition": "legacy_campaigns/sest-world-sandbox/campaign.json",
        "save_policy": "Keep native saves unchanged. Expanded identity retained; new content requires a new game.",
        "economy": {"campaign_values": "game credits", "combat_catalogue": "USD estimates; catalogue basis shown in UI"},
        "counts": {key: len(world.get(key, [])) for key in ("bases", "forces", "patrols", "catalogue")},
        "bounds": world["bounds"],
        "longitude_policy": "Continuous engine interval; wrap only for geographic display.",
        "theatres": THEATRES,
        "features": ["replenishment", "tankers", "convoys", "ground", "spyShips", "traffic", "ranks", "catalogue"],
        "service_policy": "Fictional service awards from completed manual battle reports; never inferred from USD spending.",
        "progression": {"stages": [{"name": n, "renown": r} for n, r in STAGES],
                        "rewards": "Native battle results and accepted Admiralty assignments; no custom currency or automatic transit reward.",
                        "supply": "Native depot production, convoys, ammunition airlifts and replenishment cargo. Credits are not physical supplies."},
        "geography": {"spec": "integration/world-sandbox/world-operations-2028.json",
                      "corrected_airfields": 37, "added_airfields": 40,
                      "terrain_validation": "Geographic mask checked; native terrain and gameplay acceptance pending."},
    }
