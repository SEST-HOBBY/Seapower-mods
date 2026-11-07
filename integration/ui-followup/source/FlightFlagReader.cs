using System.Reflection;

namespace Sest.UiFixes
{
    internal static class FlightFlagReader
    {
        internal static object Read(FieldInfo aircraftField, FieldInfo helicopterField, object target)
        {
            if (target == null) return true;
            if (aircraftField != null && aircraftField.DeclaringType.IsInstanceOfType(target))
                return aircraftField.GetValue(target);
            if (helicopterField != null && helicopterField.DeclaringType.IsInstanceOfType(target))
                return helicopterField.GetValue(target);
            // Retain the original 30-second hold/timeout for an unknown type.
            return false;
        }
    }
}
