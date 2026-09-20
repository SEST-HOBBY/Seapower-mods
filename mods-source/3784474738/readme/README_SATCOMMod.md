# SATCOM Missile Guidance

## Configure an ammunition INI

Add or change these keys in the existing sections:

```ini
[General]
Retargetable=True

[Guidance]
MidCourseCorrection=4
```

- `MidCourseCorrection=4` enables SATCOM guidance.
- `Retargetable=True` allows target changes during flight. Set it to `False` if you do not want retargeting.

The missile flies towards its stored interception point without continuous launcher guidance or a tracking radar. Its normal terminal seeker takes over when active. A moving target's position is not continuously refreshed during mid-course flight.

For retargetable missiles, use the normal in-game retargeting controls to select a new target or map position. The missile status panel shows `Link to SATCOM`.

Restart the game and launch a new missile after editing. To remove SATCOM, restore the ammunition's previous `MidCourseCorrection` value.
