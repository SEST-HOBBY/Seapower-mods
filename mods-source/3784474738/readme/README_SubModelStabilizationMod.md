# Stabilized Ship SubModels

Keep a radar platform, sensor mount or flight-deck element steady while the ship moves.

## Configure a vessel INI

Add the settings to the section of the SubModel you want to stabilize. That section must also be listed under `[Submodels]`.

```ini
[Submodels]
SubModel3=RadarPlatform

[RadarPlatform]
Object=radar_base
IsStabilized=SystemActive
Stabilization=Pitch,Roll
StabilizedSystem=SensorSystem3
```

Replace `radar_base` and `SensorSystem3` with the actual model and system on your ship. Keep existing SubModel entries and use an unused number. If the file uses `NumberOfSubModels`, update its count too.

## Choose when and how to stabilize

| Key | Options |
|---|---|
| `IsStabilized` | `SystemActive`: while the linked system is on. `FlightOps`: during an aircraft launch or landing. |
| `Stabilization` | `Pitch`, `Roll`, `Yaw`, or a comma-separated combination. |
| `StabilizedSystem` | The ship's system reference, such as `SensorSystem3`. Needed for `SystemActive` only. |

`Pitch,Roll` keeps the platform level. Add `Yaw` to hold its heading when stabilization activates. Normal animations, such as radar rotation, continue.

For a flight-deck SubModel, use:

```ini
IsStabilized=FlightOps
Stabilization=Pitch,Roll
```

FlightOps applies only during an actual launch or landing, not whenever aircraft are aboard. Use the exact spelling `Stabilization`.

Restart the game and check the ship in a fresh mission. See [example_stabilization.ini](example_stabilization.ini) for a complete fragment.
