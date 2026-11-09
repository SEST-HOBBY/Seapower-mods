using System;
using System.Collections.Generic;
using System.IO;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    // Each entry is an exact captured image whose own startup guard rejected
    // this native game. Changed author images are not matched by filename.
    private static readonly Dictionary<string, string> StartupHolds = new(StringComparer.Ordinal) {
        ["2247e384050029b671ec0673849688d735ed6e76127ec6ae3c37f63f92a33169"] = "Exterior Cameras: author camera contract rejected",
        ["262669de6ea1b320724126d111c2a43dcfe42b93866e74fb1812da2ffcfd7937"] = "K5 Kraken contact strike: ObjectsManager.removeObject hook body changed",
        ["1138dccfd42a630a17aa6e0131ce95497281265915b88d694ca5ce916ebe7b81"] = "XQ-58 shadow contacts: author game-assembly guard rejected",
        ["ab546e6b0134c5a46c8f4ad3e347537e205a9da419088a53373097c70c813df2"] = "Alpine scoped runtime fixes: CheckFiringConstraints hook body changed",
        ["5c10a344f5fba730cae191110e58dcd14d55e959f7bd67b50017765928de4f41"] = "MV-75/Cheyenne II systems: FollowCamera.lateUpdate hook body changed",
        ["f933cec252c0c2ba99192e3f14b0f333d11456005c496a49d8b532d3e3187f81"] = "EC-2 comms jamming: AI.MaintainMPA hook body changed",
        ["3c0b3b8fb9b01d16a8df2e085372ad04d95f611e6e378dedbd01e0c1d9f80aaa"] = "MV-75 crew escape: author game-assembly guard rejected",
    };

    private static bool HoldRejectedStartup(string hash, string source, Action<string> log)
    {
        if (!StartupHolds.TryGetValue(hash, out var reason)) return false;
        log("SKIPPED before CLR load: " + Path.GetFileName(source) + "; " + reason + ". Data retained; this feature awaits a verified author port.");
        return true;
    }

    // Native helper DLLs (such as DllInjector's version.dll) have a valid PE
    // header but no CLR directory. They are dependencies, not CLR plugins.
    // Malformed files still reach Cecil's existing error path.
    private static bool IsNativePeLibrary(string source)
    {
        using var stream = File.OpenRead(source);
        using var reader = new BinaryReader(stream);
        if (stream.Length < 64 || reader.ReadUInt16() != 0x5a4d) return false;
        stream.Position = 0x3c;
        int pe = reader.ReadInt32();
        if (pe < 64 || pe > stream.Length - 24) return false;
        stream.Position = pe;
        if (reader.ReadUInt32() != 0x00004550) return false;
        stream.Position = pe + 20;
        int optionalSize = reader.ReadUInt16();
        long optional = pe + 24;
        if (optionalSize < 96 || optional + optionalSize > stream.Length) return false;
        stream.Position = optional;
        int magic = reader.ReadUInt16();
        int directory = magic == 0x10b ? 96 : magic == 0x20b ? 112 : 0;
        if (directory == 0 || optionalSize < directory) return false;
        stream.Position = optional + directory - 4;
        uint count = reader.ReadUInt32();
        if (count <= 14) return true;
        if (optionalSize < directory + 15 * 8) return false;
        stream.Position = optional + directory + 14 * 8;
        uint cliAddress = reader.ReadUInt32(), cliSize = reader.ReadUInt32();
        return cliAddress == 0 && cliSize == 0;
    }
}
