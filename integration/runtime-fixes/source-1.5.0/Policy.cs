using System;
using System.IO;

namespace Sest.RuntimeFixes
{
    internal static class Policy
    {
        internal const float LookAheadNm = 1.10f; // Includes native samples through 1.08 nm (about 2 km).
        internal const float LandClearanceFeet = 500f;

        internal static bool Finite(float value) { return !float.IsNaN(value) && !float.IsInfinity(value); }

        internal static bool IsMst(string name)
        {
            if (String.IsNullOrWhiteSpace(name)) return false;
            string id = Path.GetFileNameWithoutExtension(name.Replace('\\', '/'));
            return String.Equals(id, "usn_rgm-109e5a", StringComparison.OrdinalIgnoreCase) ||
                String.Equals(id, "usn_ugm-109e5a", StringComparison.OrdinalIgnoreCase);
        }

        internal static bool CruiseStage(string stage)
        {
            switch (stage)
            {
                case "ToBearing": case "MaintainHeight": case "MoveToLoftAlt": case "MaintainLoftAlt":
                case "MoveToSeaSkimming": case "MaintainSeaSkimming": case "MoveToFinalFlightAlt":
                case "MaintainFinalFlightAlt": case "AlignSensorToTarget": return true;
                default: return false;
            }
        }

        internal static float Altitude(float native, float highestLand, float clearance)
        {
            if (!Finite(native) || !Finite(highestLand) || !Finite(clearance) || highestLand <= 0 || clearance <= 0)
                return native;
            float floor = highestLand + clearance;
            return Finite(floor) ? Math.Max(native, floor) : native;
        }

        internal static bool PackEnabled(string[] lines, string folder)
        {
            string section = "";
            foreach (string raw in lines)
            {
                string line = raw.Trim();
                if (line.StartsWith("[")) { section = line; continue; }
                if (!String.Equals(section, "[LoadOrder]", StringComparison.OrdinalIgnoreCase)) continue;
                int eq = line.IndexOf('=');
                if (eq < 0 || !line.Substring(0, eq).EndsWith("Directory", StringComparison.OrdinalIgnoreCase)) continue;
                string[] parts = line.Substring(eq + 1).Split(',');
                if (parts.Length == 2 && String.Equals(parts[0].Trim(), folder, StringComparison.OrdinalIgnoreCase))
                {
                    bool enabled;
                    return Boolean.TryParse(parts[1].Trim(), out enabled) && enabled;
                }
            }
            return false;
        }

        internal static bool OptionEnabled(string[] lines, string option)
        {
            string section = "";
            foreach (string raw in lines)
            {
                string line = raw.Trim();
                if (line.StartsWith("[")) { section = line; continue; }
                int eq = line.IndexOf('=');
                if (!String.Equals(section, "[Runtime]", StringComparison.OrdinalIgnoreCase) || eq < 0) continue;
                if (String.Equals(line.Substring(0, eq).Trim(), option, StringComparison.OrdinalIgnoreCase))
                    return line.Substring(eq + 1).Trim() == "1";
            }
            return false;
        }

        internal static string TextOption(string[] lines,string option,string fallback)
        {
            string section="";
            foreach(string raw in lines)
            {
                string line=raw.Trim();if(line.StartsWith("[")){section=line;continue;}
                int eq=line.IndexOf('=');
                if(String.Equals(section,"[Runtime]",StringComparison.OrdinalIgnoreCase) && eq>=0 &&
                    String.Equals(line.Substring(0,eq).Trim(),option,StringComparison.OrdinalIgnoreCase))return line.Substring(eq+1).Trim();
            }
            return fallback;
        }
    }
}
