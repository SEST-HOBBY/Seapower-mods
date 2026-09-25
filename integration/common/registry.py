"""Keep an upstream registry file from renaming the whole game.

`language_*/loadout_names.ini` has ONE section, `[LoadoutNames]`, so every key
in it is a global loadout id shared by every aircraft that offers that
loadout. `Strike` is not the F-35A's strike loadout - it is the strike loadout
of 212 aircraft files across this collection, `AntiShip` of 159, `AirToAir`
of 180.

The RAAF F-35A upstream (3514484654) renames six of those generic ids to
F-35A-specific text - `AntiShip=Anti-Ship JMS (Internal Only)`,
`Strike=Close Air Support (Full Payload)`, and `AirToAir=Ait-to-air (Full
Payload)`, typo included. The packs here copied that file wholesale to inherit
its F-35A loadout names, which meant a French Alouette II's anti-ship fit
displayed as "Anti-Ship JMS (Internal Only)". The US Naval Aviation Chinese
file does the same to eighteen ids, including the cargo types on merchant
ships: `Oil`, `Ore`, `Troops`, `Fertilizer`.

Being ABOVE everything makes it worse, not better. A SEST pack sits at the top
of the load order by design, so its copy of a key beats the upstream's and the
base game's alike - and a pack that carries the upstream's rename forward has
guaranteed it wins.

So: keys the upstream INVENTED are carried through, because that is the point
of copying the file. Keys the base game already defines are restored to the
base game's value. That is a repair rather than a removal - dropping the line
would only hand the key back to the upstream mod, which is still installed and
still above vanilla. Writing the vanilla value at priority one is what
actually puts the names back.
"""
import re


def vanilla_values(path):
    """{key: value} of a single-section registry file, comments stripped."""
    out = {}
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        s = line.strip()
        if s.startswith(("#", ";", "[")) or "=" not in s:
            continue
        key, _, value = s.partition("=")
        out[key.strip()] = value
    return out


def restore_vanilla(body, vanilla_path, keep=(), label=""):
    """Rewrite `body` so no line redefines a value the base game already sets.

    `keep` is the ids the pack means to define itself; they are left alone even
    if the base game happens to use the same name. Returns (text, [repaired]).
    """
    van = vanilla_values(vanilla_path)
    keep = set(keep)
    repaired, out = [], []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith(("#", ";", "[")) or "=" not in s:
            out.append(line)
            continue
        key, _, value = s.partition("=")
        key = key.strip()
        if key in keep or key not in van:
            out.append(line)
            continue
        # Compare on the visible text only: vanilla carries trailing `//`
        # comments on most of these and the upstream does not.
        mine = value.split("//")[0].strip()
        theirs = van[key].split("//")[0].strip()
        if mine == theirs:
            out.append(line)
            continue
        repaired.append((key, mine, theirs))
        out.append(f"{key}={van[key].rstrip()}")
    if repaired and label:
        print(f"  {label}: restored {len(repaired)} base-game name(s) the "
              f"upstream had renamed globally - "
              + ", ".join(k for k, _, _ in repaired))
    return "\n".join(out), repaired


def rewrite_values(body, mapping, label=""):
    """Replace the VALUE of keys already present in `body`, in place.

    Appending a second definition of the same key would rely on last-wins
    inside one file, which nothing here has established. Rewriting the line the
    upstream already wrote does not.

    The case this exists for: the dingtools F-15EX upstream ships
    `StrikeJSOW=StrikeJSOW` and `Strike183=StrikeARRW` - the internal id as its
    own display text - so the English loadout picker lists raw identifiers
    while the same mod's Chinese file gives them proper names. A SEST pack sits
    above every mod that spells them better, so SEST's copy is the one a player
    reads.
    """
    done, out = [], []
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith(("#", ";", "[")) and "=" in s:
            key = s.partition("=")[0].strip()
            if key in mapping:
                done.append(key)
                out.append(f"{key}={mapping[key]}")
                continue
        out.append(line)
    if done and label:
        print(f"  {label}: named {len(done)} loadout(s) the upstream left as "
              f"raw identifiers - " + ", ".join(done))
    return "\n".join(out), done
