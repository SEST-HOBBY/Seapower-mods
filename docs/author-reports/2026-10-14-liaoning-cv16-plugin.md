# PLAN Type 001 Aircraft Carrier Liaoning (3774859959): the ski-jump plugin throws on every helicopter on deck

Drafted 14 Oct 2026 for the SEST author to post on the mod's Workshop page. Not posted by the repo.

**Seen on:** Sea Power 0.8.5 Build 261008 (Steam build 25806545, Unity 6000.0.67f1), with the mod's `CV16.dll` as shipped: 30,720 bytes, SHA-256 `c592e4c118643e04a2a62314066dacfd1662fbd4ba8a64dfdcd4583082cd2940`, file version 1.0.0, dated 16 Aug 2026, loaded through Anchor Chain as `ACC CV16 Ski-Jump Fix (meltemi.acc.cv16.skijumpfix)`. The mod's `_info.ini` says ApproximateVersion=0.8.2.

**What happens.** With the carrier in a mission and a helicopter on her deck, `Player.log` fills with this exception, repeated every physics tick while a fixed-wing aircraft is in its take-off state:

```
ArgumentException: Field _isInFlight defined on type SeaPower.Aircraft is not a field on the target object which is of type SeaPower.Helicopter.
Parameter name: obj
  at System.Reflection.RuntimeFieldInfo.GetValue (System.Object obj)
  at meltemi.CV16.plugin.ForwardRunwayClearancePatch.IsClear (System.Object launchPoint)
  at meltemi.CV16.plugin.ForwardRunwayClearancePatch.PlaneTakeoffPrefix (System.Object __instance)
  at (wrapper dynamic-method) SeaPower.PlaneTakeOff.DMD<SeaPower.PlaneTakeOff::onFixedUpdate>(SeaPower.PlaneTakeOff)
  at SeaPower.StateMachine.OnFixedUpdate ()
```

In the SEST author's in-game check of 13 Oct 2026 the kept tail of the log (the last 4,000 of 6,080 lines) carried it 193 times. A session without the Liaoning (the playtest of 14 Oct) carried it 0 times.

The BepInEx log also shows a HarmonyX warning at load: `meltemi.acc.cv16.skijumpfix: You should only patch implemented methods/constructors to avoid issues. Patch the declared method void SeaPower.FlightDeckPoint::Release(SeaPower.ObjectBase occupyingObject) instead of ...`.

**Why (read from the stack, not the source).** `ForwardRunwayClearancePatch.IsClear` reads the private field `_isInFlight` of `SeaPower.Aircraft` by reflection from whatever object occupies a flight-deck point. A helicopter on the deck is a `SeaPower.Helicopter`, which is not an `Aircraft` and has no such field, so `FieldInfo.GetValue` throws. The prefix is on `PlaneTakeOff.onFixedUpdate`, so it throws again every tick. Whether the fixed-wing launch still completes when the prefix aborts is not seen.

**Fix.** Test the occupant's type before reading the field (`occupyingObject is Aircraft`, or `as Aircraft` and treat a helicopter as whatever clearance the design wants), and wrap the reflection in a try/catch so one odd occupant cannot stall the deck.

**What SEST does meanwhile.** Nothing; the SEST pack does not redistribute or modify the DLL. The Liaoning is not placed in any SEST mission.

---
Draft text for the Workshop comment:

> Hi, with 0.8.5 (Build 261008) and your plugin as shipped (CV16.dll 1.0.0, 16 Aug), Player.log fills with `ArgumentException: Field _isInFlight defined on type SeaPower.Aircraft is not a field on the target object which is of type SeaPower.Helicopter` from `ForwardRunwayClearancePatch.IsClear`, called by `PlaneTakeoffPrefix`, every physics tick while a helicopter sits on a deck point and a jet is taking off (193 times in the tail of one session's log). Looks like `IsClear` reads `Aircraft._isInFlight` by reflection from any occupant; a type check (`is Aircraft`) before the read, or a try/catch, would stop it. HarmonyX also warns at load about patching `FlightDeckPoint::Release` on the base rather than the declared method. Happy to send the full log.
