using System;
using System.Globalization;
using System.IO;

namespace Sest.RuntimeFixes;

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
