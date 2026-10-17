# Side operations: the slate

Decided 17 Oct 2026: side operations go into the existing campaigns as
**in-theatre optional missions**, themed on four kinds of work:
smugglers and arms runners, privately escorted armed merchants, air defence,
and major assault and defence operations. Some are linked to each other and
to the core missions; others stand alone. Each one puts collection mods to
work that no SEST mission uses yet, where they fit.

Nothing here is built yet. Seeds are in `integration/mission-seeds/` (index in
its README). Every operation is rebuilt as a campaign mission spec and passes
the same gates as the core missions.

## How an optional works here (constraints that shape the slate)

- **Same sea area and date window** as its campaign; it hangs off the main
  chain (`group="optional"`, `expires_after`), so skipping it never blocks the
  campaign.
- **A fixed detachment flies it** (`window=dict(detachment=True)`) unless
  noted: no buy, repair or rearm window, and the player's owned ships are not
  spent. That matters most in Sulu Line, where there is no free rearm.
- **Links are campaign variables**: an optional `declares` an outcome and a
  later mission reads it (`spawn_if`), the way TS10A Northern Priority feeds
  TS11 Approaches. That is the only link the game carries between missions,
  and only within one campaign's save.
- **Units must have ids a campaign file can name.** Project 2498 Zyetseth
  (`Project 2498 Zyetseth Class Assault Vessel`) has spaces in its id, so it is
  out; its sister file `civ_fv_okean_surprise` (a fishing trawler with a hidden
  torpedo tube) is in. The Steelfin cruiser is a `#!copy` overlay; that SEST's
  builder places it correctly is unverified.
- **A mod an optional uses becomes a requirement** of that campaign, and comes
  off the coverage excuse list.

## Thread A: The Night Market (Sulu Line; smugglers and arms runners; linked)

The drug money is what buys Meridian's guns. Two optionals and one change to
a core mission.

| ID / date | Operation | Task | Forces and mods exercised | Link |
|---|---|---|---|---|
| SL-O1 · 15 Oct | **Night Market** (seed: Narco Transit) | Night, calm sea: find a narco-submarine running south through the Sulu Sea among fishing boats, and take it before it reaches the Tawi-Tawi coast. A civilian AS350 is the runners' eye. | Philippine Navy patrol ship and its helicopter (detachment). Red Storm Arsenal's `_narco_narcosub_adv` and `_narco_speedboat`; **civilian AS350** (`civ_as-350`, unused); fishing traffic. | Declares `SLNarcoTaken` |
| SL-O2 · 29 Oct | **The Okean** | The money's delivery: an armed trawler mother-ship transfers crates to fast boats off Tawi-Tawi, with a Meridian helicopter shuttling. Board-or-sink choice by classification; the trawler fights back with its hidden torpedo. | Detachment as above. **Project 2498's `civ_fv_okean_surprise`** (unused) under the Meridian flag; **Iranian Navy Bell 212** (`irinavy_bell-212`, unused) as the Meridian shuttle; `_narco_speedboat`. If `SLNarcoTaken`, the trawler's name is in the brief and she is revealed at the start. | Declares `SLOkeanTaken` |
| SL05 · 9 Nov (core, changed) | **Celebes Gate** | As built. | As built. | If `SLOkeanTaken`, the spotter drone does not come: the network lost its money and its eyes. |

## Thread B: Escorted Hulls (Southern Watch; privately escorted armed merchants; linked)

Meridian's escorts in the Arafura and Banda Seas, before and after the
shooting starts.

| ID / date | Operation | Task | Forces and mods exercised | Link |
|---|---|---|---|---|
| SW-O5 · 21 Oct | **Paper Trail** (bible O02; seed: Sanctioned Cargo) | Shadow a Meridian-escorted logistics merchant to its handover and identify the receiver, without firing first: the rules are still Hold. | An Anzac and its Seahawk; a US uncrewed scout loaned to the RAN: **Saronic Corsair Scout** (`usn_asv_saronic_corsair_scout`, unused) or **Anduril K5 KRAKEN** (`usn_usv_k5_kraken`, unused), the RAN's own Ghost Shark being the same idea. | Declares `SWPaperTrail`; SW04 The Quiet Passenger reveals one patrol lane if true (bible: "identifies a likely patrol lane for SW04"). |
| SW-O6 · 3 Nov | **The Second Convoy** (seed: NF3 Sanctioned Convoy) | Weapons Free now: stop an escorted armed convoy running dark for Biak, with civilian traffic in the same water. | An Anzac pair (detachment). Armed merchants (`wp_ms_andizhan_armed`), the Q-ship (`wp_ms_mercur_decoy`), **`civ_fv_okean_surprise`** (unused), Peykaap escorts, all under the Meridian flag. | Reads `SWPaperTrail` (the convoy's route is known if true). |

## Thread C: Air defence (Southern Watch; stand-alone)

| ID / date | Operation | Task | Forces and mods exercised |
|---|---|---|---|
| SW-O7 · 15 Nov | **Bomber Stream** (seed: NF3 Bomber Stream) | Intercept an H-6K and Tu-95 raid on Tindal and Darwin before launch range. | RAAF F-35A JATM, Wedgetail and tankers, a US F-22 detachment; the raid from the PLAAF and Russian bomber mods. |
| SW-O8 · 22 Nov | **Ballistic Shield** (seed: NF3 Ballistic Shield) | Meridian's missiles from the Biak enclave: hold Darwin against a mixed raid of ballistic missiles and one-way drones. | Patriot and THAAD at Darwin; the US **Steelfin land battery** (`usa_steelfin_launcher`, unused). Raid: **Fattah-1, Fattah-2** (unused), **Shahed 238** (unused), **Emad** (unused). Overlaps Dispatch D5 Range Week in kind but not in place or stakes. |

## Thread D: Major assault and defence (Southern Watch; stand-alone, with rewards)

| ID / date | Operation | Task | Forces and mods exercised | Reward |
|---|---|---|---|---|
| SW-O9 · 15 Nov | **Second Ring** (seeds: NF3 SEAD over the Shelf, Deep Strike Corridor) | After The Open Door, Russia has rebuilt the Biak belt with newer kit. Take it down before the relief ships go through. | B-52 with ARRW, F-15EX, EA-18G. Red: **S-350 Vityaz**, **Buk-M3**, **Nebo-U**, **S-300PMU2** (all unused). | Fewer air threats in SW09 Southern Lifeline. |
| SW-O10 · 17 Nov | **Viper Zero** (bible O09; seed: Viper Zero) | JASDF F-2A strike on a PLAN amphibious group off Kalimantan that threatens the arriving Japanese task group. | JASDF F-2A Late, the **EC-2 stand-off jammer** (`jasdf_ec-2`, unused) in support, and the **JMSDF Hyuga** (`jmsdf_ddh_hyuga`, unused) group the strike protects. | F-2A support becomes the Japanese option for SW10 (bible). |

## Order of work

1. **SL-O1 Night Market**, the pilot: the first thread's first step, and
   the first optional in Sulu Line, which proves the package handles
   optionals and a declared variable.
2. SL-O2 and the SL05 link, closing Thread A.
3. Thread B, then D (Viper Zero has its slot and reward written already),
   then C.

Of the 40 mods no SEST mission uses yet, this slate puts 16 to work: civilian
AS350, the Project 2498 trawler, Iranian Bell 212, Saronic Corsair, Anduril
Maritime Drones, Steelfin, Fattah-1, Fattah-2, Shahed 238, Emad, S-350,
Buk-M3, Nebo-U, S-300PMU2, EC-2 and Hyuga.
