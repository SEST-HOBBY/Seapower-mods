// Mock records below deliberately use a small test-only serializer. Production
// delegates native record parsing to the game; no game code is embedded here.
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using Sest.RuntimeFixes;

namespace SeaPower
{
    public partial class IniHandler
    {
        public Dictionary<string,Dictionary<string,string>> Data { get; set; } =
            new Dictionary<string,Dictionary<string,string>>(StringComparer.OrdinalIgnoreCase);
        public bool doesKeyExist(string section,string key) { return Data.ContainsKey(section) && Data[section].ContainsKey(key); }
    }
    public static partial class Utils
    {
        public static readonly Dictionary<string,IniHandler> Catalogs=new Dictionary<string,IniHandler>();
        public static readonly Dictionary<string,IniHandler> Units=new Dictionary<string,IniHandler>();
        public static bool CatalogFailure,UnitFailure;
        public static IniHandler openVirtualIniFile(string basePath,string fileName,string folderName,bool checkCached)
        {
            if (CatalogFailure) throw new InvalidOperationException("test catalog failure");
            if (checkCached || fileName!=folderName) throw new Exception("wrong virtual INI call");
            IniHandler result; return Catalogs.TryGetValue(fileName,out result)?result:new IniHandler();
        }
        public static IniHandler openIniFile(string rootPath,string name,bool logErrors,bool useCaching)
        {
            if (UnitFailure) throw new InvalidOperationException("test one-item read failure");
            if (logErrors || !useCaching || !rootPath.StartsWith("/") || !name.StartsWith("/")) throw new Exception("wrong unit INI call");
            IniHandler result; return Units.TryGetValue(rootPath+name,out result)?result:new IniHandler();
        }
        public static IniHandler openIniFile(string path,bool log,bool cache) { throw new Exception("wrong openIniFile overload"); }
    }
    public class Ammunition
    {
        public enum Type { Missile,ASROC,RBU,AirDepthCharge,Torpedo,Bomb,Projectile,AerialRocket,MLRS,Chaff,Noisemaker,Sonobuoy,Fueltank,Container,Paratrooper }
    }
    public class WeaponReportAmmoData
    {
        public string AmmoRef { get; set; }
        public Ammunition.Type AmmoType { get; set; }
        public int Launched { get; set; }
        public int ProjectileFired { get; set; }
        public int CiwsRoundsFired { get; set; }
    }
    public class TaskforceWeaponReport
    {
        public readonly Dictionary<string,WeaponReportAmmoData> Rows=new Dictionary<string,WeaponReportAmmoData>();
        public Dictionary<string,WeaponReportAmmoData> BuildTaskforceTotals() { return Rows; }
    }
}

namespace SeapowerUI.ViewModels
{
    public struct LinearCampaignTaskForceDebriefRegisterSnapshotRow
    {
        public string IniRef,Folder,ObjectType;
        public int Count;
        public bool IsDestroyed;
    }
    public class LinearCampaignTaskForceDebriefSummaryRow
    {
        public string Label { get; private set; }
        public string Value { get; private set; }
        public LinearCampaignTaskForceDebriefSummaryRow(string label,string value,bool isPositive,bool isNegative)
        { Label=label;Value=value; }
    }
    public static partial class LinearCampaignTaskForceModeRules
    {
        public static SeaPower.IniHandler State;
        public static SeaPower.IniHandler OpenCampaignStateIni() { return State; }
    }
    public partial class LinearCampaignTaskForceDebriefViewModel
    {
        public static readonly Dictionary<string,SeaPower.TaskforceWeaponReport> Reports=new Dictionary<string,SeaPower.TaskforceWeaponReport>();
        public ObservableCollection<LinearCampaignTaskForceDebriefSummaryRow> SummaryRows { get; private set; } =
            new ObservableCollection<LinearCampaignTaskForceDebriefSummaryRow>();
        public void Load(SeaPower.LinearCampaignMission mission)
        { SummaryRows.Clear();SummaryRows.Add(new LinearCampaignTaskForceDebriefSummaryRow("Native","preserved",false,false)); }
        static bool HasDebriefSnapshot(SeaPower.IniHandler ini,int index)
        { return ini.Data.ContainsKey(GetDebriefSectionName(index)) && ini.Data[GetDebriefSectionName(index)].ContainsKey("Complete"); }
        static string GetDebriefSectionName(int index) { return "Mission_"+index+"_TaskForceDebrief"; }
        static bool TryParseRegisterRows(string text,ref List<LinearCampaignTaskForceDebriefRegisterSnapshotRow> rows)
        {
            rows=new List<LinearCampaignTaskForceDebriefRegisterSnapshotRow>();
            if (text=="malformed") return false;
            foreach (string line in text.Split(';'))
            {
                if (line.Length==0) continue;
                string[] p=line.Split('|');
                rows.Add(new LinearCampaignTaskForceDebriefRegisterSnapshotRow {
                    IniRef=p[0],Folder=p[1],ObjectType=p[2],Count=Int32.Parse(p[3],CultureInfo.InvariantCulture),IsDestroyed=p[4]=="lost"});
            }
            return true;
        }
        static bool TryReadWeaponReports(SeaPower.IniHandler campaignStateIni,int missionIndex,
            ref SeaPower.TaskforceWeaponReport playerReport,ref SeaPower.TaskforceWeaponReport enemyReport,ref SeaPower.TaskforceWeaponReport neutralReport)
        {
            var section=campaignStateIni.Data[GetDebriefSectionName(missionIndex)];
            string key;
            if (section.TryGetValue("PlayerWeaponReport",out key)) Reports.TryGetValue(key,out playerReport);
            if (section.TryGetValue("EnemyWeaponReport",out key)) Reports.TryGetValue(key,out enemyReport);
            neutralReport=null;return playerReport!=null || enemyReport!=null;
        }
    }
}

static class CostTests
{
    static int checks;
    static void Check(bool value,string name) { checks++;if(!value)throw new Exception("cost: "+name); }
    static Dictionary<string,string> Dict(params string[] values)
    {
        var result=new Dictionary<string,string>(StringComparer.OrdinalIgnoreCase);
        for(int i=0;i<values.Length;i+=2)result[values[i]]=values[i+1];return result;
    }
    static void Token(Dictionary<string,string> data,string key,string value)
    { if(value!="~") data[key]=value=="EMPTY"?"":value; }
    static SeaPower.IniHandler Ini(string section,Dictionary<string,string> value)
    { var ini=new SeaPower.IniHandler();ini.Data.Add(section,value);return ini; }
    static void Catalogs()
    {
        SeaPower.Utils.Catalogs.Clear();SeaPower.Utils.Units.Clear();SeaPower.Utils.CatalogFailure=false;SeaPower.Utils.UnitFailure=false;
        foreach(string kind in new[]{"weapon","vessel","aircraft"})
            SeaPower.Utils.Catalogs[kind+"costs"]=Ini("Costs",Dict("OverrideInline","False"));
        SeaPower.Utils.Catalogs["sest_land_costs"]=Ini("Costs",Dict("OverrideInline","False"));
        SeaPower.Utils.Catalogs["config"]=Ini("Costs",Dict("UseCurrentYearCosts","False","CurrentYear","2026-08"));
        SeaPower.Utils.Catalogs["weaponcosts"].Data["round"]=Dict("WeaponCosts","10","CurrentYearCost","20","Category","Gun");
        SeaPower.Utils.Catalogs["weaponcosts"].Data["decoy"]=Dict("WeaponCosts","3","CurrentYearCost","6","Category","Decoy");
        SeaPower.Utils.Catalogs["weaponcosts"].Data["simulator"]=Dict("WeaponCosts","0","CurrentYearCost","0","Category","Ignore");
        SeaPower.Utils.Catalogs["vesselcosts"].Data["ship"]=Dict("VesselCosts","1000000","CurrentYearCost","2000000");
        SeaPower.Utils.Catalogs["aircraftcosts"].Data["plane"]=Dict("AircraftCosts","100000","CurrentYearCost","200000");
        SeaPower.Utils.Catalogs["sest_land_costs"].Data["radar"]=Dict("LandCosts","300000","CurrentYearCost","600000");
    }
    static SeaPower.TaskforceWeaponReport Report(params SeaPower.WeaponReportAmmoData[] rows)
    { var r=new SeaPower.TaskforceWeaponReport();foreach(var a in rows)r.Rows.Add(a.AmmoRef,a);return r; }
    static SeaPower.WeaponReportAmmoData Ammo(string reference,SeaPower.Ammunition.Type type,int launched,int fired=0,int ciws=0)
    { return new SeaPower.WeaponReportAmmoData {AmmoRef=reference,AmmoType=type,Launched=launched,ProjectileFired=fired,CiwsRoundsFired=ciws}; }
    static Dictionary<string,string> Mission(string player,string enemy,string losses="",string kills="")
    { return Dict("Complete","True","PlayerWeaponReport",player,"EnemyWeaponReport",enemy,"LossRows",losses,"KillRows",kills); }
    static string Row(SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel vm,string label)
    { return vm.SummaryRows.Single(x=>x.Label==label).Value; }
    static void Show(SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel vm,int index)
    { var m=new SeaPower.LinearCampaignMission{_index=index};vm.Load(m);CampaignCosts.Postfix(vm,m); }
    internal static int Run(string[] args)
    {
        Check(args.Length==1 && File.Exists(args[0]),"shared precedence fixture present");
        foreach(string line in File.ReadAllLines(args[0]).Skip(1))
        {
            if(line.Length==0)continue;string[] p=line.Split('\t');
            var own=Dict();var entry=Dict();var global=Dict();
            Token(own,"CurrentYearCost",p[1]);Token(entry,"CurrentYearCost",p[2]);
            Token(global,"OverrideInline",p[3]);Token(entry,"OverrideInline",p[4]);Token(entry,"OverrideCurrentYearCost",p[5]);
            string expected=p[6]=="~"?null:p[6]=="EMPTY"?"":p[6];
            Check(CombatPrices.Resolve(own,global,entry,"CurrentYearCost")==expected,"precedence "+p[0]);
        }
        Check(CombatPrices.Parse("0")==0,"explicit zero known");
        foreach(string invalid in new[]{"","-1","1,000","1e3","NaN","Infinity"," 1","1000000000000001"})
            Check(!CombatPrices.Parse(invalid).HasValue,"invalid price "+invalid);
        Check(CombatPrices.Parse("1.25")==1.25m,"invariant decimal");
        Check(!CombatPrices.ValidCategory("é") && !CombatPrices.ValidCategory("SAM/") && !CombatPrices.ValidCategory(" "),"category character rule");
        Check(CombatPrices.ValidCategory("Fuel tank"),"category spaces allowed");
        Check(CombatAmount.Money(999999999)=="$1.00B","format rounding carries unit");
        Check(CombatAmount.Money(0)=="$0" && CombatAmount.Money(4120000)=="$4.12M","money formats");
        var empty=new CombatAmount();empty.Add(new CombatPrice{Amount=0},1);Check(!empty.Incomplete && empty.Count==1,"zero remains a known item");
        empty.Add(new CombatPrice(),3);Check(empty.Unknown==3 && empty.Text=="$0 + ?","unknown counted, not free");
        var ignored=new CombatAmount();ignored.Add(new CombatPrice{Amount=100,Ignored=true},3);Check(ignored.Count==0 && !ignored.Incomplete,"explicit included item ignored");

        Catalogs();
        var state=new SeaPower.IniHandler();
        state.Data["Mission_1_TaskForceDebrief"]=Mission("p1","e1","ship|vessels|Vessel|1|lost;plane|aircraft|Aircraft|4|lost;radar|land_units|LandUnit|2|lost","plane|aircraft|Helicopter|2|lost;ship|vessels|Vessel|1|damaged");
        state.Data["Mission_2_TaskForceDebrief"]=Mission("p2","");
        state.Data["Mission_3_TaskForceDebrief"]=Dict("PlayerWeaponReport","p1"); // unfinished, no snapshot
        state.Data["Mission_9_TaskForceDebrief_extra"]=Mission("p1","e1"); // not a debrief section
        var native=SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel.Reports;native.Clear();
        native["p1"]=Report(Ammo("round",SeaPower.Ammunition.Type.Projectile,2,8,8),Ammo("decoy",SeaPower.Ammunition.Type.Chaff,2),Ammo("simulator",SeaPower.Ammunition.Type.Paratrooper,3));
        native["e1"]=Report(Ammo("round",SeaPower.Ammunition.Type.Projectile,0,5,5));
        native["p2"]=Report(Ammo("round",SeaPower.Ammunition.Type.Projectile,0,4));
        SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules.State=state;
        CampaignCosts.Bind(Assembly.GetExecutingAssembly());
        var vm=new SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel();
        Show(vm,1);
        Check(vm.SummaryRows[0].Label=="Native" && vm.SummaryRows[0].Value=="preserved","native rows retained");
        Check(Row(vm,"Combat Cost: Weapons")=="Player $106 | Enemy $50","rounds and decoys once, not CIWS twice");
        Check(Row(vm,"Combat Cost: Ships")=="Player $1.00M | Enemy $0","damaged ship not a loss");
        Check(Row(vm,"Combat Cost: Aircraft")=="Player $400K | Enemy $200K","all saved aircraft losses include parked/onboard quantities");
        Check(Row(vm,"Combat Cost: Land")=="Player $600K | Enemy $0","land losses priced separately");
        Check(Row(vm,"Combat Cost: Campaign").EndsWith("(2 missions)"),"completed exact sections only");
        Check(Row(vm,"Combat Cost: Mission").Contains("+ ?") && Row(vm,"Combat Cost: Incomplete").Contains("remaining stores"),"unrecorded stores never treated as zero");
        int count=vm.SummaryRows.Count;Show(vm,1);Check(vm.SummaryRows.Count==count,"reopening does not duplicate rows");
        Show(vm,2);Check(Row(vm,"Combat Cost: Mission")=="Player $40 | Enemy $0","blank weapon report is known zero");
        Check(Row(vm,"Combat Cost: Campaign").Contains("(2 missions)"),"campaign independent of opened debrief");
        Check(state.Data.Count==4 && state.Data["Mission_1_TaskForceDebrief"].Count==5,"campaign save unchanged");
        SeaPower.Utils.Catalogs["config"].Data["Costs"]["UseCurrentYearCosts"]="True";
        Show(vm,2);Check(Row(vm,"Combat Cost: Mission")=="Player $80 | Enemy $0","price-mode change reprices saved counts");
        Check(Row(vm,"Combat Cost: Basis").Contains("2026-08"),"shared current basis label");
        state.Data["Mission_2_TaskForceDebrief"].Remove("EnemyWeaponReport");
        Show(vm,2);Check(Row(vm,"Combat Cost: Weapons").EndsWith("Enemy $0 + ?"),"missing report differs from blank");
        state.Data["Mission_2_TaskForceDebrief"]["LossRows"]="malformed";
        Show(vm,2);Check(Row(vm,"Combat Cost: Ships").Contains("Player $0 + ?"),"malformed rows incomplete");
        state.Data["Mission_2_TaskForceDebrief"]["LossRows"]="";
        SeaPower.Utils.UnitFailure=true;
        Show(vm,2);Check(Row(vm,"Combat Cost: Weapons").StartsWith("Player $0 + ?"),"per-item failure unknown");
        SeaPower.Utils.UnitFailure=false;Show(vm,2);Check(Row(vm,"Combat Cost: Weapons").StartsWith("Player $80"),"item failure did not disable accounting");
        int original=state.Data.Count;SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules.State=new SeaPower.IniHandler();
        Show(vm,1);Check(vm.SummaryRows.Count==1,"new campaign empty, no cross-campaign cached totals");
        SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules.State=state;
        SeaPower.Utils.Catalogs["weaponcosts"].Data.Remove("Costs");Show(vm,1);Check(vm.SummaryRows.Count==1,"disabled tracker catalog does not manufacture totals");
        Catalogs();SeaPower.Utils.CatalogFailure=true;Show(vm,1);Check(vm.SummaryRows.Count==1,"catalog-wide failure retains native debrief");
        SeaPower.Utils.CatalogFailure=false;Show(vm,1);Check(vm.SummaryRows.Count==1,"failed feature remains off for session, other runtime modules unaffected");
        Check(state.Data.Count==original,"no persistence writes");
        return checks+InventoryTests.Run();
    }
}
