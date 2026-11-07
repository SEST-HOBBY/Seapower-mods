// Bridges for the hash-pinned private BetterTacMap image (AssemblyAdapters.
// BetterTacMap.cs). Each reproduces native beta Build 261026 behaviour.
using System;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using SeaPower;
using SeapowerUI;

namespace AnchorChain;

public static partial class BetaCompatibilityCalls
{
    // The internal members these bridges need, found structurally (declaring
    // type, name, parameter types). Kept in their own holder so a failed lookup
    // fails only these bridges, never BetaCompatibilityCalls' shared statics.
    private static class BetterTacMapNative
    {
        private const BindingFlags Instance = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
        internal static readonly Type Entry = typeof(GizmoLayerManager).GetNestedTypes(BindingFlags.Public | BindingFlags.NonPublic)
            .Single(t => t.FullName == "SeapowerUI.GizmoLayerManager+Entry" && t.IsValueType);
        internal static readonly ConstructorInfo EntryCtor = Entry.GetConstructors(Instance)
            .Single(c => Parameters(c, "System.Int32", "System.String", "System.Boolean"));
        internal static readonly ConstructorInfo LayerCtor = typeof(MapLayer).GetConstructors(Instance)
            .Single(c => c.IsAssembly && Parameters(c, "SeapowerUI.MapDisplayState", "SeapowerUI.GizmoLayerManager+Entry&", "System.Boolean"));
        internal static readonly AccessTools.FieldRef<MapUnitViewModel, MapLabelCandidate> Label =
            AccessTools.FieldRefAccess<MapUnitViewModel, MapLabelCandidate>(Field(typeof(MapUnitViewModel), "Label", typeof(MapLabelCandidate)));
        internal static readonly AccessTools.FieldRef<MapUnitViewModel, bool> Line3Initialized =
            AccessTools.FieldRefAccess<MapUnitViewModel, bool>(Field(typeof(MapUnitViewModel), "_line3Initialized", typeof(bool)));
        internal static readonly AccessTools.FieldRef<MapUnitViewModel, string> ContactInfoLine3 =
            AccessTools.FieldRefAccess<MapUnitViewModel, string>(Field(typeof(MapUnitViewModel), "_contactInfoLine3", typeof(string)));
        internal static readonly AccessTools.FieldRef<MapLabelCandidate, bool> Realized =
            AccessTools.FieldRefAccess<MapLabelCandidate, bool>(Field(typeof(MapLabelCandidate), "Realized", typeof(bool)));
        internal static readonly AccessTools.FieldRef<MapLabelCandidate, int> Prefix =
            AccessTools.FieldRefAccess<MapLabelCandidate, int>(Field(typeof(MapLabelCandidate), "Prefix", typeof(int)));
        internal static readonly AccessTools.FieldRef<MapLabelCandidate, MapLabelLine> HeadLine =
            AccessTools.FieldRefAccess<MapLabelCandidate, MapLabelLine>(Field(typeof(MapLabelCandidate), "HeadLine", typeof(MapLabelLine)));
        internal static readonly ConditionalWeakTable<MapUnitViewModel, Due> Next = new ConditionalWeakTable<MapUnitViewModel, Due>();

        internal sealed class Due { internal double At = double.NegativeInfinity; }

        private static bool Parameters(MethodBase method, params string[] names)
            => method.GetParameters().Select(p => p.ParameterType.FullName).SequenceEqual(names);

        private static FieldInfo Field(Type owner, string name, Type type)
        {
            var field = owner.GetField(name, Instance | BindingFlags.DeclaredOnly);
            if (field == null || field.IsStatic || field.FieldType != type)
                throw new MissingFieldException("Inspected beta " + owner.Name + "." + name + " changed");
            return field;
        }
    }

    // Replaces the author's `newobj MapLayer::.ctor(int layerNumber, string
    // name, bool visibleInMenu)` (stable rid 4335, public, _visible left at
    // true). Mirrors native MapDisplayState..ctor(bool) IL_0079-008c, which
    // builds each Tactical layer as new MapLayer(this, ref entry, visible)
    // from an Entry(Number, Name, InMenu); visible is true, as stable left it.
    // The author's Register then sets Visible itself.
    public static MapLayer BetterTacMapNewLayer(int layerNumber, string name, bool visibleInMenu, MapDisplayState owner)
    {
        if (owner == null) throw new ArgumentNullException(nameof(owner));
        object entry = BetterTacMapNative.EntryCtor.Invoke(new object[] { layerNumber, name, visibleInMenu });
        return (MapLayer)BetterTacMapNative.LayerCtor.Invoke(new object[] { owner, entry, true });
    }

    // Native MapUnitViewModel.UpdateContactInfoLine3 (beta rid 5756) calls
    // set_ContactInfoLine3, where the author's label Prefix runs, only when
    // its own inputs change (IL_00c1-010a, IL_0131, IL_0284) and the rebuilt
    // text differs from _contactInfoLine3 (IL_03da-03eb, BuilderEquals).
    // Stable called the setter on every Update. Every half second, while line
    // 3 is shown, this clears both fields: the next Update then treats the
    // inputs as changed, BuilderEquals(builder, null) is false, the setter
    // and the author's Prefix run, and BumpContentVersion re-measures the
    // label. The raw field writes raise no PropertyChanged.
    public static void BetterTacMapRefreshLine3(MapUnitViewModel view)
        => BetterTacMapRefreshLine3At(view, GameTime.unscaledTime);

    public const double BetterTacMapLine3Seconds = 0.5;

    public static bool BetterTacMapRefreshLine3At(MapUnitViewModel view, double now)
    {
        if (view == null || !BetterTacMapLine3Shown(view)) return false;
        var due = BetterTacMapNative.Next.GetOrCreateValue(view);
        if (now < due.At) return false;
        due.At = now + BetterTacMapLine3Seconds;
        BetterTacMapNative.Line3Initialized(view) = false;
        BetterTacMapNative.ContactInfoLine3(view) = null;
        return true;
    }

    // Native UpdateContactInfoLine3 IL_0000-0030: line 3 is shown when the
    // label is realized and its prefix covers it (index 2, or 3 with a head line).
    public static bool BetterTacMapLine3Shown(MapUnitViewModel view)
    {
        var label = BetterTacMapNative.Label(view);
        if (label == null) return false;
        int line = (BetterTacMapNative.HeadLine(label) != null ? 1 : 0) + 2;
        return BetterTacMapNative.Realized(label) && BetterTacMapNative.Prefix(label) > line;
    }
}
