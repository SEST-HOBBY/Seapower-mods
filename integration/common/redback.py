"""The SEST Redback fit (SEST_REDBACK), added the same way to every carrier.

The AGR-30 Redback is SEST's one upgraded 70mm guided rocket (round and pod in
SEST Allied Fixes: sest_agr-30, sest_agr-30_pod). The decision of 19 Oct 2026
put it on every A-10, Apache, Seahawk, F-16 and Hornet SEST fields, and an
aircraft's file can only be shipped by one SEST pack - so the A-10C+, the
F-16CM and the US Super Hornets get the fit from their own pack's builder,
and everything else from Allied Fixes. This module is the one recipe they
share: clone a fit the aircraft already flies, put Redback pods on the
pylons it names, keep everything else on that fit as the author hung it.
"""
import re
import sys

LOADOUT = "SEST_REDBACK"
POD = "sest_agr-30_pod"


def add_fit(text, unit, donor, swaps):
    """`text` with SEST_REDBACK declared and its block after `donor`'s.

    swaps: (store id, "pod" or None, how many) - every station line hanging
    that store becomes a Redback pod (the seat suffix after `|` is kept, as
    the pylon's mount), or with None is dropped from the fit; the count must
    match exactly, so an upstream change to the donor stops the build.
    """
    if re.search(rf"^\[WeaponSystem1{LOADOUT}\]", text, re.M):
        sys.exit(f"{unit}: {LOADOUT} is already defined - re-check upstream")
    text, n = re.subn(r"^(AvailableLoadouts=[^\r\n]*?)(\s*)$", rf"\1,{LOADOUT}\2",
                      text, count=1, flags=re.M)
    if n != 1:
        sys.exit(f"{unit}: AvailableLoadouts line not found")
    # searched after the edit above: offsets held across it go stale
    m = re.search(rf"^\[WeaponSystem1{re.escape(donor)}\][^\n]*\n(.*?)(?=^\[)",
                  text, re.M | re.S)
    if not m:
        sys.exit(f"{unit}: donor fit {donor} not found - upstream changed")
    body = m.group(1)
    for store, to, need in swaps:
        line = rf"^(Station\d+=){re.escape(store)}((?:\|[^\r\n]*)?)(\r?\n|$)"
        if to == "pod":
            body, k = re.subn(line, rf"\g<1>{POD}\g<2>\g<3>", body, flags=re.M)
        else:
            body, k = re.subn(line, "", body, flags=re.M)
        if k != need:
            sys.exit(f"{unit}/{donor}: {k} station(s) hang {store}, expected {need} "
                     "- upstream changed the fit")
    if POD not in body:
        sys.exit(f"{unit}/{donor}: no Redback pod in the derived fit")
    return text[:m.end()] + f"[WeaponSystem1{LOADOUT}]\n" + body + text[m.end():]
