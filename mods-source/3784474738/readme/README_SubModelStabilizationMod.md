# Vessel SubModel Stabilization

Small AnchorChain extension for Sea Power that stabilizes individual SubModel roots
against selected vessel rotations. The configuration is placed directly in the
respective SubModel section of the vessel INI.

## Configuration

The three keys are named exactly:

```ini
IsStabilized=
Stabilization=
StabilizedSystem=
```

Direct SubModel definitions:

```ini
[SubModel3]
Object=radar_base
IsStabilized=SystemActive
Stabilzation=Pitch,Roll
StabilizedSystem=SensorSystem3

[SubModel7]
Object=flightdeck_platform
IsStabilized=FlightOps
Stabilzation=Pitch,Roll

[SubModel8]
Object=eo_base
IsStabilized=SystemActive
Stabilzation=Pitch,Yaw,Roll
StabilizedSystem=SensorSystem6
```

`Pitch`, `Yaw`, and `Roll` can be specified in any order, separated by commas.
The order has no effect; unknown tokens are ignored with a warning. Full
stabilization is written explicitly as `Pitch,Yaw,Roll`.

## Activation

- `IsStabilized=FlightOps` is active only while the runtime FlightDeck states
  `LaunchInProgress` or `LandingInProgress` are active. Merely having a flight
  deck or embarked aircraft is not sufficient.
- `IsStabilized=SystemActive` resolves `StabilizedSystem` to the vessel's actual
  system instance and uses its generic `IsOn` state. The code is not restricted
  to radar system classes.