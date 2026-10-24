"""Complete, explicitly estimated cost coverage without changing equipment.

The conservative mapper in costs.py remains a distinct first stage. This stage
implements the owner's 24 October request to fill *all* remaining prices,
including author blanks, while preserving every previously usable field.
Nothing in this module calls acquisition points dollars. Rough models are
labelled, ranged and traceable to a versioned policy; they are not verified
procurement quotations. Land costs belong to SEST's own accounting plugin.
"""
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import copy
import csv
import io
import json
import re

from . import costs

LAND = ("land_units", "sest_land_costs", "LandCosts", "LandCostCategory")
CATEGORY_RE = re.compile(r"[A-Za-z0-9 _-]{1,20}\Z", re.ASCII)
DEFAULT_CATEGORIES = {
    "missile": "Other", "asroc": "ASW", "rbu": "ASW", "airdepthcharge": "ASW",
    "torpedo": "Torpedo", "bomb": "Bomb", "projectile": "Gun", "aerialrocket": "Rocket",
    "mlrs": "Rocket", "chaff": "Decoy", "noisemaker": "Decoy", "moss": "Decoy",
    "sonobuoy": "Sonobuoy", "fueltank": "Fuel tank", "container": "Pod",
    "paratrooper": "Ignore",
}

# Explicit design/family/role comparators. These deliberately avoid
# name collisions such as the modern RAN Supply and the old Battle-class Anzac.
# The inherited historical series keeps its donor's reference-year basis.
FAMILIES = {
    "weapon": [
        (r"aim[-_]?424|malice", r"^usn_aim-174b$"),
        (r"aim[-_]?120b", r"aim[-_]?120b(?:$|_)"),
        (r"aim[-_]?120c[-_]?5", r"aim[-_]?120c[-_]?5(?:$|_)"),
        (r"aim[-_]?120c[-_]?7", r"aim[-_]?120c[-_]?7(?:$|_)"),
        (r"aim[-_]?120d", r"aim[-_]?120d(?:$|_)"),
        (r"aim[-_]?260", r"aim[-_]?260(?:$|_)"),
        (r"aam[-_]?3(?:$|_)", r"aim[-_]?9m(?:$|_)"),
        (r"aam[-_]?4", r"aim[-_]?120c[-_]?7(?:$|_)"),
        (r"asm[-_]?3", r"yj[-_]?12(?:_|$)"),
        (r"(?:akk[-_]?90|ty[-_]?90)", r"^usn_aim-9x$"),
        (r"akd[-_]?10", r"agm[-_]?114k(?:_|$)"),
        (r"apkws|agr[-_]?20", r"apkws"),
        (r"agm[-_]?183|arrw", r"^usn_arrw$"),
        (r"gbu[-_]?31.*v4", r"gbu[-_]?31v4"),
        (r"gbu[-_]?31", r"gbu[-_]?31v1"),
        (r"gbu[-_]?32", r"gbu[-_]?32"),
        (r"gbu[-_]?38", r"gbu[-_]?38"),
        (r"gbu[-_]?12", r"^usn_gbu-12d$"),
        (r"gbu[-_]?24", r"^usn_gbu-24$"),
        (r"(?:am|mm|sm)[-_]?39", r"(?:am|mm|sm)[-_]?39"),
        (r"mm[-_]?40", r"mm[-_]?40"),
        (r"rim[-_]?162", r"rim[-_]?162"),
        (r"mk[-_]?48", r"mk[-_]?48"),
        (r"mk[-_]?46", r"mk[-_]?46"),
        (r"mk[-_]?54", r"mk[-_]?54"),
    ],
    "vessel": [
        (r"arleigh.*flt2a", r"arleigh.*flight2a_2026$"),
        (r"arleigh.*flt1", r"arleigh.*flight1_2025$"),
        (r"arleigh", r"arleigh.*flight2a_2026$"),
        (r"bunker.hill", r"ticonderoga.*(?:vls|1986)"),
        (r"spruance", r"spruance"),
        (r"nimitz", r"nimitz"),
        (r"seawolf", r"seawolf"),
        (r"ohio", r"ohio"),
        (r"victor3", r"victor.*3|victor3"),
        (r"udaloy2", r"udaloy"),
        (r"grisha4", r"grisha"),
        (r"james.madison|franklin", r"franklin|james.madison"),
        (r"charles.de.gaulle", r"charles.de.gaulle"),
        (r"canberra", r"canberra|juan.carlos"),
        (r"jacinto", r"peacock"),
        (r"cannon", r"cannon"),
        (r"hamilton", r"hamilton"),
        (r"oliver.hazard.perry", r"oliver.hazard.perry"),
        (r"054a", r"054a"),
        (r"s.26p", r"039a|yuan"),
        (r"takatsuki", r"takatsuki"),
        (r"hatsuyuki", r"hatsuyuki"),
        (r"tachikaze", r"tachikaze"),
        (r"type.021", r"type.021|huangfeng"),
        (r"adelaide", r"adelaide"),
        (r"quickmatch", r"river|rothesay"),
    ],
    "aircraft": [
        (r"f[-_]?35b", r"f[-_]?35b"), (r"f[-_]?35a", r"f[-_]?35a"),
        (r"ea[-_]?18g", r"ea[-_]?18g"),
        (r"fa?[-_]?18a", r"f/?a?[-_]?18a"),
        (r"f[-_]?111", r"f[-_]?111"), (r"f[-_]?14b", r"f[-_]?14b"),
        (r"f[-_]?15k", r"f[-_]?15e"), (r"kf[-_]?16|f[-_]?16c", r"f[-_]?16c"),
        (r"f[-_]?4e", r"f[-_]?4e"), (r"f[-_]?5e", r"f[-_]?5e"),
        (r"f[-_]?2a", r"f[-_]?2a"), (r"av[-_]?8b.*plus|av[-_]?8b\+", r"av[-_]?8b.*plus|av[-_]?8b\+"),
        (r"av[-_]?8b", r"av[-_]?8b"), (r"av[-_]?8a|harrier|gr3", r"harrier|av[-_]?8a"),
        (r"mq[-_]?4c|triton", r"mq[-_]?4c"), (r"rq[-_]?180", r"rq[-_]?4"),
        (r"p[-_]?8|usn_p8|raaf_p8|rnzaf_p8", r"p[-_]?8"),
        (r"p[-_]?3", r"p[-_]?3c"), (r"e[-_]?7a", r"e[-_]?7"),
        (r"mh[-_]?60|s[-_]?70b", r"mh[-_]?60r"),
        (r"uh[-_]?60m", r"uh[-_]?60"), (r"mrh90|nh90", r"nh90"),
        (r"sea.?lynx|lynx", r"lynx"), (r"seaking|sh[-_]?3h", r"sea.?king|sh[-_]?3h"),
        (r"mv[-_]?22|mv22|sv22", r"mv[-_]?22|mv22"),
        (r"ch[-_]?53|ch53", r"ch[-_]?53|ch53"),
        (r"ah.?mk.?1|ah[-_]?64", r"ah[-_]?64e"),
        (r"bell[-_]?212|ab212", r"bell[-_]?212|ab[-_]?212"),
        (r"rc135", r"rc[-_]?135"), (r"kc[-_]?46", r"kc[-_]?46"),
        (r"kc[-_]?10", r"kc[-_]?10"), (r"mig[-_]?31", r"mig[-_]?31"),
        (r"su[-_]?24", r"su[-_]?24"), (r"su[-_]?27p", r"su[-_]?27"),
        (r"j[-_]?7", r"j[-_]?7|mig[-_]?21"), (r"tu[-_]?95", r"tu[-_]?95"),
        (r"h[-_]?6", r"h[-_]?6"), (r"j[-_]?10", r"j[-_]?10"),
        (r"j[-_]?11", r"j[-_]?11"), (r"j[-_]?15", r"j[-_]?15"),
        (r"j[-_]?16", r"j[-_]?16"), (r"z[-_]?9", r"z[-_]?9"),
        (r"z[-_]?18", r"z[-_]?18"), (r"z[-_]?20", r"z[-_]?20"),
    ],
}


def info(kind):
    return LAND if kind == "land" else costs.KINDS[kind]


def providers(root):
    root = Path(root)
    registry = json.loads((root / "data/mod-catalog.json").read_text(encoding="utf-8"))
    out = [(p["folder"], root / p["source"] / p["folder"])
           for p in registry["local_packs"] if p["folder"] != "SEST_Combat_Costs"]
    out += [(t.strip(), root / "mods-source" / t.strip())
            for t in (root / "data/load-order.tokens.txt").read_text().splitlines() if t.strip().isdigit()]
    return out + [("vanilla", root / "mods-source/_vanilla/original")]


class Definitions:
    """Static native-order metadata, including a self alias's next provider.

    Cost catalogs remain authoritative for price precedence; this resolver is
    used for classification, dates, display names and inherited inline fields.
    It does not run any third-party code or claim to simulate runtime plugins.
    """
    def __init__(self, root):
        self.root, self.chains, self.cache = Path(root), defaultdict(list), {}
        for owner, base in providers(root):
            for kind in (*costs.KINDS, "land"):
                folder = info(kind)[0]
                for path in sorted((base / folder).glob("*.ini")):
                    if path.stem.casefold().endswith(("_variants", "_squadrons", "_loadouts")):
                        continue
                    text = path.read_text(encoding="utf-8-sig", errors="replace")
                    sections = costs.parse_ini(text)
                    alias = re.search(r"^#!alias\s+([^\r\n]+)", text, re.M)
                    if "general" not in sections and not alias:
                        continue
                    if kind == "weapon" and not sections.get("general", {}).get("type") and not alias:
                        continue
                    self.chains[kind, path.stem.casefold()].append({
                        "id": path.stem, "owner": owner, "path": path, "sections": sections,
                        "alias": alias[1].strip() if alias else None,
                        "general": sections.get("general", {})})

    def sections(self, kind, uid, layer=0, seen=()):
        key = (kind, uid.casefold(), layer)
        if key in self.cache:
            return self.cache[key]
        if key in seen:
            raise ValueError("Cost metadata alias cycle: " + repr((*seen, key)))
        chain = self.chains.get((kind, uid.casefold()), [])
        if layer >= len(chain):
            return {}
        item = chain[layer]
        out = {}
        if item["alias"]:
            ref = Path(item["alias"].replace("\\", "/")).stem.casefold()
            out = self.sections(kind, ref, layer + 1 if ref == uid.casefold() else 0, (*seen, key))
        out = {s: dict(v) for s, v in out.items()}
        for section, values in item["sections"].items():
            out[section] = dict(out.get(section, {}), **values)
        self.cache[key] = out
        return out


def number(value, default=0):
    try:
        return float(str(value).split(",")[0])
    except (ValueError, TypeError):
        return default


def rounded(amount):
    """Three significant digits: model uncertainty never warrants cents."""
    n = Decimal(str(amount))
    if n <= 0:
        return "0"
    quantum = Decimal(10) ** max(0, n.adjusted() - 2)
    return str(int(n.quantize(quantum, rounding=ROUND_HALF_UP)))


def service_year(sections):
    for section in (sections.get("general", {}), *sections.values()):
        for key in ("focdate", "iocdate", "inservicedate", "inserviceyear"):
            match = re.search(r"\b(19\d\d|20\d\d)\b", section.get(key, ""))
            if match:
                return min(2026, int(match[1]))
    return None


def cpi(year, policy):
    anchors = sorted((int(k), Decimal(str(v))) for k, v in policy["cpi_anchors"].items())
    if year <= anchors[0][0]:
        return anchors[0][1]
    for (a, av), (b, bv) in zip(anchors, anchors[1:]):
        if a <= year <= b:
            return av + (bv-av) * Decimal(year-a) / Decimal(b-a)
    return anchors[-1][1]


def select_model(kind, uid, sections):
    """One auditable replacement model; no native points are consulted."""
    name = uid.casefold()
    general, guidance = sections.get("general", {}), sections.get("guidance", {})
    typ = general.get("type", "").casefold()
    if kind == "weapon":
        # Visual/control/ejection processes are not purchased consumables.
        if re.search(r"(?:^all_dummy$|dircm|^(?:all_(?:600kw_)?laser|usn_laser|ger_hel)$|firedecal|ship_spawner|^(?:air_drop|fs2?|para|supply|vehicle)$)", name):
            return "none", None
        if typ == "paratrooper":
            return "none", None
        if typ == "torpedo":
            if "canto" in name: return "canto", None
            if re.search(r"seaspider|m15at|yu[-_]?12a", name): return "antitorpedo", None
            if re.search(r"g7[eat]|si270|tipo_i|g6e", name): return "ww2_torpedo", None
            if re.search(r"mu[-_]?90|stingray|mk[-_]?54|torped[-_]?45|torped[-_]?47|yu[-_]?12", name): return "modern_light_torpedo", None
            if number(general.get("mass")) >= 700:
                return ("legacy_torpedo" if re.search(r"53[-_]?65|65[-_]?76|set[-_]?65|at[-_]?2|saet|e15|set[-_]?40", name) else "heavy_torpedo"), None
            return "light_torpedo", None
        if typ == "sonobuoy":
            if re.search(r"101|110|125|926|sonoflash", name): return "multistatic_buoy", None
            if re.search(r"ssq[-_]?62|ssq[-_]?47|963|skf[-_]?(?:15|20)", name): return "active_buoy", None
            return "passive_buoy", None
        if typ in ("noisemaker", "moss"):
            if "canto" in name: return "canto", None
            if "nixie" in name: return "towed_decoy", None
            return ("mobile_decoy" if typ == "moss" else "acoustic_decoy"), None
        if typ == "chaff":
            if "nulka" in name: return "active_rf_decoy", None
            if re.search(r"mass|omnitrap|sealem|sylena|sclar|3dds", name): return "multispectral_decoy", None
            return ("air_chaff" if re.search(r"aircraft|all_air|dircm", name) else "ship_chaff"), None
        if typ == "fueltank": return "fuel_tank", None
        if typ == "container":
            if re.search(r"refu[ei]l|d[-_]?704|sargent|buddy", name): return "refuel_pod", None
            if re.search(r"alq|ngj|ecm|jamm|skyshadow|sky_shadow|elan|sorbtsiya|sorbcija", name): return "ew_pod", None
            if re.search(r"sniper|litening|pave.?tack|pave.?spike|atflir|lantirn|aaq|aas[-_]?38|recon|tgp|scout", name): return "sensor_pod", None
            if re.search(r"gun.?pod|aden|gau[-_]?|gsh|suu[-_]?(?:16|23)|mk[-_]?4_gun", name): return "gun_pod", None
            if re.search(r"agr[-_]?30_pod19|lau[-_]?61|ub[-_]?32|b[-_]?8|b[-_]?13|lau[-_]?3", name): return "large_pod", None
            if re.search(r"agr[-_]?30_pod|lau[-_]?68|lau[-_]?10|ub[-_]?16|matra|sneb|rocket", name): return "small_pod", None
            if "tank" in name: return "fuel_tank", None
            return "rack", None
        if typ == "projectile":
            match = re.search(r"(?:cal[_-]?|^|_)(\d+(?:\.\d+)?)(?:mm|in)", name)
            calibre = number(match[1]) if match else 30
            if "in" in name and "mm" not in name: calibre *= 25.4
            bands = [(8,1),(13,5),(21,40),(26,65),(35,90),(45,250),(60,1700),(80,2500),(110,3000),(135,4000),(160,8000),(500,20000)]
            value = next((p for c,p in bands if calibre <= c), 20000)
            return "projectile", value
        if typ == "aerialrocket":
            return ("heavy_air_rocket" if number(general.get("mass")) > 80 else "air_rocket"), None
        if typ in ("rbu", "airdepthcharge"):
            return ("depth_charge" if typ == "airdepthcharge" else "asw_rocket"), None
        if typ == "mlrs":
            return ("guided_mlrs" if re.search(r"gnss|m31|gmlrs|guided", name) else "unguided_mlrs"), None
        if typ == "bomb":
            if re.search(r"b[-_]?61|rn[-_]?40|rn[-_]?42|nuclear|rn[-_]?24", name): return "nuclear_bomb", None
            if "flare" in name: return "air_flare", None
            if number(guidance.get("guidancetype")) or re.search(r"gbu|gb[-_]|walleye|bolt|agm[-_]?62", name): return "guided_bomb", None
            return "unguided_bomb", max(1000, number(general.get("mass"), 250)*12)
        if typ == "missile" or typ == "asroc" or not typ:
            if typ == "asroc": return "light_torpedo", None
            if re.search(r"hyperson|hgv|zircon|tsirkon|cps|dark.?eagle|lrhw|arrw|agm[-_]?183", name): return "hypersonic", None
            if re.search(r"trident|minuteman|bulava|topol|yars|sarmat|ss[-_]?n[-_]?(?:20|23|30)|df[-_]?(?:31|41)|icbm", name): return "strategic", None
            if re.search(r"iskander|mgm[-_]?140|atacms|df[-_]|fateh|isk|prsm|prithvi|9m723|ss[-_]?21|ss[-_]?26", name): return "ballistic", None
            if re.search(r"akd|hellfire|agm[-_]?114|tow|spike|hot[-_]?|at[-_]?\d|vikhr|atgm", name): return "atgm", None
            if re.search(r"stinger|mistral|starstreak|igla|strela|manpad", name): return "manpad", None
            if general.get("airlaunched", "").casefold() == "true" and general.get("targettype", "").casefold() == "aaw":
                return ("ir_aam" if number(guidance.get("guidancetype")) == 1 else "aam"), None
            if re.search(r"aim[-_]|aam[-_]|pl[-_]|r[-_]?(?:27|33|37|60|73|77)|aa[-_]|shafrir|python|derby", name):
                return ("ir_aam" if number(guidance.get("guidancetype")) == 1 or re.search(r"aim[-_]?9|aam[-_]?3|shafrir|python",name) else "aam"), None
            if general.get("targettype", "").casefold() == "aaw": return "sam", None
            if general.get("targettype", "").casefold() == "asuw": return "asm", None
            return "cruise", None
        raise ValueError(f"No cost classification for weapon {uid}: {typ}")
    if kind == "aircraft":
        if name in ("shared_settings", "profile_"): return "none", None
        if "satellite" in name: return "satellite", None
        if re.search(r"balloon", name): return "small_uav", 200000
        if re.search(r"f[-_]?47|fa[-_]?xx|j[-_]?36|j[-_]?50|yf[-_]?23|su[-_]?47|jh[-_]?[26]|j9$", name): return "future_fighter", None
        if re.search(r"mq[-_]?4|triton|global.?hawk|rq[-_]?4|rq[-_]?180", name): return "large_uav", None
        if re.search(r"fury|loyal|wingman|mq[-_]?28|xq[-_]?", name): return "loyal_wingman", None
        if re.search(r"uav|rq[-_]?7|djo|drone|mq[-_]?9", name): return "small_uav", None
        if re.search(r"aew|kj[-_]|ec[-_]?2|tu[-_]?214r|rc[-_]?135|e[-_]?7|zdk|kq100", name): return "aew", None
        if re.search(r"kc[-_]|y[-_]?20|yy[-_]?20|c[-_]?17|c[-_]?130|il[-_]?76", name): return "transport", None
        if re.search(r"civ_a(?:3|[0-9])|boeing|airbus", name): return "civil_airliner", None
        if re.search(r"n22|searchmaster|t28|t-28", name): return "civil_light", None
        if re.search(r"mv[-_]?22|mv22|mv75|v280|ch[-_]?53|ch53|v[-_]?19", name): return "heavy_helo", None
        if general.get("unittype", "").casefold() == "helicopter": return "helo", None
        if re.search(r"f[-_]?35|f[-_]?22|j[-_]?20|j[-_]?35|su[-_]?57", name): return "stealth_fighter", None
        return "fighter", None
    if kind == "vessel":
        if re.search(r"humpback|president|^test$", name): return "none", None
        if "sea_mine" in name: return "missile_boat", 50000
        if "uuv" in name: return "uuv", None
        if re.search(r"usv|asv|corsair", name): return "usv", None
        if re.search(r"ssbn|ssgn|ohio|franklin|madison", name): return "ssbn", None
        if re.search(r"ssn|seawolf|victor", name): return "ssn", None
        if general.get("unittype", "").casefold() == "submarine" or re.search(r"collins|_ss_|ming|s-26", name): return "ssk", None
        if "choules" in name: return "amphibious", 400000000
        if re.search(r"cvn|nimitz|ford", name): return "carrier", None
        if re.search(r"lhd|lpd|lsd|lst|take_|tarlac|sichang", name): return "amphibious", None
        if re.search(r"aor|taoe|aor_|chula|supply|lewis.clark|type90[13]", name): return "auxiliary", None
        if re.search(r"_dd[g_]|destroy|_cg_|udaloy|bunker|spruance|ins_d", name): return "destroyer", None
        if re.search(r"_ff[g_h_]|frigate|anzac|cannon|makut|hamilton|054a|ins_f", name): return "frigate", None
        if re.search(r"opv|arafura|tarlac", name): return "patrol", None
        if re.search(r"_pt|_pb_|boat|grisha|corvette|lazaga|malvar|ch[oa]nburi|khamron|_fs_", name): return "missile_boat", None
        return ("missile_boat" if number(general.get("length"), 100) < 90 else "merchant"), None
    if kind == "land":
        subtype = general.get("landunitsubtype", "").casefold()
        if re.search(r"uav_forward|drone.?squad", name): return "uav_team", None
        if re.search(r"infantry|soldier|marine|troop|rifle|commando|squad", name): return "infantry", None
        if re.search(r"command|_cp$|_c2|c2_|control", name): return "command", None
        if subtype == "radar" or re.search(r"radar|_sr$|_tr$|_rs$|_str$", name): return "radar", None
        if subtype == "sam":
            return ("sam_launcher" if re.search(r"launcher|_ln$|_tel$|_ln_|_launcher", name) else "land_sam"), None
        if subtype == "aaa": return "aaa", None
        if subtype == "missilesite": return "missile_site", None
        if subtype == "oilrig": return "oilrig", None
        if subtype == "bridge": return "bridge", None
        if subtype == "airbase": return ("small_airbase" if re.search(r"small|strip|heliport|far[pm]", name) else "airbase"), None
        if subtype == "port": return "port", None
        if re.search(r"hangar", name): return "hangar", None
        if re.search(r"fuel|fueltank|oil_tank", name): return "fuel_store", None
        if subtype == "installation": return "installation", None
        if re.search(r"tank|leopard|abrams|pzh|k9_|_k9$|howitzer|2s19|_t[-_]?(?:54|55|62|72|80|90)|m109|challenger|type99", name): return "tank", None
        if re.search(r"btr|bmp|apc|ifv|warrior|m113|bradley|aslav|boxer|cv90", name): return "apc", None
        if re.search(r"truck|ural|zil|gaz|car_|jeep|humvee|utility|technical", name): return "truck", None
        return "land_mobile", None
    raise ValueError(kind)


def family_price(kind, uid, catalog, historical):
    for pattern, donor_pattern in FAMILIES.get(kind, []):
        if not re.search(pattern, uid, re.I):
            continue
        candidates = [(key, row) for key, row in catalog.items()
                      if re.search(donor_pattern, key, re.I)
                      and costs.price(row.get(historical.casefold())) not in (None, 0)
                      and costs.price(row.get("currentyearcost")) not in (None, 0)]
        if candidates:
            key, row = sorted(candidates, key=lambda pair: (len(pair[0]), pair[0]))[0]
            return key, row
    return None, None


def _model(kind, uid, sections, policy, donor_catalog):
    key, amount = select_model(kind, uid, sections)
    if key == "projectile":
        model = {"usd":amount,"category":"Gun","label":"per-projectile calibre-band replacement estimate, not cost per burst","source":"policy"}
    else:
        model = dict(policy["models"][key])
        if amount is not None: model["usd"] = amount
    model.setdefault("source", "policy")
    year = service_year(sections)
    source, donor = family_price(kind, uid, donor_catalog, info(kind)[2]) if key != "none" else (None,None)
    current = rounded(model["usd"])
    historical = rounded(Decimal(current) * cpi(year or 2026, policy) / Decimal(str(policy["cpi_current_estimate"])))
    basis = model["label"]
    if donor:
        historical, current = donor[info(kind)[2].casefold()], donor["currentyearcost"]
        basis = "design/family/role catalog comparator " + source + "; donor reference-year series retained; not a class-specific quote"
    multiplier = Decimal(str(model.get("uncertainty", 2)))
    return {"model":key,"historical":historical,"current":current,"category":model["category"],
            "source":source,"basis":basis,"source_id":"tracker" if donor else model["source"],
            "historical_year":None if donor else (year or 2026),
            "historical_basis":"donor reference year" if donor else ("configured service-year CPI model" if year else "2026 replacement proxy; IOC unknown"),
            "confidence":"catalog comparator estimate" if donor else "rough model",
            "current_low":rounded(Decimal(current)/multiplier),"current_high":rounded(Decimal(current)*multiplier),
            "disposition":model.get("disposition","counted")}


def build_complete(root, mappings, policy=None):
    """(installed result, provenance context), preserving all known fields."""
    result, context = costs._build(root, mappings)
    context["land_estimates"] = mappings.get("land", [])
    return complete(root, result, context, policy)


def complete(root, result, context, policy=None):
    policy = policy or json.loads((Path(root)/"integration/combat-costs/coverage-policy.json").read_text())
    result, context = copy.deepcopy(result), copy.deepcopy(context)
    defs = Definitions(root)
    context["units"]["land"] = {uid:dict(layers[0]) for (kind,uid),layers in defs.chains.items() if kind=="land"}
    context["catalogs"]["land"],context["merged"]["land"] = {},{}
    result["extensions"]["land"] = {}
    # Take donors from the conservative stage only, never from an estimate
    # just generated earlier in alphabetical order.
    donors = copy.deepcopy(context["merged"])
    receipts = {(e["kind"],e["target"].casefold()): e for e in result["entries"]}
    # Checked land research is the land's conservative stage: the models
    # only fill a field it leaves blank, as for the tracker's own kinds.
    land_units = context["units"]["land"]
    for item in context.get("land_estimates", []):
        uid = item["target"].casefold()
        if uid not in land_units:
            raise ValueError("land: reviewed target no longer exists: " + item["target"])
        if ("land", uid) in receipts:
            raise ValueError("land: duplicate reviewed estimate: " + item["target"])
        fields = costs.estimate_fields("land", item, LAND)
        result["extensions"]["land"][uid] = fields
        context["merged"]["land"][uid] = {k.casefold(): v for k, v in fields.items()}
        receipts["land", uid] = {"kind": "land", "target": land_units[uid]["id"], "source": None, "origin": "estimate",
                                 "basis": item["basis"], "fields": fields, "estimate": item["estimate"],
                                 "sources": item["sources"]}
    rows, before, filled = [], {}, Counter()
    for kind, units in context["units"].items():
        hist, cat_key = info(kind)[2:]
        merged = context["merged"][kind]
        before[kind] = {}
        for uid, unit in sorted(units.items()):
            sections = defs.sections(kind,uid)
            own = sections.get("general",unit["general"])
            before[kind][uid] = {f:costs.price(costs.resolve_field(own,merged,uid,f)) for f in (hist,"CurrentYearCost")}
            proposed = _model(kind,uid,sections,policy,donors[kind])
            extra = result["extensions"][kind].get(uid,{}).copy()
            methods, field_sources = {}, {}
            prior = receipts.get((kind,uid))
            checked_current = before[kind][uid]["CurrentYearCost"]
            if prior and prior["origin"] == "estimate" and before[kind][uid][hist] is None and checked_current is not None:
                # A checked current-only price: backcast it, so the pair
                # stays one estimate rather than an unrelated model figure.
                year = service_year(sections)
                proposed = dict(proposed, basis=prior["basis"], historical_year=year or 2026,
                    historical=rounded(checked_current * cpi(year or 2026, policy) / Decimal(str(policy["cpi_current_estimate"]))),
                    historical_basis="CPI backcast of SEST's checked current price"+(" to the service year" if year else "; IOC unknown, 2026 proxy"),
                    confidence="CPI backcast of checked current price")
            for label,field in (("historical",hist),("current","CurrentYearCost")):
                if before[kind][uid][field] is None:
                    extra[field] = proposed[label]
                    # A preferred inline blank/invalid otherwise masks the
                    # catalog. Override only this missing field, never all fields.
                    if field.casefold() in own:
                        extra["Override"+field] = "True"
                    methods[label] = proposed["confidence"]
                    field_sources[label] = proposed["basis"]
                    filled[kind] += 1
                else:
                    methods[label] = "existing usable value preserved"
                    _, origin = costs.field_origin(own,merged,uid,field)
                    if origin == "inline": field_sources[label] = "inline equipment price"
                    elif uid in context["catalogs"][kind]: field_sources[label] = "tracker author catalog"
                    elif prior and prior["origin"] == "estimate": field_sources[label] = "SEST checked research: " + prior["basis"]
                    elif prior and prior.get("source"): field_sources[label] = "reviewed catalog mapping: " + prior["source"]
                    else: field_sources[label] = "existing resolved catalog price"
            category = costs.resolve_field(own,merged,uid,"Category",cat_key) if cat_key else None
            if cat_key:
                if not category or not CATEGORY_RE.fullmatch(category) or category.casefold()=="ignore":
                    category = proposed["category"]
                    extra["Category"] = category
                    if cat_key.casefold() in own: extra["OverrideCategory"]="True"
            # An aircraft price has no native category; land does, for SEST.
            category = category or proposed["category"]
            if extra != result["extensions"][kind].get(uid,{}):
                old = receipts.get((kind,uid))
                receipts[kind,uid] = {"kind":kind,"target":unit["id"],"origin":"completion",
                    "source":proposed["source"],"basis":proposed["basis"],"fields":extra,
                    "completion":proposed,"field_methods":methods,
                    "prior_origin":old.get("origin") if old else None,
                    "sources":(old["sources"] if old and old["origin"]=="estimate" else [])+[policy["sources"][proposed["source_id"]],policy["sources"]["policy"]]}
                result["extensions"][kind][uid] = extra
                merged[uid] = dict(merged.get(uid,{}),**{k.casefold():v for k,v in extra.items()})
            values = {label:costs.price(costs.resolve_field(own,merged,uid,field))
                      for label,field in (("historical",hist),("current","CurrentYearCost"))}
            if any(v is None for v in values.values()):
                raise ValueError(f"Incomplete final prices: {kind} {uid}: {values}")
            # Preserve a physical item's pre-existing zero too: a public
            # price override is not silently reinterpreted as a fresh quote.
            historical_filled = methods["historical"] != "existing usable value preserved"
            basis = proposed["historical_basis"] if historical_filled else field_sources["historical"] + "; original reference-year basis retained"
            year = proposed["historical_year"] if historical_filled else (prior.get("estimate",{}).get("historical_year") if prior else None)
            disposition = "included or non-procured" if category.casefold()=="ignore" else "counted"
            row = {"kind":kind,"id":unit["id"],"owner":unit["owner"],"path":str(unit["path"].relative_to(Path(root))),
                   "category":category,"type":own.get("type",own.get("landunitsubtype",own.get("unittype",""))),
                   "historical":str(values["historical"]),"current":str(values["current"]),
                   "field_methods":methods,"field_sources":field_sources,
                   "completion":proposed if any(v!="existing usable value preserved" for v in methods.values()) else None,
                   "disposition":disposition,"historical_basis":basis,
                   "historical_reference_year":year,
                   "current_low":proposed["current_low"] if methods["current"]!="existing usable value preserved" else None,
                   "current_high":proposed["current_high"] if methods["current"]!="existing usable value preserved" else None}
            rows.append(row)
        sest = [r for r in rows if r["kind"]==kind and r["owner"].startswith("SEST_")]
        result["coverage"][kind] = {"eligible":len(units),"historical_known":len(units),"current_known":len(units),
            "sest_eligible":len(sest),"sest_historical_known":len(sest),"sest_current_known":len(sest),"unknown":[]}
    result["entries"] = sorted(receipts.values(),key=lambda e:(e["kind"],e["target"].casefold()))
    result["completion"] = {"policy_version":policy["version"],"price_year":policy["price_year"],
        "reference_scope":"all resolved collection/vanilla definitions, including labelled non-procured helpers",
        "rows":rows,"filled_fields":dict(filled),"known_fields_preserved":sum(v is not None for k in before.values() for u in k.values() for v in u.values()),
        "category_counts":dict(Counter(r["category"] for r in rows)),"sources":policy["sources"]}
    context["receipts"] = {(e["kind"],e["target"].casefold()):e for e in result["entries"]}
    context["completion"] = result["completion"]
    return result,context


def render_complete(kind,result):
    target = info(kind)[1]
    lines = (["; SEST-owned land-platform prices; Combat Cost Tracker itself does not bind land platforms."] if kind=="land"
             else [f"#!extend systems/{target}.ini"])
    lines += ["; Complete SEST coverage: existing usable prices are preserved; gaps use labelled estimates.",
              "; Prices are USD. Rough ranges are sensitivity bands, not confidence intervals.",
              "; Zero for a helper or transfer is explicitly documented; people are never priced."]
    if kind == "land":
        lines += ["", "[Costs]", "OverrideInline=False"]
    for entry in result["entries"]:
        if entry["kind"]!=kind: continue
        lines += ["","; "+entry["basis"]]
        if entry.get("completion"):
            c=entry["completion"]
            modeled={mode for mode,method in entry["field_methods"].items() if method!="existing usable value preserved"}
            lines += ["; SEST estimate for "+", ".join(sorted(modeled))+": "+c["confidence"]+"; model="+c["model"] if modeled
                      else "; SEST category completion only; both existing price fields retained."]
            if "historical" in modeled:
                lines += ["; Historical basis: "+c["historical_basis"]+("; year="+str(c["historical_year"]) if c["historical_year"] else "")]
            if "current" in modeled:
                lines += ["; Modeled 2026 replacement sensitivity: USD "+c["current_low"]+" to "+c["current_high"]]
            lines += ["; Accounting: "+c["disposition"],"; Field provenance: "+json.dumps(entry["field_methods"],sort_keys=True)]
            lines += ["; Source: "+s["title"]+" - "+s["url"] for s in entry["sources"]]
        elif entry.get("estimate"):
            lines += costs.estimate_comments(kind,entry,info(kind))
        else:
            lines += ["; Source catalog section: "+(entry["source"] or "none")]
        lines += ["["+entry["target"]+"]"]+[f"{k}={v}" for k,v in entry["fields"].items()]
    return "\n".join(lines)+"\n"


def render_config(root,result):
    """Expose priced expendables; retain the captured mode/currency/position."""
    path=Path(root)/"mods-source/3807187341/systems/combatcosts/config.ini"
    base=costs.read_ini(path).get("weaponcategories",{}).get("order","")
    categories=[x.strip() for x in base.split(",") if x.strip()]
    for category in ("Gun","Decoy","Sonobuoy","Fuel tank","Pod","Other"):
        if category not in categories: categories.append(category)
    return "#!extend systems/combatcosts/config.ini\n; SEST: show expenditure categories covered by the complete catalog.\n; Currency, reference year, cost mode, overlay position and hotkey are inherited.\n[WeaponCategories]\nOrder="+",".join(categories)+"\n"


def reports(result):
    completion=result["completion"]
    md=["# Complete SEST combat cost coverage", "", "Generated from the resolved collection and vanilla definitions. Prices are USD per represented item. Existing usable prices remain authoritative; remaining prices are SEST family comparisons or rough replacement models. These models implement the owner's request for coverage with estimates, and are not independently confirmed procurement quotes.",
        "", "Historical model prices use configured service-year CPI backcasts where a year exists; otherwise they are explicitly 2026 replacement proxies. The 2026 CPI value is a Q2-based estimate. Ranges are sensitivity bands, not statistical confidence intervals.",
        "", "Ammunition, embarked aircraft, removable pods and tank contents are excluded from fitted platform estimates. A pod's own estimate covers its hardware, and its rounds are separate. Personnel, visual helpers and simulated processes have an explicit non-procured disposition. Native tracker limitations and the SEST debrief extension are described in README.md.","",
        "| Kind | References | Historical prices | Current prices |", "|---|---:|---:|---:|"]
    for kind,c in result["coverage"].items():
        md.append(f"| {kind} | {c['eligible']} | {c['historical_known']} | {c['current_known']} |")
    md += ["", f"Preserved {completion['known_fields_preserved']} pre-existing usable price fields. Filled {sum(completion['filled_fields'].values())} missing fields. No acquisition-point field was used as USD.", ""]
    buf=io.StringIO(); writer=csv.writer(buf,lineterminator="\n")
    writer.writerow(["kind","id","owner","type","category","historical_usd","current_usd","historical_method","current_method","historical_basis","reference_year","current_model_low","current_model_high","accounting","model","historical_source","current_source"])
    for kind in result["coverage"]:
        md += ["## "+kind.title(),"", "| Reference | Category | Historical USD | Current USD | Provenance | Accounting |", "|---|---|---:|---:|---|---|"]
        for r in (x for x in completion["rows"] if x["kind"]==kind):
            model=r["completion"]
            provenance="; ".join(f"{k}: {v} ({r['field_sources'][k]})" for k,v in r["field_methods"].items()).replace("|","/").replace("\n"," ")
            md.append(f"| `{r['id']}` | {r['category']} | {r['historical']} | {r['current']} | {provenance} | {r['disposition']} |")
            writer.writerow([kind,r["id"],r["owner"],r["type"],r["category"],r["historical"],r["current"],r["field_methods"]["historical"],r["field_methods"]["current"],r["historical_basis"],r["historical_reference_year"] or "",r["current_low"] or "",r["current_high"] or "",r["disposition"],model["model"] if model else "",r["field_sources"]["historical"],r["field_sources"]["current"]])
        md.append("")
    md += ["## Model and research sources",""]+["- "+s["title"]+": "+s["url"] for s in completion["sources"].values()]
    return "\n".join(md)+"\n",buf.getvalue()
