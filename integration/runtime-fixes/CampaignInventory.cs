using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text;

namespace Sest.RuntimeFixes
{
    // Only raw remaining quantities are stored, never USD or campaign points.
    // Our versioned keys coexist with native data. Past losses without a
    // capture stay incomplete; they are never reconstructed from guessed fits.
    internal sealed class InventoryLedger
    {
        internal readonly Dictionary<string,long> Ammo=new Dictionary<string,long>(StringComparer.OrdinalIgnoreCase);
        internal readonly Dictionary<string,long> Captured=new Dictionary<string,long>(StringComparer.OrdinalIgnoreCase);
        internal readonly HashSet<object> Seen=new HashSet<object>();
        internal long Unknown;
        internal void Add(string kind,Dictionary<string,long> ammo,bool incomplete)
        {
            Captured[kind]=Get(Captured,kind)+1;
            foreach(var pair in ammo) Ammo[pair.Key]=checked(Get(Ammo,pair.Key)+pair.Value);
            if(incomplete)Unknown++;
        }
        internal static long Get(Dictionary<string,long> values,string key)
        { long value;return values.TryGetValue(key,out value)?value:0; }
        internal string Serialize()
        {
            var lines=new List<string>{"SEST-INVENTORY-1",Unknown.ToString(CultureInfo.InvariantCulture)};
            foreach(string kind in new[]{"vessel","aircraft","land"})lines.Add(kind+"\t"+Get(Captured,kind));
            var names=new List<string>(Ammo.Keys);names.Sort(StringComparer.OrdinalIgnoreCase);
            foreach(string name in names)lines.Add(Uri.EscapeDataString(name)+"\t"+Ammo[name].ToString(CultureInfo.InvariantCulture));
            return Convert.ToBase64String(Encoding.UTF8.GetBytes(String.Join("\n",lines)));
        }
        internal static InventoryLedger Parse(string text)
        {
            if(String.IsNullOrWhiteSpace(text) || text.Length>4000000)return null;
            try
            {
                string[] lines=Encoding.UTF8.GetString(Convert.FromBase64String(text)).Split('\n');
                if(lines.Length<5 || lines.Length>100005 || lines[0]!="SEST-INVENTORY-1")return null;
                long unknown;if(!Int64.TryParse(lines[1],NumberStyles.None,CultureInfo.InvariantCulture,out unknown) || unknown<0)return null;
                var result=new InventoryLedger{Unknown=unknown};
                for(int i=2;i<lines.Length;i++)
                {
                    string[] pair=lines[i].Split('\t');long count;
                    if(pair.Length!=2 || !Int64.TryParse(pair[1],NumberStyles.None,CultureInfo.InvariantCulture,out count) || count<0 || count>1000000000000L)return null;
                    string key=Uri.UnescapeDataString(pair[0]);if(String.IsNullOrWhiteSpace(key) || key.Contains("\n") || key.Contains("\r"))return null;
                    var dictionary=i<5?result.Captured:result.Ammo;
                    if(dictionary.ContainsKey(key))return null;dictionary.Add(key,count);
                }
                if(result.Captured.Count!=3 || !result.Captured.ContainsKey("vessel") || !result.Captured.ContainsKey("aircraft") || !result.Captured.ContainsKey("land"))return null;
                return result;
            }
            catch(FormatException){return null;}
        }
    }

    internal static class CampaignInventory
    {
        internal const string MissionSaveKey="SestCombatInventoryV1";
        internal const string PlayerKey="SestCombatInventoryPlayerV1",EnemyKey="SestCombatInventoryEnemyV1";
        internal const string PlayerSpentKey="SestCombatExpenditurePlayerV1",EnemySpentKey="SestCombatExpenditureEnemyV1";
        static ConditionalWeakTable<object,InventoryLedger> ledgers=new ConditionalWeakTable<object,InventoryLedger>();
        static FieldInfo objectType,parameters,objectRef,registers,deck,deckAmmo,deckAccountable,player,enemy,index;
        static PropertyInfo amounts,registerRef,registerType,registerDestroyed,registerCount;
        static MethodInfo write,read,saveFile,openState,sectionName,hasSnapshot;
        static MethodInfo registerTarget,saveTarget,loadTarget,campaignTarget;
        static FieldInfo weaponsSpent,spentNumber;
        static bool active;

        internal sealed class Capture
        {
            internal object Unit;internal string Kind,Reference,Type;
            internal long Before;
            internal Dictionary<string,long> Ammo;
            internal bool Incomplete;
        }
        internal sealed class Prior
        {
            internal bool Snapshot;
            internal string Player,Enemy;
            internal string PlayerSpent,EnemySpent;
        }
        static FieldInfo Field(Type type,string name,Type expected=null)
        {
            var f=type.GetField(name,Api.All);
            if(f==null || (expected!=null && f.FieldType!=expected))throw new MissingFieldException(type.FullName,name);
            return f;
        }
        static PropertyInfo Property(Type type,string name,Type expected=null)
        {
            var p=type.GetProperty(name,Api.All);
            if(p==null || (expected!=null && p.PropertyType!=expected))throw new MissingMemberException(type.FullName,name);
            return p;
        }
        internal static void Bind(Assembly game)
        {
            Type obj=Api.Type(game,"SeaPower.ObjectBase"),obp=Api.Type(game,"SeaPower.ObjectBaseParameters"),tf=Api.Type(game,"SeaPower.Taskforce");
            Type reg=Api.Type(game,"SeaPower.UnitRegister"),ini=Api.Type(game,"SeaPower.IniHandler"),save=Api.Type(game,"SeaPower.SaveLoadManager");
            Type vm=Api.Type(game,"SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel");
            Type rules=Api.Type(game,"SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules"),mission=Api.Type(game,"SeaPower.LinearCampaignMission");
            Type debrief=Api.Type(game,"SeapowerUI.ViewModels.MissionDebriefViewModel"),globals=Api.Type(game,"SeaPower.Globals");
            objectType=Field(obj,"_type");parameters=Field(obj,"_obp",obp);objectRef=Field(obp,"_objectIniName",typeof(string));
            amounts=Property(obj,"AmmunitionAmountDictionary");registers=Field(tf,"_unitStatusRegister");
            registerRef=Property(reg,"IniRef",typeof(string));registerType=Property(reg,"ObjectType");
            registerDestroyed=Property(reg,"IsDestroyed",typeof(bool));registerCount=Property(reg,"Count",typeof(int));
            deck=Field(obp,"_flightDeck");deckAmmo=Field(deck.FieldType,"_currentAmmo");deckAccountable=Field(deck.FieldType,"_accountableAmmunition");
            if(!objectType.FieldType.IsEnum || !typeof(IEnumerable).IsAssignableFrom(amounts.PropertyType) ||
                !typeof(IEnumerable).IsAssignableFrom(registers.FieldType) ||
                (deckAmmo.FieldType!=typeof(float) && deckAmmo.FieldType!=typeof(double)))throw new MissingMemberException("inventory collection API");
            write=Api.Method(ini,"writeValue",typeof(void),typeof(string),typeof(string),typeof(string));
            read=Api.Method(ini,"readValue",typeof(string),typeof(string),typeof(string),typeof(string),typeof(bool));
            saveFile=Api.Method(ini,"saveFile",typeof(void),typeof(bool));
            openState=Api.Method(rules,"OpenCampaignStateIni",ini);
            sectionName=Api.Method(vm,"GetDebriefSectionName",typeof(string),typeof(int));
            hasSnapshot=Api.Method(vm,"HasDebriefSnapshot",typeof(bool),ini,typeof(int));
            index=Field(mission,"_index",typeof(int));player=Field(globals,"_playerTaskforce",tf);enemy=Field(globals,"_enemyTaskforce",tf);
            registerTarget=Api.Method(tf,"RegisterUnitStatus",typeof(void),typeof(bool),obj,typeof(bool),typeof(bool));
            weaponsSpent=Field(tf,"_weaponsSpent");spentNumber=Field(Api.Type(game,"SeaPower.WeaponsSpent"),"_number",typeof(int));
            saveTarget=Api.Method(save,"WriteTaskforceAarData",typeof(void),ini,tf,typeof(string));
            loadTarget=Api.Method(save,"LoadTaskforceAarData",typeof(void),ini,tf,typeof(string));
            campaignTarget=Api.Method(vm,"SaveDebriefSnapshot",typeof(void),mission,debrief);
            active=true;ledgers=new ConditionalWeakTable<object,InventoryLedger>();
        }
        internal static void Install(Assembly game)
        {
            Bind(game);
            const string owner="io.github.sest-hobby.combat-inventories";
            try
            {
                Api.Hooks(registerTarget,typeof(CampaignInventory),"BeforeRegister","AfterRegister",owner);
                Api.Postfix(saveTarget,typeof(CampaignInventory),"AfterSave",owner);
                Api.Postfix(loadTarget,typeof(CampaignInventory),"AfterLoad",owner);
                Api.Hooks(campaignTarget,typeof(CampaignInventory),"BeforeCampaignSave","AfterCampaignSave",owner);
            }
            catch{active=false;throw;}
            Api.Log("combat inventory capture installed: raw remaining quantities in versioned SEST keys; hull, airframe and land costs remain separate");
        }
        static string Kind(string type)
        {
            switch(type.ToLowerInvariant())
            {case "vessel":case "submarine":return "vessel";case "aircraft":case "helicopter":return "aircraft";case "landunit":return "land";default:return null;}
        }
        static long Count(object tf,string reference,string type)
        {
            long count=0;
            foreach(object row in (IEnumerable)registers.GetValue(tf))
                if((bool)registerDestroyed.GetValue(row,null) && String.Equals((string)registerRef.GetValue(row,null),reference,StringComparison.OrdinalIgnoreCase) &&
                    String.Equals(registerType.GetValue(row,null).ToString(),type,StringComparison.OrdinalIgnoreCase))
                    count=checked(count+(int)registerCount.GetValue(row,null));
            return count;
        }
        static InventoryLedger Ledger(object tf)
        {
            var ledger=ledgers.GetOrCreateValue(tf);
            // A reused task-force object with a fresh empty native register is
            // a new mission. The first loss prefix runs before its row is added.
            if(ledger.Captured.Count>0)
            {
                bool any=false;
                foreach(object row in (IEnumerable)registers.GetValue(tf))
                    if((bool)registerDestroyed.GetValue(row,null) && (int)registerCount.GetValue(row,null)>0){any=true;break;}
                if(!any){ledgers.Remove(tf);ledger=new InventoryLedger();ledgers.Add(tf,ledger);}
            }
            return ledger;
        }
        internal static void BeforeRegister(object __instance,bool __0,object __1,bool __2,out Capture __state)
        {
            __state=null;if(!active || __0 || !__2 || __instance==null || __1==null)return;
            try
            {
                var ledger=Ledger(__instance);if(ledger.Seen.Contains(__1))return;
                string type=objectType.GetValue(__1).ToString(),kind=Kind(type);if(kind==null)return;
                object obp=parameters.GetValue(__1);if(obp==null)return;
                var capture=new Capture{Unit=__1,Type=type,Kind=kind,Reference=(string)objectRef.GetValue(obp),Ammo=new Dictionary<string,long>(StringComparer.OrdinalIgnoreCase)};
                capture.Before=Count(__instance,capture.Reference,type);
                try
                {
                    foreach(object pair in (IEnumerable)amounts.GetValue(__1,null))
                    {
                        string key=(string)pair.GetType().GetProperty("Key").GetValue(pair,null);
                        int amount=(int)pair.GetType().GetProperty("Value").GetValue(pair,null);
                        if(amount<0){capture.Incomplete=true;continue;}
                        if(amount>0)capture.Ammo[key]=checked(InventoryLedger.Get(capture.Ammo,key)+amount);
                    }
                }
                catch(Exception){capture.Incomplete=true;}
                object flightDeck=deck.GetValue(obp);
                if(flightDeck!=null)
                {
                    // Native deck ammunition is a point pool, not a USD or an
                    // itemized stock quantity. Retain the incomplete marker.
                    if(Convert.ToDouble(deckAmmo.GetValue(flightDeck),CultureInfo.InvariantCulture)!=0)capture.Incomplete=true;
                    foreach(DictionaryEntry pair in (IDictionary)deckAccountable.GetValue(flightDeck))
                        if(Convert.ToInt64(pair.Value,CultureInfo.InvariantCulture)>0)capture.Incomplete=true;
                }
                __state=capture;
            }
            catch(Exception e){Api.LogFailure("one combat inventory capture unavailable",e);}
        }
        internal static void AfterRegister(object __instance,Capture __state)
        {
            if(!active || __state==null)return;
            try
            {
                if(Count(__instance,__state.Reference,__state.Type)!=__state.Before+1)return;
                var ledger=ledgers.GetOrCreateValue(__instance);
                if(!ledger.Seen.Add(__state.Unit))return;
                ledger.Add(__state.Kind,__state.Ammo,__state.Incomplete);
            }
            catch(Exception e){Api.LogFailure("combat inventory record unavailable",e);}
        }
        static string Read(object ini,string section,string key)
        { return (string)read.Invoke(ini,new object[]{section,key,"",false}); }
        static void Write(object ini,string section,string key,string value)
        { write.Invoke(ini,new object[]{section,key,value}); }
        internal static void AfterSave(object __0,object __1,string __2)
        {
            if(!active || __0==null || __1==null)return;
            try
            {
                Write(__0,__2,MissionSaveKey,Ledger(__1).Serialize());
                if(CombatHistory.CurrentId!=null)Write(__0,__2,CombatHistory.SessionKey,CombatHistory.CurrentId);
            }
            catch(Exception e){Api.LogFailure("combat inventory save supplement unavailable",e);}
        }
        internal static void AfterLoad(object __0,object __1,string __2)
        {
            if(!active || __0==null || __1==null)return;
            try
            {
                InventoryLedger value=InventoryLedger.Parse(Read(__0,__2,MissionSaveKey)) ?? new InventoryLedger();
                ledgers.Remove(__1);ledgers.Add(__1,value);
                CombatHistory.RestoreSession(Read(__0,__2,CombatHistory.SessionKey),__1);
            }
            catch(Exception e){Api.LogFailure("combat inventory load supplement unavailable",e);}
        }
        internal static void BeforeCampaignSave(object __0,out Prior __state)
        {
            __state=null;if(!active || __0==null)return;
            try
            {
                int i=(int)index.GetValue(__0);object ini=openState.Invoke(null,null);if(ini==null || i<1)return;
                string section=(string)sectionName.Invoke(null,new object[]{i});
                __state=new Prior{Snapshot=(bool)hasSnapshot.Invoke(null,new object[]{ini,i}),Player=Read(ini,section,PlayerKey),Enemy=Read(ini,section,EnemyKey),
                    PlayerSpent=Read(ini,section,PlayerSpentKey),EnemySpent=Read(ini,section,EnemySpentKey)};
            }
            catch(Exception e){Api.LogFailure("combat inventory campaign precheck unavailable",e);}
        }
        internal static void AfterCampaignSave(object __0,Prior __state)
        {
            if(!active || __0==null || __state==null)return;
            try
            {
                int i=(int)index.GetValue(__0);object ini=openState.Invoke(null,null);
                if(ini==null || !(bool)hasSnapshot.Invoke(null,new object[]{ini,i}))return;
                string section=(string)sectionName.Invoke(null,new object[]{i});
                string p=__state.Snapshot?__state.Player:Serialize(player.GetValue(null));
                string e=__state.Snapshot?__state.Enemy:Serialize(enemy.GetValue(null));
                string ps=__state.Snapshot?__state.PlayerSpent:SerializeSpent(player.GetValue(null));
                string es=__state.Snapshot?__state.EnemySpent:SerializeSpent(enemy.GetValue(null));
                // An old snapshot or replay without our capture stays absent.
                if(!String.IsNullOrEmpty(p))Write(ini,section,PlayerKey,p);
                if(!String.IsNullOrEmpty(e))Write(ini,section,EnemyKey,e);
                if(!String.IsNullOrEmpty(ps))Write(ini,section,PlayerSpentKey,ps);
                if(!String.IsNullOrEmpty(es))Write(ini,section,EnemySpentKey,es);
                if(!String.IsNullOrEmpty(p) || !String.IsNullOrEmpty(e) || !String.IsNullOrEmpty(ps) || !String.IsNullOrEmpty(es))saveFile.Invoke(ini,new object[]{false});
                if(CombatHistory.CurrentId!=null)
                    CombatHistory.CompleteCampaign(CampaignCosts.StateSource(ini),i,__state.Snapshot,CampaignCosts.CaptureLive("Campaign mission "+i));
            }
            catch(Exception e){Api.LogFailure("combat inventory campaign supplement unavailable; native records retained",e);}
        }
        static string Serialize(object tf)
        { return tf==null?"":Ledger(tf).Serialize(); }
        internal static InventoryLedger Current(object tf)
        { return active && tf!=null?Ledger(tf):null; }
        static string SerializeSpent(object tf)
        { return tf==null?"":Spent(tf).Serialize(); }
        internal static InventoryLedger Spent(object tf)
        {
            var result=new InventoryLedger();
            if(tf==null || weaponsSpent==null)return null;
            foreach(DictionaryEntry pair in (IDictionary)weaponsSpent.GetValue(tf))
            {
                int count=(int)spentNumber.GetValue(pair.Value);
                if(count<0){result.Unknown++;continue;}
                if(count>0)result.Ammo[(string)pair.Key]=count;
            }
            return result;
        }
    }
}
