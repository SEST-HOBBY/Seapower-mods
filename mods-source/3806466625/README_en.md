# V-22 Osprey / SV-22 2024 — 1.1.45

Includes the US MV-22B, Japanese V-22B and fictional SV-22 2024 ASW variant under the Naval tiltrotor category. On 2026-10-12, the user confirmed that continuous SV-22 dipping-sonar tasks work in game.

## Installation and updates

1. Install and enable Anchor Chain (Workshop ID 3380210757) and its required loader.
2. Place the `V-22` folder in `Sea Power_Data/StreamingAssets/`, with `_info.ini` at the mod root.
3. Enable the mod. After updating plugins, fully exit and restart the game. Avoid enabling another Osprey copy at the same time.

Current plugins: mechanics 1.1.45 and deck operations 1.1.36, for the installed Sea Power 0.8.5 Build 261008. This cleanup retains the working plugin binaries and resources.

## Aircraft and functions

| Aircraft | Nation / scenario availability | Functions |
| --- | --- | --- |
| MV-22B | US Marine Corps / 2007 | Transport, SAR, manual hover and terminal auto-hover |
| V-22B | Japan Ground Self-Defense Force / 2020 | Same transport functions; independent grey-blue paint and Japanese markings |
| SV-22 | Fictional US ASW variant / 2024 | Sonobuoy search, torpedo attack, continuous dipping-sonar tasks and manual hover; zero passenger capacity |

US units retain VMM-263 and VMM-162; Japanese units retain the 107th and 108th Squadrons. SV-22's 2024 date is fictional scenario availability. Campaign unit-date filtering requires the corresponding year.

Transports offer Empty, Transport and Ferry profiles. Default, Transport and rescue configurations carry 32 people; base preparation time is 20 minutes. Slow SAR selects 10 kt and a 20 ft altitude target; native rescue also checks actual height, speed and remaining capacity. Hover selects zero speed while retaining the altitude command.

The final point of a player's non-loop transport route can trigger braking, hover and position hold. Requested and actual altitude must be at or below 5000 ft to enter; 5500 ft is the exit threshold. New route, course or speed commands release automatic control.

## SV-22 stores and release

| Loadout | Torpedoes | Passive buoys | Active buoys |
| --- | ---: | ---: | ---: |
| ASW | 4 | 32 | 16 |
| ASWKiller | 6 | 12 | 4 |
| ASWHunter | 0 | 48 | 16 |
| Empty / Ferry | 0 | 0 | 0 |

Independent Mk 54 Mod 1, SSQ-53G and SSQ-62F configurations use stock visual assets. Stores occupy separate cabin slots; only the selected weapon moves to the aft-ramp release point, followed by native parachute, water-entry and guidance behavior.

SV-22 retains manual Hover. Ordinary waypoints do not trigger automatic hover, Slow SAR is absent and passenger capacity is zero. Equipment data, mass estimates, release limits and sources are in [SV22_PROTOTYPE.txt](SV22_PROTOTYPE.txt). Non-public modern performance is estimated for gameplay.

## Continuous dipping sonar

Create dipping-sonar waypoints from the ALFS sensor menu and place successive task points. For the executing task, SV-22 approaches, descends to approximately 35 ft and slows to hover. Vertical nacelles, steady actual attitude and native speed, water-depth and operability conditions are required before the belly hatch opens and the probe deploys. Actual deployment height must be 20–45 ft; sea state affects the safe altitude.

Listening starts after the probe enters water. New native tasks default to 120 seconds; the chosen duration is retained, with 0 meaning indefinite listening until cancellation. After listening, the cable and probe retract and the hatch closes before the next point starts. Normal completion restores the prior speed and altitude commands.

Actual player speed/altitude changes, task deletion or another executing task cancel special control and request retrieval. Native landing, refueling, shutdown and loss of control take priority. Internal speed and altitude refreshes continue without being treated as player cancellation.

The independent sensor is `SV22_2024_ALFS`. Stock AQS-13 probe, material and cable visuals use separate modern-system gameplay data. SV-22 has a dedicated belly aperture, two hatch doors and an interior sonar well.

## Flight, refueling and deck operations

- Configured maximum speed is 275 kt. Total configured range is 2200 km for transports and 1850 km for SV-22.
- All three support manual hover, nacelle tilt, landing gear, wing/blade folding and shutdown audio. Ships need suitable VTOL launch and recovery facilities.
- The sea altitude floor is 20 ft plus native wave allowance. Low-speed gameplay limits are +12/-6 m/s with 3 m/s² vertical acceleration and braking near the target. Forward low-speed pitch is limited to 15 degrees; zero-speed hover stays level.
- Out-of-combat/combat altitude response thresholds are 500/500 ft. Normal non-combat cruise ascent uses the native 30-second energy trade with actual/demanded speed at least 130 kt and an upward height error above 5 m. Native power and climb-rate limits remain in effect; actual speed may fall during ascent.
- Native probe-and-drogue refueling, landing, deck and crash handling retain control. Search radar, electro-optics, radar warning, defensive jamming and data sharing are provided.

## Validation record

Existing records cover current-game compilation, configuration/resources and offline mechanics, audio, loadout, cache, release, hover and deck regressions. The user's 2026-10-12 feedback confirms continuous SV-22 dipping tasks work; it does not separately confirm underwater detection performance or every platform behavior. This file cleanup verifies runtime files by SHA-256 and retains their original bytes.

## Assets and licensing

The exterior model and base textures come from the user-supplied Bell Boeing V-22 Osprey asset pack. Crew, replacement engine audio and ASW visuals use Sea Power resources. The Japanese aircraft is operated by the JGSDF; its livery is based on aircraft 91707.

The Japanese profile photo was taken by the Japan Maritime Self-Defense Force, sourced from a Wikimedia Commons crop and cropped/resized for this mod. Credit under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). [Original image and license](https://commons.wikimedia.org/wiki/File:JGSDF_V-22_Osprey_landing_on_the_JS_Ise%EF%BC%88DDH-182%EF%BC%89-02_(cropped).jpg).

See [CHANGELOG.md](CHANGELOG.md) for changes. 中文：[README.md](README.md)。
