using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using AnchorChain;

static class LoaderTests
{
    sealed class Mod : IAnchorChainMod
    {
        internal int Calls;
        internal Action Action;
        public void TriggerEntryPoint() { Calls++; if (Action != null) Action(); }
    }
    static int checks;
    static void Check(bool ok, string why) { checks++; if (!ok) throw new Exception(why); }
    static void Main()
    {
        var events = new List<string>(); var errors = new List<string>();
        var failed = new Mod { Action = () => { throw new Exception("synthetic partial-install failure"); } };
        var blocked = new Mod();
        var root = new Mod { Action = () => events.Add("root") };
        var next = new Mod { Action = () => events.Add("next") };
        var last = new Mod { Action = () => events.Add("last") };
        var graph = new Dictionary<string, (ACPlugin, IAnchorChainMod)> {
            ["failed"] = (new ACPlugin("failed", "failure", "1.0.0", new[] { "blocked" }), failed),
            ["blocked"] = (new ACPlugin("blocked", "blocked", "1.0.0", null, new[] { "failed" }), blocked),
            ["root"] = (new ACPlugin("root", "root", "1.0.0", new[] { "next" }), root),
            ["next"] = (new ACPlugin("next", "next", "1.0.0", new[] { "last" }, new[] { "root" }), next),
            ["last"] = (new ACPlugin("last", "last", "1.0.0", null, new[] { "next" }), last),
        };
        var runner = typeof(AnchorChainLoader).GetMethod("RunPending", BindingFlags.Static | BindingFlags.NonPublic);
        Check(runner != null, "actual fork scheduler exists");
        runner.Invoke(null, new object[] { graph, (Action<string>)(_ => { }), (Action<string>)(s => errors.Add(s)) });
        Check(failed.Calls == 1, "failed plugin is attempted exactly once");
        Check(blocked.Calls == 0, "dependent of failed plugin is never invoked");
        Check(root.Calls == 1 && next.Calls == 1 && last.Calls == 1, "unrelated dependency chain completes once");
        Check(String.Join(",", events) == "root,next,last", "dependency order is preserved");
        Check(errors.Count == 1 && errors[0].Contains("skipped for this run"), "failure is reported once");
        var impossible = new Mod();
        graph = new Dictionary<string, (ACPlugin, IAnchorChainMod)> {
            ["root"] = (new ACPlugin("root", "root", "1.0.0", new[] { "wait" }), new Mod()),
            ["wait"] = (new ACPlugin("wait", "wait", "1.0.0", null, new[] { "missing" }), impossible),
        };
        errors.Clear(); runner.Invoke(null, new object[] { graph, (Action<string>)(_ => { }), (Action<string>)(s => errors.Add(s)) });
        Check(impossible.Calls == 0, "unmet dependency is never invoked");
        Check(errors.Count == 1 && errors[0].Contains("no further progress"), "unresolvable plan terminates instead of spinning");
        // Mod Manager ticks, as Anchor Chain 1.2.0 get_SelectedDirectories and FindFile.
        var select = typeof(AnchorChainLoader).GetMethod("SelectedDirectories", BindingFlags.Static | BindingFlags.NonPublic);
        var find = typeof(AnchorChainLoader).GetMethod("FindIn", BindingFlags.Static | BindingFlags.NonPublic);
        Check(select != null && find != null, "fork Mod Manager selection exists");
        string temp = Path.Combine(Path.GetTempPath(), "sest-loader-" + Guid.NewGuid().ToString("N"));
        var workshop = Directory.CreateDirectory(Path.Combine(temp, "3790594162"));
        var second = Directory.CreateDirectory(Path.Combine(temp, "3774572038"));
        var local = Directory.CreateDirectory(Path.Combine(temp, "IdentifyExpanded"));
        var configs = Directory.CreateDirectory(Path.Combine(temp, "ACConfigs"));
        try {
            var rows = new List<(DirectoryInfo, bool)> { (local, false), (workshop, true),
                (new DirectoryInfo(Path.Combine(temp, "unsubscribed")), true), (configs, false), (null, true), (second, true) };
            var picked = (List<DirectoryInfo>)select.Invoke(null, new object[] { rows });
            Check(picked.Count == 2 && picked[0] == workshop && picked[1] == second,
                "only ticked Mod Manager folders that exist are scanned, in Mod Manager order");
            File.WriteAllText(Path.Combine(configs.FullName, "a_user.ini"), "");
            File.WriteAllText(Path.Combine(local.FullName, "b.ini"), "");
            File.WriteAllText(Path.Combine(second.FullName, "c.ini"), "");
            File.WriteAllText(Path.Combine(configs.FullName, "c.ini"), "");
            Check((string)find.Invoke(null, new object[] { picked, configs.FullName, "a_user.ini" }) == Path.Combine(configs.FullName, "a_user.ini"),
                "user configs in unticked ACConfigs are still found, not reset each launch");
            Check(find.Invoke(null, new object[] { picked, configs.FullName, "b.ini" }) == null, "an unticked mod's config is not used");
            Check((string)find.Invoke(null, new object[] { picked, configs.FullName, "c.ini" }) == Path.Combine(second.FullName, "c.ini"),
                "ticked folders are searched before ACConfigs, as 1.2.0");
        } finally { Directory.Delete(temp, true); }
        Check(typeof(AnchorChainLoader).Assembly.GetName().Version == new Version(1, 1, 0, 0), "AnchorChain assembly identity is preserved");
        Console.WriteLine("Bounded loader regressions passed: " + checks + " assertions against the compiled fork scheduler; no Unity execution.");
    }
}
