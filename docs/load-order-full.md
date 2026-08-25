# Full Load Order — every active mod, top to bottom

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 129 active subscriptions plus 14 SEST local packs. Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

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
13. **SEST ADF Persistent ISR** — contests nothing - MQ-4C Triton + Zephyr S, mesh from the MQ-9 mod
14. **SEST RAAF Bases** — contests nothing - additive RAAF airfields

## Tier 1 — loader

15. **Anchor Chain** — loader — SeaLifter loads via its preloader alongside

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

16. **Custom Loadout Editor** — code mod — position not order-sensitive
17. **AI Doctrine Overhaul** — code mod — changes AI globally
18. **Better TacMap** — code mod — UI

## Tier 2 — weapon/system databases (this exact order)

19. **SAM Pack** — author: "top of TOE"
20. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
21. **Dingtools Weapon Pack** — author: "above any of my mods"
22. **U.S. Navy 2027 Capabilities mod** — above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's
23. **Euromod - Main Pack** — above all Euromod addons
24. **Modern PLAN Systems** — above PLAN ships

## Tier 3 — patches, each above what it modifies (this exact order)

25. **F-35C Lightning II Alt. Loadouts** — kept for now — MUST stay below SEST F-35C JATM
26. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
27. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
28. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
29. **Flight Deck Ops** — above carriers
30. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
31. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

32. 1143.5 Kuznetsov
33. Auxilliary Merchant Pack
34. Charles De Gaulle & Modern French Navy Pack (WIP)
35. Chinese Navy (PLAN)
36. Euromod - Cold War Spanish Navy
37. Euromod - Modern British Navy
38. Euromod - Modern Dutch navy
39. Euromod - Modern German Navy
40. Euromod - Modern Italian Navy
41. Euromod - Modern Japanese Maritime Self Defence Force
42. Euromod - Modern Nordic Navy
43. Euromod - Modern Spanish Navy
44. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
45. Italian Navy Mod
46. Kirov-class (Pyotr Velikiy Upgrade)
47. Merchants Expanded
48. Modern US Navy
49. Mogami-class Frigate
50. Nimitz Expanded
51. PLAN Submarines
52. PLAN Type 001 Aircraft Carrier Liaoning
53. PLAN Type 071 Amphibious Transport Dock
54. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
55. Russian Navy 21
56. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
57. Type 003 Aircraft Carrier - PLANS Fujian CV-18
58. Type 003 Fujian / Type 004 CVN Aircraft Carriers
59. United States Naval Aviation
60. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

61. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
62. <<E-3G>>
63. <<Tu-16N>>
64. [DEPRECATED] Boeing F/A-18E/F Super Hornet — *kept for now — below Murder Hornet*
65. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
66. [DEPRECATED] Lockheed Martin F-35C Lighting II — *kept for now — must stay below SEST F-35C JATM (any tier below 3 satisfies this)*
67. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
68. A-10A Thunderbolt II
69. A-10C
70. AH-64 Apache
71. Apex Predators MIG-29A & F-16A
72. Armed Oil Rig with Helo MOD
73. ARRW (AGM-183)
74. AVIC HARBIN Z-21
75. B-1B Lancer
76. B-2 Spirit
77. B-52H Stratofortress
78. Boeing P-8 Poseidon
79. Buildings and Targets for Missions
80. ChengDu J-10C Vigorous Dragon
81. Civil Aircraft Mod (Airbus Family)
82. Dassault Rafale
83. David's Sling
84. Eurofighter Typhoon
85. F-117 Nighthawk
86. F-15 EX Eagle II
87. F-16C Fighting Falcon (modern)
88. F-22 Raptor
89. French Army Vehicles
90. French Helicopter Package
91. General Atomics MQ-9 Reaper
92. Humpback Whale
93. IL-78 TANKER
94. Iskander TBM
95. J-20 (歼-20 威龙)
96. Ka-27RLD
97. KC-135 STRATOTANKER
98. KC-46A Pegasus - Strategic Tanker
99. Lockheed AC-130 Pack
100. McDonnell Douglas KC-10A Extender - Strategic Tanker
101. MH-60R Seahawk — *watchlist: order vs other MH-60 sources decides which wins*
102. Mi-8 T/TV
103. Mi-8EW
104. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
105. MiG-35 Fulcrum-F (米格-35 支点-F)
106. Mil Mi-24 Hind
107. MORE SU-24M VARIANTS
108. Pickup truck extension
109. PLA Shenyang J-11BS
110. PLA Sukhoi Su-27UBK
111. RAAF F-35A Lighting II
112. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
113. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
114. SAAB AEW&C PACK
115. SCUD-B
116. Sea Lynx
117. SEJJIL (Iran Ballistic Missiles)
118. Shahed-136 Kamikaze Drone (Geran-2)
119. Shenyang J-11
120. Shenyang J-16A (歼-16A 潜龙)
121. Shenyang J-50 (沈阳航空工业 歼-50)
122. Shenyang J-8
123. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
124. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
125. Su-25 Frogfoot
126. Su-30SM2
127. SU-57 Felon (重刑犯)
128. Sukhoi Flanker Family (苏霍伊侧卫家族)
129. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
130. TU-160 Blackjack
131. Tu-214R Family (图-214R家族)
132. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
133. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
134. Type 12 SSM-ER Anti-Ship Missile System
135. U-2 "Dragon Lady"
136. VH-3D Marine One MOD
137. XIAN JH-7A (歼轰-7A 飞豹)
138. Y-20 / KJ-3000
139. Y-8/Y-9 Special Mission Aircraft Family

## Tier 6 — airbases last

140. Modern Chinese Airbase (Large)
141. Modern Russian Airbase (Large)
142. Modern US Airbase

## Tier 7 — bulk arsenals, below everything they duplicate

143. **Red Storm Arsenal** — LAST - 638 unique files kept, 13 duplicated ones all lose

