using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;

namespace Sest.RuntimeFixes
{
    // Cumulative campaign combat costs, phase 1 of
    // docs/combat-costs/campaign-costs-design.md. When the task-force debrief
    // opens, every completed mission's own saved [Mission_<i>_TaskForceDebrief]
    // record (weapon reports, kill and loss rows) is priced with the Combat
    // Cost Tracker's price lists under CombatCosts 0.7.1's rules, read from its
    // IL (CostPolicy; integration/common/costs.py mirrors the same rules), and
    // rows are appended to the Mission Summary. The tracker is never called or
    // patched. Nothing is written to the save or the state INI, and on any
    // failure the native rows are left as they are.
    internal static class CampaignCosts
    {
        // CombatCosts.dll 0.7.1.0, data/combat-cost-capture.json: noted in the log, not gated.
        const string Tracker071 = "74afa9028fc0c52b93f415263504f51ecf8d056a624feaebcc8053ba5a1c0ac3";
        static MethodInfo openState, hasSnapshot, sectionName, parseRows, readReports, buildTotals, getData,
            readString, keyExists, openVirtual, openIni;
        static PropertyInfo summaryRows, ammoRef, ammoType, launched, fired;
        static FieldInfo missionIndex, rowRef, rowFolder, rowType, rowCount, rowDestroyed;
        static ConstructorInfo summaryRow;
        static bool active;
        static readonly HashSet<string> noted = new HashSet<string>(StringComparer.Ordinal);
        static readonly HashSet<string> named = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        internal static MethodInfo Bind(Assembly game)
        {
            Type model = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel");
            Type rules = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules");
            Type row = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefSummaryRow");
            Type snapshot = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefRegisterSnapshotRow");
            Type mission = Api.Type(game, "SeaPower.LinearCampaignMission"), ini = Api.Type(game, "SeaPower.IniHandler");
            Type report = Api.Type(game, "SeaPower.TaskforceWeaponReport"), ammo = Api.Type(game, "SeaPower.WeaponReportAmmoData");
            Type utils = Api.Type(game, "SeaPower.Utils"), kinds = Api.Type(game, "SeaPower.Ammunition+Type");
            Type objects = Api.Type(game, "SeaPower.ObjectBase+ObjectType");
            foreach (string name in CostPolicy.CountedTypes)
                if (!kinds.IsEnum || !Enum.IsDefined(kinds, name)) throw new MissingMemberException(kinds.FullName, name);
            foreach (string name in CostPolicy.PricedObjects)
                if (!objects.IsEnum || !Enum.IsDefined(objects, name)) throw new MissingMemberException(objects.FullName, name);
            Type data = typeof(Dictionary<string, Dictionary<string, string>>);
            openState = Api.Method(rules, "OpenCampaignStateIni", ini);
            hasSnapshot = Api.Method(model, "HasDebriefSnapshot", typeof(bool), ini, typeof(int));
            sectionName = Api.Method(model, "GetDebriefSectionName", typeof(string), typeof(int));
            parseRows = Api.Method(model, "TryParseRegisterRows", typeof(bool), typeof(string),
                typeof(List<>).MakeGenericType(snapshot).MakeByRefType());
            readReports = Api.Method(model, "TryReadWeaponReports", typeof(bool), ini, typeof(int),
                report.MakeByRefType(), report.MakeByRefType(), report.MakeByRefType());
            buildTotals = Api.Method(report, "BuildTaskforceTotals", typeof(Dictionary<,>).MakeGenericType(typeof(string), ammo));
            getData = Api.Method(ini, "get_Data", data);
            readString = Api.Method(ini, "readValue", typeof(string), typeof(string), typeof(string), typeof(string), typeof(bool));
            keyExists = Api.Method(ini, "doesKeyExist", typeof(bool), typeof(string), typeof(string));
            openVirtual = Api.Method(utils, "openVirtualIniFile", ini, typeof(string), typeof(string), typeof(string), typeof(bool));
            openIni = Api.Method(utils, "openIniFile", ini, typeof(string), typeof(string), typeof(bool), typeof(bool));
            summaryRows = model.GetProperty("SummaryRows", Api.All);
            if (summaryRows == null || !typeof(IList).IsAssignableFrom(summaryRows.PropertyType) ||
                !summaryRows.PropertyType.IsGenericType || summaryRows.PropertyType.GetGenericArguments()[0] != row)
                throw new MissingMemberException(model.FullName, "SummaryRows");
            ammoRef = Property(ammo, "AmmoRef", typeof(string));
            ammoType = Property(ammo, "AmmoType", kinds);
            launched = Property(ammo, "Launched", typeof(int));
            fired = Property(ammo, "ProjectileFired", typeof(int));
            missionIndex = Field(mission, "_index", typeof(int));
            rowRef = Field(snapshot, "IniRef", typeof(string));
            rowFolder = Field(snapshot, "Folder", typeof(string));
            rowType = Field(snapshot, "ObjectType", typeof(string));
            rowCount = Field(snapshot, "Count", typeof(int));
            rowDestroyed = Field(snapshot, "IsDestroyed", typeof(bool));
            summaryRow = row.GetConstructor(new[] { typeof(string), typeof(string), typeof(bool), typeof(bool) });
            if (summaryRow == null) throw new MissingMethodException(row.FullName, ".ctor");
            active = true;
            return Api.Method(model, "Load", typeof(void), mission);
        }

        static PropertyInfo Property(Type type, string name, Type expected)
        {
            PropertyInfo result = type.GetProperty(name, Api.All);
            if (result == null || result.PropertyType != expected || result.GetGetMethod(true) == null)
                throw new MissingMemberException(type.FullName, name);
            return result;
        }

        static FieldInfo Field(Type type, string name, Type expected)
        {
            FieldInfo result = type.GetField(name, Api.All);
            if (result == null || result.IsStatic || result.FieldType != expected) throw new MissingMemberException(type.FullName, name);
            return result;
        }

        internal static void Install(Assembly game)
        {
            MethodInfo target = Bind(game);
            Api.Postfix(target, typeof(CampaignCosts), "Postfix", "io.github.sest-hobby.campaign-combat-costs");
            Api.Log("campaign combat costs installed: debrief rows priced from the Combat Cost Tracker's price lists; nothing written to the save");
        }

        static void Note(string key, string message) { if (noted.Add(key)) Api.Log(message); }

        static string Describe(Exception error)
        {
            while (error is TargetInvocationException && error.InnerException != null) error = error.InnerException;
            return error.GetType().Name + ": " + error.Message;
        }

        internal static void Postfix(object __instance, object __0)
        {
            if (!active || __instance == null || __0 == null) return;
            try
            {
                int index = (int)missionIndex.GetValue(__0);
                if (index < 1) return;
                object state = openState.Invoke(null, new object[0]);
                if (state == null)
                {
                    Note("state", "combat costs: no campaign state INI; rows not shown");
                    return;
                }
                if (!(bool)hasSnapshot.Invoke(null, new object[] { state, index }))
                {
                    Note("snapshot", "combat costs mission " + index + ": no debrief snapshot; rows not shown");
                    return;
                }
                IList rows = summaryRows.GetValue(__instance, null) as IList;
                if (rows == null) throw new InvalidOperationException("SummaryRows is null");
                CostPricer pricer = Catalogs();
                if (pricer == null)
                {
                    Note("catalogs", "combat costs: Combat Cost Tracker price lists not found (is the tracker enabled?); rows not shown");
                    return;
                }
                Note("tracker", "combat costs: tracker price lists found; " + Tracker() +
                    " (rules mirrored from 0.7.1 " + Tracker071.Substring(0, 8) + "...)");
                MissionCost shown = null, campaign = new MissionCost();
                foreach (int i in Missions(state, index))
                {
                    MissionCost cost = Price(state, i, pricer);
                    campaign.Add(cost);
                    if (i == index) shown = cost;
                }
                // Build every row before touching the bound collection.
                var additions = new List<object>();
                foreach (string[] text in CostPolicy.Rows(shown, campaign, pricer.Basis))
                    additions.Add(summaryRow.Invoke(new object[] { text[0], text[1], false, false }));
                foreach (object row in additions) rows.Add(row);
                Api.Log(CostPolicy.LogLine(index, pricer.Basis, shown, campaign));
                foreach (string failure in pricer.Failures)
                    Note("read " + failure, "combat costs: could not read " + failure + "; counted as unpriced");
                var fresh = new List<string>();
                foreach (string name in pricer.Unpriced) if (named.Add(name)) fresh.Add(name);
                if (fresh.Count > 0)
                    Api.Log("combat costs: no " + pricer.Basis + " price for " + CostPolicy.Names(fresh, 20));
            }
            catch (Exception e)
            {
                active = false;
                Api.LogFailure("campaign combat costs disabled for this session", e);
            }
        }

        static Dictionary<string, Dictionary<string, string>> Data(object ini)
        {
            return ini == null ? null : (Dictionary<string, Dictionary<string, string>>)getData.Invoke(ini, null);
        }

        // Opened exactly as the tracker opens them, with every enabled mod's #!extend applied.
        static Dictionary<string, Dictionary<string, string>> Virtual(string folder, string name)
        {
            return Data(openVirtual.Invoke(null, new object[] { folder, name, name, false }));
        }

        static CostPricer Catalogs()
        {
            var weapons = Virtual("systems", "weaponcosts");
            var vessels = Virtual("systems", "vesselcosts");
            var aircraft = Virtual("systems", "aircraftcosts");
            // SEST's extend files carry no [Costs]: without the tracker's own lists there is nothing to price with.
            if (!CostPolicy.HasCosts(weapons) || !CostPolicy.HasCosts(vessels) || !CostPolicy.HasCosts(aircraft)) return null;
            return new CostPricer(weapons, vessels, aircraft, Virtual("systems/combatcosts", "config"),
                (root, reference) => Data(openIni.Invoke(null, new object[] { root, "/" + reference + ".ini", false, true })));
        }

        static string Tracker()
        {
            foreach (Assembly assembly in AppDomain.CurrentDomain.GetAssemblies())
            {
                string name;
                try { name = assembly.GetName().Name; }
                catch (Exception) { continue; }
                if (!String.Equals(name, "CombatCosts", StringComparison.OrdinalIgnoreCase)) continue;
                try
                {
                    string digest;
                    using (var stream = File.OpenRead(assembly.Location))
                    using (var sha = SHA256.Create())
                        digest = BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
                    return "CombatCosts.dll " + digest.Substring(0, 12) + (digest == Tracker071 ? "" : ", not the reviewed 0.7.1 build");
                }
                catch (Exception e) { return "CombatCosts.dll unreadable (" + Describe(e) + ")"; }
            }
            return "CombatCosts.dll not loaded";
        }

        // Each completed mission once: the sections the game itself names, plus the one shown.
        static List<int> Missions(object state, int index)
        {
            var found = new List<int> { index };
            var data = Data(state);
            if (data == null) return found;
            foreach (string key in new List<string>(data.Keys))
            {
                int i;
                if (key == null || key.Length <= 25 || !key.StartsWith("Mission_", StringComparison.Ordinal) ||
                    !key.EndsWith("_TaskForceDebrief", StringComparison.Ordinal) ||
                    !Int32.TryParse(key.Substring(8, key.Length - 25), NumberStyles.None, CultureInfo.InvariantCulture, out i) ||
                    i < 1 || found.Contains(i)) continue;
                if (String.Equals((string)sectionName.Invoke(null, new object[] { i }), key, StringComparison.Ordinal) &&
                    (bool)hasSnapshot.Invoke(null, new object[] { state, i })) found.Add(i);
            }
            found.Sort();
            return found;
        }

        static MissionCost Price(object state, int index, CostPricer pricer)
        {
            var cost = new MissionCost();
            string section = (string)sectionName.Invoke(null, new object[] { index });
            object[] reports = { state, index, null, null, null };
            readReports.Invoke(null, reports);
            Weapons(state, index, section, "PlayerWeaponReport", reports[2], cost.Player, cost, pricer);
            Weapons(state, index, section, "EnemyWeaponReport", reports[3], cost.Enemy, cost, pricer);
            Losses(state, section, "KillRows", cost.Enemy, cost, pricer);
            Losses(state, section, "LossRows", cost.Player, cost, pricer);
            return cost;
        }

        static void Weapons(object state, int index, string section, string key, object report, SideCost side,
            MissionCost cost, CostPricer pricer)
        {
            // The game writes a blank value for a side that fired nothing (WriteWeaponReport).
            if (!(bool)keyExists.Invoke(state, new object[] { section, key })) { side.WeaponsMissing = true; return; }
            if (String.IsNullOrWhiteSpace((string)readString.Invoke(state, new object[] { section, key, "", false }))) return;
            if (report == null) { side.WeaponsMissing = true; return; }  // unreadable; the game logs why
            IDictionary totals;
            try { totals = (IDictionary)buildTotals.Invoke(report, null); }
            catch (TargetInvocationException e)
            {
                Note("totals " + index + key, "combat costs mission " + index + ": " + key + " not totalled (" + Describe(e) +
                    "); shown as not recorded");
                side.WeaponsMissing = true;
                return;
            }
            if (totals == null) { side.WeaponsMissing = true; return; }
            foreach (object ammo in totals.Values)
            {
                if (ammo == null) continue;
                // The tracker's _number: CIWS bursts are already inside ProjectileFired.
                long count = (long)(int)launched.GetValue(ammo, null) + (int)fired.GetValue(ammo, null);
                if (count <= 0) continue;
                decimal? price;
                if (!pricer.Weapon(ammoRef.GetValue(ammo, null) as string, ammoType.GetValue(ammo, null).ToString(), out price))
                {
                    cost.Ignored += count;
                    continue;
                }
                if (price.HasValue) side.Weapons += price.Value * count;
                else side.Rounds += count;
            }
        }

        static void Losses(object state, string section, string key, SideCost side, MissionCost cost, CostPricer pricer)
        {
            object[] parsed = { (string)readString.Invoke(state, new object[] { section, key, "", false }), null };
            parseRows.Invoke(null, parsed);
            var rows = parsed[1] as IEnumerable;
            if (rows == null) return;
            foreach (object row in rows)
            {
                int count = (int)rowCount.GetValue(row);
                if (!(bool)rowDestroyed.GetValue(row) || count <= 0) continue;  // kill rows include damaged units
                string type = rowType.GetValue(row) as string, reference = rowRef.GetValue(row) as string;
                if (CostPolicy.IsShip(type))
                {
                    decimal? price = pricer.Vessel(reference, rowFolder.GetValue(row) as string);
                    if (price.HasValue) side.Losses += price.Value * count; else side.Ships += count;
                }
                else if (CostPolicy.IsAircraft(type))
                {
                    decimal? price = pricer.Aircraft(reference);
                    if (price.HasValue) side.Losses += price.Value * count; else side.Aircraft += count;
                }
                else cost.Unpriceable += count;
            }
        }
    }

    internal sealed class SideCost
    {
        internal decimal Weapons, Losses;
        internal long Rounds, Ships, Aircraft;  // counted, price unknown
        internal bool WeaponsMissing;           // this mission's report is absent or unreadable
        internal int MissingReports;            // summed: missions whose report is missing
        internal decimal Total { get { return Weapons + Losses; } }
        internal bool WeaponsIncomplete { get { return WeaponsMissing || MissingReports > 0 || Rounds > 0; } }
        internal bool LossesIncomplete { get { return Ships > 0 || Aircraft > 0; } }
        internal bool Incomplete { get { return WeaponsIncomplete || LossesIncomplete; } }

        internal void Add(SideCost other)
        {
            Weapons += other.Weapons; Losses += other.Losses;
            Rounds += other.Rounds; Ships += other.Ships; Aircraft += other.Aircraft;
            MissingReports += other.MissingReports + (other.WeaponsMissing ? 1 : 0);
        }
    }

    internal sealed class MissionCost
    {
        internal readonly SideCost Player = new SideCost(), Enemy = new SideCost();
        internal long Unpriceable, Ignored;     // destroyed land and other units; rounds the tracker ignores
        internal int Missions, MissingReports;  // campaign: missions added, and those with a side's report missing
        internal bool WeaponsMissing { get { return Player.WeaponsMissing || Enemy.WeaponsMissing; } }
        internal bool Incomplete { get { return Player.Incomplete || Enemy.Incomplete; } }

        internal void Add(MissionCost mission)
        {
            Player.Add(mission.Player); Enemy.Add(mission.Enemy);
            Unpriceable += mission.Unpriceable; Ignored += mission.Ignored;
            Missions++;
            if (mission.WeaponsMissing) MissingReports++;
        }
    }

    internal delegate Dictionary<string, Dictionary<string, string>> UnitIni(string root, string reference);

    // One debrief's prices, cached within the call (the tracker's Overlay.GetPrice,
    // GetVesselPrice and GetAircraftPrice, without its log lines).
    internal sealed class CostPricer
    {
        struct Price { internal bool Ignored; internal decimal? Amount; }
        readonly Dictionary<string, Dictionary<string, string>> weapons, vessels, aircraft;
        readonly UnitIni unitIni;
        readonly Dictionary<string, Price> cache = new Dictionary<string, Price>(StringComparer.OrdinalIgnoreCase);
        internal readonly bool Current;
        internal readonly string Basis;
        internal readonly List<string> Unpriced = new List<string>(), Failures = new List<string>();

        internal CostPricer(Dictionary<string, Dictionary<string, string>> weaponCatalog,
            Dictionary<string, Dictionary<string, string>> vesselCatalog, Dictionary<string, Dictionary<string, string>> aircraftCatalog,
            Dictionary<string, Dictionary<string, string>> settings, UnitIni unitIni)
        {
            // Overlay.LoadConfig: config = SharedSettings.Apply(weapon catalog, config.ini, false); its
            // [Costs] decides the cost mode for all three kinds.
            weapons = CostPolicy.Apply(weaponCatalog, settings);
            vessels = vesselCatalog;
            aircraft = aircraftCatalog;
            this.unitIni = unitIni;
            Current = CostPolicy.UseCurrentYear(weapons);
            Basis = CostPolicy.Basis(weapons);
        }

        // False: the tracker leaves this round at its default category, Ignore, and counts nothing.
        internal bool Weapon(string reference, string type, out decimal? price)
        {
            Price result = Resolve("weapon", reference, type ?? "", "/ammunition", weapons, Current ? "CurrentYearCost" : "WeaponCosts");
            price = result.Amount;
            return !result.Ignored;
        }

        internal decimal? Vessel(string reference, string folder)
        {
            string root = "/" + (String.IsNullOrEmpty(folder) ? "vessels" : folder.Trim('/', '\\'));
            return Resolve("vessel", reference, null, root, vessels, Current ? "CurrentYearCost" : "VesselCosts").Amount;
        }

        // Aircraft and helicopters alike: the tracker opens both from /aircraft.
        internal decimal? Aircraft(string reference)
        {
            return Resolve("aircraft", reference, null, "/aircraft", aircraft, Current ? "CurrentYearCost" : "AircraftCosts").Amount;
        }

        Price Resolve(string kind, string reference, string type, string root,
            Dictionary<string, Dictionary<string, string>> catalog, string field)
        {
            string key = kind + "|" + type + "|" + root + "|" + reference;
            Price result;
            if (cache.TryGetValue(key, out result)) return result;
            Dictionary<string, Dictionary<string, string>> unit = null;
            bool failed = false;
            if (!String.IsNullOrWhiteSpace(reference))
            {
                try { unit = unitIni(root, reference); }
                catch (Exception e)
                {
                    while (e is TargetInvocationException && e.InnerException != null) e = e.InnerException;
                    Failures.Add(kind + " " + reference + " (" + e.GetType().Name + ": " + e.Message + ")");
                    failed = true;
                }
            }
            if (!failed)
            {
                result.Ignored = type != null && CostPolicy.WeaponExcluded(
                    CostPolicy.ResolveField(unit, catalog, reference, "Category", "WeaponCostCategory"), type);
                if (!result.Ignored) result.Amount = CostPolicy.ParsePrice(CostPolicy.ResolveField(unit, catalog, reference, field, field));
            }
            if (!result.Ignored && !result.Amount.HasValue)
                Unpriced.Add(kind + " " + (String.IsNullOrWhiteSpace(reference) ? "(blank)" : reference));
            cache[key] = result;
            return result;
        }
    }

    // CombatCosts 0.7.1's price rules (WeaponCostsMod.CostRules, SharedSettings,
    // VesselRules and AircraftRules, read from the IL of 74afa902...) over plain
    // dictionaries, and the row text. tests/cost_precedence.tsv and
    // tests/cost_exclusion.tsv hold the cases costs.py is checked against too.
    internal static class CostPolicy
    {
        internal const string Ignore = "Ignore";
        internal static readonly decimal MaxPrice = 1000000000000000m;
        // CostRules.Resolve's fallback table: the only types given a category without one of their own.
        static readonly string[] Fallback = { "asroc", "rbu", "airdepthcharge", "torpedo", "bomb", "projectile", "aerialrocket", "mlrs" };
        internal static readonly string[] CountedTypes = { "Missile", "ASROC", "RBU", "AirDepthCharge", "Torpedo", "Bomb",
            "Projectile", "AerialRocket", "MLRS" };
        internal static readonly string[] PricedObjects = { "Vessel", "Submarine", "Aircraft", "Helicopter" };
        static readonly string[] Units = { "K", "M", "B", "T" };

        // CostRules.Value: the first section and key equal ignoring case; the value trimmed.
        internal static string Value(Dictionary<string, Dictionary<string, string>> ini, string section, string key)
        {
            if (ini == null) return null;
            foreach (KeyValuePair<string, Dictionary<string, string>> s in ini)
            {
                if (s.Value == null || !String.Equals(s.Key, section, StringComparison.OrdinalIgnoreCase)) continue;
                foreach (KeyValuePair<string, string> pair in s.Value)
                    if (String.Equals(pair.Key, key, StringComparison.OrdinalIgnoreCase)) return (pair.Value ?? "").Trim();
            }
            return null;
        }

        // CostRules.Preference: an invalid or missing value keeps the broader setting.
        internal static bool Preference(Dictionary<string, Dictionary<string, string>> ini, string section, string key, bool fallback)
        {
            string value = Value(ini, section, key);
            bool parsed;
            return value != null && Boolean.TryParse(value, out parsed) ? parsed : fallback;
        }

        // CostRules.ResolveField. A missing key falls back to the other side; a blank one wins.
        internal static string ResolveField(Dictionary<string, Dictionary<string, string>> unit,
            Dictionary<string, Dictionary<string, string>> catalog, string reference, string field, string inlineField)
        {
            bool preferList = Preference(catalog, "Costs", "OverrideInline", false);
            preferList = Preference(catalog, reference, "OverrideInline", preferList);
            preferList = Preference(catalog, reference, "Override" + field, preferList);
            string own = Value(unit, "General", inlineField), listed = Value(catalog, reference, field);
            return preferList ? listed ?? own : own ?? listed;
        }

        // CostRules.ParsePrice: 0 (free) to 1e15, digits and one decimal point only.
        internal static decimal? ParsePrice(string value)
        {
            decimal amount;
            if (String.IsNullOrWhiteSpace(value) ||
                !Decimal.TryParse(value, NumberStyles.AllowDecimalPoint, CultureInfo.InvariantCulture, out amount)) return null;
            return amount >= 0 && amount <= MaxPrice ? amount : (decimal?)null;
        }

        internal static bool ValidCategory(string category)
        {
            if (String.IsNullOrWhiteSpace(category) || category.Length > 20) return false;
            foreach (char c in category)
                if (!(c >= 'A' && c <= 'Z' || c >= 'a' && c <= 'z' || Char.IsDigit(c) || c == ' ' || c == '-' || c == '_')) return false;
            return true;
        }

        // CostRules.Resolve: Price starts as "Ignore" and keeps it for an invalid or
        // Ignore category, or, with none, for a type outside Missile and the fallback table.
        internal static bool WeaponExcluded(string category, string ammoType)
        {
            if (!String.IsNullOrEmpty(category))
                return !ValidCategory(category) || String.Equals(category, Ignore, StringComparison.OrdinalIgnoreCase);
            if (String.Equals(ammoType, "Missile", StringComparison.OrdinalIgnoreCase)) return false;
            return ammoType == null || Array.IndexOf(Fallback, ammoType.ToLowerInvariant()) < 0;
        }

        // SharedSettings.Apply(catalog, settings, false): a case-insensitive copy whose
        // [Costs] takes config.ini's UseCurrentYearCosts and CurrentYear when present.
        internal static Dictionary<string, Dictionary<string, string>> Apply(Dictionary<string, Dictionary<string, string>> catalog,
            Dictionary<string, Dictionary<string, string>> settings)
        {
            var result = new Dictionary<string, Dictionary<string, string>>(StringComparer.OrdinalIgnoreCase);
            if (catalog != null)
                foreach (KeyValuePair<string, Dictionary<string, string>> section in catalog)
                {
                    var copy = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
                    if (section.Value != null) foreach (KeyValuePair<string, string> pair in section.Value) copy[pair.Key] = pair.Value;
                    result[section.Key] = copy;
                }
            if (!result.ContainsKey("Costs")) result.Add("Costs", new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase));
            foreach (string key in new[] { "UseCurrentYearCosts", "CurrentYear" })
            {
                string value = Value(settings, "Costs", key);
                if (value != null) result["Costs"][key] = value;
            }
            return result;
        }

        internal static bool UseCurrentYear(Dictionary<string, Dictionary<string, string>> config)
        {
            bool value;
            return Boolean.TryParse(Value(config, "Costs", "UseCurrentYearCosts"), out value) && value;
        }

        // CostRules.CostBasis, but "current" for a blank year as well as a missing one.
        internal static string Basis(Dictionary<string, Dictionary<string, string>> config)
        {
            if (!UseCurrentYear(config)) return "IOC";
            string year = Value(config, "Costs", "CurrentYear");
            return String.IsNullOrEmpty(year) ? "current" : year;
        }

        internal static bool HasCosts(Dictionary<string, Dictionary<string, string>> catalog)
        {
            if (catalog == null) return false;
            foreach (string section in catalog.Keys)
                if (String.Equals(section, "Costs", StringComparison.OrdinalIgnoreCase)) return true;
            return false;
        }

        internal static bool IsShip(string type)
        {
            return String.Equals(type, "Vessel", StringComparison.OrdinalIgnoreCase) ||
                String.Equals(type, "Submarine", StringComparison.OrdinalIgnoreCase);
        }

        internal static bool IsAircraft(string type)
        {
            return String.Equals(type, "Aircraft", StringComparison.OrdinalIgnoreCase) ||
                String.Equals(type, "Helicopter", StringComparison.OrdinalIgnoreCase);
        }

        // Invariant, 3 significant digits, half away from zero; whole dollars below $1,000.
        internal static string Money(decimal amount)
        {
            if (amount < 0) amount = 0;
            decimal whole = Math.Round(amount, 0, MidpointRounding.AwayFromZero);
            if (whole < 1000) return "$" + whole.ToString("0", CultureInfo.InvariantCulture);
            int unit = 0;
            decimal scaled = amount / 1000;
            while (scaled >= 1000 && unit < Units.Length - 1) { scaled /= 1000; unit++; }
            decimal rounded = Math.Round(scaled, Digits(scaled), MidpointRounding.AwayFromZero);
            if (rounded >= 1000 && unit < Units.Length - 1)
            {
                unit++;
                rounded = Math.Round(scaled / 1000, 2, MidpointRounding.AwayFromZero);
            }
            return "$" + rounded.ToString("F" + Digits(rounded), CultureInfo.InvariantCulture) + Units[unit];
        }

        static int Digits(decimal value) { return value >= 100 ? 0 : value >= 10 ? 1 : 2; }

        static string Count(long n, string one, string many)
        {
            return n.ToString(CultureInfo.InvariantCulture) + " " + (n == 1 ? one : many);
        }

        static string Unknown(bool incomplete) { return incomplete ? " + ?" : ""; }

        static string Weapons(SideCost side)
        {
            return side.WeaponsMissing ? "not recorded" : Money(side.Weapons) + Unknown(side.Rounds > 0);
        }

        static string Gaps(MissionCost cost, bool campaign)
        {
            var parts = new List<string>();
            long rounds = cost.Player.Rounds + cost.Enemy.Rounds, ships = cost.Player.Ships + cost.Enemy.Ships;
            long aircraft = cost.Player.Aircraft + cost.Enemy.Aircraft;
            if (rounds > 0) parts.Add(Count(rounds, "round", "rounds"));
            if (ships > 0) parts.Add(Count(ships, "ship", "ships"));
            if (aircraft > 0) parts.Add(Count(aircraft, "aircraft", "aircraft"));
            if (campaign && cost.MissingReports > 0)
                parts.Add("weapons not recorded for " + Count(cost.MissingReports, "mission", "missions"));
            if (!campaign && cost.WeaponsMissing) parts.Add("weapons not recorded");
            return parts.Count == 0 ? "none" : String.Join(", ", parts.ToArray());
        }

        // The rows appended to the Mission Summary: label, value.
        internal static List<string[]> Rows(MissionCost mission, MissionCost campaign, string basis)
        {
            SideCost p = mission.Player, e = mission.Enemy;
            var rows = new List<string[]>
            {
                new[] { "Combat Cost: Weapons", "Player " + Weapons(p) + " | Enemy " + Weapons(e) },
                new[] { "Combat Cost: Losses", "Player " + Money(p.Losses) + Unknown(p.LossesIncomplete) +
                    " | Enemy " + Money(e.Losses) + Unknown(e.LossesIncomplete) },
                new[] { "Combat Cost: Mission", "Player " + Money(p.Total) + Unknown(p.Incomplete) +
                    " | Enemy " + Money(e.Total) + Unknown(e.Incomplete) },
                new[] { "Combat Cost: Campaign", "Player " + Money(campaign.Player.Total) + Unknown(campaign.Player.Incomplete) +
                    " | Enemy " + Money(campaign.Enemy.Total) + Unknown(campaign.Enemy.Incomplete) +
                    " (" + Count(campaign.Missions, "mission", "missions") + ")" },
                new[] { "Combat Cost: Basis", "USD, " + basis + " prices; stores aboard and land units excluded" },
            };
            if (mission.Incomplete || campaign.Incomplete)
                rows.Add(new[] { "Combat Cost: Unpriced", "Mission: " + Gaps(mission, false) + " | Campaign: " + Gaps(campaign, true) });
            return rows;
        }

        static string Raw(decimal value) { return value.ToString(CultureInfo.InvariantCulture); }

        static string LogSide(SideCost side)
        {
            return "weapons " + (side.WeaponsMissing ? "not recorded" : Raw(side.Weapons) + " +" + side.Rounds + "?") +
                ", losses " + Raw(side.Losses) + " +" + (side.Ships + side.Aircraft) + "?";
        }

        static string LogTotal(SideCost side)
        {
            return Raw(side.Total) + " +" + (side.Rounds + side.Ships + side.Aircraft) + "?" +
                (side.MissingReports > 0 ? " (weapons not recorded for " + Count(side.MissingReports, "mission", "missions") + ")" : "");
        }

        internal static string LogLine(int index, string basis, MissionCost mission, MissionCost campaign)
        {
            return "combat costs mission " + index + " (" + basis + "): player " + LogSide(mission.Player) +
                "; enemy " + LogSide(mission.Enemy) + "; campaign " + Count(campaign.Missions, "mission", "missions") +
                ": player " + LogTotal(campaign.Player) + ", enemy " + LogTotal(campaign.Enemy) +
                "; land and other units not priced: " + mission.Unpriceable + " (campaign " + campaign.Unpriceable + ")" +
                "; rounds the tracker ignores: " + mission.Ignored + " (campaign " + campaign.Ignored + ")";
        }

        internal static string Names(List<string> names, int limit)
        {
            var shown = names.Count > limit ? names.GetRange(0, limit) : names;
            string text = String.Join(", ", shown.ToArray());
            return names.Count > limit ? text + " and " + (names.Count - limit) + " more" : text;
        }
    }
}
