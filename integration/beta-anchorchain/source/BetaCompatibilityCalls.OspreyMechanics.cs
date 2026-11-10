// Bridges for the hash-pinned OspreyMechanics 1.1.45 image only (see
// AssemblyAdapters.OspreyMechanics.cs). Stable Build 261021 kept the last
// ISpeedCommand object in ObjectBase.SpeedCommand, and the plugin decides
// "I own this unit's speed" by ReferenceEquals with the ConstantSpeed it
// issued. Beta Build 261026 keeps one SpeedState per unit and applies value
// SpeedRequests to it. The plugin's orders are therefore applied through the
// native SetSpeedCommand(in SpeedRequest), and its reads hand back the order
// object it issued while the unit's SpeedState still holds exactly that
// request; otherwise they hand back what the game holds.
using System;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using SeaPower;

namespace AnchorChain;

public static partial class BetaCompatibilityCalls
{
    // The plugin's own speed order: the request it applied and the knots it
    // asked for (what its OwnsSpeed compares with ExpectedKnots). It never
    // reaches native code: SpeedCommand.Value stays the unit's SpeedState.
    public sealed class OspreyMechanicsSpeedOrder : ISpeedCommand
    {
        public readonly SpeedRequest Request;
        private readonly float knots;
        internal OspreyMechanicsSpeedOrder(SpeedRequest request, float knots) { Request = request; this.knots = knots; }
        // As SpeedState.get_Kind and get_Telegraph: read from the request.
        public SpeedKind Kind => Request.Kind;
        public int Telegraph => Request.Step;
        public bool AvoidingCavitation => false;
        public float CommandSpeedInKnots => knots;
        public float SpeedInKnots => knots;
        public float SpeedInMach => Request.Kind == SpeedKind.Mach ? Request.Value : 0f;
        public float MachLimit => 0f;
        public bool SpeedIsOverriden => false;
        public float OverridenSpeedInKnots => 0f;
        public float GetDemandedSpeedInKnots(ObjectBase objectBase) => knots;
        public float GetDemandedSpeedInMetresPerSecond(ObjectBase objectBase) => knots / 1.94384f;
        public void Update(ObjectBase objectBase) { }
        public void OverrideSpeed(float speedInKnots) { }
        public void CancelSpeedOverride() { }
    }

    // The order the plugin last applied to each unit (stable: SpeedCommand.Value
    // after its SetSpeedCommand), and the order whose native call is running.
    private static readonly ConditionalWeakTable<ObjectBase, OspreyMechanicsSpeedOrder> ospreyMechanicsApplied = new();
    [ThreadStatic] private static OspreyMechanicsSpeedOrder ospreyMechanicsInFlight;
    [ThreadStatic] private static ObjectBase ospreyMechanicsInFlightUnit;

    // Replaces newobj ConstantSpeed(float speedInKnots, ObjectBase objectBase).
    // Mirrors beta ConstantSpeed..ctor (stores the knots; objectBase unused)
    // followed by ConstantSpeed.ToRequest(): SpeedRequest.Knots(speedInKnots).
    public static ISpeedCommand OspreyMechanicsConstantSpeed(float speedInKnots, ObjectBase objectBase)
        => new OspreyMechanicsSpeedOrder(SpeedRequest.Knots(speedInKnots), speedInKnots);

    // Replaces callvirt ObjectBase.SetSpeedCommand(ISpeedCommand). Calls beta
    // ObjectBase.SetSpeedCommand(in SpeedRequest) with the order's request (an
    // equal request leaves the state unchanged, as natively), and records the
    // order as the unit's current plugin command, as stable's set_Value did.
    public static void OspreyMechanicsSetSpeedCommand(ObjectBase unit, ISpeedCommand command)
    {
        if (command is not OspreyMechanicsSpeedOrder order)
            throw new ArgumentException("OspreyMechanics speed order was not created by its beta bridge");
        var request = order.Request;
        var previous = ospreyMechanicsInFlight; var previousUnit = ospreyMechanicsInFlightUnit;
        ospreyMechanicsInFlight = order; ospreyMechanicsInFlightUnit = unit;
        try { unit.SetSpeedCommand(in request); }
        finally { ospreyMechanicsInFlight = previous; ospreyMechanicsInFlightUnit = previousUnit; }
        ospreyMechanicsApplied.Remove(unit);
        ospreyMechanicsApplied.Add(unit, order);
    }

    // Follows the plugin's native read unit.SpeedCommand.Value (beta: null, or
    // the unit's SpeedState). Returns the plugin's order while the SpeedState
    // still holds the request that order applied, else the native value.
    public static ISpeedCommand OspreyMechanicsSpeedCommand(ObjectBase unit, ISpeedCommand current)
        => OspreyMechanicsOwned(unit, current);

    // As OspreyMechanicsSpeedCommand, for the value DippingSonar keeps as
    // ResumeSpeed and re-applies on retrieval. A native SpeedState is captured
    // as an order holding its current request (SpeedState.get_Request) and its
    // SpeedState.GetDemandedSpeedInKnots, so the re-apply restores that request.
    public static ISpeedCommand OspreyMechanicsSpeedSnapshot(ObjectBase unit, ISpeedCommand current)
    {
        var owned = OspreyMechanicsOwned(unit, current);
        return owned is SpeedState state ? new OspreyMechanicsSpeedOrder(state.Request, state.GetDemandedSpeedInKnots(unit)) : owned;
    }

    // Replaces each load of the hooks' stable speedCommand argument, now
    // "ref SpeedRequest request" bound to beta SetSpeedCommand(in SpeedRequest
    // request). The plugin's own call hands back its in-flight order (stable
    // passed that object). Any other call replaced the plugin's command on
    // stable, so the plugin no longer owns the unit's speed; it gets the unit's
    // SpeedState when that holds the request (as SpeedCommand.Value does after
    // SetSpeedCommand), else an order for the incoming request.
    public static ISpeedCommand OspreyMechanicsIncomingSpeedCommand(ObjectBase unit, in SpeedRequest request)
    {
        var flight = ospreyMechanicsInFlight;
        if (flight != null && ReferenceEquals(ospreyMechanicsInFlightUnit, unit) && flight.Request.Equals(request)) return flight;
        if (unit is not null) ospreyMechanicsApplied.Remove(unit);
        var state = unit.Speed;
        if (state is not null && state.Request.Equals(request)) return state;
        return new OspreyMechanicsSpeedOrder(request, request.Kind == SpeedKind.Constant ? request.Value : 0f);
    }

    // Replaces AccessTools.Method(type, name, parameters, generics) at the two
    // SetSpeedCommand lookups. The stable lookups (by name, or with
    // [ISpeedCommand]) resolve to beta's SetSpeedCommand(in SpeedRequest
    // request); the generic SetSpeedCommand<T>(in T order) forwards to it, so
    // that one target sees every speed order. Anything else passes through.
    public static MethodInfo OspreyMechanicsMethod(Type type, string name, Type[] parameters, Type[] generics)
    {
        if (type != null && type.FullName == "SeaPower.ObjectBase" && type.Assembly.GetName().Name == "Seapower-Scripts" &&
            name == "SetSpeedCommand" && generics == null &&
            (parameters == null || (parameters.Length == 1 && parameters[0]?.FullName == "SeaPower.ISpeedCommand"))) {
            var matches = type.GetMethods(BindingFlags.DeclaredOnly | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                .Where(m => m.Name == "SetSpeedCommand" && !m.IsGenericMethodDefinition && m.ReturnType == typeof(void) &&
                    m.GetParameters().Length == 1 && m.GetParameters()[0].Name == "request" && m.GetParameters()[0].ParameterType.IsByRef &&
                    m.GetParameters()[0].ParameterType.GetElementType().FullName == "SeaPower.SpeedRequest")
                .ToArray();
            if (matches.Length != 1) throw new InvalidOperationException("Inspected beta ObjectBase.SetSpeedCommand(in SpeedRequest) changed");
            return matches[0];
        }
        return AccessTools.Method(type, name, parameters, generics);
    }

    private static ISpeedCommand OspreyMechanicsOwned(ObjectBase unit, ISpeedCommand current)
        => current is SpeedState state && unit is not null && ospreyMechanicsApplied.TryGetValue(unit, out var mine) &&
            state.Request.Equals(mine.Request) ? mine : current;
}
