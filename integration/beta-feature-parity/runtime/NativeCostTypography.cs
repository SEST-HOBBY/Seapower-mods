using System;
using System.Collections.Generic;
using Noesis;

namespace Sest.RuntimeFixes;

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
				panel.Children.Add(new Border
				{
					Height = 6f
				});
				continue;
			}
            if (row.Kind == CostLineKind.Ribbon && row.Colours != null)
            {
                var band = new StackPanel { Orientation = Orientation.Horizontal };
                foreach (string colour in row.Colours)
                    band.Children.Add(new Border { Width = 20f, Height = 20f, Background = Ink(colour) });
                panel.Children.Add(new Border { Child = band, BorderBrush = Ink("#B0B8BC"), BorderThickness = new Thickness(1f), HorizontalAlignment = HorizontalAlignment.Left, Margin = new Thickness(0f, 10f, 0f, 4f) });
            }
			TextBlock textBlock = new TextBlock();
			textBlock.Text = row.Text.TrimStart();
			textBlock.TextWrapping = TextWrapping.Wrap;
			textBlock.FontSize = 14f;
			textBlock.FontWeight = FontWeight.Normal;
			textBlock.Foreground = Ink("#DCE4EA");
			textBlock.Margin = new Thickness(0f, 0f, 0f, 4f);
			TextBlock textBlock2 = textBlock;
			switch (row.Kind)
			{
			case CostLineKind.Basis:
				textBlock2.FontSize = 11f;
				textBlock2.Foreground = Ink("#9BAEBB");
				textBlock2.Margin = new Thickness(0f, 0f, 0f, 6f);
				break;
			case CostLineKind.PlayerTotal:
			case CostLineKind.EnemyTotal:
				textBlock2.FontSize = 16f;
				textBlock2.FontWeight = FontWeight.DemiBold;
				textBlock2.Foreground = Ink((row.Kind != CostLineKind.PlayerTotal) ? "#E3C4B0" : "#B7DEC5");
				textBlock2.Margin = new Thickness(0f, 6f, 0f, 3f);
				break;
			case CostLineKind.Breakdown:
				textBlock2.FontSize = 12f;
				textBlock2.Foreground = Ink("#B6C4CE");
				textBlock2.Margin = new Thickness(10f, 0f, 0f, 2f);
				break;
			case CostLineKind.Section:
				textBlock2.FontSize = 11f;
				textBlock2.FontWeight = FontWeight.DemiBold;
				textBlock2.Foreground = Ink("#B6C8D4");
				textBlock2.Margin = new Thickness(0f, 10f, 0f, 5f);
				break;
			case CostLineKind.Ribbon:
            case CostLineKind.Mission:
				textBlock2.FontWeight = FontWeight.DemiBold;
				textBlock2.Foreground = Ink("#F0F3F5");
				textBlock2.Margin = new Thickness(0f, 0f, 0f, 4f);
				break;
			case CostLineKind.Amount:
				textBlock2.Margin = new Thickness(8f, 0f, 0f, 3f);
				break;
			case CostLineKind.Time:
				textBlock2.FontSize = 11f;
				textBlock2.FontStyle = FontStyle.Italic;
				textBlock2.Foreground = Ink("#9BAEBB");
				textBlock2.Margin = new Thickness(8f, 0f, 0f, 6f);
				break;
			case CostLineKind.Category:
				textBlock2.FontSize = 12f;
				textBlock2.Foreground = Ink("#B6C4CE");
				textBlock2.Margin = new Thickness(16f, 0f, 0f, 3f);
				break;
			case CostLineKind.Item:
				textBlock2.FontSize = 12f;
				textBlock2.Foreground = Ink("#A3B3BF");
				textBlock2.Margin = new Thickness(26f, 0f, 0f, 2f);
				break;
			}
			if (row.Kind == CostLineKind.Mission)
			{
				panel.Children.Add(new Border
				{
					Child = textBlock2,
					BorderBrush = Ink("#34434D"),
					BorderThickness = new Thickness(0f, 1f, 0f, 0f),
					Padding = new Thickness(0f, 8f, 0f, 0f),
					Margin = new Thickness(0f, 5f, 0f, 0f)
				});
			}
			else
			{
				panel.Children.Add(textBlock2);
			}
		}
	}
}
