namespace Sest.RuntimeFixes;

internal sealed class CostReportLine
{
	internal readonly CostLineKind Kind;

	internal readonly string Text;

	internal CostReportLine(CostLineKind kind, string text)
	{
		Kind = kind;
		Text = text;
	}
}
