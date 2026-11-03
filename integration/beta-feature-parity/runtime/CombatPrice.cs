namespace Sest.RuntimeFixes;

internal sealed class CombatPrice
{
	internal decimal? Amount;

	internal string Category;

	internal bool Ignored;

	// Which catalog section or unit file supplied the amount, for the item rows.
	internal string Source;
}
