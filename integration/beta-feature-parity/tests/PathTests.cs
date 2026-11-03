using System;
using System.IO;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;

public static class FakePaths
{
    public static string ModDir { [MethodImpl(MethodImplOptions.NoInlining)] get { return "/old/StreamingAssets/IdentifyExpanded"; } }
    public static string RootDir { [MethodImpl(MethodImplOptions.NoInlining)] get { return ModDir; } }
    public static string StreamingAssets { [MethodImpl(MethodImplOptions.NoInlining)] get { return Path.GetDirectoryName(ModDir); } }
}
public static class MissingPaths { public static string ModDir { get { return "old"; } } }
public static class PathTests
{
    static void Check(bool ok, string message) { if (!ok) throw new Exception(message); Console.WriteLine("PASS " + message); }
    public static void Main(string[] args)
    {
        string data = Path.GetFullPath("/tmp/sest-identify-data");
        string game = Path.GetFullPath("/tmp/game/StreamingAssets");
        Sest.IdentifyDataPaths.Plugin.ApplyPatches(typeof(FakePaths), data, game);
        Check(FakePaths.ModDir == data, "ModDir moves outside StreamingAssets");
        Check(FakePaths.RootDir == data, "RootDir follows data path");
        Check(FakePaths.StreamingAssets == game, "StreamingAssets retains its original meaning");
        Check(!FakePaths.ModDir.StartsWith(game + Path.DirectorySeparatorChar), "data root cannot create a local mod entry");
        var audio = Path.Combine(FakePaths.ModDir, "audio", "broadcast"); Directory.CreateDirectory(audio);
        Check(Directory.Exists(audio), "upstream audio creation uses the new data root");
        new Harmony(Sest.IdentifyDataPaths.Plugin.HarmonyId).UnpatchSelf();
        Check(FakePaths.ModDir == "/old/StreamingAssets/IdentifyExpanded", "unpatch restores original getter");
        bool rejected = false;
        try { Sest.IdentifyDataPaths.Plugin.ApplyPatches(typeof(MissingPaths), data, game); }
        catch (InvalidOperationException) { rejected = true; }
        Check(rejected && FakePaths.ModDir == "/old/StreamingAssets/IdentifyExpanded", "missing API is rejected without partial patches");
        var a = CustomAttributeData.GetCustomAttributes(typeof(Sest.IdentifyDataPaths.Plugin))[0];
        var before = (System.Collections.Generic.IList<CustomAttributeTypedArgument>)a.ConstructorArguments[3].Value;
        Check(a.ConstructorArguments.Count == 5 && before.Count == 1 &&
            (string)before[0].Value == "com.fmsv.identifyexpanded", "Anchor Chain before-Identify metadata retained");
        if (args.Length == 1)
        {
            Assembly real = Assembly.LoadFrom(args[0]);
            Type paths = real.GetType("IdentifyExpanded.ModPaths", true);
            Sest.IdentifyDataPaths.Plugin.ApplyPatches(paths, data, game);
            Check((string)paths.GetProperty("ModDir").GetValue(null) == data, "captured Identify Expanded ModDir getter redirects");
            Check((string)paths.GetProperty("RootDir").GetValue(null) == data, "captured Identify Expanded RootDir redirects");
            Check((string)paths.GetProperty("StreamingAssets").GetValue(null) == game, "captured Identify Expanded StreamingAssets is preserved");
            new Harmony(Sest.IdentifyDataPaths.Plugin.HarmonyId).UnpatchSelf();
        }
        Console.WriteLine("Managed path regressions passed; Unity gameplay not tested.");
    }
}
