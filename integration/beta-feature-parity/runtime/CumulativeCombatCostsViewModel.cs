using System.ComponentModel;

namespace Sest.RuntimeFixes;

public sealed class CumulativeCombatCostsViewModel : INotifyPropertyChanged
{
	private string subtitle = string.Empty;

	private string summary = string.Empty;

	private string details = string.Empty;

	private string notes = string.Empty;

	private string title = "CUMULATIVE COMBAT COSTS";

    public string Title => title;
    internal bool World { get; private set; }

	public string Subtitle => subtitle;

	public string Summary => summary;

	public string Details => details;

	public string Notes => notes;

	internal int Revision { get; private set; }

	internal CostReportLine[] SummaryRows { get; private set; } = new CostReportLine[0];


	internal CostReportLine[] DetailRows { get; private set; } = new CostReportLine[0];


	public event PropertyChangedEventHandler PropertyChanged;

	internal void Set(CampaignCosts.CostView report, bool live)
	{
		bool flag = Change(ref title, report.Title ?? "CUMULATIVE COMBAT COSTS", "Title");
        flag |= World != report.World;
        World = report.World;
        flag |= Change(ref subtitle, report.Subtitle ?? (((!live) ? "Campaign" : "Current mission") + " | F11 closes | Drag the title bar to move"), "Subtitle");
		flag |= Change(ref summary, string.Join("\n", report.Summary), "Summary");
		flag |= Change(ref details, string.Join("\n", report.Details), "Details");
		if (flag | Change(ref notes, string.Join("\n", report.Notes), "Notes"))
		{
			SummaryRows = report.SummaryRows.ToArray();
			DetailRows = report.DetailRows.ToArray();
			Revision++;
		}
	}

	private bool Change(ref string field, string text, string name)
	{
		if (field == text)
		{
			return false;
		}
		field = text;
		this.PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
		return true;
	}
}
