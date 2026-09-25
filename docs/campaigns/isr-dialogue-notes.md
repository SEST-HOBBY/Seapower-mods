# In-mission intel: notes toward a modern ISR voice

A first look, not a rewrite. Nothing in the missions has been changed for
this yet; these are notes to come back to.

## What the player hears now

Every in-mission message both campaigns send is one of five kinds, each a
single line of prose written once per mission:

| Kind | When it fires | Where it is written |
|---|---|---|
| Stage intel | a classify or area stage completes | `victory.after.intel` |
| Reveal intel | the mission opens and an earlier mission's result is read | `reveal_if[].intel` |
| Flag intel | a named enemy unit is destroyed | `flags[].intel` |
| Support-loss intel | a support asset is lost | `support_loss[].intel` |
| Discovery / reward intel | a classify objective pays off | `reveals`, `discoveries` |

They are well written, but they are narrative: "Lifter over the platform",
"WHISKEY classified: one low-profile semi-submersible". Nothing tells the
player where a threat is now, which way it is going, or which sensor saw it,
and nothing arrives unless the player has just done something.

## What modern ISR-cued traffic sounds like

Short, time-stamped, sourced, and positional. The shape:

```
1215K  SENTRY 21 (Triton): carrier group, 41 12S 152 03E, course 040, 14 kn.
       Two escorts in company. Deck spotted, no launch observed. Next pass 1245K.
```

- **Time first**, in the theatre's zone (K is UTC+10, Australian Eastern).
- **Source named**: Triton, P-8, Wedgetail link track, a satellite pass, a
  sonobuoy field, ESM, a partner nation's report. It tells the player what
  to trust and what to re-task.
- **A fix, course and speed**, not "somewhere to the south".
- **Confidence and age** when the fix is old or inferred ("datum 3 hours
  old, area of probability 10 NM").
- **What changed**, not the whole picture again.

## A builder feature that would do most of the work

The builder already knows every red unit's start, route and telegraph
speed. A mission could declare:

```python
isr_updates=[
    dict(at_minutes=15, units=["red_cv"], source="SENTRY 21 (Triton)"),
    dict(at_minutes=35, units=["red_sub"], source="Kiwi 05 sonobuoy field",
         accuracy_nm=8, note="below the layer"),
]
```

and the builder would compute each unit's expected position along its route
at that minute, write the message in the shape above, and emit a timed
trigger (`Condition_Type=Time`, `Action_Taskforce1_Intel`), the same
mechanism the stage messages already use. A submarine's fix would be offset
by `accuracy_nm` so the report is a datum, not a cheat. Satellite passes
could be scheduled the same way, at realistic intervals, for missions where
no aircraft is on station.

What it cannot know is whether the unit is still where its route says:
a unit the player has engaged or that has deviated is reported where it
should be. Keeping the updates to the first half of a mission, or to units
the player has not yet classified, keeps that honest.

## Line-by-line suggestions from the proofreading pass

The reviewers of each mission slice were asked to point at up to four
in-mission lines each and say how they could read as an ISR update. They are
collected below, unedited, as raw material.

ISRNOTES
