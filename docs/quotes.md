# The SEST quotation set

The lines the loading screen, the mission briefings and the Briefing Room
film share. One list drives all three: `integration/common/quotes.py`.

- **Loading screen.** SEST Collection Fixes numbers every quote behind the
  game's nineteen tips and the pack's own (`language_en/loading_tips.ini`).
- **Briefings.** Each campaign mission carries one quote under its photo
  banner, chosen by the mission's role (escort, patrol, recon, strike, fleet,
  logistics, opening) and different from every other mission's in the
  campaign while the set lasts.
- **Briefing Room.** A mission-browser entry (`missions/SEST Briefing Room/`)
  that plays a 73-second film in the right pane, the way the game's own
  Video Tutorials do: the collection's forces in real photographs with eleven
  of the lines over them. `tools/make_briefing_video.py` builds it from the
  gallery; the mp4 is committed under `integration/campaign/briefing_room/`
  and never re-encoded by the build.

What the game's data does **not** reach: the main-menu background and any
menu video. Nothing in `config.ini` or `ui/` names either, and no mod in
the collection replaces them. A code mod (Anchor Chain / BepInEx) would be
the only route, and the pack does not ship one.

## The rule on attribution

Three kinds, and the label says which. A modern internet aphorism never
borrows the authority of a Fleet Admiral.

| Kind | Meaning |
|---|---|
| named | a traceable speaker and an official or archival source; the year is shown only where the source dates the line |
| institution | an official formulation, such as a summit declaration |
| maxim | a traditional or anonymous saying, labelled as such |

The set follows the 6 October 2026 research note's "best additions" and
its attribution audit. Wording is ASCII (straight quotes, hyphens) because
the game's font has no glyph for curly quotes in some weights.

## The lines

| Quote | Attribution | Kind | Source |
|---|---|---|---|
| Air superiority is not guaranteed. It must be earned every day. | Gen. Kenneth S. Wilsbach, Chief of Staff, US Air Force, 2025 | named | First letter to the force, December 2025 (af.mil) |
| Neither air superiority nor victory are American birthrights. Both are at significant risk. | Gen. Mark Kelly, Commander, Air Combat Command, 2021 | named | Air Combat Command address, 2021 (af.mil) |
| Victory smiles upon those who anticipate the changes in the character of war, not upon those who wait to adapt themselves after the changes occur. | Giulio Douhet, 1921 | named | The Command of the Air; reproduced by Air University |
| We must think in terms of tomorrow. | Gen. Henry H. 'Hap' Arnold, US Army Air Forces | named | Air University, historical treatment of Arnold and future airpower |
| It's not enough to talk about deterrence: I believe we must demonstrate that we can deliver air power to degrade, disrupt, destroy, and defeat. | Air Marshal Stephen Chappell, Chief of Air Force, RAAF, 2026 | named | Chief of Air Force address, March 2026 (defence.gov.au) |
| Simply stated, strategic deterrence is about communicating capability and intent. | Adm. Cecil D. Haney, Commander, US Strategic Command | named | USSTRATCOM commander's remarks (stratcom.mil) |
| Saying so, unfortunately, does not make it true; and if true, saying so does not always make it believed. | Thomas C. Schelling | named | Arms and Influence; quoted by National Defense University, 2025 |
| Stability is not a passive state of affairs - it's achieved through strength and active diplomacy. | Air Marshal Robert Chipman, Chief of Air Force, RAAF, 2023 | named | Chief of Air Force address, 2023 (defence.gov.au) |
| Readiness is critical to an effective deterrence, not only in Air Force, but across all domains. | Air Vice-Marshal Harvey Reynolds, Deputy Chief of Air Force, RAAF | named | Deputy Chief of Air Force remarks (defence.gov.au) |
| If deterrence fails, we'll provide a decisive response. Decisive in every way that word means. | Gen. John E. Hyten, Commander, US Strategic Command, 2018 | named | USSTRATCOM commander's remarks, 2018 (stratcom.mil) |
| An attack on one is an attack on all. | NATO Ankara Summit Declaration, 2026 | institution | NATO Heads of State and Government, Ankara, July 2026 (nato.int) |
| Readiness is our first responsibility. | Gen. Kenneth S. Wilsbach, Chief of Staff, US Air Force, 2025 | named | First letter to the force, December 2025 (af.mil) |
| We are not training for our best day out. We are training for our worst day and then the next day and the day after. | Wing Commander Tim Hurford, RAAF, 2026 | named | RAAF Aviator Symposium, March 2026 (defence.gov.au) |
| This is so we can fight not just the way we want to, but the way we have to. | Air Vice-Marshal Glen Braz, Air Commander Australia, 2026 | named | On RAAF fighting depth, March 2026 (defence.gov.au) |
| Combat is unforgiving, and victory belongs to the side that adapts faster, fights harder, and endures longer. | Gen. Eric M. Smith, Commandant of the Marine Corps, 2025 | named | Force Design update, 2025 (marines.mil) |
| If we fail to adapt, fail to innovate, fail to develop and grow, we will find ourselves forever reacting and struggling. | Gen. Anthony Zinni, US Marine Corps | named | Reproduced in the US Marine Corps' official modernization history |
| Train, train, train, and train some more. | Gen. Leon E. Salomon, US Army | named | US Army leadership collection (army.mil) |
| Plans are worthless, but planning is everything. | Dwight D. Eisenhower, 1957 | named | Eisenhower Presidential Library, remarks of 14 November 1957 |
| Under pressure, you don't rise to the occasion - you sink to the level of your training. | military training maxim, speaker unknown; often called a SEAL saying | maxim | No original speaker, unit or dated source found; not Archilochus |
| The more you sweat in training, the less you bleed in battle. | traditional training maxim | maxim | 'Sweat in peace, bleed in war' is recorded from 1939; the training wording came later |
| An understanding of both pure logistics and the broad aspects of applied logistics is essential to the exercise of high command. | Rear Adm. Henry E. Eccles, US Navy, 1959 | named | Logistics in the National Defense |
| During deployment, it is too late to practice battlefield sustainment skills. | Gen. Gustave F. Perna, US Army Materiel Command, 2019 | named | Army Sustainment, 2019 (army.mil) |
| Our stockpiles need to be replenished. And we need this to happen fast. | Radmila Shekerinska, NATO Deputy Secretary General, 2026 | named | Ankara Dialogues, July 2026 (nato.int) |
| There is no strong defence without a strong defence industry. | Mark Rutte, NATO Secretary General, 2026 | named | NATO Summit Defence Industry Forum, 2026 (nato.int) |
| 'Better' is the enemy of 'good enough'. | Soviet naval maxim, reportedly displayed in Adm. Sergey Gorshkov's office | maxim | The office motto is reported; Gorshkov did not originate the saying |
| United we fought and united we prevail. | Fleet Adm. Chester W. Nimitz, 1945 | named | Message to the Pacific Fleet, 2 September 1945 (history.navy.mil) |

To change a line, edit `integration/common/quotes.py`, rebuild
(`python3 tools/build_all.py`) and, if the line is one of the eleven in the
film, run `python3 tools/make_briefing_video.py` and commit the new mp4.
