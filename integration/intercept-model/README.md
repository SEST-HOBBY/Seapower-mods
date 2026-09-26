# SEST Intercept Model

Puts back the game's global intercept table. `ammunition/` is a whole-file override, and the
Tu-95 With AS-15 mod ships an `ammunition/damage.ini` built on a copy older than 0.8.x. It is
the only other copy in the collection, so it wins, and it drops eight global keys that every
anti-air round reads: the five `InterceptSizeBonus*` values, `InterceptOutOfAltitudePenalty=0.5`,
`InterceptSpeedPenaltyMultiplier=1.4` and `InterceptChanceOutOfAltitudeOverride=0.05`, a hard 5%
ceiling on any intercept where the target is outside the round's attack-altitude band. The pack
ships vanilla's table with the one change that mod meant to make (the `VeryLarge` impact tier,
2000.0 / 1000.0) carried forward.

**Not tested in game.** `tools/make_intercept_ab_builds.py` writes two deployables that differ
only in `damage.ini`, for a paired test, and it has never been run on the PC. Nothing in the files
says what the engine does with a deleted global. If it already falls back to the same numbers,
this pack changes nothing. If it does not, the pack arms the 5% out-of-band ceiling across the
collection. The one reading from the game points that way: under the truncated table the SM-3 read
7% against targets far below its floor, above what a live 5% ceiling allows. Expect SAMs with a
high floor to be held to 5% against anything below it: the SA-21 40N6 (21,000 ft) and 48N6E3
(2,900 ft) TELs, HQ-19 (99,000 ft), THAAD (20,000 ft) and the SM-3 (150,000 ft, set by SEST
Collection Fixes). The NORTHERN FRONT missions place the SA-21 TELs with no 9M96 TEL beside them.
In the campaign, Range Week's Shahed-136s are authored to fly no higher than 300 ft, under both
the Stunner's 500 ft floor and THAAD's; if the ceiling is live, neither battery does better than
5% against them, and that mission ends when one launcher or radar is lost.

Restoring the ceiling would turn three rounds into dead weapons, so the pack fixes them too:

| Round | Mod | Change |
|---|---|---|
| `usn_rim_174a/b/c` (SM-6) | Red Storm Arsenal (3413868677) | `MinAttackAltitude` 70000 -> 15 |
| `rok_k-sam-II` (K-SAM II, a copy of the Red Storm SM-6 file) | Euromod-South Korea Navy (3789208859) | `MinAttackAltitude` 70000 -> 15 |
| `idf_stunner` (David's Sling) | David's Sling (3558173926) | `MaxAttackAltitude=51,000` -> `51000`, which reads as 51 under a de-DE or fr-FR locale |

The four SM-6-family rounds also carry `SupplyCategory=SEST_LongRangeSAM`. That is not a fix:
SEST Replenishment At Sea meters every heavy ship-launched area SAM under that category, and as
this pack ships these files the tag has to ride in its copy. The replenishment builder checks
that it is there and fails if the rule stops selecting one of them.

The builder stops if the Tu-95 copy stops differing from vanilla by exactly those eight keys and
the two impact values, or if any file it overrides gains a second provider. The reasoning, the
counts, and the three paired tests that would settle what is still inference are in the builder's
docstring. `tools/survey_attack_altitudes.py` re-derives the counts after an export and lists
rounds the ceiling would harm.

**Requires:** Tu-95 With AS-15 · Red Storm Arsenal · David's Sling · Euromod-South Korea Navy.
**Order:** consolidated into SEST Integration, above every Workshop mod.
**Rebuild:** `python3 integration/intercept-model/build_patch.py`
