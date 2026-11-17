"""The story screens: the tasking that opens the campaign, the pages between
the missions and the signal that closes it. The builder takes EVENTS[0] as
the prologue and EVENTS[-1] as the epilogue and hangs the rest before the
mission each names in `before`.

The pages are the task group's own traffic and the press around it. The
Meridian Maritime Group, every named merchant, tanker and trawler, the
named Meridian ships and the commander are fiction. Task Force 88 is the
Pakistan Navy's real Gwadar task force (formed in December 2016) and the
Regional Maritime Security Patrol its real patrol programme (2018); their
2028 operations here are fiction. No Indian or Iranian state unit and no
insurgency ashore is in the story: the opponent is Meridian alone.

The intelligence summary carries the fleet's own marking, not the
coalition's RELEASABLE TO COALITION PARTNERS: the task group has no partner
navy, as Red Line's carries its headquarters' own.
"""

EVENTS = [
    # --- prologue: the tasking, 22 October --------------------------------
    dict(file="00_tasking", form="signal",
         title="The Fuel Road\\n22 October 2028",
         sub="Tasking signal from Commander Pakistan Fleet",
         header=[("FROM:", "COMMANDER PAKISTAN FLEET, KARACHI"),
                 ("TO:", "COMMANDER TASK FORCE 88"),
                 ("DTG:", "220500Z OCT 28"), ("PREC:", "IMMEDIATE"),
                 ("SUBJ:", "WAR-RISK NOTICE - GULF TO KARACHI TANKER ROUTE")],
         body=[
             "1. LLOYD'S JOINT WAR COMMITTEE HAS LISTED THE NORTH ARABIAN SEA. "
             "INSURERS ARE DECLINING VOYAGES FROM THE GULF TO KARACHI AND GWADAR. "
             "NO COALITION ESCORTS ARE AVAILABLE: THE US FIFTH FLEET'S SHIPS HAVE "
             "SAILED EAST.", "",
             "2. THE MERIDIAN MARITIME GROUP IS OFFERING TANKERS ON THE ROUTE ITS "
             "OWN ESCORTS AND INSPECTIONS. TWO MASTERS WHO REFUSED REPORT ARMED "
             "TRAWLERS KEEPING COMPANY AND ORDERS TO DIVERT.", "",
             "3. TASK FORCE 88 WILL KEEP THE FUEL ROAD OPEN: THE KARACHI "
             "APPROACHES, THE GWADAR ANCHORAGE AND PORT QASIM.", "",
             "4. NO REPLENISHMENT SHIP IS ALLOCATED. SHIPS WILL REARM AT KARACHI "
             "BETWEEN TASKINGS.", "",
             "ACKNOWLEDGE."],
         note_label="COMMANDER'S NOTE",
         note="Meridian is a company with guns, not a navy. Every one of its boats is "
              "first a contact to be identified among the dhows."),

    # --- before MK02: the press, Gwadar -----------------------------------
    dict(file="01_gwadar", before="Gwadar Roads",
         title="The roads off Gwadar\\n30 October 2028",
         sub="Tankers wait for a pilot, merchants for a berth",
         dateline="30 OCTOBER 2028  |  GWADAR",
         headline="TANKERS WAIT OFF GWADAR AS INSURERS STAY AWAY",
         body=[
             "Two tankers carrying fuel for Gwadar have been at anchor off the port for "
             "three days, waiting for a pilot. Port officials say the "
             "anchorage now holds more ships than it has room for, and that two of "
             "them do not answer on the port's working channel.",
             "Fishermen from Pishukan and Jiwani say armed trawlers have been working "
             "the coast at night without nets out. A Navy spokesman said a frigate "
             "would be off Gwadar by Friday, and that the Air Force had been asked "
             "for aircraft.",
             "The Meridian Maritime Group, which says it offers security to shipping, "
             "did not answer questions about its vessels."]),

    # --- before MK03: the intsum -------------------------------------------
    dict(file="02_mothership", before="Hangor", form="intsum",
         title="The mothership\\n5 November 2028",
         sub="Fleet intelligence summary",
         org="Commander Pakistan Fleet, Karachi", ref="INTSUM 28-061",
         date="5 November 2028", subject="Meridian's tender off the Makran coast",
         marking="SECRET  //  PAKISTAN NAVY ONLY",
         body=[
             "1. The armed trawlers that attacked the Gwadar anchorage did not come "
             "from a port. They were fuelled and armed at sea.",
             "2. A Meridian-chartered merchant, MV MERIDIAN SENTINEL, has been seen "
             "three times south of Gwadar, each time at night and each time with "
             "trawlers alongside. She mounts two heavy machine guns, one firing to each beam.",
             "3. PNS HANGOR is on passage in the area. She will be detached to trail "
             "the merchant to her next rendezvous and classify her, unseen.",
             "4. Assess that Meridian will try once more, against the Port Qasim "
             "convoy, and that SENTINEL will be with its boats when it does."],
         note="A submarine on a trail fires nothing. What she brings back is the "
              "mothership's signature, for the convoy."),

    # --- before MK04: the convoy order --------------------------------------
    dict(file="03_convoy", before="Port Qasim", form="signal",
         title="The last convoy\\n13 November 2028",
         sub="Signal from Commander Pakistan Fleet",
         header=[("FROM:", "COMMANDER PAKISTAN FLEET, KARACHI"),
                 ("TO:", "COMMANDER TASK FORCE 88"),
                 ("DTG:", "132100Z NOV 28"), ("PREC:", "FLASH"),
                 ("SUBJ:", "PORT QASIM CONVOY")],
         body=[
             "1. THREE TANKERS WITH THE MONTH'S FUEL FOR PORT QASIM ARE AT THE "
             "KARACHI OUTER ANCHORAGE. THEY WEIGH AT 0300 FOR THE DEEP-WATER ROUTE.", "",
             "2. MERIDIAN SENTINEL AND AT LEAST THREE ARMED BOATS ARE OFF THE INDUS "
             "MOUTHS.", "",
             "3. BRING THE CONVOY IN. STOP SENTINEL: SINK HER, OR CLOSE HER UNTIL "
             "SHE HEAVES TO. A SHIP THAT HAS HOVE TO IS NOT TO BE FIRED ON.", "",
             "ACKNOWLEDGE."],
         note_label="COMMANDER'S NOTE",
         note="If Sentinel stops, Meridian's boats have nowhere to fuel. That is the "
              "end of this, not the convoy."),

    # --- epilogue: Meridian withdraws, 17 November --------------------------
    dict(file="99_withdrawal", form="signal",
         title="The road is open\\n17 November 2028",
         sub="Signal from Commander Pakistan Fleet",
         header=[("FROM:", "COMMANDER PAKISTAN FLEET, KARACHI"),
                 ("TO:", "COMMANDER TASK FORCE 88"),
                 ("DTG:", "170600Z NOV 28"), ("PREC:", "PRIORITY"),
                 ("SUBJ:", "MERIDIAN WITHDRAWAL")],
         body=[
             "1. THE MERIDIAN MARITIME GROUP HAS ANNOUNCED THAT IT IS 'SUSPENDING "
             "ITS ESCORT SERVICE' IN THE NORTH ARABIAN SEA. NO ARMED TRAWLER HAS "
             "BEEN SEEN SINCE THE FIFTEENTH.", "",
             "2. TWO INSURERS HAVE RESUMED COVER FOR KARACHI AND GWADAR.", "",
             "3. TASK FORCE 88 WILL RESUME REGIONAL MARITIME SECURITY PATROLS. "
             "REPORT THE STATE OF THE SHIPS BY 1200.", "",
             "WELL DONE."],
         note_label="COMMANDER'S NOTE",
         note="The fuel came in. What we did not have - an oiler, an offshore patrol "
              "vessel, a long-range patrol aircraft - goes in the report too."),
]
