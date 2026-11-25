// Starts admitted, hash-pinned Workshop BepInEx plugins once per process, in
// dependency order, the way a BepInEx host does: one component each on a
// persistent object. SEST's own code; it registers nothing in BepInEx's
// Chainloader.PluginInfos.
using System;
using System.Collections.Generic;
using System.Linq;
using BepInEx.Bootstrap;
using UnityEngine;

namespace AnchorChain;

internal static class WorkshopBepInRunner
{
    internal const string HostName = "SEST Workshop BepInEx plugins";

    // Pure ordering, tested without Unity. Returns the start order; every GUID
    // that cannot start gets one reason in skipped. A dependency in running
    // (already started by BepInEx or another loader) counts as met.
    internal static List<string> Order(IReadOnlyDictionary<string, string[]> after, Dictionary<string, string> skipped, ICollection<string> running)
    {
        var order = new List<string>();
        var pending = new List<string>(after.Keys.Where(g => !skipped.ContainsKey(g)).OrderBy(g => g, StringComparer.Ordinal));
        for (int budget = after.Count + 1; pending.Count != 0 && budget-- > 0;) {
            foreach (string guid in pending.ToList()) {
                string missing = after[guid].FirstOrDefault(d => !running.Contains(d) && (!after.ContainsKey(d) || skipped.ContainsKey(d)));
                if (missing != null) {
                    skipped[guid] = "needs " + missing + ", which is not admitted or did not start";
                    pending.Remove(guid);
                }
                else if (after[guid].All(d => running.Contains(d) || order.Contains(d))) { order.Add(guid); pending.Remove(guid); }
            }
        }
        foreach (string guid in pending) skipped[guid] = "dependency cycle";
        return order;
    }

    // Keel's loader or starter in this process means Keel starts these
    // plugins itself; SEST then starts none that name Keel's starter.
    internal static string KeelRunning(IEnumerable<string> loadedAssemblyNames, IEnumerable<string> pluginGuids)
    {
        string loaded = loadedAssemblyNames.FirstOrDefault(n => BetaAssemblyPolicy.ForeignLoaderAssemblies.Contains(n));
        if (loaded != null) return loaded + " is loaded";
        return pluginGuids.Contains(BetaAssemblyPolicy.KeelStubGuid) ? BetaAssemblyPolicy.KeelStubGuid + " is registered" : null;
    }

    internal static void Start(List<(WorkshopBepInPlugin Pin, Type Type)> admitted, Action<string> info, Action<string> error)
    {
        if (admitted.Count == 0) return;
        var byGuid = new Dictionary<string, (WorkshopBepInPlugin Pin, Type Type)>(StringComparer.Ordinal);
        var skipped = new Dictionary<string, string>(StringComparer.Ordinal);
        string keel = KeelRunning(AppDomain.CurrentDomain.GetAssemblies().Select(a => a.GetName().Name), Chainloader.PluginInfos.Keys);
        var running = new HashSet<string>(Chainloader.PluginInfos.Keys, StringComparer.Ordinal);
        foreach (var item in admitted) {
            string guid = item.Pin.Guid;
            // Started by BepInEx or another loader: not started twice, and met for its dependents.
            if (running.Contains(guid)) {
                info("Workshop BepInEx plugin " + guid + " is already running (started by BepInEx or another loader); SEST does not start it again.");
                continue;
            }
            if (byGuid.ContainsKey(guid)) { skipped[guid] = "found twice"; continue; }
            byGuid[guid] = item;
            if (keel != null && item.Pin.KeelStarterMarker) skipped[guid] = "R.A.T.S. Keel is running (" + keel + ") and starts it";
        }
        var order = Order(byGuid.ToDictionary(kv => kv.Key, kv => kv.Value.Pin.After, StringComparer.Ordinal), skipped, running);
        GameObject host = null;
        foreach (string guid in order) {
            var (pin, type) = byGuid[guid];
            string blocked = pin.After.FirstOrDefault(skipped.ContainsKey);
            if (blocked != null) { skipped[guid] = "needs " + blocked + ", which did not start"; continue; }
            if (host == null) {
                // Default hideFlags, as BepInEx's own manager object.
                host = new GameObject(HostName);
                UnityEngine.Object.DontDestroyOnLoad(host);
            }
            string failure = null;
            void Capture(string condition, string stack, LogType kind) { if (kind == LogType.Exception && failure == null) failure = condition; }
            Application.logMessageReceived += Capture;
            Component started = null;
            try { started = host.AddComponent(type); }      // Awake runs inside this call
            catch (Exception ex) { failure = ex.GetType().Name + ": " + ex.Message; }
            finally { Application.logMessageReceived -= Capture; }
            if (failure != null || started == null) {
                // No retries: the author's OnDestroy removes any patches it applied.
                if (started != null) UnityEngine.Object.DestroyImmediate(started);
                skipped[guid] = "failed to start: " + (failure ?? "no component");
                continue;
            }
            info("Started Workshop BepInEx plugin " + pin.Name + " " + pin.Version + " (" + guid + ", Workshop " + pin.WorkshopId + ")"
                + (pin.KeelStarterMarker ? "; started by SEST's loader, R.A.T.S. Keel is not running" : ""));
        }
        foreach (var kv in skipped.OrderBy(kv => kv.Key, StringComparer.Ordinal))
            error("Workshop BepInEx plugin " + kv.Key + " not started: " + kv.Value + ". Unit data retained.");
    }
}
