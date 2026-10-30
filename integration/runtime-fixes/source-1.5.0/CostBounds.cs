using System;

namespace Sest.RuntimeFixes {
internal struct CostBounds
{
	internal float Left;

	internal float Top;

	internal float Right;

	internal float Bottom;

	internal float Width => Right - Left;

	internal float Height => Bottom - Top;

	internal CostBounds(float l, float t, float r, float b)
	{
		Left = l;
		Top = t;
		Right = Math.Max(l + 1f, r);
		Bottom = Math.Max(t + 1f, b);
	}
}

}
