# SEST Cross-Deck

Allied flight decks operate the similar allied aircraft. A hull's
`[FlightDeck] AircraftSupported` is written by its mod for its own navy, so a
Mogami from the allied reserve took the JMSDF's Seahawks but not the
campaigns' MH-60R, a Type 45 or Type 23 no German or Dutch Sea Lynx, and an
Italian FREMM no Royal Navy Merlin. This pack adds, to
every deck registered to an allied navy, the allied members of each airframe
family the deck already lists one of: Seahawk, NH90 NFH, Lynx/Wildcat, Merlin,
Sea King, AB 212, Panther, Seasprite, Cougar, Wasp, Alouette, CH-53, Osprey,
first-generation Harrier, AV-8B/F-35B and the catapult carrier types. A deck
gains nothing from a family it does not already fly, and a deck that takes
everything already (no list, or the game's `Helicopters` wildcard) is left
alone.

Campaign fits (27 Oct 2026): a few decks also take a type no family reaches,
because one campaign sells the deck and that aircraft together and the hull's
own list was written for another navy or an older air group
(`CAMPAIGN_DECK_TYPES` in `build_pack.py`, one comment per fit). Sulu Line's:
the H-76 on the Jose Rizal and Miguel Malvar classes (whose lists name only a
Korean Super Lynx), on HTMS Naresuan and on the Anzac; the Thai Seahawk and
the RAN MH-60R on Naresuan and BRP Tarlac. They come after the family
additions, a type already listed or added is not repeated, and the stub and
`CROSS-DECK.txt` show them under "Campaign deck fits".

Makran Line's (11 Nov 2026): the Pakistani Pack's Z-9CE (`plan_z-9ce`) on the
Pakistan Navy's Tughril (`pns_type_054a_p`, whose list names only the PLAN's
Z-9C, Z-9D and Z-9F) and Alamgir (`pns_ffg_oliver_hazard_perry_longhull`).
Pakistan is not one of the allied navies, and the families stay the allies':
a deck outside them is planned only for its campaign fits and gains nothing
else. The Alamgir's own list names a Lynx, a Wasp, two Alouette-family types
and a Seasprite, so treating her as allied would have added 21 allied
navies' helicopters to her deck.

Mechanism: one `#!extend` stub per hull in `vessels_overwrite/` (the game's
own patch mechanic, below, which Euromod uses to assign combat systems),
setting `AircraftSupported` to the winning file's list plus the additions. The list is
read at build time, so rebuild after every export. `CROSS-DECK.txt` in the pack
lists every deck and what it gained. The campaign builder reads the same stubs
(`deck_types` in `integration/campaign/build_pack.py`), so a bought allied
hull's deck is measured the way the game sees it.

    python3 integration/cross-deck/build_pack.py

Sea Power 0.8.7's own code applies `#!extend` files generically, whatever
section they set (read from its `Seapower-Scripts.dll`, `eab2297b...`, on
28 Oct 2026): `IniHandler.ScanForModifierFiles` scans every enabled mod
folder's `.ini` files and registers each `#!extend` target, and
`IniHandler.open` reads those files before the target file and keeps the
first value of each key, so the stub's `AircraftSupported` is the one the
deck gets. The deck fits should therefore take effect; none has yet been
seen in game. Test cards: Southern Watch 6J; Sulu Line 8.2-8.3 for the
campaign fits. The Makran Line fits need the same check: a Z-9CE launched
from, and recovered on, a Tughril and the Alamgir.
