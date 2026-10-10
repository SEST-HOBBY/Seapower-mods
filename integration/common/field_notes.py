"""The SEST field notes: what the pack does that the game does not say.

Until 10 Oct 2026 these were loading-screen tips, numbered behind the game's
own. The loading screen now carries the quotation set alone (common/quotes.py,
build_loading_tips in integration/collection-fixes/build_patch.py), so the
notes moved to the SEST Briefing Room entry in the mission browser
(write_briefing_room in integration/campaign/build_pack.py), where a player
looking for the pack's own advice finds them under the film. Each was checked
against the pack when written: docs/replenishment-in-play.md, the briefing ROE
and TIME sections, and SETUP.
"""

NOTES = [
    "The Situation button at the bottom right of the campaign screen lists the "
    "enemy forces the campaign's missions place, nation by nation.",
    "A date-time group on a signal reads day, time Zulu, month, year. 210600Z OCT 28 "
    "is 21 October 2028 at 0600 Zulu.",
    "A contact handed to you as a datum ages off the plot in minutes unless your own "
    "sensors hold it. Classification is yours.",
    "Loadouts whose names begin SEST are this collection's own fits - AIM-260 JATM, "
    "AIM-424 MALICE and LRASM on allied airframes. Their figures follow public sources and "
    "are fiction where the sources stop.",
    "In an Open Allocation campaign every buy window sells the whole roster, and a unit "
    "of your own nation costs a fifth less.",
    "The side operations - the Dispatches, the optional and contingency missions - sail "
    "your own ships, and what you lose there stays lost.",
    "Survivors your helicopters and ships pick up are paid for at the debrief. A "
    "liferaft beacon is worth the detour.",
    "REQUIRED-MODS.txt beside each campaign lists every mod its missions reach, and "
    "LOAD-ORDER.txt the order they were built against. A unit that spawns with a stock fit "
    "is a mod that has moved.",
    "To reload missiles and torpedoes at sea, bring a supply ship within "
    "about a mile and slow down. Most auxiliaries stop supplying above 13 knots.",
    "An oiler such as the Henry J. Kaiser passes guns, ESSM, Harpoon and "
    "torpedoes but no strike missiles. Tomahawks need a Supply-class, Sacramento "
    "or Lewis and Clark.",
    "Surface your submarines before you replenish them. The game will "
    "rearm a boat underwater; the SEST campaigns treat that as off limits.",
    "Reaching a SEST mission's planned time brings a Behind Schedule "
    "signal, not a loss. The operation closes at one and a half times the plan.",
    "Identify before you shoot. In the SEST campaigns, losing a protected "
    "neutral cancels the operation.",
    "Every SEST briefing ends with a Recognition section: real photographs "
    "of your own forces and the expected opposition.",
    "After Steam updates the SEST pack or a collection mod, close the game "
    "and run SETUP again from the pack's folder.",
    "The SEST pack's Gallery folder holds real photographs of the "
    "collection's units. Open gallery.html in your web browser.",
]


def check():
    for n in NOTES:
        if "=" in n or "\n" in n or "<" in n or any(ord(ch) > 126 for ch in n):
            raise ValueError(f"field note must be one ASCII line, no '=' or '<': {n[:50]}")
    return len(NOTES)
