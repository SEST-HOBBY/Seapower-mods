"""Airbase launch-rate retune: the [FlightDeck] keys that pace how fast a
large airfield gets aircraft off the ground, set to the game's own large-base
values where a mod's copy dropped or lowered them.

Why (6 Oct 2026): the player reported Chinese aircraft taking off very
slowly from the collection's large airbases. The two bases the SEST missions
fly them from are byte-for-byte the game's own large-base geometry with new
[AirGroup] and [FlightDeck] numbers:

  pla_airbase_modern (3631042692)   = vanilla wp_airbase_1 (Tier 4 - Large
      Airbase, 96 aircraft, 48 ground crews, 96 park slots) carrying 220
      aircraft on 40 crews and 80 slots: more than twice the aircraft,
      fewer crews to ready them, through the same seven plane pads and two
      runway launch points.
  plaaf_airlift_airbase (3782020901) = vanilla wp_large_pvo_airbase with the
      SpawnInterval, GroundCrewCount and DeckParkSlots lines deleted, so the
      game's defaults - whatever they are - pace a 192-aircraft base. The
      changelog (0.6, "Added mandatory spawn delay") makes SpawnInterval the
      key that paces consecutive spawns; the game's two bases that set it
      use 0.4.

What is changed, and only upward or where absent:
  SpawnInterval         set to 0.4 where absent (the game's large-base value)
  LaunchDelay           lowered to 1 where higher (every modern base uses 1)
  GroundCrewCount       raised to half the AircraftCapacity, the game's own
                        ratio (48 for 96), where lower or absent
  DeckParkSlots         raised to the AircraftCapacity, the game's own ratio,
                        where lower or absent
  ForwardsTaxiVelocity  raised to 25 where lower (the game's wp_airbase_5,
                        its other Tier 4 base, taxis at 25; the long taxiways
                        of these bases are where the time goes)
  SlowTaxiVelocity      raised to 8 where lower

Nothing in the geometry is touched: elevators, launch points, taxi paths
and recovery points stay the author's. The file is the mod's own text with
these lines changed in place, so a mod update that re-tunes the keys itself
shows up as a diff here rather than being silently overwritten; the retune
retires key by key as the author's values reach these.

None of this has been watched in the game: it is a draft for the play test
(docs/play-test-guide.md, "Airbase launch rate"), and the numbers are the
game's own, not a guess at better ones.
"""
import math
import re

SPAWN_INTERVAL = "0.4"
LAUNCH_DELAY = 1
CREW_RATIO = 0.5
TAXI_FORWARD = 25
TAXI_SLOW = 8


def _flightdeck(text):
    m = re.search(r"^\[FlightDeck\][^\n]*\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
    if not m:
        raise ValueError("no [FlightDeck] section")
    return m


def _value(body, key):
    m = re.search(rf"^{key}=([^\s/#]+)", body, re.M)
    return m.group(1) if m else None


def retune(text):
    """(new text, [change notes]) for one airbase ini. Idempotent: a second
    pass changes nothing."""
    m = _flightdeck(text)
    body = m.group(1)
    capacity = _value(body, "AircraftCapacity")
    if capacity is None:
        raise ValueError("no AircraftCapacity in [FlightDeck]")
    capacity = int(capacity)
    changes = []

    def set_key(key, new, when):
        nonlocal body
        old = _value(body, key)
        if old is None:
            # after LaunchDelay if present, else at the end of the section
            anchor = re.search(r"^LaunchDelay=[^\n]*\n", body, re.M)
            line = f"{key}={new}\n"
            if anchor:
                body = body[:anchor.end()] + line + body[anchor.end():]
            else:
                body = body.rstrip("\n") + "\n" + line
            changes.append(f"{key}={new} added ({when})")
            return
        try:
            old_n, new_n = float(old), float(new)
        except ValueError:
            return
        if (when == "raise" and new_n > old_n) or (when == "lower" and new_n < old_n):
            body = re.sub(rf"^{key}=[^\n]*", f"{key}={new}", body, count=1, flags=re.M)
            changes.append(f"{key} {old} -> {new}")

    if _value(body, "SpawnInterval") is None:
        set_key("SpawnInterval", SPAWN_INTERVAL, "absent")
    set_key("LaunchDelay", LAUNCH_DELAY, "lower")
    set_key("GroundCrewCount", math.ceil(capacity * CREW_RATIO), "raise")
    set_key("DeckParkSlots", capacity, "raise")
    set_key("ForwardsTaxiVelocity", TAXI_FORWARD, "raise")
    set_key("SlowTaxiVelocity", TAXI_SLOW, "raise")
    return text[:m.start(1)] + body + text[m.end(1):], changes


def header(unit_id, mod, changes):
    lines = "\n".join(f"#   {c}" for c in changes)
    return (f"# SEST Collection Fixes - {unit_id}.ini: the {mod} file with its launch\n"
            "# rate set to the game's own large-base values (AIRBASE_RETUNE in\n"
            "# build_patch.py; integration/common/airbase.py says why). Changed lines:\n"
            f"{lines}\n# Everything else is the author's text, byte for byte.\n")
