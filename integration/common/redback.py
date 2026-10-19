"""The SEST Redback fit (SEST_REDBACK), added the same way to every carrier.

The AGR-30 Redback is SEST's one upgraded 70mm guided rocket (round and pods in
SEST Allied Fixes: sest_agr-30, the 7-tube LAU-68 sest_agr-30_pod and the
19-tube LAU-3 sest_agr-30_pod19). The decision of 19 Oct 2026 put it on every
A-10, Apache, Seahawk, F-16 and Hornet SEST fields, and an aircraft's file can
only be shipped by one SEST pack - so the A-10C+, the F-16CM and the US Super
Hornets get the fit from their own pack's builder, and everything else from
Allied Fixes. This module is the one recipe they share: clone a fit the
aircraft already flies, put Redback pods on the pylons it names, keep
everything else on that fit as the author hung it.

A station line's seat - the name after `|` - picks the airframe's
<seat>Positions= offsets, and a seat with two or three positions hangs a store
at each (the F/A-18A's TwinMk83 is how it carries two pods on one pylon). A
pod that kept the seat of the store it replaced hung where that store did: on
a TER's or a Hellfire rail's points, inside the F-16's SDB racks, and on no
offset at all where the store had none. So a swap names the pod's own seat,
and the fit hides whatever rack the pod would otherwise sit inside.
"""
import re
import sys

LOADOUT = "SEST_REDBACK"
POD = "sest_agr-30_pod"         # LAU-68, 7 rounds: racks, twin mounts, the MQ-9
POD19 = "sest_agr-30_pod19"     # LAU-3, 19 rounds: a single pylon
PODS = {"pod": POD, "pod19": POD19}
KEEP = object()                 # seat: keep the replaced store's


def add_fit(text, unit, donor, swaps, hide=(), positions=None):
    """`text` with SEST_REDBACK declared and its block after `donor`'s.

    swaps: (store id, to, how many[, seat[, stations]]). Every station line
    hanging that store - on the stations named, if any - becomes `to`, "pod"
    or "pod19", or with None is dropped from the fit. seat: KEEP (the
    default) keeps the replaced store's, "" drops it, a name sets it, and a
    named seat must have its Positions= key. The count must match exactly,
    so an upstream change to the donor stops the build.
    hide: sub-models added to the fit's SubModelsToHide.
    positions: {seat: value} - Positions= keys SEST adds to the airframe,
    after its last one ahead of the fits; a key the author already wrote
    stops the build.
    """
    if re.search(rf"^\[WeaponSystem1{LOADOUT}\]", text, re.M):
        sys.exit(f"{unit}: {LOADOUT} is already defined - re-check upstream")
    for seat, value in (positions or {}).items():
        if re.search(rf"^{re.escape(seat)}Positions=", text, re.M):
            sys.exit(f"{unit}: {seat}Positions is already defined - re-check upstream")
        fits = re.search(r"^\[WeaponSystem1\w", text, re.M)
        last = None
        for last in re.finditer(r"^[A-Za-z0-9_.-]+Positions=[^\n]*\n",
                                text[:fits.start() if fits else len(text)], re.M):
            pass
        if last is None:
            sys.exit(f"{unit}: no Positions= keys to add {seat}Positions after")
        text = (text[:last.end()] + f"# SEST: the Redback pod mount\n{seat}Positions={value}\n"
                + text[last.end():])
    text, n = re.subn(r"^(AvailableLoadouts=[^\r\n]*?)(\s*)$", rf"\1,{LOADOUT}\2",
                      text, count=1, flags=re.M)
    if n != 1:
        sys.exit(f"{unit}: AvailableLoadouts line not found")
    # searched after the edits above: offsets held across them go stale
    m = re.search(rf"^\[WeaponSystem1{re.escape(donor)}\][^\n]*\n(.*?)(?=^\[)",
                  text, re.M | re.S)
    if not m:
        sys.exit(f"{unit}/{donor}: donor fit not found - upstream changed")
    body = m.group(1)
    for store, to, need, *rest in swaps:
        seat = rest[0] if rest else KEEP
        stations = "|".join(str(s) for s in rest[1]) if len(rest) > 1 else r"\d+"
        if seat is not KEEP and seat and not re.search(
                rf"^{re.escape(seat)}Positions=", text, re.M):
            sys.exit(f"{unit}: seat {seat} has no {seat}Positions= key")
        line = rf"^(Station(?:{stations})=){re.escape(store)}((?:\|[^\r\n]*)?)(\r?\n|$)"
        if to is None:
            body, k = re.subn(line, "", body, flags=re.M)
        else:
            mount = r"\g<2>" if seat is KEEP else (f"|{seat}" if seat else "")
            body, k = re.subn(line, rf"\g<1>{PODS[to]}{mount}\g<3>", body, flags=re.M)
        if k != need:
            sys.exit(f"{unit}/{donor}: {k} station(s) hang {store}, expected {need} "
                     "- upstream changed the fit")
    if POD not in body and POD19 not in body:
        sys.exit(f"{unit}/{donor}: no Redback pod in the derived fit")
    if hide:
        h = re.search(r"^SubModelsToHide=([^\r\n]*)", body, re.M)
        have = [x for x in h.group(1).split(",") if x] if h else []
        names = ",".join(have + [x for x in hide if x not in have])
        body = (body[:h.start()] + f"SubModelsToHide={names}" + body[h.end():] if h
                else f"SubModelsToHide={names}\n" + body)
    return text[:m.end()] + f"[WeaponSystem1{LOADOUT}]\n" + body + text[m.end():]
