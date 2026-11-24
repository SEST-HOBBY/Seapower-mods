using System;
using System.Collections.Generic;
using System.IO;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    // Each entry is an exact captured image whose own startup guard rejected
    // this native game. Changed author images are not matched by filename.
    // R15: re-keyed to the 17 November 0.9.3 capture. Each reason is the
    // author's own verdict on 0.9.3-261116: BetaApiTests runs every
    // build-contract guard and reads every game-hash list against the
    // captured game, and requires this table to match. The Alpine-family
    // images were re-uploaded on 16 November; their guards still reject
    // this game. Saronic Corsair and K5 Kraken are the images R14 held.
    private static readonly Dictionary<string, string> StartupHolds = new(StringComparer.Ordinal) {
        ["1a3eb996201106c800133aa3ed884e7642c43fb58ea29fcd0c8d98390a739459"] = "Saronic Corsair strike USV: ObjectsManager.removeObject hook body changed",
        ["70b291d7697919eb8165ef719b7f19d230b027722600d2a618064c21053d17a0"] = "Alpine scoped runtime fixes: CheckFiringConstraints hook body changed",
        ["8166b925a7090a993011fcb1899f9c46730615884cc0d8c6275b8bf61061fbc4"] = "MV-75/Cheyenne II systems: FollowCamera.lateUpdate hook body changed",
        ["0cbf7b8068971ec00b0448bcdf524e2c4364ee5eedbf6e9269a092a48b7f125a"] = "EC-2 comms jamming: AI.MaintainMPA hook body changed",
        ["da8a45c111325fa8b97a6a20d72d8a7ccf77799f1478171f0c73f8df563c593a"] = "K5 Kraken contact strike: ObjectsManager.removeObject hook body changed",
        // These three guard with a fixed list of accepted Seapower-Scripts.dll
        // SHA-256 values instead of a build contract; no list has 0.9.3's
        // aae79728. One image serves both Exterior Cameras items.
        ["2b2e02910fe511fdb457e8b68edef3df7e80ce1061781e1c63782cc52abbe0f1"] = "Exterior Cameras: author game-assembly guard rejects 0.9.3",
        ["744b9ac5cb1bc42cbd604f47baabb79e2a71c6b2e257bb0df3620f249cc9988c"] = "XQ-58 shadow contacts: author game-assembly guard rejects 0.9.3",
        ["9374053f4e56693d1cd4d021dd0a7f6252144befefcc8213f1dfbdab11513e9c"] = "MV-75 crew escape: author game-assembly guard rejects 0.9.3",
        // R16: R.A.T.S. Keel (3835527459, 24 Nov images) is a takeover mod
        // loader that would replace SEST's bounded loader. Held by design,
        // not awaiting a port. The Echidna and Ghost Shark plugins that name
        // Keel's starter are started by SEST's loader (WorkshopBepInPolicy.cs).
        ["986531887e4be588aa3816821217fff9e7c9de7b305c65248e4d2fe2d535c987"] = "R.A.T.S. Keel loader: a takeover mod loader, not admitted under SEST",
        ["1fb4ec5de9b97a4671ce6dc9c8e339b3406c202f25e828499c5bcb796f51b621"] = "R.A.T.S. Keel preloader patcher: a takeover mod loader, not admitted under SEST",
        ["57d9465cefe20e09adc35a9929600cb8c6b4b5b46ac12a1baf69478043925d0a"] = "R.A.T.S. Keel starter stub: a takeover mod loader, not admitted under SEST",
    };

    // Holds that are a SEST decision rather than an author's own verdict.
    private static readonly HashSet<string> ByDesignHolds = new(StringComparer.Ordinal) {
        "986531887e4be588aa3816821217fff9e7c9de7b305c65248e4d2fe2d535c987",
        "1fb4ec5de9b97a4671ce6dc9c8e339b3406c202f25e828499c5bcb796f51b621",
        "57d9465cefe20e09adc35a9929600cb8c6b4b5b46ac12a1baf69478043925d0a",
    };

    private static bool HoldRejectedStartup(string hash, string source, Action<string> log)
    {
        if (!StartupHolds.TryGetValue(hash, out var reason)) return false;
        log("SKIPPED before CLR load: " + Path.GetFileName(source) + "; " + reason + (ByDesignHolds.Contains(hash)
            ? ". Data retained; held by design, SEST changes no file of it." : ". Data retained; this feature awaits a verified author port."));
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
