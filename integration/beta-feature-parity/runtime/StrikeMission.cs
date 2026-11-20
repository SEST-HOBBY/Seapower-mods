using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using AnchorChain;
using SeaPower;
using UnityEngine;

namespace Sest.RuntimeFixes;

// SEST fire missions for the Coordinated Strike Tool (Workshop 3806686336,
// exact image 093b8ad6, pinned by CoordinatedStrikeRefinements).
//
// 1. Target picker: the author's F8 "Select target track" list is drawn by
//    SEST in the Contacts window's terms - grouped by domain, with class and
//    identity from Contact Log (3819427362, a1b8b450) when it is loaded,
//    range and bearing from the selected unit, speed, course, altitude, a
//    search box and sorting. "+" adds a track as another target.
// 2. Multi-target fire missions: each target is one of the author's own
//    StrikePlan objects, so the author's range, simulation and timing maths
//    runs per target. The author's panel shows and edits the active one;
//    the FIRE MISSION section lists them all, switches between them and can
//    lock every target to one time on target.
// 3. Automated shoot: when armed, each locked leg is ordered with the game's
//    own engage order (ObjectBase.AddEngageTask(new EngageTask(...)), the
//    same order the player's attack click gives) at its launch time. The
//    author's launch detection then counts the shots as usual.
//
// Nothing is written to disk and nothing persists between missions. Auto-fire
// is off at every mission start and disarms itself on leaving the mission or
// changing task force. Any binding or drawing failure stops this feature and
// leaves the author's panel exactly as it was.
internal static class StrikeMission
{
	internal const string HarmonyId = "io.github.sest-hobby.strike-mission";

	private const string ContactLogHash = "a1b8b450df0933df61984651fe2b19138acd605aa4b526bbfc23565d8295015e";

	private const string SearchControl = "SEST_StrikeSearch";

	private const float KnotsPerUnity = 1f / 0.0076554087f;

	private sealed class Order
	{
		internal int Sent;
		internal float LastAt = float.NegativeInfinity;
		internal EngageTask Task;
		internal ObjectBase Shooter;
	}

	private sealed class Row
	{
		internal Vehicle Vehicle;
		internal string Label = "", Detail = "", Group = "";
		internal int Relation, Domain;
		internal double RangeNm = double.NaN, Bearing = double.NaN, SpeedKt = double.NaN, Course = double.NaN, AltFt = double.NaN;
		internal Color Colour;
	}

	// Bound author members.
	private static Type panelType, planType, legType, dataType, stylesType, listType, filterType, pickerType;
	private static FieldInfo planField, stylesField, filterField, hostileField, pickerListField, taskforceField, focusedField, prepLeadField;
	private static FieldInfo legsField, impactField, shooterField, ammoField, firedField, statusField, salvoField, launchedField, launchTimeField;
	private static PropertyInfo targetProperty, lockedProperty, armingProperty, previewProperty;
	private static MethodInfo planUpdate, planLock, planUnlock, planSimulate, timingMethod, openMethod, closeMethod, leftButton, resetAlerts, beginList, listRow, endList, savePrefs, px;
	private static FieldInfo timingLead, timingRequested;
	private static Func<List<Vehicle>> contacts;
	private static Func<Vehicle, string> contactLabel, contactDetail;
	private static Func<Vehicle, bool> vehicleAlive;
	private static Func<Vehicle, Color> relationColour;
	private static Func<ObjectBase> selectedUnit;
	private static Func<ObjectBase, string, int> ammoCount;
	private static Func<ObjectBase, string, Ammunition> getAmmo;
	private static Func<ObjectBase, string> unitLabel;
	private static Func<Ammunition, string> ammoLabel;
	private static Action<ObjectBase, string, Vehicle> prepareLaunchers;
	private static Func<float> gameNow;
	private static Func<bool> inMission;
	private static MethodInfo domainOf;

	// Contact Log, optional.
	private static Type contactLogType;
	private static FieldInfo storeField;
	private static PropertyInfo recordsProperty;
	private static FieldInfo recClass, recType, recUnitName, recSeen, recWeapon, recAlt, recHandle, recKey, recActive;
	private static bool contactLogTried;
	private static UnityEngine.Object contactLog;
	private static double contactLogNext;
	private static Dictionary<Vehicle, object> records = new Dictionary<Vehicle, object>();
	private static Dictionary<string, object> recordsByKey = new Dictionary<string, object>(StringComparer.Ordinal);

	// Mission state.
	private static readonly List<object> plans = new List<object>();
	private static readonly ConditionalWeakTable<object, Order> orders = new ConditionalWeakTable<object, Order>();
	private static readonly List<Order> issued = new List<Order>();
	private static readonly List<string> events = new List<string>();
	private static readonly HashSet<int> collapsed = new HashSet<int>();
	private static object panel;
	private static Taskforce taskforce;
	private static bool hooked, stopped, armed, sameTimeOnTarget = true, confirmArm;
	private static float confirmUntil, nextUpdate;
	private static string search = "";
	private static List<Row> pickerRows = new List<Row>();
	private static string rowsKey;
	private static float rowsNext;
	private static int rowsTotal;
	private static StrikeMissionPolicy.Sort sort;

	// The author's ContactFilter (All, Air, Surface, Sub, Land) as its
	// GameData.TargetDomain (Surface, Air, Subsurface, Land).
	private static readonly int[] FilterDomain = { -1, 1, 0, 2, 3 };

	// Picker groups in Contacts order, by TargetDomain value.
	private static readonly int[] GroupOrder = { 1, 0, 2, 3 };

	private static readonly string[] GroupNames = { "SURFACE", "AIR", "SUBSURFACE", "LAND" };

	private static double RealNow => (double)System.Diagnostics.Stopwatch.GetTimestamp() / System.Diagnostics.Stopwatch.Frequency;

	internal static bool Armed => armed;

	internal static void Poll(Type strikePanel)
	{
		if (hooked || stopped)
		{
			return;
		}
		try
		{
			Bind(strikePanel.Assembly);
			Api.Postfix(Api.Method(panelType, "Update", typeof(void)), typeof(StrikeMission), "AfterUpdate", HarmonyId);
			Api.Hooks(Api.Method(panelType, "DrawTargetPicker", typeof(void)), typeof(StrikeMission), "BeforeTargetPicker", null, HarmonyId);
			Api.Postfix(Api.Method(panelType, "DrawPlan", typeof(void)), typeof(StrikeMission), "AfterPlan", HarmonyId);
			Api.Postfix(Api.Method(panelType, "DrawWindow", typeof(void), typeof(int)), typeof(StrikeMission), "AfterWindow", HarmonyId);
			Api.Postfix(Api.Method(panelType, "LeaveMission", typeof(void)), typeof(StrikeMission), "AfterLeaveMission", HarmonyId);
			hooked = true;
			Api.Log("Coordinated Strike fire missions ready: Contacts-style target picker, several targets per mission, one time on target for all, and auto-fire (off until armed)");
		}
		catch (Exception error)
		{
			stopped = true;
			Api.LogFailure("strike fire missions unavailable; author panel retained", error);
		}
	}

	internal static void Bind(Assembly assembly)
	{
		panelType = Api.Type(assembly, "CoordinatedStrikeTool.StrikePanel");
		planType = Api.Type(assembly, "CoordinatedStrikeTool.StrikePlan");
		legType = Api.Type(assembly, "CoordinatedStrikeTool.StrikeLeg");
		dataType = Api.Type(assembly, "CoordinatedStrikeTool.GameData");
		stylesType = Api.Type(assembly, "CoordinatedStrikeTool.PanelStyles");
		listType = Api.Type(assembly, "CoordinatedStrikeTool.StrikePanel+ListView");
		filterType = Api.Type(assembly, "CoordinatedStrikeTool.StrikePanel+ContactFilter");
		pickerType = Api.Type(assembly, "CoordinatedStrikeTool.StrikePanel+Picker");
		Type timing = Api.Type(assembly, "CoordinatedStrikeTool.StrikePanel+Timing");
		Type domain = Api.Type(assembly, "CoordinatedStrikeTool.GameData+TargetDomain");
		Type status = Api.Type(assembly, "CoordinatedStrikeTool.LegStatus");
		if (!Enum.GetNames(status).SequenceEqual(new[] { "Ok", "OutOfRange", "TooClose", "TargetLost" }) ||
			!Enum.GetNames(domain).SequenceEqual(new[] { "Surface", "Air", "Subsurface", "Land" }) ||
			!Enum.GetNames(filterType).SequenceEqual(new[] { "All", "Air", "Surface", "Sub", "Land" }) ||
			!Enum.GetNames(pickerType).SequenceEqual(new[] { "None", "Target", "Shooter", "Weapon" }))
		{
			throw new MissingMemberException("inspected strike enums changed");
		}
		planField = Field(panelType, "_plan", planType);
		stylesField = Field(panelType, "_s", stylesType);
		filterField = Field(panelType, "_contactFilter", filterType);
		hostileField = Field(panelType, "_hostileOnly", typeof(bool));
		pickerListField = Field(panelType, "_pickerList", listType);
		taskforceField = Field(panelType, "_planTaskforce", typeof(Taskforce));
		focusedField = Field(panelType, "_fieldFocused", typeof(bool));
		prepLeadField = Field(panelType, "_prepLead", typeof(float));
		timingMethod = Api.Method(panelType, "CurrentTiming", timing, typeof(float));
		timingLead = Field(timing, "Lead", typeof(float));
		timingRequested = Field(timing, "RequestedImpact", typeof(float?));
		openMethod = Api.Method(panelType, "Open", typeof(void), pickerType);
		closeMethod = Api.Method(panelType, "Close", typeof(void));
		leftButton = Api.Method(panelType, "LeftButton", typeof(GUIStyle));
		resetAlerts = Api.Method(panelType, "ResetLaunchAlerts", typeof(void));
		beginList = Api.Method(panelType, "BeginList", typeof(void), listType, typeof(int), typeof(GUIStyle));
		listRow = Api.Method(panelType, "ListRow", typeof(void), listType);
		endList = Api.Method(panelType, "EndList", typeof(void), listType);
		savePrefs = Api.Method(panelType, "SavePrefs", typeof(void));
		foreach (string name in new[] { "Update", "DrawTargetPicker", "DrawPlan", "LeaveMission" })
		{
			Api.Method(panelType, name, typeof(void));
		}
		Api.Method(panelType, "DrawWindow", typeof(void), typeof(int));
		px = Api.Method(stylesType, "Px", typeof(int), typeof(float));
		foreach (string name in new[] { "Section", "Text", "TextBold", "Muted", "Hint", "Row", "RowAlt", "Button", "Primary", "Toggle", "Segment", "Field" })
		{
			Field(stylesType, name, typeof(GUIStyle));
		}

		legsField = Field(planType, "Legs", typeof(List<>).MakeGenericType(legType));
		impactField = Field(planType, "ImpactTime", typeof(float?));
		targetProperty = Property(planType, "Target", typeof(Vehicle), writable: true);
		lockedProperty = Property(planType, "IsLocked", typeof(bool));
		armingProperty = Property(planType, "Arming", typeof(bool));
		previewProperty = Property(planType, "PreviewImpactTime", typeof(float));
		planUpdate = Api.Method(planType, "Update", typeof(void), typeof(float), typeof(float), typeof(float?));
		planLock = Api.Method(planType, "Lock", typeof(void), typeof(float), typeof(float), typeof(float?), typeof(float));
		planUnlock = Api.Method(planType, "Unlock", typeof(void));
		planSimulate = Api.Method(planType, "SimulateDue", typeof(void), typeof(float), typeof(double));
		if (planType.GetConstructor(Type.EmptyTypes) == null || legType.GetConstructor(Type.EmptyTypes) == null)
		{
			throw new MissingMethodException("inspected strike plan constructors");
		}

		shooterField = Field(legType, "Shooter", typeof(ObjectBase));
		ammoField = Field(legType, "AmmoName", typeof(string));
		firedField = Field(legType, "Fired", typeof(bool));
		statusField = Field(legType, "Status", status);
		salvoField = Field(legType, "Salvo", typeof(int));
		launchedField = Field(legType, "Launched", typeof(int));
		launchTimeField = Field(legType, "LaunchTime", typeof(float));

		contacts = Static<Func<List<Vehicle>>>("Contacts", typeof(List<Vehicle>));
		contactLabel = Static<Func<Vehicle, string>>("ContactLabel", typeof(string), typeof(Vehicle));
		contactDetail = Static<Func<Vehicle, string>>("ContactDetail", typeof(string), typeof(Vehicle));
		vehicleAlive = Static<Func<Vehicle, bool>>("IsAlive", typeof(bool), typeof(Vehicle));
		relationColour = Static<Func<Vehicle, Color>>("RelationshipColor", typeof(Color), typeof(Vehicle));
		selectedUnit = Static<Func<ObjectBase>>("SelectedUnit", typeof(ObjectBase));
		ammoCount = Static<Func<ObjectBase, string, int>>("AmmoCount", typeof(int), typeof(ObjectBase), typeof(string));
		getAmmo = Static<Func<ObjectBase, string, Ammunition>>("GetAmmo", typeof(Ammunition), typeof(ObjectBase), typeof(string));
		unitLabel = Static<Func<ObjectBase, string>>("UnitLabel", typeof(string), typeof(ObjectBase));
		ammoLabel = Static<Func<Ammunition, string>>("AmmoLabel", typeof(string), typeof(Ammunition));
		prepareLaunchers = Static<Action<ObjectBase, string, Vehicle>>("PrepareLaunchers", typeof(void), typeof(ObjectBase), typeof(string), typeof(Vehicle));
		gameNow = Static<Func<float>>("get_Now", typeof(float));
		inMission = Static<Func<bool>>("get_InMission", typeof(bool));
		domainOf = Api.Method(dataType, "DomainOf", domain, typeof(Vehicle));
		if (!domainOf.IsStatic)
		{
			throw new MissingMethodException(dataType.FullName, "DomainOf");
		}

		// The native engage order the player's attack click gives.
		if (typeof(EngageTask).GetConstructor(new[] { typeof(string), typeof(ObjectBase), typeof(ObjectBase), typeof(int), typeof(int), typeof(bool), typeof(bool) }) == null ||
			Api.Method(typeof(ObjectBase), "AddEngageTask", typeof(void), typeof(EngageTask)).IsStatic ||
			Api.Method(typeof(ObjectBase), "RemoveEngageTask", typeof(void), typeof(EngageTask)).IsStatic ||
			typeof(ObjectBase).GetField("_currentEngageTasks", Api.All)?.FieldType != typeof(List<EngageTask>) ||
			typeof(AmmunitionParameters).GetField("_ammunitionFileName", Api.All)?.FieldType != typeof(string))
		{
			throw new MissingMemberException("inspected native engage order");
		}
	}

	// Contact Log's store, matched by the plotting-table Vehicle it records.
	internal static void BindContactLog(Assembly assembly)
	{
		contactLogType = Api.Type(assembly, "ContactLog.ContactLogBehaviour");
		Type store = Api.Type(assembly, "ContactLog.ContactStore");
		Type record = Api.Type(assembly, "ContactLog.ContactRecord");
		storeField = Field(contactLogType, "_store", store);
		recordsProperty = Property(store, "Records", typeof(IEnumerable<>).MakeGenericType(record));
		recClass = Field(record, "Class", typeof(string));
		recType = Field(record, "Type", typeof(string));
		recUnitName = Field(record, "UnitName", typeof(string));
		recSeen = Field(record, "SeenVisually", typeof(bool));
		recWeapon = Field(record, "IsWeapon", typeof(bool));
		recAlt = Field(record, "AltFt", typeof(double));
		recHandle = Field(record, "Handle", typeof(object));
		recKey = Field(record, "Key", typeof(string));
		recActive = Field(record, "Active", typeof(List<string>));
	}

	private static FieldInfo Field(Type owner, string name, Type type)
	{
		FieldInfo field = owner.GetField(name, Api.All);
		if (field == null || field.FieldType != type)
		{
			throw new MissingFieldException(owner.FullName, name);
		}
		return field;
	}

	private static PropertyInfo Property(Type owner, string name, Type type, bool writable = false)
	{
		PropertyInfo property = owner.GetProperty(name, Api.All);
		if (property == null || property.PropertyType != type || property.GetGetMethod(true) == null || (writable && property.GetSetMethod(true) == null))
		{
			throw new MissingMemberException(owner.FullName, name);
		}
		return property;
	}

	private static T Static<T>(string name, Type returns, params Type[] parameters) where T : class
	{
		MethodInfo method = Api.Method(dataType, name, returns, parameters);
		if (!method.IsStatic)
		{
			throw new MissingMethodException(dataType.FullName, name);
		}
		return (T)(object)Delegate.CreateDelegate(typeof(T), method);
	}

	internal static void Fail(string what, Exception error)
	{
		if (stopped)
		{
			return;
		}
		stopped = true;
		Disarm("fire missions stopped");
		Api.LogFailure(what + "; fire missions stopped, author panel retained", error);
	}

	// ---- plan access -------------------------------------------------------

	private static object Active => panel == null ? null : planField.GetValue(panel);
	private static Vehicle TargetOf(object plan) => (Vehicle)targetProperty.GetValue(plan, null);
	private static IList LegsOf(object plan) => (IList)legsField.GetValue(plan);
	private static bool Locked(object plan) => (bool)lockedProperty.GetValue(plan, null);
	private static bool Arming(object plan) => (bool)armingProperty.GetValue(plan, null);
	private static float? Impact(object plan) => (float?)impactField.GetValue(plan);
	private static int Status(object leg) => Convert.ToInt32(statusField.GetValue(leg), CultureInfo.InvariantCulture);
	private static bool Alive(Vehicle v) => v != null && vehicleAlive(v);
	private static int Px(float value) => (int)px.Invoke(stylesField.GetValue(panel), new object[] { value });
	private static GUIStyle Style(string name) => (GUIStyle)stylesType.GetField(name, Api.All).GetValue(stylesField.GetValue(panel));
	private static GUILayoutOption W(float width) => GUILayout.Width(Px(width));

	private static void Timing(float now, out float lead, out float? requested)
	{
		object timing = timingMethod.Invoke(panel, new object[] { now });
		lead = (float)timingLead.GetValue(timing);
		requested = (float?)timingRequested.GetValue(timing);
	}

	private static void EnsureActiveListed()
	{
		object active = Active;
		if (active != null && !plans.Contains(active))
		{
			plans.Insert(0, active);
		}
	}

	private static void MakeActive(object plan)
	{
		if (plan == null || plan == Active)
		{
			return;
		}
		planField.SetValue(panel, plan);
		resetAlerts.Invoke(panel, null);
	}

	private static object PlanFor(Vehicle v)
	{
		foreach (object plan in plans)
		{
			if (TargetOf(plan) == v)
			{
				return plan;
			}
		}
		return null;
	}

	private static object AddTarget(Vehicle v)
	{
		EnsureActiveListed();
		object existing = PlanFor(v);
		if (existing != null)
		{
			return existing;
		}
		object active = Active;
		if (active != null && TargetOf(active) == null && LegsOf(active).Count == 0)
		{
			targetProperty.SetValue(active, v, null);
			return active;
		}
		object plan = Activator.CreateInstance(planType, true);
		targetProperty.SetValue(plan, v, null);
		plans.Add(plan);
		return plan;
	}

	private static void RemovePlan(object plan)
	{
		if (plans.Count <= 1)
		{
			return;
		}
		CancelOrders(plan);
		int index = plans.IndexOf(plan);
		plans.Remove(plan);
		if (plan == Active)
		{
			MakeActive(plans[Math.Min(index, plans.Count - 1)]);
		}
	}

	private static void CopyShooters(object from, object to)
	{
		IList target = LegsOf(to);
		foreach (object leg in LegsOf(from))
		{
			object copy = Activator.CreateInstance(legType, true);
			shooterField.SetValue(copy, shooterField.GetValue(leg));
			ammoField.SetValue(copy, ammoField.GetValue(leg));
			salvoField.SetValue(copy, salvoField.GetValue(leg));
			target.Add(copy);
		}
	}

	private static void Clear(string why)
	{
		Disarm(why);
		object active = Active;
		plans.Clear();
		if (active != null)
		{
			plans.Add(active);
		}
		events.Clear();
		search = "";
		pickerRows = new List<Row>();
		rowsKey = null;
	}

	// ---- per-frame work (postfix on the author's Update) -------------------

	internal static void AfterUpdate(object __instance)
	{
		if (stopped)
		{
			return;
		}
		try
		{
			panel = __instance;
			if (!inMission())
			{
				if (plans.Count > 1 || armed)
				{
					Clear("left the mission");
				}
				return;
			}
			Taskforce current = (Taskforce)taskforceField.GetValue(__instance);
			if (current != taskforce)
			{
				if (taskforce != null)
				{
					Clear("task force changed");
				}
				taskforce = current;
			}
			EnsureActiveListed();
			float now = gameNow();
			object active = Active;
			if (plans.Count > 1 && Time.unscaledTime >= nextUpdate)
			{
				nextUpdate = Time.unscaledTime + 0.25f;
				Timing(now, out float lead, out float? requested);
				float prep = (float)prepLeadField.GetValue(__instance);
				foreach (object plan in plans)
				{
					if (plan == active)
					{
						continue;
					}
					planUpdate.Invoke(plan, new object[] { now, lead, requested });
					if (Locked(plan) && prep > 0f)
					{
						Prepare(plan, now, prep);
					}
				}
			}
			if (plans.Count > 1)
			{
				foreach (object plan in plans)
				{
					if (plan != active && LegsOf(plan).Count > 0)
					{
						planSimulate.Invoke(plan, new object[] { now, 1.0 });
					}
				}
			}
			if (armed)
			{
				AutoFire(now);
			}
			if (confirmArm && Time.unscaledTime > confirmUntil)
			{
				confirmArm = false;
			}
		}
		catch (Exception error)
		{
			Fail("strike mission update failed", error);
		}
	}

	// The author readies launchers only for the plan on show; SEST does the
	// same, with the author's own helper and lead, for the other targets.
	private static void Prepare(object plan, float now, float prep)
	{
		Vehicle target = TargetOf(plan);
		if (!Alive(target))
		{
			return;
		}
		foreach (object leg in LegsOf(plan))
		{
			float until = (float)launchTimeField.GetValue(leg) - now;
			if (!(bool)firedField.GetValue(leg) && (int)launchedField.GetValue(leg) <= 0 && Status(leg) == StrikeMissionPolicy.StatusOk && until <= prep && until >= -30f)
			{
				prepareLaunchers((ObjectBase)shooterField.GetValue(leg), (string)ammoField.GetValue(leg), target);
			}
		}
	}

	private static void AutoFire(float now)
	{
		foreach (object plan in plans)
		{
			Vehicle target = TargetOf(plan);
			bool alive = Alive(target);
			bool locked = Locked(plan), arming = Arming(plan);
			foreach (object leg in LegsOf(plan))
			{
				Order order = orders.GetValue(leg, _ => new Order());
				bool pending = order.Task != null && order.Shooter != null && order.Shooter._currentEngageTasks.Contains(order.Task);
				int shots = StrikeMissionPolicy.ShotsToOrder(armed, locked, arming, alive, Status(leg), (bool)firedField.GetValue(leg),
					(int)salvoField.GetValue(leg), (int)launchedField.GetValue(leg), (float)launchTimeField.GetValue(leg), now, order.Sent, pending, order.LastAt);
				if (shots <= 0)
				{
					continue;
				}
				ObjectBase shooter = (ObjectBase)shooterField.GetValue(leg);
				string name = (string)ammoField.GetValue(leg);
				Ammunition ammo = shooter == null || shooter.IsDestroyed ? null : getAmmo(shooter, name);
				if (ammo?._ap == null || target.Object == null)
				{
					order.Sent = StrikeMissionPolicy.MaxOrders;
					Note("Auto-fire skipped " + name + ": weapon or target no longer available");
					continue;
				}
				var task = new EngageTask(ammo._ap._ammunitionFileName, target.Object, shooter, shots);
				shooter.AddEngageTask(task);
				order.Sent++;
				order.LastAt = now;
				order.Task = task;
				order.Shooter = shooter;
				issued.Add(order);
				Note("Auto-fire: " + unitLabel(shooter) + " ordered " + shots + " x " + ammoLabel(ammo) + " at " + contactLabel(target) + (order.Sent > 1 ? " (retry " + (order.Sent - 1) + ")" : ""));
			}
		}
	}

	private static void CancelOrders(object plan)
	{
		foreach (object leg in LegsOf(plan))
		{
			if (orders.TryGetValue(leg, out Order order))
			{
				Withdraw(order);
			}
		}
	}

	// Orders SEST issued that the game still holds are withdrawn, so no
	// further rounds of them launch; weapons already in the air are not touched.
	private static void Withdraw(Order order)
	{
		try
		{
			if (order.Task != null && order.Shooter != null && !order.Shooter.IsDestroyed && order.Shooter._currentEngageTasks.Contains(order.Task))
			{
				order.Shooter.RemoveEngageTask(order.Task);
			}
		}
		catch (Exception error)
		{
			Api.LogFailure("auto-fire order could not be withdrawn", error);
		}
		order.Task = null;
	}

	private static void Disarm(string why)
	{
		if (armed)
		{
			Api.Log("Coordinated Strike auto-fire disarmed: " + why);
		}
		armed = false;
		confirmArm = false;
		foreach (Order order in issued)
		{
			Withdraw(order);
		}
		issued.Clear();
	}

	private static void Note(string text)
	{
		Api.Log("Coordinated Strike " + text);
		events.Insert(0, text);
		if (events.Count > 4)
		{
			events.RemoveAt(events.Count - 1);
		}
	}

	internal static void AfterLeaveMission()
	{
		if (!stopped)
		{
			Clear("left the mission");
			taskforce = null;
		}
	}

	// The search box suppresses game hotkeys the way the author's own fields do.
	internal static void AfterWindow(object __instance)
	{
		if (stopped || Event.current == null || Event.current.type != EventType.Repaint)
		{
			return;
		}
		try
		{
			if (GUI.GetNameOfFocusedControl() == SearchControl)
			{
				focusedField.SetValue(__instance, true);
			}
		}
		catch (Exception error)
		{
			Fail("strike search focus", error);
		}
	}

	// ---- FIRE MISSION section (postfix on DrawPlan) ------------------------

	internal static void AfterPlan(object __instance)
	{
		if (stopped)
		{
			return;
		}
		try
		{
			panel = __instance;
			EnsureActiveListed();
			float now = gameNow();
			object active = Active;
			GUILayout.Space(Px(8f));
			GUILayout.BeginHorizontal();
			GUILayout.Label("FIRE MISSION  ·  " + plans.Count + (plans.Count == 1 ? " target" : " targets"), Style("Section"));
			GUILayout.FlexibleSpace();
			if (GUILayout.Button("+  Add targets", Style("Button"), W(140f)))
			{
				OpenTargetPicker();
			}
			GUILayout.EndHorizontal();
			if (plans.Count > 1)
			{
				int n = 0;
				foreach (object plan in plans.ToList())
				{
					DrawPackage(plan, plan == active, now, (n++ % 2 == 0) ? Style("Row") : Style("RowAlt"));
				}
				DrawOverCommitted();
				DrawMissionLock(now);
			}
			else
			{
				GUILayout.Label("Add more targets to plan one fire mission against several tracks; each target keeps its own shooters.", Style("Hint"));
			}
			DrawAutoFire();
		}
		catch (Exception error)
		{
			Fail("strike mission drawing failed", error);
		}
	}

	private static void OpenTargetPicker()
	{
		openMethod.Invoke(panel, new object[] { Enum.ToObject(pickerType, 1) });
	}

	private static void DrawPackage(object plan, bool isActive, float now, GUIStyle rowStyle)
	{
		Vehicle target = TargetOf(plan);
		IList legs = LegsOf(plan);
		int rounds = 0, launched = 0, ok = 0, problems = 0;
		foreach (object leg in legs)
		{
			rounds += (int)salvoField.GetValue(leg);
			launched += (int)launchedField.GetValue(leg);
			if (Status(leg) == StrikeMissionPolicy.StatusOk)
			{
				ok++;
			}
			else
			{
				problems++;
			}
		}
		string state;
		Color colour = new Color(0.61f, 0.68f, 0.73f);
		if (!Alive(target))
		{
			state = target == null ? "No target" : "Target lost";
			colour = new Color(1f, 0.35f, 0.31f);
		}
		else if (legs.Count == 0)
		{
			state = "No shooters";
			colour = new Color(1f, 0.78f, 0.24f);
		}
		else if (Locked(plan) && Impact(plan).HasValue)
		{
			state = launched >= rounds ? "All " + rounds + " launched" : "TOT in " + Clock(Impact(plan).Value - now) + "  ·  " + launched + "/" + rounds + " away";
			colour = new Color(0.30f, 0.85f, 0.39f);
		}
		else
		{
			state = ok + "/" + legs.Count + " legs in range" + (problems > 0 ? "" : "  ·  ready");
			colour = problems > 0 ? new Color(1f, 0.78f, 0.24f) : new Color(0.72f, 0.87f, 0.77f);
		}
		GUILayout.BeginHorizontal(rowStyle);
		GUILayout.Label(isActive ? ">" : " ", Style("TextBold"), W(14f));
		GUIStyle name = new GUIStyle(Style("TextBold"));
		name.normal.textColor = Alive(target) ? Color.Lerp(relationColour(target), new Color(0.86f, 0.89f, 0.92f), 0.45f) : new Color(0.61f, 0.68f, 0.73f);
		GUILayout.Label(target == null ? "(no target)" : contactLabel(target), name, W(250f));
		GUILayout.Label(legs.Count + (legs.Count == 1 ? " leg, " : " legs, ") + rounds + " rds", Style("Muted"), W(120f));
		GUIStyle stateStyle = new GUIStyle(Style("Text"));
		stateStyle.normal.textColor = colour;
		GUILayout.Label(state, stateStyle, W(210f));
		GUILayout.FlexibleSpace();
		if (isActive)
		{
			GUILayout.Label("Editing", Style("Muted"), W(70f));
		}
		else if (GUILayout.Button("Edit", Style("Button"), W(70f)))
		{
			MakeActive(plan);
		}
		if (!isActive && legs.Count == 0 && LegsOf(Active).Count > 0 && GUILayout.Button("Copy shooters", Style("Button"), W(120f)))
		{
			CopyShooters(Active, plan);
		}
		if (GUILayout.Button("x", Style("Button"), W(30f)))
		{
			RemovePlan(plan);
		}
		GUILayout.EndHorizontal();
	}

	private static void DrawOverCommitted()
	{
		var planned = new List<KeyValuePair<string, int>>();
		var units = new Dictionary<string, Tuple<ObjectBase, string>>(StringComparer.Ordinal);
		foreach (object plan in plans)
		{
			foreach (object leg in LegsOf(plan))
			{
				if ((bool)firedField.GetValue(leg))
				{
					continue;
				}
				ObjectBase shooter = (ObjectBase)shooterField.GetValue(leg);
				string ammo = (string)ammoField.GetValue(leg);
				if (shooter == null || shooter.IsDestroyed)
				{
					continue;
				}
				string key = shooter.GetInstanceID() + "|" + ammo;
				units[key] = Tuple.Create(shooter, ammo);
				planned.Add(new KeyValuePair<string, int>(key, (int)salvoField.GetValue(leg) - (int)launchedField.GetValue(leg)));
			}
		}
		foreach (var over in StrikeMissionPolicy.OverCommitted(planned, key => ammoCount(units[key].Item1, units[key].Item2)))
		{
			var unit = units[over.Key];
			Ammunition ammo = getAmmo(unit.Item1, unit.Item2);
			GUIStyle warn = new GUIStyle(Style("Muted"));
			warn.normal.textColor = new Color(1f, 0.78f, 0.24f);
			GUILayout.Label(unitLabel(unit.Item1) + ": " + over.Value[0] + " x " + (ammo == null ? unit.Item2 : ammoLabel(ammo)) + " planned across targets, " + over.Value[1] + " carried", warn);
		}
	}

	private static void DrawMissionLock(float now)
	{
		bool anyLocked = plans.Any(Locked);
		GUILayout.BeginHorizontal();
		bool same = GUILayout.Toggle(sameTimeOnTarget, "Same time on target for all: " + (sameTimeOnTarget ? "ON" : "OFF"), Style("Toggle"), GUILayout.ExpandWidth(false));
		if (same != sameTimeOnTarget && !anyLocked)
		{
			sameTimeOnTarget = same;
		}
		GUILayout.FlexibleSpace();
		if (anyLocked)
		{
			if (GUILayout.Button("Unlock all targets", Style("Button"), W(190f)))
			{
				foreach (object plan in plans)
				{
					CancelOrders(plan);
					planUnlock.Invoke(plan, null);
				}
				resetAlerts.Invoke(panel, null);
			}
		}
		else if (GUILayout.Button("LOCK ALL TARGETS", Style("Primary"), W(190f)))
		{
			LockAll(now);
		}
		GUILayout.EndHorizontal();
	}

	private static void LockAll(float now)
	{
		Timing(now, out float lead, out float? requested);
		var ready = new List<object>();
		foreach (object plan in plans)
		{
			planUpdate.Invoke(plan, new object[] { now, lead, requested });
			if (Alive(TargetOf(plan)) && LegsOf(plan).Cast<object>().Any(l => Status(l) == StrikeMissionPolicy.StatusOk))
			{
				ready.Add(plan);
			}
		}
		if (ready.Count == 0)
		{
			Note("Nothing to lock: no target has a shooter in range");
			return;
		}
		float? impact = sameTimeOnTarget ? StrikeMissionPolicy.CommonImpact(ready.Select(p => (float)previewProperty.GetValue(p, null)), requested) : requested;
		foreach (object plan in ready)
		{
			planLock.Invoke(plan, new object[] { now, lead, impact, 0f });
		}
		resetAlerts.Invoke(panel, null);
		int skipped = plans.Count - ready.Count;
		Note("Locked " + ready.Count + (ready.Count == 1 ? " target" : " targets") + (sameTimeOnTarget && impact.HasValue ? ", time on target in " + Clock(impact.Value - now) : "") + (skipped > 0 ? "; " + skipped + " not ready and left unlocked" : ""));
	}

	private static void DrawAutoFire()
	{
		GUILayout.BeginHorizontal();
		GUIStyle state = new GUIStyle(Style("TextBold"));
		state.normal.textColor = armed ? new Color(1f, 0.35f, 0.31f) : new Color(0.61f, 0.68f, 0.73f);
		GUILayout.Label(armed ? "AUTO-FIRE ARMED" : "AUTO-FIRE OFF", state, W(170f));
		GUILayout.Label(armed ? "Locked legs are fired at their launch times." : "You launch each leg yourself.", Style("Muted"));
		GUILayout.FlexibleSpace();
		if (armed)
		{
			if (GUILayout.Button("Disarm", Style("Button"), W(150f)))
			{
				Disarm("player");
				Note("Auto-fire disarmed; queued orders were withdrawn");
			}
		}
		else if (!confirmArm)
		{
			if (GUILayout.Button("Arm auto-fire", Style("Button"), W(150f)))
			{
				confirmArm = true;
				confirmUntil = Time.unscaledTime + 4f;
			}
		}
		else if (GUILayout.Button("Confirm: ARM", Style("Primary"), W(150f)))
		{
			armed = true;
			confirmArm = false;
			Note("Auto-fire armed");
		}
		GUILayout.EndHorizontal();
		foreach (string line in events)
		{
			GUILayout.Label(line, Style("Hint"));
		}
	}

	private static string Clock(float seconds)
	{
		if (seconds < 0f)
		{
			return "now";
		}
		int s = Mathf.RoundToInt(seconds);
		return s >= 3600 ? (s / 3600) + ":" + (s / 60 % 60).ToString("00") + ":" + (s % 60).ToString("00") : (s / 60) + ":" + (s % 60).ToString("00");
	}

	// ---- Target picker (replaces the author's DrawTargetPicker) ------------

	internal static bool BeforeTargetPicker(object __instance)
	{
		if (stopped)
		{
			return true;
		}
		try
		{
			panel = __instance;
			EnsureActiveListed();
			DrawPicker();
		}
		catch (Exception error)
		{
			Fail("strike target picker failed", error);
		}
		return false;
	}

	private static void DrawPicker()
	{
		object listView = pickerListField.GetValue(panel);
		GUILayout.Label("SELECT TARGET TRACKS", Style("Section"));
		GUILayout.Label("Click a track to target it with the plan on show.  +  adds it to the fire mission as another target.", Style("Muted"));

		GUILayout.BeginHorizontal();
		int filter = Convert.ToInt32(filterField.GetValue(panel), CultureInfo.InvariantCulture);
		string[] names = Enum.GetNames(filterType);
		for (int i = 0; i < names.Length; i++)
		{
			if (GUILayout.Toggle(filter == i, names[i], Style("Segment"), W(66f)) && filter != i)
			{
				filterField.SetValue(panel, Enum.ToObject(filterType, i));
				savePrefs.Invoke(panel, null);
			}
		}
		GUILayout.Space(Px(8f));
		bool hostile = (bool)hostileField.GetValue(panel);
		bool hostileNow = GUILayout.Toggle(hostile, "Hostile only: " + (hostile ? "ON" : "OFF"), Style("Toggle"), GUILayout.ExpandWidth(false));
		if (hostileNow != hostile)
		{
			hostileField.SetValue(panel, hostileNow);
			savePrefs.Invoke(panel, null);
		}
		GUILayout.FlexibleSpace();
		GUILayout.EndHorizontal();

		GUILayout.BeginHorizontal();
		GUILayout.Label("Find", Style("Muted"), W(40f));
		GUI.SetNextControlName(SearchControl);
		search = GUILayout.TextField(search ?? "", 40, Style("Field"), W(200f));
		GUILayout.Space(Px(12f));
		GUILayout.Label("Sort", Style("Muted"), W(40f));
		foreach (StrikeMissionPolicy.Sort s in Enum.GetValues(typeof(StrikeMissionPolicy.Sort)))
		{
			if (GUILayout.Toggle(sort == s, s.ToString(), Style("Segment"), W(72f)) && sort != s)
			{
				sort = s;
			}
		}
		GUILayout.FlexibleSpace();
		GUILayout.EndHorizontal();

		RefreshContactLog();
		ObjectBase origin = selectedUnit();
		if (origin == null || origin.IsDestroyed || origin.isWeapon())
		{
			origin = null;
		}
		// Rows are rebuilt only on a Layout pass (so Layout and Repaint draw the
		// same controls) and at most four times a second.
		string key = filter + "|" + hostileNow + "|" + sort + "|" + search + "|" + (origin == null ? 0 : origin.GetInstanceID());
		if (Event.current.type == EventType.Layout && (key != rowsKey || Time.unscaledTime >= rowsNext))
		{
			rowsKey = key;
			rowsNext = Time.unscaledTime + 0.25f;
			List<Vehicle> all = contacts();
			rowsTotal = all.Count;
			var rows = new List<Row>();
			foreach (Vehicle v in all)
			{
				Row row = Describe(v, origin);
				if (filter != 0 && row.Domain != FilterDomain[filter])
				{
					continue;
				}
				if (hostileNow && row.Relation != 0)
				{
					continue;
				}
				if (!StrikeMissionPolicy.Matches(search, row.Label, row.Detail, row.Group))
				{
					continue;
				}
				rows.Add(row);
			}
			rows.Sort((a, b) => StrikeMissionPolicy.Compare(sort, a.Relation, a.RangeNm, a.Label, a.SpeedKt, b.Relation, b.RangeNm, b.Label, b.SpeedKt));
			pickerRows = rows;
		}
		List<Row> shown = pickerRows;
		string from = origin != null ? "Range and bearing from " + unitLabel(origin) : "Select one of your units in game for range and bearing";
		GUILayout.Label(from + (rowsTotal > shown.Count ? "  ·  " + (rowsTotal - shown.Count) + " filtered out" : "") + (contactLog != null ? "  ·  class and identity from Contacts" : ""), Style("Muted"));

		GUILayout.BeginHorizontal();
		GUILayout.Space(Px(6f));
		GUILayout.Label("", Style("Muted"), W(38f));
		GUILayout.Label("Track", Style("Muted"), W(220f));
		GUILayout.Label("Class / identity", Style("Muted"), W(190f));
		GUILayout.Label("Range", Style("Muted"), W(62f));
		GUILayout.Label("Brg", Style("Muted"), W(40f));
		GUILayout.Label("Speed", Style("Muted"), W(56f));
		GUILayout.Label("Crs", Style("Muted"), W(40f));
		GUILayout.Label("Alt / depth", Style("Muted"), W(80f));
		GUILayout.EndHorizontal();

		GUIStyle rowStyle = Style("Row");
		beginList.Invoke(panel, new object[] { listView, 15, rowStyle });
		if (shown.Count == 0)
		{
			GUILayout.Label(rowsTotal == 0 ? "No contacts on the plot." : "No contacts match the filters.", Style("Muted"));
		}
		object active = Active;
		Vehicle activeTarget = TargetOf(active);
		foreach (int g in GroupOrder)
		{
			List<Row> members = shown.Where(r => r.Domain == g).ToList();
			if (members.Count == 0)
			{
				continue;
			}
			bool shut = collapsed.Contains(g);
			if (GUILayout.Button((shut ? "+  " : "-  ") + GroupNames[g] + "  (" + members.Count + ")", Style("Section")))
			{
				if (shut)
				{
					collapsed.Remove(g);
				}
				else
				{
					collapsed.Add(g);
				}
			}
			listRow.Invoke(panel, new[] { listView });
			if (shut)
			{
				continue;
			}
			int n = 0;
			foreach (Row row in members)
			{
				DrawPickerRow(row, row.Vehicle == activeTarget, PlanFor(row.Vehicle) != null, (n++ % 2 == 0) ? rowStyle : Style("RowAlt"));
				listRow.Invoke(panel, new[] { listView });
			}
		}
		endList.Invoke(panel, new[] { listView });

		GUILayout.Space(Px(6f));
		GUILayout.BeginHorizontal();
		GUILayout.Label(plans.Count + (plans.Count == 1 ? " target in the fire mission" : " targets in the fire mission"), Style("Muted"));
		GUILayout.FlexibleSpace();
		if (GUILayout.Button("Done", Style("Button"), W(120f)))
		{
			closeMethod.Invoke(panel, null);
		}
		GUILayout.EndHorizontal();
	}

	private static void DrawPickerRow(Row row, bool isActiveTarget, bool inMission, GUIStyle style)
	{
		GUILayout.BeginHorizontal(style);
		if (inMission)
		{
			GUILayout.Label(isActiveTarget ? " >" : " in", Style("Muted"), W(38f));
		}
		else if (GUILayout.Button("+", Style("Button"), W(38f)))
		{
			AddTarget(row.Vehicle);
		}
		GUIStyle track = (GUIStyle)leftButton.Invoke(panel, null);
		track.normal.textColor = row.Colour;
		track.hover.textColor = row.Colour;
		if (GUILayout.Button(row.Label, track, W(220f)))
		{
			object existing = PlanFor(row.Vehicle);
			if (existing != null)
			{
				MakeActive(existing);
			}
			else
			{
				targetProperty.SetValue(Active, row.Vehicle, null);
			}
			closeMethod.Invoke(panel, null);
		}
		GUILayout.Label(row.Detail, Style("Text"), W(190f));
		GUILayout.Label(double.IsNaN(row.RangeNm) ? "-" : row.RangeNm.ToString("F1", CultureInfo.InvariantCulture) + " nm", Style("Text"), W(62f));
		GUILayout.Label(StrikeMissionPolicy.Compass(row.Bearing), Style("Text"), W(40f));
		GUILayout.Label(double.IsNaN(row.SpeedKt) ? "-" : row.SpeedKt.ToString("F0", CultureInfo.InvariantCulture) + " kt", Style("Text"), W(56f));
		GUILayout.Label(row.SpeedKt >= 1 ? StrikeMissionPolicy.Compass(row.Course) : "-", Style("Text"), W(40f));
		GUILayout.Label(double.IsNaN(row.AltFt) ? "" : Math.Round(Math.Abs(row.AltFt)).ToString("N0", CultureInfo.InvariantCulture) + " ft", Style("Text"), W(80f));
		GUILayout.EndHorizontal();
	}

	private static Row Describe(Vehicle v, ObjectBase origin)
	{
		var row = new Row { Vehicle = v, Label = contactLabel(v) };
		row.Domain = Convert.ToInt32(domainOf.Invoke(null, new object[] { v }), CultureInfo.InvariantCulture);
		int relation = Convert.ToInt32(v.CurrentRelationship(), CultureInfo.InvariantCulture);
		row.Relation = relation == 1 ? 0 : relation == 0 ? 1 : relation == 2 ? 2 : 3;
		row.Colour = Color.Lerp(relationColour(v), new Color(0.86f, 0.89f, 0.92f), 0.45f);
		Vector3 velocity = v.UnityVelocityVector;
		row.SpeedKt = new Vector2(velocity.x, velocity.z).magnitude * KnotsPerUnity;
		row.Course = Math.Atan2(velocity.x, velocity.z) * 180.0 / Math.PI;
		if (origin != null && v.KnownUnityPosition.HasValue)
		{
			Vector3 to = v.KnownUnityPosition.Value - origin.transform.position;
			row.RangeNm = new Vector2(to.x, to.z).magnitude / 27.559496f;
			row.Bearing = Math.Atan2(to.x, to.z) * 180.0 / Math.PI;
		}
		object record = Record(v);
		string detail = "";
		if (record != null)
		{
			string cls = (string)recClass.GetValue(record) ?? "";
			string ident = !(bool)recWeapon.GetValue(record) && (bool)recSeen.GetValue(record) ? (string)recUnitName.GetValue(record) ?? "" : "";
			detail = cls.Length > 0 && ident.Length > 0 ? cls + "  ·  " + ident : cls + ident;
			string type = (string)recType.GetValue(record) ?? "";
			double alt = (double)recAlt.GetValue(record);
			if (type == "Aircraft" || type == "Subsurface")
			{
				row.AltFt = alt;
			}
			var active = (List<string>)recActive.GetValue(record);
			row.Group = type + " " + (active == null ? "" : string.Join(" ", active.ToArray()));
		}
		row.Detail = detail.Length > 0 ? detail : contactDetail(v);
		return row;
	}

	private static object Record(Vehicle v)
	{
		if (contactLog == null)
		{
			return null;
		}
		if (records.TryGetValue(v, out object record))
		{
			return record;
		}
		recordsByKey.TryGetValue(v.Id.ToString(CultureInfo.InvariantCulture), out record);
		return record;
	}

	private static void RefreshContactLog()
	{
		if (RealNow < contactLogNext)
		{
			return;
		}
		contactLogNext = RealNow + 0.5;
		try
		{
			if (!contactLogTried)
			{
				contactLogTried = true;
				Assembly assembly = AppDomain.CurrentDomain.GetAssemblies().FirstOrDefault(a => a.GetType("ContactLog.ContactLogBehaviour", false) != null);
				if (assembly == null)
				{
					return;
				}
				using (var sha = System.Security.Cryptography.SHA256.Create())
				using (var stream = System.IO.File.OpenRead(BetaAssemblyPolicy.OriginalLocation(assembly)))
				{
					if (BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant() != ContactLogHash)
					{
						Api.Log("Coordinated Strike picker: uninspected Contact Log image; class and identity columns use the strike tool's own labels");
						return;
					}
				}
				BindContactLog(assembly);
			}
			if (contactLogType == null || storeField == null)
			{
				return;
			}
			if (contactLog == null)
			{
				contactLog = UnityEngine.Object.FindObjectOfType(contactLogType);
				if (contactLog == null)
				{
					return;
				}
			}
			var byVehicle = new Dictionary<Vehicle, object>();
			var byKey = new Dictionary<string, object>(StringComparer.Ordinal);
			object store = storeField.GetValue(contactLog);
			if (store != null && recordsProperty.GetValue(store, null) is IEnumerable all)
			{
				foreach (object record in all)
				{
					if (recHandle.GetValue(record) is Vehicle v)
					{
						byVehicle[v] = record;
					}
					string key = (string)recKey.GetValue(record);
					if (key != null)
					{
						byKey[key] = record;
					}
				}
			}
			records = byVehicle;
			recordsByKey = byKey;
		}
		catch (Exception error)
		{
			contactLogType = null;
			contactLog = null;
			records = new Dictionary<Vehicle, object>();
			recordsByKey = new Dictionary<string, object>(StringComparer.Ordinal);
			Api.LogFailure("Contact Log columns unavailable in the strike picker; strike tool labels used", error);
		}
	}
}
