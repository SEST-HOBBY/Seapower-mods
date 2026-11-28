"""GCO's command structure for Dynamic Campaign Mod 1.0.4: sea regions,
fleets and Career starts.

Dynamic Campaign Mod 1.0.4 builds its command chain from three campaign
fields the original GCO never had:

- "seaRegions": a file beside the campaign folders (sea_regions_world.json)
  naming the theatre's strategic sea regions, each a set of [lat, lon]
  polygons. DCM makes each region a sector of the fleet that holds it.
- "fleets": each side's fleets, each with a base and a depot of its side and
  its regions. DCM's rule (CampaignDefinition validation, 1.0.4): every
  region in exactly one fleet of a side.
- "careerStarts": the starts Career offers, each for nations of a playable
  side. Without them DCM greys Career out ("Not in this campaign yet").

The regions here are rectangles in the campaign's continuous longitude
(-100 to 258). They do not overlap, and every water point inside the bounds
falls in exactly one of them except the inland seas in INLAND, which no
fleet can reach. check() proves both on the land mask the campaign checker
uses.

Fleets follow the real 2028 commands where the collection has the base (US
2nd, 3rd, 4th, 5th, 6th and 7th Fleets, the Royal Navy, the JMSDF Self
Defense Fleet, the Royal Australian Navy, the Indian Navy; Russia's
Northern, Baltic, Black Sea and Pacific Fleets, the PLA Navy's three theatre
fleets and Iran's navy). Their split of the world's oceans is a scenario
choice. "navy" names a navy in Dynamic Campaign Mod's own commander book
(commanders/navies.json): it draws the commanders' names, ranks and
portraits. A navy the book does not have is left out; DCM then takes the
navy of the base's nation, or of the side's first nation.

Career starts are scenario choices too: each puts the player's first ships
at a named place with a first order of DCM's own kinds (hold, intercept,
defend), shaped as Dynamic Campaign Mod's own campaigns write them.
"""
REGIONS_FILE = "sea_regions_world.json"
LAT_MIN, LAT_MAX, LON_MIN, LON_MAX = -79.0, 81.0, -100.0, 258.0

# id: (name, [(south, north, west, east), ...]) in continuous longitude.
REGIONS = {
    "canadian_arctic": ("Canadian Arctic and Baffin Bay", [(66, 81, -100, -35)]),
    "north_atlantic_west": ("Western North Atlantic", [(45, 66, -100, -35)]),
    "western_atlantic": ("US East Coast", [(30, 45, -100, -35)]),
    "caribbean_gulf": ("Gulf of Mexico and Caribbean", [(5, 30, -100, -55)]),
    "central_atlantic": ("Central Atlantic", [(5, 30, -55, -35)]),
    "south_atlantic_west": ("South American Waters", [(-79, 5, -100, -35)]),
    "greenland_sea": ("Greenland Sea and GIUK Gap", [(60, 81, -35, -6)]),
    "northeast_atlantic": ("Eastern North Atlantic", [(36, 60, -35, -6)]),
    "eastern_central_atlantic": ("Canaries and West Africa", [(5, 36, -35, -6)]),
    "south_atlantic": ("South Atlantic and Gulf of Guinea", [(-79, 5, -35, 20), (5, 8, -6, 20)]),
    "norwegian_barents": ("Norwegian, Barents and White Seas", [(66, 81, -6, 60), (63, 66, 32, 45)]),
    "north_sea_baltic": ("North Sea and Baltic", [(50, 66, -6, 32)]),
    "channel_biscay": ("Channel and Bay of Biscay", [(43.5, 50, -6, 3)]),
    "mediterranean_west": ("Western Mediterranean", [(30, 43.5, -6, 15), (43.5, 46, 3, 15)]),
    "mediterranean_east": ("Eastern Mediterranean and Adriatic", [(30, 41, 15, 37), (41, 46, 15, 20)]),
    "black_sea": ("Black Sea", [(41, 48, 27, 42)]),
    "red_sea": ("Red Sea", [(12, 30, 32, 44)]),
    "persian_gulf": ("Persian Gulf", [(23, 31, 47, 57.5)]),
    "arabian_sea": ("Arabian Sea and Gulf of Aden", [(5, 23, 44, 78), (23, 26, 57.5, 70), (10, 12, 42, 44)]),
    "bay_of_bengal": ("Bay of Bengal", [(5, 26, 78, 98)]),
    "western_indian_ocean": ("Western Indian Ocean", [(-45, 5, 20, 78)]),
    "eastern_indian_ocean": ("Eastern Indian Ocean", [(-45, 0, 78, 105), (0, 5, 78, 98)]),
    "indonesian_seas": ("Indonesian Seas", [(-12, 0, 105, 141)]),
    "timor_west_australia": ("Timor Sea and Western Australia", [(-45, -12, 105, 141)]),
    "south_china_sea": ("South China Sea", [(0, 23, 98, 121)]),
    "east_china_sea": ("East China Sea and Taiwan Strait", [(23, 33, 117, 131)]),
    "yellow_sea": ("Yellow Sea", [(33, 41, 117, 129)]),
    "sea_of_japan": ("Sea of Japan", [(33, 52, 129, 142)]),
    "philippine_sea": ("Philippine Sea", [(0, 23, 121, 145), (23, 33, 131, 145)]),
    "japan_pacific": ("Pacific off Japan", [(33, 45, 142, 160)]),
    "okhotsk": ("Sea of Okhotsk and Kurils", [(52, 66, 135, 170), (45, 52, 142, 170)]),
    "siberian_arctic": ("Kara, Laptev and East Siberian Seas", [(66, 81, 60, 170)]),
    "bering": ("Bering, Chukchi and Beaufort Seas", [(52, 81, 170, 200), (66, 81, 200, 258)]),
    "gulf_of_alaska": ("Gulf of Alaska", [(52, 66, 200, 235)]),
    "north_pacific": ("North Pacific", [(33, 52, 170, 235), (33, 45, 160, 170)]),
    "central_pacific": ("Central Pacific and Hawaii", [(0, 33, 145, 235)]),
    "eastern_pacific": ("US West Coast and Eastern Pacific", [(0, 60, 235, 258)]),
    "coral_tasman": ("Coral and Tasman Seas", [(-45, -10, 141, 180)]),
    "south_pacific": ("South Pacific", [(-45, 0, 180, 258), (-10, 0, 141, 180)]),
    "southern_ocean": ("Southern Ocean", [(-79, -45, 20, 258)]),
}

# Water no fleet can reach: (name, south, north, west, east).
INLAND = [("Caspian Sea", 36, 48, 46, 56), ("Lake Baikal", 51, 56, 103, 110),
          ("Aral Sea", 43, 47, 58, 62), ("Lake Balkhash", 44, 48, 73, 80)]

# (id, name, navy or None, side, base, depot, [regions])
FLEETS = [
    ("us_2nd_fleet", "US 2nd Fleet", "usn", "blue", "usa_norfolk_naval_station_norfolk",
     "usa_norfolk_naval_station_norfolk", ["canadian_arctic", "north_atlantic_west", "western_atlantic"]),
    ("us_4th_fleet", "US 4th Fleet", "usn", "blue", "home_usa_kings_bay", "usa_norfolk_naval_station_norfolk",
     ["caribbean_gulf", "central_atlantic", "south_atlantic_west", "south_atlantic"]),
    ("royal_navy", "Royal Navy Fleet", "rn", "blue", "home_uk_portsmouth", "home_uk_portsmouth",
     ["greenland_sea", "northeast_atlantic", "norwegian_barents", "north_sea_baltic", "channel_biscay"]),
    ("us_6th_fleet", "US 6th Fleet", "usn", "blue", "med_rota_naval_station", "med_sigonella_nas_sigonella",
     ["eastern_central_atlantic", "mediterranean_west", "mediterranean_east", "black_sea"]),
    ("us_5th_fleet", "US 5th Fleet", "usn", "blue", "me_bahrain_nsa_bahrain", "me_bahrain_nsa_bahrain",
     ["red_sea", "persian_gulf", "arabian_sea"]),
    ("indian_navy", "Indian Navy", None, "blue", "home_ind_mumbai", "home_ind_mumbai",
     ["bay_of_bengal", "western_indian_ocean", "eastern_indian_ocean"]),
    ("us_7th_fleet", "US 7th Fleet", "usn", "blue", "wpac_yokosuka_naval_base", "wpac_yokosuka_naval_base",
     ["south_china_sea", "east_china_sea", "yellow_sea", "philippine_sea", "indonesian_seas"]),
    ("jmsdf_fleet", "JMSDF Self Defense Fleet", "jmsdf", "blue", "home_jpn_kure", "home_jpn_kure",
     ["sea_of_japan", "japan_pacific", "okhotsk"]),
    ("us_3rd_fleet", "US 3rd Fleet", "usn", "blue", "usp_sandiego_naval_base_san_diego",
     "usp_sandiego_naval_base_san_diego",
     ["north_pacific", "central_pacific", "eastern_pacific", "gulf_of_alaska", "bering", "siberian_arctic"]),
    ("australian_fleet", "Australian Fleet", "ran", "blue", "aus_stirling_hmas_stirling",
     "aus_stirling_hmas_stirling", ["timor_west_australia", "coral_tasman", "south_pacific", "southern_ocean"]),

    ("northern_fleet", "Northern Fleet", "soviet", "red", "home_rus_severomorsk", "home_rus_severomorsk",
     ["norwegian_barents", "greenland_sea", "siberian_arctic", "canadian_arctic", "north_atlantic_west",
      "northeast_atlantic", "western_atlantic", "central_atlantic", "caribbean_gulf"]),
    ("baltic_fleet", "Baltic Fleet", "soviet", "red", "home_rus_baltiysk", "home_rus_baltiysk",
     ["north_sea_baltic", "channel_biscay"]),
    ("black_sea_fleet", "Black Sea Fleet", "soviet", "red", "home_rus_novorossiysk", "home_rus_novorossiysk",
     ["black_sea", "mediterranean_east", "mediterranean_west", "eastern_central_atlantic", "south_atlantic",
      "south_atlantic_west"]),
    ("iranian_navy", "Islamic Republic of Iran Navy", None, "red", "home_irn_bandar_abbas",
     "home_irn_bandar_abbas", ["persian_gulf", "red_sea", "arabian_sea", "western_indian_ocean"]),
    ("pacific_fleet", "Pacific Fleet", "soviet", "red", "home_rus_vladivostok", "home_rus_vladivostok",
     ["sea_of_japan", "okhotsk", "bering", "gulf_of_alaska", "japan_pacific", "north_pacific", "eastern_pacific"]),
    ("plan_north_sea", "PLAN Northern Theatre Fleet", "plan", "red", "home_chn_qingdao", "home_chn_qingdao",
     ["yellow_sea"]),
    ("plan_east_sea", "PLAN Eastern Theatre Fleet", "plan", "red", "chn_zhejiang_ningbo_naval_base",
     "chn_zhejiang_ningbo_naval_base", ["east_china_sea", "philippine_sea", "central_pacific"]),
    ("plan_south_sea", "PLAN Southern Theatre Fleet", "plan", "red", "home_chn_zhanjiang", "home_chn_zhanjiang",
     ["south_china_sea", "indonesian_seas", "bay_of_bengal", "eastern_indian_ocean", "timor_west_australia",
      "coral_tasman", "south_pacific", "southern_ocean"]),
]

CAREER_BUDGET = 500     # about two Arleigh Burkes at GCO's prices; DCM's 1985 campaigns give 515
CAREER_SUBS_MOST = 1


def _hold(title, briefing, lat, lon, radius, hours, days):
    return {"kind": "hold", "title": title, "briefing": briefing, "lat": lat, "lon": lon,
            "radiusNm": radius, "hours": hours, "days": days}


def _intercept(title, briefing, lat, lon, radius, days):
    return {"kind": "intercept", "title": title, "briefing": briefing, "lat": lat, "lon": lon,
            "radiusNm": radius, "days": days}


def _defend(title, briefing, base, radius, hours, days):
    return {"kind": "defend", "base": base, "title": title, "briefing": briefing,
            "radiusNm": radius, "hours": hours, "days": days}


# (id, name, nations, kind, difficulty, lat, lon, first order)
CAREER_STARTS = [
    ("gco_us_luzon_strait", "Luzon Strait, west of Batanes", ["US"], "tf", "medium", 19.5, 119.0,
     _intercept("Find the Fujian carrier group",
                "PLANS Fujian and her escorts sailed from Hainan and are believed to be working some 300 nm "
                "south-west of you, between the Paracels and Scarborough Shoal. Find the group and engage it "
                "within 3 days, before its aircraft can cover the approaches to the Luzon Strait. Expect J-15s "
                "from the carrier and land-based fighters from Woody Island.", 16.0, 114.0, 60, 3)),
    ("gco_us_kola", "Barents Sea, north of the Kola Inlet", ["US"], "sub", "hard", 72.6, 33.0,
     _hold("Watch the Kola Inlet",
           "Every Northern Fleet group bound for the Norwegian Sea comes out of the Kola Inlet past Severomorsk, "
           "and the submarine bases at Gadzhiyevo and Zapadnaya Litsa lie beside it. Take station within 40 nm "
           "of the inlet's mouth and keep the boat there for 18 hours in all within 2 days. Expect patrol "
           "aircraft from Olenya and a submarine on patrol at the entrance.", 70.3, 33.8, 40, 18, 2)),
    ("gco_us_hormuz", "Gulf of Oman, off Fujairah", ["US"], "tf", "easy", 25.2, 57.2,
     _hold("Hold the Strait of Hormuz",
           "The tanker lanes out of the Gulf pass within sight of Iran's bases at Bandar Abbas and Jask. Take "
           "station within 25 nm of the strait's narrows and keep a ship there for 12 hours in all within 2 "
           "days. Expect fast attack craft, a submarine and land-based missiles: stay out in the deep channel.",
           26.4, 56.6, 25, 12, 2)),
    ("gco_uk_giuk", "Iceland-Faroes Gap", ["UK"], "tf", "medium", 63.0, -10.5,
     _hold("Close the Iceland-Faroes gap",
           "Northern Fleet submarines and surface groups bound for the Atlantic must cross the gap between "
           "Iceland and the Faroes. Take station within 40 nm of the marked point and keep a ship there for 24 "
           "hours in all within 3 days. Expect submarines first, and long-range bombers from the Kola.",
           63.6, -8.5, 40, 24, 3)),
    ("gco_fr_crete", "Libyan Sea, south of Crete", ["France"], "tf", "easy", 34.3, 24.8,
     _defend("Guard Souda Bay",
             "Souda Bay is the coalition's forward anchorage in the eastern Mediterranean, and the Black Sea "
             "Fleet's ships and submarines can reach it through the Aegean. Keep a ship within 60 nm of the "
             "bay for 12 hours in all within 2 days and see that it is not attacked.",
             "med_souda_bay_nsa", 60, 12, 2)),
    ("gco_jp_tsushima", "Korea Strait, off Tsushima", ["Japan"], "tf", "easy", 34.6, 129.7,
     _hold("Hold the Tsushima Strait",
           "The Pacific Fleet's way south from Vladivostok, and North Korea's from Sinpo, runs through the "
           "Korea Strait either side of Tsushima. Take station within 30 nm of the eastern channel and keep a "
           "ship there for 12 hours in all within 2 days.", 34.2, 129.6, 30, 12, 2)),
    ("gco_au_lombok", "Bali Sea, north of Lombok", ["Australia"], "tf", "medium", -7.6, 116.0,
     _hold("Watch the Lombok Strait",
           "The deep-water route between the Indian Ocean and the Java Sea runs through the Lombok Strait, and "
           "submarines out of the South China Sea use it to reach Australia's western approaches. Take station "
           "within 30 nm of the strait and keep a ship there for 12 hours in all within 3 days.",
           -8.6, 115.8, 30, 12, 3)),
    ("gco_in_arabian", "Arabian Sea, south of Karachi", ["India"], "tf", "medium", 22.0, 66.0,
     _hold("Watch the approaches to Karachi",
           "Pakistan's fleet and its Chinese-built submarines sail from Karachi. Take station within 40 nm of "
           "the marked point south of the port and keep a ship there for 18 hours in all within 3 days. Expect "
           "JF-17s from Masroor and a submarine on patrol off the harbour.", 24.2, 66.5, 40, 18, 3)),

    ("gco_ru_bear_gap", "Barents Sea, west of the Kola", ["Russia"], "tf", "medium", 71.5, 27.0,
     _hold("Cover the Bear Gap",
           "The Northern Fleet's bastion begins at the gap between the North Cape and Bear Island. Take station "
           "within 40 nm of the marked point and keep a ship there for 24 hours in all within 2 days, so that "
           "no NATO submarine or surface group enters the Barents Sea unseen.", 73.0, 20.0, 40, 24, 2)),
    ("gco_ru_north_channel", "North Atlantic, west of the Hebrides", ["Russia"], "sub", "hard", 58.5, -11.0,
     _hold("Watch the North Channel",
           "The Royal Navy's submarines and the convoys for the Clyde pass through the North Channel between "
           "Scotland and Ireland. Take the boat within 30 nm of the marked point and keep it there for 18 hours "
           "in all within 3 days. Expect P-8s from Lossiemouth and frigates out of Faslane.",
           55.6, -6.4, 30, 18, 3)),
    ("gco_ru_vladivostok", "Peter the Great Gulf", ["Russia"], "tf", "easy", 42.6, 132.2,
     _defend("Guard Vladivostok",
             "The Pacific Fleet's main base must not be caught in harbour. Keep a ship within 60 nm of "
             "Vladivostok for 12 hours in all within 2 days and see that it is not attacked.",
             "home_rus_vladivostok", 60, 12, 2)),
    ("gco_cn_scarborough", "South China Sea, east of the Paracels", ["China"], "tf", "medium", 16.5, 114.5,
     _hold("Hold Scarborough Shoal",
           "Scarborough Shoal guards the eastern approach to the South China Sea from Subic Bay and the "
           "Philippine Sea. Take station within 40 nm of the shoal and keep a ship there for 24 hours in all "
           "within 3 days. Expect the US 7th Fleet out of Subic and Guam.", 15.2, 117.8, 40, 24, 3)),
    ("gco_cn_taiwan", "Taiwan Strait, off Pingtan", ["China"], "tf", "hard", 25.3, 120.2,
     _hold("Close the Taiwan Strait",
           "Close the Taiwan Strait to the coalition's ships. Take station within 30 nm of the marked point "
           "in mid-strait and keep a ship there for 24 hours in all within 2 days. Expect anti-ship missiles "
           "from Taiwan's coast and fighters from both sides of the strait.", 24.6, 119.8, 30, 24, 2)),
    ("gco_cn_miyako", "East China Sea, north of the Miyako Strait", ["China"], "sub", "hard", 25.8, 125.0,
     _hold("Watch the Miyako Strait",
           "The Miyako Strait between Okinawa and Miyako-jima is the fleet's way into the Pacific, and the "
           "JMSDF watches it. Take the boat within 30 nm of the strait and keep it there for 18 hours in all "
           "within 3 days.", 24.9, 125.6, 30, 18, 3)),
    ("gco_ir_hormuz", "Strait of Hormuz, off Bandar Abbas", ["Iran"], "tf", "medium", 26.9, 56.3,
     _hold("Hold the Strait of Hormuz",
           "The coalition's ships in the Gulf leave and supply it through the Strait of Hormuz. Take station "
           "within 20 nm of the narrows and keep a ship there for 18 hours in all within 2 days. Expect the US "
           "5th Fleet out of Bahrain.", 26.5, 56.4, 20, 18, 2)),
]


def _poly(rect):
    s, n, w, e = rect
    return [[n, w], [n, e], [s, e], [s, w]]


def regions_file():
    return {
        "_comment": ("Global Command Operations' sea regions for Dynamic Campaign Mod 1.0.4, the same for both "
                     "sides; built by integration/world-sandbox/command_structure.py. Rectangles in the "
                     "campaign's continuous longitude (-100 to 258)."),
        "name": "World",
        "regions": [{"id": rid, "name": name, "areas": [_poly(r) for r in rects]}
                    for rid, (name, rects) in REGIONS.items()],
    }


def fleets():
    out = []
    for fid, name, navy, side, base, depot, regions in FLEETS:
        f = {"id": fid, "name": name}
        if navy:
            f["navy"] = navy
        f.update(side=side, base=base, depot=depot, regions=list(regions))
        out.append(f)
    return out


def career_starts():
    return {"budget": CAREER_BUDGET, "subsMost": CAREER_SUBS_MOST,
            "starts": [{"id": sid, "name": name, "nations": list(nations), "kind": kind, "difficulty": diff,
                        "lat": lat, "lon": lon, "firstOrder": dict(order)}
                       for sid, name, nations, kind, diff, lat, lon, order in CAREER_STARTS]}


def apply(world):
    """Add the command structure to the modernised world (in place)."""
    world["seaRegions"] = REGIONS_FILE
    world["fleets"] = fleets()
    world["careerStarts"] = career_starts()
    import build_dynamic_campaign       # the campaign checker's land mask
    check(world, is_water=build_dynamic_campaign.is_water)
    return world


def _inside(rect, lat, lon):
    s, n, w, e = rect
    return s <= lat < n and w <= lon < e


def region_of(lat, lon):
    return [rid for rid, (_n, rects) in REGIONS.items() if any(_inside(r, lat, lon) for r in rects)]


def check(world, is_water=None, step=1.0):
    """DCM 1.0.4's own rules for these fields, plus SEST's coverage proof.
    Raises ValueError with every problem found."""
    bad = []
    bases = {b["id"]: b for b in world["bases"]}
    sides = {s["id"]: s for s in world["sides"]}
    playable = {n for s in world["sides"] if not s.get("aiOnly") and not s.get("comingSoon") for n in s["nations"]}
    for rid, (_name, rects) in REGIONS.items():
        for s, n, w, e in rects:
            if not (LAT_MIN <= s < n <= LAT_MAX and LON_MIN <= w < e <= LON_MAX):
                bad.append(f"region {rid}: rectangle {(s, n, w, e)} outside the campaign bounds")
    # No two rectangles overlap.
    flat = [(rid, r) for rid, (_n, rects) in REGIONS.items() for r in rects]
    for i, (a, ra) in enumerate(flat):
        for b, rb in flat[i + 1:]:
            if ra[0] < rb[1] and rb[0] < ra[1] and ra[2] < rb[3] and rb[2] < ra[3]:
                bad.append(f"regions {a} and {b} overlap")
    b = world["bounds"]
    if (b["latMin"], b["latMax"], b["lonMin"], b["lonMax"]) != (LAT_MIN, LAT_MAX, LON_MIN, LON_MAX):
        bad.append(f"campaign bounds {b} are not the regions' {LAT_MIN, LAT_MAX, LON_MIN, LON_MAX}")
    ids = set()
    for f in world["fleets"]:
        if f["id"] in ids:
            bad.append(f"fleet id {f['id']} is used twice")
        ids.add(f["id"])
        for key in ("base", "depot"):
            x = bases.get(f[key])
            if x is None:
                bad.append(f"fleet {f['id']}: unknown {key} {f[key]}")
            elif x["side"] != f["side"]:
                bad.append(f"fleet {f['id']}: {key} {f[key]} is on another side")
            elif key == "depot" and not x.get("depot"):
                bad.append(f"fleet {f['id']}: {f[key]} is not a depot")
        if f["side"] not in sides:
            bad.append(f"fleet {f['id']}: unknown side {f['side']}")
        for r in f["regions"]:
            if r not in REGIONS:
                bad.append(f"fleet {f['id']}: unknown sea region {r}")
    for side in sides:
        held = [r for f in world["fleets"] if f["side"] == side for r in f["regions"]]
        for rid in REGIONS:
            if held.count(rid) != 1:
                bad.append(f"sea region {rid} is in {held.count(rid)} fleets of {side}; DCM needs exactly one")
    cs = world["careerStarts"]
    if not 1 <= cs["subsMost"] <= 3 or cs["budget"] <= 0:
        bad.append("careerStarts: budget above 0 and subsMost 1 to 3")
    seen = set()
    for s in cs["starts"]:
        if s["id"] in seen:
            bad.append(f"career start {s['id']} is used twice")
        seen.add(s["id"])
        if not set(s["nations"]) <= playable:
            bad.append(f"career start {s['id']}: {s['nations']} not all nations of a playable side")
        if s["kind"] not in ("tf", "sub") or s["difficulty"] not in ("easy", "medium", "hard"):
            bad.append(f"career start {s['id']}: kind tf or sub, difficulty easy, medium or hard")
        o = s["firstOrder"]
        points = [(s["lat"], s["lon"])] + ([(o["lat"], o["lon"])] if "lat" in o else [])
        for lat, lon in points:
            if not (b["latMin"] <= lat <= b["latMax"] and b["lonMin"] <= lon <= b["lonMax"]):
                bad.append(f"career start {s['id']}: {lat}, {lon} outside the bounds")
            elif is_water and is_water(lat, lon) is False:
                bad.append(f"career start {s['id']}: {lat}, {lon} is land")
        if o["kind"] == "defend":
            x = bases.get(o["base"])
            side = next(sd["id"] for sd in world["sides"] if s["nations"][0] in sd["nations"])
            if x is None or x["side"] != side:
                bad.append(f"career start {s['id']}: defend base {o['base']} is not its side's")
        if o["kind"] not in ("hold", "intercept", "defend") or not o["title"] or not o["briefing"] or o["days"] <= 0:
            bad.append(f"career start {s['id']}: first order needs a known kind, a title, a briefing and days")
    if is_water:
        lat = LAT_MIN + step / 2
        while lat < LAT_MAX:
            lon = LON_MIN + step / 2
            while lon < LON_MAX:
                if is_water(lat, lon) and len(region_of(lat, lon)) != 1:
                    wrapped = ((lon + 180) % 360) - 180
                    if not any(s <= lat <= n and w <= wrapped <= e for _nm, s, n, w, e in INLAND):
                        bad.append(f"water at {lat}, {lon} is in {len(region_of(lat, lon))} regions")
                lon += step
            lat += step
    if bad:
        raise ValueError("GCO command structure:\n  " + "\n  ".join(bad))
