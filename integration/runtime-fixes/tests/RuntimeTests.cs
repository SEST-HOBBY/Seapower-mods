// Test-only native API stand-ins. This file and AnchorChain.cs never ship
// inside a game mod. Tests exercise the actual plugin's bind and callbacks.
// The stand-ins take the shapes verify_native_api.py checks on Sea Power
// 0.8.7: nested FlightStage and CrewSkill, a read-only snapshot, and the
// readValue overloads that the exact (string, string, bool, bool) one beats.
// The campaign-cost stand-ins take the shapes verify_native_api.py checks:
// a nested Ammunition.Type, a non-public snapshot-row struct and rules class,
// the 4-argument openIniFile beside a 3-argument decoy, and the game's own
// row parser and weapon-report reader, which the plugin calls, not copies.
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using Sest.RuntimeFixes;

namespace UnityEngine
{
    public struct Vector3 { public float x, y, z; }
    public class Transform { public Vector3 eulerAngles { get; set; } }
    public class Component { public Transform transform { get; set; } = new Transform(); }
    public class Behaviour : Component { }
    public class MonoBehaviour : Behaviour { }
    public static class Debug { public static void Log(object value) { Console.WriteLine(value); } }
}

namespace SeaPower
{
    public struct GeoPosition { public float Latitude; }
    public class ObjectBase : UnityEngine.MonoBehaviour
    {
        public enum CrewSkill { Green, Regular, Veterans }
        public enum ObjectType { Other, Vessel, Submarine, Aircraft, Helicopter, LandUnit, Biologic, Missile }
        public GeoPosition _geoPosition { get; set; }
    }
    public class AmmunitionParameters { public string _ammunitionFileName; public bool _terrainFollowFlight = true; }
    public class WeaponBase : ObjectBase
    {
        public enum FlightStage { None, DropFromAircraft, Launch, SurfaceWaterEntry, GoToSurface, ToBearing,
            MaintainHeight, MoveToLoftAlt, MaintainLoftAlt, MoveToSeaSkimming, MaintainSeaSkimming,
            MoveToFinalFlightAlt, MaintainFinalFlightAlt, AlignSensorToTarget, TerminalApproach, SelfDestruct = 18 }
        public AmmunitionParameters _ap;
        public FlightStage _flightStage { get; set; } = FlightStage.MaintainLoftAlt;
    }
    public class Missile : WeaponBase { }
    public static class Utils
    {
        public static float heightInFeetToUnity(float feet) { return feet * .00453571f; }
        // Merged catalogs by "basePath/fileName"; a missing one opens empty, as with the tracker disabled.
        public static readonly Dictionary<string, IniHandler> Virtual = new Dictionary<string, IniHandler>();
        public static readonly Dictionary<string, IniHandler> Files = new Dictionary<string, IniHandler>(StringComparer.OrdinalIgnoreCase);
        public static readonly List<string> Opened = new List<string>();
        public static string Throw;
        public static IniHandler openVirtualIniFile(string basePath, string fileName, string folderName, bool checkCached)
        {
            if (checkCached || fileName != folderName) throw new Exception("catalog not opened as the tracker opens it");
            if (Throw == basePath + "/" + fileName) throw new InvalidOperationException("test catalog failure");
            IniHandler ini;
            return Virtual.TryGetValue(basePath + "/" + fileName, out ini) ? ini : new IniHandler();
        }
        public static IniHandler openIniFile(string rootPath, string name, bool logErrors, bool useCaching)
        {
            if (logErrors || !useCaching) throw new Exception("unit file not opened as the tracker opens it");
            Opened.Add(rootPath + name);
            if (Throw == rootPath + name) throw new IOException("test unit file failure");
            IniHandler ini;
            return Files.TryGetValue(rootPath + name, out ini) ? ini : null;
        }
        public static IniHandler openIniFile(string fullPath, bool logErrors, bool useCaching) { throw new Exception("3-argument openIniFile bound"); }
    }
    public class Ammunition
    {
        public enum Type { Unknown, Projectile, Missile, RBU, ASROC, Torpedo, Noisemaker, Chaff, Bomb, AerialRocket,
            None, Sonobuoy, MLRS, Cluster, MOSS, Paratrooper, Fueltank, AirDepthCharge }
    }
    public class WeaponReportAmmoData
    {
        public string AmmoRef { get; set; }
        public Ammunition.Type AmmoType { get; set; }
        public int Launched { get; set; }
        public int ProjectileFired { get; set; }
        public int CiwsRoundsFired { get; set; }
    }
    // Test format: AmmoRef,Type,Launched,ProjectileFired,CiwsRoundsFired per launching unit, joined by ';'.
    public class TaskforceWeaponReport
    {
        public readonly List<WeaponReportAmmoData> Units = new List<WeaponReportAmmoData>();
        public Dictionary<string, WeaponReportAmmoData> BuildTaskforceTotals()
        {
            var totals = new Dictionary<string, WeaponReportAmmoData>(StringComparer.OrdinalIgnoreCase);
            foreach (WeaponReportAmmoData unit in Units)
            {
                WeaponReportAmmoData total;
                if (!totals.TryGetValue(unit.AmmoRef, out total))
                    totals.Add(unit.AmmoRef, total = new WeaponReportAmmoData { AmmoRef = unit.AmmoRef, AmmoType = unit.AmmoType });
                total.Launched += unit.Launched; total.ProjectileFired += unit.ProjectileFired; total.CiwsRoundsFired += unit.CiwsRoundsFired;
            }
            return totals;
        }
        public static TaskforceWeaponReport Parse(string raw)
        {
            if (String.IsNullOrWhiteSpace(raw)) return null;
            var report = new TaskforceWeaponReport();
            foreach (string unit in raw.Split(';'))
            {
                string[] f = unit.Split(',');
                Ammunition.Type type;
                if (f.Length != 5 || !Enum.TryParse(f[1], out type)) return null;
                report.Units.Add(new WeaponReportAmmoData { AmmoRef = f[0], AmmoType = type, Launched = Int32.Parse(f[2]),
                    ProjectileFired = Int32.Parse(f[3]), CiwsRoundsFired = Int32.Parse(f[4]) });
            }
            return report;
        }
    }
    public static class TerrainUtils
    {
        public static float Height, LastDistance, LastHeading, LastLatitude;
        public static bool Throw;
        public static float GetSafeAltitudeOverSurface(ObjectBase objBase, float targetAltitude,
            float minAltOverSea, bool cantStayAtAltitude, bool isWeapon) { return targetAltitude; }
        public static float CrudeGetHighestTerrainHeightAhead(GeoPosition geoPosition, float heading,
            float distanceLimit, bool isCalledFromJob)
        {
            if (Throw) throw new InvalidOperationException("test terrain failure");
            LastDistance = distanceLimit; LastHeading = heading; LastLatitude = geoPosition.Latitude;
            return Height;
        }
    }
    public class LinearCampaignMission { public int _index; }
    public class IniHandler
    {
        public HashSet<string> Sections = new HashSet<string>();
        public HashSet<string> Destroyed = new HashSet<string>();
        // Case-sensitive on purpose: the plugin must match sections and keys ignoring case itself.
        public Dictionary<string, Dictionary<string, string>> Data { get; private set; } = new Dictionary<string, Dictionary<string, string>>();
        public bool doesSectionExist(string section) { return Sections.Contains(section) || Data.ContainsKey(section); }
        public bool doesKeyExist(string sectionName, string key)
        {
            Dictionary<string, string> section;
            return Data.TryGetValue(sectionName, out section) && section.ContainsKey(key);
        }
        public void Set(string section, string key, string value)
        {
            Dictionary<string, string> keys;
            if (!Data.TryGetValue(section, out keys)) Data.Add(section, keys = new Dictionary<string, string>());
            keys[key] = value;
        }
        public static IniHandler Parse(string text)
        {
            var ini = new IniHandler();
            string section = "";
            foreach (string line in text.Split('\n'))
            {
                if (line.StartsWith("[")) { section = line.Trim('[', ']'); ini.Data[section] = new Dictionary<string, string>(); }
                else if (line.Contains("=")) ini.Set(section, line.Substring(0, line.IndexOf('=')), line.Substring(line.IndexOf('=') + 1));
            }
            return ini;
        }
        public bool readValue(string sectionName, string key, bool defaultValue, bool performLogging)
        {
            return key == "IsDestroyed" ? Destroyed.Contains(sectionName) : defaultValue;
        }
        public T readValue<T>(string sectionName, string key, T defaultValue, bool performLogging) { throw new Exception("generic readValue bound"); }
        public bool? readValue(string sectionName, string key, bool? defaultValue, bool performLogging) { throw new Exception("nullable readValue bound"); }
        public string readValue(string sectionName, string key, string defaultValue, bool performLogging)
        {
            Dictionary<string, string> section;
            string value;
            return Data.TryGetValue(sectionName, out section) && section.TryGetValue(key, out value) ? value : defaultValue;
        }
    }
}

namespace SeapowerUI.ViewModels
{
    public class LinearCampaignTaskForceBuilderRosterItem
    {
        public string InstanceId { get; set; }
        public string UnitFolder { get; set; } = "vessels";
        public string UnitType { get; set; }
        public string Category { get; set; } = "Frigate";
        public string VariantReference { get; set; } = "Variant1";
        public SeaPower.ObjectBase.CrewSkill CrewSkill { get; set; } = SeaPower.ObjectBase.CrewSkill.Veterans;
    }
    public class LinearCampaignTaskForceSnapshot
    {
        public readonly List<LinearCampaignTaskForceBuilderRosterItem> Source = new List<LinearCampaignTaskForceBuilderRosterItem>();
        public ReadOnlyCollection<LinearCampaignTaskForceBuilderRosterItem> Items { get { return Source.AsReadOnly(); } }
    }
    public static class LinearCampaignTaskForceSaveManager
    {
        public static LinearCampaignTaskForceSnapshot Launch = new LinearCampaignTaskForceSnapshot();
        public static string LastSection;
        static string MissionLaunchSection(int index) { return "TaskForceMode_Mission" + index + "_Launch"; }
        static string MissionLaunchUnitPrefix(int index) { return "TaskForceMode_Mission" + index + "_Launch_Unit"; }
        static LinearCampaignTaskForceSnapshot ReadSnapshot(SeaPower.IniHandler state, string section, string prefix)
        {
            LastSection = section;
            if (!state.doesSectionExist(section) || !prefix.EndsWith("_Launch_Unit")) throw new Exception("wrong snapshot");
            return Launch;
        }
    }
    public class LinearCampaignTaskForceDebriefUnitRow
    {
        public string InstanceId { get; private set; }
        public string IniRef { get; private set; }
        public string IniFolder { get; private set; }
        public string VariantReference { get; private set; }
        public bool IsDestroyed { get; private set; }
        public SeaPower.ObjectBase.CrewSkill CrewSkill { get; private set; }
        public LinearCampaignTaskForceDebriefUnitRow(string instanceId, string iniRef, string iniFolder, string category,
            string variantReference, string damageState, bool isDestroyed, bool isFlagship, SeaPower.ObjectBase.CrewSkill crewSkill, int quantity)
        {
            InstanceId = instanceId; IniRef = iniRef; IniFolder = iniFolder; VariantReference = variantReference;
            IsDestroyed = isDestroyed; CrewSkill = crewSkill;
        }
    }
    public class LinearCampaignTaskForceDebriefSummaryRow
    {
        public string Label { get; private set; }
        public string Value { get; private set; }
        public bool IsPositive { get; private set; }
        public bool IsNegative { get; private set; }
        public LinearCampaignTaskForceDebriefSummaryRow(string label, string value, bool isPositive, bool isNegative)
        {
            Label = label; Value = value; IsPositive = isPositive; IsNegative = isNegative;
        }
    }
    internal struct LinearCampaignTaskForceDebriefRegisterSnapshotRow
    {
        public string IniRef, Folder, ObjectType;
        public int Count;
        public bool IsDestroyed, IsDamaged;
        public int VariantIndex;
    }
    internal static class LinearCampaignTaskForceModeRules
    {
        public static SeaPower.IniHandler State;
        public static SeaPower.IniHandler OpenCampaignStateIni() { return State; }
    }
    public class LinearCampaignTaskForceDebriefViewModel
    {
        public ObservableCollection<LinearCampaignTaskForceDebriefUnitRow> UnitRows { get; private set; } =
            new ObservableCollection<LinearCampaignTaskForceDebriefUnitRow>();
        public ObservableCollection<LinearCampaignTaskForceDebriefSummaryRow> SummaryRows { get; private set; } =
            new ObservableCollection<LinearCampaignTaskForceDebriefSummaryRow>();
        void ReadUnitRows(SeaPower.IniHandler state, SeaPower.LinearCampaignMission mission) { }
        static IEnumerable<LinearCampaignTaskForceDebriefUnitRow> SortDebriefUnitRows(IEnumerable<LinearCampaignTaskForceDebriefUnitRow> rows)
        {
            return rows.OrderBy(r => r.IniFolder).ThenBy(r => r.InstanceId).ToList();
        }
        // As on 0.8.7: Clear() first, then the native summary rows.
        internal void Load(SeaPower.LinearCampaignMission mission)
        {
            SummaryRows.Clear();
            foreach (string label in new[] { "Mission Outcome", "Completed", "Mission Score", "Survivors Rescued" })
                SummaryRows.Add(new LinearCampaignTaskForceDebriefSummaryRow(label, "native", false, false));
        }
        public static bool HasDebriefSnapshot(SeaPower.IniHandler campaignStateIni, int missionIndex)
        {
            return campaignStateIni != null && missionIndex > 0 && campaignStateIni.doesSectionExist(GetDebriefSectionName(missionIndex));
        }
        static string GetDebriefSectionName(int missionIndex)
        {
            return "Mission_" + missionIndex.ToString(CultureInfo.InvariantCulture) + "_TaskForceDebrief";
        }
        // The game's own row format: IniRef|Folder|ObjectType|Count|IsDestroyed|IsDamaged|VariantIndex, joined by '~'.
        static bool TryParseRegisterRows(string rawValue, ref List<LinearCampaignTaskForceDebriefRegisterSnapshotRow> rows)
        {
            rows = new List<LinearCampaignTaskForceDebriefRegisterSnapshotRow>();
            if (String.IsNullOrWhiteSpace(rawValue)) return false;
            foreach (string raw in rawValue.Split(new[] { '~' }, StringSplitOptions.RemoveEmptyEntries))
            {
                string[] f = raw.Split('|');
                int count;
                bool destroyed, damaged;
                if (f.Length < 6 || String.IsNullOrWhiteSpace(f[0])) continue;
                rows.Add(new LinearCampaignTaskForceDebriefRegisterSnapshotRow { IniRef = f[0], Folder = f[1], ObjectType = f[2],
                    Count = Int32.TryParse(f[3], out count) ? Math.Max(1, count) : 1,
                    IsDestroyed = Boolean.TryParse(f[4], out destroyed) && destroyed,
                    IsDamaged = Boolean.TryParse(f[5], out damaged) && damaged, VariantIndex = 0 });
            }
            return rows.Count > 0;
        }
        // As on 0.8.7: a blank, missing or unparsable report all come back null.
        static bool TryReadWeaponReports(SeaPower.IniHandler campaignStateIni, int missionIndex, ref SeaPower.TaskforceWeaponReport playerReport,
            ref SeaPower.TaskforceWeaponReport enemyReport, ref SeaPower.TaskforceWeaponReport neutralReport)
        {
            playerReport = enemyReport = neutralReport = null;
            if (campaignStateIni == null || missionIndex < 1) return false;
            string section = GetDebriefSectionName(missionIndex);
            playerReport = SeaPower.TaskforceWeaponReport.Parse(campaignStateIni.readValue(section, "PlayerWeaponReport", "", false));
            enemyReport = SeaPower.TaskforceWeaponReport.Parse(campaignStateIni.readValue(section, "EnemyWeaponReport", "", false));
            neutralReport = SeaPower.TaskforceWeaponReport.Parse(campaignStateIni.readValue(section, "NeutralWeaponReport", "", false));
            return playerReport != null || enemyReport != null || neutralReport != null;
        }
    }
}

static class RuntimeTests
{
    static int checks;
    static void Check(bool value, string name) { checks++; if (!value) throw new Exception(name); }
    static void Equal(float a, float b, string name) { Check(Math.Abs(a-b) < .0001f, name); }

    static void Main(string[] args)
    {
        Check(Policy.PackEnabled(new[] { "[LoadOrder]", "Mod1Directory=SEST_Integration,True" }, "SEST_Integration"), "enabled pack");
        Check(!Policy.PackEnabled(new[] { "[LoadOrder]", "Mod1Directory=SEST_Integration,False" }, "SEST_Integration"), "disabled pack");
        Check(!Policy.PackEnabled(new[] { "[Other]", "Mod1Directory=SEST_Integration,True" }, "SEST_Integration"), "other section");
        Check(!Policy.PackEnabled(new[] { "[LoadOrder]", "Mod1Directory=SEST_Integration,True" }, "3812461539"), "different owning folder");
        Check(!Policy.OptionEnabled(new[] { "[Runtime]", "TerrainClearance=0" }, "TerrainClearance"), "feature off");
        Check(Policy.OptionEnabled(new[] { "[Runtime]", "TerrainClearance=1" }, "TerrainClearance"), "feature on");
        Check(Policy.IsMst("ammunition\\usn_ugm-109e5a.ini"), "UGM alias");
        Check(!Policy.IsMst("usn_rgm-109c"), "other Tomahawk");
        Check(!Policy.IsMst("other_usn_rgm-109e5a"), "no substring match");
        Check(!Policy.CruiseStage("TerminalApproach"), "terminal excluded");
        Check(!Policy.CruiseStage("Launch"), "boost excluded");
        Check(!Policy.CruiseStage("Unknown"), "unknown stage excluded");
        Equal(Policy.Altitude(2, -1, 3), 2, "sea unchanged");
        Equal(Policy.Altitude(2, 0, 3), 2, "zero terrain unchanged");
        Equal(Policy.Altitude(10, 4, 3), 10, "native higher retained");
        Check(float.IsNaN(Policy.Altitude(float.NaN, 4, 3)), "NaN native retained");
        Equal(Policy.Altitude(2, float.NaN, 3), 2, "NaN terrain ignored");
        Equal(Policy.Altitude(2, 4, float.PositiveInfinity), 2, "invalid clearance ignored");

        Assembly game = Assembly.GetExecutingAssembly();
        TerrainClearance.Bind(game);
        var missile = new SeaPower.Missile { _ap = new SeaPower.AmmunitionParameters { _ammunitionFileName = "usn_rgm-109e5a" },
            _geoPosition = new SeaPower.GeoPosition { Latitude = -1.2f } };
        missile.transform.eulerAngles = new UnityEngine.Vector3 { y = 123f };
        SeaPower.TerrainUtils.Height = 8;
        float result = .1f;
        TerrainClearance.Postfix(missile, true, ref result);
        Equal(result, 8 + SeaPower.Utils.heightInFeetToUnity(500), "land altitude raised");
        Equal(SeaPower.TerrainUtils.LastDistance, 1.1f, "native longer lookahead");
        Equal(SeaPower.TerrainUtils.LastHeading, 123f, "uses actual heading");
        Equal(SeaPower.TerrainUtils.LastLatitude, -1.2f, "uses actual position");
        SeaPower.TerrainUtils.Height = -3; result = .07f;
        TerrainClearance.Postfix(missile, true, ref result); Equal(result, .07f, "open sea profile retained");
        SeaPower.TerrainUtils.Height = 8; result = .1f;
        missile._flightStage = SeaPower.WeaponBase.FlightStage.TerminalApproach;
        TerrainClearance.Postfix(missile, true, ref result); Equal(result, .1f, "terminal descent retained");
        missile._flightStage = SeaPower.WeaponBase.FlightStage.MaintainHeight;
        missile._ap = new SeaPower.AmmunitionParameters { _ammunitionFileName = "usn_aim-260" };
        TerrainClearance.Postfix(missile, true, ref result); Equal(result, .1f, "other weapons retained");
        missile._ap = new SeaPower.AmmunitionParameters { _ammunitionFileName = "usn_ugm-109e5a", _terrainFollowFlight = false };
        TerrainClearance.Postfix(missile, true, ref result); Equal(result, .1f, "non terrain mode retained");
        missile._ap._terrainFollowFlight = true;
        TerrainClearance.Postfix(missile, false, ref result); Equal(result, .1f, "non weapon call retained");
        TerrainClearance.Postfix(new SeaPower.ObjectBase(), true, ref result); Equal(result, .1f, "aircraft calls excluded");
        SeaPower.TerrainUtils.Throw = true;
        TerrainClearance.Postfix(missile, true, ref result); Equal(result, .1f, "runtime failure retained native result");
        SeaPower.TerrainUtils.Throw = false;
        TerrainClearance.Postfix(missile, true, ref result); Equal(result, .1f, "failure disables own correction");

        TaskForceDebrief.Bind(game);
        var state = new SeaPower.IniHandler();
        state.Sections.Add("TaskForceMode_Mission11_Launch");
        var snapshot = SeapowerUI.ViewModels.LinearCampaignTaskForceSaveManager.Launch;
        snapshot.Source.Add(new SeapowerUI.ViewModels.LinearCampaignTaskForceBuilderRosterItem { InstanceId = "arafura", UnitType = "ran_opv_arafura" });
        snapshot.Source.Add(new SeapowerUI.ViewModels.LinearCampaignTaskForceBuilderRosterItem { InstanceId = "warramunga", UnitType = "ran_ffh_anzac", VariantReference = "Variant3" });
        snapshot.Source.Add(new SeapowerUI.ViewModels.LinearCampaignTaskForceBuilderRosterItem { InstanceId = "survivor", UnitType = "ran_ddg_hobart" });
        snapshot.Source.Add(new SeapowerUI.ViewModels.LinearCampaignTaskForceBuilderRosterItem { InstanceId = "air", UnitType = "ran_mh-60r", UnitFolder = "aircraft" });
        snapshot.Source.Add(new SeapowerUI.ViewModels.LinearCampaignTaskForceBuilderRosterItem { InstanceId = "notdeployed", UnitType = "ran_ffh_anzac" });
        foreach (string id in new[] { "arafura", "warramunga", "air" })
        { state.Sections.Add("Mission_11_" + id); state.Destroyed.Add("Mission_11_" + id); }
        state.Sections.Add("Mission_11_survivor");
        var model = new SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel();
        var mission = new SeaPower.LinearCampaignMission { _index = 11 };
        TaskForceDebrief.Postfix(model, state, mission);
        Check(model.UnitRows.Count == 2, "exactly two missing lost ships restored");
        Check(model.UnitRows.All(r => r.IsDestroyed), "restored rows are lost");
        Check(model.UnitRows.Single(r => r.InstanceId == "warramunga").VariantReference == "Variant3", "hull identity preserved");
        Check(model.UnitRows.All(r => r.CrewSkill == SeaPower.ObjectBase.CrewSkill.Veterans), "proficiency preserved");
        TaskForceDebrief.Postfix(model, state, mission);
        Check(model.UnitRows.Count == 2, "no duplicate loss rows");
        Check(snapshot.Items.Count == 5 && state.Destroyed.Count == 3, "save and roster unmodified");
        var other = new SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel();
        TaskForceDebrief.Postfix(other, state, new SeaPower.LinearCampaignMission { _index = 10 });
        Check(other.UnitRows.Count == 0, "no nearest mission fallback");
        var listed = new SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel();
        listed.UnitRows.Add(new SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefUnitRow("ARAFURA", "ran_opv_arafura", "vessels",
            "Patrol", "Variant1", "Lost", true, false, SeaPower.ObjectBase.CrewSkill.Regular, 1));
        TaskForceDebrief.Postfix(listed, state, mission);
        Check(listed.UnitRows.Count == 2 && listed.UnitRows.Count(r => r.InstanceId.ToLowerInvariant() == "arafura") == 1,
            "a loss the native rows already list is not repeated");
        CampaignCostTests(game, args);
        Console.WriteLine("Runtime regressions passed: " + checks + " assertions (mocked native API; PC gameplay still required)");
    }

    // ---- Campaign combat costs (CampaignCosts.cs) ----
    static SeaPower.IniHandler Ini(string text) { return SeaPower.IniHandler.Parse(text); }

    static Dictionary<string, Dictionary<string, string>> Pairs(Dictionary<string, Dictionary<string, string>> ini, string section, string cell)
    {
        if (cell == "-") return ini;
        var keys = new Dictionary<string, string>();
        foreach (string pair in cell.Split(';')) keys[pair.Substring(0, pair.IndexOf('='))] = pair.Substring(pair.IndexOf('=') + 1);
        ini[section] = keys;
        return ini;
    }

    static IEnumerable<string[]> Table(string path, int columns)
    {
        bool header = true;
        foreach (string line in File.ReadAllLines(path))
        {
            if (line.Length == 0 || line.StartsWith("#")) continue;
            string[] cells = line.Split('\t');
            if (cells.Length != columns) throw new Exception("table row shape: " + line);
            if (header) { header = false; continue; }
            yield return cells;
        }
    }

    static string Cell(string value) { return value == "-" ? null : value == "(blank)" ? "" : value; }

    static Dictionary<string, Dictionary<string, string>> Copy(Dictionary<string, Dictionary<string, string>> data)
    {
        return data.ToDictionary(s => s.Key, s => new Dictionary<string, string>(s.Value));
    }

    static bool Same(Dictionary<string, Dictionary<string, string>> a, Dictionary<string, Dictionary<string, string>> b)
    {
        return a.Count == b.Count && a.All(s => b.ContainsKey(s.Key) && s.Value.Count == b[s.Key].Count &&
            s.Value.All(k => { string v; return b[s.Key].TryGetValue(k.Key, out v) && v == k.Value; }));
    }

    static int Occurrences(StringWriter log, string fragment)
    {
        string text = log.ToString();
        int count = 0;
        for (int at = text.IndexOf(fragment, StringComparison.Ordinal); at >= 0; at = text.IndexOf(fragment, at + 1, StringComparison.Ordinal)) count++;
        return count;
    }

    static List<string> Shown(SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel model, SeaPower.LinearCampaignMission mission)
    {
        model.Load(mission);
        CampaignCosts.Postfix(model, mission);
        return model.SummaryRows.Select(r => r.Label + " = " + r.Value).ToList();
    }

    static SeaPower.IniHandler CampaignState()
    {
        var state = new SeaPower.IniHandler();
        const string m1 = "Mission_1_TaskForceDebrief", m2 = "Mission_2_TaskForceDebrief", m3 = "Mission_3_TaskForceDebrief";
        state.Set(m1, "MissionResult", "Victory");
        // Two launchers of one round in different letter case; a gun with CIWS bursts already inside ProjectileFired.
        state.Set(m1, "PlayerWeaponReport", "USN_RIM-66M,Missile,2,0,0;usn_rim-66m,Missile,1,0,0;usn_mk45_he,Projectile,0,10,4;" +
            "chaff_rr,Chaff,6,0,0;usn_mk46,Torpedo,1,0,0;sono_dicass,Sonobuoy,2,0,0;ignored_round,Missile,5,0,0;" +
            "bad_cat,Missile,5,0,0;mlrs_round,MLRS,4,0,0");
        state.Set(m1, "EnemyWeaponReport", "");  // what the game writes for a side that fired nothing
        state.Set(m1, "KillRows", "enemy_dd|vessels|Vessel|1|True|False|0~enemy_dd|vessels|Vessel|1|False|True|0~" +
            "enemy_jet|aircraft|Aircraft|2|True|False|0~enemy_heli|aircraft|Helicopter|1|True|False|0~sam_site|land_units|LandUnit|1|True|False|0");
        state.Set(m1, "LossRows", "usn_ffg|vessels|Vessel|1|True|False|0~usn_sh-60b|aircraft|Helicopter|1|True|False|0~" +
            "unknown_ship|vessels|Vessel|1|True|False|0");
        state.Set(m2, "EnemyWeaponReport", "not a report");  // no PlayerWeaponReport key at all
        state.Set(m2, "KillRows", "enemy_sub|submarines|Submarine|1|True|False|0");
        state.Set(m3, "PlayerWeaponReport", "usn_rim-66m,Missile,2,0,0");
        state.Set(m3, "EnemyWeaponReport", "enemy_ssm,Missile,4,0,0");
        // Not missions: a child row section, and a name GetDebriefSectionName never gives.
        state.Set("Mission_3_TaskForceDebrief_Kill_1", "KillRows", "enemy_sub|submarines|Submarine|5|True|False|0");
        state.Set("Mission_03_TaskForceDebrief", "KillRows", "enemy_sub|submarines|Submarine|5|True|False|0");
        state.Set("Mission_4_TaskForceMode", "KillRows", "enemy_sub|submarines|Submarine|5|True|False|0");
        return state;
    }

    static void Catalogs(string config)
    {
        var virtualFiles = SeaPower.Utils.Virtual;
        virtualFiles["systems/weaponcosts"] = Ini("[Costs]\nOverrideInline=False\n[usn_rim-66m]\nCategory=SAM\nWeaponCosts=400000\n" +
            "CurrentYearCost=2100000\n[usn_mk45_he]\nWeaponCosts=1000\nCurrentYearCost=1500\n[usn_mk46]\nCategory=Torpedo\n" +
            "[chaff_rr]\nWeaponCosts=50\n[sono_dicass]\nCategory=ASW\n[ignored_round]\nCategory=ignore\nWeaponCosts=999\n" +
            "[bad_cat]\nCategory=SAM!\nWeaponCosts=999\n[enemy_ssm]\nWeaponCosts=  1500000  \n[mlrs_round]\nCategory=\nWeaponCosts=100");
        virtualFiles["systems/vesselcosts"] = Ini("[Costs]\nOverrideInline=False\n[usn_ffg]\nVesselCosts=500000000\n" +
            "CurrentYearCost=1000000000\n[ENEMY_SUB]\nVesselCosts=300000000");
        virtualFiles["systems/aircraftcosts"] = Ini("[Costs]\nOverrideInline=False\n[usn_sh-60b]\nAircraftCosts=20000000\n" +
            "CurrentYearCost=40000000\n[enemy_jet]\nAircraftCosts=30000000");
        virtualFiles["systems/combatcosts/config"] = Ini(config);
        SeaPower.Utils.Files["/ammunition/usn_mk45_he.ini"] = Ini("[General]\nType=Projectile\nWeaponCosts=1200");
        SeaPower.Utils.Files["/vessels/enemy_dd.ini"] = Ini("[General]\nVesselCosts=700000000");
        SeaPower.Utils.Files["/aircraft/enemy_heli.ini"] = Ini("[General]\nAircraftCosts=10000000");
    }

    static void CampaignCostTests(Assembly game, string[] args)
    {
        // Shared with tools/tests/test_combat_costs.py (costs.field_origin, costs.price, costs.weapon_excluded).
        int precedence = 0, exclusion = 0;
        foreach (string[] c in Table(args[0], 8))
        {
            var catalog = Pairs(Pairs(new Dictionary<string, Dictionary<string, string>>(), "Costs", c[1]), "round", c[2]);
            string selected = CostPolicy.ResolveField(Pairs(new Dictionary<string, Dictionary<string, string>>(), "General", c[3]),
                catalog, "Round", c[4], c[5]);
            decimal? price = CostPolicy.ParsePrice(selected);
            Check(selected == Cell(c[6]) && (c[7] == "-" || (c[7] == "unknown" ? !price.HasValue :
                price == Decimal.Parse(c[7], CultureInfo.InvariantCulture))), "precedence: " + c[0]);
            precedence++;
        }
        foreach (string[] c in Table(args[1], 4))
        {
            Check(CostPolicy.WeaponExcluded(Cell(c[1]), c[2]) == (c[3] == "excluded"), "exclusion: " + c[0]);
            exclusion++;
        }
        Check(precedence >= 40 && exclusion >= 30, "both shared tables read");
        Check(CostPolicy.ParsePrice(" 5") == null && CostPolicy.ParsePrice(null) == null, "ParsePrice takes trimmed values only");

        string[][] money = { new[] { "0", "$0" }, new[] { "950", "$950" }, new[] { "999.4", "$999" }, new[] { "999.5", "$1.00K" },
            new[] { "1000", "$1.00K" }, new[] { "12345", "$12.3K" }, new[] { "99950", "$100K" }, new[] { "4120000", "$4.12M" },
            new[] { "4125000", "$4.13M" }, new[] { "41200000", "$41.2M" }, new[] { "412000000", "$412M" },
            new[] { "999999999", "$1.00B" }, new[] { "1840000000", "$1.84B" }, new[] { "2500000000000", "$2.50T" } };
        foreach (string[] m in money)
            Check(CostPolicy.Money(Decimal.Parse(m[0], CultureInfo.InvariantCulture)) == m[1], "money " + m[0] + " -> " + m[1]);

        var listFalse = Ini("[Costs]\nUseCurrentYearCosts=False").Data;
        var current = CostPolicy.Apply(listFalse, Ini("[Costs]\nUseCurrentYearCosts=True\nCurrentYear=2026-08").Data);
        Check(CostPolicy.UseCurrentYear(current) && CostPolicy.Basis(current) == "2026-08" && listFalse["Costs"]["UseCurrentYearCosts"] == "False",
            "config.ini UseCurrentYearCosts=True replaces the catalog's, on a copy");
        Check(CostPolicy.Basis(CostPolicy.Apply(Ini("[Costs]\nUseCurrentYearCosts=True").Data, Ini("[Costs]\nOther=1").Data)) == "current" &&
            CostPolicy.Basis(CostPolicy.Apply(listFalse, Ini("[Costs]\nUseCurrentYearCosts=yes").Data)) == "IOC" &&
            CostPolicy.Basis(CostPolicy.Apply(null, null)) == "IOC", "an absent config keeps the catalog's mode; invalid means IOC");

        var postfix = typeof(CampaignCosts).GetMethod("Postfix", BindingFlags.NonPublic | BindingFlags.Static);
        Check(String.Join(" ", postfix.GetParameters().Select(p => p.Name)) == "__instance __0", "Harmony argument names");
        Check(CampaignCosts.Bind(game).Name == "Load", "binds the debrief's Load");

        TextWriter stdout = Console.Out;
        var log = new StringWriter();
        Console.SetOut(log);
        try
        {
            Catalogs("[Costs]\nUseCurrentYearCosts=False\nCurrentYear=2026-08");
            var state = CampaignState();
            SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules.State = state;
            var before = Copy(state.Data);
            var model = new SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel();
            var m1 = new SeaPower.LinearCampaignMission { _index = 1 };
            List<string> rows = Shown(model, m1);
            string[] native = { "Mission Outcome = native", "Completed = native", "Mission Score = native", "Survivors Rescued = native" };
            string campaign = "Combat Cost: Campaign = Player $522M + ? | Enemy $1.08B + ? (3 missions)";
            string basis = "Combat Cost: Basis = USD, IOC prices; stores aboard and land units excluded";
            string gaps = "Campaign: 3 rounds, 1 ship, weapons not recorded for 1 mission";
            Check(rows.Count == 10 && rows.Take(4).SequenceEqual(native), "native rows first, in order, then six");
            Check(rows[4] == "Combat Cost: Weapons = Player $1.21M + ? | Enemy $0",
                "weapons: launched + fired, any letter case, CIWS not added, ignored rounds skipped, blank report $0");
            Check(rows[5] == "Combat Cost: Losses = Player $520M + ? | Enemy $770M",
                "losses: destroyed rows only, x Count, ships and aircraft, inline prices, unknown hull + ?");
            Check(rows[6] == "Combat Cost: Mission = Player $521M + ? | Enemy $770M", "mission = weapons + losses");
            Check(rows[7] == campaign, "campaign: three completed missions, decoy sections not read");
            Check(rows[8] == basis, "IOC basis");
            Check(rows[9] == "Combat Cost: Unpriced = Mission: 3 rounds, 1 ship | " + gaps, "unpriced counts, never zero");
            Check(model.SummaryRows.Skip(4).All(r => !r.IsPositive && !r.IsNegative), "cost rows are neutral");
            Check(Occurrences(log, "combat costs mission 1 (IOC): player weapons 1212400 +3?, losses 520000000 +1?; " +
                "enemy weapons 0 +0?, losses 770000000 +0?; campaign 3 missions: player 522012400 +4? " +
                "(weapons not recorded for 1 mission), enemy 1076000000 +0? (weapons not recorded for 1 mission); " +
                "land and other units not priced: 1 (campaign 1); rounds the tracker ignores: 16 (campaign 16)") == 1, "log line matches the rows");
            Check(Occurrences(log, "combat costs: no IOC price for weapon usn_mk46, weapon sono_dicass, vessel unknown_ship") == 1,
                "unpriced references named for the cost list");
            Check(Occurrences(log, "combat costs: tracker price lists found; CombatCosts.dll not loaded (rules mirrored from 0.7.1 74afa902...)") == 1,
                "tracker hash noted, not gated");
            Check(SeaPower.Utils.Opened.Contains("/aircraft/usn_sh-60b.ini") && SeaPower.Utils.Opened.Contains("/aircraft/enemy_heli.ini") &&
                SeaPower.Utils.Opened.Contains("/vessels/unknown_ship.ini"), "helicopters and air groups from /aircraft, hulls from their folder");

            Check(Shown(model, m1).SequenceEqual(rows), "reopening never duplicates rows");
            Check(Same(before, state.Data), "the campaign state is not changed");
            Check(!SeaPower.Utils.Virtual["systems/weaponcosts"].Data["Costs"].ContainsKey("UseCurrentYearCosts"), "the catalog is not changed");

            List<string> third = Shown(model, new SeaPower.LinearCampaignMission { _index = 3 });
            Check(third[4] == "Combat Cost: Weapons = Player $800K | Enemy $6.00M" && third[7] == campaign &&
                third[9] == "Combat Cost: Unpriced = Mission: none | " + gaps, "mission 3: its own figures, the same campaign total");
            List<string> second = Shown(model, new SeaPower.LinearCampaignMission { _index = 2 });
            Check(second[4] == "Combat Cost: Weapons = Player not recorded | Enemy not recorded" &&
                second[5] == "Combat Cost: Losses = Player $0 | Enemy $300M" &&
                second[6] == "Combat Cost: Mission = Player $0 + ? | Enemy $300M + ?" && second[7] == campaign &&
                second[9] == "Combat Cost: Unpriced = Mission: weapons not recorded | " + gaps,
                "an absent or unreadable report is not recorded and + ?, never $0");
            Check(SeaPower.Utils.Opened.Contains("/submarines/enemy_sub.ini"), "a submarine opens from its own folder");
            Check(Occurrences(log, "no IOC price for") == 1, "each unpriced reference is named once a session");

            SeaPower.Utils.Virtual["systems/combatcosts/config"] = Ini("[Costs]\nUseCurrentYearCosts=True\nCurrentYear=2026-08");
            rows = Shown(model, m1);
            Check(rows[8] == "Combat Cost: Basis = USD, 2026-08 prices; stores aboard and land units excluded" &&
                rows[4] == "Combat Cost: Weapons = Player $6.32M + ? | Enemy $0", "current-year mode from config.ini");
            second = Shown(model, new SeaPower.LinearCampaignMission { _index = 2 });
            Check(second[5] == "Combat Cost: Losses = Player $0 | Enemy $0 + ?", "a missing CurrentYearCost is unknown, never the historical price");
            Check(Occurrences(log, "no 2026-08 price for weapon mlrs_round") == 1, "current-year gaps named");
            SeaPower.Utils.Virtual["systems/combatcosts/config"] = Ini("[Costs]\nUseCurrentYearCosts=False");

            SeaPower.Utils.Throw = "/ammunition/usn_mk45_he.ini";
            rows = Shown(model, m1);
            Shown(model, m1);
            Check(rows.Count == 10 && rows[4] == "Combat Cost: Weapons = Player $1.20M + ? | Enemy $0" &&
                rows[9].StartsWith("Combat Cost: Unpriced = Mission: 13 rounds, 1 ship | "), "an unreadable unit file is counted as unpriced");
            Check(Occurrences(log, "combat costs: could not read weapon usn_mk45_he (IOException: test unit file failure); counted as unpriced") == 1,
                "and logged once");
            SeaPower.Utils.Throw = null;

            Check(Shown(model, new SeaPower.LinearCampaignMission { _index = 5 }).SequenceEqual(native) &&
                Shown(model, new SeaPower.LinearCampaignMission { _index = 6 }).SequenceEqual(native) &&
                Occurrences(log, "no debrief snapshot; rows not shown") == 1, "no snapshot: no rows, logged once");
            SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules.State = null;
            Check(Shown(model, m1).SequenceEqual(native) && Shown(model, m1).SequenceEqual(native) &&
                Occurrences(log, "no campaign state INI; rows not shown") == 1, "no state INI: no rows, logged once");
            SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules.State = state;
            SeaPower.Utils.Virtual["systems/vesselcosts"] = Ini("[usn_ffg]\nVesselCosts=1");  // an extend file alone
            Check(Shown(model, m1).SequenceEqual(native), "a catalog without [Costs]: the tracker is not enabled, no rows");
            SeaPower.Utils.Virtual.Clear();
            Check(Shown(model, m1).SequenceEqual(native) && Occurrences(log,
                "combat costs: Combat Cost Tracker price lists not found (is the tracker enabled?); rows not shown") == 1,
                "no catalogs at all: no rows, logged once");

            Catalogs("[Costs]\nUseCurrentYearCosts=False");
            Check(Shown(model, m1).Count == 10, "rows return with the catalogs");
            SeaPower.Utils.Throw = "systems/weaponcosts";
            Check(Shown(model, m1).SequenceEqual(native), "a failure adds nothing; native rows intact");
            Check(Occurrences(log, "campaign combat costs disabled for this session: InvalidOperationException: test catalog failure") == 1,
                "the failure turns the module off, with its reason");
            SeaPower.Utils.Throw = null;
            Check(Shown(model, m1).SequenceEqual(native), "and later debriefs stay native");

            var debrief = new SeaPower.IniHandler();
            debrief.Sections.Add("TaskForceMode_Mission11_Launch");
            debrief.Sections.Add("Mission_11_arafura");
            debrief.Destroyed.Add("Mission_11_arafura");
            var units = new SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel();
            TaskForceDebrief.Postfix(units, debrief, new SeaPower.LinearCampaignMission { _index = 11 });
            Check(units.UnitRows.Count == 1, "the debrief correction still works");
        }
        finally
        {
            Console.SetOut(stdout);
            Console.Write(log.ToString());
        }
    }
}
