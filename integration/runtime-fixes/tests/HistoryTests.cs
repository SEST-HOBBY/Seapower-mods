using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using Sest.RuntimeFixes;

static class HistoryTests
{
    static int checks;
    static void Check(bool value,string label){checks++;if(!value)throw new Exception("history: "+label);}
    static CombatGameRecord Record(string id,long rounds=4)
    {
        var game=new CombatGameRecord{Id=id,Name="Trial α / & <test>",EndedUtc=123456,Status="Ended"};
        var side=new CombatSideRecord{Name="Player"};side.Spent.Ammo["round"]=rounds;
        side.Platforms.Ammo["land:radar"]=1;side.Platforms.Captured["land"]=1;
        side.Stores.Captured["land"]=1;side.Stores.Ammo["decoy"]=2;
        game.Sides.Add(side);return game;
    }
    internal static int Run()
    {
        string dir=Path.Combine(Path.GetTempPath(),"sest-history-"+Guid.NewGuid().ToString("N"));Directory.CreateDirectory(dir);
        try
        {
            var raw=Record("abc");var copy=CombatGameRecord.Decode(raw.Encode());
            Check(copy.Name==raw.Name && copy.Sides[0].Spent.Ammo["round"]==4,"unicode and quantities round trip");
            Check(copy.Sides[0].Platforms.Ammo["land:radar"]==1 && copy.Context==null,"platform kinds retained; runtime identity not persisted");
            Check(CombatGameRecord.Decode("broken")==null,"malformed history record rejected");
            raw.Sides.Add(new CombatSideRecord{Name="Player"});Check(CombatGameRecord.Decode(raw.Encode())==null,"duplicate sides rejected");raw.Sides.RemoveAt(1);
            raw.Id="invalid/id";Check(CombatGameRecord.Decode(raw.Encode())==null,"invalid identities rejected");raw.Id="abc";
            var store=new CombatHistoryStore(Path.Combine(dir,"history.txt"));store.Put(raw);store.Put(Record("abc",9));
            Check(store.Games.Count==1 && store.Games[0].Sides[0].Spent.Ammo["round"]==9,"continued session replaces its own record");
            var reopened=new CombatHistoryStore(Path.Combine(dir,"history.txt"));Check(reopened.Games.Count==1,"ended sessions survive restart");
            var changed=Record("def");changed.EndedUtc=223456;reopened.Put(changed);
            Check(reopened.Games[0].Id=="def" && reopened.Games.Count==2,"newest game first");
            string path=Path.Combine(dir,"bad.txt"),bad="unknown data\nkeep this";File.WriteAllText(path,bad);
            var failed=new CombatHistoryStore(path);failed.Put(Record("new"));
            Check(failed.ReadOnly && File.ReadAllText(path)==bad,"corrupt archive preserved without replacement");

            CampaignCosts.BindMenu(Assembly.GetExecutingAssembly());CampaignInventory.Bind(Assembly.GetExecutingAssembly());
            var tf=new SeaPower.Taskforce();SeaPower.Globals._playerTaskforce=tf;SeaPower.Globals._enemyTaskforce=new SeaPower.Taskforce();
            tf._weaponsSpent["round"]=new SeaPower.WeaponsSpent{_number=4};
            tf._unitStatusRegister.Add(new SeaPower.UnitRegister{IniRef="radar",IniFolder="land_units",ObjectType=SeaPower.ObjectBase.ObjectType.LandUnit,Count=1,IsDestroyed=true});
            var live=CampaignCosts.CaptureLive("Current mission");
            Check(live.Sides[0].Platforms.Ammo["land:radar"]==1,"live native land register retained");
            Check(live.Sides[0].Stores.Unknown>0,"uncaptured past inventory incomplete");
            var lines=CampaignCosts.CampaignLines(new List<CombatGameRecord>{live},10);
            Check(lines.Any(s=>s.Contains("Land $600K")) && lines.Any(s=>s.Contains("Weapons $80")),"raw live quantities use selected catalogs");
            SeaPower.Utils.Catalogs["config"].Data["Costs"]["UseCurrentYearCosts"]="False";
            Check(CampaignCosts.CampaignLines(new List<CombatGameRecord>{live},10).Any(s=>s.Contains("Weapons $40")),"same raw game repriced when basis changes");
            SeaPower.Utils.Catalogs["config"].Data["Costs"]["UseCurrentYearCosts"]="True";

            CombatHistory.Open(Path.Combine(dir,"sessions.txt"));object context=new object();live.Context=tf;
            CombatHistory.Observe(context,live);string id=CombatHistory.CurrentId;
            var save=new SeaPower.IniHandler();CampaignInventory.AfterSave(save,tf,"Taskforce1");
            Check(save.Data["Taskforce1"][CombatHistory.SessionKey]==id,"native mid-mission save gets only own session identifier");
            CombatHistory.Observe(null,null);Check(CombatHistory.Games.Count==1,"leaving mission archives latest raw quantities");
            var resumed=new SeaPower.Taskforce();resumed._weaponsSpent["round"]=new SeaPower.WeaponsSpent{_number=6};resumed._unitStatusRegister.AddRange(tf._unitStatusRegister);
            CampaignInventory.AfterLoad(save,resumed,"Taskforce1");SeaPower.Globals._playerTaskforce=resumed;
            CombatHistory.Observe(new object(),CampaignCosts.CaptureLive("Resumed"));Check(CombatHistory.CurrentId==id,"loading mission retains session identity");
            CombatHistory.Observe(null,null);Check(CombatHistory.Games.Count==1 && CombatHistory.Games[0].Sides[0].Spent.Ammo["round"]==6,"reloaded session updates without double count");
            CombatHistory.Observe(new object(),CampaignCosts.CaptureLive("Fresh game"));Check(CombatHistory.CurrentId!=id,"reused task force does not retain consumed restored ID");
            string fresh=CombatHistory.CurrentId;
            var reset=CampaignCosts.CaptureLive("Cleared registers");reset.Sides[0].Spent.Ammo.Clear();CombatHistory.Refresh(reset);CombatHistory.Finish();
            Check(CombatHistory.Games.Single(x=>x.Id==fresh).Sides[0].Spent.Ammo["round"]==6,"teardown cannot erase expenditure with cleared registers");
            var other=CampaignCosts.CaptureLive("Next game");other.Context=new object();other.Sides[0].Spent.Ammo["round"]=999;CombatHistory.Refresh(other);CombatHistory.Finish();
            Check(CombatHistory.Games.Single(x=>x.Id==fresh).Sides[0].Spent.Ammo["round"]==6,"teardown cannot replace history with a different task force");
            resumed._weaponsSpent["round"]._number=7;CombatHistory.Refresh(CampaignCosts.CaptureLive("Final shot"));CombatHistory.Finish();
            Check(CombatHistory.Games.Single(x=>x.Id==fresh).Sides[0].Spent.Ammo["round"]==7,"final accepted snapshot retains last shot");
            CombatHistory.CompleteCampaign("campaign-hash",4,false,CampaignCosts.CaptureLive("Finished"));
            Check(CombatHistory.Games.Count==2 && CombatHistory.Games.Any(x=>x.MissionIndex==4&&x.Status=="Completed"),"completed campaign tagged separately");
            CombatHistory.Observe(null,null);CombatHistory.Observe(new object(),CampaignCosts.CaptureLive("Replay"));
            CombatHistory.CompleteCampaign("campaign-hash",4,true,CampaignCosts.CaptureLive("Replay"));
            Check(CombatHistory.Games.Count==3 && CombatHistory.Games.Count(x=>x.Status=="Replay")==1,"replay retained once as its own session");

            var state=new SeaPower.IniHandler{FilePath="test-current-campaign.ini"};
            state.Data["Mission_1_TaskForceDebrief"]=new Dictionary<string,string>{{"Complete","True"},{"MissionName","Old mission"},{"PlayerWeaponReport",""},{"EnemyWeaponReport",""},{"LossRows",""},{"KillRows",""}};
            state.Data["Mission_2_TaskForceDebrief"]=new Dictionary<string,string>{{"Complete","True"},{"PlayerWeaponReport",""},{"EnemyWeaponReport",""},{"LossRows","radar|land_units|LandUnit|1|lost"},{"KillRows",""}};
            state.Data["Mission_3_TaskForceDebrief"]=new Dictionary<string,string>{{"LossRows",""}};
            SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules.State=state;
            var saved=CampaignCosts.SavedGames();
            Check(saved.Count==2 && saved[0].MissionIndex==2,"history imports only completed exact native debriefs");
            Check(saved[1].Name=="Old mission" && saved[1].EndedUtc==0,"old debrief name retained without inventing date");
            Check(saved[0].Sides[0].Stores.Unknown>0,"old lost magazines remain unknown");
            lines=CampaignCosts.CampaignLines(saved,10);
            Check(lines.Any(x=>x.Contains("Land $600K")),"campaign totals include saved land losses");
            Check(lines[0].EndsWith("2 completed missions.") && lines.Any(x=>x.StartsWith("1. Old mission")) && lines.Any(x=>x.StartsWith("2. Campaign mission 2")),"one line per completed mission under the totals");
            Check(CampaignCosts.CampaignLines(saved,1).Any(x=>x=="+ 1 earlier missions, included in the totals"),"long campaigns list the latest missions and keep all in the totals");
            Check(state.Writes==0 && state.Saves==0,"viewing history and totals never writes campaign saves");
            CombatHistory.Observe(null,null);

            // Stores lost before the .sav fix: recover them from the one local
            // record of that completed mission whose losses match exactly.
            string legacy;using(var sha=System.Security.Cryptography.SHA256.Create())
                legacy=BitConverter.ToString(sha.ComputeHash(System.Text.Encoding.UTF8.GetBytes(state.FilePath))).Replace("-","").ToLowerInvariant();
            Func<string,string,long,CombatGameRecord> completed=(key,origin,decoys)=>{
                var g=Record(key);g.Status="Completed";g.MissionIndex=2;g.Source=origin;g.Sides[0].Stores.Ammo["decoy"]=decoys;return g;};
            Action<CombatGameRecord[]> archive=games=>{
                string file=Path.Combine(dir,"recover-"+Guid.NewGuid().ToString("N")+".txt");
                File.WriteAllLines(file,new[]{"SEST-COMBAT-HISTORY-1"}.Concat(games.Select(g=>g.Encode())));CombatHistory.Open(file);};
            archive(new[]{completed("one",legacy,2)});saved=CampaignCosts.SavedGames();
            Check(saved[0].Sides[0].Stores.Ammo["decoy"]==2 && saved[0].Sides[0].Stores.Unknown==0 && saved[0].Status=="Saved debrief + local record","stores lost in a mission completed before the fix recovered from its local record");
            Check(saved[0].Sides[0].Spent.Ammo["round"]==4,"the same record supplies the full expenditure");
            Check(state.Writes==0 && state.Saves==0,"recovery reads only; the campaign save is not rewritten");
            archive(new[]{completed("one",legacy,2),completed("two",legacy,5)});
            Check(CampaignCosts.SavedGames()[0].Sides[0].Stores.Unknown>0,"two candidate records: nothing guessed");
            var other2=completed("three",legacy,2);other2.Sides[0].Platforms.Ammo["land:radar"]=2;archive(new[]{other2});
            Check(CampaignCosts.SavedGames()[0].Sides[0].Stores.Unknown>0,"a record with different losses is not used");
            archive(new[]{completed("four","another-campaign",2)});
            Check(CampaignCosts.SavedGames()[0].Sides[0].Stores.Unknown>0,"a record from another campaign is not used");
            SeaPower.SaveLoadManager.CampaignSave="saves/Red Line.sav";string a=CampaignCosts.CampaignSource(state);
            SeaPower.SaveLoadManager.CampaignSave="saves/Steel Highway.sav";string b=CampaignCosts.CampaignSource(state);
            SeaPower.SaveLoadManager.CampaignSave="";
            Check(a!=b && CampaignCosts.CampaignSource(state)==legacy,"each campaign .sav names its own campaign");
            archive(new[]{completed("five",b,2)});SeaPower.SaveLoadManager.CampaignSave="saves/Steel Highway.sav";
            Check(CampaignCosts.SavedGames()[0].Sides[0].Stores.Ammo["decoy"]==2,"records written with the campaign identity also recover");
            SeaPower.SaveLoadManager.CampaignSave="saves/Test campaign.sav";
            CombatHistory.Observe(null,null);
        }
        finally{Directory.Delete(dir,true);}
        return checks;
    }
}
