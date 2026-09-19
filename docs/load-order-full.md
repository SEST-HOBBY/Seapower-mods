# Full Load Order — every active mod, top to bottom

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 140 active subscriptions plus the SEST Integration Pack (18 packs consolidated). Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

Tier 0 is the SEST block and must stay unbroken at the top. Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are alphabetical — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 0 — the consolidated SEST pack (must stay above everything)

1. **SEST Integration Pack** — ALL SEST content consolidated into one entry by tools/consolidate_packs.py - one Mod Manager slot at the very top carries every patch, so nothing can jump over an individual pack again

## Tier 1 — loader

2. **Anchor Chain** — loader — SeaLifter loads via its preloader alongside

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

3. **Custom Loadout Editor** — code mod — position not order-sensitive
4. **AI Doctrine Overhaul** — code mod — changes AI globally
5. **Better TacMap** — code mod — UI

## Tier 2 — weapon/system databases (this exact order)

6. **SAM Pack** — author: "top of TOE"
7. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
8. **Dingtools Weapon Pack** — author: "above any of my mods"
9. **U.S. Navy 2027 Capabilities mod** — above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's
10. **Euromod - Main Pack** — above all Euromod addons
11. **Modern PLAN Systems** — above PLAN ships
12. **PLA & PLAN & PLAAF AEP** — Anchor Chain #!extend patches over PLA/PLAN/PLAAF rounds - an extend only applies if it outranks the copy it layers onto

## Tier 3 — patches, each above what it modifies (this exact order)

13. **F-35C Lightning II Alt. Loadouts** — kept for now — MUST stay below SEST F-35C JATM
14. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
15. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
16. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
17. **Flight Deck Ops** — above carriers
18. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
19. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

20. 1143.5 Kuznetsov
21. Auxilliary Merchant Pack
22. Charles De Gaulle & Modern French Navy Pack (WIP)
23. Chinese Navy (PLAN)
24. Euromod - Cold War Spanish Navy
25. Euromod - Modern British Navy
26. Euromod - Modern Dutch navy
27. Euromod - Modern German Navy
28. Euromod - Modern Italian Navy
29. Euromod - Modern Japanese Maritime Self Defence Force
30. Euromod - Modern Nordic Navy
31. Euromod - Modern Spanish Navy
32. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
33. Italian Navy Mod
34. Kirov-class (Pyotr Velikiy Upgrade)
35. Merchants Expanded
36. Modern US Navy
37. Mogami-class Frigate
38. Nimitz Expanded
39. PLAN Submarines
40. PLAN Type 001 Aircraft Carrier Liaoning
41. PLAN Type 071 Amphibious Transport Dock
42. RE-power: the resupply mod
43. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
44. Russian Navy 21
45. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
46. Type 003 Aircraft Carrier - PLANS Fujian CV-18
47. Type 003 Fujian / Type 004 CVN Aircraft Carriers
48. United States Naval Aviation
49. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

50. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
51. <<E-3G>>
52. <<Tu-16N>>
53. [DEPRECATED] Boeing F/A-18E/F Super Hornet — *kept for now — below Murder Hornet*
54. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
55. [DEPRECATED] Lockheed Martin F-35C Lighting II — *kept for now — must stay below SEST F-35C JATM (any tier below 3 satisfies this)*
56. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
57. A-10A Thunderbolt II
58. A-10C
59. AH-64 Apache
60. Apex Predators MIG-29A & F-16A
61. Armed Oil Rig with Helo MOD
62. ARRW (AGM-183)
63. AVIC HARBIN Z-21
64. B-1B Lancer
65. B-2 Spirit
66. B-52H Stratofortress
67. Boeing P-8 Poseidon
68. Buildings and Targets for Missions
69. CH-53E Standalone
70. ChengDu J-10C Vigorous Dragon
71. Civil Aircraft Mod (Airbus Family)
72. Dassault Rafale
73. David's Sling
74. Eurofighter Typhoon
75. Euromod - Anchorchain Expansion Pack
76. F-117 Nighthawk
77. F-15 EX Eagle II
78. F-15E StrikeEagle
79. F-16C Fighting Falcon (modern)
80. F-22 Raptor
81. F-2A 'Viper Zero'
82. French Army Vehicles
83. French Helicopter Package
84. General Atomics MQ-9 Reaper
85. Humpback Whale
86. IL-78 TANKER
87. Iskander TBM
88. J-16 Multirole Fighter
89. J-20 (歼-20 威龙)
90. J-36 Tailless Fighter
91. Ka-27RLD
92. KC-135 STRATOTANKER
93. KC-46A Pegasus - Strategic Tanker
94. Lockheed AC-130 Pack
95. McDonnell Douglas KC-10A Extender - Strategic Tanker
96. MH-60R Seahawk — *resolved (collection audit): sits directly above US Naval Aviation so its squadrons file matches the loading model; unit file stays with U.S. Navy 2027*
97. Mi-8 T/TV
98. Mi-8EW
99. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
100. MiG-31 Foxhound
101. MiG-35 Fulcrum-F (米格-35 支点-F)
102. Mil Mi-24 Hind
103. MORE SU-24M VARIANTS
104. Pickup truck extension
105. PLA Shenyang J-11BS
106. PLA Sukhoi Su-27UBK
107. RAAF F-35A Lighting II
108. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
109. RQ-180 White Bat Airframe
110. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
111. SAAB AEW&C PACK
112. SCUD-B
113. Sea Lynx
114. SEJJIL (Iran Ballistic Missiles)
115. Shahed-136 Kamikaze Drone (Geran-2)
116. Shenyang J-11
117. Shenyang J-16A (歼-16A 潜龙)
118. Shenyang J-50 (沈阳航空工业 歼-50)
119. Shenyang J-8
120. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
121. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
122. Su-25 Frogfoot
123. Su-30SM2
124. SU-57 Felon (重刑犯)
125. Sukhoi Flanker Family (苏霍伊侧卫家族)
126. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
127. TU-160 Blackjack
128. Tu-214R Family (图-214R家族)
129. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
130. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
131. Type 12 SSM-ER Anti-Ship Missile System
132. U-2 "Dragon Lady"
133. VH-3D Marine One MOD
134. XIAN JH-7A (歼轰-7A 飞豹)
135. Y-20 / KJ-3000
136. Y-8/Y-9 Special Mission Aircraft Family
137. YF-23 Black Widow II

## Tier 6 — airbases last

138. Modern Chinese Airbase (Large)
139. Modern Russian Airbase (Large)
140. Modern US Airbase

## Tier 7 — bulk arsenals, below everything they duplicate

141. **Red Storm Arsenal** — LAST - 638 unique files kept, 13 duplicated ones all lose

