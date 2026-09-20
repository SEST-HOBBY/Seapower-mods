"""The AIM-260's seat correction, shared by every pack that mounts one.

WHY THIS EXISTS
A station line `Station<n>=<store>|<Key>` applies `<Key>Positions` as a fixed
offset from the hardpoint. That offset compensates for where the store's MESH
ORIGIN sits, so a seat key belongs to a mesh, not to a station. Mount two
stores with different origins on one key and only one of them can sit flush.

Every airframe in the collection seats the AIM-260 on a key named for, and
tuned against, an AIM-120 - the mod authors' own doing. The AIM-260 renders
from dts_aim-260.obj, whose origin sits lower and further aft than the
AIM-120's, so it hangs low and aft of the rail. It was reported on the F-15EX
inner wing pylons, where the 610 gal tank alongside gives the eye a reference.

THE NUMBER
This is the settled value from the only in-game measurement in the repo: the
F-35 JATM packs tuned the same difference over four passes and finished at
+0.0025 up with +0.002..0.0035 forward. Their opening guess (up 0.005) clipped
the pylons and was halved, so this takes their final figure rather than their
first and errs small. It is still a FIRST CUT elsewhere - the F-35 compared a
different AIM-120 mesh, so the order is right but the value is not proven on
any other airframe.

Units are model units, roughly 7 cm per 0.001. +y is up, +z is forward.

TUNING - this is the one dial for every pack:
  rounds still hang low          -> raise the middle number
  rounds still sit aft of the rail -> raise the last number
  rounds now clip INTO the pylon or the tank -> halve them
0.0005 is about 3.5 cm.
"""

SEAT_DELTA = (0.0, 0.0025, 0.0025)


def shift(slots, delta=SEAT_DELTA):
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
