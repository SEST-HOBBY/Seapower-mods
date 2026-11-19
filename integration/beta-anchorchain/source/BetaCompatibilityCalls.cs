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
    // The next three members are kept only because AssemblyAdapters.cs still
    // names them in its mission-set and secondary-side rules. Neither rule
    // matches anything in Dynamic Campaign Mod 1.0.0 (6008e9c5), so no adapted
    // image calls them. Do not reuse LegacySecondaryEnemy: in 1.0.0
    // "Taskforce3" is the player's allied side, not a second enemy.

    // Use beta's mission entry API so file-layer mounts follow the mission too.
    // currentMissionFilePath now has a private setter; do not bypass it.
    public static void SetCampaignMissionPath(string path) => Globals.OpenMission(path);

    public static Taskforce SecondaryEnemyTaskforce => LegacySecondaryEnemy(Globals._enemyTaskforce);

    public static Taskforce LegacySecondaryEnemy(Taskforce primary) => primary?.Relations?.Sides
        .FirstOrDefault(side => side.IsAI && side._nameInMissionFile == "Taskforce3" &&
            !ReferenceEquals(side, primary));

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
