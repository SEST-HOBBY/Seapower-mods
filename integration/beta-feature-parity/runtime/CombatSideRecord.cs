namespace Sest.RuntimeFixes;

internal sealed class CombatSideRecord
{
	internal string Name;

	internal InventoryLedger Spent = new InventoryLedger();

	internal InventoryLedger Platforms = new InventoryLedger();

	internal InventoryLedger Stores = new InventoryLedger();
}
