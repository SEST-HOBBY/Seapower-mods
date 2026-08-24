# Full Load Order — every active mod, top to bottom

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 126 active subscriptions plus 6 SEST local packs. Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are alphabetical — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 1 — loader

1. **Anchor Chain** — loader — SeaLifter loads via its preloader alongside

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

2. **Custom Loadout Editor** — code mod — position not order-sensitive
3. **AI Doctrine Overhaul** — code mod — changes AI globally
4. **Better TacMap** — code mod — UI

## Tier 2 — weapon/system databases (this exact order)

5. **SAM Pack** — author: "top of TOE"
6. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
7. **Dingtools Weapon Pack** — author: "above any of my mods"
8. **U.S. Navy 2027 Capabilities mod** — above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's
9. **Euromod - Main Pack** — above all Euromod addons
10. **Modern PLAN Systems** — above PLAN ships

## Tier 3 — patches, each above what it modifies (this exact order)

11. **SEST Growler NGJ + MALICE** — LOCAL — above U.S. Navy 2027, F/A-18E/F and US Naval Aviation
12. **SEST F-15EX Revamp** — LOCAL — above the F-15EX mod ("F-15SE")
13. **SEST F-35C JATM** — LOCAL — above every other usn_f-35c source (the four below it here)
14. **F-35C Lightning II Alt. Loadouts** — kept for now — MUST stay below SEST F-35C JATM
15. **SEST RAAF F-35A JATM** — LOCAL — above the RAAF F-35A mod
16. **SEST JMSDF Mogami** — LOCAL — above the Mogami-class Frigate mod
17. **SEST RAAF Wedgetail** — LOCAL — above the E-7A Wedgetail mod
18. **SEST Raptor Squadrons** — LOCAL — above the F-22 mod (which promises 7 squadrons, defines 1)
19. **SEST Zumwalt CPS Fix** — LOCAL — above Modern US Navy (repairs the DDG-1000 CPS hull)
20. **SEST TacMap Colors** — LOCAL — overrides the vanilla tactical-map UI colours
21. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
22. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
23. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
24. **Flight Deck Ops** — above carriers
25. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
26. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

27. 1143.5 Kuznetsov
28. Auxilliary Merchant Pack
29. Charles De Gaulle & Modern French Navy Pack (WIP)
30. Chinese Navy (PLAN)
31. Euromod - Cold War Spanish Navy
32. Euromod - Modern British Navy
33. Euromod - Modern Dutch navy
34. Euromod - Modern German Navy
35. Euromod - Modern Italian Navy
36. Euromod - Modern Japanese Maritime Self Defence Force
37. Euromod - Modern Nordic Navy
38. Euromod - Modern Spanish Navy
39. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
40. Italian Navy Mod
41. Kirov-class (Pyotr Velikiy Upgrade)
42. Merchants Expanded
43. Modern US Navy
44. Mogami-class Frigate
45. Nimitz Expanded
46. PLAN Submarines
47. PLAN Type 001 Aircraft Carrier Liaoning
48. PLAN Type 071 Amphibious Transport Dock
49. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
50. Russian Navy 21
51. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
52. Type 003 Aircraft Carrier - PLANS Fujian CV-18
53. Type 003 Fujian / Type 004 CVN Aircraft Carriers
54. United States Naval Aviation
55. Virginia-, Seawolf-, and Ohio-class Submarines
56. **SEST RAN Fleet** — LOCAL — below the Euromod packs it clones from

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

57. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
58. <<E-3G>>
59. <<Tu-16N>>
60. [DEPRECATED] Boeing F/A-18E/F Super Hornet — *kept for now — below Murder Hornet*
61. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
62. [DEPRECATED] Lockheed Martin F-35C Lighting II — *kept for now — must stay below SEST F-35C JATM (any tier below 3 satisfies this)*
63. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
64. A-10A Thunderbolt II
65. A-10C
66. AH-64 Apache
67. Apex Predators MIG-29A & F-16A
68. Armed Oil Rig with Helo MOD
69. AVIC HARBIN Z-21
70. B-1B Lancer
71. B-2 Spirit
72. B-52H Stratofortress
73. Boeing P-8 Poseidon
74. Buildings and Targets for Missions
75. ChengDu J-10C Vigorous Dragon
76. Civil Aircraft Mod (Airbus Family)
77. Dassault Rafale
78. Eurofighter Typhoon
79. F-117 Nighthawk
80. F-15 EX Eagle II
81. F-16C Fighting Falcon (modern)
82. F-22 Raptor
83. French Army Vehicles
84. French Helicopter Package
85. General Atomics MQ-9 Reaper
86. Humpback Whale
87. IL-78 TANKER
88. Iskander TBM
89. J-20 (歼-20 威龙)
90. Ka-27RLD
91. KC-135 STRATOTANKER
92. KC-46A Pegasus - Strategic Tanker
93. Lockheed AC-130 Pack
94. McDonnell Douglas KC-10A Extender - Strategic Tanker
95. MH-60R Seahawk — *watchlist: order vs other MH-60 sources decides which wins*
96. Mi-8 T/TV
97. Mi-8EW
98. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
99. MiG-35 Fulcrum-F (米格-35 支点-F)
100. Mil Mi-24 Hind
101. MORE SU-24M VARIANTS
102. Pickup truck extension
103. PLA Shenyang J-11BS
104. PLA Sukhoi Su-27UBK
105. RAAF F-35A Lighting II
106. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
107. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
108. SAAB AEW&C PACK
109. SCUD-B
110. Sea Lynx
111. SEJJIL (Iran Ballistic Missiles)
112. Shahed-136 Kamikaze Drone (Geran-2)
113. Shenyang J-11
114. Shenyang J-16A (歼-16A 潜龙)
115. Shenyang J-50 (沈阳航空工业 歼-50)
116. Shenyang J-8
117. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
118. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
119. Su-25 Frogfoot
120. Su-30SM2
121. SU-57 Felon (重刑犯)
122. Sukhoi Flanker Family (苏霍伊侧卫家族)
123. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
124. TU-160 Blackjack
125. Tu-214R Family (图-214R家族)
126. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
127. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
128. Type 12 SSM-ER Anti-Ship Missile System
129. U-2 "Dragon Lady"
130. VH-3D Marine One MOD
131. XIAN JH-7A (歼轰-7A 飞豹)
132. Y-20 / KJ-3000
133. Y-8/Y-9 Special Mission Aircraft Family

## Tier 6 — airbases last

134. Modern Chinese Airbase (Large)
135. Modern Russian Airbase (Large)
136. Modern US Airbase
137. **SEST RAAF Bases** — LOCAL — additive; bottom by convention

