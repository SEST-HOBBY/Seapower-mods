"""Presentation and compatibility contract for the combined fictional 2028 world.

The regional builder adds to the original; this layer never drops bases,
forces, patrols, catalogue entries, identities or the engine's unwrapped
longitude interval. DCM fields stay in campaign.json; SEST metadata lives in
a sibling file so native deserialisation remains independent of our UI.
"""
import copy

CAMPAIGN_ID = "sest.world_sandbox_2028.regional"
NAME = "SEST Modernised Worldwide Campaign 2028"

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
        "One fictional worldwide campaign combining the original World Sandbox and its complete regional expansion. "
        "October 2028: command a multinational coalition across the Atlantic, European waters, the Middle East, "
        "Indian Ocean and Pacific. Regional ports, forward air detachments, replenishment groups and patrols are "
        "part of this world. The scenario's deployments, alliances and quantities are game design choices, not "
        "a statement of actual readiness or national policy.<LineBreak/><LineBreak/>"
        "Use the Dynamic Campaign panels for orders, recruitment, supplies, ground operations and convoys. "
        "SEST's F11 Operations window adds campaign overview, forces, recorded combat costs and a separate "
        "service-ribbon record on the inspected beta build. Campaign points are game credits; USD catalogue "
        "estimates in the cost report remain a separate measure.<LineBreak/><LineBreak/>"
        "Requires the SEST collection and Dynamic Campaign Mod. Beta map and topographic layers follow the "
        "installed game's map mode. Existing Regional Expansion saves retain their campaign identity; new "
        "world content is applied when starting a new campaign."
    )
    return world


def operations_manifest(world):
    return {
        "schema": "sest.world-operations.v1",
        "campaign_id": world["id"],
        "display_name": world["name"],
        "combined_sources": ["original-world", "regional-expansion-2028"],
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
    }
