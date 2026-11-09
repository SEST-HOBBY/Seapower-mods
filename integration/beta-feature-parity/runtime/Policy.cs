using System;
using System.IO;

namespace Sest.RuntimeFixes;

internal static class Policy
{
	internal const float LookAheadNm = 1.1f;

	internal const float LandClearanceFeet = 500f;

	internal static bool Finite(float value)
	{
		return !float.IsNaN(value) && !float.IsInfinity(value);
	}

	internal static bool IsMst(string name)
	{
		if (string.IsNullOrWhiteSpace(name))
		{
			return false;
		}
		string fileNameWithoutExtension = Path.GetFileNameWithoutExtension(name.Replace('\\', '/'));
		return string.Equals(fileNameWithoutExtension, "usn_rgm-109e5a", StringComparison.OrdinalIgnoreCase) || string.Equals(fileNameWithoutExtension, "usn_ugm-109e5a", StringComparison.OrdinalIgnoreCase);
	}

	internal static bool CruiseStage(string stage)
	{
		switch (stage)
		{
		case "ToBearing":
		case "MaintainHeight":
		case "MoveToLoftAlt":
		case "MaintainLoftAlt":
		case "MoveToSeaSkimming":
		case "MaintainSeaSkimming":
		case "MoveToFinalFlightAlt":
		case "MaintainFinalFlightAlt":
		case "AlignSensorToTarget":
			return true;
		default:
			return false;
		}
	}

	internal static float Altitude(float native, float highestLand, float clearance)
	{
		if (!Finite(native) || !Finite(highestLand) || !Finite(clearance) || highestLand <= 0f || clearance <= 0f)
		{
			return native;
		}
		float num = highestLand + clearance;
		return (!Finite(num)) ? native : Math.Max(native, num);
	}

	internal static bool PackEnabled(string[] lines, string folder)
	{
		string a = string.Empty;
		foreach (string text in lines)
		{
			string text2 = text.Trim();
			if (text2.StartsWith("["))
			{
				a = text2;
			}
			else
			{
				if (!string.Equals(a, "[LoadOrder]", StringComparison.OrdinalIgnoreCase))
				{
					continue;
				}
				int num = text2.IndexOf('=');
				if (num >= 0 && text2.Substring(0, num).EndsWith("Directory", StringComparison.OrdinalIgnoreCase))
				{
					string[] array = text2.Substring(num + 1).Split(',');
					bool result;
					if (array.Length == 2 && string.Equals(array[0].Trim(), folder, StringComparison.OrdinalIgnoreCase))
					{
						return bool.TryParse(array[1].Trim(), out result) && result;
					}
				}
			}
		}
		return false;
	}

	internal static bool OptionEnabled(string[] lines, string option)
	{
		string a = string.Empty;
		foreach (string text in lines)
		{
			string text2 = text.Trim();
			if (text2.StartsWith("["))
			{
				a = text2;
				continue;
			}
			int num = text2.IndexOf('=');
			if (string.Equals(a, "[Runtime]", StringComparison.OrdinalIgnoreCase) && num >= 0 && string.Equals(text2.Substring(0, num).Trim(), option, StringComparison.OrdinalIgnoreCase))
			{
				return text2.Substring(num + 1).Trim() == "1";
			}
		}
		return false;
	}

	internal static string TextOption(string[] lines, string option, string fallback)
	{
		string a = string.Empty;
		foreach (string text in lines)
		{
			string text2 = text.Trim();
			if (text2.StartsWith("["))
			{
				a = text2;
				continue;
			}
			int num = text2.IndexOf('=');
			if (string.Equals(a, "[Runtime]", StringComparison.OrdinalIgnoreCase) && num >= 0 && string.Equals(text2.Substring(0, num).Trim(), option, StringComparison.OrdinalIgnoreCase))
			{
				return text2.Substring(num + 1).Trim();
			}
		}
		return fallback;
	}
}
