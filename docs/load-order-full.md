# Full Load Order — every active mod, top to bottom

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 129 active subscriptions plus 13 SEST local packs. Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

Tier 0 is the SEST block and must stay unbroken at the top. Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are alphabetical — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 0 — SEST local packs (must stay above everything)

1. **SEST Growler NGJ + MALICE** — above U.S. Navy 2027, F/A-18E/F, Murder Hornet, US Naval Aviation
2. **SEST F-15EX Revamp** — above the F-15EX mod ("F-15SE")
3. **SEST B-52H ARRW** — above Dingtools and the B-52H mod - AGM-183A loft + W62
4. **SEST Allied Fixes** — above U.S. Navy 2027 - repairs the P-8 anti-ship fit
5. **SEST F-35C JATM** — above every other usn_f-35c source
6. **SEST RAAF F-35A JATM** — above the RAAF F-35A mod
7. **SEST JMSDF Mogami** — above the Mogami-class Frigate mod
8. **SEST RAAF Wedgetail** — above the E-7A Wedgetail mod
9. **SEST Raptor Squadrons** — above the F-22 mod (which promises 7 squadrons, defines 1)
10. **SEST Zumwalt CPS Fix** — above Modern US Navy (repairs the DDG-1000 CPS hull)
11. **SEST TacMap Colors** — overrides the vanilla tactical-map UI colours
12. **SEST RAN Fleet** — contests nothing - additive RAN hulls
13. **SEST RAAF Bases** — contests nothing - additive RAAF airfields

## Tier 1 — loader

14. **Anchor Chain** — loader — SeaLifter loads via its preloader alongside

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

15. **Custom Loadout Editor** — code mod — position not order-sensitive
16. **AI Doctrine Overhaul** — code mod — changes AI globally
17. **Better TacMap** — code mod — UI

## Tier 2 — weapon/system databases (this exact order)

18. **SAM Pack** — author: "top of TOE"
19. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
20. **Dingtools Weapon Pack** — author: "above any of my mods"
21. **U.S. Navy 2027 Capabilities mod** — above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's
22. **Euromod - Main Pack** — above all Euromod addons
23. **Modern PLAN Systems** — above PLAN ships

## Tier 3 — patches, each above what it modifies (this exact order)

24. **F-35C Lightning II Alt. Loadouts** — kept for now — MUST stay below SEST F-35C JATM
25. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
26. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
27. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
28. **Flight Deck Ops** — above carriers
29. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
30. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

31. 1143.5 Kuznetsov
32. Auxilliary Merchant Pack
33. Charles De Gaulle & Modern French Navy Pack (WIP)
34. Chinese Navy (PLAN)
35. Euromod - Cold War Spanish Navy
36. Euromod - Modern British Navy
37. Euromod - Modern Dutch navy
38. Euromod - Modern German Navy
39. Euromod - Modern Italian Navy
40. Euromod - Modern Japanese Maritime Self Defence Force
41. Euromod - Modern Nordic Navy
42. Euromod - Modern Spanish Navy
43. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
44. Italian Navy Mod
45. Kirov-class (Pyotr Velikiy Upgrade)
46. Merchants Expanded
47. Modern US Navy
48. Mogami-class Frigate
49. Nimitz Expanded
50. PLAN Submarines
51. PLAN Type 001 Aircraft Carrier Liaoning
52. PLAN Type 071 Amphibious Transport Dock
53. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
54. Russian Navy 21
55. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
56. Type 003 Aircraft Carrier - PLANS Fujian CV-18
57. Type 003 Fujian / Type 004 CVN Aircraft Carriers
58. United States Naval Aviation
59. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

60. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
61. <<E-3G>>
62. <<Tu-16N>>
63. [DEPRECATED] Boeing F/A-18E/F Super Hornet — *kept for now — below Murder Hornet*
64. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
65. [DEPRECATED] Lockheed Martin F-35C Lighting II — *kept for now — must stay below SEST F-35C JATM (any tier below 3 satisfies this)*
66. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
67. A-10A Thunderbolt II
68. A-10C
69. AH-64 Apache
70. Apex Predators MIG-29A & F-16A
71. Armed Oil Rig with Helo MOD
72. ARRW (AGM-183)
73. AVIC HARBIN Z-21
74. B-1B Lancer
75. B-2 Spirit
76. B-52H Stratofortress
77. Boeing P-8 Poseidon
78. Buildings and Targets for Missions
79. ChengDu J-10C Vigorous Dragon
80. Civil Aircraft Mod (Airbus Family)
81. Dassault Rafale
82. David's Sling
83. Eurofighter Typhoon
84. F-117 Nighthawk
85. F-15 EX Eagle II
86. F-16C Fighting Falcon (modern)
87. F-22 Raptor
88. French Army Vehicles
89. French Helicopter Package
90. General Atomics MQ-9 Reaper
91. Humpback Whale
92. IL-78 TANKER
93. Iskander TBM
94. J-20 (歼-20 威龙)
95. Ka-27RLD
96. KC-135 STRATOTANKER
97. KC-46A Pegasus - Strategic Tanker
98. Lockheed AC-130 Pack
99. McDonnell Douglas KC-10A Extender - Strategic Tanker
100. MH-60R Seahawk — *watchlist: order vs other MH-60 sources decides which wins*
101. Mi-8 T/TV
102. Mi-8EW
103. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
104. MiG-35 Fulcrum-F (米格-35 支点-F)
105. Mil Mi-24 Hind
106. MORE SU-24M VARIANTS
107. Pickup truck extension
108. PLA Shenyang J-11BS
109. PLA Sukhoi Su-27UBK
110. RAAF F-35A Lighting II
111. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
112. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
113. SAAB AEW&C PACK
114. SCUD-B
115. Sea Lynx
116. SEJJIL (Iran Ballistic Missiles)
117. Shahed-136 Kamikaze Drone (Geran-2)
118. Shenyang J-11
119. Shenyang J-16A (歼-16A 潜龙)
120. Shenyang J-50 (沈阳航空工业 歼-50)
121. Shenyang J-8
122. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
123. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
124. Su-25 Frogfoot
125. Su-30SM2
126. SU-57 Felon (重刑犯)
127. Sukhoi Flanker Family (苏霍伊侧卫家族)
128. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
129. TU-160 Blackjack
130. Tu-214R Family (图-214R家族)
131. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
132. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
133. Type 12 SSM-ER Anti-Ship Missile System
134. U-2 "Dragon Lady"
135. VH-3D Marine One MOD
136. XIAN JH-7A (歼轰-7A 飞豹)
137. Y-20 / KJ-3000
138. Y-8/Y-9 Special Mission Aircraft Family

## Tier 6 — airbases last

139. Modern Chinese Airbase (Large)
140. Modern Russian Airbase (Large)
141. Modern US Airbase

## Tier 7 — bulk arsenals, below everything they duplicate

142. **Red Storm Arsenal** — LAST - 638 unique files kept, 13 duplicated ones all lose

