"""The story screens: the tasking that opens the campaign, the pages between
the missions and the signal that closes it. The builder takes EVENTS[0] as
the prologue and EVENTS[-1] as the epilogue and hangs the rest before the
mission each names in `before`.

The pages are the task group's own traffic and the press around it. The
Meridian network, the named ships of the charter convoys, the outposts'
figures and every officer quoted are fiction; the real places and the real
ships of the Philippine and Thai navies are used as they are.
"""

EVENTS = [
    # --- prologue: the tasking, 10 October --------------------------------
    dict(file="00_tasking", form="signal",
         title="The Island Road\\n10 October 2028",
         sub="Tasking signal from Naval Forces West",
         header=[("FROM:", "NAVAL FORCES WEST, PUERTO PRINCESA"),
                 ("TO:", "COMMANDER, SULU SEA TASK GROUP"),
                 ("DTG:", "100600Z OCT 28"), ("PREC:", "IMMEDIATE"),
                 ("SUBJ:", "SULU SEA TASK GROUP - TASKING")],
         body=[
             "1. THE UNITED STATES SEVENTH FLEET HAS SAILED NORTH. NO US "
             "ESCORTS WILL BE AVAILABLE SOUTH OF LUZON FOR THE PERIOD.", "",
             "2. THE MERIDIAN MARITIME GROUP IS OPERATING ARMED CRAFT FROM "
             "CAGAYANCILLO AND THE SULU COAST AND IS SUPPLYING WEAPONS ASHORE ON "
             "JOLO. CHINESE COAST GUARD AND MILITIA VESSELS ARE BLOCKING THE "
             "RESUPPLY OF AYUNGIN SHOAL.", "",
             "3. THE TASK GROUP WILL KEEP THE ISLAND SUPPLY ROAD OPEN: PUERTO "
             "PRINCESA - BALABAC - JOLO - AYUNGIN. THE ROYAL THAI NAVY WILL "
             "DETACH A FRIGATE AND AN OILER UNDER TASK GROUP COMMAND.", "",
             "4. THERE IS NO MUNITIONS RESERVE SOUTH OF MANILA. WHAT THE GROUP "
             "FIRES IS REPLACED ONLY BY ITS OWN SUPPLY SHIPS. PLAN ACCORDINGLY.",
             "", "ACKNOWLEDGE."],
         note_label="COMMANDER'S NOTE",
         note="Paragraph 4 is the one that matters. Every round fired has to come "
              "back from a ship we bought and kept afloat."),

    # --- before SL02: the press, Jolo -------------------------------------
    dict(file="01_jolo", before="Fire Mission Jolo",
         title="The ridge above Patikul\\n18 October 2028",
         sub="The Marines on Jolo ask for naval gunfire",
         dateline="18 OCTOBER 2028  |  ZAMBOANGA CITY",
         headline="MARINES PINNED ON JOLO COAST ROAD",
         body=[
             "A Marine battalion that landed east of Jolo town on Monday has been "
             "held for two days below a ridge above Patikul, where fighters armed "
             "by the Meridian network have set up drone launch rails and gun "
             "trucks.",
             "Two Air Force helicopters were driven off yesterday by fire from an "
             "air-defence vehicle that the armed forces say came ashore from a "
             "Meridian coaster in September. The battalion has asked for naval "
             "gunfire.",
             "The Navy's task group in the Sulu Sea has confirmed it will provide "
             "it. A Navy spokesman would not say how many rounds the ships carry, "
             "or when they will next be resupplied."]),

    # --- before SL04: the logistics intsum --------------------------------
    dict(file="02_munitions", before="Service at Sea", form="intsum",
         title="Munitions state\\n31 October 2028",
         sub="Naval Forces West logistics summary",
         org="Naval Forces West, Puerto Princesa", ref="LOGSUM 28-044",
         date="31 October 2028", subject="Task group munitions and the Subic charter",
         body=[
             "1. The task group has fired at Jolo and has not been resupplied. "
             "There is no naval munitions reserve south of Manila.",
             "2. MV SULU PROVIDER, a C8 barge carrier on charter to Military "
             "Sealift Command, has loaded 76 mm, MICA, Harpoon and torpedoes at "
             "Subic from stocks the Seventh Fleet left behind. She will be at a "
             "rendezvous east of Cagayancillo at 0700 on 2 November.",
             "3. She cannot come alongside a pier the group can reach, and she "
             "will not wait. Ships take stores from her at sea, one at a time, "
             "at eight knots or less.",
             "4. Meridian has been asking about her in Subic. Assess that the "
             "rendezvous is known."],
         note="There is no second charter. If she is lost, the group's own supply ships are"
              " all the ammunition it has."),

    # --- before SL07: the closure order ----------------------------------
    dict(file="03_closure", before="Balabac Strait", form="signal",
         title="Closure\\n23 November 2028",
         sub="Flash signal from Naval Forces West",
         header=[("FROM:", "NAVAL FORCES WEST, PUERTO PRINCESA"),
                 ("TO:", "COMMANDER, SULU SEA TASK GROUP"),
                 ("DTG:", "222000Z NOV 28"), ("PREC:", "FLASH"),
                 ("SUBJ:", "BALABAC STRAIT")],
         body=[
             "1. BEIJING WILL ANNOUNCE AT 0300 LOCAL THE CLOSURE OF THE SOUTHERN "
             "PASSAGES TO COALITION SHIPPING. THE SOUTHERN SURFACE GROUP IS "
             "SEVENTY MILES WEST OF THE BALABAC STRAIT, STEERING EAST.", "",
             "2. THE CONVOY FOR BALABAC AND THE SULU IS AT THE ANCHORAGE EAST OF "
             "THE STRAIT.", "",
             "3. THE TASK GROUP WILL HOLD THE STRAIT. WEAPONS FREE.", "",
             "4. THERE WILL BE NO RESUPPLY BEFORE THE ACTION.", "",
             "ACKNOWLEDGE."],
         note_label="COMMANDER'S NOTE",
         note="Paragraph 4 we knew. This is what the supply ships were kept for."),

    # --- epilogue: the ceasefire, 27 November -----------------------------
    dict(file="99_ceasefire", form="signal",
         title="Ceasefire\\n27 November 2028",
         sub="Signal from Naval Forces West",
         header=[("FROM:", "NAVAL FORCES WEST, PUERTO PRINCESA"),
                 ("TO:", "COMMANDER, SULU SEA TASK GROUP"),
                 ("DTG:", "270100Z NOV 28"), ("PREC:", "FLASH"),
                 ("SUBJ:", "CEASEFIRE")],
         body=[
             "1. A CEASEFIRE TOOK EFFECT AT 0000 TODAY.", "",
             "2. THE ISLAND SUPPLY ROAD REMAINS OPEN. THE BALABAC AND AYUNGIN "
             "GARRISONS HAVE BEEN SUPPLIED THROUGHOUT.", "",
             "3. THE TASK GROUP WILL REMAIN AT SEA UNTIL RELIEVED. REPORT "
             "MUNITIONS STATE AND THE STATE OF THE SUPPLY SHIPS BY 0600.", "",
             "WELL DONE."],
         note_label="COMMANDER'S NOTE",
         note="Munitions state: what the supply ships had left, and what we "
              "chose not to fire."),
]
