using System;
using System.ComponentModel;
using System.Globalization;
using System.IO;

namespace Sest.RuntimeFixes {
internal enum CostLineKind
{
	Body,
	Basis,
	PlayerTotal,
	EnemyTotal,
	Breakdown,
	Section,
	Mission,
	Amount,
	Time,
	Category,
	Spacer
}

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

public sealed class CumulativeCombatCostsViewModel : INotifyPropertyChanged
{
	public event PropertyChangedEventHandler PropertyChanged;

	private string subtitle = string.Empty;

	private string summary = string.Empty;

	private string details = string.Empty;

	private string notes = string.Empty;

	public string Title
	{
		get { return "CUMULATIVE COMBAT COSTS"; }
	}

	public string Subtitle
	{
		get { return subtitle; }
	}

	public string Summary
	{
		get { return summary; }
	}

	public string Details
	{
		get { return details; }
	}

	public string Notes
	{
		get { return notes; }
	}

	internal int Revision { get; private set; }

	internal CostReportLine[] SummaryRows { get; private set; } = new CostReportLine[0];

	internal CostReportLine[] DetailRows { get; private set; } = new CostReportLine[0];

	internal void Set(CampaignCosts.CostView report, bool live)
	{
		bool changed = Change(ref subtitle, (live ? "Current mission" : "Campaign") + " | F11 closes | Drag the title bar to move", "Subtitle");
		changed |= Change(ref summary, string.Join("\n", report.Summary), "Summary");
		changed |= Change(ref details, string.Join("\n", report.Details), "Details");
		changed |= Change(ref notes, string.Join("\n", report.Notes), "Notes");
		if (changed)
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
		PropertyChangedEventHandler handler = PropertyChanged;
		if (handler != null)
		{
			handler(this, new PropertyChangedEventArgs(name));
		}
		return true;
	}
}

internal struct CostBounds
{
	internal float Left;

	internal float Top;

	internal float Right;

	internal float Bottom;

	internal float Width
	{
		get { return Right - Left; }
	}

	internal float Height
	{
		get { return Bottom - Top; }
	}

	internal CostBounds(float l, float t, float r, float b)
	{
		Left = l;
		Top = t;
		Right = Math.Max(l + 1f, r);
		Bottom = Math.Max(t + 1f, b);
	}
}

internal sealed class CostWindowState
{
	internal float X = 12f;

	internal float Y = 170f;

	internal float Width = 570f;

	internal float Height = 560f;

	internal bool Positioned;

	internal void Fit(CostBounds area, bool menu)
	{
		if (float.IsNaN(Width) || float.IsInfinity(Width))
		{
			Width = 570f;
		}
		if (float.IsNaN(Height) || float.IsInfinity(Height))
		{
			Height = 560f;
		}
		if (float.IsNaN(X) || float.IsInfinity(X))
		{
			X = area.Left;
		}
		if (float.IsNaN(Y) || float.IsInfinity(Y))
		{
			Y = area.Top;
		}
		Width = Math.Min(area.Width, Math.Max(Math.Min(360f, area.Width), Width));
		Height = Math.Min(area.Height, Math.Max(Math.Min(300f, area.Height), Height));
		if (menu && !Positioned)
		{
			Y = area.Top;
		}
		X = Math.Max(area.Left, Math.Min(X, area.Right - Width));
		Y = Math.Max(area.Top, Math.Min(Y, area.Bottom - Height));
	}

	internal string Encode()
	{
		return string.Join("|", "1", X.ToString("R", CultureInfo.InvariantCulture), Y.ToString("R", CultureInfo.InvariantCulture), Width.ToString("R", CultureInfo.InvariantCulture), Height.ToString("R", CultureInfo.InvariantCulture));
	}

	internal static CostWindowState Parse(string text)
	{
		CostWindowState costWindowState = new CostWindowState();
		string[] array = (text ?? string.Empty).Trim().Split('|');
		if (array.Length != 5 || array[0] != "1")
		{
			return costWindowState;
		}
		float[] array2 = new float[4];
		for (int i = 0; i < 4; i++)
		{
			if (!float.TryParse(array[i + 1], NumberStyles.Float, CultureInfo.InvariantCulture, out array2[i]) || float.IsNaN(array2[i]) || float.IsInfinity(array2[i]) || array2[i] < 0f || array2[i] > 100000f)
			{
				return costWindowState;
			}
		}
		if (array2[2] < 100f || array2[3] < 100f)
		{
			return costWindowState;
		}
		costWindowState.X = array2[0];
		costWindowState.Y = array2[1];
		costWindowState.Width = array2[2];
		costWindowState.Height = array2[3];
		costWindowState.Positioned = true;
		return costWindowState;
	}

	internal void Save(string path)
	{
		try
		{
			if (File.Exists(path))
			{
				string text = File.ReadAllText(path);
				if (!text.TrimStart().StartsWith("1|", StringComparison.Ordinal))
				{
					return;
				}
			}
			Directory.CreateDirectory(Path.GetDirectoryName(path));
			string text2 = path + ".tmp";
			File.WriteAllText(text2, Encode());
			if (File.Exists(path))
			{
				File.Replace(text2, path, null);
			}
			else
			{
				File.Move(text2, path);
			}
		}
		catch (Exception error)
		{
			Api.LogFailure("cost-window position stays in memory", error);
		}
	}
}

}
