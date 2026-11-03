using System;

namespace Sest.RuntimeFixes;

internal sealed class UiStartupGate
{
	internal bool Ready { get; private set; }

	internal bool Failed { get; private set; }

	internal bool TryStart(bool initialized, bool attachedView, bool teardown, Action initialize)
	{
		if (teardown || !initialized)
		{
			return false;
		}
		if (Ready)
		{
			return true;
		}
		if (Failed || !attachedView)
		{
			return false;
		}
		try
		{
			initialize();
			Ready = true;
			return true;
		}
		catch
		{
			Failed = true;
			throw;
		}
	}
}
