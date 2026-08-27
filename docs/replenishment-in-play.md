# Replenishment at Sea — how it plays

A player's guide to what the SEST replenishment pack actually changes at the map.
For how it works under the hood, see `integration/replenishment/README.md`.

---

## The short version

**Bring a supply ship alongside, slow down, and your magazines refill.**

Before this pack, they did not. Guns and short-range point defence topped up fine, but
anti-ship missiles, torpedoes and every VLS strike round were one-shot for the whole mission:
when a Burke emptied its cells, that was the end of that Burke's war. **2,080 launchers across
292 ships** now reload where nothing could reload them before.

---

## Doing it

Three things have to be true at once, and all three are things you control:

**Get close.** Between 0.3 and 1.0 nautical miles, depending on the ship. The big fleet
auxiliaries work at a full mile; a submarine tender or a small oiler wants you almost
alongside.

**Slow down.** Both ships. Most auxiliaries stop supplying above 13 knots, and the receiver
above 16. The Don tender needs you down to 5. This is the gate you will trip most often —
a task force at transit speed is not replenishing, and a group under air attack that goes to
flank has just cut its own resupply.

**Wait.** Rounds come across one at a time and heavy ones take real minutes. See below.

Most auxiliaries service **two ships at once**; the Akademik Pashin does one. Queue the rest.

---

## What comes back

Everything the ship can hold — but the difference this pack makes is in the heavy end:

| | before | now |
|---|---|---|
| Gun ammunition, CIWS, RAM, ESSM | reloaded | reloaded |
| Harpoon, NSM, Exocet, Kalibr, YJ-18 | **never** | reloaded |
| Ship and submarine torpedoes | **never** | reloaded |
| VLS strike rounds — Tomahawk, LRASM, SM-6 | **never** | reloaded |

That third row is the big one. Red Storm Arsenal models every Mk41 cell as its own launcher,
so a Burke, a Tico or an arsenal ship had **no way at all** to take a missile back aboard.

---

## Picking the right ship

The number that matters is the **size ceiling** — the heaviest single round a ship will pass.
It is not about how much she carries; it is about what she can physically hand over.

### No ceiling — the ammunition ships

**Supply-class T-AOE · Sacramento AOE · Lewis and Clark T-AKE · Kilauea AE · Algol T-AKR**

Pass anything. These are what you bring when the strike group is going to shoot Tomahawks.
The Algol is the odd one out — a fast sealift Ro-Ro, not a proper replenishment ship, so she
passes anything but slowly and nearly stopped (8 knots, half a mile).

### Middle tier — 5,000 to 13,000

**Type 901 Fuyu (9,000) · Boris Chilikin (13,000) · Mashuu · Tide · Type 903A Fuchi (5,000) ·
Don tender · HMAS Supply (8,000)**

These pass Tomahawk (4,350) and Mk48 (4,695) but stop somewhere in the heavyweight bracket.
The Boris Chilikin's ceiling is threaded deliberately: she passes an SS-N-22 Moskit at 12,300
and refuses an SS-N-19 Granit at 21,000, because Granit's angled below-deck silos are not a
thing you reload at sea.

### Fuel first — 2,000

**Henry J. Kaiser T-AO · Teide · T2 · Kazbek · Sealift Pacific · Delvar · Akademik Pashin**

Guns, CIWS, ESSM, RAM, SM-2MR, Harpoon and ship torpedoes all pass. **Every strike round is
refused.** An oiler keeps you fighting; she does not rearm your strike package.

---

## How long it takes

Time to pass **one** round:

| round | Supply T-AOE | Sacramento | Type 901 | Tide | Kaiser |
|---|---:|---:|---:|---:|---:|
| RAM | 1s | 1s | 1s | 2s | 2s |
| ESSM | 4s | 4s | 5s | 6s | 8s |
| VL-ASROC | 9s | 10s | 11s | 14s | 20s |
| Harpoon | 13s | 14s | 16s | 19s | 29s |
| Tomahawk | 33s | 36s | 40s | 48s | **refused** |
| Mk48 ADCAP | 36s | 39s | 43s | 52s | **refused** |
| NSM / SM-6 | 62s | 67s | 73s | **refused** | **refused** |
| Zircon | 77s | 83s | **refused** | **refused** | **refused** |

In practice: **a full 8-cell Tomahawk module off a Supply-class takes about four and a half
minutes.** A 24-round ESSM magazine off a Tide takes a little over two. You are stationary,
slow and predictable the whole time — plan the window.

---

## How much a ship carries

Every auxiliary has a finite hold. It **runs out**, and it does not refill at sea.

| ship | Tomahawks | ESSM | Harpoons |
|---|---:|---:|---:|
| Supply-class T-AOE | 160 | 1,400 | 405 |
| Sacramento AOE | 137 | 1,200 | 347 |
| Lewis and Clark T-AKE | 126 | 1,100 | 318 |
| Algol T-AKR | 114 | 1,000 | 289 |
| Type 901 Fuyu | 91 | 800 | 231 |
| Mashuu AOE | 57 | 500 | 144 |
| Type 903A Fuchi | 50 | 440 | 127 |
| Boris Chilikin | 45 | 400 | 115 |
| Tide AOR | 41 | 360 | 104 |
| HMAS Supply | 36 | 320 | 92 |
| Don tender | 34 | 300 | 86 |
| Henry J. Kaiser T-AO | — | 160 | 46 |
| Teide oiler | — | 240 | 69 |
| Akademik Pashin | — | 180 | 52 |

Those are the extremes, not a shopping list — a hold spent on Tomahawks is not there for
torpedoes.

The number worth internalising: **a Flight III Burke's full 100-cell VLS load costs about
275,000 points to replace.** So —

- a **Supply-class T-AOE** carries **two and a half** full Burke reloads, then she is empty
- a **Type 901 Fuyu** carries about **one and a half**
- a **Tide** cannot fill even one

And a complete VLS reload at a Supply-class's transfer rate takes **about thirty-five minutes**
alongside. You will almost never do one. What you will do is top up the cells that matter and
get moving — which is exactly the decision the mechanic exists to make you take.

---

## Your fleet

**BLUE — five modern auxiliaries.** Supply-class T-AOE, Lewis and Clark T-AKE, Henry J.
Kaiser T-AO, JMSDF Mashuu, RFA Tide. All five carry their own navy's radar and point defence:
Artisan and Sea Ceptor on the Tide, OPS-48 and NOLQ-2 on the Mashuu, Phalanx Block 1B and
ESSM on the Americans.

**RED — three.** Type 901 Fuyu with Type 382/364 radar and twin Type 730 CIWS; Type 903A
Fuchi and the Russian Akademik Pashin, both **unarmed** — as their real counterparts are.
Give them an escort or lose them.

In the mission editor they group under **Replenishment (BLUE)** and **Replenishment (RED)**,
two adjacent blocks rather than scattered through *Fleet Auxiliary*.

Behind them sit the ten upstream auxiliaries — Sacramento, Kilauea, Boris Chilikin, Algol,
Don, Teide, T2, Kazbek, Sealift Pacific, Delvar — plus HMAS Supply from the RAN pack.
**Nineteen supply-capable hulls in all.**

---

## What still will not come back

**Sealed canisters on Cold War hulls.** Osa boats, Sa'ar boats, Kresta and Charlie boats,
Jianghus, wartime destroyers — **18 rounds across 70 launchers** whose weapons are welded-shut
deck tubes with no magazine behind them. This pack covers the modern fleet; those hulls are
deliberately left as the game shipped them.

**Italian and French hulls, for now.** Seven more rounds — Otomat, MILAS, Alfa, MM40 Exocet
Block 3 and two chaff types — sit on 26 hulls from the Italian Navy Mod and the Modern French
Navy pack, which the launcher fix does not yet cover. Fixable in a line if you want them;
say so.

**SS-N-19 Granit.** By design, as above.

**Aircraft ordnance.** Aircraft rearm from a carrier's or airbase's flight deck, which is a
separate system this pack does not touch and does not need to. Your Hornets are fine.

---

## What it changes about how you fight

**A strike group without an auxiliary has exactly one magazine.** That was always true; you
just could not do anything about it before. Now the composition of your task force is a real
decision — bring the T-AOE and you can fight twice.

**The oiler is now worth killing.** Sink the auxiliary and the group ahead of it fights with
what it has left. Expect the AI's to be escorted, and escort yours. Two of the RED ships
cannot defend themselves at all.

**Submarines can rearm, including submerged.** The engine applies no depth check and there is
no data-side way to add one — so this is a house rule, not a mechanic. **Surface your boats
before you reload them.** The capability is left on rather than removed, because taking it
away would also remove surfaced rearming, which is entirely legitimate.

**Watch the speed gate.** More replenishment attempts fail on 13 knots than on anything else.

---

*Numbers in this guide are generated from the shipped pack. Re-check them after a rebuild with
`python3 tools/check_reloadable.py`.*
