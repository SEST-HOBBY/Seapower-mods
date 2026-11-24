// Fixed-wing bridges for the J-36 systems (AssemblyAdapters.J36Systems.cs)
// and Osprey Mechanics (AssemblyAdapters.OspreyMechanics.cs) images on
// 0.9.3-261123. The private-field accessors live in their own nested class
// so that a failed lookup can fail only these bridges, never the type
// initializer every other bridge shares.
using HarmonyLib;
using SeaPower;

namespace AnchorChain;

public static partial class BetaCompatibilityCalls
{
    private static class FixedWingFields
    {
        internal static readonly AccessTools.FieldRef<FixedWingFlightPhysics, AircraftPerfData> Perf =
            AccessTools.FieldRefAccess<FixedWingFlightPhysics, AircraftPerfData>("_perf");
        internal static readonly AccessTools.FieldRef<FixedWingFlightPhysics, float> Thrust =
            AccessTools.FieldRefAccess<FixedWingFlightPhysics, float>("_physThrust");
        // MotionController.Position is protected; the native step reads it from inside.
        internal static readonly System.Func<MotionController, UnityEngine.Vector3> Position =
            AccessTools.MethodDelegate<System.Func<MotionController, UnityEngine.Vector3>>(
                AccessTools.PropertyGetter(typeof(MotionController), "Position"));
    }

    // J-36: what FieldInfo.GetValue(__instance) returned for the field
    // _aircraftParameters before it became a property.
    public static object FixedWingParameters(object physics) => ((FixedWingFlightPhysics)physics)._aircraftParameters;

    // J-36: the drag power the author's _dragPower lookup read, boxed as
    // FieldInfo.GetValue boxed it. 261123 keeps it in _perf.DragPower.
    public static object FixedWingDragPower(object physics) => FixedWingFields.Perf((FixedWingFlightPhysics)physics).DragPower;

    // J-36: the author's FieldInfo.SetValue(__instance, (object)dragPower).
    public static void SetFixedWingDragPower(object physics, object value)
        => FixedWingFields.Perf((FixedWingFlightPhysics)physics).DragPower = (float)value;

    // Osprey hover sub-step fuel burn, as FixedWingFlightPhysics.FixedUpdateBody
    // burns: FuelFlow(_perf, speed, altitude, _physThrust), then
    // BurnFuelAtRate and UpdateFuelConsumptionThrottled, only while there is
    // fuel. The speed is the author's: distance / step = Max(speed, 48.872334).
    // BurnFuelAtRate burns rate * GameTime.fixedDeltaTime; the hover splits a
    // fixed step into sub-steps of at most 0.05 s, so each sub-step burns its
    // own share, step / fixedDeltaTime, as the author's distance burn did.
    public static void OspreyHoverFuel(Aircraft aircraft, float distance, float step, FixedWingFlightPhysics physics)
        => OspreyHoverBurn(aircraft, distance, step, physics, GameTime.fixedDeltaTime);

    // The same with the game step passed in (the managed tests run it without
    // the Unity player, which GameTime's static constructor needs).
    public static void OspreyHoverBurn(Aircraft aircraft, float distance, float step, FixedWingFlightPhysics physics, float dt)
    {
        if (ReferenceEquals(aircraft, null)) throw new System.NullReferenceException();
        if (!(dt > 0f) || !(step > 0f) || !(aircraft.Ap._currentFuelMass > 0f)) return;
        float speed = distance / step;
        float altitude = FixedWingFields.Position(physics).y * 67.2000656f;
        float rate = AircraftPerformance.FuelFlow(in FixedWingFields.Perf(physics), speed, altitude, FixedWingFields.Thrust(physics));
        aircraft.BurnFuelAtRate(rate * (step / dt), speed);
        aircraft.UpdateFuelConsumptionThrottled();
    }
}
