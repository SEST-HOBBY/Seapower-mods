using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using Noesis;
using Noesis.Interactivity;
using SeaPower;
using SeapowerUI;
using SeapowerUI.ViewModels;

namespace Sest.RuntimeFixes {
internal static class NativeCombatSurface
{
	private static readonly CumulativeCombatCostsViewModel model = new CumulativeCombatCostsViewModel();

	private static FrameworkElement root;

	private static WindowHost home;

	private static Window window;

	private static ScrollViewer scroll;

	private static StackPanel summaryPanel;

	private static StackPanel detailPanel;

	private static int renderedRevision = -1;

	private static ResourceDictionary templates;

	private static bool shown;

	private static bool closing;

	private static bool wasLive;

	private static bool boundsLogged;

	private static string scope;

	private static string path;

	private static CostWindowState state;

	private static Action closed;

	private static double nextLayout;

	private static double nextSave;

	private static string lastSaved;

	private static PropertyInfo cameraPressed;

	private static FieldInfo uiInitialized;

	private static readonly UiStartupGate startup = new UiStartupGate();

	private const string Xaml = "<ResourceDictionary xmlns='http://schemas.microsoft.com/winfx/2006/xaml/presentation' xmlns:x='http://schemas.microsoft.com/winfx/2006/xaml' xmlns:local='clr-namespace:SeapowerUI' xmlns:sest='clr-namespace:Sest.RuntimeFixes;assembly=SEST.RuntimeFixes'>\n<DataTemplate DataType='{x:Type sest:CumulativeCombatCostsViewModel}'>\n<local:Window x:Name='SestCostWindow' Header='{Binding Title}' Width='570' Height='560' MinWidth='100' MinHeight='100' X='12' Y='170' AnchorRight='False' AnchorBottom='False' Draggable='True' CanResize='True' HorizontalAlignment='Left' VerticalAlignment='Top' HorizontalContentAlignment='Stretch' VerticalContentAlignment='Stretch' Background='#ED151D24'>\n<Grid Margin='10' Background='#ED151D24'><Grid.RowDefinitions><RowDefinition Height='Auto'/><RowDefinition Height='Auto'/><RowDefinition Height='*'/><RowDefinition Height='Auto'/></Grid.RowDefinitions>\n<TextBlock Text='{Binding Subtitle}' Foreground='#9BAEBB' FontSize='11' TextWrapping='Wrap' Margin='0,0,0,8'/>\n<StackPanel x:Name='SestCostSummary' Grid.Row='1' Margin='0,0,0,10'/>\n<ScrollViewer x:Name='SestCostScroll' Grid.Row='2' VerticalScrollBarVisibility='Auto' HorizontalScrollBarVisibility='Disabled' Background='Transparent' CanContentScroll='False'>\n<StackPanel x:Name='SestCostDetails' Margin='0,0,10,0'/></ScrollViewer>\n<TextBlock Grid.Row='3' Text='{Binding Notes}' Foreground='#A8B6C2' FontSize='11' TextWrapping='Wrap' Margin='0,10,0,0'/>\n</Grid></local:Window></DataTemplate></ResourceDictionary>";

	internal static bool Ready
	{
		get { return startup.Ready && !NoesisTeardown.InProgress; }
	}

	internal static void Bind()
	{
		using (FileStream inputStream = File.OpenRead(typeof(GUI).Assembly.Location))
		{
			using (SHA256 sHA = SHA256.Create())
			{
				if (BitConverter.ToString(sHA.ComputeHash(inputStream)).Replace("-", string.Empty).ToLowerInvariant() != "c4e2c37cd9162fe9e4d6426b646cdaa9a16ccbcd80e69261cc900a4386920d65")
				{
					throw new InvalidOperationException("uninspected Noesis UI assembly");
				}
			}
		}
		uiInitialized = typeof(GUI).GetField("_initialized", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		if (uiInitialized == null || !uiInitialized.IsStatic || uiInitialized.FieldType != typeof(bool))
		{
			throw new MissingFieldException("captured Noesis initialization flag");
		}
		Api.Log("native cost UI deferred until Noesis is initialized and a game view is attached");
	}

	internal static bool EnsureReady(bool live)
	{
		if (NoesisTeardown.InProgress || uiInitialized == null || !(bool)uiInitialized.GetValue(null))
		{
			return false;
		}
		if (startup.Ready)
		{
			return true;
		}
		FrameworkElement frameworkElement = Root(live);
		bool attachedView = frameworkElement != null && frameworkElement.IsLoaded && View.Find(frameworkElement) != null && Host(frameworkElement) != null;
		return startup.TryStart(initialized: true, attachedView, teardown: false, InitializeReady);
	}

	private static void InitializeReady()
	{
		GUI.RegisterType(typeof(CumulativeCombatCostsViewModel));
		templates = GUI.ParseXaml("<ResourceDictionary xmlns='http://schemas.microsoft.com/winfx/2006/xaml/presentation' xmlns:x='http://schemas.microsoft.com/winfx/2006/xaml' xmlns:local='clr-namespace:SeapowerUI' xmlns:sest='clr-namespace:Sest.RuntimeFixes;assembly=SEST.RuntimeFixes'>\n<DataTemplate DataType='{x:Type sest:CumulativeCombatCostsViewModel}'>\n<local:Window x:Name='SestCostWindow' Header='{Binding Title}' Width='570' Height='560' MinWidth='100' MinHeight='100' X='12' Y='170' AnchorRight='False' AnchorBottom='False' Draggable='True' CanResize='True' HorizontalAlignment='Left' VerticalAlignment='Top' HorizontalContentAlignment='Stretch' VerticalContentAlignment='Stretch' Background='#ED151D24'>\n<Grid Margin='10' Background='#ED151D24'><Grid.RowDefinitions><RowDefinition Height='Auto'/><RowDefinition Height='Auto'/><RowDefinition Height='*'/><RowDefinition Height='Auto'/></Grid.RowDefinitions>\n<TextBlock Text='{Binding Subtitle}' Foreground='#9BAEBB' FontSize='11' TextWrapping='Wrap' Margin='0,0,0,8'/>\n<StackPanel x:Name='SestCostSummary' Grid.Row='1' Margin='0,0,0,10'/>\n<ScrollViewer x:Name='SestCostScroll' Grid.Row='2' VerticalScrollBarVisibility='Auto' HorizontalScrollBarVisibility='Disabled' Background='Transparent' CanContentScroll='False'>\n<StackPanel x:Name='SestCostDetails' Margin='0,0,10,0'/></ScrollViewer>\n<TextBlock Grid.Row='3' Text='{Binding Notes}' Foreground='#A8B6C2' FontSize='11' TextWrapping='Wrap' Margin='0,10,0,0'/>\n</Grid></local:Window></DataTemplate></ResourceDictionary>") as ResourceDictionary;
		if (templates == null)
		{
			throw new InvalidOperationException("native cost-window template could not be parsed; original tracker retained");
		}
		Api.Hooks(Api.Method(Api.FindType("SeapowerUI.SceneEdit.Behaviours.MapDragger"), "MapZoom", typeof(void), typeof(object), typeof(MouseWheelEventArgs)), typeof(NativeCombatSurface), "BeforeMapWheel", null, "io.github.sest-hobby.cost-input");
		Type type = Api.FindType("SeaPower.CameraManager");
		cameraPressed = type.GetProperty("LeftMousePressed", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		if (cameraPressed == null || cameraPressed.PropertyType != typeof(bool))
		{
			throw new MissingMemberException("native camera mouse guard");
		}
		Api.Hooks(Api.Method(type, "OnLateUpdate", typeof(void)), typeof(NativeCombatSurface), "BeforeCamera", null, "io.github.sest-hobby.cost-input", "AfterCamera");
		Api.Log("native cost UI initialized after the game attached its Noesis view; map input guards installed");
	}

	private static void Register(FrameworkElement target)
	{
		if (target != null && !target.Resources.MergedDictionaries.Contains(templates))
		{
			target.Resources.MergedDictionaries.Add(templates);
		}
	}

	internal static IEnumerable<DependencyObject> Walk(DependencyObject start)
	{
		if (start == null)
		{
			yield break;
		}
		Queue<DependencyObject> queue = new Queue<DependencyObject>();
		queue.Enqueue(start);
		int count = 0;
		while (queue.Count > 0 && count++ < 20000)
		{
			DependencyObject current = queue.Dequeue();
			yield return current;
			int n = VisualTreeHelper.GetChildrenCount(current);
			for (int i = 0; i < n; i++)
			{
				queue.Enqueue(VisualTreeHelper.GetChild(current, i));
			}
		}
	}

	internal static WindowHost Host(DependencyObject target)
	{
		DependencyObject dependencyObject = target;
		while (dependencyObject != null)
		{
			BehaviorCollection behaviors = Interaction.GetBehaviors(dependencyObject);
			foreach (Behavior item in behaviors)
			{
				if (item is WindowHost)
				{
					return (WindowHost)item;
				}
			}
			dependencyObject = VisualTreeHelper.GetParent(dependencyObject);
		}
		return null;
	}

	private static FrameworkElement Root(bool live)
	{
		return live ? (Globals._mainGameViewModel == null ? null : Globals._mainGameViewModel.RootControl) : LinearCampaignView.Instance;
	}

	internal static void Tick(bool live, bool open, CampaignCosts.CostView report, string identity, Action onClosed, double now)
	{
		if (NoesisTeardown.InProgress)
		{
			Forget();
			return;
		}
		if (!Ready)
		{
			return;
		}
		PopOutBridge.EnsureBound();
		closed = onClosed;
		FrameworkElement target = Root(live);
		if (!object.ReferenceEquals(root, target) || wasLive != live)
		{
			Close();
			root = target;
			wasLive = live;
			home = root == null ? null : Host(root);
			path = System.IO.Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.UserProfile), "AppData", "LocalLow", "Triassic Games", "Sea Power", "SEST", live ? "combat-window-mission.txt" : "combat-window-campaign.txt");
			try
			{
				state = CostWindowState.Parse(File.Exists(path) ? File.ReadAllText(path) : null);
			}
			catch (Exception error)
			{
				state = new CostWindowState();
				Api.LogFailure("cost-window placement could not be read; defaults used", error);
			}
			lastSaved = state.Encode();
			nextLayout = (nextSave = 0.0);
			boundsLogged = false;
			Register(root);
		}
		Register(PopOutBridge.Root);
		if (!open || root == null || home == null)
		{
			Close();
			return;
		}
		if (scope != identity)
		{
			scope = identity;
			if (scroll != null)
			{
				scroll.ScrollToVerticalOffset(0f);
			}
		}
		model.Set(report, live);
		if (!shown)
		{
			if (PopOutBridge.HostOpening(home, model))
			{
				home.Windows.Add(model);
			}
			shown = true;
			nextLayout = 0.0;
			Api.Log("native cumulative-cost window opened in " + (live ? "mission" : "campaign") + "; draggable, resizable, native scrolling");
		}
		else if (!home.Windows.Contains(model) && !PopOutBridge.Contains(model))
		{
			shown = false;
			window = null;
			scroll = null;
			summaryPanel = (detailPanel = null);
			renderedRevision = -1;
			if (closed != null)
			{
				closed();
			}
			return;
		}
		if (now < nextLayout)
		{
			return;
		}
		nextLayout = now + 0.2;
		FrameworkElement host = PopOutBridge.Contains(model) ? PopOutBridge.Root : root;
		Window found = window != null && window.IsDescendantOf(host) ? window : Walk(host).OfType<Window>().FirstOrDefault((Window w) => object.ReferenceEquals(w.DataContext, model));
		if (found == null)
		{
			return;
		}
		if (!object.ReferenceEquals(window, found))
		{
			window = found;
			scroll = Walk(window).OfType<ScrollViewer>().FirstOrDefault((ScrollViewer s) => s.Name == "SestCostScroll");
			summaryPanel = Walk(window).OfType<StackPanel>().FirstOrDefault((StackPanel p) => p.Name == "SestCostSummary");
			detailPanel = Walk(window).OfType<StackPanel>().FirstOrDefault((StackPanel p) => p.Name == "SestCostDetails");
			if (summaryPanel == null || detailPanel == null)
			{
				throw new MissingMemberException("native cost report text panels");
			}
			renderedRevision = -1;
			window.PreviewMouseWheel += OnWheel;
			if (!PopOutBridge.Contains(model))
			{
				ApplyBounds(live, initial: true);
			}
			PopOutBridge.Decorate(window);
		}
		if (renderedRevision != model.Revision)
		{
			NativeCostTypography.Render(summaryPanel, model.SummaryRows);
			NativeCostTypography.Render(detailPanel, model.DetailRows);
			renderedRevision = model.Revision;
		}
		if (!PopOutBridge.Contains(model))
		{
			ApplyBounds(live, initial: false);
		}
		if (now >= nextSave && !PopOutBridge.Contains(model))
		{
			nextSave = now + 1.0;
			string text = state.Encode();
			if (text != lastSaved)
			{
				state.Positioned = true;
				state.Save(path);
				lastSaved = text;
			}
		}
	}

	private static void OnWheel(object sender, MouseWheelEventArgs e)
	{
		if (scroll != null)
		{
			scroll.ScrollToVerticalOffset(Math.Max(0f, Math.Min(scroll.ScrollableHeight, scroll.VerticalOffset - (float)e.Delta * 0.4f)));
		}
		e.Handled = true;
	}

	private static Rect Bounds(FrameworkElement element, FrameworkElement ancestor)
	{
		Rect result = new Rect(0f, 0f, element.ActualWidth, element.ActualHeight);
		result.Transform(element.TransformToAncestor(ancestor));
		return result;
	}

	private static bool BoundTo(ItemsControl items, object source, string name)
	{
		if (source != null && object.ReferenceEquals(items.ItemsSource, source))
		{
			return true;
		}
		Binding binding = BindingOperations.GetBinding(items, ItemsControl.ItemsSourceProperty);
		string text = binding == null || binding.Path == null ? null : binding.Path.Path;
		return text == name || (text != null && text.EndsWith("." + name, StringComparison.Ordinal));
	}

	internal static CostBounds MenuBounds(FrameworkElement host)
	{
		float num = 8f;
		float num2 = host.ActualHeight - 8f;
		FrameworkElement frameworkElement = host.FindName("CampaignTimelineRibbonScrollViewer") as FrameworkElement;
		if (frameworkElement == null)
		{
			frameworkElement = Walk(host).OfType<ScrollViewer>().FirstOrDefault((ScrollViewer s) => s.Name != null && s.Name.IndexOf("TimelineRibbon", StringComparison.OrdinalIgnoreCase) >= 0);
		}
		if (frameworkElement != null && frameworkElement.IsVisible && frameworkElement.ActualHeight > 0f)
		{
			num2 = Math.Min(num2, Bounds(frameworkElement, host).Top - 8f);
		}
		LinearCampaignMapViewModel linearCampaignMapViewModel = host.DataContext as LinearCampaignMapViewModel;
		if (linearCampaignMapViewModel != null)
		{
			foreach (ItemsControl item in Walk(host).OfType<ItemsControl>())
			{
				if (!BoundTo(item, linearCampaignMapViewModel.TaskForceManagerVisibleUnits, "TaskForceManagerVisibleUnits") && !BoundTo(item, linearCampaignMapViewModel.TaskForceManagerUnits, "TaskForceManagerUnits"))
				{
					continue;
				}
				FrameworkElement frameworkElement2 = item;
				DependencyObject parent = VisualTreeHelper.GetParent(item);
				while (parent != null && !object.ReferenceEquals(parent, host))
				{
					FrameworkElement frameworkElement3 = parent as FrameworkElement;
					if (frameworkElement3 != null && frameworkElement3.ActualHeight > 0f && frameworkElement3.ActualHeight < host.ActualHeight * 0.48f && frameworkElement3.ActualWidth > host.ActualWidth * 0.65f)
					{
						frameworkElement2 = frameworkElement3;
					}
					parent = VisualTreeHelper.GetParent(parent);
				}
				if (frameworkElement2.IsVisible && frameworkElement2.ActualHeight > 0f)
				{
					num = Math.Max(num, Bounds(frameworkElement2, host).Bottom + 8f);
				}
			}
		}
		if (!boundsLogged && num > 8f && frameworkElement != null && num2 - num > 100f)
		{
			boundsLogged = true;
			Api.Log("campaign cost window bounds measured between native bars: " + num + " to " + num2 + " of " + host.ActualHeight);
		}
		return new CostBounds(8f, num, Math.Max(9f, host.ActualWidth - 8f), Math.Max(num + 1f, num2));
	}

	private static void ApplyBounds(bool live, bool initial)
	{
		if (root.ActualWidth <= 0f || root.ActualHeight <= 0f)
		{
			return;
		}
		if (!initial)
		{
			state.X = window.X;
			state.Y = window.Y;
			state.Width = window.Width;
			state.Height = window.Height;
		}
		CostBounds area = live ? new CostBounds(8f, 8f, root.ActualWidth - 8f, root.ActualHeight - 8f) : MenuBounds(root);
		state.Fit(area, !live);
		window.MaxWidth = area.Width;
		window.MaxHeight = area.Height;
		window.Width = state.Width;
		window.Height = state.Height;
		window.X = state.X;
		window.Y = state.Y;
	}

	internal static bool IsMouseOver
	{
		get { return shown && window != null && window.IsVisible && window.IsMouseOver; }
	}

	internal static bool BeforeMapWheel(object __1)
	{
		if (!IsMouseOver)
		{
			return true;
		}
		((MouseWheelEventArgs)__1).Handled = true;
		return false;
	}

	internal static void BeforeCamera(object __instance, ref bool __state)
	{
		__state = IsMouseOver && (bool)cameraPressed.GetValue(__instance, null);
		if (__state)
		{
			cameraPressed.SetValue(__instance, false, null);
		}
	}

	internal static Exception AfterCamera(object __instance, bool __state, Exception __exception)
	{
		if (__state)
		{
			cameraPressed.SetValue(__instance, true, null);
		}
		return __exception;
	}

	internal static void Close()
	{
		if (NoesisTeardown.InProgress)
		{
			Forget();
			return;
		}
		if (closing || !shown)
		{
			return;
		}
		closing = true;
		try
		{
			if (window != null)
			{
				window.PreviewMouseWheel -= OnWheel;
			}
			if (home != null)
			{
				home.Windows.Remove(model);
			}
			PopOutBridge.Remove(model);
			shown = false;
			window = null;
			scroll = null;
			summaryPanel = (detailPanel = null);
			renderedRevision = -1;
		}
		finally
		{
			closing = false;
		}
	}

	private static void Forget()
	{
		shown = false;
		window = null;
		scroll = null;
		home = null;
		root = null;
		summaryPanel = (detailPanel = null);
		renderedRevision = -1;
	}
}

}
