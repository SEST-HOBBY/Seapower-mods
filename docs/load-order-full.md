# Full Load Order — every active mod, top to bottom

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 148 active subscriptions plus the SEST Integration Pack (20 packs consolidated). Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

Tier 0 is the SEST block and must stay unbroken at the top. Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are alphabetical — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 0 — the consolidated SEST pack (must stay above everything)

1. **SEST Integration Pack** — ALL SEST content consolidated into one entry by tools/consolidate_packs.py - one Mod Manager slot at the very top carries every patch, so nothing can jump over an individual pack again

## Tier 1 — loader

2. **Anchor Chain** — loader — SeaLifter loads via its preloader alongside

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

3. **Custom Loadout Editor** — code mod — position not order-sensitive
4. **Better TacMap** — code mod — UI
5. **Coordinated Strike Tool** — code mod — time-on-target planner (F8); no game data, one _info.ini
6. **Automatic SAR** — code mod — right-click SAR; the campaign pays for survivors
7. **Identify Expanded** — code mod — identification and challenge orders; reads its own ini

## Tier 2 — weapon/system databases (this exact order)

8. **SAM Pack** — author: "top of TOE"
9. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
10. **Dingtools Weapon Pack** — author: "above any of my mods"
11. **U.S. Navy 2027 Capabilities mod** — above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's
12. **Euromod - Main Pack** — above all Euromod addons
13. **Modern PLAN Systems** — above PLAN ships

## Tier 3 — patches, each above what it modifies (this exact order)

14. **F-35C Lightning II Alt. Loadouts** — kept for now — MUST stay below SEST F-35C JATM
15. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
16. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
17. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
18. **Flight Deck Ops** — above carriers
19. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
20. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

21. 1143.5 Kuznetsov
22. [DEPRECATED] Anzac Class Frigate — *KEEP — SEST RAN Fleet dependency; SEST wins both ran_ffh_anzac files, so this mod's hull is masked until the pack is rebased onto it*
23. Auxilliary Merchant Pack
24. Charles De Gaulle & Modern French Navy Pack (WIP)
25. Chinese Navy (PLAN)
26. Euromod - Cold War Spanish Navy
27. Euromod - Modern British Navy
28. Euromod - Modern Dutch navy
29. Euromod - Modern German Navy
30. Euromod - Modern Italian Navy
31. Euromod - Modern Japanese Maritime Self Defence Force
32. Euromod - Modern Nordic Navy
33. Euromod - Modern Spanish Navy
34. Euromod-South Korea Navy
35. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
36. Italian Navy Mod
37. Kirov-class (Pyotr Velikiy Upgrade)
38. Merchants Expanded
39. Modern US Navy
40. Mogami-class Frigate
41. Moloti's Armed Merchantmen — *beside Merchants Expanded; no collision with anything, position free*
42. Nimitz Expanded
43. PLAN Submarines
44. PLAN Type 001 Aircraft Carrier Liaoning
45. PLAN Type 071 Amphibious Transport Dock
46. RE-power: the resupply mod
47. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
48. Russian Navy 21
49. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
50. Type 003 Aircraft Carrier - PLANS Fujian CV-18
51. Type 003 Fujian / Type 004 CVN Aircraft Carriers
52. United States Naval Aviation
53. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

54. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
55. <<E-3G>>
56. <<Tu-16N>>
57. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
58. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
59. A-10A Thunderbolt II
60. A-10C
61. AH-64 Apache
62. Anduril FQ-44 Fury US Navy Carrier Wingmen
63. Apex Predators MIG-29A & F-16A
64. Armed Oil Rig with Helo MOD
65. ARRW (AGM-183)
66. AVIC HARBIN Z-21
67. B-1B Lancer
68. B-2 Spirit
69. B-52H Stratofortress
70. Boeing P-8 Poseidon
71. Buildings and Targets for Missions
72. CH-53E Standalone v0.1.0
73. ChengDu J-10C Vigorous Dragon
74. Civil Aircraft Mod (Airbus Family)
75. David's Sling
76. Eurofighter Typhoon
77. Euromod - Anchorchain Expansion Pack
78. F-117 Nighthawk
79. F-15 EX Eagle II
80. F-15E StrikeEagle
81. F-16C Fighting Falcon (modern)
82. F-22 Raptor
83. F-2A 'Viper Zero'
84. French Air Force — *canonical order puts it at the bottom, above the PLAAF Aircraft Pack and Red Storm Arsenal: its 12 shared rounds are identical or older copies of the MQ-9 Reaper's, the French Navy pack's and the Soviet AEW&C pack's, and it loses every one; the Rafale and Mirage 2000 families load from it alone*
85. French Army Vehicles
86. French Helicopter Package
87. General Atomics MQ-9 Reaper
88. Humpback Whale
89. IL-78 TANKER
90. Iskander TBM
91. J-20 (歼-20 威龙)
92. J-36 Tailless Fighter
93. Ka-27RLD
94. KC-135 STRATOTANKER
95. KC-46A Pegasus - Strategic Tanker
96. Lockheed AC-130 Pack
97. McDonnell Douglas KC-10A Extender - Strategic Tanker
98. MH-60R Seahawk — *keep subscribed: ADO Nimitz 2000s draws its deck Seahawks from this mod's usn_sh-60b model folder. The MH-60R squadron table is SEST Collection Fixes' now (United States Naval Aviation's, written for the model that loads, plus 816 Squadron RAN), so its position above US Naval Aviation no longer decides it; unit file stays with U.S. Navy 2027*
99. Mi-8 T/TV
100. Mi-8EW
101. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
102. MiG-31 Foxhound
103. MiG-35 Fulcrum-F (米格-35 支点-F)
104. Mil Mi-24 Hind
105. MORE SU-24M VARIANTS
106. MV-22B Osprey Tiltrotor / JGSDF V-22B
107. MV-75 Cheyenne II — *beside the MV-22B; no collision with anything, position free*
108. Pickup truck extension
109. PLA & PLAN & PLAAF AEP — *Anchorchain expansion — below the loader, with the Euromod one*
110. PLA Shenyang J-11BS
111. PLA Sukhoi Su-27UBK
112. PLAAF Aircraft Pack — *canonical order puts it second to last, above Red Storm Arsenal only: 56 shared files all lost to the specialist PLAAF mods above it, so only its H-6 family, J-7s, J-10A and 39 rounds load; SEST Collection Fixes restores the English loading tips its language_en folder overwrites*
113. RAAF F-35A Lighting II
114. RC-135V/W Rivet Joint — *above Red Storm Arsenal, whose RC-135W is a different file (usaf_rc_135) — no collision; its sensors.ini merges*
115. Rebuilt J-16 / J-16D — *duplicate platform with Shenyang J-16A — different unit ids, both load*
116. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
117. RQ-180 White Bat Airframe
118. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
119. SAAB AEW&C PACK
120. SCUD-B
121. Sea Lynx
122. SEJJIL (Iran Ballistic Missiles)
123. Shahed-136 Kamikaze Drone (Geran-2)
124. Shenyang J-11
125. Shenyang J-16A (歼-16A 潜龙)
126. Shenyang J-50 (沈阳航空工业 歼-50)
127. Shenyang J-8
128. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
129. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
130. Su-25 Frogfoot
131. Su-30SM2
132. SU-57 Felon (重刑犯)
133. Sukhoi Flanker Family (苏霍伊侧卫家族)
134. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
135. TU-160 Blackjack
136. Tu-214R Family (图-214R家族)
137. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
138. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
139. Type 12 SSM-ER Anti-Ship Missile System
140. U-2 "Dragon Lady"
141. VH-3D Marine One MOD
142. XIAN JH-7A (歼轰-7A 飞豹)
143. Y-20 / KJ-3000
144. Y-8/Y-9 Special Mission Aircraft Family
145. YF-23 Black Widow II

## Tier 6 — airbases last

146. Modern Chinese Airbase (Large)
147. Modern Russian Airbase (Large)
148. Modern US Airbase

## Tier 7 — bulk arsenals, below everything they duplicate

149. **Red Storm Arsenal** — LAST - 638 unique files kept, 13 duplicated ones all lose

