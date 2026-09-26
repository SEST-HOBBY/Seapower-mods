"""The story screens: the tasking that opens the campaign, the group
commander's own signals, the southern orders and the signal that closes it.
The builder takes EVENTS[0] as the prologue and EVENTS[-1] as the epilogue
and hangs the rest before the mission each names in `before`.

Every page is a signal, and every one is from this side of the table: the
note under it is the group commander's, not a coalition analyst's, so each
sets `note_label`. The two signals the coalition intercepted - Southern
Watch's 05b on 22 November and Southern Reach's 07b on 25 February - are
here as sent. Every sentence the coalition decrypted is kept word for word;
what the intercept missed at either end is the only text added. No page
says how Fujian's Shadow ended, or what happened on 26 February: those are
the coalition's to tell.
"""

EVENTS = [
    # --- prologue: the tasking, 3 November --------------------------------
    dict(file="00_tasking", form="signal",
         title="Protection and Evacuation\\n3 November 2028",
         sub="Tasking signal from Fleet headquarters",
         header=[("FROM:", "FLEET HEADQUARTERS"),
                 ("TO:", "COMMANDER, CARRIER TASK GROUP"),
                 ("DTG:", "022200Z NOV 28"), ("PREC:", "IMMEDIATE"),
                 ("SUBJ:", "PROTECTION AND EVACUATION - TASKING")],
         body=[
             "1. THE GROUP WILL ENTER THE MOLUCCA SEA AND TAKE STATION IN THE "
             "BANDA APPROACHES TO PROTECT CHINESE NATIONALS AND PROPERTY IN THE "
             "REGION, AND TO EVACUATE THEM IF ASKED.", "",
             "2. THE COALITION ESCORT FORCE IS TO BE ASKED TO SUSPEND ITS "
             "PATROLS IN THE APPROACHES. IT WILL DECLINE. YESTERDAY A DESTROYER "
             "OF THE NORTHERN ELEMENT FIRED ON A PROTECTED CONVOY AND WAS "
             "ANSWERED. THAT ELEMENT IS NOT UNDER YOUR COMMAND AND ITS ACTION IS "
             "UNDER REVIEW. THE OTHER SIDE WILL NOT DRAW THAT DISTINCTION.", "",
             "3. THE GROUP IS NOT AT WAR WITH ANY STATE. IT WILL NOT FIRE FIRST.", "",
             "4. THE GROUP STAYS UNTIL THERE IS A SETTLEMENT. FUEL AND "
             "ORDNANCE ARE WHAT IT SAILS WITH. PLAN ACCORDINGLY.", "",
             "ACKNOWLEDGE."],
         note_label="COMMANDER'S NOTE",
         note="Paragraph 3 is the order. Paragraph 2 is the reason it will be hard."),

    # --- before RL04: the signal the coalition intercepted, as sent --------
    dict(file="01_guidance", before="The Order to Withdraw",
         form="signal", strap="OUTGOING",
         title="Guidance requested\\n22 November 2028",
         sub="The group's signal as sent, the reply, and the order of the 26th",
         header=[("FROM:", "COMMANDER, CARRIER TASK GROUP"),
                 ("TO:", "FLEET HEADQUARTERS"), ("DTG:", "220110Z NOV 28"),
                 ("PREC:", "IMMEDIATE"), ("SUBJ:", "GROUP STATE - GUIDANCE REQUESTED")],
         body=[
             "Group state follows. The escorts are worn and the air wing has "
             "flown for nineteen days. I am not asking to withdraw. I am stating "
             "what the group can do. It can close the corridor for the period of "
             "the ceasefire talks. It cannot hold it against a determined passage "
             "and preserve itself, and I will not be the officer who lost the "
             "carrier to prove a point that a signature would have proved.", "",
             "The coalition force is smaller than it was. It is also better at "
             "this than it was. Their escorts do not chase. Their aircraft do not "
             "come out to fight us where we are strong. They protect the "
             "transports and they let us come to them, and every time we do we "
             "spend fuel we cannot replace here.", "",
             "Request guidance on whether the closure is to be enforced against "
             "the passage expected on the twenty-third. If so I will enforce it. "
             "If the settlement is to be signed regardless, I request the order "
             "to withdraw before I am given the order to withdraw damaged.", "",
             "REPLY 220540Z: ENFORCE THE CLOSURE ON THE TWENTY-THIRD.", "",
             "ORDER 261100Z: CEASEFIRE TAKES EFFECT 0000 ON 27 NOVEMBER. "
             "WITHDRAW NORTH-WEST. ACKNOWLEDGE."],
         note_label="COMMANDER'S NOTE",
         note="Acknowledged at 2304 local on the 26th, fifty-six minutes before "
              "it took effect. The twenty-third is in the group's report, not on "
              "this page."),

    # --- chapter card: before RL05, the southern orders --------------------
    dict(file="02_southern_orders", before="Under the Convergence", form="signal",
         title="New orders\\n22 December 2028",
         sub="Signal from Fleet headquarters, received at sea: the southern tasking",
         header=[("FROM:", "FLEET HEADQUARTERS"),
                 ("TO:", "COMMANDER, CARRIER TASK GROUP"),
                 ("DTG:", "220300Z DEC 28"), ("PREC:", "IMMEDIATE"),
                 ("SUBJ:", "SOUTHERN TASKING")],
         body=[
             "1. ON ARRIVAL YOU ASSUME COMMAND OF THE SOUTHERN OCEAN FISHERIES "
             "AND RESEARCH PROTECTION GROUP. ITS DESTROYER, FRIGATE, CORVETTES AND "
             "RESEARCH TRAWLER COME UNDER YOUR ORDERS. THE DESTROYER IS YOUR "
             "FLAGSHIP. SHE IS NOT TO BE LOST.", "",
             "2. LIAONING, TWO FRIGATES AND A CORVETTE CONTINUE SOUTH-EAST. THE "
             "SUBMARINE GOES AHEAD OF THEM AND IS NOT TO BE REPORTED ON ANY NET "
             "UNTIL THE CARRIER IS ON STATION.", "",
             "3. THE CONTRACTOR IN THE SOUTH IS AUSTRAL MERIDIAN SERVICES. YOU "
             "HAVE MET ITS PARENT.", "",
             "4. A COASTER WAS TORPEDOED SOUTH OF THE AUCKLAND ISLANDS ON THE "
             "TWENTY-FIRST. NO CHINESE UNIT FIRED. THE RUSSIAN DETACHMENT IN THE "
             "SOUTH WORKS UNDER ITS OWN ARRANGEMENT, NOT THIS HEADQUARTERS'.", "",
             "5. THE GROUP IS NOT AT WAR WITH ANY STATE. IT WILL NOT FIRE FIRST.", "",
             "ACKNOWLEDGE."],
         note_label="COMMANDER'S NOTE",
         note="Received five days out of the Java Sea. Paragraph 5 is "
              "November's paragraph 3, word for word. This time paragraph 3 is "
              "the reason it will be hard."),

    # --- epilogue: the signal of 25 February, as sent ----------------------
    dict(file="03_last_signal", form="signal", strap="OUTGOING",
         title="The last signal\\n25 February 2029",
         sub="The protection group commander to Fleet headquarters, as sent",
         header=[("FROM:", "COMMANDER, PROTECTION GROUP"),
                 ("TO:", "FLEET HEADQUARTERS"), ("DTG:", "250140Z FEB 29"),
                 ("PREC:", "IMMEDIATE"), ("SUBJ:", "THE MOVEMENT OF THE 26TH - GUIDANCE REQUESTED")],
         body=[
             "Estimate of the group for the headquarters' decision. The group "
             "has been at sea since October and in contact since December. I "
             "have a carrier with an air wing that has flown seventy days, a "
             "flagship I am ordered not to lose, and escorts that have been where "
             "the other side's aircraft could reach them for a month. The "
             "approaches can be closed for a week. They cannot be held.", "",
             "The Australians are fewer than they were in December. They are "
             "also not alone now: they and the New Zealanders fly out of each "
             "other's airfields. Their escorts do not chase. They protect the "
             "movement and let us come to them, and the last time we came to "
             "them, off Portland, we came back with fewer ships.", "",
             "I request guidance on whether the closure is to be enforced "
             "against the movement expected on the twenty-sixth, and on which of "
             "the two elements detached to the ports is to rejoin. If both are "
             "held where they are, I will enforce it with what I have. I would "
             "rather be told not to."],
         note_label="FILE NOTE",
         note="The reply is not on this page, and what followed on the "
              "twenty-sixth is the other side's account."),
]
