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

Mechanism: one `#!extend` stub per hull in `vessels_overwrite/` (Anchor
Chain's own patch mechanic, as Euromod assigns combat systems), setting
`AircraftSupported` to the winning file's list plus the additions. The list is
read at build time, so rebuild after every export. `CROSS-DECK.txt` in the pack
lists every deck and what it gained. The campaign builder reads the same stubs
(`deck_types` in `integration/campaign/build_pack.py`), so a bought allied
hull's deck is measured the way the game sees it.

    python3 integration/cross-deck/build_pack.py

Not demonstrated in game: that the engine honours an `AircraftSupported` set
through `#!extend`. Test card: Southern Watch 6J.
