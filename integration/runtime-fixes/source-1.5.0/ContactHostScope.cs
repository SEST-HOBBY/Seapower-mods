using System;

namespace Sest.RuntimeFixes {
internal static class ContactHostScope
{
	[ThreadStatic]
	private static int depth;

	internal static bool Active => depth > 0;

	internal static int Begin()
	{
		int result = depth;
		depth++;
		return result;
	}

	internal static void End(int previous)
	{
		depth = previous;
	}
}

}
