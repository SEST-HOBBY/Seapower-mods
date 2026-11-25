// Bridges for the Enhanced Decoy 0.5.4 image (AssemblyAdapters.EnhancedDecoy.cs)
// on 0.9.3-261123. The image was written for one chaff attacher and one
// ammunition per launcher; 261123 keeps a list of rounds, each with its own
// ammunition, attacher and decoy band. Both bridges pick the same round: the
// first one that covers the chaff band (Band Chaff or Both), else round 0.
using System;
using System.Collections;
using System.Reflection;
using SeaPower;

namespace AnchorChain;

public static partial class BetaCompatibilityCalls
{
    private static readonly FieldInfo ChaffRoundsField =
        typeof(WeaponSystemChaff).GetField("_rounds", BindingFlags.Instance | BindingFlags.NonPublic);
    private static readonly Type ChaffRoundType = ChaffRoundsField?.FieldType.GetGenericArguments()[0];
    private static readonly FieldInfo ChaffRoundAttacherField = ChaffRoundType?.GetField("Attacher");
    private static readonly FieldInfo ChaffRoundBandField = ChaffRoundType?.GetField("Band");

    // Stands in for a read of the retired WeaponSystemChaff._ammoInUse field.
    // RoundAmmo(Chaff) is the native first round whose band covers chaff;
    // _ammoInUse is the native round 0 getter (null with no rounds). A null
    // launcher throws NullReferenceException, as the field read did.
    public static Ammunition EnhancedDecoyChaffAmmo(WeaponSystemChaff system)
        => system.RoundAmmo(DecoyBand.Chaff) ?? system._ammoInUse;

    // Stands in for FieldInfo.GetValue(system) on the retired
    // WeaponSystemChaff._chaff field and ignores the FieldInfo: the attacher
    // of the same round (first with Band Chaff or Both, else round 0), or
    // null with no rounds. A null launcher throws, as GetValue(null) did.
    public static object EnhancedDecoyChaffAttacher(FieldInfo field, object system)
    {
        if (system == null) throw new TargetException("Non-static field requires a target.");
        var rounds = (IList)ChaffRoundsField.GetValue((WeaponSystemChaff)system);
        if (rounds == null || rounds.Count == 0) return null;
        foreach (object round in rounds) {
            var band = (DecoyBand)ChaffRoundBandField.GetValue(round);
            if (band == DecoyBand.Chaff || band == DecoyBand.Both) return ChaffRoundAttacherField.GetValue(round);
        }
        return ChaffRoundAttacherField.GetValue(rounds[0]);
    }
}
