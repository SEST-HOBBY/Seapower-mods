// Small ABI bridges used only by the hash-pinned private images. No native or
// author assembly is patched on disk. These calls retain native beta behavior.
using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using System.Linq;
using HarmonyLib;
using SeaPower;
using SeapowerUI.ViewModels;
using SeapowerUI;

namespace AnchorChain;

public static class BetaCompatibilityCalls
{
    public static MapUnitViewModel VehicleViewModel(Vehicle vehicle)
        => FindVehicleViewModel(vehicle, Globals._mainGameViewModel?.Map?.MapKnownUnits?.AllUnits)
            ?? FindVehicleViewModel(vehicle, Globals._mainGameViewModel?.SecondMap?.MapKnownUnits?.AllUnits);

    public static MapUnitViewModel FindVehicleViewModel(Vehicle vehicle, IEnumerable<MapUnitViewModel> units)
        => vehicle == null ? null : units?.FirstOrDefault(view => ReferenceEquals(view.Unit, vehicle));

    private static class DecoyStyle
    {
        internal static readonly FieldInfo Color = AccessTools.Field(typeof(WeaponContactViewModel), "_attackColor");
        internal static readonly object Allied = Enum.Parse(Color.FieldType, "WeaponVectorAllied");
    }

    // The captured author call always supplies WeaponVectorAlliedColor. Beta's
    // renderer stores a palette key instead of a fixed Noesis colour value.
    public static void SetDecoyLineColor(WeaponContactViewModel contact, Noesis.Color unused)
        => DecoyStyle.Color.SetValue(contact, DecoyStyle.Allied);

    // Stable's ignorePath argument was ineffective (its comparison was thrown
    // away). Preserve its actual first-match lookup using all active beta layers.
    public static string GetLegacyFile(FileManager manager, string path, string ignorePath)
        => manager.GetFile(path, LayerKind.All);

    // The sole old campaign speed call builds ConstantSpeed(float,ObjectBase).
    // Beta replaces that class/interface pair with a value-type SpeedRequest.
    public static SpeedRequest ConstantSpeedRequest(float knots, ObjectBase unused)
        => SpeedRequest.Knots(knots);

    public static void SetSpeedRequest(ObjectBase unit, SpeedRequest request)
        => unit.SetSpeedCommand(in request);

    // Use beta's mission entry API so file-layer mounts follow the mission too.
    // currentMissionFilePath now has a private setter; do not bypass it.
    public static void SetCampaignMissionPath(string path) => Globals.OpenMission(path);

    public static Taskforce SecondaryEnemyTaskforce => LegacySecondaryEnemy(Globals._enemyTaskforce);

    public static Taskforce LegacySecondaryEnemy(Taskforce primary) => primary?.Relations?.Sides
        .FirstOrDefault(side => side.IsAI && side._nameInMissionFile == "Taskforce3" &&
            !ReferenceEquals(side, primary));

    public static PropertyInfo CampaignProperty(Type type, string name)
        => type == typeof(Globals) && name == "_secondEnemyTaskforce"
            ? typeof(BetaCompatibilityCalls).GetProperty(nameof(SecondaryEnemyTaskforce))
            : AccessTools.Property(type, name);

    public static MethodInfo CampaignMethod(Type type, string name, Type[] parameters, Type[] generics)
    {
        if (type == typeof(ObjectBase) && name == "SetAttackAtWaypointTask" && parameters?.Length == 10)
            parameters = parameters.Concat(new[] { typeof(string), typeof(string) }).ToArray();
        return AccessTools.Method(type, name, parameters, generics);
    }

    // A not-yet-assigned/pooled unit is ineligible for an enemy hail. Returning
    // true preserves the caller's existing skip branch before IsEnemyUnit runs.
    public static bool SkipEnemyHailCandidate(ObjectBase unit)
        => ReferenceEquals(unit, null) || ReferenceEquals(unit._taskforce, null) || unit.IsPlayerUnit;

    // Beta's constructor branches to _sources.Add(this), rather than directly
    // to ret. Reuse that real merge label and keep the new registration epilogue.
    // The original transpiler and its one-argument validation remain intact.
    public static CodeInstruction FindDecoyContactExit(List<CodeInstruction> body, Predicate<CodeInstruction> unused)
    {
        FieldInfo sources = AccessTools.Field(typeof(WeaponContactViewModel), "_sources");
        CodeInstruction exit = null;
        for (int i = 0; i + 5 < body.Count; i++) {
            if (body[i].opcode != OpCodes.Ldarg_0 || body[i+1].opcode != OpCodes.Ldfld ||
                !Equals(body[i+1].operand, sources) || body[i+2].opcode != OpCodes.Ldarg_0 ||
                body[i+3].operand is not MethodInfo add || add.Name != "Add" || add.ReturnType != typeof(bool) ||
                body[i+4].opcode != OpCodes.Pop || body[i+5].opcode != OpCodes.Ret) continue;
            if (exit != null) throw new InvalidOperationException("Ambiguous beta contact registration epilogue");
            exit = body[i];
        }
        if (exit == null || exit.labels.Count == 0)
            throw new InvalidOperationException("Inspected beta contact registration epilogue/label changed");
        return exit;
    }
}
