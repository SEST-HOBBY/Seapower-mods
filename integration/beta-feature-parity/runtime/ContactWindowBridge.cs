using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Security.Cryptography;
using Noesis;
using SeaPower;
using SeapowerUI;
using SeapowerUI.ViewModels;

namespace Sest.RuntimeFixes;

internal static class ContactWindowBridge
{
	private sealed class Entry
	{
		internal object Owner;

		internal Window Window;

		internal Panel Home;

		internal bool HomeIsGamePanel;

		internal bool Detached;

		internal bool Moving;

		internal bool InitialChoiceApplied;

		internal Button Button;

		internal CostWindowState Main;

		internal ContactPopOutState State;

		internal string Path;

		internal string LastSaved;
	}

	private const string ContactHash = "a1b8b450df0933df61984651fe2b19138acd605aa4b526bbfc23565d8295015e";

	private static bool bound;

	private static bool rejected;

	private static bool reported;

	private static FieldInfo windowField;

	private static FieldInfo tabField;

	private static FieldInfo panelField;

	private static FieldInfo inPanelField;

	private static FieldInfo mainRootField;

	private static MethodInfo saveGeometry;

	private static MethodInfo findGamePanel;

	private static readonly ConditionalWeakTable<object, Entry> entries = new ConditionalWeakTable<object, Entry>();

	private static readonly ConditionalWeakTable<Window, Entry> ownedWindows = new ConditionalWeakTable<Window, Entry>();

	private static FrameworkElement MainRoot
	{
		get
		{
			MainGameViewModel mainGameViewModel = Globals._mainGameViewModel;
			return (!(mainGameViewModel == null)) ? (mainRootField.GetValue(mainGameViewModel) as FrameworkElement) : null;
		}
	}

	internal static void Disable(Exception error)
	{
		rejected = true;
		Warn("Contacts bridge unavailable; original mod retained", error);
	}

	internal static void EnsureBound()
	{
		if (bound || rejected || !NativeCombatSurface.Ready)
		{
			return;
		}
		Assembly[] assemblies = AppDomain.CurrentDomain.GetAssemblies();
		foreach (Assembly assembly in assemblies)
		{
			if (assembly.GetType("ContactLog.NativeWindow", throwOnError: false) == null)
			{
				continue;
			}
			using (FileStream inputStream = File.OpenRead(assembly.Location))
			{
				using SHA256 sHA = SHA256.Create();
				if (BitConverter.ToString(sHA.ComputeHash(inputStream)).Replace("-", string.Empty).ToLowerInvariant() != "a1b8b450df0933df61984651fe2b19138acd605aa4b526bbfc23565d8295015e")
				{
					rejected = true;
					Api.Log("Contacts bridge inactive for an uninspected Contact Log DLL");
					break;
				}
			}
			Type type = Api.Type(assembly, "ContactLog.NativeWindow");
			windowField = RequireField(type, "_window", typeof(object));
			tabField = RequireField(type, "_tabContactsBtn", typeof(object));
			panelField = RequireField(type, "_panel", typeof(object));
			inPanelField = RequireField(type, "_isInPanel", typeof(bool));
			mainRootField = RequireField(typeof(MainGameViewModel), "<RootControl>k__BackingField", typeof(FrameworkElement));
			saveGeometry = Api.Method(type, "SaveGeometry", typeof(void));
			findGamePanel = Api.Method(type, "FindGamePanel", typeof(object));
			Api.Hooks(Api.Method(type, "EnsureWindow", typeof(bool), typeof(float)), typeof(ContactWindowBridge), "BeforeMainLookup", null, "io.github.sest-hobby.contacts-popout", "FinishMainLookup");
			Api.Hooks(Api.Method(Api.Type(assembly, "ContactLog.NoesisBar"), "Step", typeof(void), typeof(float)), typeof(ContactWindowBridge), "BeforeMainLookup", null, "io.github.sest-hobby.contacts-popout", "FinishMainLookup");
			Api.Hooks(Api.Method(Api.Type(assembly, "ContactLog.NoesisApi"), "Roots", typeof(List<object>)), typeof(ContactWindowBridge), "RootsForHost", null, "io.github.sest-hobby.contacts-popout");
			Api.Postfix(Api.Method(type, "Tick", typeof(void), typeof(bool)), typeof(ContactWindowBridge), "AfterTick", "io.github.sest-hobby.contacts-popout");
			Api.Hooks(saveGeometry, typeof(ContactWindowBridge), "BeforeSaveGeometry", null, "io.github.sest-hobby.contacts-popout");
			MethodInfo[] array = new MethodInfo[3]
			{
				Api.Method(type, "UpdateStacking", typeof(void)),
				Api.Method(type, "ApplyStacking", typeof(void), typeof(string)),
				Api.Method(type, "FocusPanelChild", typeof(void), typeof(object), typeof(string))
			};
			foreach (MethodInfo target in array)
			{
				Api.Hooks(target, typeof(ContactWindowBridge), "BeforeStacking", null, "io.github.sest-hobby.contacts-popout");
			}
			Api.Hooks(Api.Method(type, "Reset", typeof(void)), typeof(ContactWindowBridge), "BeforeReset", null, "io.github.sest-hobby.contacts-popout");
			bound = true;
			Api.Log("Contact Log 1.0.1 bridge installed: main-view host lookup, shared Contacts/Rules pop-out and return, separate placement");
			break;
		}
	}

	private static FieldInfo RequireField(Type owner, string name, Type expected)
	{
		FieldInfo field = owner.GetField(name, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		if (field == null || field.FieldType != expected)
		{
			throw new MissingFieldException(owner.FullName, name);
		}
		return field;
	}

	internal static void BeforeMainLookup(ref int __state)
	{
		__state = ContactHostScope.Begin();
	}

	internal static Exception FinishMainLookup(Exception __exception, int __state)
	{
		ContactHostScope.End(__state);
		return __exception;
	}

	internal static bool RootsForHost(ref List<object> __result)
	{
		if (!ContactHostScope.Active)
		{
			return true;
		}
		__result = new List<object>();
		if (NoesisTeardown.InProgress)
		{
			return false;
		}
		FrameworkElement mainRoot = MainRoot;
		if (mainRoot != null)
		{
			__result.Add(mainRoot);
		}
		return false;
	}

	private static Panel MainPanel(object owner, out bool gamePanel)
	{
		int previous = ContactHostScope.Begin();
		object obj;
		try
		{
			obj = findGamePanel.Invoke(owner, null);
		}
		finally
		{
			ContactHostScope.End(previous);
		}
		Panel panel = obj as Panel;
		FrameworkElement mainRoot = MainRoot;
		gamePanel = panel != null && mainRoot != null && panel.IsDescendantOf(mainRoot);
		if (gamePanel)
		{
			return panel;
		}
		if (mainRoot == null)
		{
			return null;
		}
		return (mainRoot.FindName("OverlayCanvasNew") as Panel) ?? NativeCombatSurface.Walk(mainRoot).OfType<Panel>().FirstOrDefault((Panel p) => p.Name == "OverlayCanvasNew");
	}

	internal static void AfterTick(object __instance, bool __0)
	{
		if (!NativeCombatSurface.Ready || NoesisTeardown.InProgress)
		{
			return;
		}
		try
		{
			Window window = windowField.GetValue(__instance) as Window;
			if (window == null)
			{
				return;
			}
			if (!entries.TryGetValue(__instance, out var value) || !object.ReferenceEquals(value.Window, window))
			{
				if (value != null)
				{
					PopOutBridge.TrackStandalone(value.Window, track: false);
					ownedWindows.Remove(value.Window);
				}
				entries.Remove(__instance);
				Entry entry = new Entry();
				entry.Owner = __instance;
				entry.Window = window;
				value = entry;
				FrameworkElement mainRoot = MainRoot;
				Panel panel = VisualTreeHelper.GetParent(window) as Panel;
				if (panel != null && mainRoot != null && panel.IsDescendantOf(mainRoot))
				{
					value.Home = panel;
					value.HomeIsGamePanel = (bool)inPanelField.GetValue(__instance);
				}
				else
				{
					value.Home = MainPanel(__instance, out value.HomeIsGamePanel);
				}
				if (value.Home == null)
				{
					return;
				}
				value.Main = Snapshot(window);
				value.Path = System.IO.Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.UserProfile), "AppData", "LocalLow", "Triassic Games", "Sea Power", "SEST", "contacts-popout-v1.txt");
				try
				{
					value.State = ContactPopOutState.Parse((!File.Exists(value.Path)) ? null : File.ReadAllText(value.Path));
				}
				catch (Exception error)
				{
					value.State = new ContactPopOutState
					{
						Writable = false
					};
					Warn("Contacts saved screen choice could not be read", error);
				}
				value.LastSaved = value.State.Encode();
				entries.Add(__instance, value);
				ownedWindows.Add(window, value);
			}
			DependencyObject dependencyObject = tabField.GetValue(__instance) as DependencyObject;
			StackPanel stackPanel = ((!(dependencyObject == null)) ? (VisualTreeHelper.GetParent(dependencyObject) as StackPanel) : null);
			if (stackPanel != null && (value.Button == null || !value.Button.IsDescendantOf(window)))
			{
				value.Button = new Button
				{
					Name = "SestContactsPopOut",
					Width = 114f,
					Height = 24f,
					Margin = new Thickness(8f, 0f, 0f, 0f),
					FontSize = 12f,
					Focusable = false
				};
				Entry captured = value;
				value.Button.Click += delegate(object sender, RoutedEventArgs args)
				{
					try
					{
						Move(captured, !captured.Detached);
					}
					catch (Exception error3)
					{
						Warn("Contacts screen switch failed; prior host retained", error3);
					}
					args.Handled = true;
				};
				stackPanel.Children.Add(value.Button);
			}
			if (__0 && !value.InitialChoiceApplied)
			{
				if (VisualTreeHelper.GetParent(window) != value.Home)
				{
					Move(value, detached: false);
				}
				if (value.State.Detached && PopOutBridge.CanOpenStandalone)
				{
					Move(value, detached: true);
				}
				value.InitialChoiceApplied = true;
			}
			if (value.Button != null)
			{
				bool flag = value.Detached || PopOutBridge.CanOpenStandalone;
				value.Button.Content = ((!value.Detached) ? "Pop out" : "Return to game");
				value.Button.IsEnabled = flag && !window.Maximized;
				value.Button.ToolTip = (window.Maximized ? "Restore the window from maximized size before changing screens" : ((!flag) ? "Pop-Out Windows needs an available second monitor" : ((!value.Detached) ? "Move Contacts and Classification Rules to the Pop-Out monitor" : "Return Contacts and Classification Rules to the main game screen")));
			}
		}
		catch (Exception error2)
		{
			Warn("Contacts pop-out control unavailable; original content retained", error2);
		}
	}

	private static CostWindowState Snapshot(Window window)
	{
		float num = ((!float.IsNaN(window.Width)) ? window.Width : window.ActualWidth);
		float num2 = ((!float.IsNaN(window.Height)) ? window.Height : window.ActualHeight);
		CostWindowState costWindowState = new CostWindowState();
		costWindowState.X = ((!float.IsNaN(window.X)) ? Math.Max(0f, window.X) : 0f);
		costWindowState.Y = ((!float.IsNaN(window.Y)) ? Math.Max(0f, window.Y) : 0f);
		costWindowState.Width = ((!(num >= 100f)) ? 1250f : num);
		costWindowState.Height = ((!(num2 >= 100f)) ? 426f : num2);
		costWindowState.Positioned = true;
		return costWindowState;
	}

	private static void Apply(Window window, CostWindowState placement, FrameworkElement root)
	{
		if (root.ActualWidth > 0f && root.ActualHeight > 0f)
		{
			placement.Fit(new CostBounds(8f, 8f, root.ActualWidth - 8f, root.ActualHeight - 8f), menu: false);
		}
		window.Width = placement.Width;
		window.Height = placement.Height;
		window.X = placement.X;
		window.Y = placement.Y;
	}

	private static void Save(Entry entry)
	{
		string text = entry.State.Encode();
		if (!(text == entry.LastSaved))
		{
			entry.State.Save(entry.Path);
			entry.LastSaved = text;
		}
	}

	private static void Move(Entry entry, bool detached)
	{
		if (entry.Moving || entry.Window.Maximized || NoesisTeardown.InProgress)
		{
			return;
		}
		Panel panel = entry.Home;
		FrameworkElement frameworkElement = MainRoot;
		if (detached)
		{
			if (!PopOutBridge.OpenStandalone())
			{
				return;
			}
			frameworkElement = PopOutBridge.Root;
			panel = frameworkElement as Panel;
		}
		if (panel == null || frameworkElement == null)
		{
			return;
		}
		Panel panel2 = VisualTreeHelper.GetParent(entry.Window) as Panel;
		if (panel2 == null || (object.ReferenceEquals(panel2, panel) && entry.Detached == detached))
		{
			return;
		}
		bool detached2 = entry.Detached;
		CostWindowState costWindowState = Snapshot(entry.Window);
		if (!detached2 && object.ReferenceEquals(panel2, entry.Home))
		{
			saveGeometry.Invoke(entry.Owner, null);
			entry.Main = costWindowState;
		}
		else
		{
			entry.State.Placement = costWindowState;
		}
		object value = panelField.GetValue(entry.Owner);
		bool flag = (bool)inPanelField.GetValue(entry.Owner);
		bool detached3 = entry.State.Detached;
		entry.Moving = true;
		try
		{
			panel2.Children.Remove(entry.Window);
			panel.Children.Add(entry.Window);
			entry.Detached = detached;
			panelField.SetValue(entry.Owner, entry.Home);
			inPanelField.SetValue(entry.Owner, entry.HomeIsGamePanel);
			Apply(entry.Window, (!detached) ? entry.Main : entry.State.Placement, frameworkElement);
			PopOutBridge.TrackStandalone(entry.Window, detached);
			entry.State.Detached = detached;
			Save(entry);
			Api.Log("Contacts and Classification Rules moved to " + ((!detached) ? "the main game screen" : "the Pop-Out monitor"));
		}
		catch
		{
			Panel panel3 = VisualTreeHelper.GetParent(entry.Window) as Panel;
			if (panel3 != null)
			{
				panel3.Children.Remove(entry.Window);
			}
			panel2.Children.Add(entry.Window);
			entry.Detached = detached2;
			panelField.SetValue(entry.Owner, value);
			inPanelField.SetValue(entry.Owner, flag);
			entry.State.Detached = detached3;
			entry.Window.X = costWindowState.X;
			entry.Window.Y = costWindowState.Y;
			entry.Window.Width = costWindowState.Width;
			entry.Window.Height = costWindowState.Height;
			PopOutBridge.TrackStandalone(entry.Window, detached2);
			throw;
		}
		finally
		{
			entry.Moving = false;
		}
	}

	internal static bool BeforeStacking(object __instance)
	{
		if (NoesisTeardown.InProgress)
		{
			return false;
		}
		Entry value;
		return !entries.TryGetValue(__instance, out value) || (!value.Detached && !value.Moving);
	}

	internal static bool BeforeSaveGeometry(object __instance)
	{
		if (NoesisTeardown.InProgress)
		{
			return false;
		}
		if (!entries.TryGetValue(__instance, out var value) || (!value.Detached && !value.Moving))
		{
			return true;
		}
		if (value.Detached && !value.Moving)
		{
			value.State.Placement = Snapshot(value.Window);
			Save(value);
		}
		return false;
	}

	internal static bool BeforePopOutRemember(Window window)
	{
		Entry value;
		return window == null || !ownedWindows.TryGetValue(window, out value);
	}

	internal static void BeforeReset(object __instance)
	{
		if (!entries.TryGetValue(__instance, out var value))
		{
			return;
		}
		try
		{
			if (!NoesisTeardown.InProgress)
			{
				if (value.Detached)
				{
					value.State.Placement = Snapshot(value.Window);
					Save(value);
				}
				PopOutBridge.TrackStandalone(value.Window, track: false);
				Panel panel = VisualTreeHelper.GetParent(value.Window) as Panel;
				if (panel != null)
				{
					panel.Children.Remove(value.Window);
				}
			}
		}
		catch (Exception error)
		{
			Warn("Contacts detached-host cleanup unavailable", error);
		}
		finally
		{
			entries.Remove(__instance);
			ownedWindows.Remove(value.Window);
		}
	}

	private static void Warn(string label, Exception error)
	{
		if (!reported)
		{
			reported = true;
			Api.LogFailure(label, error);
		}
	}
}
