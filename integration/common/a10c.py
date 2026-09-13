"""The A-10C's unregistered infrared head, and its impossible squadron count.

Two defects in the A-10C mod (3459682829) that two SEST packs both need to
repair: SEST Allied Fixes on the standard aircraft, SEST A-10C+ on its clone.
Shared here so the two cannot drift apart.

1. UNREGISTERED IR HEAD. [SensorSystem2], the Maverick head, declares no
   ModuleType=Sensor and no Mount. Of 2167 aircraft sensor blocks across this
   collection 2126 declare ModuleType=Sensor; this is one of the 41 that do
   not, and usa_a-10a.ini from the same author is another. It is why the
   aircraft reads as carrying no infrared sensor at all.

2. SEVEN SQUADRONS, TWO LIVERIES. usa_a-10c_squadrons.ini declares
   NumberOfSquadrons=7 and defines two, and the language file names two.
   Five squadrons resolve to no livery texture, which is the likeliest reason
   the aircraft only ever appears in one scheme.

Both are repaired against what the file actually says rather than against a
remembered value, so an upstream fix fails the build loudly instead of being
papered over a second time.
"""
import re

IR_SENSOR = "A-10_IR"


def register_ir_head(text, where):
    """Give [SensorSystem2] the Mount and ModuleType every working peer has."""
    m = re.search(r"^(\[SensorSystem2\][^\n]*\n(?:(?!^\[).*\n)*)", text, re.M)
    if not m:
        raise SystemExit(f"{where}: [SensorSystem2] not found - upstream changed")
    block = m.group(1)
    if f"SystemName={IR_SENSOR}" not in block:
        raise SystemExit(f"{where}: [SensorSystem2] is no longer the {IR_SENSOR} head - "
                         "re-check which slot carries it")
    if re.search(r"^ModuleType=Sensor", block, re.M):
        raise SystemExit(f"{where}: [SensorSystem2] now registers itself upstream - "
                         "drop this fix")
    fixed = block.rstrip("\n") + "\nMount=Dummy\nModuleType=Sensor\n"
    return text[:m.start(1)] + fixed + text[m.end(1):]


def fix_squadron_count(text, where):
    """-> (text, old, new). Declare the number of squadrons actually defined."""
    defined = len(re.findall(r"^\[Squadron\d+\]", text, re.M))
    m = re.search(r"^NumberOfSquadrons=(\d+)", text, re.M)
    if not m:
        raise SystemExit(f"{where}: no NumberOfSquadrons line")
    if not defined:
        raise SystemExit(f"{where}: no [SquadronN] sections at all - re-check by hand")
    if int(m.group(1)) == defined:
        raise SystemExit(f"{where}: the count already matches ({defined}) - drop this fix")
    return text[:m.start(1)] + str(defined) + text[m.end(1):], m.group(1), defined
