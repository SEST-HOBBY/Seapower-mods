// Bridge for the Z-21 Gun and EOTS Synchronization image
// (AssemblyAdapters.Z21GunMoveFire.cs) on 0.9.3-261123.
using SeaPower;

namespace AnchorChain;

public static partial class BetaCompatibilityCalls
{
    // Z-21: the weapon's container object, which 261123 keeps in the
    // system's WeaponParameters. Stands in for FieldInfo.GetValue(system)
    // and ignores the FieldInfo; a system without parameters gives null,
    // which the author's code already treats as "no gun".
    public static object WeaponContainerObject(System.Reflection.FieldInfo field, object weaponSystem)
    {
        WeaponParameters parameters = (weaponSystem as WeaponSystem)?._vwp;
        return parameters == null ? null : parameters._containerBaseObject;
    }
}
