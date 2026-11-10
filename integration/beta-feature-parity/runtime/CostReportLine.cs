namespace Sest.RuntimeFixes;

internal sealed class CostReportLine
{
	internal readonly CostLineKind Kind;

	internal readonly string Text;
    internal readonly string[] Colours;

	internal CostReportLine(CostLineKind kind, string text)
	    : this(kind, text, null) { }

    internal CostReportLine(CostLineKind kind, string text, string[] colours)
    {
        Kind = kind; Text = text; Colours = colours;
    }
}
