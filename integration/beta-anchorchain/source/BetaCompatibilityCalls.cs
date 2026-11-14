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

public static partial class BetaCompatibilityCalls
{
    private static readonly System.Collections.IEnumerable retiredFormationMembership = new object[0];
    public static System.Collections.IEnumerable LegacyFormationMembership(MapFormationViewModel unused)
        => retiredFormationMembership;

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

    // Identify's sender search also enumerates pooled/unassigned objects.
    // They cannot send a player broadcast; do not enter the native getter
    // until a taskforce exists. Assigned units retain the native decision.
    public static bool IsInitializedPlayerUnit(ObjectBase unit)
        => !ReferenceEquals(unit, null) && !ReferenceEquals(unit._taskforce, null) && unit.IsPlayerUnit;
}
