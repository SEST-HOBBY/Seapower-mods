// Test-only native API stand-ins. This file and AnchorChain.cs never ship
// inside a game mod. Tests exercise the actual plugin's bind and callbacks.
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Reflection;
using Sest.RuntimeFixes;

namespace UnityEngine
{
    public struct Vector3 { public float x, y, z; }
    public class Transform { public Vector3 eulerAngles { get; set; } }
    public class Component { public Transform transform { get; set; } = new Transform(); }
    public static class Debug { public static void Log(object value) { Console.WriteLine(value); } }
}

namespace SeaPower
{
    public enum FlightStage { None, Launch, ToBearing, MaintainHeight, MoveToLoftAlt, MaintainLoftAlt,
        MoveToSeaSkimming, MaintainSeaSkimming, MoveToFinalFlightAlt, MaintainFinalFlightAlt,
        AlignSensorToTarget, TerminalApproach, SelfDestruct }
    public struct GeoPosition { public float Latitude; }
    public class ObjectBase : UnityEngine.Component { public GeoPosition _geoPosition { get; set; } }
    public class AmmunitionParameters { public string _ammunitionFileName; public bool _terrainFollowFlight = true; }
    public class WeaponBase : ObjectBase
    {
        public AmmunitionParameters _ap;
        public FlightStage _flightStage { get; set; } = FlightStage.MaintainLoftAlt;
    }
    public class Missile : WeaponBase { }
    public static class Utils { public static float heightInFeetToUnity(float feet) { return feet * .00453571f; } }
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
        public bool doesSectionExist(string section) { return Sections.Contains(section); }
        public bool readValue(string section, string key, bool defaultValue, bool performLogging)
        {
            return key == "IsDestroyed" ? Destroyed.Contains(section) : defaultValue;
        }
    }
}

namespace SeapowerUI.ViewModels
{
    public enum CrewSkill { Green, Regular, Veterans }
    public class LinearCampaignTaskForceBuilderRosterItem
    {
        public string InstanceId { get; set; }
        public string UnitFolder { get; set; } = "vessels";
        public string UnitType { get; set; }
        public string Category { get; set; } = "Frigate";
        public string VariantReference { get; set; } = "Variant1";
        public CrewSkill CrewSkill { get; set; } = CrewSkill.Veterans;
    }
    public class LinearCampaignTaskForceSnapshot
    {
        public List<LinearCampaignTaskForceBuilderRosterItem> Items { get; set; } = new List<LinearCampaignTaskForceBuilderRosterItem>();
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
        public CrewSkill CrewSkill { get; private set; }
        public LinearCampaignTaskForceDebriefUnitRow(string id, string uid, string folder, string category,
            string variant, string damage, bool destroyed, bool flagship, CrewSkill crew, int count)
        {
            InstanceId = id; IniRef = uid; IniFolder = folder; VariantReference = variant; IsDestroyed = destroyed; CrewSkill = crew;
        }
    }
    public class LinearCampaignTaskForceDebriefViewModel
    {
        public ObservableCollection<LinearCampaignTaskForceDebriefUnitRow> UnitRows { get; private set; } =
            new ObservableCollection<LinearCampaignTaskForceDebriefUnitRow>();
        void ReadUnitRows(SeaPower.IniHandler state, SeaPower.LinearCampaignMission mission) { }
        static IEnumerable<LinearCampaignTaskForceDebriefUnitRow> SortDebriefUnitRows(IEnumerable<LinearCampaignTaskForceDebriefUnitRow> rows)
        {
            return rows.OrderBy(r => r.IniFolder).ThenBy(r => r.InstanceId).ToList();
        }
    }
}

static class RuntimeTests
{
    static int checks;
    static void Check(bool value, string name) { checks++; if (!value) throw new Exception(name); }
    static void Equal(float a, float b, string name) { Check(Math.Abs(a-b) < .0001f, name); }

    static void Main()
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
        missile._flightStage = SeaPower.FlightStage.TerminalApproach;
        TerrainClearance.Postfix(missile, true, ref result); Equal(result, .1f, "terminal descent retained");
        missile._flightStage = SeaPower.FlightStage.MaintainHeight;
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
        snapshot.Items.Add(new SeapowerUI.ViewModels.LinearCampaignTaskForceBuilderRosterItem { InstanceId = "arafura", UnitType = "ran_opv_arafura" });
        snapshot.Items.Add(new SeapowerUI.ViewModels.LinearCampaignTaskForceBuilderRosterItem { InstanceId = "warramunga", UnitType = "ran_ffh_anzac", VariantReference = "Variant3" });
        snapshot.Items.Add(new SeapowerUI.ViewModels.LinearCampaignTaskForceBuilderRosterItem { InstanceId = "survivor", UnitType = "ran_ddg_hobart" });
        snapshot.Items.Add(new SeapowerUI.ViewModels.LinearCampaignTaskForceBuilderRosterItem { InstanceId = "air", UnitType = "ran_mh-60r", UnitFolder = "aircraft" });
        snapshot.Items.Add(new SeapowerUI.ViewModels.LinearCampaignTaskForceBuilderRosterItem { InstanceId = "notdeployed", UnitType = "ran_ffh_anzac" });
        foreach (string id in new[] { "arafura", "warramunga", "air" })
        { state.Sections.Add("Mission_11_" + id); state.Destroyed.Add("Mission_11_" + id); }
        state.Sections.Add("Mission_11_survivor");
        var model = new SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel();
        var mission = new SeaPower.LinearCampaignMission { _index = 11 };
        TaskForceDebrief.Postfix(model, state, mission);
        Check(model.UnitRows.Count == 2, "exactly two missing lost ships restored");
        Check(model.UnitRows.All(r => r.IsDestroyed), "restored rows are lost");
        Check(model.UnitRows.Single(r => r.InstanceId == "warramunga").VariantReference == "Variant3", "hull identity preserved");
        Check(model.UnitRows.All(r => r.CrewSkill == SeapowerUI.ViewModels.CrewSkill.Veterans), "proficiency preserved");
        TaskForceDebrief.Postfix(model, state, mission);
        Check(model.UnitRows.Count == 2, "no duplicate loss rows");
        Check(snapshot.Items.Count == 5 && state.Destroyed.Count == 3, "save and roster unmodified");
        var other = new SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel();
        TaskForceDebrief.Postfix(other, state, new SeaPower.LinearCampaignMission { _index = 10 });
        Check(other.UnitRows.Count == 0, "no nearest mission fallback");
        Console.WriteLine("Runtime regressions passed: " + checks + " assertions (mocked native API; PC gameplay still required)");
    }
}
