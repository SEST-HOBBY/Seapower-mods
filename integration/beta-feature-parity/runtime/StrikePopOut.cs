using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using UnityEngine;

namespace Sest.RuntimeFixes;

// Coordinated Strike Tool 1.3.1 (093b8ad6) draws its F8 panel with IMGUI:
// StrikePanel.OnGUI calls GUILayout.Window(0x5EA90, _window, DrawWindow, ...).
// Pop-Out Windows 1.4.1 (c241a0d6) moves only Noesis SeapowerUI.Window view
// models between WindowHosts and has no IMGUI path, so its own Move/Decorate
// cannot carry this panel. SEST therefore uses Pop-Out only for its monitor
// surface (PopOutScreen.Open activates the display, claims the mouse there and
// shapes the see-through window through ScreenCutOut.Collect) and lets the author's own OnGUI run in that
// display's IMGUI pass, chosen by Event.displayIndex. Plan, timing, selection,
// salvo and launch logic stay authored. The author's main-screen position
// stays in PlayerPrefs; SEST remembers a separate pop-out position.
internal static class StrikePopOut
{
	internal const string HarmonyId = "io.github.sest-hobby.strike-popout";

	// The author's exact title text (OnGUI IL_013d/IL_0144) plus KeyName(_toggleKey).
	internal const string Title = "COORDINATED STRIKE   ·   ";

	internal const string LockedTitle = "COORDINATED STRIKE   ·   LOCKED   ·   ";

	private const int ConfirmFrames = 120;

	private const double ConfirmSeconds = 2.0;

	private static FieldInfo windowField, shownField, visibleField, prefsField, stylesField, planField, keyField, smallField, titleStyleField, focusedField;

	private static MethodInfo px, inMission, suppressed, capture, locked, keyName, releaseFocus;

	private static bool hooked, stopped, available, popped, pending, unsupported, autoTried, requested, shown, open, buttonEnabled, sawRepaint, sawClick, probed;

	private static int display = -1, pendingFrame, pressFrame, clickFrame = -10, misses, openFrame;

	private static double next, pendingAt, openAt;

	private static Vector2 home;

	private static Rect lastArea;

	private static object panel, titleStyles;

	private static string path, titleText, lastSaved;

	private static float titleWidth;

	private static StrikePopOutState state = new StrikePopOutState();

	private static double Now => (double)System.Diagnostics.Stopwatch.GetTimestamp() / System.Diagnostics.Stopwatch.Frequency;

	internal static bool OnPopMonitor => !stopped && popped && shown;

	// Driven from CoordinatedStrikeRefinements.Poll (GameMain.Update postfix),
	// so it needs neither the Combat Cost Tracker nor NativeCombatSurface.Ready.
	// Nothing is hooked until Pop-Out Windows 1.4.1 itself has been bound.
	internal static void Poll(Type panelType)
	{
		if (hooked || stopped || Now < next)
		{
			return;
		}
		next = Now + 2.0;
		try
		{
			if (!PopOutBridge.EnsureScreenBound())
			{
				return;
			}
			Bind(panelType.Assembly);
			Api.Postfix(Api.Method(panelType, "Update", typeof(void)), typeof(StrikePopOut), "AfterUpdate", HarmonyId);
			Api.Hooks(Api.Method(panelType, "OnGUI", typeof(void)), typeof(StrikePopOut), "BeforeGUI", "AfterGUI", HarmonyId);
			Api.Hooks(Api.Method(panelType, "DrawWindow", typeof(void), typeof(int)), typeof(StrikePopOut), "BeforeWindow", null, HarmonyId);
			Api.Hooks(capture, typeof(StrikePopOut), "BeforeCapture", null, HarmonyId);
			Api.Hooks(Api.Method(panelType, "SavePrefs", typeof(void)), typeof(StrikePopOut), "BeforeSave", "AfterSave", HarmonyId);
			PopOutBridge.HookStrikeSurface();
			path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "AppData", "LocalLow", "Triassic Games", "Sea Power", "SEST", "strike-popout-v1.txt");
			try
			{
				state = StrikePopOutState.Parse(File.Exists(path) ? File.ReadAllText(path) : null);
			}
			catch (Exception error)
			{
				state = new StrikePopOutState { Writable = false };
				Api.LogFailure("strike pop-out placement could not be read; defaults used", error);
			}
			lastSaved = state.Encode();
			hooked = true;
			Api.Log("Coordinated Strike pop-out ready: 'Pop out' in the F8 title bar moves the author's panel to the Pop-Out Windows monitor; plan and launch logic unchanged");
		}
		catch (Exception error2)
		{
			stopped = true;
			Api.LogFailure("strike pop-out unavailable; author window retained", error2);
		}
	}

	internal static void Bind(Assembly assembly)
	{
		Type panelType = Api.Type(assembly, "CoordinatedStrikeTool.StrikePanel");
		Type styles = Api.Type(assembly, "CoordinatedStrikeTool.PanelStyles");
		Type data = Api.Type(assembly, "CoordinatedStrikeTool.GameData");
		Type plan = Api.Type(assembly, "CoordinatedStrikeTool.StrikePlan");
		windowField = Field(panelType, "_window", typeof(Rect));
		shownField = Field(panelType, "_shown", typeof(Rect));
		visibleField = Field(panelType, "_visible", typeof(bool));
		prefsField = Field(panelType, "_prefsLoaded", typeof(bool));
		stylesField = Field(panelType, "_s", styles);
		planField = Field(panelType, "_plan", plan);
		keyField = Field(panelType, "_toggleKey", typeof(KeyCode));
		focusedField = Field(panelType, "_fieldFocused", typeof(bool));
		smallField = Field(styles, "Small", typeof(GUIStyle));
		titleStyleField = Field(styles, "Window", typeof(GUIStyle));
		px = Api.Method(styles, "Px", typeof(int), typeof(float));
		inMission = Api.Method(data, "get_InMission", typeof(bool));
		suppressed = Api.Method(data, "get_UiSuppressed", typeof(bool));
		locked = Api.Method(plan, "get_IsLocked", typeof(bool));
		keyName = Api.Method(panelType, "KeyName", typeof(string), typeof(KeyCode));
		capture = Api.Method(panelType, "SetMouseCapture", typeof(void), typeof(bool));
		releaseFocus = Api.Method(panelType, "ReleaseFieldFocus", typeof(void));
		foreach (string name in new[] { "Update", "OnGUI", "SavePrefs" })
		{
			Api.Method(panelType, name, typeof(void));
		}
		Api.Method(panelType, "DrawWindow", typeof(void), typeof(int));
		if (!inMission.IsStatic || !suppressed.IsStatic || !keyName.IsStatic || px.IsStatic || capture.IsStatic || releaseFocus.IsStatic)
		{
			throw new MissingMethodException("inspected strike-panel pop-out members");
		}
	}

	private static FieldInfo Field(Type owner, string name, Type type)
	{
		FieldInfo field = owner.GetField(name, Api.All);
		if (field == null || field.IsStatic || field.FieldType != type)
		{
			throw new MissingFieldException(owner.FullName, name);
		}
		return field;
	}

	// Which IMGUI passes run the author's OnGUI. Docked: unchanged, except that
	// the panel is not drawn or clicked on Pop-Out's monitor while that monitor
	// is open (keyboard and command events tagged with that monitor still run,
	// as they do today, in case the OS focus sits on its window). Popped
	// and shown: every pass on the Pop-Out monitor; elsewhere only keyboard and
	// command events and the Layout pass Unity runs before each of them, so
	// typing into the author's fields still works while drawing and clicks on
	// the main screen are skipped. Popped but hidden (F8): the author's hidden
	// path (alert banner, capture release) stays on the main screen.
	internal static bool Route(bool popped, bool shown, bool open, int display, int index, EventType type, bool keyed)
	{
		if (display <= 0)
		{
			return true;
		}
		if (!popped)
		{
			return !open || index != display || keyed;
		}
		if (!shown)
		{
			return index != display;
		}
		if (index == display)
		{
			return true;
		}
		return keyed && (type == EventType.Layout || type == EventType.KeyDown || type == EventType.KeyUp || type == EventType.ValidateCommand || type == EventType.ExecuteCommand);
	}

	internal static bool BeforeGUI(object __instance)
	{
		if (stopped || !available)
		{
			return true;
		}
		Event current = Event.current;
		if (current == null)
		{
			return true;
		}
		int index = current.displayIndex;
		if (display > 0 && index == display)
		{
			EventType raw = current.rawType;
			if (raw == EventType.Repaint)
			{
				sawRepaint = true;
			}
			else if (raw == EventType.MouseDown)
			{
				sawClick = true;
				clickFrame = Time.frameCount;
			}
			// The author releases a focused field when a button goes down
			// outside _window, judged by this pass's Event.mousePosition (OnGUI
			// IL_00a1-IL_00da). While popped that position belongs to the
			// Pop-Out monitor, so a click on the main screen could leave typing
			// captured. Apply the same release here, inside this display's pass,
			// from the same pointer test as BeforeCapture.
			if (popped && shown && (Input.GetMouseButtonDown(0) || Input.GetMouseButtonDown(1)) && (bool)focusedField.GetValue(__instance) && PointerElsewhere(__instance))
			{
				try
				{
					releaseFocus.Invoke(__instance, null);
				}
				catch (Exception error)
				{
					Fail("strike pop-out field focus", error);
					return true;
				}
			}
		}
		bool keyed = current.isKey || current.keyCode != KeyCode.None || current.character != '\0' || !string.IsNullOrEmpty(current.commandName);
		return Route(popped, shown, open, display, index, current.type, keyed);
	}

	// The author clamps _window to Screen.width/height (OnGUI IL_0281-IL_0302);
	// on the Pop-Out monitor the same margins are applied to that display.
	internal static void AfterGUI(object __instance)
	{
		if (stopped || !popped || !shown)
		{
			return;
		}
		Event current = Event.current;
		if (current == null || current.displayIndex != display || display >= Display.displays.Length)
		{
			return;
		}
		try
		{
			object s = stylesField.GetValue(__instance);
			if (s == null)
			{
				return;
			}
			Display monitor = Display.displays[display];
			Rect window = (Rect)windowField.GetValue(__instance);
			float edge = Px(s, 120f);
			Rect fitted = new Rect(Mathf.Clamp(window.x, edge - window.width, monitor.renderingWidth - edge), Mathf.Clamp(window.y, 0f, monitor.renderingHeight - Px(s, 40f)), window.width, window.height);
			if (fitted.x != window.x || fitted.y != window.y)
			{
				windowField.SetValue(__instance, fitted);
			}
		}
		catch (Exception error)
		{
			Fail("strike pop-out placement", error);
		}
	}

	// Drawn first in the author's window function, in window-local coordinates
	// at the right end of the title strip (the Px(34) top padding of
	// PanelStyles.Window, where only the left-aligned title is painted). The
	// author's GUI.DragWindow() runs last, so this button keeps its click and
	// the rest of the strip still drags. GUI, not GUILayout: the author's
	// measured content size (_contentSizes) is unchanged.
	internal static void BeforeWindow(object __instance)
	{
		if (stopped || !available || unsupported)
		{
			return;
		}
		bool enabled = GUI.enabled;
		try
		{
			object s = stylesField.GetValue(__instance);
			if (s == null)
			{
				return;
			}
			GUIContent label = new GUIContent(popped ? "Return" : "Pop out");
			GUIStyle style = (GUIStyle)smallField.GetValue(s);
			float width = style.CalcSize(label).x;
			float pad = Px(s, 14f);
			Rect window = (Rect)windowField.GetValue(__instance);
			if (window.width - TitleWidth(__instance, s) < width + Px(s, 8f))
			{
				return;
			}
			GUI.enabled = enabled && buttonEnabled;
			if (GUI.Button(new Rect(window.width - pad - width, Px(s, 5f), width, Px(s, 24f)), label, style))
			{
				requested = true;
			}
		}
		catch (Exception error)
		{
			Fail("strike pop-out button", error);
		}
		finally
		{
			GUI.enabled = enabled;
		}
	}

	private static float TitleWidth(object panel, object s)
	{
		string title = ((bool)locked.Invoke(planField.GetValue(panel), null) ? LockedTitle : Title) + (string)keyName.Invoke(null, new object[1] { keyField.GetValue(panel) });
		if (title != titleText || !ReferenceEquals(s, titleStyles))
		{
			titleText = title;
			titleStyles = s;
			titleWidth = ((GUIStyle)titleStyleField.GetValue(s)).CalcSize(new GUIContent(title)).x;
		}
		return titleWidth;
	}

	private static float Px(object s, float size)
	{
		return (int)px.Invoke(s, new object[1] { size });
	}

	internal static void AfterUpdate(object __instance)
	{
		if (stopped)
		{
			return;
		}
		try
		{
			panel = __instance;
			available = PopOutBridge.ScreenBound;
			bool wasOpen = open;
			open = available && PopOutBridge.ScreenOpen;
			int screen = open ? PopOutBridge.ScreenDisplay : -1;
			if (screen >= Display.displays.Length)
			{
				screen = -1;
			}
			bool mission = (bool)inMission.Invoke(null, null);
			shown = mission && (bool)visibleField.GetValue(__instance) && !(bool)suppressed.Invoke(null, null);
			if (!mission)
			{
				autoTried = false;
			}
			if ((popped || pending) && screen != display)
			{
				Dock(__instance, forget: false, "returned to the main screen: the Pop-Out monitor closed");
			}
			if (!popped && !pending)
			{
				display = screen;
			}
			if (open && !wasOpen)
			{
				openFrame = Time.frameCount;
				openAt = Now;
			}
			if (requested)
			{
				requested = false;
				if (popped)
				{
					Dock(__instance, forget: true, "returned to the main screen");
				}
				else if (!pending && !unsupported && available)
				{
					BeginPop();
				}
			}
			if (pending)
			{
				if (sawRepaint && (bool)prefsField.GetValue(__instance))
				{
					Finish(__instance);
				}
				else if (Time.frameCount - pendingFrame > ConfirmFrames && Now - pendingAt > ConfirmSeconds)
				{
					Refuse(__instance, "Unity drew no IMGUI on Pop-Out monitor " + (display + 1));
				}
			}
			if (popped && shown)
			{
				CheckClicks(__instance);
			}
			if (!popped && !pending && !unsupported && available && !autoTried && shown && state.Detached && PopOutBridge.CanOpenStandalone)
			{
				autoTried = true;
				BeginPop();
			}
			buttonEnabled = popped || (!pending && PopOutBridge.CanOpenStandalone);
			Probe();
		}
		catch (Exception error)
		{
			Fail("strike pop-out", error);
		}
	}

	private static void BeginPop()
	{
		if (!PopOutBridge.OpenStandalone())
		{
			return;
		}
		int screen = PopOutBridge.ScreenDisplay;
		if (screen <= 0 || screen >= Display.displays.Length)
		{
			return;
		}
		display = screen;
		open = true;
		pending = true;
		sawRepaint = false;
		pendingFrame = Time.frameCount;
		pendingAt = Now;
	}

	private static void Finish(object panel)
	{
		pending = false;
		Display monitor = Display.displays[display];
		Rect window = (Rect)windowField.GetValue(panel);
		object s = stylesField.GetValue(panel);
		float right = (s != null) ? Px(s, 120f) : 120f, bottom = (s != null) ? Px(s, 40f) : 40f;
		home = window.position;
		window.position = new Vector2(Mathf.Clamp(state.X, 0f, Mathf.Max(0f, monitor.renderingWidth - right)), Mathf.Clamp(state.Y, 0f, Mathf.Max(0f, monitor.renderingHeight - bottom)));
		windowField.SetValue(panel, window);
		popped = true;
		misses = 0;
		pressFrame = 0;
		Api.Log("Coordinated Strike panel moved to Pop-Out monitor " + (display + 1) + " (" + monitor.renderingWidth + "x" + monitor.renderingHeight + "); plan, timing and launch controls unchanged");
	}

	private static void Dock(object panel, bool forget, string why)
	{
		bool was = popped;
		pending = false;
		if (popped)
		{
			Rect window = (Rect)windowField.GetValue(panel);
			state.X = Mathf.Max(0f, window.x);
			state.Y = Mathf.Max(0f, window.y);
			window.position = home;
			windowField.SetValue(panel, window);
			popped = false;
			capture.Invoke(panel, new object[1] { false });
		}
		if (forget)
		{
			state.Detached = false;
		}
		Save();
		if (was)
		{
			Api.Log("Coordinated Strike panel " + why);
		}
	}

	private static void Refuse(object panel, string why)
	{
		bool was = popped;
		// The button goes; the docked routing (kept off Pop-Out's monitor) stays.
		unsupported = true;
		Dock(panel, forget: true, "returned to the main screen: " + why);
		if (!was)
		{
			Api.Log("Coordinated Strike pop-out unavailable: " + why + "; the F8 panel stays on the main screen");
		}
	}

	// A press over the popped panel (seen through legacy Input and
	// Display.RelativeMouseAt, as Pop-Out's ClaimMouse does) must arrive as an
	// IMGUI MouseDown on that display. The choice is remembered only once one
	// has; two missed presses return the panel to the main screen.
	private static void CheckClicks(object panel)
	{
		int frame = Time.frameCount;
		if (pressFrame == 0)
		{
			if (Input.GetMouseButtonDown(0) && PointerOver(panel))
			{
				pressFrame = frame;
			}
			return;
		}
		if (frame - pressFrame < 3)
		{
			return;
		}
		if (clickFrame >= pressFrame - 1)
		{
			misses = 0;
			if (!state.Detached)
			{
				state.Detached = true;
				Save();
			}
		}
		else if (++misses >= 2)
		{
			Refuse(panel, "Unity drew the panel on monitor " + (display + 1) + " but sent its clicks elsewhere");
		}
		pressFrame = 0;
	}

	private static bool PointerOver(object panel)
	{
		Vector3 pointer = Display.RelativeMouseAt(Input.mousePosition);
		if (pointer == Vector3.zero || (int)pointer.z != display || display <= 0 || display >= Display.displays.Length)
		{
			return false;
		}
		Display monitor = Display.displays[display];
		float ratio = (monitor.systemHeight > 0) ? ((float)monitor.renderingHeight / (float)monitor.systemHeight) : 1f;
		return ((Rect)shownField.GetValue(panel)).Contains(new Vector2(pointer.x * ratio, (float)monitor.renderingHeight - pointer.y * ratio));
	}

	// True only when Unity reports where the pointer is and it is not over the
	// popped panel; an unknown pointer (Vector3.zero) never releases focus.
	private static bool PointerElsewhere(object panel)
	{
		Vector3 pointer = Display.RelativeMouseAt(Input.mousePosition);
		return pointer != Vector3.zero && !PointerOver(panel);
	}

	// While popped the main screen must not be held as "mouse over UI" by a
	// rectangle that is now on another monitor; the panel captures only when
	// the pointer is over it on the Pop-Out monitor (needed in Pop-Out's
	// shared mode, where ClaimMouse yields to the game's own view).
	internal static void BeforeCapture(object __instance, ref bool __0)
	{
		if (stopped || !popped)
		{
			return;
		}
		try
		{
			__0 = shown && PointerOver(__instance);
		}
		catch (Exception error)
		{
			Fail("strike pop-out mouse capture", error);
		}
	}

	// The author's SavePrefs writes _window.x/.y as its main-screen position.
	// SavePrefs also runs from OnApplicationQuit (cst.il:10273), F8 hide and
	// LeaveMission, so the Pop-Out position is recorded here too: quitting
	// while popped keeps where the panel sat on the Pop-Out monitor.
	internal static void BeforeSave(object __instance, ref object __state)
	{
		__state = null;
		if (stopped || !popped)
		{
			return;
		}
		Rect window = (Rect)windowField.GetValue(__instance);
		state.X = Mathf.Max(0f, window.x);
		state.Y = Mathf.Max(0f, window.y);
		Save();
		__state = window;
		window.position = home;
		windowField.SetValue(__instance, window);
	}

	internal static void AfterSave(object __instance, object __state)
	{
		if (__state is Rect window)
		{
			windowField.SetValue(__instance, window);
		}
	}

	// Pop-Out's see-through region is built from Noesis windows only
	// (ScreenCutOut.Collect -> MonitorWindow.Shape); without this the IMGUI
	// panel would be clipped away on a see-through monitor.
	internal static void AddShape(List<Rect> keep)
	{
		if (!OnPopMonitor || panel == null)
		{
			return;
		}
		Rect shownArea = (Rect)shownField.GetValue(panel);
		if (shownArea.width <= 0f || shownArea.height <= 0f)
		{
			return;
		}
		Rect area = new Rect(shownArea.x - 2f, shownArea.y - 2f, shownArea.width + 4f, shownArea.height + 4f);
		keep.Add(area);
		if (lastArea.width > 0f && lastArea != area)
		{
			keep.Add(lastArea);
		}
		lastArea = area;
	}

	private static void Probe()
	{
		if (probed || !open || display <= 0 || (!sawClick && (Time.frameCount - openFrame < 600 || Now - openAt < 10.0)))
		{
			return;
		}
		probed = true;
		Api.Log("strike pop-out probe: Pop-Out monitor " + (display + 1) + " IMGUI repaint=" + sawRepaint + ", clicks=" + sawClick + "; game window " + Screen.width + "x" + Screen.height);
	}

	private static void Save()
	{
		string text = state.Encode();
		if (text != lastSaved)
		{
			state.Save(path);
			lastSaved = text;
		}
	}

	internal static void Fail(string label, Exception error)
	{
		if (stopped)
		{
			return;
		}
		try
		{
			if (popped && panel != null)
			{
				Dock(panel, forget: true, "returned to the main screen after an error");
			}
		}
		catch
		{
		}
		stopped = true;
		Api.LogFailure(label + " stopped; author window kept on the main screen", error);
	}
}
