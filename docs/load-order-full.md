# Full Load Order — every active mod, top to bottom

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 129 active subscriptions plus 12 SEST local packs. Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

Tier 0 is the SEST block and must stay unbroken at the top. Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are alphabetical — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 0 — SEST local packs (must stay above everything)

1. **SEST Growler NGJ + MALICE** — above U.S. Navy 2027, F/A-18E/F, Murder Hornet, US Naval Aviation
2. **SEST F-15EX Revamp** — above the F-15EX mod ("F-15SE")
3. **SEST B-52H ARRW** — above Dingtools and the B-52H mod - AGM-183A loft + W62
4. **SEST F-35C JATM** — above every other usn_f-35c source
5. **SEST RAAF F-35A JATM** — above the RAAF F-35A mod
6. **SEST JMSDF Mogami** — above the Mogami-class Frigate mod
7. **SEST RAAF Wedgetail** — above the E-7A Wedgetail mod
8. **SEST Raptor Squadrons** — above the F-22 mod (which promises 7 squadrons, defines 1)
9. **SEST Zumwalt CPS Fix** — above Modern US Navy (repairs the DDG-1000 CPS hull)
10. **SEST TacMap Colors** — overrides the vanilla tactical-map UI colours
11. **SEST RAN Fleet** — contests nothing - additive RAN hulls
12. **SEST RAAF Bases** — contests nothing - additive RAAF airfields

## Tier 1 — loader

13. **Anchor Chain** — loader — SeaLifter loads via its preloader alongside

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

14. **Custom Loadout Editor** — code mod — position not order-sensitive
15. **AI Doctrine Overhaul** — code mod — changes AI globally
16. **Better TacMap** — code mod — UI

## Tier 2 — weapon/system databases (this exact order)

17. **SAM Pack** — author: "top of TOE"
18. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
19. **Dingtools Weapon Pack** — author: "above any of my mods"
20. **U.S. Navy 2027 Capabilities mod** — above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's
21. **Euromod - Main Pack** — above all Euromod addons
22. **Modern PLAN Systems** — above PLAN ships

## Tier 3 — patches, each above what it modifies (this exact order)

23. **F-35C Lightning II Alt. Loadouts** — kept for now — MUST stay below SEST F-35C JATM
24. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
25. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
26. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
27. **Flight Deck Ops** — above carriers
28. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
29. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

30. 1143.5 Kuznetsov
31. Auxilliary Merchant Pack
32. Charles De Gaulle & Modern French Navy Pack (WIP)
33. Chinese Navy (PLAN)
34. Euromod - Cold War Spanish Navy
35. Euromod - Modern British Navy
36. Euromod - Modern Dutch navy
37. Euromod - Modern German Navy
38. Euromod - Modern Italian Navy
39. Euromod - Modern Japanese Maritime Self Defence Force
40. Euromod - Modern Nordic Navy
41. Euromod - Modern Spanish Navy
42. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
43. Italian Navy Mod
44. Kirov-class (Pyotr Velikiy Upgrade)
45. Merchants Expanded
46. Modern US Navy
47. Mogami-class Frigate
48. Nimitz Expanded
49. PLAN Submarines
50. PLAN Type 001 Aircraft Carrier Liaoning
51. PLAN Type 071 Amphibious Transport Dock
52. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
53. Russian Navy 21
54. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
55. Type 003 Aircraft Carrier - PLANS Fujian CV-18
56. Type 003 Fujian / Type 004 CVN Aircraft Carriers
57. United States Naval Aviation
58. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

59. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
60. <<E-3G>>
61. <<Tu-16N>>
62. [DEPRECATED] Boeing F/A-18E/F Super Hornet — *kept for now — below Murder Hornet*
63. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
64. [DEPRECATED] Lockheed Martin F-35C Lighting II — *kept for now — must stay below SEST F-35C JATM (any tier below 3 satisfies this)*
65. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
66. A-10A Thunderbolt II
67. A-10C
68. AH-64 Apache
69. Apex Predators MIG-29A & F-16A
70. Armed Oil Rig with Helo MOD
71. ARRW (AGM-183)
72. AVIC HARBIN Z-21
73. B-1B Lancer
74. B-2 Spirit
75. B-52H Stratofortress
76. Boeing P-8 Poseidon
77. Buildings and Targets for Missions
78. ChengDu J-10C Vigorous Dragon
79. Civil Aircraft Mod (Airbus Family)
80. Dassault Rafale
81. David's Sling
82. Eurofighter Typhoon
83. F-117 Nighthawk
84. F-15 EX Eagle II
85. F-16C Fighting Falcon (modern)
86. F-22 Raptor
87. French Army Vehicles
88. French Helicopter Package
89. General Atomics MQ-9 Reaper
90. Humpback Whale
91. IL-78 TANKER
92. Iskander TBM
93. J-20 (歼-20 威龙)
94. Ka-27RLD
95. KC-135 STRATOTANKER
96. KC-46A Pegasus - Strategic Tanker
97. Lockheed AC-130 Pack
98. McDonnell Douglas KC-10A Extender - Strategic Tanker
99. MH-60R Seahawk — *watchlist: order vs other MH-60 sources decides which wins*
100. Mi-8 T/TV
101. Mi-8EW
102. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
103. MiG-35 Fulcrum-F (米格-35 支点-F)
104. Mil Mi-24 Hind
105. MORE SU-24M VARIANTS
106. Pickup truck extension
107. PLA Shenyang J-11BS
108. PLA Sukhoi Su-27UBK
109. RAAF F-35A Lighting II
110. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
111. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
112. SAAB AEW&C PACK
113. SCUD-B
114. Sea Lynx
115. SEJJIL (Iran Ballistic Missiles)
116. Shahed-136 Kamikaze Drone (Geran-2)
117. Shenyang J-11
118. Shenyang J-16A (歼-16A 潜龙)
119. Shenyang J-50 (沈阳航空工业 歼-50)
120. Shenyang J-8
121. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
122. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
123. Su-25 Frogfoot
124. Su-30SM2
125. SU-57 Felon (重刑犯)
126. Sukhoi Flanker Family (苏霍伊侧卫家族)
127. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
128. TU-160 Blackjack
129. Tu-214R Family (图-214R家族)
130. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
131. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
132. Type 12 SSM-ER Anti-Ship Missile System
133. U-2 "Dragon Lady"
134. VH-3D Marine One MOD
135. XIAN JH-7A (歼轰-7A 飞豹)
136. Y-20 / KJ-3000
137. Y-8/Y-9 Special Mission Aircraft Family

## Tier 6 — airbases last

138. Modern Chinese Airbase (Large)
139. Modern Russian Airbase (Large)
140. Modern US Airbase

## Tier 7 — bulk arsenals, below everything they duplicate

141. **Red Storm Arsenal** — LAST - 638 unique files kept, 13 duplicated ones all lose

