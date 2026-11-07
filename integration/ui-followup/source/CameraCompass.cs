using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Noesis;
using SeaPower;
using SeapowerUI;
using SeapowerUI.ViewModels;
using UnityEngine;
using GameWindow = SeapowerUI.Window;

namespace Sest.UiFixes
{
    internal static class CameraCompass
    {
        static MainGameView mainView;
        static MainGameViewModel main;
        static FrameworkElement tape;
        static Panel home, current, pip;
        static int homeIndex, attempts, monitor = -1;
        static float next;
        static bool reported, routingFailed;
        static GameObject overlay;
        static Camera camera;
        static Grid screenHost;
        static ScaleTransform scale;
        static MethodInfo createView, flatten;
        static SavedValue[] placement;
        const string RootXaml = "<local:ScalableUserControl xmlns='http://schemas.microsoft.com/winfx/2006/xaml/presentation' xmlns:x='http://schemas.microsoft.com/winfx/2006/xaml' xmlns:local='clr-namespace:SeapowerUI' IsHitTestVisible='False'><Grid><Grid><Grid.LayoutTransform><ScaleTransform x:Name='CompassScale'/></Grid.LayoutTransform><Grid x:Name='CameraCompassHost'/></Grid></Grid></local:ScalableUserControl>";

        sealed class SavedValue
        {
            readonly DependencyObject owner;
            readonly DependencyProperty property;
            readonly BindingBase binding;
            readonly object local;
            internal SavedValue(DependencyObject target, DependencyProperty p)
            { owner = target; property = p; binding = BindingOperations.GetBindingBase(target, p); local = target.ReadLocalValue(p); }
            internal void Restore()
            {
                if (binding != null) BindingOperations.SetBinding(owner, property, binding);
                else if (Equals(local, DependencyProperty.UnsetValue)) owner.ClearValue(property);
                else owner.SetValue(property, local);
            }
        }
        internal static void Install()
        {
            try
            {
                var pop = ContactsFix.Find("SeaPowerPopOut.PopOutScreen");
                ContactsFix.Require(pop.Assembly, ContactsSurfaceFix.PopOutHash);
                createView = typeof(NoesisView).GetMethod("CreateView", ContactsFix.All, null, new[] { typeof(FrameworkElement) }, null);
                flatten = pop.GetMethod("Flatten", ContactsFix.All);
                if (createView == null || flatten == null) throw new MissingMethodException("Inspected Noesis overlay contract");
            }
            catch (Exception e)
            { createView = flatten = null; ContactsFix.Log("Camera compass inactive: " + e.Message); }
        }
        static IEnumerable<DependencyObject> Walk(DependencyObject root)
        {
            if (root == null) yield break;
            var queue = new Queue<DependencyObject>(); queue.Enqueue(root); int count = 0;
            while (queue.Count != 0 && count++ < 20000)
            {
                var item = queue.Dequeue(); yield return item;
                int children = VisualTreeHelper.GetChildrenCount(item);
                for (int i = 0; i < children; i++) queue.Enqueue(VisualTreeHelper.GetChild(item, i));
            }
        }
        static bool HeadingBinding(DependencyObject target, DependencyProperty property)
        {
            var binding = BindingOperations.GetBindingBase(target, property) as Noesis.Binding;
            return binding?.Path?.Path == "BearingTapeTransform";
        }
        static bool HeadingTransform(Noesis.Transform transform)
        {
            if (transform is TranslateTransform t && HeadingBinding(t, TranslateTransform.XProperty)) return true;
            if (transform is TransformGroup group)
                foreach (var child in group.Children) if (HeadingTransform(child)) return true;
            return false;
        }
        static FrameworkElement FindTape()
        {
            foreach (var element in Walk(mainView).OfType<FrameworkElement>())
            {
                if (!HeadingTransform(element.RenderTransform) && !HeadingTransform(element.LayoutTransform) &&
                    !HeadingBinding(element, Canvas.LeftProperty)) continue;
                // Require the exact camera-heading binding and its short clipped
                // viewport. Never select an unrelated HUD bar by its screen position.
                FrameworkElement viewport = element;
                for (int depth = 0; viewport != null && depth < 6; depth++, viewport = ContactsFix.UiParent(viewport) as FrameworkElement)
                {
                    if ((!viewport.ClipToBounds && viewport.Clip == null) || viewport.ActualHeight <= 0 || viewport.ActualHeight > 72 ||
                        viewport.ActualWidth <= 0 || viewport.ActualWidth > 1000) continue;
                    var outer = ContactsFix.UiParent(viewport) as FrameworkElement;
                    if (outer is Panel panel && panel.Children.Count <= 4 && outer.ActualHeight > 0 && outer.ActualHeight <= 72 &&
                        Math.Abs(outer.ActualWidth - viewport.ActualWidth) < 4 &&
                        !Walk(outer).Any(x => x is ButtonBase || x is TextBox)) viewport = outer;
                    if (ContactsFix.UiParent(viewport) is Panel) return viewport;
                }
            }
            return null;
        }
        static Panel PipHost()
        {
            if (pip != null && pip.IsDescendantOf(mainView)) return pip;
            pip = null;
            var window = Walk(mainView).OfType<GameWindow>().FirstOrDefault(w =>
                w.DataContext?.GetType().FullName == "SeapowerUI.ViewModels.WorldViewWindowViewModel");
            if (window == null) return null;
            var content = window.Content as FrameworkElement;
            return pip = content as Panel ?? Walk(content).OfType<Grid>().FirstOrDefault();
        }
        static Panel ScreenHost(int display)
        {
            if (overlay != null && monitor == display)
            { if (!overlay.activeSelf) overlay.SetActive(true); return screenHost; }
            // Release the native compass from the old overlay before disposing it.
            Move(home);
            if (overlay != null) UnityEngine.Object.Destroy(overlay);
            overlay = null; screenHost = null; scale = null; camera = null; monitor = -1;
            GameObject candidate = null;
            try
            {
                var root = (ScalableUserControl)Noesis.GUI.ParseXaml(RootXaml);
                root.Resources = (ResourceDictionary)flatten.Invoke(null, new object[] { mainView.Resources });
                root.DataContext = main;
                var host = (Grid)root.FindName("CameraCompassHost");
                var transform = (ScaleTransform)root.FindName("CompassScale");
                if (host == null || transform == null) throw new InvalidOperationException("Camera compass host missing");
                candidate = new GameObject("SEST unit camera compass");
                var cam = candidate.AddComponent<Camera>();
                cam.cullingMask = 0; cam.depth = 89; cam.targetDisplay = display;
                cam.clearFlags = CameraClearFlags.Depth;
                cam.useOcclusionCulling = false; cam.allowHDR = false; cam.allowMSAA = false;
                var view = candidate.AddComponent<NoesisView>();
                view.UseRealTimeClock = true;
                view.EnableKeyboard = false; view.EnableMouse = false; view.EnableTouch = false; view.EnableActions = false;
                if (SeaPower.DM._noesisView != null) view.DPIScale = SeaPower.DM._noesisView.DPIScale;
                createView.Invoke(view, new object[] { root });
                overlay = candidate; camera = cam; screenHost = host; scale = transform; monitor = display;
                return screenHost;
            }
            catch { if (candidate != null) UnityEngine.Object.Destroy(candidate); throw; }
        }
        static void Move(Panel target)
        {
            if (target == null || tape == null || current == target) return;
            var previous = ContactsFix.UiParent(tape) as Panel;
            if (previous == null) throw new InvalidOperationException("Compass parent changed outside the inspected panel path");
            previous.Children.Remove(tape);
            try
            {
                if (target == home) target.Children.Insert(Math.Min(homeIndex, target.Children.Count), tape);
                else target.Children.Add(tape);
            }
            catch { previous.Children.Add(tape); throw; }
            current = target;
            if (target == home) foreach (var value in placement) value.Restore();
            else
            {
                tape.DataContext = main;
                tape.SetCurrentValue(FrameworkElement.MarginProperty, new Thickness(0));
                tape.SetCurrentValue(FrameworkElement.HorizontalAlignmentProperty, HorizontalAlignment.Center);
                tape.SetCurrentValue(FrameworkElement.VerticalAlignmentProperty, VerticalAlignment.Top);
                tape.SetCurrentValue(UIElement.IsHitTestVisibleProperty, false);
            }
            ContactsFix.Log("Camera compass moved to " + (target == home ? "main 3D view" : (target == screenHost ? "unit-camera monitor " + (monitor + 1) : "3D picture-in-picture")) + ".");
        }
        internal static void Tick()
        {
            if (createView == null || flatten == null || Time.unscaledTime < next) return;
            next = Time.unscaledTime + 0.2f;
            try
            {
                var view = MainGameView.Instance; var vm = Globals._mainGameViewModel;
                if (view == null || vm == null) return;
                if (!ReferenceEquals(mainView, view) || !ReferenceEquals(main, vm))
                { End(); mainView = view; main = vm; }
                if (routingFailed) return;
                if (tape == null)
                {
                    if (attempts++ >= 6) return;
                    next = Time.unscaledTime + 1;
                    tape = FindTape();
                    if (tape == null)
                    {
                        if (attempts == 6) ContactsFix.Log("Camera compass not relocated: exact heading-bound clipped viewport was not found. A UI tree capture is needed.");
                        return;
                    }
                    home = ContactsFix.UiParent(tape) as Panel; current = home; homeIndex = home.Children.IndexOf(tape);
                    placement = new[] { new SavedValue(tape, FrameworkElement.MarginProperty), new SavedValue(tape, FrameworkElement.HorizontalAlignmentProperty),
                        new SavedValue(tape, FrameworkElement.VerticalAlignmentProperty), new SavedValue(tape, FrameworkElement.DataContextProperty),
                        new SavedValue(tape, UIElement.IsHitTestVisibleProperty) };
                    ContactsFix.Log("Camera compass identified by BearingTapeTransform: " + tape.GetType().Name + " '" + tape.Name + "' " + tape.ActualWidth + "x" + tape.ActualHeight + ".");
                }
                bool fullMap = main.MapVisible && main.Map != null && main.Map.IsFullscreen;
                var destination = CompassRouting.Choose(main.IsHudVisible, fullMap, main.WorldViewDetached, main.ShowPip3D);
                bool visible = destination != CompassDestination.Hidden;
                Panel target = home;
                if (destination == CompassDestination.Detached3D)
                {
                    target = ScreenHost(main.WorldViewMonitor);
                    float s = (Singleton<OptionsManager>.InstanceExists() ? Singleton<OptionsManager>.Instance.UIScale : 1) * Math.Max(1, Math.Min(camera.pixelWidth, camera.pixelHeight)) / 1080f;
                    if (Math.Abs(scale.ScaleX - s) > 0.001f) { scale.ScaleX = s; scale.ScaleY = s; }
                }
                else if (destination == CompassDestination.Pip3D) { target = PipHost(); if (target == null) visible = false; }
                Move(target);
                if (destination != CompassDestination.Detached3D && overlay != null && overlay.activeSelf) overlay.SetActive(false);
                var visibility = visible ? Visibility.Visible : Visibility.Collapsed;
                if (tape.Visibility != visibility) tape.SetCurrentValue(UIElement.VisibilityProperty, visibility);
            }
            catch (Exception e)
            {
                routingFailed = true; // Do not recreate a failing native overlay every frame.
                if (!reported) { reported = true; ContactsFix.Log("Camera compass routing skipped: " + e.GetType().Name + ": " + e.Message); }
            }
        }
        internal static void End()
        {
            // No reads/writes against UI objects whose native view is tearing down.
            if (overlay != null) UnityEngine.Object.Destroy(overlay);
            overlay = null; camera = null; screenHost = null; scale = null; monitor = -1;
            mainView = null; main = null; tape = null; home = current = pip = null; placement = null;
            attempts = 0; reported = routingFailed = false; next = 0;
        }
    }
}
