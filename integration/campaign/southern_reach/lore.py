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
         sub="A 'fisheries' frigate is stopping ships bound for Antarctica",
         dateline="6 DECEMBER 2028  |  MARITIME BORDER COMMAND, HOBART DETACHMENT",
         headline="THE PAPER WAR GOES SOUTH",
         body=[
             "Nine days after the ceasefire in the north, the network that "
             "tried to close the Arafura has come south under a new flag. The "
             "Southern Ocean Fisheries and Research Protection Group - a "
             "frigate, two corvettes and a research trawler with more antennas "
             "than nets - has been off Tasmania since October.",
             "Its frigate demands a compliance certificate from every ship bound "
             "for the ice. Its contractor, Austral Meridian Services, shares an "
             "address with Meridian's old escort company. New name; the "
             "pretext is now conservation.",
             (
                 "Hobart's first convoy of the season - the resupply ship Southern Endeavour, "
                 "the fuel coaster Derwent Spirit and MV Coral Pioneer - sails at dawn with the"
                 " stations' year of fuel, food and people, under a new southern force "
                 "allocation informed by the northern escort operation."
             ),
             "Get the convoy out of Storm Bay. Put a name on the trawler. "
             "Nobody shoots at a fishing boat in December."]),

    # --- before SR02 Silent Track: the 6 December log, ahead of the 8 December cable
    dict(file="00c_santos_log", before="Silent Track", form="log",
         title="Master's log, MV Coral Pioneer\\n6 December 2028",
         sub="Deck log extract, the morning out of Storm Bay",
         ship="MV Coral Pioneer", master="L. Santos", date="6 December 2028",
         entries=[
             ("0515", "Departed the Derwent astern of SOUTHERN ENDEAVOUR, DERWENT "
                      "SPIRIT in company. Convoy speed 12 kn. Escort on the "
                      "starboard quarter, from the task group that came for us in "
                      "the Arafura in October."),
             ("0602", "Trawler fleet on radar to the south. Three hulls. One of "
                      "them has been forty miles off the Derwent every time a ship "
                      "sailed for the ice since October. Dr Marsh, the voyage leader "
                      "in SOUTHERN ENDEAVOUR, asked me on VHF which one. I said the one with the antennas."),
             ("0640", "Hailed on Ch16 by \"Fisheries Protection\" and asked for "
                      "our environmental compliance certificate. Told them our "
                      "compliance is with the Australian Antarctic Division and "
                      "they could ask Hobart. They asked again. Escort came up "
                      "on the same channel and the conversation ended."),
             ("0730", (
                 "Clear of the bay. Wilkins airlink passed overhead at 0620. Sea state 4 and "
                 "building. Chief Engineer reports No. 2 bearing at 48 degrees C and steady. "
                 "Machinery watch continued."
             ))],
         note="For the owners: the escort did not have to be told what the "
              "trawler was. Whoever she is, she remembers what Meridian's "
              "Escort Seven did in the Arafura.  - L.S."),

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
             (
                 "2. THE LONGLINER'S REPORT SOUTH OF CAMPBELL ON THE SIXTH GIVES US A SEARCH "
                 "AREA, NOT A CLASSIFICATION. SUBSEQUENT ACOUSTIC REPORTING SUGGESTS A NUCLEAR "
                 "SUBMARINE. RANGE FROM A TENDER DOES NOT EXCLUDE A DIESEL-ELECTRIC BOAT. "
                 "COLLINS AND KIWI 05 ARE TO CONFIRM THE CONTACT."
             ), "",
             "3. COLLINS AND MY AIRCRAFT WILL PUT A NAME ON IT. THE CEASEFIRE "
             "HOLDS DOWN HERE UNTIL SOMEBODY SAYS IT DOES NOT, AND THAT IS NOT "
             "GOING TO BE A POSEIDON WITH A TORPEDO.", "",
             "4. A RESEARCH VESSEL WITH A NEW ZEALAND FLAG, RV SOUTHERN SURVEYOR, "
             "IS ON THE RIDGE WITH A SCIENCE PARTY. SHE IS OURS. SHE HAS BEEN TOLD "
             "TO KEEP HER TRANSPONDER ON AND HER MOUTH SHUT.", "",
             "REWI"]),

    # --- before SR04 Macquarie Passage ------------------------------------
    dict(file="01_sitrep", before="Macquarie Passage",
         title="The first week\\n14 December 2028",
         sub="Two names on a chart and a crew brought home",
         dateline="14 DECEMBER 2028  |  MARITIME BORDER COMMAND, HOBART DETACHMENT",
         headline="THE SOUTH HAS A PICTURE",
         body=[
             (
                 "The first convoy has cleared Storm Bay. Reports identify Nan Hai 27 as the "
                 "suspected collector among the fishing vessels. On 9 December, Collins and a "
                 "New Zealand Poseidon classified an Akula on the Macquarie Ridge, designated "
                 "VICTOR. The acoustic record gives later patrols a basis for comparison; it "
                 "does not establish the submarine's present position."
             ),
             "The airlink to Wilkins went down on the southern route on the "
             "twelfth. Its crew were found aboard Nan Hai 24, a factory trawler "
             "from the fishing fleet the protection group escorts. She had "
             "\"recovered\" them and was hove to, waiting for Nan Hai 27 to come "
             "for them, when the task group put a boarding party alongside. "
             "The trawler's master says he was taking them to the nearest "
             "medical facility. The nearest medical facility was Hobart, and he "
             "was not going there.",
             "Macquarie Island's resupply is next: HMAS Supply and Coral "
             "Pioneer into Buckles Bay for a service window that the island's "
             "weather allows about one day in three. The Russian research "
             "vessel Akademik Fersman, keeping station west of the island, has a "
             "submarine somewhere near her, and the boat is not there for the "
             "science.",
             "Nobody has fired at anybody. The Commodore's note to the force "
             "this morning: \"That is the aim. Keep it that way, and "
             "keep the window.\""]),

    # --- before SR05 Empty Horizon -----------------------------------------
    dict(file="01b_ams_intercept", before="Empty Horizon",
         form="signal", strap="INTERCEPT",
         title="Intercept: the Austral Meridian net\\n17 December 2028",
         sub="Commercial HF, transcribed",
         header=[("NET:", "COMMERCIAL HF, 8291 KHZ - THE MERIDIAN NET'S FREQUENCY IN THE NORTH"),
                 ("DTG:", "170220Z DEC 28"),
                 ("NOTE:", "TRANSLATED / TRANSCRIBED. A: \"AUSTRAL CONTROL\". "
                           "B: \"PROTECTION ONE\", ASSESSED AS THE GROUP'S FRIGATE. PARTIAL.")],
         body=[
             (
                 "A: Protection One, Control. The command element holds its box south of the "
                 "fleet until the carrier is in the area. Compliance corridors resume when it "
                 "is."
             ),
             (
                 "B: Control, One. The grey force has a long-range aircraft over us every day. "
                 "It sees the box."
             ),
             (
                 "A: It sees a fishing fleet with an escort. That is what it is for. Do not "
                 "illuminate the aircraft. Do not answer the aircraft."
             ),
             "B: And the trawler.",
             "A: The trawler is a trawler. Control out.",
             "B: [unreadable] ... eight days ... [unreadable]"],
         note="Speaker A's traffic pattern matches the Meridian duty controller "
              "intercepted in the north on 1 November. \"The carrier\" is assessed as the group's "
              "reinforcement, transiting; not yet in the Southern Ocean. "
              "\"Eight days\" is not understood."),

    # --- before SR06 Broken Supply Line ------------------------------------
    dict(file="01c_brand_signal", before="Broken Supply Line", form="signal",
         title="Where the ships are\\n21 December 2028",
         sub="Signal from the New Zealand maritime liaison",
         header=[("FROM:", "CDR T. BRAND RNZN, HQ JOINT FORCES NEW ZEALAND"),
                 ("TO:", "COMAUSMARTG"), ("DTG:", "201500Z DEC 28"),
                 ("PREC:", "PRIORITY"), ("SUBJ:", "BLUFF, INVERCARGILL AND OUR FRIGATES")],
         body=[
             "1. BLUFF IS OPEN TO YOUR SHIPS FOR REPAIR AND STORES. THE SLIPWAY "
             "CAN TAKE A COASTER. INVERCARGILL AIRPORT IS OPEN TO YOUR POSEIDONS "
             "AND OURS; A DETACHMENT IS THERE FROM THIS MORNING.", "",
             "2. SO THAT NOBODY HAS TO ASK: THE FRIGATE TE KAHA IS AT DEVONPORT, "
             "AUCKLAND, IN THE MIDDLE OF A REFIT SHE CANNOT LEAVE, AND HER SISTER "
             "TE MANA IS ON THE PACIFIC STATION "
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
         headline="NO LONGER A CEASEFIRE",
         body=[
             (
                 "A torpedo struck Derwent Spirit on the resupply route on the twenty-first, "
                 "south of the Auckland Islands. The coaster reached the escort handover on one"
                 " engine and continued towards Bluff. Acoustic evidence links the attack to "
                 "VICTOR, the Akula reported on the Macquarie Ridge. Joint intelligence "
                 "assesses that link as probable; the next patrol must establish a fresh "
                 "contact."
             ),
             (
                 "Canberra and Wellington have authorised an operation against the submarine "
                 "responsible. RV Akademik Fersman, the research vessel associated with its "
                 "support network, is excluded from that authority. Its activities are to be "
                 "documented, not attacked. The distinction is specific to these orders: a "
                 "vessel's civilian appearance alone does not settle its role."
             ),
             (
                 "The fisheries-protection formation has made no public response. Satellite "
                 "radar imagery places its frigate and intelligence collector near the fishing "
                 "fleet. Separate imagery and intercepted naval traffic indicate a carrier "
                 "movement from the Java Sea towards the south-east. These are dated "
                 "observations; patrol aircraft are tasked to establish the formation's current"
                 " position."
             ),
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
             (
                 "1. POSEIDON SORTIES FROM HOBART HAVE LIMITED TIME ON STATION AFTER TRANSIT "
                 "AND RECOVERY RESERVES. NO TANKER IS ALLOCATED TO THESE SOUTHERN PATROLS. PLAN"
                 " EACH SEARCH AROUND THE AIRCRAFT'S ASSIGNED SORTIE, NOT AN ASSUMED SECOND "
                 "PASS."
             ), "",
             (
                 "2. SATELLITE RADAR IMAGERY, SHIP REPORTS AND INTERCEPTED EMISSIONS HELP US "
                 "CUE THE SEARCH. THEY DO NOT PROVIDE UNBROKEN TRACKING. WEATHER CAN GROUND THE"
                 " AIRCRAFT NEEDED TO UPDATE THOSE REPORTS; CLOUD CAN ALSO PREVENT OPTICAL "
                 "CONFIRMATION. MARK THE AGE AND CONFIDENCE OF EVERY POSITION."
             ), "",
             (
                 "3. NO LAND-BASED FIGHTER COVER IS ALLOCATED TO THE DEEP-SOUTHERN OPERATIONS. "
                 "THE ESCORTS MUST PROVIDE LOCAL AIR DEFENCE. FIGHTER SUPPORT RESUMES IN THE "
                 "TASMAN WHERE THE ASSIGNED BASES CAN SUPPORT IT. PLAN YOUR FORCE ACCORDINGLY."
             ), "",
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
             "VICTOR, the boat that fired on the coaster, was hunted on Christmas Eve at "
             "57 South, and the task group's report on the hunt is in the "
             "ledger. New Zealand's Antarctic gateway at Christchurch was held on "
             "the twenty-eighth "
             "with a corvette trying to inspect a tanker in Pegasus Bay and a "
             "New Zealand Poseidon overhead telling it, in two languages, that "
             "it would not.",
             "The carrier Liaoning is here. It arrived south of the fishing fleet on the "
             "thirtieth with two frigates and a corvette, and its aircraft flew "
             "over the fleet on New Year's Eve for the cameras. The protection "
             "group now has an air wing and a reason to think the "
             "resupply season is negotiable.",
             "It is not. The January voyage sailed from Hobart on the thirty-first: Southern Endeavour "
             "with Casey's second lift, Derwent Spirit out of Bluff with a new "
             "plate and the same Chief, Coral Pioneer, and Aurora Trader and "
             "Davis Provider, chartered by the Antarctic Division because it "
             "will not be told to wait.",
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
             "corvettes, a Type 093B nuclear boat, one intelligence collector "
             "(NAN HAI 27) and a replenishment hull, with a Russian "
             "research-support detachment - a tender, two nuclear boats (an "
             "Akula and a Yasen), and very long-range aircraft with tanker "
             "support - operating alongside it under its own orders, not the "
             "group's.",
             (
                 "2. Recent radar-satellite detections and naval emissions place the formation "
                 "near the fishing fleet, south of the Casey route. Identification of the "
                 "carrier remains to be confirmed locally. Assessed intent: obstruct the final "
                 "resupply voyages while inviting the coalition to fire first. Positions are "
                 "intelligence cues, not continuous weapon-quality tracks."
             ),
             "3. Guidance to the force. Identify the carrier and the collector "
             "by class and name. Do not fire on anything that has not fired. "
             "AKADEMIK FERSMAN at the ice edge is a research vessel, whatever "
             "she was to the Akula in December. A trawler is a trawler.",
             (
                 "4. VICTOR's status depends on the Christmas Eve action report. A confirmed "
                 "loss removes that particular threat; otherwise an Akula remains possible near"
                 " the formation. A second Russian nuclear submarine, assessed as Yasen-class "
                 "and designated SIERRA-TWO, remains unlocated. Neither satellite imagery nor a"
                 " surface vessel's position establishes a submerged boat's location."
             )],
         note=(
             "Confirm the contacts. Observe the engagement restrictions. Bring back evidence.  "
             "- Cdre Mercer"
         )),

    # --- before SR11 Last Ship South --------------------------------------
    dict(file="03c_marsh_signal", before="Last Ship South", form="signal",
         title="From the voyage leader\\n9 January 2029",
         sub="A message from RSV Southern Endeavour",
         header=[("FROM:", "DR H. MARSH, VOYAGE LEADER, RSV SOUTHERN ENDEAVOUR"),
                 ("TO:", "CDRE MERCER, FOR THE ESCORT COMMANDER"),
                 ("DTG:", "090710Z JAN 29"), ("SUBJ:", "THE LAST VOYAGE SOUTH")],
         body=[
             "1. CASEY HAS ITS PEOPLE, ITS FOOD AND MOST OF ITS SPARES. IT DOES "
             "NOT HAVE ITS WINTER FUEL, BECAUSE THE FUEL COASTER'S DECEMBER VOYAGE "
             "ENDED AT BLUFF WITH A TORPEDO HOLE IN HER AND HER JANUARY ONE HAD TO "
             "BE FOUGHT THROUGH. WHAT SAILS ON THE "
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
             (
                 "Southern Endeavour has cleared the final escort handover for Casey. The ship "
                 "carries the remaining stores for winter; the season's final fuel position "
                 "will depend on the tanker and cargo-loss reports. The Division is reconciling"
                 " deliveries to Casey, Davis, Mawson and Macquarie before deciding what can "
                 "still sail."
             ),
             (
                 "The protection group has turned north. Triton surface-search reporting, "
                 "correlated with recent imagery, places the carrier, escorts, collector, "
                 "replenishment hull and Russian tender Akademik Fersman east of Tasmania, "
                 "moving towards the Tasman at a reported fourteen knots. That is the last "
                 "reported formation; the next patrol must update its course and membership. "
                 "The fishing fleet has been left to fish."
             ),
             "Nobody in Canberra or Wellington believes it is going home. The "
             "Tasman is where the two countries' ports, ferries, cables and "
             "trade are, and a group that wanted to make the Antarctic route "
             "unusable and could not is heading for the water between Sydney "
             "and Auckland.",
             "The task group's last job in the south is to shadow it out and "
             "put a name on every hull in the group: the carrier, the "
             "replenishment ship, the collector. Its first job in the Tasman "
             "will be to meet it."]),

    # --- chapter card: before TS01 Home Waters ----------------------------
    dict(file="05_chapter", before="Home Waters",
         title="Tasman Shield\\n21 January 2029",
         sub="The approaches Australia and New Zealand share",
         dateline="21 JANUARY 2029  |  MARITIME BORDER COMMAND, SYDNEY",
         headline="TASMAN SHIELD",
         body=[
             "The task group has had its days alongside at Sydney, and the "
             "ledger says what it sails with: the hulls that came out of the "
             "south, the aircraft that came back, and the magazines Sydney's "
             "dockyard refilled.",
             "The group that came north has its carrier and its flagship, a "
             "Type 052D destroyer, in the Tasman; a tender and a diesel boat "
             "working the New Zealand side; its contractor, Austral Meridian "
             "Services, with coasters in every port; and an aim "
             "that has not changed since October: make the approaches unusable "
             "long enough that a \"joint compliance\" settlement looks like "
             "peace.",
             "New Zealand's contribution is No. 5 Squadron's Poseidons, the "
             "airfields at Ohakea, Whenuapai, "
             "Invercargill and Christchurch, and Commander Brand's plain "
             "signals about where its ships are not. Australia's is the task "
             "group, Williamtown's fighters from the first of February, and the "
             "Poseidons at Edinburgh.",
             "Fiordland first: the tourist traffic hides a tender. Then Cook "
             "Strait, then the Tasman crossing. New Zealand's relief detachment "
             "for the Antarctic gateway flies the Tasman air bridge on the "
             "eleventh of February, and a carrier is between it and Sydney."]),

    # --- before TS03 Chatham Watch ----------------------------------------
    dict(file="05b_rewi_cable", before="Chatham Watch", form="signal",
         title="Two air forces\\n27 January 2029",
         sub="Signal from No. 5 Squadron RNZAF",
         header=[("FROM:", "SQNLDR T. REWI, NO. 5 SQN RNZAF, OHAKEA"),
                 ("TO:", "COMAUSMARTG"), ("DTG:", "270300Z JAN 29"),
                 ("PREC:", "IMMEDIATE"), ("SUBJ:", "WEST OF THE CHATHAMS - THE RENDEZVOUS")],
         body=[
             (
                 "1. TANGO IS THE DIESEL-ELECTRIC SUBMARINE REPORTED ON THE COOK STRAIT CABLE "
                 "ROUTE. INTERCEPTS INDICATE A PLANNED STORES TRANSFER WITH AUSTRAL COMPLIANCE."
                 " THIS IS A SPECIFIC RENDEZVOUS, NOT A REQUIREMENT FOR EVERY DIESEL BOAT. THE "
                 "TENDER SAILED EAST ON THE TWENTY-SIXTH AND STOPPED TRANSMITTING AIS."
             ), "",
             (
                 "2. A SATELLITE RADAR DETECTION AND THE TENDER'S LAST REPORTED COURSE DEFINE "
                 "THE SEARCH AREA WEST OF THE CHATHAMS. THEY DO NOT CONFIRM A SUBMARINE "
                 "ALONGSIDE. THE POSEIDONS ARE TO REACQUIRE THE TENDER AND CHECK FOR A SURFACED"
                 " BOAT BEFORE REPORTING A RENDEZVOUS."
             ), "",
             "3. YOUR POSEIDON AND MINE, ONE SEARCH PLAN, TWO AIR FORCES, OUT OF "
             "OHAKEA. WELLINGTON HAS AUTHORISED WEAPONS ON THE BOAT. IT HAS NOT "
             "AUTHORISED WEAPONS ON THE COASTER, WHICH IS A MERCHANT HULL WITH A "
             "CREW WHO WERE TOLD THEY WERE DELIVERING FUEL.", "",
             (
                 "4. KEEP THE SEARCH WEST OF 180 DEGREES; THE CHATHAM ISLANDS LIE EAST OF THAT "
                 "MERIDIAN. REPORT OBSERVATION TIMES IN UTC, WITH THE SOURCE AND CONFIDENCE OF "
                 "EACH FIX. THE CIVIL DATE LINE BENDS AROUND THE ISLANDS; DO NOT USE THE "
                 "MERIDIAN AS A DATE BOUNDARY."
             ), "",
             "REWI"]),

    # --- before TS04 Tasman Crossing --------------------------------------
    dict(file="06_sitrep", before="Tasman Crossing",
         title="The New Zealand side\\n31 January 2029",
         sub="Fiordland, Cook Strait and a rendezvous two air forces watched",
         dateline="31 JANUARY 2029  |  MARITIME BORDER COMMAND, SYDNEY",
         headline="THE STRAIT IS OPEN",
         body=[
             "The tender Austral Compliance was found among the Milford cruise "
             "ships on the twenty-second. TANGO, the diesel boat she served, was "
             "found on the Cook Strait cable route on the twenty-fifth, among the "
             "ferries, and the ferries ran. The two of them met east of New "
             "Zealand on the twenty-eighth, and two air forces were watching.",
             (
                 "Wellington has published the Poseidons' recordings of the 28 January "
                 "rendezvous. Austral Meridian Services has announced a review of its "
                 "subcontractors. The group has not commented. Patrol imagery places its "
                 "carrier in the central Tasman, while Wedgetail and partner air reports record"
                 " carrier aircraft over the Sydney-Auckland airway during the past four days. "
                 "The latest surface and air observations still need to be correlated."
             ),
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
             "The Tasman crossing held on the first. Farncomb fought ROMEO, the "
             "group's Type 093B, under the cable corridor on the fourth and her "
             "report is in the ledger. Bass Strait's rigs are standing, its "
             "ferries ran, and Southern Compliance, an Austral Meridian merchant "
             "that radiated a frigate's radar all morning, was told what she was "
             "on channel 16 and did not answer. "
             "The relief detachment crossed the air bridge on the eleventh "
             "under Williamtown's fighters, with the carrier's coming for it.",
             "The Bight was searched for four days for SIERRA-TWO, the Russian "
             "detachment's Yasen, and the oiler Boris Chilikin that keeps her at sea. What was found "
             "there is in the ledger too.",
             "The group's carrier, its flagship and what is left of its escorts "
             "are south of the Portland approaches, and the southern convoy - "
             "Adelaide's fuel, Melbourne's cargo, and Coral Pioneer, because "
             "she is always there - sails tomorrow through them.",
             "It is a fleet action, and it is the group's last full-strength "
             "one. The task group sails with everything it owns, rearmed at "
             "Adelaide, with Edinburgh's Poseidons and fighters "
             "overhead. After it, both sides will be counting."]),

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
             "The Australians are fewer than they were in December. They are "
             "also not alone now: they and the New Zealanders fly out of each "
             "other's airfields. "
             "Their escorts do not chase. They protect the movement and let us "
             "come to them, and the last time we came to them, off Portland, we came back "
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
             ("0930", "Convoy conference aboard the escort flagship. Four hulls for "
                      "Auckland with the relief cargo. One group out there is "
                      "complying with the withdrawal and one has not said. Told: "
                      "\"Sail as planned.\" Same words as the night before "
                      "the Darwin passage in November."),
             ("1015", (
                 "Chief Engineer reports No. 2 bearing at 66 degrees C. Eleven knots "
                 "acceptable. Convoy speed set to 11 kn."
             )),
             ("1100", "Crew briefed. The two who asked in November whether "
                      "Meridian's Escort Seven, which ordered us to heave to on "
                      "18 October, was out there asked again, this time about "
                      "the trawler that held the Wilkins airlink's crew in "
                      "December. I said I did not know. That is true."),
             ("1630", "Sydney Heads astern. Escorts on both beams. A New "
                      "Zealand aircraft overhead going the same way we are. "
                      "Three months ago this ship was chartered for a fortnight's "
                      "run to Macquarie Island.")],
         note=(
             "For whoever reads this afterwards: the escorts have brought us through two seas, "
             "a strait, Buckles Bay and a summer. There are fewer familiar voices on the radio "
             "now. On the second we ask them to bring the Auckland convoy through once more.  -"
             " L.S."
         )),

    # --- epilogue ----------------------------------------------------------
    dict(file="24_closing", title="Southern Cross\\n2 March 2029",
         sub="The approaches held, and what it cost",
         dateline="2 MARCH 2029  |  MARITIME BORDER COMMAND, SYDNEY",
         headline="THE APPROACHES ARE OURS",
         body=[
             "The relief convoy made Auckland. The group that came south in "
             "October to make the Antarctic route unusable, and came north in "
             "January to do the same to the Tasman, has turned for home with "
             "fewer ships than it arrived with, and the two countries that held "
             "the line against it are counting what is left, at Sydney and at "
             "Auckland.",
             (
                 "The final relief convoy is through. The resupply programme is accounting for "
                 "winter stocks, port authorities are keeping the ferry routes open, and the "
                 "repaired cable is back in service. There are losses to account for as well as"
                 " passages completed. The compliance contractor has closed its Hobart office."
             ),
             (
                 "The task group's report lists the ships and aircraft that returned, the crews"
                 " lost and the ammunition spent. Those costs belong beside the result: "
                 "Australia and New Zealand can continue to use their ports and sea routes "
                 "without accepting the protection group's inspections."
             ),
             "Master Santos's entry for the arrival, which she has allowed to "
             "be quoted, reads: \"Alongside Auckland. All hands. Same escort.\"",
             "Stand down the watch."]),
]
