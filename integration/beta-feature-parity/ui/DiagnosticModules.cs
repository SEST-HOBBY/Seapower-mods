namespace Sest.UiFixes
{
    internal static class DiagnosticModules
    {
        // Hashes from the 27 October 11:13 Brisbane capture. Timing hooks only.
        // Each entry is { assembly name, inspected hash, ... }.
        internal static readonly string[][] Known = {
            new[] { "CombatCosts", "8f7195ff1540d1901446b3783789c84e1f76bebe943da7606afd85f9dd3d78bc" },
            new[] { "ContactLog", "a1b8b450df0933df61984651fe2b19138acd605aa4b526bbfc23565d8295015e" },
            new[] { "EnhancedUIMod", "37b9301de2f6d19cd5bd7e16f5042aca6eb80979313b3c84a3a26be106ec6f95" },
            new[] { "IdentifyExpanded", "9f0ec630e9d7659082bdce61743a87895de14f1903a44c68395f8f158af8afd7" },
            new[] { "SEST.MenuBackground", "9dfd561db256aaa2455ff0039783b46cfbaf113b641c97f0815121d3a4502515" },
            new[] { "SEST.RuntimeFixes", BuildPins.RuntimeSha256 },
            // Pop-Out 1.3.0: update methods are Rats.Shared.ModHost.Update (calls PopOutScreen.Tick) and PopOutScreen.LateUpdate.
            new[] { "SeaPowerPopOut", ContactsSurfaceFix.PopOut13Hash },
            new[] { "SeaPowerSquadPanel", "eff3fa12904a0c61e8fa9f1d10d94e9fa67b0aa76b27c5399808e7ecdd961f4c" },
            new[] { "SeaPowerTopo", "32b00107bbdeb705c6bb91045b0bb5396f5815724a239b8c8f78026e1382b206" },
            new[] { "UiWorkerProbe", "b87d7a1b2b97b2f717be8303ebf4c9fca29d730715bb6283ecbe4a2df594b7b7" },
        };
    }
}
