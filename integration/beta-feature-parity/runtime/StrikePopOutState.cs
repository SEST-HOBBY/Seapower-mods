using System;
using System.Globalization;
using System.IO;

namespace Sest.RuntimeFixes;

// SEST's own record for the Coordinated Strike pop-out: whether the player
// last chose the Pop-Out monitor and where the panel sat there. The author's
// main-screen position stays in PlayerPrefs (CoordinatedStrikeTool.x/.y).
internal sealed class StrikePopOutState
{
	internal const string Header = "SEST_STRIKE_1";

	internal bool Detached;

	internal float X = 80f;

	internal float Y = 80f;

	internal bool Writable = true;

	internal string Encode()
	{
		return Header + "\n" + (Detached ? "1" : "0") + "\n" + X.ToString("R", CultureInfo.InvariantCulture) + "|" + Y.ToString("R", CultureInfo.InvariantCulture);
	}

	internal static StrikePopOutState Parse(string text)
	{
		StrikePopOutState state = new StrikePopOutState();
		if (string.IsNullOrWhiteSpace(text))
		{
			return state;
		}
		string[] lines = text.Replace("\r", string.Empty).Trim().Split('\n');
		string[] at = lines.Length == 3 ? lines[2].Split('|') : new string[0];
		if (lines.Length != 3 || lines[0] != Header || (lines[1] != "0" && lines[1] != "1") || at.Length != 2 ||
			!float.TryParse(at[0], NumberStyles.Float, CultureInfo.InvariantCulture, out float x) ||
			!float.TryParse(at[1], NumberStyles.Float, CultureInfo.InvariantCulture, out float y) ||
			float.IsNaN(x) || float.IsNaN(y) || x < 0f || y < 0f || x > 100000f || y > 100000f)
		{
			state.Writable = false;
			return state;
		}
		state.Detached = lines[1] == "1";
		state.X = x;
		state.Y = y;
		return state;
	}

	internal void Save(string path)
	{
		if (!Writable || path == null)
		{
			return;
		}
		try
		{
			if (File.Exists(path) && !Parse(File.ReadAllText(path)).Writable)
			{
				Writable = false;
				return;
			}
			Directory.CreateDirectory(Path.GetDirectoryName(path));
			string temp = path + ".tmp";
			File.WriteAllText(temp, Encode());
			if (File.Exists(path))
			{
				File.Replace(temp, path, null);
			}
			else
			{
				File.Move(temp, path);
			}
		}
		catch (Exception error)
		{
			Api.LogFailure("strike pop-out placement stays in memory", error);
		}
	}
}
