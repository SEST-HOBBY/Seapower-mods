# MV-22B Osprey — 1.1.30 local test build

Version 1.1.30 adapts default/beta game clocks and float/double spawn timestamps. Diagnostic failures disable diagnostics without interrupting native ship updates. Default-API fixtures, beta assembly resolution and offline regressions passed; flight/deck operations and ship effects still require restart and in-game testing on each version.

An unarmed transport tiltrotor for Sea Power, with US Marine Corps and JGSDF variants.

## Installation

1. Install and enable Anchor Chain (Workshop ID: 3380210757) and its required loader.
2. Place the archive's `V-22` folder in `Sea Power_Data/StreamingAssets/`. Keep `_info.ini` directly inside `V-22`.
3. Enable the mod and fully restart the game. Move the previous version out before updating and avoid loading a local and Workshop copy together.

## Variants and squadrons

The two Osprey units are the US Marine Corps MV-22B and the JGSDF V-22B. The USMC unit offers VMM-263 and VMM-162; the JGSDF unit offers the Transport Aviation Group's 107th and 108th Squadrons. Each unit's Default entry uses its own variant settings. Both share the Naval transport tiltrotor category.

## JGSDF variant

Select “V-22B Osprey, Japan Ground Self-Defense Force” to use the separate jgsdf_mv22b_osprey unit. Its grey-blue livery, roundels and Japanese service markings follow JGSDF aircraft 91707. It shares the original Osprey's model, flight animation, logistics profiles and deck operations. The real aircraft belongs to the JGSDF and has operated from JMSDF decks.

## Features and use

- Empty, Transport and Ferry profiles. Default, transport and rescue configurations have capacity for 32 personnel. Ferry uses internal fuel without external tanks.
- All three profiles have a base 20-minute ready-up time; the game's flight-deck timing mode affects actual progress. On ships with a reachable helicopter launch spot, the Osprey takes off vertically from that spot.
- Retains the Wasp recovery-route fallback and deck timing logs. Version 1.1.21 requests native engine shutdown when an Osprey is stationary and aligned at a carrier elevator with folding pending after recovery. Three consecutive Enterprise landings completed hangar stow in game. Fully restart the game after updating. Version 1.1.16 removed the empty exhaust resource that delayed the first deck spawn.
- Configured maximum sea-level speed: 275 knots, approximately 509.3 km/h. The cruise setting is slower.
- Configured maximum total range: 2200 km. Return rescue missions need fuel allowances for takeoff, landing, hover and reserves.
- For rescue, select Transport and choose Low-speed rescue (10 kt, also commands 20 ft), then Hover (0 kt, retaining the current altitude order) when in position. These are the only two lowest speed menu entries. Native wave clearance can raise actual sea altitude. Native rescue requires altitude above surface at or below 55 ft, speed at or below 12 kt and spare transport capacity. Fully restart and retest in game.
- Terminal waypoint auto-hover engages only when both requested and current altitude are at or below 5,000 ft. It slows before the final point of a non-looping player route, then commands a stationary hover and holds its position once stopped. Above the limit, the native cruise order remains in effect. Once braking starts, it disengages when either requested or current altitude exceeds 5,500 ft, preventing repeated switching near the boundary. Loop waypoints are excluded; a new route, speed or course order releases automatic control. Manual hover commands are unchanged. The 1.1.26 game log confirmed arrival, zero speed, position lock and release on a new route twice; 1.1.27 removes a misleading speed replacement log and tightens handoff exit conditions.
- Upgraded search radar, EO/IR, wideband radar warning and defensive jamming, with data sharing. Radar range limit: 220 km. Optical parameters follow the installed F/A-18F Block III mod. Actual detection depends on the target, weather and line of sight.
- Nacelles follow measured airspeed during recovery and remain vertical during landing and deck operations. The lower forward wing fairing stays on the fixed fuselage while the rest stows with the wing; the stow axis follows the roof slope. Looping engine audio stops after deck shutdown and rotor spin-down. On relaunch, it stays silent during transfer and unfolding, then resumes once the wing and blades are fully extended and the rotor starts turning.
- Exterior geometry, crew and spatial anchors use 1.6x visual scaling; flight performance values retain their original units.
- Separate Chinese and English localization selected by the game language.

## Assets

The exterior model and base textures come from the user-provided Bell Boeing V-22 Osprey asset archive. The JGSDF profile uses a JMSDF photo cropped and resized from [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:JGSDF_V-22_Osprey_landing_on_the_JS_Ise%EF%BC%88DDH-182%EF%BC%89-02_(cropped).jpg), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); attribution: Japan Maritime Self-Defense Force. Crew and substitute engine audio use Sea Power game resources. Search and defensive avionics are gameplay configurations, not a complete representation of real aircraft equipment.
