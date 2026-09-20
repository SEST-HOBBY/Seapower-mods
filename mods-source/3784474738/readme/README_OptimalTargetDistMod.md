# Preferred Missile Range and Target Altitude

Set which missiles the AI should prefer at different ranges and when it may automatically engage targets above or below their altitude limits.

## Configure an ammunition INI

Add the optional keys to its existing `[Guidance]` section:

```ini
[Guidance]
OptimalTargetDist=60,180
MinAttackAltitude=15
MaxAttackAltitude=80000
AutoAttackBelowMinAltitude=True
AutoAttackAboveMaxAltitude=False
```

| Key | Meaning |
|---|---|
| `OptimalTargetDist` | Preferred range in nautical miles. Use a range such as `60,180` or one preferred distance such as `60`. |
| `MinAttackAltitude` | Lower target-altitude limit, in feet. |
| `MaxAttackAltitude` | Upper target-altitude limit, in feet. |
| `AutoAttackBelowMinAltitude` | `True` allows automatic attacks below the lower limit; `False` blocks them. |
| `AutoAttackAboveMaxAltitude` | `True` allows automatic attacks above the upper limit; `False` blocks them. |

The example prefers this missile at 60-180 nautical miles. It allows automatic attacks below 15 feet but waits for targets to descend to 80,000 feet or lower.

## Set up layered defense

Configure the competing missiles together: for example, `OptimalTargetDist=0,10` for a short-range missile and `OptimalTargetDist=10,50` for a longer-range missile.

These are preferences, not new firing-range limits. The game still checks weapon availability, range and guidance requirements, and can fall back to other suitable missiles. Mixing configured and unconfigured ammunition may retain the game's original selection.

Omitted altitude switches use the existing `AutoAttackOutsideAltitudes` setting. Omit all new keys to keep normal behavior. Restart the game and test with a fresh mission after editing.
