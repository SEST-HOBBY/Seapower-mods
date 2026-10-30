// Compile-time stand-in ONLY (never shipped). Members/owners mirror the
// MemberRefs that SEST.RuntimeFixes 1.5.0 (7ba6d6d9...) itself records.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
[assembly: AssemblyVersion("0.0.0.0")]
namespace Noesis
{
    public class BaseComponent
    {
        public static bool operator ==(BaseComponent a, BaseComponent b) { return ReferenceEquals(a, b); }
        public static bool operator !=(BaseComponent a, BaseComponent b) { return !ReferenceEquals(a, b); }
        public override bool Equals(object o) { return ReferenceEquals(this, o); }
        public override int GetHashCode() { return 0; }
    }
    public class DispatcherObject : BaseComponent { }
    public class DependencyObject : DispatcherObject { }
    public class DependencyProperty : BaseComponent { }
    public class Visual : DependencyObject
    {
        public bool IsDescendantOf(Visual v) { return false; }
        public Matrix4 TransformToAncestor(Visual v) { return default(Matrix4); }
    }
    public delegate void RoutedEventHandler(object sender, RoutedEventArgs e);
    public delegate void MouseWheelEventHandler(object sender, MouseWheelEventArgs e);
    public class RoutedEventArgs : EventArgs { public bool Handled { get; set; } }
    public class MouseEventArgs : RoutedEventArgs { }
    public class MouseWheelEventArgs : MouseEventArgs { public int Delta { get { return 0; } } }
    public class UIElement : Visual
    {
        public event MouseWheelEventHandler PreviewMouseWheel;
        public bool IsMouseOver { get { return false; } }
        public bool IsVisible { get { return false; } }
        public bool Focusable { get; set; }
        public bool IsEnabled { get; set; }
        void Touch() { PreviewMouseWheel(null, null); }
    }
    public class FrameworkElement : UIElement
    {
        public object FindName(string n) { return null; }
        public float ActualHeight { get { return 0; } }
        public float ActualWidth { get { return 0; } }
        public object DataContext { get; set; }
        public float Height { get; set; }
        public bool IsLoaded { get { return false; } }
        public string Name { get; set; }
        public ResourceDictionary Resources { get; set; }
        public float Width { get; set; }
        public Thickness Margin { get; set; }
        public float MaxHeight { get; set; }
        public float MaxWidth { get; set; }
        public object ToolTip { get; set; }
    }
    public class Control : FrameworkElement { public float FontSize { get; set; } }
    public class ContentControl : Control { public object Content { get; set; } }
    public class HeaderedContentControl : ContentControl { }
    public class UserControl : ContentControl { }
    public class ButtonBase : ContentControl { public event RoutedEventHandler Click; void Touch() { Click(null, null); } }
    public class Button : ButtonBase { }
    public class ScrollViewer : ContentControl
    {
        public void ScrollToVerticalOffset(float o) { }
        public float ScrollableHeight { get { return 0; } }
        public float VerticalOffset { get { return 0; } }
    }
    public class ItemsControl : Control
    {
        public IEnumerable ItemsSource { get; set; }
        public static DependencyProperty ItemsSourceProperty { get { return null; } }
    }
    public class Panel : FrameworkElement { public UIElementCollection Children { get { return null; } } }
    public class StackPanel : Panel { }
    public class Decorator : FrameworkElement { public UIElement Child { get; set; } }
    public class Border : Decorator
    {
        public Brush BorderBrush { get; set; }
        public Thickness BorderThickness { get; set; }
        public Thickness Padding { get; set; }
    }
    public enum FontWeight { Normal = 400, DemiBold = 600, SemiBold = 600, Bold = 700 }
    public enum FontStyle { Normal = 0, Oblique = 1, Italic = 2 }
    public enum TextWrapping { NoWrap = 0, Wrap = 1, WrapWithOverflow = 2 }
    public class TextBlock : FrameworkElement
    {
        public float FontSize { get; set; }
        public FontStyle FontStyle { get; set; }
        public FontWeight FontWeight { get; set; }
        public Brush Foreground { get; set; }
        public string Text { get; set; }
        public TextWrapping TextWrapping { get; set; }
    }
    public class Freezable : DependencyObject { }
    public class Animatable : Freezable { }
    public class Brush : Animatable { }
    public class SolidColorBrush : Brush { public SolidColorBrush(Color c) { } }
    public struct Color { public static Color FromRgb(byte r, byte g, byte b) { return default(Color); } }
    public struct Thickness { public Thickness(float l, float t, float r, float b) { } }
    public struct Matrix4 { }
    public struct Rect
    {
        public Rect(float x, float y, float w, float h) { }
        public void Transform(Matrix4 m) { }
        public float Bottom { get { return 0; } }
        public float Top { get { return 0; } }
    }
    public class BaseUICollection : BaseComponent { public void Clear() { } }
    public class UICollection<T> : BaseUICollection
    {
        public void Add(T i) { }
        public bool Contains(T i) { return false; }
        public void Insert(int x, T i) { }
        public bool Remove(T i) { return false; }
    }
    public class UIElementCollection : UICollection<UIElement> { }
    public class ResourceDictionary : BaseComponent { public ResourceDictionaryCollection MergedDictionaries { get { return null; } } }
    public class ResourceDictionaryCollection : UICollection<ResourceDictionary> { }
    public class FreezableCollection<T> : Animatable
    {
        public struct Enumerator : IDisposable { public bool MoveNext() { return false; } public T Current { get { return default(T); } } public void Dispose() { } }
        public Enumerator GetEnumerator() { return default(Enumerator); }
    }
    public class PropertyPath : BaseComponent { public string Path { get { return null; } } }
    public class Binding : BaseComponent { public PropertyPath Path { get { return null; } } }
    public static class BindingOperations { public static Binding GetBinding(DependencyObject o, DependencyProperty p) { return null; } }
    public static class GUI
    {
        public static object ParseXaml(string x) { return null; }
        public static void RegisterType(Type t) { }
    }
    public class View : BaseComponent { public static View Find(BaseComponent c) { return null; } }
    public static class VisualTreeHelper
    {
        public static DependencyObject GetChild(DependencyObject o, int i) { return null; }
        public static int GetChildrenCount(DependencyObject o) { return 0; }
        public static DependencyObject GetParent(DependencyObject o) { return null; }
    }
}
namespace Noesis.Interactivity
{
    public abstract class Behavior : Noesis.Animatable { }
    public class Behavior<T> : Behavior where T : Noesis.DependencyObject { }
    public class BehaviorCollection : Noesis.FreezableCollection<Behavior> { }
    public static class Interaction { public static BehaviorCollection GetBehaviors(Noesis.DependencyObject o) { return null; } }
}
