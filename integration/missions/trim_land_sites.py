#!/usr/bin/env python3
"""Trim every land site in a mission to its core - and keep every site.

A generated showcase site is a swarm: the airbase, its fuel and ammo, a
command truck, two spare trucks, a tent group, then the builder's layers on
top - a gun ring, six SHORAD vehicles, a NASAMS battery, two Patriot
batteries with their search radars, two EW stations and a THAAD section.
Thirty-five icons where the eye wants one installation. This pass reads a
mission you have edited and saved, and writes a COPY in which each site is
cut back to the things that matter, without moving, retyping or renaming a
single unit that survives:

  keep   the airbase / port / bridge / rig model, one search radar, ONE SAM
         battery (its fire-control radar plus the first --tels launchers),
         the BMD section where a site has one, the fuel farm, the ammo
         dump, a command element, one of each kind of industrial building,
         up to --coastal anti-ship launchers, --tbm ballistic-missile TELs,
         --drones drone launchers, one vehicle of each class in a combat
         group (tank, IFV, APC, gun, MLRS, anti-tank, recon), one SHORAD
         vehicle where nothing longer-ranged is kept
  cut    every gun ring, the SHORAD swarm once a battery is kept, second and
         third batteries with their search radars, spare radars, trucks,
         tent groups, trenches and bunkers, duplicate vehicles, the crowd of
         technicals beyond --technicals

Sites are never deleted. Every formation keeps at least one member (its
first member when that unit carries the site's name), every unit outside a
formation - the bridges and rigs the editor left as stray labelled units -
is kept, and the number of formations per side is checked to be identical
before and after. A launcher is kept only with the radar that guides it, and
the output is re-read and checked against the source before it is written.

Neutral airfields are grounded: every neutral land unit whose file carries
an [AirGroup] (the vanilla airfield_small_1 spawns an E-3A, four P-3Cs and a
dozen fighters by default) gets CustomAirGroup=True with no aircraft lines -
the form the mission editor writes for an emptied base and the form the
shipped missions use. Blue and red air groups are not touched.

The source mission is read, never written; the output is a new file. Every
choice is by rule and file order, so re-running gives the same bytes.

    python3 integration/missions/trim_land_sites.py                       # SEST Banda Front edited -> SEST Banda Front Lean
    python3 integration/missions/trim_land_sites.py --dry-run             # the plan and the numbers, nothing written
    python3 integration/missions/trim_land_sites.py --source "X" --out "Y"
    python3 integration/missions/trim_land_sites.py --tels 4 --no-bmd     # bigger battery, no THAAD
"""
import argparse
import re
import sys
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_land_defence import Mission, unit_info, ad_layer, DOCTRINES    # noqa: E402

MISSIONS = Path(__file__).resolve().parent
SIDES = ("Taskforce1", "Taskforce2", "Neutral")
SOURCE = "SEST Banda Front edited"
OUT = "SEST Banda Front Lean"
# Hand-placed formations whose leaders stand this close are one site, and a
# site keeps one SAM battery. In the Banda Front save a site's own sub-groups
# (the garrison beside its industrial park, the S-400 battalion beside Biak)
# stand 0.4-2.9 nm from the site's leader, and the nearest base that is a
# base of its own (Darwin's fuel terminal, HMAS Coonawarra, Robertson
# Barracks beside RAAF Darwin) stands 3.5 nm off. Batang's coastal battery is
# the one sub-group further out, at 3.6 nm; --cluster-nm 4 folds it into its
# park, and folds Robertson Barracks' SAMP/T into RAAF Darwin, which then
# loses its own NASAMS. The default reads the ask per base.
CLUSTER_NM = 3.0
SITE_NM = 10.0              # a launcher never looks further than this for its radar
AD_LAYER = " Air Defence"   # the builder's layer formations: "<site> Air Defence"
COASTAL_LAYER = " Coastal Battery"

# ---------------------------------------------------------------------------
# What a unit is, for the purpose of deciding whether a site needs it
# ---------------------------------------------------------------------------
VEHICLE_CLASSES = [
    ("mlrs", r"_mlrs_|_phl-|bm-21|_m270"),
    ("arty", r"_spa_|_spc_|_spg_|_2s3|caesar|plz-"),
    ("mbt", r"_mbt_|_lt_"),
    ("ifv", r"_ifv_|_afv_"),
    ("at", r"_td_|_tow$|hj-10"),
    ("apc", r"_apc_|aav7|_m113"),
    ("recon", r"_vbl_|_recon|_arv_"),
    ("truck", r"_car_|_vlfs|_truck"),
]
STATIC_KINDS = [
    ("fuel", r"fueltanks"),
    ("ammo", r"ammo"),
    ("command", r"headquarters|_command$|^fob$"),
    ("comms", r"comm_buildings|radiostation"),
    ("warehouse", r"^warehouses"),
    ("industry:refinery", r"refinery"),
    ("industry:pump", r"oil_pump"),
    ("industry:power", r"powerplant"),
    ("industry:works", r"industry_buildings"),
    ("camp", r"tentgroup"),
    ("fort", r"bunker|trench|watchtower"),
    ("sosus", r"^all_sosus$"),
]
# One of each of these is kept per formation (first in file order).
ONE_EACH = {"fuel", "ammo", "command", "comms", "warehouse", "sosus",
            "industry:refinery", "industry:pump", "industry:power", "industry:works"}
VEHICLE_ONE_EACH = {"mlrs", "arty", "mbt", "ifv", "at", "apc", "recon"}
CAPPED = {"tbm": "tbm", "drone": "drones", "technical": "technicals"}   # kind -> argparse cap
CLASS_RANK = {"area": 3, "medium": 2, "shorad": 1}
# The radars the doctrine tables pair with a BMD launcher (AN/TPY-2 for
# THAAD and so on): a BMD launcher names no guidance system in its file.
BMD_RADARS = {b["radar"] for d in DOCTRINES.values() for era in d.values()
              for b in era.get("bmd", []) if b.get("radar")}
# The search radars the doctrine tables stand up as a site's early warning:
# preferred over a battery's own acquisition radar when one radar is kept.
EW_RADARS = {r for d in DOCTRINES.values() for era in d.values() for r in era.get("ew", [])}


def kind(uid):
    """The trimming category of a land-unit type, from its id and the facts
    build_land_defence reads out of the file the game will load."""
    info = unit_info(uid)
    if info is None:
        sys.exit(f"{uid}: no enabled mod defines this land unit - run tools/preflight.py first")
    low = uid.lower()
    roles = set(info["roles"])
    if low.startswith("civ_car_pickup"):
        return "technical"
    if info["subtype"] == "Airbase" or "Airfield" in roles:
        return "asset"                       # airbases and the FPV drone team, air groups and all
    if info["subtype"] == "Bridge":
        return "asset"
    if info["subtype"] == "OilRig":
        return "asset"
    if info["subtype"] == "Port" and not low.startswith("warehouses"):
        return "asset"                       # docks; the Buildings pack files warehouses as Port
    for k, pat in STATIC_KINDS:
        if re.search(pat, low):
            return k
    if "sam_site" in low:
        return "sam_site"                    # a whole battery in one model
    if info["bmd"]:
        return "bmd_tel"
    if re.search(r"shahed|dronesquad", low):
        return "drone"
    if re.search(r"df-(?!10)\d|ss-26|scud|sejjil", low) and info["subtype"] == "MobileUnit":
        return "tbm"                         # DF-15/21/26, Iskander, Scud, Sejjil; the DF-10A is a cruise missile
    if re.search(VEHICLE_CLASSES[0][1], low):
        return "mlrs"
    if info["subtype"] == "MissileSite":
        return "coastal"                     # Harpoon, YJ, Bal, Bastion, Redut launchers
    if info["subtype"] == "MobileUnit" and ({"ASuW", "ASM"} & roles) and info["max_aaw_nm"] is None \
            and any(t == "Missile" for t, _ in info["weapons"]):
        return "coastal"                     # YJ-12/62, CJ-10, DF-10A launch vehicles
    if "coastal_artillery" in low:
        return "coastal"
    if info["guidance"]:
        return "tel"                         # a launcher that fires only with a battery radar
    layer = ad_layer(info)
    if layer == "aaa":
        return "aaa"
    if layer == "shorad":
        return "shorad"
    if layer in ("medium", "area"):
        return "self_sam"                    # SAMP/T, Buk, Rapier: launcher and radar in one
    if info["subtype"] == "Radar" or low.endswith("_radar") or "radar" in low or \
            (not info["weapons"] and info["radars"]):
        return "radar"
    for k, pat in VEHICLE_CLASSES:
        if re.search(pat, low):
            return k
    return "other"


# ---------------------------------------------------------------------------
class Side:
    """One side's land units and formations, classified and bound together."""

    def __init__(self, mission, side, cluster_nm=CLUSTER_NM):
        self.m, self.side, self.geo = mission, side, mission.geo
        self.units = OrderedDict()
        for name, ty, x, z, body in mission.units(side, "LandUnit"):
            self.units[name] = {"name": name, "type": ty, "x": x, "z": z, "body": body, "kind": kind(ty),
                                "info": unit_info(ty), "formation": None, "fcr": None, "tels": [],
                                "named": mission.name_override(name) is not None}
        self.forms = []
        labels = {}
        for fi, (_, key, members, tail) in enumerate(mission.formation_specs(side)):
            label = tail.split("|")[1] if tail.count("|") >= 1 else ""
            land = [u for u in members if u in self.units]
            if not land:
                continue                     # a ship group
            for u in land:
                if self.units[u]["formation"] is not None:
                    sys.exit(f"{side}: {u} is in two formations")
                self.units[u]["formation"] = len(self.forms)
            self.forms.append({"key": key, "label": label, "members": land, "kind": "site",
                               "site": None, "cluster": None, "keep": OrderedDict(), "batteries": []})
            labels[label] = len(self.forms) - 1
        # the builder's layer formations belong to the site they are named for
        for f in self.forms:
            for suffix, lk in ((AD_LAYER, "ad"), (COASTAL_LAYER, "coastal")):
                if f["label"].endswith(suffix) and f["label"][:-len(suffix)] in labels:
                    f["kind"], f["site"] = lk, labels[f["label"][:-len(suffix)]]
        self.strays = [u for u in self.units.values() if u["formation"] is None]
        self._cluster(cluster_nm)
        self._bind_guidance()

    def sites(self):
        """[[formation labels]] for every site made of more than one formation."""
        by = OrderedDict()
        for f in self.forms:
            by.setdefault(f["cluster"], []).append(f["label"])
        return [labels for labels in by.values() if len(labels) > 1]

    # --- who guides whom -------------------------------------------------
    def dist(self, a, b):
        return self.geo.dist(a["x"], a["z"], b["x"], b["z"])

    def _bind_guidance(self):
        """Every launcher that needs an external radar is bound to the radar
        that guides it: the nearest radar of this side providing the system
        the launcher names, preferring one in the launcher's own formation,
        then one at the same site, never further than SITE_NM. Distance is
        not a criterion beyond that - the editor lays a saved formation out
        as rings at its spacing, so a launcher can stand miles from the radar
        it was planned around and still be that radar's launcher. A BMD
        launcher, which names no guidance system, takes the nearest radar of
        a type the doctrine tables pair with it."""
        radars = [u for u in self.units.values() if u["kind"] in ("radar", "sam_site")]

        def cluster_of(u):
            return self.forms[u["formation"]]["cluster"] if u["formation"] is not None else None

        for u in self.units.values():
            if u["info"]["guidance"]:
                ok = [r for r in radars if r["info"]["radars"] & u["info"]["guidance"]]
            elif u["kind"] == "bmd_tel":
                ok = [r for r in radars if r["type"] in BMD_RADARS]
            else:
                continue
            cands = sorted((r["formation"] != u["formation"], cluster_of(r) != cluster_of(u),
                            self.dist(u, r), r["name"]) for r in ok if self.dist(u, r) <= SITE_NM)
            if cands:
                u["fcr"] = cands[0][3]
                self.units[u["fcr"]]["tels"].append(u["name"])

    def in_reach(self, u):
        """Whether a launcher stands inside its radar's guidance radius."""
        r = u["info"]["guidance_radius"]
        return u["fcr"] is not None and (r is None or self.dist(u, self.units[u["fcr"]]) <= r + 1e-6)

    def batteries(self):
        """Every SAM battery on the side: [(class, range, order, home
        formation, radar name or None, [launcher names])], launchers with
        the radar's own formation first."""
        out = []
        order = {n: i for i, n in enumerate(self.units)}
        for u in self.units.values():
            if u["kind"] == "radar" and u["tels"] and \
                    any(self.units[t]["kind"] == "tel" for t in u["tels"]):
                tels = [t for t in u["tels"] if self.units[t]["kind"] == "tel"]
                tels.sort(key=lambda t: (self.units[t]["formation"] != u["formation"], order[t]))
                cls = max((ad_layer(self.units[t]["info"]) or "shorad" for t in tels),
                          key=lambda c: CLASS_RANK.get(c, 0))
                rng = max((self.units[t]["info"]["max_aaw_nm"] or 0.0) for t in tels)
                out.append((cls, rng, order[u["name"]], u["formation"], u["name"], tels))
            elif u["kind"] == "sam_site":
                out.append((ad_layer(u["info"]) or "area", u["info"]["max_aaw_nm"] or 0.0,
                            order[u["name"]], u["formation"], None, [u["name"]]))
        seen = set()
        for u in self.units.values():          # self-contained launchers, grouped by type per formation
            if u["kind"] != "self_sam" or (u["formation"], u["type"]) in seen:
                continue
            seen.add((u["formation"], u["type"]))
            group = [v["name"] for v in self.units.values()
                     if v["kind"] == "self_sam" and v["formation"] == u["formation"] and v["type"] == u["type"]]
            out.append((ad_layer(u["info"]), u["info"]["max_aaw_nm"] or 0.0, order[u["name"]],
                        u["formation"], None, group))
        return out

    def bmd_batteries(self):
        """[(home formation, radar or None, [launcher names])] for the BMD sections."""
        groups = OrderedDict()
        for u in self.units.values():
            if u["kind"] == "bmd_tel":
                groups.setdefault(u["fcr"] or ("solo", u["formation"]), []).append(u["name"])
        out = []
        for key, tels in groups.items():
            radar = None if isinstance(key, tuple) else key
            home = self.units[radar]["formation"] if radar else self.units[tels[0]]["formation"]
            out.append((home, radar, tels))
        return out

    # --- which formations make one site ------------------------------------
    def _cluster(self, radius):
        """Hand-placed formations whose leaders stand within `radius` nm of
        each other are one site; a builder layer joins the site it is named for."""
        parent = list(range(len(self.forms)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        # a formation stands where its first member stands: the generator put
        # every group's leader within a mile of the site centre, and the editor
        # leaves the leader in place when it lays the rest out as rings
        cx = {}
        for i, f in enumerate(self.forms):
            if f["kind"] == "site":
                lead = self.units[f["members"][0]]
                cx[i] = (lead["x"], lead["z"])
        for i in cx:
            for j in cx:
                if i < j and self.geo.dist(*cx[i], *cx[j]) <= radius:
                    parent[find(i)] = find(j)
        for i, f in enumerate(self.forms):
            if f["kind"] != "site":
                parent[find(i)] = find(f["site"])
        for i, f in enumerate(self.forms):
            f["cluster"] = find(i)


def b_first(b):
    """The unit that identifies a kept battery: its radar, else its first launcher."""
    return b[2] or b[3][0]


# ---------------------------------------------------------------------------
class Trimmer:
    def __init__(self, side, args):
        self.s, self.a = side, args
        self.notes = []
        self.kept_batteries = []       # (formation, cls, radar, kept launchers)
        self.hand_battery_cls = {}     # cluster -> best class kept in a hand-placed formation
        self.hand_ew = set()           # clusters where a hand-placed formation keeps a radar
        self.bound_radars = set()      # radars spoken for by a kept battery or BMD section

    def rank(self, b):
        return (CLASS_RANK.get(b[0], 0), b[1], -b[2])

    def decide(self):
        s = self.s
        # 1. batteries: one per hand-placed formation, then one per layer where the site has none
        by_home = {}
        for b in s.batteries():
            by_home.setdefault(b[3], []).append(b)
        for fi, f in enumerate(s.forms):
            if f["kind"] == "site" and by_home.get(fi):
                best = max(by_home[fi], key=self.rank)
                self.keep_battery(fi, best)
                c = f["cluster"]
                if best[0] in ("area", "medium"):
                    self.hand_battery_cls[c] = best[0]
        for fi, f in enumerate(s.forms):
            if f["kind"] == "ad" and by_home.get(fi):
                best = max(by_home[fi], key=self.rank)
                if f["cluster"] in self.hand_battery_cls and best[0] in ("area", "medium"):
                    own = next(b for b in self.kept_batteries
                               if s.forms[b[0]]["cluster"] == f["cluster"] and b[1] in ("area", "medium"))
                    self.notes.append(f"{f['label']}: its {best[0]} battery goes, the site keeps its own "
                                      f"{s.units[b_first(own)]['type']} battery in {s.forms[own[0]]['label']!r}")
                elif best[0] in ("area", "medium"):
                    self.keep_battery(fi, best)
                # a shorad-class "battery" here is a Tor/HQ-17 pair; the shorad rule below decides
        # 2. BMD sections
        if self.a.keep_bmd:
            for home, radar, tels in s.bmd_batteries():
                f = s.forms[home]
                if radar:
                    f["keep"][radar] = "bmd radar"
                    self.bound_radars.add(radar)
                for t in tels[:2]:
                    f["keep"][t] = "bmd launcher"
                self.kept_batteries.append((home, "bmd", radar, tels[:2]))
        else:
            for home, radar, tels in s.bmd_batteries():
                if radar:
                    self.bound_radars.add(radar)          # never mistaken for the search radar
        # 3. everything else, formation by formation: hand-placed first so the layers can defer to them
        for fi, f in enumerate(s.forms):
            if f["kind"] == "site":
                self.trim_formation(fi)
        for fi, f in enumerate(s.forms):
            if f["kind"] != "site":
                self.trim_formation(fi)
        # 4. a kept launcher keeps the radar that guides it, wherever that radar stands
        for f in s.forms:
            for u in list(f["keep"]):
                fcr = s.units[u]["fcr"]
                if fcr and s.units[u]["kind"] != "bmd_tel":
                    home = s.forms[s.units[fcr]["formation"]]
                    home["keep"].setdefault(fcr, f"guides {s.units[u]['type']}")
                    self.bound_radars.add(fcr)

    def keep_battery(self, fi, b):
        cls, rng, _, home, radar, tels = b
        f = self.s.forms[fi]
        if radar:
            f["keep"][radar] = f"{cls} battery radar"
            self.bound_radars.add(radar)
        kept = tels if radar is None and len(tels) == 1 and self.s.units[tels[0]]["kind"] == "sam_site" \
            else tels[:self.a.tels]
        for t in kept:
            self.s.forms[self.s.units[t]["formation"]]["keep"][t] = f"{cls} battery launcher"
        self.kept_batteries.append((fi, cls, radar, kept))

    def trim_formation(self, fi):
        s, a = self.s, self.a
        f = s.forms[fi]
        keep = f["keep"]
        units = [s.units[u] for u in f["members"]]
        first = units[0]
        if f["kind"] == "site" or first["named"]:
            keep.setdefault(first["name"], "carries the site name")
        cluster = f["cluster"]
        # what this formation (hand-placed) or this site (a layer) already keeps
        if f["kind"] == "site":
            has_battery = any(b[0] == fi and b[1] != "bmd" for b in self.kept_batteries)
        else:
            has_battery = any(b[1] != "bmd" and s.forms[b[0]]["cluster"] == cluster for b in self.kept_batteries)
        seen_one = {s.units[u]["kind"] for u in keep}
        seen_type = {}
        count = {}
        for u in keep:
            k = s.units[u]["kind"]
            if k in CAPPED or k == "coastal":
                count[k] = count.get(k, 0) + 1
                seen_type.setdefault(k, set()).add(s.units[u]["type"])
        # the search radar: one per hand-placed formation, and one in a layer
        # only where the site has none yet. A radar that guides launchers is a
        # battery's, not the site's eyes; prefer the doctrine tables' early-
        # warning types, then a named radar, then file order.
        free = [u for u in units if u["kind"] == "radar" and not u["tels"] and u["name"] not in self.bound_radars]
        has_free = any(s.units[u]["kind"] == "radar" and not s.units[u]["tels"] for u in keep)
        want_ew = f["kind"] == "site" or cluster not in self.hand_ew
        if want_ew and free and not has_free:
            pick = min(free, key=lambda u: (u["type"] not in EW_RADARS, not u["named"], units.index(u)))
            keep[pick["name"]] = "search radar"
            has_free = True
        if f["kind"] == "site" and has_free:
            self.hand_ew.add(cluster)
        # armed technicals before the pickup with nothing on the back
        ordered = sorted(units, key=lambda u: (u["kind"] == "technical" and not u["info"]["weapons"]))
        for u in ordered:
            k = u["kind"]
            if u["name"] in keep:
                continue
            if k in ("asset", "other"):
                keep[u["name"]] = "the installation" if k == "asset" else "unclassified, kept"
            elif k in ONE_EACH or k in VEHICLE_ONE_EACH:
                if k not in seen_one:
                    seen_one.add(k)
                    keep[u["name"]] = k
            elif k == "coastal":
                if count.get(k, 0) < a.coastal:
                    count[k] = count.get(k, 0) + 1
                    keep[u["name"]] = "coastal launcher"
            elif k in CAPPED:
                if count.get(k, 0) < getattr(a, CAPPED[k]) and u["type"] not in seen_type.setdefault(k, set()):
                    seen_type[k].add(u["type"])
                    count[k] = count.get(k, 0) + 1
                    keep[u["name"]] = k
            # tel / self_sam / sam_site / bmd_tel / radar: the battery passes decided; aaa, camp,
            # fort, truck and shorad: cut unless kept below
        for u in ordered:      # the caps allow a second of a type once every type is in
            k = u["kind"]
            if u["name"] in keep or k not in CAPPED:
                continue
            if count.get(k, 0) < getattr(a, CAPPED[k]):
                count[k] = count.get(k, 0) + 1
                keep[u["name"]] = k
        # one SHORAD vehicle where nothing longer-ranged defends the site
        if not has_battery:
            shorad = next((u for u in units if u["kind"] == "shorad"), None)
            if shorad:
                keep.setdefault(shorad["name"], "shorad, the only air defence here")
        # never empty: keep the most meaningful unit there is
        if not keep:
            fallback = sorted(units, key=lambda u: ({"radar": 0, "shorad": 1, "self_sam": 2, "tel": 3,
                                                     "aaa": 4}.get(u["kind"], 5),
                                                    bool(u["tels"]), not u["named"], units.index(u)))
            keep[fallback[0]["name"]] = "kept so the formation survives"
            self.notes.append(f"{f['label']}: down to one unit ({fallback[0]['type']})")

    def removals(self):
        out = []
        for f in self.s.forms:
            out.extend(u for u in f["members"] if u not in f["keep"])
        return out


# ---------------------------------------------------------------------------
def ground_neutral_air(mission, side_obj):
    """CustomAirGroup=True with nothing under it on every neutral land unit
    whose file can spawn aircraft. Returns [(section, type, what it spawned)]."""
    done = []
    for u in side_obj.units.values():
        text = u["info"]["file"].read_text(encoding="utf-8", errors="replace")
        declared, lines = mission.air_group(u["name"])
        if "[AirGroup]" not in text and "[FlightDeck]" not in text and not (declared or lines):
            continue
        if declared and not lines:
            continue                          # already grounded
        before = ", ".join(f"{a}={s}" for a, s in lines) if lines else "the unit file's default [AirGroup]"
        mission.set_custom_air_group(u["name"], ())
        done.append((u["name"], u["type"], before))
    return done


def check_guidance(side_obj, kept):
    """Every kept launcher that needs a radar keeps the radar that guides it.
    Returns (bugs, notes, launchers kept, of which outside their radar's
    guidance radius) - the reach figure describes the source's geometry,
    which the trim leaves exactly as it is."""
    problems, orphans, n, far = [], [], 0, 0
    for name in kept:
        u = side_obj.units[name]
        if not u["info"]["guidance"]:
            continue
        n += 1
        if u["fcr"] is None:
            orphans.append(f"{u['name']} ({u['type']}) has no radar for {sorted(u['info']['guidance'])} "
                           f"within {SITE_NM:.0f} nm in the source either")
        elif u["fcr"] not in kept:
            problems.append(f"{u['name']} ({u['type']}) kept without its radar {u['fcr']}")
        elif not side_obj.in_reach(u):
            far += 1
    return problems, orphans, n, far


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=SOURCE, help=f"mission to read, without .ini (default: {SOURCE!r})")
    ap.add_argument("--out", default=OUT, help=f"mission to write, without .ini (default: {OUT!r})")
    ap.add_argument("--tels", type=int, default=3, help="launchers kept per SAM battery (default 3)")
    ap.add_argument("--coastal", type=int, default=2, help="anti-ship launchers kept per formation (default 2)")
    ap.add_argument("--tbm", type=int, default=2, help="ballistic-missile TELs kept per formation (default 2)")
    ap.add_argument("--drones", type=int, default=2, help="drone launchers kept per formation (default 2)")
    ap.add_argument("--technicals", type=int, default=2, help="technicals kept per formation (default 2)")
    ap.add_argument("--cluster-nm", type=float, default=CLUSTER_NM,
                    help=f"formations whose leaders stand this close are one site (default {CLUSTER_NM})")
    ap.add_argument("--no-bmd", dest="keep_bmd", action="store_false",
                    help="cut the THAAD / BMD sections too (default: keep radar + 2 launchers)")
    ap.add_argument("--keep-neutral-air", action="store_true",
                    help="leave neutral air groups alone (default: ground every neutral base)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan and the numbers, write nothing")
    return ap.parse_args()


def main():
    a = parse_args()
    src = MISSIONS / f"{a.source}.ini"
    out = MISSIONS / f"{a.out}.ini"
    if not src.exists():
        sys.exit(f"no such mission: {src}")
    if out.resolve() == src.resolve() or a.out == a.source:
        sys.exit("the output must be a different mission from the source - the source is never written")
    for n, v in (("tels", a.tels), ("coastal", a.coastal), ("tbm", a.tbm), ("drones", a.drones),
                 ("technicals", a.technicals)):
        if v < 1:
            sys.exit(f"--{n} must be at least 1")

    mission = Mission(src)
    problems = mission.verify()
    if problems:
        sys.exit(f"{src.name} fails its own checks before anything is done:\n  " + "\n  ".join(problems))
    before = {side: len(mission.units(side, "LandUnit")) for side in SIDES}
    forms_before = {side: [(k, t) for _, k, _, t in mission.formation_specs(side)] for side in SIDES}
    src_bodies = {}
    for side in SIDES:
        for name, ty, x, z, body in mission.units(side, "LandUnit"):
            src_bodies[name] = body

    print(f"source: {src.name}   ->   {out.name}")
    print(f"tels {a.tels}  coastal {a.coastal}  tbm {a.tbm}  drones {a.drones}  technicals {a.technicals}"
          f"  bmd {'kept' if a.keep_bmd else 'cut'}  neutral air {'left' if a.keep_neutral_air else 'grounded'}\n")

    sides, removals, kept_names, grounded, reach = {}, {}, {}, [], {}
    for side in SIDES:
        s = Side(mission, side, a.cluster_nm)
        t = Trimmer(s, a)
        t.decide()
        sides[side] = (s, t)
        removals[side] = t.removals()
        kept_names[side] = set(s.units) - set(removals[side])
        print(f"===== {side}: {len(s.forms)} formations, {len(s.strays)} stray labelled unit(s) kept as they are")
        for labels in s.sites():
            print(f"  site: {' + '.join(repr(l) for l in labels)}")
        for f in s.forms:
            kept = [u for u in f["members"] if u in f["keep"]]
            cut = [u for u in f["members"] if u not in f["keep"]]
            tag = {"site": "", "ad": "  [layer]", "coastal": "  [layer]"}[f["kind"]]
            print(f"  {f['label']!r}{tag}: {len(f['members'])} -> {len(kept)}")
            print("      keep: " + ", ".join(f"{s.units[u]['type']}" for u in kept))
            if cut:
                print("      cut:  " + ", ".join(f"{s.units[u]['type']}" for u in cut))
        for n in t.notes:
            print(f"  note: {n}")
        bad, orphans, n_guided, n_far = check_guidance(s, kept_names[side])
        for o in orphans:
            print(f"  note: {o}")
        if bad:
            sys.exit(f"{side}: launchers left without their radar - this is a bug in the trimmer:\n  "
                     + "\n  ".join(bad))
        reach[side] = (n_guided, n_far)
        print()

    # --- apply ---------------------------------------------------------------
    for side in SIDES:
        mission.remove_land_units(side, removals[side])
    if not a.keep_neutral_air:
        grounded = ground_neutral_air(mission, Side(mission, "Neutral", a.cluster_nm))
    mission.set_name(a.out)
    desc = re.search(r"^Description=(.*)$", mission.body("[Language_en]"), re.M)
    if desc:
        mission.set_description(desc.group(1).rstrip(". ") +
                                ". Lean edition: every site trimmed to its core, neutral airfields grounded.")
    problems = mission.verify()
    if problems:
        sys.exit("NOT written - the result fails its own checks:\n  " + "\n  ".join(problems))

    # --- prove the result against the source before writing --------------------
    after = {side: len(mission.units(side, "LandUnit")) for side in SIDES}
    forms_after = {side: [(k, t) for _, k, _, t in mission.formation_specs(side)] for side in SIDES}
    for side in SIDES:
        if forms_before[side] != forms_after[side]:
            sys.exit(f"{side}: formation keys or labels changed - refusing to write")
        s, t = sides[side]
        new_bodies = {name: body for name, ty, x, z, body in mission.units(side, "LandUnit")}
        # every kept unit is there, in the same order, byte for byte (air group aside)
        expect = [n for n in s.units if n in kept_names[side]]
        got = list(new_bodies)
        if len(got) != len(expect):
            sys.exit(f"{side}: expected {len(expect)} units after trimming, found {len(got)}")
        strip = lambda b: "\n".join(l for l in b.split("\n")
                                    if not (l.startswith("CustomAirGroup=") or Mission.AIRGROUP_LINE.match(l)))
        for old, new in zip(expect, got):
            if src_bodies[old] != new_bodies[new] and strip(src_bodies[old]) != strip(new_bodies[new]):
                sys.exit(f"{side}: {old} -> {new} body changed - refusing to write")
        for u in s.strays:
            if u["body"] not in new_bodies.values() and strip(u["body"]) not in map(strip, new_bodies.values()):
                sys.exit(f"{side}: stray unit {u['name']} ({u['type']}) lost - refusing to write")
    live = []
    if not a.keep_neutral_air:
        for name, ty, *_ in mission.units("Neutral", "LandUnit"):
            declared, lines = mission.air_group(name)
            text = unit_info(ty)["file"].read_text(encoding="utf-8", errors="replace")
            capable = "[AirGroup]" in text or "[FlightDeck]" in text
            if lines or (capable and not declared):
                live.append(f"{name} ({ty})")
        if live:
            sys.exit("neutral land units still able to spawn aircraft:\n  " + "\n  ".join(live))

    # --- report ----------------------------------------------------------------
    print("===== summary")
    print(f"  {'side':12} {'formations':>10} {'strays':>7} {'units before':>13} {'after':>6}")
    for side in SIDES:
        s, _ = sides[side]
        print(f"  {side:12} {len(s.forms):>10} {len(s.strays):>7} {before[side]:>13} {after[side]:>6}")
    tot_b, tot_a = sum(before.values()), sum(after.values())
    n_forms = sum(len(sides[s][0].forms) for s in SIDES)
    n_strays = sum(len(sides[s][0].strays) for s in SIDES)
    print(f"  {'total':12} {n_forms:>10} {n_strays:>7} {tot_b:>13} {tot_a:>6}   "
          f"({100 * (tot_b - tot_a) / tot_b:.0f}% of the land units cut, "
          f"{n_forms + n_strays} sites before and after)")
    n_guided, n_far = sum(v[0] for v in reach.values()), sum(v[1] for v in reach.values())
    if n_far:
        print(f"  note: {n_far} of the {n_guided} kept launchers that need a battery radar stand outside its "
              f"guidance radius. That is the source's geometry (the editor lays a saved formation out as "
              f"rings at its spacing) and the trim moves nothing.")
    if grounded:
        print(f"  neutral bases grounded: {len(grounded)}")
        for name, ty, what in grounded:
            print(f"      {name:20} {ty:22} was spawning {what}")
    if a.dry_run:
        print("\ndry run - nothing written")
        return
    out.write_bytes(mission.text().encode("utf-8"))
    print(f"\nwritten: {out}")
    check = Mission(out).verify()
    if check:
        sys.exit("the written file fails verify() on re-read:\n  " + "\n  ".join(check))


if __name__ == "__main__":
    main()
