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
    // 28 Nov: all eight author images were re-uploaded; re-keyed to the new
    // hashes after BetaApiTests ran each guard again. Every one still rejects
    // 0.9.3-261123 with the same reason.
    private static readonly Dictionary<string, string> StartupHolds = new(StringComparer.Ordinal) {
        ["7283c1c1a7ffddece9d6ce7cdc4387cfaaf588f6b23b8709fb17cbe462aa0668"] = "Saronic Corsair strike USV: ObjectsManager.removeObject hook body changed",
        ["01b7d62baaf9e7760ebfe2cac1811229feb7949cc8f93573a432b70abe527cb1"] = "Alpine scoped runtime fixes: CheckFiringConstraints hook body changed",
        ["ec57f1dc8b8ed6368deb56f29d389ba83b9db3ebd7c76c3bd2cf7d7ba9a1d384"] = "MV-75/Cheyenne II systems: FollowCamera.lateUpdate hook body changed",
        ["11029cb65839af9c9a2c85bf5f639dcbc50cf2e947e19438362eb68703c98e32"] = "EC-2 comms jamming: AI.MaintainMPA hook body changed",
        ["10d4e9fd2e4aab1abe9699e239005f28acc535677b9559d56a542536258a0288"] = "K5 Kraken contact strike: ObjectsManager.removeObject hook body changed",
        // These three guard with a fixed list of accepted Seapower-Scripts.dll
        // SHA-256 values instead of a build contract; no list has 0.9.3's
        // aae79728. One image serves both Exterior Cameras items.
        ["b34a7a1a52d75509c959bf14e8c407e1010c9017d1f40fe8e44a7fa80bfb6a62"] = "Exterior Cameras: author game-assembly guard rejects 0.9.3",
        ["219d1f801570b7fc9202ba09de15a8c3852c63b07d5345d4e294e693f8570668"] = "XQ-58 shadow contacts: author game-assembly guard rejects 0.9.3",
        ["c229173e2c5b6fed8e4fb380064f34a83eeb09dc8bd92aa54d7464dc04f51281"] = "MV-75 crew escape: author game-assembly guard rejects 0.9.3",
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
