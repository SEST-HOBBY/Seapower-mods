using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;

namespace Sest.RuntimeFixes
{
    // A post-mission roster intentionally excludes sunken hulls. Section 3
    // nevertheless needs their loss rows. Reconstruct only missing hull rows
    // from this mission's exact launch snapshot + explicit IsDestroyed state.
    // Nothing is written to the save, roster, campaign points or kill totals.
    internal static class TaskForceDebrief
    {
        static MethodInfo readSnapshot, launchSection, launchPrefix, sectionExists, readDestroyed, sort;
        static ConstructorInfo rowConstructor;
        static FieldInfo missionIndex;
        static PropertyInfo snapshotItems, unitRows;
        static bool active;

        internal static MethodInfo Bind(Assembly game)
        {
            Type model = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel");
            Type save = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceSaveManager");
            Type snapshot = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceSnapshot");
            Type mission = Api.Type(game, "SeaPower.LinearCampaignMission"), ini = Api.Type(game, "SeaPower.IniHandler");
            Type row = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefUnitRow");
            Type roster = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceBuilderRosterItem");
            Type crew = roster.GetProperty("CrewSkill", Api.All).PropertyType;
            readSnapshot = Api.Method(save, "ReadSnapshot", snapshot, ini, typeof(string), typeof(string));
            launchSection = Api.Method(save, "MissionLaunchSection", typeof(string), typeof(int));
            launchPrefix = Api.Method(save, "MissionLaunchUnitPrefix", typeof(string), typeof(int));
            sectionExists = Api.Method(ini, "doesSectionExist", typeof(bool), typeof(string));
            readDestroyed = Api.Method(ini, "readValue", typeof(bool), typeof(string), typeof(string), typeof(bool), typeof(bool));
            snapshotItems = snapshot.GetProperty("Items", Api.All);
            unitRows = model.GetProperty("UnitRows", Api.All);
            missionIndex = mission.GetField("_index", Api.All);
            if (snapshotItems == null || unitRows == null || missionIndex == null || missionIndex.FieldType != typeof(int))
                throw new MissingMemberException("debrief snapshot/row/index API");
            rowConstructor = row.GetConstructor(new[] { typeof(string), typeof(string), typeof(string), typeof(string),
                typeof(string), typeof(string), typeof(bool), typeof(bool), crew, typeof(int) });
            if (rowConstructor == null) throw new MissingMethodException(row.FullName, ".ctor");
            sort = Api.Method(model, "SortDebriefUnitRows", typeof(IEnumerable<>).MakeGenericType(row),
                typeof(IEnumerable<>).MakeGenericType(row));
            active = true;
            return Api.Method(model, "ReadUnitRows", typeof(void), ini, mission);
        }

        internal static void Install(Assembly game)
        {
            MethodInfo target = Bind(game);
            Api.Postfix(target, typeof(TaskForceDebrief), "Postfix", "io.github.sest-hobby.taskforce-debrief");
            Api.Log("task-force debrief correction installed: append explicitly destroyed launch-snapshot hulls missing from section 3");
        }

        static object Value(object obj, string name) { return obj.GetType().GetProperty(name, Api.All).GetValue(obj, null); }
        static string Text(object obj, string name) { return Value(obj, name) as string ?? ""; }

        internal static void Postfix(object __instance, object __0, object __1)
        {
            if (!active || __instance == null || __0 == null || __1 == null) return;
            try
            {
                int index = (int)missionIndex.GetValue(__1);
                if (index < 1) return;
                string section = (string)launchSection.Invoke(null, new object[] { index });
                // No nearest-mission or current-roster fallback: proof must be
                // from the mission being displayed, including older debriefs.
                if (!(bool)sectionExists.Invoke(__0, new object[] { section }))
                {
                    Api.Log("debrief mission " + index + ": exact launch snapshot absent; native rows retained");
                    return;
                }
                object snapshot = readSnapshot.Invoke(null, new object[] { __0, section,
                    (string)launchPrefix.Invoke(null, new object[] { index }) });
                IList rows = unitRows.GetValue(__instance, null) as IList;
                if (rows == null || snapshot == null) return;
                var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                foreach (object row in rows) seen.Add(Text(row, "InstanceId"));
                var additions = new List<object>();
                foreach (object item in (IEnumerable)snapshotItems.GetValue(snapshot, null))
                {
                    if (item == null || !String.Equals(Text(item, "UnitFolder"), "vessels", StringComparison.OrdinalIgnoreCase)) continue;
                    string id = Text(item, "InstanceId");
                    if (String.IsNullOrWhiteSpace(id) || seen.Contains(id) || String.IsNullOrWhiteSpace(Text(item, "UnitType"))) continue;
                    string state = "Mission_" + index + "_" + id;
                    if (!(bool)sectionExists.Invoke(__0, new object[] { state }) ||
                        !(bool)readDestroyed.Invoke(__0, new object[] { state, "IsDestroyed", false, false })) continue;
                    additions.Add(rowConstructor.Invoke(new object[] { id, Text(item, "UnitType"), Text(item, "UnitFolder"),
                        Text(item, "Category"), Text(item, "VariantReference"), "Lost", true, false, Value(item, "CrewSkill"), 1 }));
                    seen.Add(id);
                }
                if (additions.Count == 0) return;
                // Build the replacement sequence before changing the bound collection.
                IList merged = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(rowConstructor.DeclaringType));
                foreach (object row in rows) merged.Add(row);
                foreach (object row in additions) merged.Add(row);
                var ordered = new List<object>();
                foreach (object row in (IEnumerable)sort.Invoke(null, new object[] { merged })) ordered.Add(row);
                rows.Clear();
                foreach (object row in ordered) rows.Add(row);
                Api.Log("debrief mission " + index + ": restored " + additions.Count + " missing lost-hull row(s) for display only");
            }
            catch (Exception e)
            {
                active = false;
                Api.LogFailure("debrief correction disabled for this session", e);
            }
        }
    }
}
