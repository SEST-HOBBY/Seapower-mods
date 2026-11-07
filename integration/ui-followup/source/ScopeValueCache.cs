namespace Sest.UiFixes
{
    // A successful value belongs to one mission. Null is never a cached hit.
    internal sealed class ScopeValueCache
    {
        object scope, value;
        internal object Get(object current)
        {
            if (!ReferenceEquals(current, scope)) { scope = current; value = null; }
            return current == null ? null : value;
        }
        internal void Remember(object current, object result)
        {
            Get(current);
            if (current != null && result != null) value = result;
        }
        internal void Clear() { scope = value = null; }
    }
}
