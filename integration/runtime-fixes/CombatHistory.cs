using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Runtime.CompilerServices;

namespace Sest.RuntimeFixes
{
    // Raw quantities only. Changing a catalog or basis reprices past games.
    internal sealed class CombatSideRecord
    {
        internal string Name;
        internal InventoryLedger Spent=new InventoryLedger(),Platforms=new InventoryLedger(),Stores=new InventoryLedger();
    }
    internal sealed class CombatGameRecord
    {
        internal string Id,Name,Source="",Status="Ended";
        internal int MissionIndex;
        internal long EndedUtc;
        internal object Context; // runtime identity only; never serialized
        internal readonly List<CombatSideRecord> Sides=new List<CombatSideRecord>();
        internal string Encode()
        {
            var lines=new List<string>{"SEST-COMBAT-GAME-1",Id,EndedUtc.ToString(CultureInfo.InvariantCulture),
                Uri.EscapeDataString(Name ?? "Game"),Uri.EscapeDataString(Source ?? ""),
                MissionIndex.ToString(CultureInfo.InvariantCulture),Uri.EscapeDataString(Status ?? "Ended")};
            foreach(var s in Sides)lines.Add(Uri.EscapeDataString(s.Name)+"\t"+s.Spent.Serialize()+"\t"+s.Platforms.Serialize()+"\t"+s.Stores.Serialize());
            return Convert.ToBase64String(Encoding.UTF8.GetBytes(String.Join("\n",lines)));
        }
        internal static CombatGameRecord Decode(string text)
        {
            if(String.IsNullOrWhiteSpace(text)||text.Length>12000000)return null;
            try
            {
                var lines=Encoding.UTF8.GetString(Convert.FromBase64String(text)).Split('\n');long ticks;int index;
                if(lines.Length<7||lines.Length>11||lines[0]!="SEST-COMBAT-GAME-1" ||
                    !Regex.IsMatch(lines[1],"\\A[A-Za-z0-9:_-]{1,160}\\z") ||
                    !Int64.TryParse(lines[2],NumberStyles.None,CultureInfo.InvariantCulture,out ticks)||ticks<0||ticks>DateTime.MaxValue.Ticks ||
                    !Int32.TryParse(lines[5],NumberStyles.None,CultureInfo.InvariantCulture,out index)||index<0)return null;
                var r=new CombatGameRecord{Id=lines[1],EndedUtc=ticks,Name=Uri.UnescapeDataString(lines[3]),Source=Uri.UnescapeDataString(lines[4]),MissionIndex=index,Status=Uri.UnescapeDataString(lines[6])};
                if(r.Name.Length>512||r.Source.Length>256||r.Status.Length>80)return null;
                var names=new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                for(int i=7;i<lines.Length;i++)
                {
                    var p=lines[i].Split('\t');if(p.Length!=4)return null;
                    var s=new CombatSideRecord{Name=Uri.UnescapeDataString(p[0]),Spent=InventoryLedger.Parse(p[1]),Platforms=InventoryLedger.Parse(p[2]),Stores=InventoryLedger.Parse(p[3])};
                    if(!new[]{"Player","Enemy","Ally","Neutral"}.Contains(s.Name)||!names.Add(s.Name)||s.Spent==null||s.Platforms==null||s.Stores==null)return null;
                    r.Sides.Add(s);
                }
                return r;
            }
            catch(FormatException){return null;}
        }
    }

    internal sealed class CombatHistoryStore
    {
        const string Header="SEST-COMBAT-HISTORY-1";
        readonly string path;
        readonly Dictionary<string,CombatGameRecord> records=new Dictionary<string,CombatGameRecord>(StringComparer.Ordinal);
        internal bool ReadOnly;
        internal CombatHistoryStore(string file)
        {
            path=file;if(!File.Exists(path))return;
            try
            {
                if(new FileInfo(path).Length>64000000)throw new InvalidDataException("history too large");
                var lines=File.ReadAllLines(path,Encoding.UTF8);
                if(lines.Length==0||lines[0]!=Header)throw new InvalidDataException("unknown history format");
                foreach(string line in lines.Skip(1))
                {
                    var r=CombatGameRecord.Decode(line);
                    if(r==null||records.ContainsKey(r.Id))throw new InvalidDataException("invalid or duplicate history entry");
                    records.Add(r.Id,r);
                }
            }
            catch(Exception e){ReadOnly=true;Api.LogFailure("combat history is read-only; existing file preserved",e);}
        }
        internal List<CombatGameRecord> Games
        { get { return records.Values.OrderByDescending(r=>r.EndedUtc).ThenBy(r=>r.Id,StringComparer.Ordinal).ToList(); } }
        internal void Put(CombatGameRecord record)
        {
            if(ReadOnly||record==null)return;
            // The same mission save/session id is replaced on continuation,
            // not charged as a second game after loading a mid-mission save.
            var copy=CombatGameRecord.Decode(record.Encode());
            if(copy==null)throw new InvalidDataException("invalid combat history record");
            records[record.Id]=copy;
            var directory=Path.GetDirectoryName(path);if(!String.IsNullOrEmpty(directory))Directory.CreateDirectory(directory);
            string temporary=path+"."+Guid.NewGuid().ToString("N")+".tmp";
            try
            {
                File.WriteAllLines(temporary,new[]{Header}.Concat(Games.Select(r=>r.Encode())),new UTF8Encoding(false));
                if(File.Exists(path))File.Replace(temporary,path,null);else File.Move(temporary,path);
            }
            finally{if(File.Exists(temporary))File.Delete(temporary);}
        }
    }

    internal static class CombatHistory
    {
        internal const string SessionKey="SestCombatSessionV1";
        static CombatHistoryStore store;
        static object mission;
        static CombatGameRecord pending;
        sealed class SavedId { internal string Value; }
        static ConditionalWeakTable<object,SavedId> restored=new ConditionalWeakTable<object,SavedId>();
        static object context;
        internal static string CurrentId { get { return pending==null?null:pending.Id; } }
        internal static void Open(string path)
        { store=new CombatHistoryStore(path);mission=null;context=null;pending=null;restored=new ConditionalWeakTable<object,SavedId>(); }
        internal static void RestoreSession(string id,object taskforce)
        {
            if(taskforce==null||String.IsNullOrEmpty(id)||!Regex.IsMatch(id,"\\A[0-9a-f]{32}\\z"))return;
            restored.Remove(taskforce);restored.Add(taskforce,new SavedId{Value=id});
        }
        internal static void Observe(object current,CombatGameRecord capture)
        {
            if(store==null)return;
            if(!Object.ReferenceEquals(current,mission)||(capture!=null&&!Object.ReferenceEquals(capture.Context,context)))
            {
                Finish();mission=current;pending=null;
                context=capture==null?null:capture.Context;
            }
            if(current==null||capture==null)return;
            SavedId saved=null;bool loaded=capture.Context!=null&&restored.TryGetValue(capture.Context,out saved);
            string restoredId=loaded?saved.Value:null;
            if(loaded)restored.Remove(capture.Context);
            if(pending==null)
            {
                capture.Id=restoredId ?? Guid.NewGuid().ToString("N");
            }
            else if(restoredId!=null&&restoredId!=pending.Id){Finish();capture.Id=restoredId;}
            else
            {
                capture.Id=pending.Id;capture.Source=pending.Source;capture.MissionIndex=pending.MissionIndex;
                capture.Status=pending.Status;capture.EndedUtc=pending.EndedUtc;
            }
            pending=capture;
        }
        internal static void Finish()
        {
            if(store==null||pending==null)return;
            if(pending.EndedUtc==0)pending.EndedUtc=DateTime.UtcNow.Ticks;
            try{store.Put(pending);}catch(Exception e){Api.LogFailure("combat game history could not be saved; native saves retained",e);}
        }
        internal static void CompleteCampaign(string source,int index,bool replay,CombatGameRecord capture)
        {
            if(pending==null)return;
            Refresh(capture);
            pending.Source=source;pending.MissionIndex=index;pending.Status=replay?"Replay":"Completed";
            pending.EndedUtc=DateTime.UtcNow.Ticks;Finish();
        }
        internal static void Refresh(CombatGameRecord capture)
        {
            if(pending==null||capture==null||capture.Context==null||!Object.ReferenceEquals(capture.Context,pending.Context))return;
            // Teardown can clear/reassign native task-force registers before
            // GameMain's final callback. Never replace the good last snapshot
            // with another mission or counters that have already been reset.
            foreach(var old in pending.Sides)
            {
                var next=capture.Sides.FirstOrDefault(s=>s.Name==old.Name);
                if(next==null||Shrank(old.Spent,next.Spent)||Shrank(old.Platforms,next.Platforms)||Shrank(old.Stores,next.Stores))return;
            }
            capture.Id=pending.Id;capture.Name=pending.Name;capture.Source=pending.Source;capture.MissionIndex=pending.MissionIndex;
            capture.Status=pending.Status;capture.EndedUtc=pending.EndedUtc;pending=capture;
        }
        static bool Shrank(InventoryLedger old,InventoryLedger next)
        {return old.Ammo.Any(p=>InventoryLedger.Get(next.Ammo,p.Key)<p.Value);}
        internal static List<CombatGameRecord> Games
        { get { return store==null?new List<CombatGameRecord>():store.Games; } }
        internal static bool ReadOnly { get { return store!=null&&store.ReadOnly; } }
    }
}
