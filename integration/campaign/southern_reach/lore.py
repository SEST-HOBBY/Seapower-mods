"""The story screens: a prologue, the chapter reports and the documents the
cast writes, hung before the missions they belong to, and an epilogue. The
builder takes EVENTS[0] as the prologue and EVENTS[-1] as the epilogue and
hangs the rest before the mission each names in `before`, in this order.

Forms are Southern Watch's four: a press sheet, a signal (cable, memo or
intercept), a deck-log extract and an INTSUM. Everything here is fiction, and
no page names a hull the player could have lost as alive: where a loss is
possible the page speaks of the class, the squadron or the role.
"""

EVENTS = [
    # --- prologue -----------------------------------------------------------
    dict(file="00_opening", title="Southern Departure\\n6 December 2028",
         sub="The season opens with a convoy, a trawler and a question",
         dateline="6 DECEMBER 2028  |  MARITIME BORDER COMMAND, HOBART DETACHMENT",
         headline="THE SEASON OPENS",
         body=[
             "The ceasefire in the north is nine days old. The task group that "
             "held the corridor is alongside at Sydney with its dents, and the "
             "escort work has moved south with the summer: the Antarctic resupply "
             "season, which runs on a calendar the ice keeps and nobody else.",
             "Hobart sails the stations' cargo, fuel and people every December. "
             "This year it sails them past a fishing fleet that arrived in "
             "October under a fisheries-protection flag, a research trawler with "
             "more antennas than nets, and a frigate that has been asking "
             "merchant masters for their compliance paperwork sixty miles south "
             "of Tasmania.",
             "None of it is a war. All of it is the same network the north just "
             "fought, with the name changed and the pretext changed to "
             "conservation. MV Coral Pioneer, with a bearing that held and a "
             "master who would not heave to, is chartered for the Macquarie "
             "run.",
             "Get the convoy out of Storm Bay. Put a name on the trawler. Nobody "
             "shoots at a fishing boat in December."]),

    # --- before SR02 Silent Track: the 6 December log, ahead of the 8 December cable
    dict(file="00c_santos_log", before="Silent Track", form="log",
         title="Master's log, MV Coral Pioneer\\n6 December 2028",
         sub="Deck log extract, the morning out of Storm Bay",
         ship="MV Coral Pioneer", master="L. Santos", date="6 December 2028",
         entries=[
             ("0515", "Departed the Derwent astern of SOUTHERN ENDEAVOUR, DERWENT "
                      "SPIRIT in company. Convoy speed 12 kn. Escort on the "
                      "starboard quarter, same class as October."),
             ("0602", "Trawler fleet on radar to the south. Three hulls. One of "
                      "them has been forty miles off the Derwent every time a ship "
                      "sailed for the ice since October. Voyage leader Dr Marsh "
                      "asked me which one. I said the one with the antennas."),
             ("0640", "Hailed on Ch16 by \"Fisheries Protection\" and asked for "
                      "our environmental compliance certificate. Told them our "
                      "compliance is with the Australian Antarctic Division and "
                      "they could ask Hobart. They asked again. Escort came up "
                      "on the same channel and the conversation ended."),
             ("0730", "Clear of the bay. Airlink went over for Wilkins at 0620, on time. "
                      "Sea state four and building. Chief reports the No.2 "
                      "bearing at 48 degrees and steady. He has stopped mentioning "
                      "it, which means he is watching it.")],
         note="For the owners: the escort did not have to be told what the "
              "trawler was. Whoever she is, she has learned from October.  - L.S."),

    # --- before SR02 Silent Track ------------------------------------------
    dict(file="00b_rewi_cable", before="Silent Track", form="signal",
         title="Wellington's allocation\\n8 December 2028",
         sub="Signal from No. 5 Squadron RNZAF",
         header=[("FROM:", "SQNLDR T. REWI, NO. 5 SQN RNZAF, OHAKEA"),
                 ("TO:", "COMAUSMARTG (CDRE MERCER)"), ("DTG:", "080410Z DEC 28"),
                 ("PREC:", "PRIORITY"), ("SUBJ:", "MACQUARIE RIDGE - AIRCRAFT AND TERMS")],
         body=[
             "1. WELLINGTON HAS ALLOCATED ONE POSEIDON, ONE CREW, ONE SORTIE A "
             "DAY FOR THE RIDGE SEARCH, KIWI 05, MY CREW, OUT OF OHAKEA. THE "
             "AIRCRAFT REMAINS UNDER NATIONAL COMMAND. IT FLIES YOUR PLAN.", "",
             "2. THE CONTACT REPORTED BY THE LONGLINER SOUTH OF CAMPBELL ON THE "
             "SIXTH IS NOT A DIESEL BOAT. NOTHING DIESEL IS TWELVE HUNDRED MILES "
             "FROM A TENDER IN DECEMBER. IT IS NUCLEAR AND IT IS WORKING THE "
             "RIDGE BECAUSE THE RIDGE IS WHERE THE RESUPPLY ROUTE CROSSES.", "",
             "3. YOUR BOAT AND MY AIRCRAFT WILL PUT A NAME ON IT. THE CEASEFIRE "
             "HOLDS DOWN HERE UNTIL SOMEBODY SAYS IT DOES NOT, AND THAT IS NOT "
             "GOING TO BE A POSEIDON WITH A TORPEDO.", "",
             "4. A RESEARCH VESSEL WITH A NEW ZEALAND FLAG, RV SOUTHERN SURVEYOR, "
             "IS ON THE RIDGE WITH A SCIENCE PARTY. SHE IS OURS. SHE HAS BEEN TOLD "
             "TO KEEP HER TRANSPONDER ON AND HER MOUTH SHUT.", "",
             "REWI"]),

    # --- before SR04 Macquarie Passage ------------------------------------
    dict(file="01_sitrep", before="Macquarie Passage",
         title="The first fortnight\\n14 December 2028",
         sub="Two names on a chart and a crew brought home",
         dateline="14 DECEMBER 2028  |  MARITIME BORDER COMMAND, HOBART DETACHMENT",
         headline="THE SOUTH HAS A PICTURE",
         body=[
             "The convoy is south. The trawler that was not one has a name - "
             "Nan Hai 27, a converted Okean hull with a collection fit that "
             "would not disgrace a navy - and so has the boat working the "
             "Macquarie Ridge, which Collins and a New Zealand Poseidon tracked "
             "for three hours on the ninth without either side doing anything "
             "the ceasefire would have to notice.",
             "The airlink to Wilkins went out of contact on the southern route "
             "on the twelfth. Its crew came off a foreign trawler that had "
             "\"recovered\" them and was steaming away from the search with "
             "them aboard when the task group put a boarding party alongside. "
             "The trawler's master says he was taking them to the nearest "
             "medical facility. The nearest medical facility was Hobart, and he "
             "was not going there.",
             "Macquarie Island's resupply is next: HMAS Supply and Coral "
             "Pioneer into Buckles Bay for a service window that the island's "
             "weather allows about one day in three. The Russian research "
             "vessel that has been keeping station west of the island has a "
             "submarine somewhere near it, and the boat is not there for the "
             "science.",
             "Nobody has fired at anybody. The Commodore's note to the force "
             "this morning: \"That is the objective. Keep it that way, and "
             "keep the window.\""]),

    # --- before SR05 Empty Horizon -----------------------------------------
    dict(file="01b_ams_intercept", before="Empty Horizon",
         form="signal", strap="INTERCEPT",
         title="Intercept: the AMS net\\n17 December 2028",
         sub="Commercial HF, transcribed",
         header=[("NET:", "COMMERCIAL HF, 8291 KHZ - THE SAME FREQUENCY AS OCTOBER"),
                 ("DTG:", "170220Z DEC 28"),
                 ("NOTE:", "TRANSLATED / TRANSCRIBED. A: \"AUSTRAL CONTROL\". "
                           "B: \"PROTECTION ONE\". PARTIAL.")],
         body=[
             "A:  Protection One, Control. The command element holds its box "
             "south of the fleet until the carrier is in the area. Compliance "
             "corridors resume when it is.",
             "B:  Control, One. The grey force has a long-range aircraft over "
             "us every day. It sees the box.",
             "A:  It sees a fishing fleet with an escort. That is what it is "
             "for. Do not illuminate the aircraft. Do not answer the aircraft.",
             "B:  And the trawler.",
             "A:  The trawler is a trawler. Control out.",
             "B:  [unreadable] ... eight days ... [unreadable]"],
         note="Speaker A's traffic pattern matches the Meridian duty controller "
              "of 1 November. \"The carrier\" is assessed as the group's "
              "reinforcement, transiting; not yet in the Southern Ocean. "
              "\"Eight days\" is not understood."),

    # --- before SR06 Broken Supply Line ------------------------------------
    dict(file="01c_brand_signal", before="Broken Supply Line", form="signal",
         title="Where the ships are\\n21 December 2028",
         sub="Signal from the New Zealand maritime liaison",
         header=[("FROM:", "CDR T. BRAND RNZN, HQ JOINT FORCES NEW ZEALAND"),
                 ("TO:", "COMAUSMARTG"), ("DTG:", "201500Z DEC 28"),
                 ("PREC:", "PRIORITY"), ("SUBJ:", "BLUFF, INVERCARGILL AND THE FLEET")],
         body=[
             "1. BLUFF IS OPEN TO YOUR SHIPS FOR REPAIR AND STORES. THE SLIPWAY "
             "CAN TAKE A COASTER. INVERCARGILL AIRPORT IS OPEN TO YOUR POSEIDONS "
             "AND OURS; A DETACHMENT IS THERE FROM THIS MORNING.", "",
             "2. SO THAT NOBODY HAS TO ASK: TE KAHA IS IN DEVONPORT IN THE MIDDLE "
             "OF A REFIT SHE CANNOT LEAVE, AND TE MANA IS ON THE PACIFIC STATION "
             "WITH A TREATY OBLIGATION SHE CANNOT LEAVE EITHER. NEW ZEALAND'S "
             "CONTRIBUTION TO THIS IS ITS PORTS, ITS AIRFIELDS AND NO. 5 "
             "SQUADRON, AND I WILL NOT PRETEND OTHERWISE IN A SIGNAL.", "",
             "3. THE COASTER DERWENT SPIRIT IS MAKING SIX KNOTS TOWARDS BLUFF "
             "WITH A HULL PATCH AND ONE ENGINE. WHATEVER HIT HER, SHE IS INSIDE "
             "OUR SEARCH AND RESCUE REGION AND WE ARE TREATING IT AS AN ATTACK "
             "UNTIL SOMEBODY SHOWS US IT WAS NOT.", "",
             "BRAND"]),

    # --- before SR07 Beneath the South -------------------------------------
    dict(file="02_sitrep", before="Beneath the South",
         title="The first shot in the south\\n23 December 2028",
         sub="A torpedo, a coaster and an authorisation",
         dateline="23 DECEMBER 2028  |  MARITIME BORDER COMMAND, HOBART DETACHMENT",
         headline="THIS IS NO LONGER A CEASEFIRE",
         body=[
             "A torpedo hit the fuel coaster on the resupply route on the "
             "twenty-first, south of the Auckland Islands, in New Zealand's "
             "search and rescue region and in nobody's war. The coaster made "
             "Bluff on one engine with an escort on each side of her. The "
             "boat that fired was the boat Collins tracked on the ridge on the "
             "ninth, and everybody knows it.",
             "Canberra and Wellington said the same thing on the same afternoon, "
             "which has not happened before. The task group is authorised to "
             "find the boat that fired and sink it. It is not authorised to "
             "touch the research vessel the boat lives off, which is a merchant "
             "hull under a state flag with a science party aboard, and the "
             "difference between those two sentences is the campaign.",
             "The fisheries-protection group has not commented. Its frigate has "
             "moved south to the fleet, and its intelligence trawler has moved "
             "with it. The carrier the intercepts talk about has been seen "
             "leaving the Java Sea, heading south-east.",
             "Christmas Eve, 57 South. The task group sails with what it "
             "rearmed at Bluff and a Poseidon it will have to share with the "
             "weather."]),

    # --- before SR08 The Gateway ------------------------------------------
    dict(file="02b_ward_memo", before="The Gateway", form="signal",
         title="Air component note\\n27 December 2028",
         sub="What flying at the bottom of the world costs",
         header=[("FROM:", "WGCDR D. WARD, AIR COMPONENT, RAAF EDINBURGH"),
                 ("TO:", "COMAUSMARTG"), ("DTG:", "270500Z DEC 28"),
                 ("SUBJ:", "THE SOUTH - WHAT A SORTIE COSTS")],
         body=[
             "1. A POSEIDON OUT OF HOBART IS ON TASK AT 55 SOUTH FOR TWO HOURS "
             "AND THEN IT IS NOT. THERE IS NO TANKER DOWN HERE, THERE WILL BE NO "
             "TANKER DOWN HERE, AND EVERY PLAN THAT ASSUMES OTHERWISE IS A PLAN "
             "WITH A HOLE IN IT.", "",
             "2. THE TRITON FLIES WHEN THE WEATHER AT HOBART LETS IT LAND AGAIN. "
             "SOUTH OF SIXTY THE WEATHER DOES NOT ASK. ASSUME THE ORBIT IS NOT "
             "THERE ON THE DAY YOU NEED IT MOST.", "",
             "3. NO FIGHTER IN AUSTRALIA CAN REACH ANYTHING SOUTH OF TASMANIA AND "
             "COME HOME. UNTIL THE FORCE IS BACK IN THE TASMAN, THE DESTROYER IS "
             "THE AIR DEFENCE. BUY ACCORDINGLY.", "",
             "4. THE NEW ZEALANDERS ARE FLYING OUT OF INVERCARGILL AND "
             "CHRISTCHURCH WITH ONE CREW AND ONE AIRCRAFT AT A TIME. THEY ARE "
             "GOOD. THEY ARE ALSO ONE AIRCRAFT.", "",
             "WARD"]),

    # --- before SR09 Cold Route -------------------------------------------
    dict(file="03_sitrep", before="Cold Route",
         title="The second voyage\\n1 January 2029",
         sub="The carrier is in the Southern Ocean",
         dateline="1 JANUARY 2029  |  MARITIME BORDER COMMAND, HOBART DETACHMENT",
         headline="THE GROUP HAS ITS CARRIER",
         body=[
             "The boat that fired on the coaster was hunted on Christmas Eve at "
             "57 South, and the task group's report on the hunt is in the "
             "ledger. The gateway at Christchurch was held on the twenty-eighth "
             "with a corvette trying to inspect a tanker in Pegasus Bay and a "
             "New Zealand Poseidon overhead telling it, in two languages, that "
             "it would not.",
             "The carrier is here. It arrived south of the fishing fleet on the "
             "thirtieth with two frigates and a corvette, and its aircraft flew "
             "over the fleet on New Year's Eve for the cameras. The protection "
             "group now has a flagship, an air wing and a reason to think the "
             "resupply season is negotiable.",
             "It is not. The January voyage sailed from Hobart on the thirty-first: Southern Endeavour "
             "with Casey's second lift, the coaster out of Bluff with a new "
             "plate and the same Chief, Coral Pioneer, and two more hulls the "
             "Division has chartered because it will not be told to wait.",
             "Wedgetail is back with the force for this one. No fighter is. "
             "The destroyer is the air defence, and the Commodore has said so "
             "in writing to everybody who wanted a different answer."]),

    # --- before SR10 Southern Line ----------------------------------------
    dict(file="03b_intsum", before="Southern Line", form="intsum",
         title="The command element\\n5 January 2029",
         sub="Coalition Joint Intelligence summary",
         org="Coalition Joint Intelligence Centre, Hobart", ref="INTSUM 029-02",
         date="5 January 2029", subject="The protection group's command element",
         body=[
             "1. The Southern Ocean Fisheries and Research Protection Group is "
             "assessed as one carrier, two to three frigates, one to two "
             "corvettes, one intelligence collector (NAN HAI 27) and a "
             "replenishment hull, with a Russian research-support detachment - "
             "a tender, at least one nuclear boat, and very long-range aircraft "
             "with tanker support - operating alongside it under a separate "
             "arrangement.",
             "2. Its command element has moved to the ice edge with the fishing "
             "fleet, south of the Casey line. Assessed intent: to be where the "
             "last resupply voyages must pass, to be seen there, and to be fired "
             "on first.",
             "3. Guidance to the force. Identify the carrier and the collector "
             "by class and name. Do not fire on a unit that has not fired. A "
             "research vessel at the ice edge is a research vessel, whatever it "
             "was last month. A trawler is a trawler.",
             "4. The boat the task group hunted on 24 December is either on the "
             "bottom or in that line. The force will know which when it "
             "arrives."],
         note="Para 3 is the whole mission. Again.  - AM"),

    # --- before SR11 Last Ship South --------------------------------------
    dict(file="03c_marsh_signal", before="Last Ship South", form="signal",
         title="From the voyage leader\\n9 January 2029",
         sub="A message from RSV Southern Endeavour",
         header=[("FROM:", "DR H. MARSH, VOYAGE LEADER, RSV SOUTHERN ENDEAVOUR"),
                 ("TO:", "CDRE MERCER, FOR THE ESCORT COMMANDER"),
                 ("DTG:", "090710Z JAN 29"), ("SUBJ:", "THE LAST VOYAGE SOUTH")],
         body=[
             "1. CASEY HAS ITS PEOPLE, ITS FOOD AND MOST OF ITS SPARES. IT DOES "
             "NOT HAVE ITS WINTER FUEL, BECAUSE THE COASTER'S FIRST VOYAGE ENDED "
             "AT BLUFF AND HER SECOND WAS FOUGHT THROUGH. WHAT SAILS ON THE "
             "TENTH IS THE WINTER.", "",
             "2. I AM TOLD THE ESCORT HAS SPENT MOST OF WHAT IT SAILED WITH. I "
             "AM TOLD THERE IS NO FIGHTER, NO TANKER AND, SOUTH OF FIFTY-FIVE, "
             "NO POSEIDON. I AM NOT A NAVAL OFFICER AND I DO NOT KNOW WHAT THAT "
             "MEANS FOR US. I WOULD LIKE TO BE TOLD, PLAINLY, BEFORE WE SAIL.", "",
             "3. THE EXPEDITIONERS HAVE ASKED ME WHETHER THE ESCORT WILL BE THERE "
             "THE WHOLE WAY. I HAVE SAID YES. PLEASE DO NOT MAKE THAT A LIE.", "",
             "MARSH"]),

    # --- before SR12 Turning North ----------------------------------------
    dict(file="04_sitrep", before="Turning North",
         title="The season is supplied\\n13 January 2029",
         sub="The stations have their winter; the group turns north",
         dateline="13 JANUARY 2029  |  MARITIME BORDER COMMAND, HOBART DETACHMENT",
         headline="THE STATIONS ARE SUPPLIED",
         body=[
             "The last ship south is south. Casey has its winter fuel, Davis and "
             "Mawson their lifts, Macquarie its year, and the Division's "
             "operations manager has sent the task group a photograph of a "
             "fuel gauge with nothing written under it.",
             "The protection group has turned north. Its carrier, its escorts, "
             "its collector, its replenishment hull and the Russian tender are "
             "in company, transiting east of Tasmania into the Tasman at "
             "fourteen knots, and the fishing fleet it came to protect has "
             "been left to fish.",
             "Nobody in Canberra or Wellington believes it is going home. The "
             "Tasman is where the two countries' ports, ferries, cables and "
             "trade are, and a group that wanted to make the Antarctic route "
             "unusable and could not is now between Sydney and Auckland.",
             "The task group's last job in the south is to shadow it out and "
             "put a name on every hull in the network. Its first job in the "
             "north will be to meet it."]),

    # --- chapter card: before TS01 Home Waters ----------------------------
    dict(file="05_chapter", before="Home Waters",
         title="Tasman Shield\\n21 January 2029",
         sub="Chapter B: the approaches two countries share",
         dateline="21 JANUARY 2029  |  MARITIME BORDER COMMAND, SYDNEY",
         headline="TASMAN SHIELD",
         body=[
             "The task group is alongside at Sydney for six days, and the "
             "ledger says what it has: the hulls that came out of the south, "
             "the aircraft that came back, and the magazines as Hobart's last "
             "window left them.",
             "The group that came north has its carrier and its flagship in the "
             "Tasman, a tender and a boat working the New Zealand side, a "
             "compliance contractor with coasters in every port, and an aim "
             "that has not changed since October: make the approaches unusable "
             "long enough that a \"joint compliance\" settlement looks like "
             "peace.",
             "New Zealand's contribution is No. 5 Squadron, Ohakea, Whenuapai, "
             "Invercargill and Christchurch, and Commander Brand's plain "
             "signals about where its ships are not. Australia's is the task "
             "group, Williamtown's fighters from the fourth week, and the "
             "Poseidons at Edinburgh.",
             "Fiordland first: the tourist traffic hides a tender. Then Cook "
             "Strait, then the crossing. The relief detachment for the "
             "Antarctic gateway flies the air bridge on the eleventh of "
             "February and a carrier is between it and Sydney."]),

    # --- before TS03 Chatham Watch ----------------------------------------
    dict(file="05b_rewi_cable", before="Chatham Watch", form="signal",
         title="Two air forces\\n27 January 2029",
         sub="Signal from No. 5 Squadron RNZAF",
         header=[("FROM:", "SQNLDR T. REWI, NO. 5 SQN RNZAF, OHAKEA"),
                 ("TO:", "COMAUSMARTG"), ("DTG:", "270300Z JAN 29"),
                 ("PREC:", "IMMEDIATE"), ("SUBJ:", "WEST OF THE CHATHAMS - THE RENDEZVOUS")],
         body=[
             "1. THE BOAT COOK STRAIT PUT A NAME ON, TANGO, IS A DIESEL BOAT. A "
             "DIESEL BOAT NEEDS A TENDER. THE TENDER IS THE AMS COASTER FIORDLAND "
             "NAMED, AUSTRAL COMPLIANCE, AND SHE SAILED EAST FROM THE STRAIT ON THE "
             "TWENTY-SIXTH WITH HER TRANSPONDER OFF.", "",
             "2. A BOAT AND A TENDER MEET ON THE SURFACE, IN DAYLIGHT, WHERE "
             "NOBODY LOOKS. EAST OF NEW ZEALAND, WEST OF THE CHATHAMS, IS WHERE "
             "NOBODY LOOKS. WE WILL BE LOOKING.", "",
             "3. YOUR POSEIDON AND MINE, ONE SEARCH PLAN, TWO AIR FORCES, OUT OF "
             "OHAKEA. WELLINGTON HAS AUTHORISED WEAPONS ON THE BOAT. IT HAS NOT "
             "AUTHORISED WEAPONS ON THE COASTER, WHICH IS A MERCHANT HULL WITH A "
             "CREW WHO WERE TOLD THEY WERE DELIVERING FUEL.", "",
             "4. KEEP EVERYTHING WEST OF THE DATE LINE. THE CHATHAMS ARE ON THE "
             "OTHER SIDE OF IT AND SO IS TOMORROW.", "",
             "REWI"]),

    # --- before TS04 Tasman Crossing --------------------------------------
    dict(file="06_sitrep", before="Tasman Crossing",
         title="The New Zealand side\\n31 January 2029",
         sub="Fiordland, Cook Strait and a rendezvous that did not happen",
         dateline="31 JANUARY 2029  |  MARITIME BORDER COMMAND, SYDNEY",
         headline="THE STRAIT IS OPEN",
         body=[
             "The tender was found among the Milford cruise ships on the "
             "twenty-second. The boat it served was found on the Cook Strait "
             "cable route on the twenty-fifth, among the ferries, and the "
             "ferries ran. The two of them tried to meet east of New Zealand on "
             "the twenty-eighth and two air forces were there first.",
             "Wellington has published the recordings. The compliance "
             "contractor has announced a review of its subcontractors. The "
             "group's carrier has not commented and has moved into the middle "
             "of the Tasman with a flagship, two frigates and an air wing that "
             "has been flying over the Sydney-Auckland airway for four days.",
             "Merchant traffic across the Tasman is sailing in dispersed groups "
             "with whatever escort can be found, which is the task group. "
             "Williamtown's fighters reach the middle of the crossing and no "
             "further; Wedgetail sees the carrier's aircraft come and cannot "
             "stop them.",
             "The Commodore's note: \"Two groups, thirty miles apart, one "
             "escort force. Decide which one you are with when the strike "
             "comes, and be with it.\""]),

    # --- before TS09 The Southern Convoy ----------------------------------
    dict(file="07_sitrep", before="The Southern Convoy",
         title="The Australian side\\n18 February 2029",
         sub="The Tasman held, Bass Strait sorted, the Bight searched",
         dateline="18 FEBRUARY 2029  |  MARITIME BORDER COMMAND, SYDNEY",
         headline="ONE CONVOY THAT MUST WORK",
         body=[
             "The crossing held on the first. Farncomb fought the group's "
             "nuclear boat under the cable corridor on the fourth and her "
             "report is in the ledger. Bass Strait's rigs are standing, its "
             "ferries ran, and a merchant that radiated a frigate's radars for "
             "six hours was told what it was on channel 16 and did not answer. "
             "The relief detachment crossed the air bridge on the eleventh "
             "under Williamtown's fighters and a carrier's.",
             "The Bight was searched for four days for the Russian detachment's "
             "last boat and the oiler that keeps it at sea. What was found "
             "there is in the ledger too.",
             "The group's carrier, its flagship and what is left of its escorts "
             "are south of the Portland approaches, and the southern convoy - "
             "Adelaide's fuel, Melbourne's cargo, and Coral Pioneer, because "
             "she is always there - sails tomorrow through them.",
             "It is a fleet action, and it is the group's last full-strength "
             "one. The task group sails with everything it owns, rearmed at "
             "Adelaide, with Edinburgh's Poseidons and fighters "
             "overhead. After it, both navies will be counting."]),

    # --- before TS11 Approaches -------------------------------------------
    dict(file="07b_opposing_intercept", before="Approaches",
         form="signal", strap="INTERCEPT",
         title="Intercept: the group commander\\n25 February 2029",
         sub="Naval HF, partial decrypt, released to the force",
         header=[("NET:", "NAVAL HF, ENCRYPTED, PARTIAL DECRYPT"),
                 ("DTG:", "250140Z FEB 29"),
                 ("NOTE:", "TRANSLATED. SPEAKER: THE PROTECTION GROUP COMMANDER, "
                           "TO HIGHER. ASSESSED AUTHENTIC.")],
         body=[
             "... the group has been at sea since October and in contact since "
             "December. I have a carrier with an air wing that has flown "
             "seventy days, a flagship I am ordered not to lose, and escorts "
             "that have been where the other side's aircraft could reach them "
             "for a month. The approaches can be closed for a week. They cannot "
             "be held.", "",
             "The two navies are smaller than they were in December. They are "
             "also two navies now, and they fly out of each other's airfields. "
             "Their escorts do not chase. They protect the movement and let us "
             "come to them, and the last time we came to them we came back "
             "with fewer ships.", "",
             "I request guidance on whether the closure is to be enforced "
             "against the movement expected on the twenty-sixth, and on which "
             "of the two elements detached to the ports is to rejoin. If both "
             "are held where they are, I will enforce it with what I have ..."],
         note="\"Which of the two elements is to rejoin\" is assessed as the "
              "northern and southern detachments off Auckland and Adelaide. "
              "Whichever the task group did not hold on the twenty-second will "
              "be in the western Tasman on the twenty-sixth. Both, if neither "
              "was."),

    # --- before TS12 Southern Cross ---------------------------------------
    dict(file="08_santos_log", before="Southern Cross", form="log",
         title="Master's log, MV Coral Pioneer\\n28 February 2029",
         sub="Deck log extract, sailing day",
         ship="MV Coral Pioneer", master="L. Santos", date="28 February 2029",
         entries=[
             ("0930", "Convoy conference aboard the flagship. Four hulls for "
                      "Auckland with the relief cargo. One group out there is "
                      "complying with the withdrawal and one has not said. Told: "
                      "\"Sail as planned.\" Same words as November."),
             ("1015", "Chief reports the No.2 bearing at 66 degrees. Will hold at "
                      "eleven knots. Convoy speed is eleven knots."),
             ("1100", "Crew briefed. The two who asked in November whether the "
                      "escort that stopped us on 18 October was out there asked "
                      "again about the trawler that held the airlink's crew in "
                      "December. I said I did not know. That is true."),
             ("1630", "Sydney Heads astern. Escorts on both beams. A New "
                      "Zealand aircraft overhead going the same way we are. "
                      "Three months ago this ship was chartered for a fortnight.")],
         note="For whoever reads these afterwards: we have now been escorted by "
              "the same people through two seas, a strait, a bay at the bottom "
              "of the world and a summer. They are fewer than they were. So are "
              "we. The route is open.  - L.S."),

    # --- epilogue ----------------------------------------------------------
    dict(file="24_closing", title="Southern Cross\\n2 March 2029",
         sub="The approaches held, and what it cost",
         dateline="2 MARCH 2029  |  MARITIME BORDER COMMAND, SYDNEY",
         headline="THE APPROACHES ARE OURS",
         body=[
             "The last movement went through. The group that came south in "
             "October to make the Antarctic route unusable, and came north in "
             "January to do the same to the Tasman, has turned for home with "
             "fewer ships than it arrived with, and the two navies that held "
             "the line against it are alongside at Sydney and Devonport "
             "counting what is left.",
             "The stations are supplied through the winter. The ferries run. "
             "The cable is where it was. The rigs are standing. The relief "
             "detachment is at Christchurch. The compliance contractor has "
             "closed its Hobart office.",
             "What the ledger says about the task group after three months in "
             "the south, the ledger says: which hulls, which aircraft, which "
             "magazines. That is the measure of this campaign - not the "
             "exchange, the route and the people who used it, in two countries.",
             "Master Santos's entry for the arrival, which she has allowed to "
             "be quoted, reads: \"Alongside Auckland. All hands. Same escort.\"",
             "Stand down the watch."]),
]
