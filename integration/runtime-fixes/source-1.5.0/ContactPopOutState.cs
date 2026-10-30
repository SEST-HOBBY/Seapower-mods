using System;
using System.IO;

namespace Sest.RuntimeFixes {
internal sealed class ContactPopOutState
{
	internal bool Detached;

	internal bool Writable = true;

	internal CostWindowState Placement = new CostWindowState
	{
		X = 24f,
		Y = 24f,
		Width = 1250f,
		Height = 426f,
		Positioned = true
	};

	internal string Encode()
	{
		return "SEST_CONTACTS_1\n" + ((!Detached) ? "0" : "1") + "\n" + Placement.Encode();
	}

	internal static ContactPopOutState Parse(string text)
	{
		ContactPopOutState contactPopOutState = new ContactPopOutState();
		if (string.IsNullOrWhiteSpace(text))
		{
			return contactPopOutState;
		}
		string[] array = text.Replace("\r", string.Empty).Trim().Split('\n');
		if (array.Length != 3 || array[0] != "SEST_CONTACTS_1" || (array[1] != "0" && array[1] != "1"))
		{
			contactPopOutState.Writable = false;
			return contactPopOutState;
		}
		CostWindowState costWindowState = CostWindowState.Parse(array[2]);
		if (!costWindowState.Positioned)
		{
			contactPopOutState.Writable = false;
			return contactPopOutState;
		}
		contactPopOutState.Detached = array[1] == "1";
		contactPopOutState.Placement = costWindowState;
		return contactPopOutState;
	}

	internal void Save(string path)
	{
		if (!Writable)
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
			string text = path + ".tmp";
			File.WriteAllText(text, Encode());
			if (File.Exists(path))
			{
				File.Replace(text, path, null);
			}
			else
			{
				File.Move(text, path);
			}
		}
		catch (Exception error)
		{
			Api.LogFailure("Contacts screen placement stays in memory", error);
		}
	}
}

}
