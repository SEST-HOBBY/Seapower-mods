using System;
using System.Collections.Generic;
using Noesis;

namespace Sest.RuntimeFixes {
internal static class NativeCostTypography
{
	private static readonly Dictionary<string, Brush> brushes = new Dictionary<string, Brush>();

	private static Brush Ink(string color)
	{
		if (!brushes.TryGetValue(color, out var value))
		{
			value = new SolidColorBrush(Color.FromRgb(Convert.ToByte(color.Substring(1, 2), 16), Convert.ToByte(color.Substring(3, 2), 16), Convert.ToByte(color.Substring(5, 2), 16)));
			brushes.Add(color, value);
		}
		return value;
	}

	internal static void Render(Panel panel, IEnumerable<CostReportLine> rows)
	{
		if (!NativeCombatSurface.Ready)
		{
			return;
		}
		panel.Children.Clear();
		foreach (CostReportLine row in rows)
		{
			if (row.Kind == CostLineKind.Spacer)
			{
				panel.Children.Add(new Border { Height = 6f });
				continue;
			}
			TextBlock text = new TextBlock
			{
				Text = row.Text.TrimStart(),
				TextWrapping = TextWrapping.Wrap,
				FontSize = 14f,
				FontWeight = FontWeight.Normal,
				Foreground = Ink("#DCE4EA"),
				Margin = new Thickness(0f, 0f, 0f, 4f)
			};
			switch (row.Kind)
			{
			case CostLineKind.Basis:
				text.FontSize = 11f;
				text.Foreground = Ink("#9BAEBB");
				text.Margin = new Thickness(0f, 0f, 0f, 6f);
				break;
			case CostLineKind.PlayerTotal:
			case CostLineKind.EnemyTotal:
				text.FontSize = 16f;
				text.FontWeight = FontWeight.DemiBold;
				text.Foreground = Ink(row.Kind == CostLineKind.PlayerTotal ? "#B7DEC5" : "#E3C4B0");
				text.Margin = new Thickness(0f, 6f, 0f, 3f);
				break;
			case CostLineKind.Breakdown:
				text.FontSize = 12f;
				text.Foreground = Ink("#B6C4CE");
				text.Margin = new Thickness(10f, 0f, 0f, 2f);
				break;
			case CostLineKind.Section:
				text.FontSize = 11f;
				text.FontWeight = FontWeight.DemiBold;
				text.Foreground = Ink("#B6C8D4");
				text.Margin = new Thickness(0f, 10f, 0f, 5f);
				break;
			case CostLineKind.Mission:
				text.FontWeight = FontWeight.DemiBold;
				text.Foreground = Ink("#F0F3F5");
				text.Margin = new Thickness(0f, 0f, 0f, 4f);
				break;
			case CostLineKind.Amount:
				text.Margin = new Thickness(8f, 0f, 0f, 3f);
				break;
			case CostLineKind.Time:
				text.FontSize = 11f;
				text.FontStyle = FontStyle.Italic;
				text.Foreground = Ink("#9BAEBB");
				text.Margin = new Thickness(8f, 0f, 0f, 6f);
				break;
			case CostLineKind.Category:
				text.FontSize = 12f;
				text.Foreground = Ink("#B6C4CE");
				text.Margin = new Thickness(16f, 0f, 0f, 3f);
				break;
			}
			if (row.Kind == CostLineKind.Mission)
			{
				panel.Children.Add(new Border
				{
					Child = text,
					BorderBrush = Ink("#34434D"),
					BorderThickness = new Thickness(0f, 1f, 0f, 0f),
					Padding = new Thickness(0f, 8f, 0f, 0f),
					Margin = new Thickness(0f, 5f, 0f, 0f)
				});
			}
			else
			{
				panel.Children.Add(text);
			}
		}
	}
}

}
