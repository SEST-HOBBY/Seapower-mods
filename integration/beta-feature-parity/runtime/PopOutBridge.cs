using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Security.Cryptography;
using Noesis;
using SeapowerUI;
using SeapowerUI.ViewModels;

namespace Sest.RuntimeFixes;

internal static class PopOutBridge
{
	private sealed class FormEntry
	{
		internal Button Button;

		internal object Bar;

		internal bool Initialized;
	}

	private const string PopHash = "5709ed68af4623fceee3f3badc8e06bdb9b98f8e095fb0deac2685a9ebc5fc36";

	private const string Pop123Hash = "6f3668aaebe366f4fecc3de5af6a1479f1765d50f176b2bd68b3434191ce3ce5";

	private const string FormationHash = "6230e8e78e2ba7ba222241d0c3dcc881d2507ebeeb4eab24b6401cc9144283dd";

	private static Type screenType;

	private static PropertyInfo instance;

	private static FieldInfo root;

	private static FieldInfo host;

	private static MethodInfo opening;

	private static MethodInfo decorate;

	private static MethodInfo move;

	private static MethodInfo place;

	private static MethodInfo openStandalone;

	private static PropertyInfo displayAvailable;

	private static FieldInfo trackedWindows;

	private static FieldInfo screenDisplay;

	private static FieldInfo hintField;

	private static FieldInfo keepField;

	private static bool pop123;

	private static bool strikeSurface;

	private static bool strikeSurfaceRejected;

	private static double screenRetry;

	private static bool formationBound;

	private static bool popRejected;

	private static bool formationRejected;

	private static bool formationErrorReported;

	private static double retry;

	[ThreadStatic]
	private static MainGameViewModel scopedMain;

	[ThreadStatic]
	private static FrameworkElement scopedRoot;

	private static readonly ConditionalWeakTable<Window, FormEntry> forms = new ConditionalWeakTable<Window, FormEntry>();

	private static object Screen => (!(instance == null)) ? instance.GetValue(null, null) : null;

	internal static bool CanOpenStandalone => Screen != null && displayAvailable != null && (bool)displayAvailable.GetValue(null, null);

	internal static bool ScreenBound => strikeSurface && Screen != null;

	internal static bool ScreenOpen => strikeSurface && Root != null;

	internal static int ScreenDisplay
	{
		get
		{
			object screen = Screen;
			return (screen != null && screenDisplay != null) ? ((int)screenDisplay.GetValue(screen)) : (-1);
		}
	}

	internal static FrameworkElement Root
	{
		get
		{
			object screen = Screen;
			return (screen != null) ? (root.GetValue(screen) as FrameworkElement) : null;
		}
	}

	private static WindowHost Host
	{
		get
		{
			object screen = Screen;
			return (screen != null) ? (host.GetValue(screen) as WindowHost) : null;
		}
	}

	// R12 adapts the Group Manager into the loader's private cache. Hash the
	// Workshop file the loader recorded for it (an unadapted image is its own
	// location), exactly as ContactsFix.Require and WorldOperations do.
	private static bool HashMatches(Assembly assembly, string expected)
	{
		using FileStream inputStream = File.OpenRead(AnchorChain.BetaAssemblyPolicy.OriginalLocation(assembly));
		using SHA256 sHA = SHA256.Create();
		return BitConverter.ToString(sHA.ComputeHash(inputStream)).Replace("-", string.Empty).ToLowerInvariant() == expected;
	}

	internal static void EnsureBound()
	{
		if (!NativeCombatSurface.Ready)
		{
			return;
		}
		double num = (double)Stopwatch.GetTimestamp() / (double)Stopwatch.Frequency;
		if (num < retry)
		{
			return;
		}
		retry = num + 1.0;
		Assembly[] assemblies = AppDomain.CurrentDomain.GetAssemblies();
		foreach (Assembly assembly in assemblies)
		{
			if (!BindScreen(assembly))
			{
				continue;
			}
			if (!formationBound && !formationRejected && assembly.GetType("SeaPowerSquadPanel.SquadManagerController", throwOnError: false) != null)
			{
				if (!HashMatches(assembly, "6230e8e78e2ba7ba222241d0c3dcc881d2507ebeeb4eab24b6401cc9144283dd"))
				{
					formationRejected = true;
					Api.Log("formation pop-out bridge inactive for an uninspected Group Manager DLL");
					continue;
				}
				Type type = Api.Type(assembly, "SeaPowerSquadPanel.SquadManagerController");
				Api.Hooks(Api.Method(type, "Tick", typeof(void), typeof(MainGameViewModel)), typeof(PopOutBridge), "BeforeFormation", "AfterFormation", "io.github.sest-hobby.formation-popout", "FinishFormation");
				Api.Postfix(Api.Method(typeof(MainGameViewModel), "get_RootControl", typeof(FrameworkElement)), typeof(PopOutBridge), "RootForFormation", "io.github.sest-hobby.formation-popout");
				Type type2 = Api.Type(assembly, "SeaPowerSquadPanel.SquadBarController");
				Api.Hooks(Api.Method(type2, "UseState", typeof(void), Api.Type(assembly, "SeaPowerSquadPanel.SquadWindowState")), typeof(PopOutBridge), "StateForFormation", null, "io.github.sest-hobby.formation-popout");
				formationBound = true;
				Api.Log("Group Manager 0.2.17 pop-out bridge installed: original controls, scoped host lookup, separate placement");
			}
		}
		try
		{
			ContactWindowBridge.EnsureBound();
		}
		catch (Exception error)
		{
			ContactWindowBridge.Disable(error);
		}
	}

	// Binds PopOutScreen from one assembly. False only for an uninspected
	// Pop-Out image (EnsureBound's former `continue`). A missing member leaves
	// the bridge unbound (Screen null) instead of half bound, then rethrows.
	private static bool BindScreen(Assembly assembly)
	{
		if (screenType != null || popRejected || assembly.GetType("SeaPowerPopOut.PopOutScreen", throwOnError: false) == null)
		{
			return true;
		}
		bool current = HashMatches(assembly, Pop123Hash);
		if (!current && !HashMatches(assembly, PopHash))
		{
			popRejected = true;
			Api.Log("pop-out bridge inactive for an uninspected Pop-Out DLL");
			return false;
		}
		try
		{
			screenType = assembly.GetType("SeaPowerPopOut.PopOutScreen");
			instance = screenType.GetProperty("Instance", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
			root = screenType.GetField("root", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
			host = screenType.GetField("host", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
			opening = Api.Method(screenType, "HostOpening", typeof(bool), typeof(WindowHost), typeof(object));
			decorate = Api.Method(screenType, "Decorate", typeof(void), typeof(Window));
			move = Api.Method(screenType, "Move", typeof(void), typeof(object), typeof(bool), typeof(bool));
			place = Api.Method(screenType, "Place", typeof(void), typeof(Window), typeof(string));
			openStandalone = Api.Method(screenType, "Open", typeof(bool));
			displayAvailable = screenType.GetProperty("DisplayAvailable", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
			trackedWindows = screenType.GetField("windows", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
			if (displayAvailable == null || displayAvailable.PropertyType != typeof(bool) || trackedWindows == null)
			{
				throw new MissingMemberException("captured standalone pop-out host");
			}
			Api.Hooks(Api.Method(screenType, "Remember", typeof(void), typeof(Window)), typeof(ContactWindowBridge), "BeforePopOutRemember", null, "io.github.sest-hobby.contacts-popout");
			if (instance == null || root == null || host == null)
			{
				throw new MissingMemberException("captured pop-out window host");
			}
			pop123 = current;
			Api.Log("native window bridge attached to the inspected Pop-Out Windows image");
		}
		catch
		{
			screenType = null;
			instance = null;
			popRejected = true;
			throw;
		}
		return true;
	}

	// The Coordinated Strike pop-out needs only Pop-Out's monitor surface, not
	// the native cost surface, so it binds without NativeCombatSurface.Ready.
	// Formation and Contacts keep EnsureBound and its existing gate. Only the
	// inspected 1.2.3 image is used: its screenDisplay, hint and keep members
	// were not reviewed in 1.1.3.
	internal static bool EnsureScreenBound()
	{
		if (strikeSurface || strikeSurfaceRejected || popRejected || NoesisTeardown.InProgress)
		{
			return strikeSurface;
		}
		double num = (double)Stopwatch.GetTimestamp() / (double)Stopwatch.Frequency;
		if (num < screenRetry)
		{
			return false;
		}
		screenRetry = num + 2.0;
		if (screenType == null)
		{
			foreach (Assembly assembly in AppDomain.CurrentDomain.GetAssemblies())
			{
				if (!BindScreen(assembly))
				{
					return false;
				}
			}
		}
		if (screenType == null)
		{
			return false;
		}
		if (!pop123)
		{
			strikeSurfaceRejected = true;
			Api.Log("Coordinated Strike pop-out needs Pop-Out Windows 1.2.3; the F8 panel stays on the main screen");
			return false;
		}
		screenDisplay = ScreenField("screenDisplay", typeof(int));
		hintField = ScreenField("hint", typeof(TextBlock));
		keepField = ScreenField("keep", typeof(List<UnityEngine.Rect>));
		strikeSurface = true;
		return true;
	}

	private static FieldInfo ScreenField(string name, Type type)
	{
		FieldInfo field = screenType.GetField(name, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
		if (field == null || field.FieldType != type)
		{
			throw new MissingFieldException(screenType.FullName, name);
		}
		return field;
	}

	internal static void HookStrikeSurface()
	{
		Api.Postfix(Api.Method(screenType, "CollectShape", typeof(void)), typeof(PopOutBridge), "AfterCollectShape", StrikePopOut.HarmonyId);
		Api.Postfix(Api.Method(screenType, "UpdateScreen", typeof(void), typeof(bool)), typeof(PopOutBridge), "AfterUpdateScreen", StrikePopOut.HarmonyId);
	}

	internal static void AfterCollectShape(object __instance)
	{
		try
		{
			if (keepField.GetValue(__instance) is List<UnityEngine.Rect> keep)
			{
				StrikePopOut.AddShape(keep);
			}
		}
		catch (Exception error)
		{
			StrikePopOut.Fail("strike pop-out see-through area", error);
		}
	}

	internal static void AfterUpdateScreen(object __instance)
	{
		try
		{
			if (StrikePopOut.OnPopMonitor && hintField.GetValue(__instance) is TextBlock textBlock)
			{
				textBlock.Visibility = Visibility.Collapsed;
			}
		}
		catch (Exception error)
		{
			StrikePopOut.Fail("strike pop-out monitor hint", error);
		}
	}

	internal static bool OpenStandalone()
	{
		object screen = Screen;
		return screen != null && openStandalone != null && (bool)openStandalone.Invoke(screen, null);
	}

	internal static void TrackStandalone(Window window, bool track)
	{
		object screen = Screen;
		if (screen == null || trackedWindows == null || window == null)
		{
			return;
		}
		if (!(trackedWindows.GetValue(screen) is IList list))
		{
			throw new MissingMemberException("captured pop-out tracking list");
		}
		if (track)
		{
			if (!list.Contains(window))
			{
				list.Add(window);
			}
		}
		else
		{
			list.Remove(window);
		}
	}

	internal static bool Contains(object model)
	{
		WindowHost windowHost = Host;
		return windowHost != null && windowHost.Windows.Contains(model);
	}

	internal static bool HostOpening(WindowHost home, object model)
	{
		EnsureBound();
		object screen = Screen;
		return screen == null || (bool)opening.Invoke(screen, new object[2] { home, model });
	}

	internal static void Remove(object model)
	{
		WindowHost windowHost = Host;
		if (windowHost != null)
		{
			windowHost.Windows.Remove(model);
		}
	}

	internal static void Decorate(Window window)
	{
		object screen = Screen;
		if (screen != null)
		{
			decorate.Invoke(screen, new object[1] { window });
		}
	}

	private static void Move(object model)
	{
		object screen = Screen;
		if (screen != null)
		{
			move.Invoke(screen, new object[3]
			{
				model,
				!Contains(model),
				true
			});
		}
	}

	internal static void BeforeFormation(MainGameViewModel __0, ref object __state)
	{
		__state = Tuple.Create(scopedMain, scopedRoot);
		if (!NoesisTeardown.InProgress && __0 != null && Contains(__0.FormationManager) && Root != null)
		{
			scopedMain = __0;
			scopedRoot = Root;
		}
	}

	internal static void RootForFormation(MainGameViewModel __instance, ref FrameworkElement __result)
	{
		if (object.ReferenceEquals(scopedMain, __instance) && scopedRoot != null)
		{
			__result = scopedRoot;
		}
	}

	internal static Exception FinishFormation(Exception __exception, object __state)
	{
		Tuple<MainGameViewModel, FrameworkElement> tuple = __state as Tuple<MainGameViewModel, FrameworkElement>;
		scopedMain = tuple?.Item1;
		scopedRoot = tuple?.Item2;
		return __exception;
	}

	internal static void StateForFormation(object __instance, ref object __0)
	{
		Window window = (Window)__instance.GetType().GetField("_window", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static).GetValue(__instance);
		if (Contains(window.DataContext) && __0 != null)
		{
			Type type = __0.GetType();
			string text = (string)type.GetMethod("Serialize", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static).Invoke(__0, null);
			__0 = type.GetMethod("Parse", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static).Invoke(null, new object[1] { text });
		}
	}

	internal static void AfterFormation(object __instance)
	{
		try
		{
			if (Screen == null || NoesisTeardown.InProgress)
			{
				return;
			}
			object value = __instance.GetType().GetField("_bar", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static).GetValue(__instance);
			if (value == null)
			{
				return;
			}
			Window window = value.GetType().GetField("_window", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static).GetValue(value) as Window;
			if (window == null)
			{
				return;
			}
			StackPanel stackPanel = NativeCombatSurface.Walk(window).OfType<StackPanel>().FirstOrDefault((StackPanel p) => p.Name == "AirSquadTools");
			if (stackPanel == null)
			{
				return;
			}
			if (!forms.TryGetValue(window, out var value2))
			{
				value2 = new FormEntry();
				forms.Add(window, value2);
			}
			if (value2.Button == null || !value2.Button.IsDescendantOf(window))
			{
				value2.Button = (Button)GUI.ParseXaml("<Button xmlns='http://schemas.microsoft.com/winfx/2006/xaml/presentation' Name='SestFormationPopOut' Width='24' Height='20' Margin='0,0,3,0' FontSize='14' Focusable='False'/>");
				value2.Button.Click += delegate(object s, RoutedEventArgs e)
				{
					Move(window.DataContext);
					e.Handled = true;
				};
				stackPanel.Children.Insert(0, value2.Button);
			}
			bool flag = Contains(window.DataContext);
			value2.Button.Content = ((!flag) ? "↗" : "↙");
			value2.Button.ToolTip = ((!flag) ? "Pop out Group Manager" : "Return Group Manager to the game");
			if (flag && (!value2.Initialized || !object.ReferenceEquals(value2.Bar, value)))
			{
				object screen = Screen;
				if (screen != null)
				{
					place.Invoke(screen, new object[2]
					{
						window,
						window.DataContext.GetType().Name
					});
				}
				object value3 = value.GetType().GetField("_state", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static).GetValue(value);
				if (value3 != null)
				{
					value3.GetType().GetMethod("SetPosition", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static).Invoke(value3, new object[2] { window.X, window.Y });
					float num = ((!float.IsNaN(window.Width)) ? window.Width : window.ActualWidth);
					float num2 = ((!float.IsNaN(window.Height)) ? window.Height : 0f);
					value3.GetType().GetMethod("SetSize", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static).Invoke(value3, new object[3] { num, num2, 1f });
				}
				value2.Initialized = true;
			}
			value2.Bar = value;
		}
		catch (Exception error)
		{
			if (!formationErrorReported)
			{
				formationErrorReported = true;
				Api.LogFailure("formation pop-out control unavailable; original group controls retained", error);
			}
		}
	}
}
