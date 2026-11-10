// Bridges for the hash-pinned private AutomaticSAR image (R6). Each one keeps
// the behaviour the author's call had on stable Build 261021, built from the
// beta Build 261026 members that replaced the stable ones.
using System;
using System.Diagnostics;
using System.Reflection;
using SeaPower;

namespace AnchorChain;

public static partial class BetaCompatibilityCalls
{
    // new ConstantMach(mach, unit) on the beta is a request value; this is
    // beta ConstantMach::.ctor(float, ObjectBase) followed by ConstantMach::ToRequest.
    public static SpeedRequest AutomaticSARMachRequest(float mach, ObjectBase unused)
        => SpeedRequest.Mach(mach);

    // 'SpeedCommand.Value as ConstantSpeed' on stable. The beta keeps one
    // SpeedState per unit; its kind is SpeedState::get_Kind (the request kind).
    public static ISpeedCommand AutomaticSARConstantKnotsCommand(ISpeedCommand command)
        => command != null && command.Kind == SpeedKind.Constant ? command : null;

    // 'SpeedCommand.Value as ConstantMach' on stable; SpeedState::get_Kind == Mach.
    public static ISpeedCommand AutomaticSARConstantMachCommand(ISpeedCommand command)
        => command != null && command.Kind == SpeedKind.Mach ? command : null;

    private static class AutomaticSARSpeedCommand
    {
        // ObjectBase.SpeedCommand is a UniRx ReactiveProperty<ISpeedCommand>;
        // AnchorChain does not reference UniRx, so it is reached by reflection.
        internal static readonly PropertyInfo Property = typeof(ObjectBase).GetProperty("SpeedCommand", BindingFlags.Public | BindingFlags.Instance);
        internal static readonly PropertyInfo HasValue = Property.PropertyType.GetProperty("HasValue", BindingFlags.Public | BindingFlags.Instance);
        internal static readonly PropertyInfo Value = Property.PropertyType.GetProperty("Value", BindingFlags.Public | BindingFlags.Instance);
    }

    // The author's submarine SAR command (no cavitation cap). First the unit's
    // beta SpeedState takes the same constant-knots order through the native
    // ObjectBase::SetSpeedCommand(ref SpeedRequest), so code that reads
    // ObjectBase.Speed sees the SAR speed and the next differing player order
    // replaces the command as it does natively. Then the author's command is
    // installed exactly as stable ObjectBase::SetSpeedCommand(ISpeedCommand)
    // did: remember the old value, set Value, dispose the old one if it is
    // IDisposable (the beta SpeedState is not; the adapter checks that).
    public static void AutomaticSARSetCustomSpeedCommand(ObjectBase unit, ISpeedCommand command)
    {
        var request = SpeedRequest.Knots(command.GetDemandedSpeedInKnots(unit));
        unit.SetSpeedCommand(in request);
        object property = AutomaticSARSpeedCommand.Property.GetValue(unit);
        var previous = (bool)AutomaticSARSpeedCommand.HasValue.GetValue(property)
            ? (ISpeedCommand)AutomaticSARSpeedCommand.Value.GetValue(property) : null;
        AutomaticSARSpeedCommand.Value.SetValue(property, command);
        if (previous is IDisposable disposable) disposable.Dispose();
    }

    // Stable InterpolateGeoPosition(a, b, t) was
    //   a.GeoOffsetByDistanceOnHeading(t * a.HeadingRangeMeters(b).Item2 / 1852, a.CourseTo(b))
    // with the stable flat formulas (60 nm per degree, atan2 bearing,
    // dLat = d/60 cos h, dLon = d/60 sin h, height from a): exactly a straight
    // lat/lon line from a to b. The longitude difference is wrapped with the
    // beta's Utils::WrapAngle(double), and the result is built with the beta
    // GeoPosition::.ctor(latitude, longitude, height), which wraps longitude.
    public static GeoPosition AutomaticSARInterpolateGeoPosition(GeoPosition from, GeoPosition to, float fraction)
        => new GeoPosition(from.Latitude + fraction * (to.Latitude - from.Latitude),
            from.Longitude + fraction * Utils.WrapAngle(to.Longitude - from.Longitude), from._height);

    public static bool AutomaticSARIsGenericSpeedForwarder(StackFrame frame)
        => AutomaticSARIsGenericSpeedForwarderMethod(frame?.GetMethod());

    // True only for the beta's ObjectBase::SetSpeedCommand<T>(ref T) forwarder
    // (definition or instantiation), matched by declaring type name, name,
    // instance, void result and its single by-ref generic parameter.
    public static bool AutomaticSARIsGenericSpeedForwarderMethod(MethodBase method)
    {
        if (method is not MethodInfo info || !info.IsGenericMethod || info.IsStatic || info.Name != "SetSpeedCommand" ||
            info.DeclaringType?.FullName != "SeaPower.ObjectBase" || info.ReturnType != typeof(void)) return false;
        var definition = info.IsGenericMethodDefinition ? info : info.GetGenericMethodDefinition();
        var parameters = definition.GetParameters();
        return definition.GetGenericArguments().Length == 1 && parameters.Length == 1 && parameters[0].ParameterType.IsByRef &&
            parameters[0].ParameterType.GetElementType().IsGenericParameter;
    }
}
