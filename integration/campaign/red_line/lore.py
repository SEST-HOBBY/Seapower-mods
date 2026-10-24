"""The story screens: the tasking that opens the campaign, the group
commander's own signals, the southern orders and the signal that closes it.
The builder takes EVENTS[0] as the prologue and EVENTS[-1] as the epilogue
and hangs the rest before the mission each names in `before`.

Every page is from this side of the table: the note under a signal or a log
is the group commander's, not a coalition analyst's, so each sets
`note_label`, the log says who kept it (`log_heading`, `master_label`), and
the intelligence summary carries the headquarters' own marking, not the
coalition's RELEASABLE TO COALITION PARTNERS. The two signals the coalition
intercepted - Southern Watch's 05b on 22 November and Southern Reach's 07b
on 25 February - are here as sent. Every sentence the coalition decrypted is
kept word for word; what the intercept missed at either end is the only text
added. No page says how Fujian's Shadow ended, or what happened on 26
February: those are the coalition's to tell.

The four pages of 20 Oct 2026 (campaign-upgrade-plan.md section 4.2, step
RL-1) stand before the side operations, and the campaign shows them whether
or not the player flies those: none of them says how one ended. A role signs
each, never a name, and there is no press page - this side's newspapers
would be real state outlets.
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

    # --- before RLO1: the request of 6 November, as tasked ----------------
    # Southern Watch's 12 November summary has the group "demanded the
    # coalition patrols suspend"; this is the demand, in the tasking's own
    # terms. The answer is the tasking's paragraph 2, and not on this page.
    dict(file="00a_the_request", before="Datum", form="signal", strap="OUTGOING",
         title="The request\\n6 November 2028",
         sub="The group's signal to the coalition escort force, as tasked",
         header=[("FROM:", "COMMANDER, CARRIER TASK GROUP"),
                 ("TO:", "COMMANDER, COALITION ESCORT FORCE"),
                 ("DTG:", "060100Z NOV 28"), ("PREC:", "PRIORITY"),
                 ("SUBJ:", "PATROLS IN THE BANDA APPROACHES")],
         body=[
             "1. A CHINESE CARRIER TASK GROUP IS ON STATION IN THE BANDA APPROACHES TO "
             "PROTECT CHINESE NATIONALS AND PROPERTY IN THE REGION, AND TO EVACUATE THEM IF "
             "ASKED.", "",
             "2. THE GROUP REQUESTS THAT THE COALITION ESCORT FORCE SUSPEND ITS PATROLS IN THE "
             "APPROACHES WHILE THE GROUP IS ON STATION, SO THAT NEITHER FORCE MISTAKES THE "
             "OTHER'S PURPOSE.", "",
             "3. THE GROUP IS NOT AT WAR WITH ANY STATE. IT WILL NOT FIRE FIRST.", "",
             "4. THE GROUP WILL ANSWER ON THIS CIRCUIT AND ON CHANNEL 16 AT ANY HOUR."],
         note_label="COMMANDER'S NOTE",
         note="Sent as the tasking ordered, on the liaison circuit and in plain language on "
              "channel 16. The tasking says what the answer will be. Paragraph 3 is the "
              "part of this one I meant."),

    # --- before RLO1: the morning after the auxiliary was hit ---------------
    # The night Routes They Can See calls "two nights ago" and Return
    # Passage "eleven days ago". Nobody claims the boat, here or anywhere.
    dict(file="00b_unclaimed", before="Datum", form="intsum",
         title="The unclaimed boat\\n11 November 2028",
         sub="Fleet headquarters intelligence summary, the morning after",
         org="Fleet headquarters, intelligence", ref="INTSUM 11-03",
         date="11 November 2028",
         subject="Torpedo attack on the Russian detachment's auxiliary",
         marking="SECRET  //  CARRIER TASK GROUP ONLY",
         body=[
             "1. At 2340 local on 10 November the Russian detachment's auxiliary was hit "
             "forward by one torpedo in the northern approaches to Biak. She is afloat and "
             "making about six knots. The Russian detachment works under its own "
             "arrangement, not this headquarters'; her recovery is its business.",
             "2. No Chinese unit fired. No state has claimed the attack, and none is expected "
             "to. The boat is assessed as nuclear from the weapon and the approach, not from "
             "any contact. She is designated GOLF.",
             "3. The enclave's fuel run goes in by the northern roads on the night of the "
             "12th, through the same water.",
             "4. Guidance to the group. Put a class on GOLF: the enclave detachment's Y-9 is "
             "available from first light. A class is not a claim, and it is not authority to "
             "attack. Whoever she belongs to, the group does not fire first on her."],
         note="Paragraph 4 is the order. Paragraph 3 is why it is this week's."),

    # --- before RLO2: the escorts Common Sea sails with ---------------------
    # The evening of Viper Zero: Langgur's F-2As went for a PLAN 054A and
    # 056A south of Seram that morning. Paragraph 3 says so as a premise -
    # the northern element's ships, not this group's - and not how it ended.
    dict(file="00c_ships_from_the_north", before="The Ships from the North",
         form="signal",
         title="Ships from the north\\n17 November 2028",
         sub="Signal from Fleet headquarters: the Japanese escorts",
         header=[("FROM:", "FLEET HEADQUARTERS"),
                 ("TO:", "COMMANDER, CARRIER TASK GROUP"),
                 ("DTG:", "171400Z NOV 28"), ("PREC:", "PRIORITY"),
                 ("SUBJ:", "JAPANESE ESCORTS SOUTHBOUND - IDENTIFICATION")],
         body=[
             "1. TWO JAPANESE ESCORTS PASSED THE TALAUD ISLANDS SOUTHBOUND ON THE 16TH. THEY "
             "ARE ASSESSED TO JOIN THE CONVOY FORMING WEST OF THE KAI ISLANDS, WHICH IS "
             "EXPECTED TO SAIL ON THE 20TH.", "",
             "2. HEADQUARTERS REQUIRES THEIR NAMES, AND WHICH OF THEM HUNTS SUBMARINES, "
             "BEFORE THEY JOIN IT. THE ENCLAVE DETACHMENT'S Y-9 IS ALLOCATED FOR THE 18TH. THE "
             "CARRIER AIR WING WILL RELEASE A J-15 PAIR TO THE ENCLAVE FIELD AS ITS ESCORT.",
             "",
             "3. JAPANESE AIRCRAFT FROM LANGGUR ENGAGED SHIPS OF THE NORTHERN ELEMENT SOUTH "
             "OF SERAM THIS MORNING. THEY WERE NOT THIS GROUP'S SHIPS. THE GROUP IS NOT AT WAR "
             "WITH JAPAN. NOTHING OF THE GROUP'S FIRES ON A JAPANESE SHIP OR AIRCRAFT THAT HAS "
             "NOT FIRED.", "",
             "4. WHAT IS DONE WITH THE PICTURE IS NOT THE GROUP'S DECISION.", "",
             "ACKNOWLEDGE."],
         note_label="COMMANDER'S NOTE",
         note="Paragraph 4 again. The convoy sails on the twentieth, and whoever meets it "
              "will not be this group."),

    # --- before RLC1: the morning watch of the 24th -------------------------
    # The day after Fujian's Shadow, and the page says nothing of it: the
    # aircraft is Liaoning's, it came down with a fire warning, and the
    # log starts at the launch.
    dict(file="00d_air_log", before="Pilot in the Water", form="log",
         title="Air operations log\\n24 November 2028",
         sub="The carrier group's air operations log, the morning watch",
         ship="Carrier Task Group", master="Air operations officer",
         date="24 November 2028",
         log_heading="AIR OPERATIONS LOG EXTRACT", master_label="KEPT BY",
         note_label="COMMANDER'S NOTE",
         entries=[
             ("0415", "Dawn patrol launched from LIAONING: FLYING SHARK 85 and 86, J-15, "
                      "combat air patrol south-east of the group."),
             ("0447", "85 reports a fire warning, right engine. Turned for the deck, wingman "
                      "in company."),
             ("0452", "85 ejected sixty miles south-east of the group. Wingman reports one "
                      "good canopy and the aircraft into the sea."),
             ("0455", "Pilot's beacon received. Position passed to the screen."),
             ("0540", "Australian patrol vessel in the southern approaches reported turning "
                      "towards the beacon, a coalition patrol aircraft over her. 86 recovered, "
                      "low on fuel."),
             ("0550", "Screen ordered to detach a ship for the recovery.")],
         note="He comes home in a Chinese ship, and nothing is fired to make it so. Both "
              "halves of that are the order."),

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
