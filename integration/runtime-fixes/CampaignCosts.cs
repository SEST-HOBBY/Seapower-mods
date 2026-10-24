using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using System.Text.RegularExpressions;
using System.Security.Cryptography;
using System.Text;

namespace Sest.RuntimeFixes
{
    // Re-price the game's saved debrief records. No dependency on tracker
    // execution, overlay visibility or its private loss ledger. No save writes.
    internal static class CampaignCosts
    {
        static MethodInfo openState, hasSnapshot, sectionName, parseRows, reports, totals, data, openVirtual, openUnit;
        static MethodInfo filePath,openCampaign,taskforceEnabled;
        static PropertyInfo summaryRows, ammoRef, ammoType, launched, fired;
        static FieldInfo missionIndex, rowRef, rowFolder, rowType, rowCount, rowDestroyed;
        static ConstructorInfo summaryConstructor;
        static FieldInfo liveRegisters,liveSpent,spentCount;
        static PropertyInfo liveRef,liveFolder,liveType,liveCount,liveDestroyed;
        static readonly List<FieldInfo> liveSides=new List<FieldInfo>();
        static bool active, missingListsReported;
        static readonly HashSet<string> warned = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        internal static MethodInfo Bind(Assembly game)
        {
            Type vm=Api.Type(game,"SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel");
            Type row=Api.Type(game,"SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefRegisterSnapshotRow");
            Type summary=Api.Type(game,"SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefSummaryRow");
            Type rules=Api.Type(game,"SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules");
            Type ini=Api.Type(game,"SeaPower.IniHandler"),mission=Api.Type(game,"SeaPower.LinearCampaignMission");
            Type report=Api.Type(game,"SeaPower.TaskforceWeaponReport"),ammo=Api.Type(game,"SeaPower.WeaponReportAmmoData");
            Type utils=Api.Type(game,"SeaPower.Utils");
            openState=Api.Method(rules,"OpenCampaignStateIni",ini);
            hasSnapshot=Api.Method(vm,"HasDebriefSnapshot",typeof(bool),ini,typeof(int));
            sectionName=Api.Method(vm,"GetDebriefSectionName",typeof(string),typeof(int));
            parseRows=Api.Method(vm,"TryParseRegisterRows",typeof(bool),typeof(string),typeof(List<>).MakeGenericType(row).MakeByRefType());
            reports=Api.Method(vm,"TryReadWeaponReports",typeof(bool),ini,typeof(int),report.MakeByRefType(),report.MakeByRefType(),report.MakeByRefType());
            totals=Api.Method(report,"BuildTaskforceTotals",typeof(Dictionary<,>).MakeGenericType(typeof(string),ammo));
            data=Api.Method(ini,"get_Data",typeof(Dictionary<string,Dictionary<string,string>>));
            openVirtual=Api.Method(utils,"openVirtualIniFile",ini,typeof(string),typeof(string),typeof(string),typeof(bool));
            openUnit=Api.Method(utils,"openIniFile",ini,typeof(string),typeof(string),typeof(bool),typeof(bool));
            summaryRows=vm.GetProperty("SummaryRows",Api.All);
            missionIndex=mission.GetField("_index",Api.All);
            summaryConstructor=summary.GetConstructor(new[]{typeof(string),typeof(string),typeof(bool),typeof(bool)});
            rowRef=Field(row,"IniRef",typeof(string)); rowFolder=Field(row,"Folder",typeof(string));
            rowType=Field(row,"ObjectType",typeof(string)); rowCount=Field(row,"Count",typeof(int));
            rowDestroyed=Field(row,"IsDestroyed",typeof(bool));
            ammoRef=Property(ammo,"AmmoRef",typeof(string)); ammoType=ammo.GetProperty("AmmoType",Api.All);
            launched=Property(ammo,"Launched",typeof(int)); fired=Property(ammo,"ProjectileFired",typeof(int));
            if (summaryRows==null || missionIndex==null || missionIndex.FieldType!=typeof(int) || summaryConstructor==null ||
                ammoType==null || !ammoType.PropertyType.IsEnum) throw new MissingMemberException("campaign combat costs API");
            active=true; missingListsReported=false; warned.Clear();
            return Api.Method(vm,"Load",typeof(void),mission);
        }

        internal static void BindLive(Assembly game)
        {
            Bind(game);
            Type tf=Api.Type(game,"SeaPower.Taskforce"),reg=Api.Type(game,"SeaPower.UnitRegister");
            liveRegisters=Field(tf,"_unitStatusRegister",typeof(List<>).MakeGenericType(reg));
            Type spent=Api.Type(game,"SeaPower.WeaponsSpent");
            liveSpent=Field(tf,"_weaponsSpent",typeof(Dictionary<,>).MakeGenericType(typeof(string),spent));
            spentCount=Field(spent,"_number",typeof(int));
            liveRef=Property(reg,"IniRef",typeof(string));liveFolder=Property(reg,"IniFolder",typeof(string));
            liveType=reg.GetProperty("ObjectType",Api.All);liveCount=Property(reg,"Count",typeof(int));
            liveDestroyed=Property(reg,"IsDestroyed",typeof(bool));
            if(liveType==null || !liveType.PropertyType.IsEnum)throw new MissingMemberException("live unit-register type");
            var globals=Api.Type(game,"SeaPower.Globals");liveSides.Clear();
            foreach(string name in new[]{"_playerTaskforce","_enemyTaskforce","_allyTaskforce","_neutralTaskforce"})
            {
                FieldInfo field=globals.GetField(name,Api.All);
                if(field!=null && field.FieldType==tf)liveSides.Add(field);
            }
            if(liveSides.Count<2)throw new MissingMemberException("live player/enemy task forces");
        }

        internal static void BindMenu(Assembly game)
        {
            BindLive(game);
            var ini=Api.Type(game,"SeaPower.IniHandler");
            var rules=Api.Type(game,"SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules");
            filePath=Api.Method(ini,"getFilePath",typeof(string));
            openCampaign=Api.Method(rules,"OpenCampaignIni",ini);
            taskforceEnabled=Api.Method(rules,"IsTaskForceModeEnabled",typeof(bool),ini);
        }

        internal static bool TaskForceMenuAvailable()
        {
            try {object ini=openCampaign.Invoke(null,null);return ini!=null&&(bool)taskforceEnabled.Invoke(null,new[]{ini});}
            catch{return false;}
        }

        internal static string StateSource(object ini)
        {
            string path=(string)filePath.Invoke(ini,null);
            using(var hash=SHA256.Create())return BitConverter.ToString(hash.ComputeHash(Encoding.UTF8.GetBytes(path ?? ""))).Replace("-","").ToLowerInvariant();
        }

        static string SideName(string field)
        {string name=field.Replace("_","").Replace("Taskforce","");return Char.ToUpperInvariant(name[0])+name.Substring(1);}

        static string PlatformKind(string type)
        {
            switch((type ?? "").ToLowerInvariant())
            {case "vessel":case "submarine":return "vessel";case "aircraft":case "helicopter":return "aircraft";case "landunit":return "land";default:return null;}
        }
        static void RawPlatform(CombatSideRecord side,string reference,string type,long count)
        {
            string kind=PlatformKind(type);
            if(kind==null||String.IsNullOrWhiteSpace(reference)||count<=0){side.Platforms.Unknown++;return;}
            string key=kind+":"+reference;
            side.Platforms.Ammo[key]=checked(InventoryLedger.Get(side.Platforms.Ammo,key)+count);
            side.Platforms.Captured[kind]=checked(InventoryLedger.Get(side.Platforms.Captured,kind)+count);
        }
        static void RawStores(CombatSideRecord side,InventoryLedger ledger)
        {
            side.Stores=ledger==null?new InventoryLedger():InventoryLedger.Parse(ledger.Serialize());
            if(ledger==null && side.Platforms.Ammo.Count>0)side.Stores.Unknown++;
            if(ledger!=null)
                foreach(string kind in new[]{"vessel","aircraft","land"})
                    if(InventoryLedger.Get(ledger.Captured,kind)!=InventoryLedger.Get(side.Platforms.Captured,kind))side.Stores.Unknown++;
        }
        internal static CombatGameRecord CaptureLive(string name)
        {
            var record=new CombatGameRecord{Name=name};
            foreach(var field in liveSides)
            {
                object tf=field.GetValue(null);if(tf==null)continue;
                if(field.Name=="_playerTaskforce")record.Context=tf;
                var side=new CombatSideRecord{Name=SideName(field.Name),Spent=CampaignInventory.Spent(tf) ?? new InventoryLedger{Unknown=1}};
                foreach(object row in (IEnumerable)liveRegisters.GetValue(tf))
                    if((bool)liveDestroyed.GetValue(row,null))RawPlatform(side,(string)liveRef.GetValue(row,null),liveType.GetValue(row,null).ToString(),(int)liveCount.GetValue(row,null));
                RawStores(side,CampaignInventory.Current(tf));record.Sides.Add(side);
            }
            return record;
        }
        static CombatSideRecord CaptureSavedSide(object report,string weapons,string losses,string stores,string captured,string name)
        {
            var side=new CombatSideRecord{Name=name};
            var spent=InventoryLedger.Parse(captured);
            if(spent!=null)side.Spent=spent;
            else if(weapons==null || (weapons.Length>0&&report==null))side.Spent.Unknown++;
            else if(weapons.Length>0)
                foreach(DictionaryEntry pair in (IDictionary)totals.Invoke(report,null))
                {
                    object ammo=pair.Value;long count=(long)(int)launched.GetValue(ammo,null)+(int)fired.GetValue(ammo,null);
                    if(count<0){side.Spent.Unknown++;continue;}
                    string reference=(string)ammoRef.GetValue(ammo,null);
                    side.Spent.Ammo[reference]=checked(InventoryLedger.Get(side.Spent.Ammo,reference)+count);
                }
            if(losses==null)side.Platforms.Unknown++;
            else if(losses.Length>0)
            {
                object[] args={losses,null};
                if(!(bool)parseRows.Invoke(null,args)||args[1]==null)side.Platforms.Unknown++;
                else foreach(object row in (IEnumerable)args[1])
                    if((bool)rowDestroyed.GetValue(row))RawPlatform(side,(string)rowRef.GetValue(row),(string)rowType.GetValue(row),(int)rowCount.GetValue(row));
            }
            RawStores(side,InventoryLedger.Parse(stores));return side;
        }
        internal static List<CombatGameRecord> SavedGames()
        {
            var games=new List<CombatGameRecord>();if(!TaskForceMenuAvailable())return games;
            object ini=openState.Invoke(null,null);if(ini==null)return games;
            string source=StateSource(ini);
            foreach(var section in Data(ini))
            {
                Match match=Regex.Match(section.Key,"\\AMission_([0-9]+)_TaskForceDebrief\\z");int index;
                if(!match.Success||!Int32.TryParse(match.Groups[1].Value,out index)||index<1||!(bool)hasSnapshot.Invoke(null,new object[]{ini,index}))continue;
                object[] reportsArgs={ini,index,null,null,null};try{reports.Invoke(null,reportsArgs);}catch{ }
                string name=CombatPrices.Get(section.Value,"MissionName") ?? "Campaign mission "+index;
                var r=new CombatGameRecord{Id="saved:"+source+":"+index,Name=name,Source=source,MissionIndex=index,Status="Saved debrief"};
                r.Sides.Add(CaptureSavedSide(reportsArgs[2],CombatPrices.Get(section.Value,"PlayerWeaponReport"),CombatPrices.Get(section.Value,"LossRows"),CombatPrices.Get(section.Value,CampaignInventory.PlayerKey),CombatPrices.Get(section.Value,CampaignInventory.PlayerSpentKey),"Player"));
                r.Sides.Add(CaptureSavedSide(reportsArgs[3],CombatPrices.Get(section.Value,"EnemyWeaponReport"),CombatPrices.Get(section.Value,"KillRows"),CombatPrices.Get(section.Value,CampaignInventory.EnemyKey),CombatPrices.Get(section.Value,CampaignInventory.EnemySpentKey),"Enemy"));
                games.Add(r);
            }
            games.Sort((a,b)=>b.MissionIndex.CompareTo(a.MissionIndex));return games;
        }
        static Side PriceRaw(CombatSideRecord raw,CombatPrices prices)
        {
            var side=new Side();
            foreach(var pair in raw.Spent.Ammo)side.Weapons.Add(Price(prices,"weapon",pair.Key,"ammunition"),pair.Value);
            side.Weapons.MissingRecords=raw.Spent.Unknown;
            foreach(var pair in raw.Platforms.Ammo)
            {
                int colon=pair.Key.IndexOf(':');if(colon<1){side.Ships.MissingRecords++;continue;}
                string kind=pair.Key.Substring(0,colon),reference=pair.Key.Substring(colon+1);
                if(kind!="vessel"&&kind!="aircraft"&&kind!="land"){side.Ships.MissingRecords++;continue;}
                var bucket=kind=="vessel"?side.Ships:kind=="aircraft"?side.Air:side.Land;
                bucket.Add(Price(prices,kind,reference,kind=="vessel"?"vessels":kind=="aircraft"?"aircraft":"land_units"),pair.Value);
            }
            side.Ships.MissingRecords+=raw.Platforms.Unknown;
            foreach(var pair in raw.Stores.Ammo)side.Stores.Add(Price(prices,"weapon",pair.Key,"ammunition"),pair.Value);
            side.Stores.MissingRecords=raw.Stores.Unknown;return side;
        }
        internal static string[] GameLines(IEnumerable<CombatGameRecord> records,bool detail)
        {
            var prices=Prices();if(prices==null)return new[]{"Enable Combat Cost Tracker and restart to load prices."};
            var sides=new Dictionary<string,Side>();int count=0;
            foreach(var r in records)
            {count++;foreach(var raw in r.Sides){Side side;if(!sides.TryGetValue(raw.Name,out side))sides[raw.Name]=side=new Side();side.Merge(PriceRaw(raw,prices));}}
            var lines=new List<string>{"USD estimates / "+prices.Basis+" / "+count+" recorded game"+(count==1?"":"s")};
            foreach(string name in new[]{"Player","Enemy","Ally","Neutral"})
            {
                Side side;if(!sides.TryGetValue(name,out side))continue;
                lines.Add(name+" total: "+side.Total.Text);
                if(detail)
                {
                    lines.Add("  Weapons "+side.Weapons.Text+" | Ships "+side.Ships.Text+" | Aircraft "+side.Air.Text);
                    lines.Add("  Land "+side.Land.Text+" | Stores lost "+side.Stores.Text);
                }
            }
            lines.Add("+ ? = missing prices or quantities, including virtual deck pools.");
            return lines.ToArray();
        }

        static FieldInfo Field(Type type,string name,Type expected)
        {
            var field=type.GetField(name,Api.All);
            if (field==null || field.FieldType!=expected) throw new MissingFieldException(type.FullName,name);
            return field;
        }
        static PropertyInfo Property(Type type,string name,Type expected)
        {
            var property=type.GetProperty(name,Api.All);
            if (property==null || property.PropertyType!=expected) throw new MissingMemberException(type.FullName,name);
            return property;
        }
        internal static void Install(Assembly game)
        {
            var target=Bind(game);
            Api.Postfix(target,typeof(CampaignCosts),"Postfix","io.github.sest-hobby.campaign-combat-costs");
            Api.Log("campaign combat costs installed: saved debrief weapons, ship, air and land losses; independent of tracker display");
        }

        static Dictionary<string,Dictionary<string,string>> Data(object ini)
        {
            if (ini==null) return new Dictionary<string,Dictionary<string,string>>();
            return (Dictionary<string,Dictionary<string,string>>)data.Invoke(ini,null);
        }
        static Dictionary<string,Dictionary<string,string>> Catalog(string name,string folder="systems")
        {
            return Data(openVirtual.Invoke(null,new object[]{folder,name,name,false}));
        }
        static CombatPrices Prices()
        {
            var lists=new Dictionary<string,Dictionary<string,Dictionary<string,string>>>();
            foreach (string kind in new[]{"weapon","vessel","aircraft"})
            {
                lists[kind]=Catalog(kind+"costs");
                if (CombatPrices.Section(lists[kind],"Costs").Count==0) return null;
            }
            lists["land"]=Catalog("sest_land_costs");
            return new CombatPrices(lists,Catalog("config","systems/combatcosts"),(folder,reference)=>{
                object ini=openUnit.Invoke(null,new object[]{"/"+folder,"/"+reference+".ini",false,true});
                return CombatPrices.Section(Data(ini),"General");
            });
        }

        sealed class Side
        {
            internal CombatAmount Weapons=new CombatAmount(),Ships=new CombatAmount(),Air=new CombatAmount(),Land=new CombatAmount(),Stores=new CombatAmount();
            internal CombatAmount Losses { get { return CombatAmount.Sum(Ships,Air,Land); } }
            internal CombatAmount Total { get { return CombatAmount.Sum(Weapons,Ships,Air,Land,Stores); } }
            internal void Merge(Side other)
            {
                Weapons.Merge(other.Weapons); Ships.Merge(other.Ships); Air.Merge(other.Air); Land.Merge(other.Land); Stores.Merge(other.Stores);
            }
        }
        sealed class Mission
        {
            internal int Index;
            internal Side Player=new Side(),Enemy=new Side();
        }

        static CombatPrice Price(CombatPrices prices,string kind,string reference,string folder,string type=null)
        {
            try
            {
                var result=prices.Read(kind,reference,folder,type);
                if (!result.Amount.HasValue && !result.Ignored) Warn(kind+" "+reference+": no "+prices.Basis+" price");
                return result;
            }
            catch (Exception e)
            {
                Warn(kind+" "+reference+": "+e.GetType().Name);
                return new CombatPrice();
            }
        }
        static void Warn(string message)
        {
            if (warned.Count<20 && warned.Add(message)) Api.Log("combat costs: "+message);
        }

        static void Weapons(Side side,CombatPrices prices,object report,string raw,string captured=null)
        {
            var ledger=InventoryLedger.Parse(captured);
            if(ledger!=null)
            {
                foreach(var pair in ledger.Ammo)side.Weapons.Add(Price(prices,"weapon",pair.Key,"ammunition"),pair.Value);
                side.Weapons.MissingRecords=ledger.Unknown;return;
            }
            if (raw==null) { side.Weapons.MissingRecords++; return; }
            if (raw.Length==0) return; // Native encoding of no weapons fired.
            if (report==null) { side.Weapons.MissingRecords++; return; }
            foreach (DictionaryEntry pair in (IDictionary)totals.Invoke(report,null))
            {
                object ammo=pair.Value;
                long count=(long)(int)launched.GetValue(ammo,null)+(int)fired.GetValue(ammo,null);
                if (count<0) { side.Weapons.MissingRecords++; continue; }
                string reference=(string)ammoRef.GetValue(ammo,null);
                string type=ammoType.GetValue(ammo,null).ToString();
                side.Weapons.Add(Price(prices,"weapon",reference,"ammunition",type),count);
            }
        }

        static void Losses(Side side,CombatPrices prices,string raw)
        {
            if (raw==null) { side.Ships.MissingRecords++; return; }
            if (raw.Length==0) return;
            object[] args={raw,null};
            if (!(bool)parseRows.Invoke(null,args) || args[1]==null) { side.Ships.MissingRecords++; return; }
            foreach (object row in (IEnumerable)args[1])
            {
                if (!(bool)rowDestroyed.GetValue(row)) continue;
                int count=(int)rowCount.GetValue(row);
                if (count<=0) { side.Ships.MissingRecords++; continue; }
                string reference=(string)rowRef.GetValue(row),folder=(string)rowFolder.GetValue(row),type=(string)rowType.GetValue(row);
                AddPlatform(side,prices,reference,folder,type,count);
            }
        }

        static void AddPlatform(Side side,CombatPrices prices,string reference,string folder,string type,int count)
        {
                string kind; CombatAmount bucket;
                if (String.Equals(type,"Vessel",StringComparison.OrdinalIgnoreCase) || String.Equals(type,"Submarine",StringComparison.OrdinalIgnoreCase))
                { kind="vessel"; folder=String.IsNullOrWhiteSpace(folder)?"vessels":folder; bucket=side.Ships; }
                else if (String.Equals(type,"Aircraft",StringComparison.OrdinalIgnoreCase) || String.Equals(type,"Helicopter",StringComparison.OrdinalIgnoreCase))
                { kind="aircraft"; folder="aircraft"; bucket=side.Air; }
                else if (String.Equals(folder,"land_units",StringComparison.OrdinalIgnoreCase) || String.Equals(type,"LandUnit",StringComparison.OrdinalIgnoreCase))
                { kind="land"; folder="land_units"; bucket=side.Land; }
                else { side.Ships.MissingRecords++; return; }
                bucket.Add(Price(prices,kind,reference,folder),count);
        }

        static void Inventories(Side side,CombatPrices prices,string saved)
        {
            var ledger=InventoryLedger.Parse(saved);
            if(ledger==null)
            { if(side.Losses.Count>0)side.Stores.MissingRecords++;return; }
            foreach(var pair in ledger.Ammo)side.Stores.Add(Price(prices,"weapon",pair.Key,"ammunition"),pair.Value);
            side.Stores.MissingRecords=ledger.Unknown;
            if(InventoryLedger.Get(ledger.Captured,"vessel")!=side.Ships.Count ||
                InventoryLedger.Get(ledger.Captured,"aircraft")!=side.Air.Count ||
                InventoryLedger.Get(ledger.Captured,"land")!=side.Land.Count)side.Stores.MissingRecords++;
        }

        static Mission Read(object ini,Dictionary<string,string> section,int index,CombatPrices prices)
        {
            var result=new Mission{Index=index};
            object[] args={ini,index,null,null,null};
            try{reports.Invoke(null,args);}catch(Exception){Warn("one native weapon report could not be parsed; retained captures are still used");}
            Weapons(result.Player,prices,args[2],CombatPrices.Get(section,"PlayerWeaponReport"),CombatPrices.Get(section,CampaignInventory.PlayerSpentKey));
            Weapons(result.Enemy,prices,args[3],CombatPrices.Get(section,"EnemyWeaponReport"),CombatPrices.Get(section,CampaignInventory.EnemySpentKey));
            Losses(result.Player,prices,CombatPrices.Get(section,"LossRows"));
            Losses(result.Enemy,prices,CombatPrices.Get(section,"KillRows"));
            Inventories(result.Player,prices,CombatPrices.Get(section,CampaignInventory.PlayerKey));
            Inventories(result.Enemy,prices,CombatPrices.Get(section,CampaignInventory.EnemyKey));
            return result;
        }

        static string Pair(CombatAmount player,CombatAmount enemy)
        { return "Player "+player.Text+" | Enemy "+enemy.Text; }

        internal static string LiveSummary()
        {
            var prices=Prices();if(prices==null)return "Enable Combat Cost Tracker and SEST, then restart the game to load the price catalogs.";
            var lines=new List<string>();
            foreach(var field in liveSides)
            {
                object tf=field.GetValue(null);if(tf==null)continue;
                var side=new Side();
                foreach(DictionaryEntry pair in (IDictionary)liveSpent.GetValue(tf))
                {
                    int count=(int)spentCount.GetValue(pair.Value);
                    if(count<0){side.Weapons.MissingRecords++;continue;}
                    side.Weapons.Add(Price(prices,"weapon",(string)pair.Key,"ammunition"),count);
                }
                foreach(object row in (IEnumerable)liveRegisters.GetValue(tf))
                    if((bool)liveDestroyed.GetValue(row,null))
                    {
                        int count=(int)liveCount.GetValue(row,null);
                        if(count<=0){side.Ships.MissingRecords++;continue;}
                        AddPlatform(side,prices,(string)liveRef.GetValue(row,null),(string)liveFolder.GetValue(row,null),liveType.GetValue(row,null).ToString(),count);
                    }
                var ledger=CampaignInventory.Current(tf);
                Inventories(side,prices,ledger==null?null:ledger.Serialize());
                string name=field.Name.Replace("_","").Replace("Taskforce","");
                name=Char.ToUpperInvariant(name[0])+name.Substring(1);
                lines.Add(name+": "+side.Total.Text);
                lines.Add("  Expended "+side.Weapons.Text+"; ships "+side.Ships.Text+"; aircraft "+side.Air.Text);
                lines.Add("  Land "+side.Land.Text+"; remaining stores lost "+side.Stores.Text);
            }
            lines.Add("");lines.Add("USD estimates, "+prices.Basis+". + ? = unpriced items or quantities not captured, including virtual deck stock pools.");
            lines.Add("Aircraft include recorded deck/ground losses. Crew, damage, repairs and fuel consumption are outside this material-loss account.");
            return String.Join("\n",lines);
        }

        internal static void Postfix(object __instance,object __0)
        {
            if (!active || __instance==null || __0==null) return;
            IList target=null; int before=0;
            try
            {
                int index=(int)missionIndex.GetValue(__0);
                object ini=openState.Invoke(null,null);
                if (ini==null || !(bool)hasSnapshot.Invoke(null,new object[]{ini,index})) return;
                var prices=Prices();
                if (prices==null)
                {
                    if (!missingListsReported) { missingListsReported=true; Api.Log("combat costs: tracker price lists not enabled; debrief rows not shown"); }
                    return;
                }
                var state=Data(ini); var campaign=new Mission(); Mission current=null; int completed=0;
                foreach (var section in state)
                {
                    Match match=Regex.Match(section.Key,"\\AMission_([0-9]+)_TaskForceDebrief\\z",RegexOptions.CultureInvariant);
                    int i;
                    if (!match.Success || !Int32.TryParse(match.Groups[1].Value,out i) || i<1) continue;
                    if (!String.Equals((string)sectionName.Invoke(null,new object[]{i}),section.Key,StringComparison.OrdinalIgnoreCase) ||
                        !(bool)hasSnapshot.Invoke(null,new object[]{ini,i})) continue;
                    var mission=Read(ini,section.Value,i,prices); completed++;
                    campaign.Player.Merge(mission.Player); campaign.Enemy.Merge(mission.Enemy);
                    if (i==index) current=mission;
                }
                if (current==null) return;
                var rows=new List<object>();
                Action<string,string> add=(label,value)=>rows.Add(summaryConstructor.Invoke(new object[]{label,value,false,false}));
                add("Combat Cost: Weapons",Pair(current.Player.Weapons,current.Enemy.Weapons));
                add("Combat Cost: Ships",Pair(current.Player.Ships,current.Enemy.Ships));
                add("Combat Cost: Aircraft",Pair(current.Player.Air,current.Enemy.Air));
                add("Combat Cost: Land",Pair(current.Player.Land,current.Enemy.Land));
                add("Combat Cost: Lost Stores",Pair(current.Player.Stores,current.Enemy.Stores));
                add("Combat Cost: Mission",Pair(current.Player.Total,current.Enemy.Total));
                add("Combat Cost: Campaign",Pair(campaign.Player.Total,campaign.Enemy.Total)+" ("+completed+" "+(completed==1?"mission":"missions")+")");
                add("Combat Cost: Basis","USD estimates, "+prices.Basis+"; updated catalogs re-price prior missions");
                if (campaign.Player.Stores.Incomplete || campaign.Enemy.Stores.Incomplete)
                    add("Combat Cost: Incomplete","+ ? includes remaining stores not captured, virtual flight-deck stock pools or incomplete native records");
                long unpriced=current.Player.Total.Unknown+current.Enemy.Total.Unknown;
                if (unpriced>0) add("Combat Cost: Unpriced",unpriced.ToString(CultureInfo.InvariantCulture)+" counted items without a selected-basis price");
                target=summaryRows.GetValue(__instance,null) as IList;
                if (target==null) throw new InvalidOperationException("summary rows are not a mutable native collection");
                before=target.Count;
                foreach (object row in rows) target.Add(row);
                Api.Log("combat costs mission "+index+" ("+prices.Basis+"): "+Pair(current.Player.Total,current.Enemy.Total)+
                    "; campaign "+completed+": "+Pair(campaign.Player.Total,campaign.Enemy.Total)+"; saved quantities only; debrief re-pricing writes no data");
            }
            catch (Exception e)
            {
                if (target!=null) { try { while (target.Count>before) target.RemoveAt(target.Count-1); } catch { } }
                active=false; Api.LogFailure("campaign combat costs disabled for this session; native debrief retained",e);
            }
        }
    }
}
