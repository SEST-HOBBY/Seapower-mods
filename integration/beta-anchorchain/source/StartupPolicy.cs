using System;
using System.Collections.Generic;
using System.IO;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    // Each entry is an exact captured image whose own startup guard rejected
    // this native game. Changed author images are not matched by filename.
    // R14: re-keyed to the 14 November 0.9.2 capture. Each reason is the
    // author's own build-contract verdict on 0.9.2 (BetaApiTests runs every
    // such guard against the captured game and requires this table to match).
    private static readonly Dictionary<string, string> StartupHolds = new(StringComparer.Ordinal) {
        ["1a3eb996201106c800133aa3ed884e7642c43fb58ea29fcd0c8d98390a739459"] = "Saronic Corsair strike USV: ObjectsManager.removeObject hook body changed",
        ["3ef5efb4a68b70df72997083b648769ec7c7691a7893a28478fe031a0d9dc3ee"] = "Alpine scoped runtime fixes: CheckFiringConstraints hook body changed",
        ["5e969d6e790ac3f59cd011a7acd0ce916c5f3fee31da0a0bf818efbc2b2b59a7"] = "MV-75/Cheyenne II systems: FollowCamera.lateUpdate hook body changed",
        ["feb9a01d5fa0bd4916d634414c8ab31e37d2b1d980d9ca4fbfe4854c01b4df76"] = "EC-2 comms jamming: AI.MaintainMPA hook body changed",
        ["da8a45c111325fa8b97a6a20d72d8a7ccf77799f1478171f0c73f8df563c593a"] = "K5 Kraken contact strike: ObjectsManager.removeObject hook body changed",
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
