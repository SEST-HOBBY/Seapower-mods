using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection.Emit;
using HarmonyLib;
using SeaPower;
using UnityEngine;

namespace Sest.UiFixes
{
    internal static class TerrainCleanup
    {
        static readonly CleanupBatchGate batch = new CleanupBatchGate();
        static AsyncOperation active;
        static GameObject driver;
        internal static void Install()
        {
            var hooks = new Harmony("io.github.sest-hobby.terrain-cleanup-batch");
            try
            {
                var target = typeof(LayeredTerrainTextureData).GetMethod("CreateTextureArray", ContactsFix.All);
                if (target == null) throw new MissingMethodException("Inspected terrain texture creation");
                hooks.Patch(target, transpiler: new HarmonyMethod(typeof(TerrainCleanup), nameof(BatchCall)));
                driver = new GameObject("SEST terrain cleanup batching");
                UnityEngine.Object.DontDestroyOnLoad(driver);
                driver.AddComponent<TerrainCleanupDriver>();
                ContactsFix.Log("Terrain cleanup: mission texture-array requests batched after 350 ms quiet or 2 s maximum; loading/menu/scene-exit cleanup retained.");
            }
            catch (Exception e)
            {
                hooks.UnpatchSelf();
                if (driver != null) UnityEngine.Object.Destroy(driver);
                driver = null;
                ContactsFix.Log("Terrain cleanup batching inactive: " + e.Message);
            }
        }
        public static IEnumerable<CodeInstruction> BatchCall(IEnumerable<CodeInstruction> input)
        {
            var call = typeof(Resources).GetMethod(nameof(Resources.UnloadUnusedAssets), Type.EmptyTypes);
            var replacement = typeof(TerrainCleanup).GetMethod(nameof(Request));
            var result = input.ToList(); int matches = 0;
            for (int i = 0; i < result.Count; i++)
                if (result[i].opcode == OpCodes.Call && Equals(result[i].operand, call))
                {
                    // This inspected caller discards the AsyncOperation. Retain
                    // every texture-build instruction and replace only call/pop.
                    if (i + 1 >= result.Count || result[i + 1].opcode != OpCodes.Pop)
                        throw new InvalidOperationException("Terrain cleanup result is no longer discarded");
                    result[i].operand = replacement;
                    result[i + 1].opcode = OpCodes.Nop; result[i + 1].operand = null;
                    matches++;
                }
            if (matches != 1) throw new InvalidOperationException("Terrain cleanup call audit: " + matches);
            return result;
        }
        public static void Request()
        {
            if (!PerformanceReview.Live || driver == null) { Resources.UnloadUnusedAssets(); return; }
            batch.Request(Time.realtimeSinceStartup);
        }
        internal static void Tick()
        {
            if (!PerformanceReview.Live) { batch.Clear(); return; }
            if (active != null && !active.isDone) return;
            int requests = batch.Take(Time.realtimeSinceStartup);
            if (requests == 0) return;
            active = Resources.UnloadUnusedAssets();
            ContactsFix.Log("Terrain cleanup: " + requests + " texture-array request(s) combined into one asset sweep.");
        }
        internal static void End()
        {
            // Native scene-exit cleanup still runs. Never read UI/native-view
            // objects or begin a new global asset walk during GameMain teardown.
            batch.Clear(); active = null;
        }
    }
    public sealed class TerrainCleanupDriver : MonoBehaviour
    {
        void Update() { TerrainCleanup.Tick(); }
    }
}
