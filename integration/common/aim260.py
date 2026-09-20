"""The AIM-260's seat correction, per airframe.

WHY A SEAT KEY MATTERS
A station line `Station<n>=<store>|<Key>` applies `<Key>Positions` as a fixed
offset from the hardpoint. That offset compensates for where the store's MESH
ORIGIN sits, so a seat key belongs to a mesh, not to a station. Mount two
stores with different origins on one key and only one of them can sit flush.

Every airframe in the collection seats the AIM-260 on a key named for, and
tuned against, an AIM-120 - the mod authors' own doing. It was reported on the
F-15EX inner wing pylons, where the 610 gal tank alongside gives the eye a
reference, that the AIM-260 there hung low and aft of the rail.

WHY THERE IS NO SHARED NUMBER ANY MORE
This module used to hold ONE delta for every pack, taken from the F-35 JATM
packs' four tuning passes. That was a category error, and it put the F-16's
rounds a missile diameter into the pylon.

The F-35's stations carry NO seat key at all: `usn_f-35c.ini` defines Pilot,
GBU-53 and the AIM-260 seats and nothing else, so its AMRAAMs sit on the bare
hardpoint. Its measured `0,0.0025,0.0035` is therefore an ABSOLUTE position
above a zero origin - not a difference between two meshes. Re-using it as a
delta added it on top of whatever AIM-120 seat the next airframe already had,
which is a different baseline on every airframe.

It is also not a mesh difference for the reason the old text gave. dts_aim-260
and dts_aim-260_w both render from dts_aim-260.obj, mesh `aim-260`, out of the
same aim-120 folder with the AIM-120's own material; they differ only in
DropDuration and a commented-out VelocityBleed. The AIM-260 is an AIM-120
derivative in the same origin convention, which is why an airframe whose
AIM-120 seat is right usually needs little or nothing for the AIM-260.

So the correction is per airframe, it is stated with its evidence, and an
airframe nobody has looked at does not get to inherit somebody else's number.

Units are model units, roughly 7 cm per 0.001. +y is up, +z is forward.

TUNING:
  round hangs low            -> raise the middle number
  round sits aft of the rail -> raise the last number
  round clips INTO the pylon -> lower them
0.0005 is about 3.5 cm; an AIM-260 body is about 18 cm across, so 0.0025 is
very nearly one full diameter - which is the size of error to expect if a
number is carried onto an airframe it was never measured on.
"""

# unit id -> (dx, dy, dz) added to that airframe's own AIM-120 seat.
SEAT_DELTA = {
    # F-15EX. Where the low-and-aft hang was actually seen. The value is the
    # F-35 packs' final figure (their opening guess of 0.005 up clipped the
    # pylons and was halved), and it lands MTH260 at absolute y=0 against an
    # MTH seat sitting at -0.0025. Not re-measured since; left as it is
    # because nothing has been reported against it.
    "usaf_f-15ex_SEII": (0.0, 0.0025, 0.0025),

    # F-16CM Block 52. Measured in game 20 Sep 2026: with the inherited
    # +0.0025 the round sat so high that the bottom of the AIM-260 was level
    # with the bottom surface of the pylon - lifted by about one body
    # diameter, which is what +0.0025 is. Its aim-120d-34/-56 seats carry
    # y=0 and only a small z trim, and the AMRAAM hangs correctly on them, so
    # the AIM-260 is seated exactly where the AIM-120 sits and no further.
    # If it now hangs low, or sits aft of the rail, raise in 0.0005 steps.
    "usaf_f-16cm-bl52d": (0.0, 0.0, 0.0),
}


def delta(airframe):
    """That airframe's correction, or a hard stop if nobody has measured one.

    Defaulting here is what caused the F-16 bug: a number measured on one
    airframe is not evidence about another, so a new pack must add its own
    entry above and say what it looked at.
    """
    if airframe not in SEAT_DELTA:
        raise KeyError(
            f"no AIM-260 seat correction recorded for {airframe!r}. Seat it on "
            f"the airframe's own AIM-120 seat with (0.0, 0.0, 0.0), look at it "
            f"in game, and add the entry to SEAT_DELTA in {__file__}")
    return SEAT_DELTA[airframe]


def shift(slots, delta):
    """Offset a seat's slot list by the delta.

    `slots` is the parsed form of a <Key>Positions value: a list of (x, y, z)
    tuples, one per slot (multi-rail seats such as the F-15EX's MTH declare
    two). Returns the value ready to write back, slots re-joined with '|'.
    """
    dx, dy, dz = delta
    return "|".join(f"{x + dx:g},{y + dy:g},{z + dz:g}" for x, y, z in slots)


def parse(value):
    """A <Key>Positions value as a list of (x, y, z) float tuples."""
    return [tuple(float(v) for v in slot.split(",")) for slot in value.split("|")]
