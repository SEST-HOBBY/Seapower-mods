# Supplement to the GPT handoff, 18 November 2026

SEST-DEV. Supplements `SEST_GPT_Independent_Research_QA_Handoff_2026-11-18.md`. It does not
replace it. Read that handoff first, then this. The full package list is in
`WORK-PACKAGES-20261118.md`.

You work from the files the owner attaches. You do not have the repository, its build tools, the
game or the owner's PC. You return documents and data files. The repository's build assistant
converts, builds and tests; the owner plays and uploads.

## 1. Where the project stands

- **Live on Steam:** release R14, built for Sea Power 0.9.2. On game 0.9.3 its code switches
  itself off; the data still loads.
- **R15:** a test build for the 0.9.3 **public beta** file. It compiles and passes its automated
  checks. It has not yet run in the game. Its first PC run is the next step. Nothing in R15 may be
  described as working in play.
- **Public-release file:** the normal 0.9.3 is a different game file. No capture of it exists yet
  and R15 stays off on it. The owner wants the next posting to work on both files. That is open
  until a capture and a build exist.
- **Dynamic Campaign Mod** (the engine of the world campaign) has not been seen running on 0.9.3.
- The four regions (Antarctica, Africa, South America, India) are research and design only. No
  region data has been added to the campaign.

## 2. What in the existing GPT handoff stands

- Tracks A, C and E (region fact register, supply and geography realism, reference fact-checking)
  stand as written. Your 24-page report `region-expansion-research.pdf` is received. It is used as
  a source list and cross-check. It is not in the builders' data format and names no unit ids, so
  it cannot be loaded; Gemini is converting region research into that format (packages GM-01 to
  GM-04) and you check the result (GP-10 below).
- Track D (runtime QA of the Regional Watch event schema) stands as a design review. Regional
  Watch has not been scoped in the repository and nothing of it is built.
- The rules stand: Australian English, sources with dates, fact / assessment / scenario labels,
  no publishing, no Git, no generated images.
- The output file names requested there stand for those tracks.

## 3. What the owner's later decisions change

1. **New Workshop item.** The handoff and the dossier say keep item 3812461539, the name "SEST
   Integration Pack - Modernised Campaigns" and all ids. The owner has since decided to repost the
   mod as a new, clean, all-in-one item named **Modern Naval Operations**. The old item will be
   marked deprecated and later removed. Saves and old ids need not carry over. Do not write a
   keep-versus-split decision sheet. Do not use "GCO" or "SEST Integration Pack" as the product
   name. The creator name stays **SEST-DEV**.
2. **Two game files.** The new item is to support the 0.9.3 public-release file and the
   public-beta file. Until the build assistant confirms it, texts say "public beta only".
3. **Left out of the new item:** the two plugins for game 0.8.7, the chain of twenty repair
   builds, SETUP branches for old game builds, the legacy world-campaign entry.
4. **Kept:** the small weapon packs, until a loadout-function enhancement replaces them.
5. **Required mods:** the list is being revised to stay lean while keeping expansive options;
   mods that nothing uses will be listed for the owner's review.
6. The "must not change" rule on the world campaign id `sest.world_sandbox_2028.regional` is
   released for the new item. Whether it changes is an open naming question. Do not assume either.

## 4. What the repository scoping found that corrects or sharpens the handoff

Paths are in the repository; you will be given the files named in each package.

- **Track B, catalogue count.** The discrepancy is real: the built `campaign.json` has 1,642
  catalogue entries; `docs/releases/20261107/validation.json`, `README-FIRST.txt` and
  `STEAM-PAGE-DESCRIPTION.txt` say 1,636. The cause has not been traced. Do not use either number
  in public text. Bases 196, forces 293, patrols 54, shipping lanes 11 and the bounds are confirmed.
- **Track B, base and unit ids.** You could not see them. They are now files:
  `docs/handoff/inputs/gmo-bases-89b9b4649.csv` (all 196 bases) and
  `docs/handoff/inputs/units-by-nation-regions.csv` (unit ids for the nations that matter to the
  four regions). Use only ids from these files.
- **Track C, neutrality.** The engine has two sides and no neutral base. Every base is owned and
  garrisoned with air-defence units and troops. "Context-only" content can only be a map label, a
  patrol waypoint, a traffic lane, or a Port flagged `notObjectiveFor`. Write recommendations in
  those terms.
- **Track C, "magic fuel".** The pack's ship replenishment transfers **ammunition only**. No SEST
  oiler transfers fuel. The "Fuel first - 2,000" tier is a ceiling in ammunition points. Whether a
  ship burns or receives fuel in a tactical mission is not established.
- **Air refuelling.** The game requires a tanker to declare `TankerSystems=` and a receiver
  `ReceiverSystems=` (Boom, ProbeAndDrogue, Wingtip). By static reading, the KC-46, KC-135 and
  KC-10A files in the collection lack the tanker declaration and cannot pass fuel. One PC test
  will confirm or refute this. No refuelling of any kind has been observed in the owner's logs.
- **Polar.** The 62S limit is a SEST data constant, not an engine limit found in code. What
  happens below it (map, routing, battle terrain) is unknown and needs one PC probe. The
  repository's land mask is unreliable south of about 60S. There is no ice in the game and no
  icebreaker, research ship or ski aircraft in the collection.
- **Track E, ribbons.** 25 world-campaign awards exist, all fictional. Today the F11 Service page
  shows the full citation for every award and the coloured strip only after award, which is the
  reverse of what the owner wants. The native campaign Service Record shows awarded ribbons only
  and cannot show progress without new runtime code.
- **Coordinated Strike.** The author's tool never launches anything; the player fires. It already
  accepts airborne aircraft that carry missiles or torpedoes as shooters. It does not plan the
  flight to a launch point, read fuel, see parked aircraft, or offer bombs and rockets. SEST's
  additions today are colours and a cost summary.

## 5. Rules for every package

1. Real, approved photographs only, with licence and source recorded. Never generate, render or
   AI-edit an image. Ribbon strips drawn from a stripe table are not photographs and are allowed.
2. Preserve upstream mod authors' credits. Never describe another author's work as SEST's.
3. No AI attribution text in any file: no "generated by", no assistant name, no disclaimers about
   being a model. Files carry the identity **SEST-DEV** or none.
4. Nothing is uploaded to Steam, GitHub or any other service by an assistant.
5. Every fact has a source: publication, date, URL, and a confidence note (high, medium, low).
6. Do not invent unit ids, base ids, ribbon ids, file names or keys. Use the ids in the attached
   files exactly, including case and punctuation.
7. Say plainly what could not be found or checked. "Not found" is an acceptable entry.
8. Do not promise features. Wording about anything not marked "tested on the PC" in the attached
   fact sheet must not say it works.
9. British/Australian spelling. Dates as 18 November 2026. Decimal degrees, south and west negative.

## 6. Work packages

Order: GP-03, GP-07, GP-05 and GP-06 can start now. GP-02 and GP-04 can be drafted now and
frozen after the owner's answers. GP-01, GP-09, GP-10, GP-11 and GP-08 wait on the inputs named.

### GP-01 Briefing consistency: tankers and replenishment

- **Goal.** Find every briefing line that promises air refuelling, fuel resupply or rearming that
  the mission cannot deliver, and propose a rewrite in the same voice.
- **Background.** Missions place tankers as units with a "Tanker" survival objective. No mission
  gives a refuel order or scores a transfer. Some placed tankers cannot pass fuel (section 4).
  Replenishment ships transfer ammunition only.
- **Attach.** `briefings-tanker-ras.csv` (mission_id, key, text; made by the build assistant from
  `integration/campaign/campaign_data.py` and `integration/campaign/southern_reach/*.py`);
  `aar-compatibility.csv` (mission_id, tanker_id, receiver_id, compatible yes/no/unknown).
- **Return.** `GP-01-briefings.csv`, UTF-8, columns:
  `mission_id,key,quoted_line,issue,rewrite,reviewer_note`. One row per affected line. `key` and
  `mission_id` copied exactly. Tokens in braces such as `{CommanderName}` unchanged. Rewrite
  within 10 per cent of the original length.
- **Acceptance.** Every `mission_id` and `key` exists in the input; no brace token altered; no
  rewrite claims a transfer for a pair marked no or unknown; length rule holds.

### GP-02 Ribbon labels, hints and citation text

- **Goal.** Supply the short text needed to show progress before an award and the full text after
  it, for the 25 world awards and the 17 fictional campaign ribbons, and split `RIBBONS.txt` into
  a spoiler-free part and a full reference.
- **Background.** Owner's rule: show progress; keep full award information until it is earned.
  Open owner questions: whether the name is hidden before award; whether the two Red Line conduct
  ribbons keep a one-word hint. Write both variants where they differ.
- **Attach.** `docs/handoff/inputs/world-awards-25.csv`;
  `integration/campaign/service_awards.py` (blocks CAMPAIGNS, MISSIONS, MILESTONES, RUNTIME at
  lines 50-97 and 458-541); `integration/campaign/setup/RIBBONS.txt`.
- **Return.**
  - `GP-02-world-awards.csv`: `id,unit_label,group,pre_award_line,pre_award_line_name_hidden,post_award_citation`.
    `unit_label` at most 3 words, lower case (for example "manual battles"). `group` is one of
    `Battle service|Watch|Theatre|Admiralty`. `pre_award_line` at most 60 characters; shows the
    counter, not the threshold wording. `post_award_citation` at most 160 characters; meaning
    unchanged. 25 rows, ids copied exactly.
  - `GP-02-campaign-ribbons.csv`: `ribbon_id,campaign,mission_code,class,pre_award_hint,requirement_line,reviewer_note`.
    `class` is `completion|operation|conduct`. `pre_award_hint` at most 50 characters with no
    condition detail. `requirement_line` at most 90 characters. One row per ribbon.
  - `GP-02-ribbons-txt.md`: the text of `RIBBONS.txt` in two parts, "What a player may read
    before playing" and "Full reference - spoilers". Every source sentence kept or moved, none
    invented. Then a list of unclear or contradictory sentences, quoted with line numbers.
- **Acceptance.** Row counts 25 and 17; ids match the inputs; no new threshold or number appears;
  length limits hold; every sentence of `RIBBONS.txt` is accounted for.

### GP-03 PC test cards

- **Goal.** Turn five test lists into printable cards the owner can follow at the PC.
- **Attach.** `docs/campaigns/red-line/test-card.md` as the pattern, and the five lists below
  (they are complete; add no tests).
  - Refuelling T1 to T10: T1 vanilla baseline (usaf_kc-10 with a boom receiver; usn_ka-3b with
    usn_fa-18a): right-click tanker, queue, contact, fuel rises. T2 unfixed modded tanker
    (usaf_kc-46a_boom with usaf_f-22): expect an "incompatible" message. T3 same pair after the
    fix: transfer, offload against capacity, drogue mesh warning. T4 declared-good pairs
    (aus_a330_mrtt with raaf_fa-18f and raaf_f-35a; wp_il-78 with wp_tu-22m2; usn_fa-18e Tanker
    loadout with usn_fa-18f). T5 bingo: receiver goes to the tanker, not base. T6 deck or airbase
    launch with UnlimitedFuel=False, one cancelled before take-off: is fuel charged and refunded,
    from where. T7 replenishment checklist items 1-5 and 7-12 with Stores=Depleted receivers, plus
    first-flight checks 4 and 5. T8 ship fuel: does a vessel show or burn fuel, does any supplier
    top it up. T9 one campaign mission with a tanker: do AI receivers use it unprompted. T10 world
    campaign: supply and forces panels, replenishment cargo, what the tankers table does, the
    Forces fuel line.
  - Coordinated Strike P0 to P5: P0 on 0.9.3 with two missile ships and one airborne missile
    aircraft: F8 opens, log line "Coordinated Strike refinements attached", add the aircraft with
    Use selected, note weapons, range and flight time flying straight and orbiting, lock, fire by
    hand, does the row go FIRED. P1 the SEST AIR LEGS block appears only for aircraft legs,
    numbers move, fuel verdict flips beyond fuel range, nothing with ships only, `StrikeAir=0`
    removes it. P2 the native window: F8 opens native, moves to the second monitor, typing in the
    time field there or steppers instead, "Classic panel" returns the author's panel with the same
    plan, `StrikeNative=0` is today's behaviour. P3 fresh settings give the native window and the
    second-monitor position survives a restart. P4 Set attack waypoint on an airborne Harpoon
    carrier: waypoint appears, aircraft flies and launches the planned salvo, row turns FIRED,
    deleting the waypoint leaves the plan; then two ships plus one aircraft, time-on-target,
    record impact spread in seconds. P5 linked SEAD plan at minus 60 s: both lock from one
    button, anti-radiation impacts lead by 60 s plus or minus the P4 spread.
  - Ribbons T1 to T10: T1 rules page with one drawn strip and one image path: which draws, any
    Noesis error. T2 briefing sheet image while the PNG is only in art/ribbons, then with a copy
    in art. T3 finish Red Line 03: screenshot the "Medal Awarded" row, picture or text. T4 new
    world save: Service shows 25 dim strips with n of m and no citation. T5 after 3 manual
    battles: first award full colour with citation, next "3 of 10" dim, an auto-resolved battle
    changes nothing. T6 existing profile from R14: same earned set, file unchanged except by new
    battles. T7 scroll, resize, pop out and return at 1080p and 1440p. T8 Red Line rules page: 5
    strips, no "no weapon launched" sentence; Southern Watch page scrolls and tabs switch. T9
    campaign Service panel states before and after Red Line 03 and 05, and a UK commander sees no
    Australian or US award. T10 standard build without the SEST runtime: campaigns load, no panel,
    no errors.
  - Polar probe: a copy of the world campaign with the southern limit at -78 and one Port at
    McMurdo. Record: does the campaign start; the "nav grid" line in the log; does the map draw
    below 62S; does a ship route to the port; does a battle there load with terrain.
  - New-item acceptance: fresh subscribe to the new item with the old item unsubscribed; SETUP
    runs; item at position 1 of the load order; code loads on the public-beta file and on the
    public-release file; each of the five campaigns starts; a new world campaign starts; F11
    opens; the old and the new item are never both enabled.
- **Return.** Five Markdown files, at most 80 columns: `GP-03-refuelling-test-card.md`,
  `GP-03-strike-test-card.md`, `GP-03-ribbons-test-card.md`, `GP-03-polar-probe-test-card.md`,
  `GP-03-new-item-test-card.md`. Per test: numbered steps, expected result per step, a
  `[ ] pass [ ] fail` box, what screenshot to take, and a "send back" line naming the log files
  (session HTML log, `Player.log`, `BepInEx\LogOutput.log`).
- **Acceptance.** Every test id from the lists appears once; no step states a result as already
  known; unit ids copied exactly; no test added or dropped.

### GP-04 Steam texts for the new item

- **Goal.** Draft the page, short description, collection description and first change note for
  **Modern Naval Operations**, a deprecation notice for the old item, and a subscriber FAQ.
- **Background.** Section 3. Subscribers of the old item get nothing automatically; they must
  subscribe to the new item, unsubscribe or disable the old one (the two must never both load),
  and run SETUP. Old saves show the game's missing-mods warning under the new item; whether a
  save can be continued past it is not established, so say "start new games".
- **Attach.** `docs/releases/20261107/STEAM-PAGE-DESCRIPTION.txt`, `STEAM-SHORT-DESCRIPTION.txt`,
  `STEAM-COLLECTION-DESCRIPTION.txt`, `STEAM-CHANGE-NOTE.txt`; a fact sheet from the build
  assistant (`new-item-fact-sheet.md`: what is in, what is left out, counts, tested / automated
  checks only / untested per feature).
- **Return.** Plain text, Steam BBCode only (`[h1] [h2] [list] [*] [b] [url]`):
  `STEAM-PAGE-DESCRIPTION.txt`, `STEAM-SHORT-DESCRIPTION.txt` (state the character count on the
  last line of your notes, not in the file), `STEAM-COLLECTION-DESCRIPTION.txt`,
  `STEAM-CHANGE-NOTE.txt`, `STEAM-OLD-ITEM-NOTICE.txt` (at most 600 characters, plus a longer
  pinned-post version below a line of dashes), `STEAM-FAQ.txt` (10 questions). Then
  `GP-04-NOTES.md` listing every statement you could not verify from the inputs.
- **Acceptance.** Every number equals the fact sheet; each feature is worded according to its
  evidence column; the line "formerly SEST Integration Pack" appears once on the page; authors'
  credits section retained; no claim about the public-release file unless the fact sheet marks it
  tested; no placeholder for a Workshop id is filled with an invented number (write `<NEW-ITEM-ID>`).

### GP-05 Coordinated Strike: design review, UI copy, maths check, author message

- **Goal.** Four small deliverables that support a native strike-planner window and aircraft
  advice.
- **Background.** Section 4, last bullet. Planned stages: (1) aircraft information in the
  existing panel; (2) a native window that calls the author's own methods, with his panel as
  fallback; (3) make it the default; (4) optional "Set attack waypoint" button and a "PUSH in"
  countdown for aircraft; (5) a linked SEAD plan, a deck availability list, bombs and rockets
  last. Stage 4 would issue an order on the player's click, which the author's tool by design
  never does. Not planned and not to be promised: automatic launch, ROE changes, EW, AEW, ASW,
  tanker or recovery roles.
- **Attach.** `native-strike-final-plan.txt` (the reviewed design, about 30k tokens);
  `strike-panel-strings.txt` (labels and hints from the author's panel, from the build assistant).
- **Return.**
  - `GP-05-plan-review.md`: numbered findings, each "section quoted | problem | suggested fix".
    Look for contradictions between the first plan and its corrections, steps with no test, and
    failure paths that leave the player with no panel. Do not rewrite the plan.
  - `GP-05-ui-copy.csv`: `key,text,alt1,alt2,alt3,max_len`. Labels at most 28 characters, hints
    at most 90. New fields: Kind, Altitude, Fuel, Launch point, Push in, Fuel short by, course
    not steady, and every disabled-button reason. Alternatives only for the five most prominent.
  - `GP-05-launch-point.md`: solution to "aircraft at P, speed v; target at T, velocity u; weapon
    in range within [Rmin, Rmax]; earliest time t and point where the range equals Rmax, heading
    chosen to minimise t; fuel = cruise burn out plus return to base B". Pseudocode of at most 40
    lines and 8 numeric test cases (inputs, expected outputs to 0.1 nm and 1 s), including a
    target opening faster than the aircraft (no solution) and a target already inside Rmin.
  - `GP-05-author-message.txt`: a message to the Coordinated Strike Tool's author, under 180
    words, polite, stating what SEST adds today, what is proposed, that his code is neither
    modified nor redistributed, and two questions (objections; would he prefer to take any of it
    upstream). Then a 60-word version for a Workshop comment.
- **Acceptance.** Findings quote text that exists in the plan; copy lengths hold; the 8 test
  cases are reproduced by the build assistant's implementation or the difference is explained;
  the message promises nothing.

### GP-06 Ribbon presentation review

- **Goal.** One decision paper that sets two designs side by side so the owner can choose.
- **Background.** Design X (repository scope): before award show a dimmed strip, the name, a
  progress figure and a short label; withhold citation, exact conditions and date. Design Y (the
  18 November dossier, section 8, and Gemini's handoff C): before award show an anonymous locked
  tile, category and counter only; no artwork, no name. Constraints both must respect: the world
  awards are drawn in code from a colour string, there are no image files; the native campaign
  Service Record shows awarded ribbons only; the campaign rules page has no commander state, so
  it can show images and withheld text but not progress; real progress in authored campaigns needs
  a new SEST runtime panel; the owner also wants world ribbons to belong to each save, while the
  ledger today is one file per player profile.
- **Attach.** This brief; dossier section 8; `Gemini-Award-Visibility-States.md` if it exists;
  `inputs/world-awards-25.csv`.
- **Return.** `GP-06-ribbon-presentation.md`, at most 4 pages: for X and Y, what the player sees
  in each of four places (world F11 Service, campaign rules page, campaign Service panel, offline
  gallery page), what each needs (data only / runtime code), what each hides, risks, and a
  recommendation with reasons. A final table of the owner decisions required.
- **Acceptance.** No place is described as able to do something the constraints rule out; both
  designs are treated for all four places.

### GP-07 Document consistency review and changelog digest

- **Goal.** Remove wording that states or implies fuel transfer or tested behaviour the evidence
  does not support.
- **Attach.** `docs/replenishment-in-play.md`; `integration/replenishment/README.md`; the fact
  sheet: "The pack transfers ammunition only. No fuel transfer exists. Tested in game: two-value
  TargetTypes=Vessel,Submarine parses; a submerged boat replenishes (kept as a house rule).
  Not recorded as run: checklist items 1-5 and 7-12, first-flight checks 1, 2, 4, 5. All tests
  predate game 0.9.2." Also `data/install-snapshot/changelog.live.txt`.
- **Return.** `GP-07-replenishment-review.csv`: `file,line_quote,problem,replacement`.
  `GP-07-changelog-digest.csv`: `date,build,tag,line` for every changelog line about fuel,
  tankers, refuelling, supply, replenishment or airbase stocks.
- **Acceptance.** Each `line_quote` is found verbatim in the named file; each changelog `line` is
  verbatim.

### GP-08 Player-facing guides (after PC results)

- **Attach.** A tested/untested fact sheet after the refuelling PC session; accepted region JSON
  files; `docs/world-sandbox/register/11-south-atlantic-france.md` as the style sample.
- **Return.** `GP-08-refuelling-guide.md` (600 to 900 words: What it is / How to use it / Limits
  / Where the numbers come from); `GP-08-region-text.md` (one paragraph per region for the
  campaign description, marked hypothetical); one register file per region in the sample's style
  with SOURCE CLAIM, CHECK and SCENARIO CHOICE kept apart.
- **Acceptance.** Every sentence traces to a line of the fact sheet or the JSON; no claim beyond
  them.

### GP-09 Old-name wording review

- **Attach.** `sest-visible-lines.csv` (`file,key,text`; about 580 player-visible lines that
  contain "SEST"), and the owner's answers on the short name and on in-fiction wording.
- **Return.** The same CSV with `proposed_text,reason` added. Change wording only; never keys,
  ids, file names or brace tokens; length within 10 per cent. Where "SEST" is the creator credit,
  keep it as SEST-DEV and say so in `reason`.
- **Acceptance.** Row count and the first three columns unchanged byte for byte.

### GP-10 Independent check of region data

- **Attach.** Gemini's accepted `GM-01` to `GM-04` JSON files with their notes; your own report;
  `inputs/gmo-bases-89b9b4649.csv`.
- **Return.** `GP-10-region-check.csv`:
  `file,json_path,field,value_in_file,value_in_source,source_url,date_accessed,verdict,note`,
  one row per disagreement in coordinates (more than 0.05 degrees), operator, host, class or
  runway heading, and one row per entry your report contradicts. A closing note on what you could
  not check.
- **Acceptance.** Every `json_path` resolves in the file; every row has a URL.

### GP-11 Naming consistency after the rebuild

- **Attach.** README, `docs/setup-runbook.md`, `docs/packaging-and-recovery.md`,
  `docs/FEATURES.md` and the pack's root .txt files as rebuilt, plus the list of names that were
  kept on purpose.
- **Return.** `GP-11-naming-consistency.csv`: `file,line_quote,problem,suggested_text`, for old
  and new names used inconsistently, instructions that still point at the old item or name, and
  kept identifiers wrongly reworded.

## 7. What to send back and how

- One folder or ZIP per package, named with the package id, holding exactly the files named in
  "Return" plus `<ID>-NOTES.md`.
- `<ID>-NOTES.md` contains: date of the work; the list of input files you were given; what could
  not be found or checked; open questions for the owner; for research rows, the source list.
- CSV: UTF-8, comma separated, one header row, fields with commas or line breaks in double
  quotes, no merged or blank spacer rows. JSON: valid, no comments. Markdown and text: plain, no
  embedded images.
- Do not include text that says who or what wrote the file. Do not restate this brief.
- Give the files to the owner. The owner places them under `docs/handoff/returns/<ID>/`; the
  build assistant runs the acceptance checks and replies with accepted, or a list of rows to fix.
- If an input file named under "Attach" was not given to you, stop and ask for it. Do not
  reconstruct it.
