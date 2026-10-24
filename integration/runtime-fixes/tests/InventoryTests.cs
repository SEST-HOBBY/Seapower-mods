using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using Sest.RuntimeFixes;

namespace SeaPower
{
    public partial class ObjectBase
    {
        public enum ObjectType { Vessel,Submarine,Aircraft,Helicopter,LandUnit,Missile }
        public ObjectType _type;
        public ObjectBaseParameters _obp;
        public Dictionary<string,int> AmmunitionAmountDictionary { get; set; }=new Dictionary<string,int>();
    }
    public class ObjectBaseParameters
    {
        public string _objectIniName;
        public FlightDeck _flightDeck;
    }
    public class FlightDeck
    {
        public float _currentAmmo;
        public Dictionary<string,int> _accountableAmmunition=new Dictionary<string,int>();
    }
    public class UnitRegister
    {
        public string IniRef { get; set; }
        public string IniFolder { get; set; }
        public ObjectBase.ObjectType ObjectType { get; set; }
        public bool IsDestroyed { get; set; }
        public int Count { get; set; }
    }
    public class Taskforce
    {
        public List<UnitRegister> _unitStatusRegister=new List<UnitRegister>();
        public Dictionary<string,WeaponsSpent> _weaponsSpent=new Dictionary<string,WeaponsSpent>();
        public void RegisterUnitStatus(bool useTmpList,ObjectBase tfObject,bool destroyed,bool damaged)
        {
            if(useTmpList)return;
            _unitStatusRegister.Add(new UnitRegister { IniRef=tfObject._obp._objectIniName,ObjectType=tfObject._type,IsDestroyed=destroyed,Count=1 });
        }
    }
    public class WeaponsSpent { public int _number; }
    public static class SaveLoadManager
    {
        public static void WriteTaskforceAarData(IniHandler ini,Taskforce taskforce,string sectionName) { }
        public static void LoadTaskforceAarData(IniHandler missionIni,Taskforce taskforce,string sectionName) { }
    }
    public static class Globals { public static Taskforce _playerTaskforce,_enemyTaskforce; }
    public partial class IniHandler
    {
        public int Writes,Saves;
        public void writeValue(string sectionName,string key,string value)
        {
            Writes++;if(!Data.ContainsKey(sectionName))Data[sectionName]=new Dictionary<string,string>();Data[sectionName][key]=value;
        }
        public void saveFile(bool overwrite) { if(overwrite)throw new Exception("native data must be merged");Saves++; }
    }
}
namespace SeapowerUI.ViewModels
{
    public class MissionDebriefViewModel { }
    public partial class LinearCampaignTaskForceDebriefViewModel
    {
        static void SaveDebriefSnapshot(SeaPower.LinearCampaignMission mission,MissionDebriefViewModel debrief) { }
    }
}

static class InventoryTests
{
    static int checks;
    static void Check(bool value,string label){checks++;if(!value)throw new Exception("inventory: "+label);}
    static SeaPower.ObjectBase Unit(string reference,SeaPower.ObjectBase.ObjectType type,params string[] ammo)
    {
        var obj=new SeaPower.ObjectBase{_type=type,_obp=new SeaPower.ObjectBaseParameters{_objectIniName=reference}};
        for(int i=0;i<ammo.Length;i+=2)obj.AmmunitionAmountDictionary.Add(ammo[i],Int32.Parse(ammo[i+1],CultureInfo.InvariantCulture));
        return obj;
    }
    static void Lose(SeaPower.Taskforce tf,SeaPower.ObjectBase unit,bool temporary=false)
    {
        CampaignInventory.Capture capture;CampaignInventory.BeforeRegister(tf,temporary,unit,true,out capture);
        tf.RegisterUnitStatus(temporary,unit,true,false);CampaignInventory.AfterRegister(tf,capture);
    }
    static InventoryLedger Saved(SeaPower.Taskforce tf)
    {
        var ini=new SeaPower.IniHandler();CampaignInventory.AfterSave(ini,tf,"Taskforce1");
        return InventoryLedger.Parse(ini.Data["Taskforce1"][CampaignInventory.MissionSaveKey]);
    }
    internal static int Run()
    {
        CampaignInventory.Bind(Assembly.GetExecutingAssembly());
        var tf=new SeaPower.Taskforce();
        var ship=Unit("ship",SeaPower.ObjectBase.ObjectType.Vessel,"round","20","decoy","3");
        Lose(tf,ship);
        var ledger=Saved(tf);
        Check(InventoryLedger.Get(ledger.Captured,"vessel")==1,"one confirmed native hull loss");
        Check(ledger.Ammo["round"]==20 && ledger.Ammo["decoy"]==3,"remaining rounds and decoys captured");
        Check(ship.AmmunitionAmountDictionary["round"]==20,"capture never consumes native inventory");
        CampaignInventory.Capture duplicate;CampaignInventory.BeforeRegister(tf,false,ship,true,out duplicate);
        Check(duplicate==null,"same unit cannot charge inventory twice");
        CampaignInventory.AfterRegister(tf,duplicate);
        Check(Saved(tf).Ammo["round"]==20,"duplicate callback leaves quantities unchanged");
        var plane=Unit("plane",SeaPower.ObjectBase.ObjectType.Aircraft,"round","4");
        Lose(tf,plane);
        Check(Saved(tf).Ammo["round"]==24 && InventoryLedger.Get(Saved(tf).Captured,"aircraft")==1,"parked aircraft captured without an in-flight requirement");
        var radar=Unit("radar",SeaPower.ObjectBase.ObjectType.LandUnit,"decoy","2");Lose(tf,radar);
        Check(InventoryLedger.Get(Saved(tf).Captured,"land")==1 && Saved(tf).Ammo["decoy"]==5,"land-platform magazines captured");
        var temp=Unit("temporary",SeaPower.ObjectBase.ObjectType.Vessel,"round","999");Lose(tf,temp,true);
        Check(Saved(tf).Ammo["round"]==24,"temporary registers excluded");
        var rejected=Unit("rejected",SeaPower.ObjectBase.ObjectType.Vessel,"round","900");
        CampaignInventory.Capture noNative;CampaignInventory.BeforeRegister(tf,false,rejected,true,out noNative);
        CampaignInventory.AfterRegister(tf,noNative);
        Check(Saved(tf).Ammo["round"]==24,"a native rejected registration does not become a loss");
        var carrier=Unit("carrier",SeaPower.ObjectBase.ObjectType.Vessel,"round","2");
        carrier._obp._flightDeck=new SeaPower.FlightDeck{_currentAmmo=50000};Lose(tf,carrier);
        ledger=Saved(tf);Check(ledger.Unknown==1,"virtual deck points remain unknown rather than USD");
        Check(ledger.Ammo["round"]==26,"known mounted inventory retained alongside unknown pool");
        string serialized=ledger.Serialize();var copy=InventoryLedger.Parse(serialized);
        Check(copy.Ammo["round"]==26 && copy.Unknown==1,"versioned quantity round trip");
        Check(InventoryLedger.Parse("not base64")==null && InventoryLedger.Parse("")==null,"malformed and absent capture distinct from known zero");
        var unicode=new InventoryLedger();unicode.Ammo["plaaf_500-Ⅲ"]=2;Check(InventoryLedger.Parse(unicode.Serialize()).Ammo["plaaf_500-Ⅲ"]==2,"unicode ammo references round trip");
        var save=new SeaPower.IniHandler();save.Data["Native"]=new Dictionary<string,string>{{"Keep","unchanged"}};
        CampaignInventory.AfterSave(save,tf,"Taskforce1");
        Check(save.Data["Native"]["Keep"]=="unchanged" && save.Data["Taskforce1"].Count==1,"mission save writes only own versioned key");
        var restored=new SeaPower.Taskforce();restored._unitStatusRegister.AddRange(tf._unitStatusRegister);
        CampaignInventory.AfterLoad(save,restored,"Taskforce1");
        Check(Saved(restored).Ammo["round"]==26,"mid-mission reload retains lost inventory");
        Lose(restored,Unit("new-plane",SeaPower.ObjectBase.ObjectType.Helicopter,"round","5"));
        Check(Saved(restored).Ammo["round"]==31,"capture continues after reload");
        restored._unitStatusRegister.Clear();
        Check(Saved(restored).Ammo.Count==0,"task-force reuse with fresh register clears old mission");

        // Native platform loss rows are priced by CampaignCosts, so only store
        // quantities enter this supplement. Airframes are never charged twice.
        var state=new SeaPower.IniHandler();
        SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules.State=state;
        SeaPower.Globals._playerTaskforce=tf;SeaPower.Globals._enemyTaskforce=new SeaPower.Taskforce();
        var mission=new SeaPower.LinearCampaignMission{_index=4};
        tf._weaponsSpent["round"]=new SeaPower.WeaponsSpent{_number=7};
        tf._weaponsSpent["tank"]=new SeaPower.WeaponsSpent{_number=1};
        CampaignInventory.Prior prior;CampaignInventory.BeforeCampaignSave(mission,out prior);
        Check(prior!=null && !prior.Snapshot,"new mission campaign precheck");
        state.Data["Mission_4_TaskForceDebrief"]=new Dictionary<string,string>{{"Complete","True"},{"Native","preserved"}};
        CampaignInventory.AfterCampaignSave(mission,prior);
        var section=state.Data["Mission_4_TaskForceDebrief"];
        Check(section["Native"]=="preserved" && section.ContainsKey(CampaignInventory.PlayerKey),"completed mission gets own capture keys only");
        Check(state.Saves==1 && InventoryLedger.Parse(section[CampaignInventory.PlayerKey]).Ammo["round"]==26,"native merge save persists campaign quantities");
        Check(InventoryLedger.Parse(section[CampaignInventory.PlayerSpentKey]).Ammo["tank"]==1,"native spent counter retained including types absent from saved weapon report");
        string original=section[CampaignInventory.PlayerKey];
        CampaignInventory.BeforeCampaignSave(mission,out prior);
        section.Remove(CampaignInventory.PlayerKey);section.Remove(CampaignInventory.EnemyKey); // emulate native snapshot replacement
        Lose(tf,Unit("replay-extra",SeaPower.ObjectBase.ObjectType.Vessel,"round","100"));
        CampaignInventory.AfterCampaignSave(mission,prior);
        Check(section[CampaignInventory.PlayerKey]==original,"replay preserves completed mission capture rather than adding a second attempt");
        var old=new SeaPower.LinearCampaignMission{_index=1};state.Data["Mission_1_TaskForceDebrief"]=new Dictionary<string,string>{{"Complete","True"}};
        CampaignInventory.BeforeCampaignSave(old,out prior);int writes=state.Writes;CampaignInventory.AfterCampaignSave(old,prior);
        Check(state.Writes==writes && !state.Data["Mission_1_TaskForceDebrief"].ContainsKey(CampaignInventory.PlayerKey),"older campaign without capture is never backfilled with current losses");
        var failed=new SeaPower.LinearCampaignMission{_index=5};CampaignInventory.BeforeCampaignSave(failed,out prior);writes=state.Writes;
        CampaignInventory.AfterCampaignSave(failed,prior);Check(state.Writes==writes,"failed or unfinished mission adds no campaign ledger");

        // Re-enable after the earlier failure-path tests, and prove the new
        // saved raw quantities are independently re-priced in the debrief.
        SeaPower.Utils.CatalogFailure=false;
        SeaPower.Utils.Catalogs["config"].Data["Costs"]["UseCurrentYearCosts"]="True";
        state.Data["Mission_4_TaskForceDebrief"]=new Dictionary<string,string>{{"Complete","True"},{"PlayerWeaponReport",""},{"EnemyWeaponReport",""},
            {"LossRows","ship|vessels|Vessel|1|lost"},{"KillRows",""}};
        var exact=new InventoryLedger();exact.Add("vessel",new Dictionary<string,long>{{"round",20},{"decoy",3}},false);
        state.Data["Mission_4_TaskForceDebrief"][CampaignInventory.PlayerKey]=exact.Serialize();
        state.Data["Mission_4_TaskForceDebrief"][CampaignInventory.EnemyKey]=new InventoryLedger().Serialize();
        state.Data.Remove("Mission_1_TaskForceDebrief");
        CampaignCosts.Bind(Assembly.GetExecutingAssembly());
        var vm=new SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel();vm.Load(mission);CampaignCosts.Postfix(vm,mission);
        string stock=vm.SummaryRows.Single(x=>x.Label=="Combat Cost: Lost Stores").Value;
        Check(stock=="Player $418 | Enemy $0","lost ammunition repriced from current mode; no airframe/hull duplication");
        Check(vm.SummaryRows.Single(x=>x.Label=="Combat Cost: Mission").Value=="Player $2.00M | Enemy $0","complete itemized inventory removes incomplete marker");
        int saveCount=state.Saves;vm.Load(mission);CampaignCosts.Postfix(vm,mission);Check(state.Saves==saveCount,"opening debrief performs no writes");
        return checks;
    }
}
