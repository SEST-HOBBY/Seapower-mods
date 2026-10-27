using System;

namespace Sest.UiFixes
{
    // Invalidate the scope before validating a cached native UI object. A view
    // from the previous mission may already have lost its native counterpart.
    internal sealed class LookupCache<T> where T : class
    {
        object context, root;
        T value;
        float next;
        internal T Resolve(object current, object host, float now, T hint, Func<T, bool> valid, Func<T> discover)
        {
            if (!ReferenceEquals(current, context) || !ReferenceEquals(host, root))
            { context = current; root = host; value = null; next = 0; }
            if (current == null || host == null) return null;
            if (hint != null && valid(hint)) return value = hint;
            if (value != null && valid(value)) return value;
            value = null;
            if (now < next) return null;
            next = now + 0.5f;
            return value = discover();
        }
    }
}
