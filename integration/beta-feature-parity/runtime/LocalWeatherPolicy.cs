using System;
using System.Collections.Generic;
using System.Globalization;

namespace Sest.RuntimeFixes;

// Local battle weather, the pure part (LocalWeatherView.cs does the game and
// DCM side): what the view layer manages, the hysteresis that decides when a
// change reaches the game, and the baseline the mission started with, which
// every save and the end of the battle get back. No game, Unity or DCM types,
// so tests/LocalWeatherTests.cs compiles this file in and runs all of it.
//
// Managed channels are the ones Trigger.TryActionTrigger (the mission
// triggers' Set Weather actions) sets mid-battle, in its order: sea state
// (Environment.setSeaState, which also sets the Ceto spectrum), wind direction
// (CloudsManager.set_CurrentWindDirection, then DynamicSky.ForceUpdate), rain,
// lightning, snow, fog. Clouds are managed only with LocalWeatherClouds=1
// (default off): Environment.changeCloudsCoverage(name), the call a trigger's
// Set Clouds makes, writes Session._missionClouds and rebuilds every cloud
// chunk, so the channel moves one DCM cover step at a time (never to or from
// "clear", which also gates the flags), at most once per CloudDwellSeconds;
// a save writes the baseline's cover with the plain Environment.setCloudsCoverage.
// Clouds is null in every ViewWeather when the channel is off.

// One weather state as the view layer manages it.
internal struct ViewWeather : IEquatable<ViewWeather>
{
    internal int SeaState;
    internal bool Rain, Fog, Lightning, Snow;
    // A CloudsManager.WindDirection name: N NE E SE S SW W NW (DCM's
    // WeatherSample.Points are the same eight).
    internal string Wind;
    // Cloud cover (a DCM BattleWeather.CloudCovers name, compared ignoring
    // case: Environment.CloudsCoverage holds it lower-cased); null when the
    // cloud channel is off.
    internal string Clouds;

    public bool Equals(ViewWeather o) =>
        SeaState == o.SeaState && Rain == o.Rain && Fog == o.Fog && Lightning == o.Lightning && Snow == o.Snow && string.Equals(Wind, o.Wind, StringComparison.Ordinal) &&
        string.Equals(Clouds, o.Clouds, StringComparison.OrdinalIgnoreCase);
    public override bool Equals(object obj) => obj is ViewWeather o && Equals(o);
    public override int GetHashCode() => SeaState * 31 + (Rain ? 1 : 0) + (Fog ? 2 : 0) + (Lightning ? 4 : 0) + (Snow ? 8 : 0) + (Wind?.GetHashCode() ?? 0) +
                                         (Clouds == null ? 0 : StringComparer.OrdinalIgnoreCase.GetHashCode(Clouds));

    // "SS7 rain thunder wind SW" ("SS3 dry wind NE" with no flags).
    public override string ToString()
    {
        var parts = new List<string> { "SS" + SeaState.ToString(CultureInfo.InvariantCulture) };
        if (Rain) parts.Add("rain");
        if (Lightning) parts.Add("thunder");
        if (Fog) parts.Add("fog");
        if (Snow) parts.Add("snow");
        if (!Rain && !Lightning && !Fog && !Snow) parts.Add("dry");
        parts.Add("wind " + (Wind ?? "?"));
        if (Clouds != null) parts.Add("clouds " + Clouds.ToLowerInvariant());
        return string.Join(" ", parts);
    }
}

internal enum ViewChannel { Sea, Wind, Rain, Lightning, Snow, Fog, Clouds }

// What the view point is: a surface unit or the free camera's focus, or an
// aircraft or helicopter (ObjectBase.IsAirUnit, attached camera) at a height.
internal enum ViewKind { Surface, Air }

// What one hysteresis step did.
internal sealed class ViewDecision
{
    internal ViewWeather Applied;
    internal readonly List<ViewChannel> Changed = new List<ViewChannel>();
    // Changes the target asks for that are not applied yet, with why:
    // "sea 3->9 confirming 2/5 s", "rain on: once per 20 s (12 s left)".
    internal readonly List<string> Held = new List<string>();
}

// Decides, every tick, which channels of the applied weather follow the
// target sampled at the view point. Times are real seconds (any monotonic
// clock). A change is applied only after the target has asked for it for
// ConfirmSeconds without a break (the view has stayed in the new weather),
// and a channel changes at most once per its dwell:
// - sea state: one Environment.setSeaState per SeaDwellSeconds, straight to
//   the sampled whole sea state (one new Ceto spectrum condition per change,
//   never a ramp); the target only has to stay on the same side of the
//   applied value, so a target moving 8, 9, 8 while 3 is applied still
//   confirms (and the latest value is applied);
// - wind direction: once per WindDwellSeconds (it re-keys the Ceto spectrum
//   through Ocean.windDir, as the sea state does);
// - rain, thunder, snow, fog: each at most once per FlagDwellSeconds.
internal sealed class LocalWeatherHysteresis
{
    internal const double ConfirmSeconds = 5;
    internal const double SeaDwellSeconds = 25;
    internal const double WindDwellSeconds = 25;
    internal const double FlagDwellSeconds = 20;
    internal const double CloudConfirmSeconds = 15;
    internal const double CloudDwellSeconds = 120;

    private sealed class Channel
    {
        internal double PendingSince = double.NaN;
        internal int PendingSign;        // sea: the side of the applied value the target is on
        internal string PendingValue;    // wind and flags: the value asked for
        internal double LastChange = double.NegativeInfinity;
        internal void Clear() { PendingSince = double.NaN; PendingSign = 0; PendingValue = null; }
    }

    private ViewWeather applied;
    private readonly Channel[] channels = new Channel[7];

    internal LocalWeatherHysteresis(ViewWeather start)
    {
        applied = start;
        for (int i = 0; i < channels.Length; i++) channels[i] = new Channel();
    }

    internal ViewWeather Applied => applied;

    // Something outside (a mission trigger) set the weather: start from it.
    // Pending changes are dropped; the dwell of each channel is kept.
    internal void Reset(ViewWeather now)
    {
        applied = now;
        foreach (var c in channels) c.Clear();
    }

    private static string S(double v) => Math.Max(0, v).ToString("0", CultureInfo.InvariantCulture);

    // True when a pending change on the channel may be applied now; else adds why not.
    private static bool Ready(Channel c, double now, double dwell, string what, ViewDecision d, double confirm = ConfirmSeconds)
    {
        double waited = now - c.PendingSince;
        if (waited < confirm)
        {
            d.Held.Add(what + " confirming " + S(waited) + "/" + S(confirm) + " s");
            return false;
        }
        double since = now - c.LastChange;
        if (since < dwell)
        {
            d.Held.Add(what + ": once per " + S(dwell) + " s (" + S(Math.Ceiling(dwell - since)) + " s left)");
            return false;
        }
        return true;
    }

    private bool Flag(ViewChannel which, bool current, bool target, double now, ViewDecision d, out bool result)
    {
        result = current;
        var c = channels[(int)which];
        if (current == target) { c.Clear(); return false; }
        string value = target ? "on" : "off";
        if (c.PendingValue != value) { c.PendingValue = value; c.PendingSince = now; }
        string name = which == ViewChannel.Lightning ? "thunder" : which.ToString().ToLowerInvariant();
        if (!Ready(c, now, FlagDwellSeconds, name + " " + value, d)) return false;
        c.Clear();
        c.LastChange = now;
        result = target;
        d.Changed.Add(which);
        return true;
    }

    internal ViewDecision Step(double now, ViewWeather target)
    {
        var d = new ViewDecision();
        var next = applied;

        var sea = channels[(int)ViewChannel.Sea];
        int sign = Math.Sign(target.SeaState - applied.SeaState);
        if (sign == 0) sea.Clear();
        else
        {
            if (sea.PendingSign != sign) { sea.PendingSign = sign; sea.PendingSince = now; }
            if (Ready(sea, now, SeaDwellSeconds, "sea " + applied.SeaState + "->" + target.SeaState, d))
            {
                sea.Clear();
                sea.LastChange = now;
                next.SeaState = target.SeaState;
                d.Changed.Add(ViewChannel.Sea);
            }
        }

        var wind = channels[(int)ViewChannel.Wind];
        if (target.Wind == null || string.Equals(target.Wind, applied.Wind, StringComparison.Ordinal)) wind.Clear();
        else
        {
            if (wind.PendingValue != target.Wind) { wind.PendingValue = target.Wind; wind.PendingSince = now; }
            if (Ready(wind, now, WindDwellSeconds, "wind " + applied.Wind + "->" + target.Wind, d))
            {
                wind.Clear();
                wind.LastChange = now;
                next.Wind = target.Wind;
                d.Changed.Add(ViewChannel.Wind);
            }
        }

        Flag(ViewChannel.Rain, applied.Rain, target.Rain, now, d, out next.Rain);
        Flag(ViewChannel.Lightning, applied.Lightning, target.Lightning, now, d, out next.Lightning);
        Flag(ViewChannel.Snow, applied.Snow, target.Snow, now, d, out next.Snow);
        Flag(ViewChannel.Fog, applied.Fog, target.Fog, now, d, out next.Fog);

        // Clouds: one CloudCovers step toward the target per change, never
        // to or from "clear"; null on either side (channel off) holds.
        var cloud = channels[(int)ViewChannel.Clouds];
        string step = LocalWeatherPolicy.CloudStep(applied.Clouds, target.Clouds);
        if (step == null) cloud.Clear();
        else
        {
            if (!string.Equals(cloud.PendingValue, step, StringComparison.OrdinalIgnoreCase)) { cloud.PendingValue = step; cloud.PendingSince = now; }
            if (Ready(cloud, now, CloudDwellSeconds, "clouds " + applied.Clouds + "->" + step, d, CloudConfirmSeconds))
            {
                cloud.Clear();
                cloud.LastChange = now;
                next.Clouds = step;
                d.Changed.Add(ViewChannel.Clouds);
            }
        }
        applied = next;
        d.Applied = next;
        return d;
    }
}

// The game side the controller drives (LocalWeatherView.GameWeather in the
// game; a recorder in the tests).
internal interface IViewWeatherTarget
{
    // The managed fields as the game holds them now.
    ViewWeather Read();
    // The visible change, with the setters Trigger.TryActionTrigger uses, for
    // the listed channels only.
    void Apply(ViewWeather w, IList<ViewChannel> changed);
    // The fields only, with the plain property setters (no Ceto spectrum, no
    // sky update): for the length of a save.
    void WriteFields(ViewWeather w);
}

// One battle's local weather: the baseline (the mission's own weather when
// the battle's view layer started, or what a mission trigger set since), the
// weather applied now, and the hysteresis between the sampled target and it.
internal sealed class LocalWeatherController
{
    private readonly IViewWeatherTarget env;
    private readonly LocalWeatherHysteresis hysteresis;
    internal ViewWeather Baseline, Applied;
    // Set by Tick when the game's weather was changed from outside since the
    // last tick (a mission trigger): which channels, and the new baseline.
    internal string External;
    // The last Apply threw partway (see Reconcile).
    private bool applyFailed;

    internal LocalWeatherController(IViewWeatherTarget target)
    {
        env = target;
        Baseline = Applied = env.Read();
        hysteresis = new LocalWeatherHysteresis(Applied);
    }

    internal static List<ViewChannel> Diff(ViewWeather a, ViewWeather b)
    {
        var d = new List<ViewChannel>();
        if (a.SeaState != b.SeaState) d.Add(ViewChannel.Sea);
        if (!string.Equals(a.Wind, b.Wind, StringComparison.Ordinal)) d.Add(ViewChannel.Wind);
        if (a.Rain != b.Rain) d.Add(ViewChannel.Rain);
        if (a.Lightning != b.Lightning) d.Add(ViewChannel.Lightning);
        if (a.Snow != b.Snow) d.Add(ViewChannel.Snow);
        if (a.Fog != b.Fog) d.Add(ViewChannel.Fog);
        if (!string.Equals(a.Clouds, b.Clouds, StringComparison.OrdinalIgnoreCase)) d.Add(ViewChannel.Clouds);
        return d;
    }

    // Fold what the game holds now into the baseline: every channel that
    // differs from what SEST last applied (a mission trigger set it), and
    // every channel in `triggered` whatever its value (a trigger that set a
    // channel to the value the view had already applied is still the
    // mission's weather; LocalWeatherView's Trigger.TryActionTrigger postfix
    // names those). Applied becomes what the game holds and the hysteresis
    // restarts from it. After an Apply that threw partway the differences are
    // SEST's own half-applied change, not a trigger's: they are taken as the
    // applied weather and never adopted. Sets External when it adopted
    // anything. Throws when the game cannot be read.
    internal void Reconcile(IEnumerable<ViewChannel> triggered = null)
    {
        External = null;
        var current = env.Read();
        if (applyFailed)
        {
            applyFailed = false;
            Applied = current;
            hysteresis.Reset(current);
            return;
        }
        var moved = Diff(Applied, current);
        if (triggered != null)
            foreach (var c in triggered)
                if (!moved.Contains(c)) moved.Add(c);
        if (moved.Count == 0) return;
        moved.Sort();
        // A channel the game no longer holds at what was applied, or one a
        // trigger set: that value is the mission's weather now.
        foreach (var c in moved)
            switch (c)
            {
                case ViewChannel.Sea: Baseline.SeaState = current.SeaState; break;
                case ViewChannel.Wind: Baseline.Wind = current.Wind; break;
                case ViewChannel.Rain: Baseline.Rain = current.Rain; break;
                case ViewChannel.Lightning: Baseline.Lightning = current.Lightning; break;
                case ViewChannel.Snow: Baseline.Snow = current.Snow; break;
                case ViewChannel.Fog: Baseline.Fog = current.Fog; break;
                case ViewChannel.Clouds: Baseline.Clouds = current.Clouds; break;
            }
        Applied = current;
        hysteresis.Reset(current);
        External = string.Join(", ", moved) + (triggered == null ? " changed outside (a mission trigger?)" : " set by a mission trigger") + "; baseline now " + Baseline;
    }

    internal ViewDecision Tick(double now, ViewWeather target)
    {
        Reconcile();
        string external = External;
        var d = hysteresis.Step(now, target);
        // The hysteresis has moved on: Applied is what the game should hold
        // from here, set before the setters run so that an exception in
        // them cannot leave it behind the game.
        Applied = d.Applied;
        if (d.Changed.Count > 0)
        {
            try { env.Apply(d.Applied, d.Changed); }
            catch
            {
                // Some setters may have run: Applied is what the game holds
                // (when it can still be read), and the next Reconcile does not
                // take the half-applied channels for a trigger's.
                applyFailed = true;
                try { Applied = env.Read(); } catch { }
                throw;
            }
        }
        External = external;
        return d;
    }

    // Prefix on the save: the file gets the baseline. Changes since the last
    // tick (a trigger within the 2 s before the save) are adopted first, and
    // the fields are swapped when what the game holds is not the baseline.
    // True when they were swapped (AfterSave puts the view weather back).
    // When the game cannot be read the baseline is written anyway.
    internal bool BeforeSave(IEnumerable<ViewChannel> triggered = null)
    {
        ViewWeather held;
        try { Reconcile(triggered); held = Applied; }
        catch { env.WriteFields(Baseline); return true; }
        if (held.Equals(Baseline)) return false;
        env.WriteFields(Baseline);
        return true;
    }

    internal void AfterSave(bool swapped)
    {
        if (swapped) env.WriteFields(Applied);
    }

    // The end of the battle (or a stop): the baseline, visibly. Changes since
    // the last tick are adopted first; then every channel the game holds
    // away from the baseline is put back (diffed against env.Read(), not the
    // cached Applied, so a half-failed Apply is undone too; every channel
    // when the game cannot be read). The channels put back, none when the
    // game already held the baseline.
    internal List<ViewChannel> Restore(IEnumerable<ViewChannel> triggered = null)
    {
        List<ViewChannel> changed;
        try { Reconcile(triggered); changed = Diff(env.Read(), Baseline); }
        catch
        {
            changed = new List<ViewChannel> { ViewChannel.Sea, ViewChannel.Wind, ViewChannel.Rain, ViewChannel.Lightning, ViewChannel.Snow, ViewChannel.Fog };
            if (Baseline.Clouds != null) changed.Add(ViewChannel.Clouds);
        }
        Applied = Baseline;
        if (changed.Count > 0) env.Apply(Baseline, changed);
        return changed;
    }
}

internal static class LocalWeatherPolicy
{
    internal static readonly string[] WindPoints = { "N", "NE", "E", "SE", "S", "SW", "W", "NW" };
    // DCM 1.0.4 BattleWeather.CloudCovers, in order (LocalWeatherTests checks
    // the DCM array; the game's clouds.ini sections and
    // MissionEditorViewModel.WeatherState_ME carry the same names).
    internal static readonly string[] CloudCovers = { "Clear", "Scattered", "Scattered_1", "Scattered_2", "Broken", "Broken_2", "Broken_3", "Overcast" };

    // The next cover from `applied` toward `target`, one step; null when
    // there is nothing to do: either is null or unknown, they are the same,
    // or either is "clear" (clear gates the weather flags, and the game
    // skips Weather= under it).
    internal static string CloudStep(string applied, string target)
    {
        int a = CloudIndex(applied), t = CloudIndex(target);
        if (a <= 0 || t <= 0 || a == t) return null;
        return CloudCovers[a + Math.Sign(t - a)];
    }

    internal static int CloudIndex(string name)
    {
        if (name == null) return -1;
        for (int i = 0; i < CloudCovers.Length; i++)
            if (string.Equals(CloudCovers[i], name.Trim(), StringComparison.OrdinalIgnoreCase)) return i;
        return -1;
    }
    // DCM keys its weather snapshots by the exact second (WeatherModel.Sane,
    // SnapshotAt) and keeps 24: the view samples at this battle-time step, so
    // a battle adds one snapshot per step, not one per sample. The steps are
    // anchored at the exact Engagement.At (start + k * 10 min), so step 0 is
    // the very time DCM wrote the battle's [Environment] from (Battles.WeatherOf):
    // at the battle centre at the start the view samples the written weather.
    internal const int SampleMinutes = 10;

    internal static DateTime SampleTime(DateTime start, DateTime utc)
    {
        long step = TimeSpan.TicksPerMinute * SampleMinutes;
        long since = Math.Max(0, utc.Ticks - start.Ticks);
        return new DateTime(start.Ticks + since - since % step, DateTimeKind.Utc);
    }

    // The view target from one DCM BattleWeather (the same ToBattle the
    // battle's [Environment] is written from), the way the game reads an
    // [Environment] Weather= line (SceneCreator.setWeatherConditions): Rain ->
    // IsRaining, Thunderstorm -> IsLightning, Snow -> IsSnowing, Fog -> IsFog,
    // and none of them while the clouds are "clear" (the game skips the
    // Weather line then, and CameraManager.updateWeatherEffects draws no
    // rain under a clear sky). Clouds are the battle's own (held). A wind
    // point the game has no name for keeps the baseline wind. clouds: DCM's
    // BattleWeather.Clouds, used only when the cloud channel is on (the
    // baseline carries a cover); heldClouds is then the cover applied now.
    internal static ViewWeather Target(int seaState, bool rain, bool thunder, bool snow, bool fog, string windFrom, string heldClouds, ViewWeather baseline, string clouds = null)
    {
        bool clear = string.Equals((heldClouds ?? "").Trim(), "clear", StringComparison.OrdinalIgnoreCase);
        return new ViewWeather
        {
            SeaState = Math.Max(0, Math.Min(12, seaState)),
            Rain = rain && !clear,
            Lightning = thunder && !clear,
            Snow = snow && !clear,
            Fog = fog && !clear,
            Wind = Array.IndexOf(WindPoints, windFrom) >= 0 ? windFrom : baseline.Wind,
            // Only when the channel is on (the baseline then carries a cover).
            Clouds = baseline.Clouds == null ? null : (CloudIndex(clouds) >= 0 ? clouds : baseline.Clouds),
        };
    }

    // Altitude rules for an aircraft view (LocalWeatherAircraft=1). The game
    // holds one weather, and already fades rain/snow by the camera's height
    // against the cloud layer (CameraManager.updateWeatherEffects) and
    // judges visual ranges against it (ModifyVisualIdentificationRangeByEnvironmentalConditions),
    // so an aircraft view samples the weather under it like a ship, except:
    // - sea state is held above airSeaMaxM (the waves are barely drawn from
    //   there, and a jet sweeping 8 nm a minute would re-key every ship's
    //   sea through one global Ceto spectrum);
    // - fog (a surface layer) is held above fogTopM (the cloud layer's end
    //   height; 300 m when the game's cloud parameters cannot be read).
    // Holding means the target takes the applied value, so nothing changes
    // on that channel until the view is low again or on a ship. `held` gets why.
    internal static ViewWeather ForView(ViewWeather target, ViewWeather applied, ViewKind kind, double heightM, double fogTopM, double airSeaMaxM, List<string> held)
    {
        if (kind != ViewKind.Air || double.IsNaN(heightM)) return target;
        string at = heightM.ToString("0", CultureInfo.InvariantCulture) + " m";
        if (heightM > airSeaMaxM && target.SeaState != applied.SeaState)
        {
            held?.Add("sea " + applied.SeaState + "->" + target.SeaState + " held: aircraft at " + at + " (above " + airSeaMaxM.ToString("0", CultureInfo.InvariantCulture) + " m)");
            target.SeaState = applied.SeaState;
        }
        double top = double.IsNaN(fogTopM) || fogTopM <= 0 ? DefaultFogTopM : fogTopM;
        if (heightM > top && target.Fog != applied.Fog)
        {
            held?.Add("fog " + (target.Fog ? "on" : "off") + " held: aircraft at " + at + " (above the " + top.ToString("0", CultureInfo.InvariantCulture) + " m fog top)");
            target.Fog = applied.Fog;
        }
        return target;
    }
    internal const double DefaultFogTopM = 300;

    // What the view does with this battle at this tick. Wait: no DCM
    // weather model yet and no view running (one line, nothing changed).
    internal enum GateResult { Run, Quiet, End, Wait }

    // allBattles: LocalWeatherAllBattles=1 (every DCM battle whose written
    // weather is the model's own, DCM's own weather when the campaign has no
    // placed storms); hasModel: WorldStorms.BattleModel found a model;
    // hasPlaced: the model carries placed storms now; placedAtStart: the
    // running view started with placed storms (null when no view runs). A
    // running view ends (baseline restored) when the model goes, or when it
    // started on placed storms and they go (the battle's [Environment] was
    // written with them); one started on DCM's own weather keeps running.
    internal static GateResult Gate(bool allBattles, bool hasModel, bool hasPlaced, bool? placedAtStart)
    {
        if (!hasModel) return placedAtStart != null ? GateResult.End : GateResult.Wait;
        if (placedAtStart == true && !hasPlaced) return GateResult.End;
        if (placedAtStart != null) return GateResult.Run;
        return hasPlaced || allBattles ? GateResult.Run : GateResult.Quiet;
    }

    // Above this height an attached unit is airborne whatever its type (a
    // missile, bomb or shell the camera follows: ObjectBase.IsAirUnit is only
    // Aircraft or Helicopter); a ship is near 0 m, a submarine below it.
    internal const double AirborneMinM = 100;

    // The view kind of an attached unit: Air for an Aircraft or Helicopter
    // (any height: a helicopter at 120 m still gets ForView, which leaves it
    // like a ship below the fog top and AirSeaMaxM) or anything above
    // AirborneMinM; else Surface. A NaN height is Surface.
    internal static ViewKind KindOf(bool isAirUnit, double heightM) =>
        isAirUnit || (!double.IsNaN(heightM) && heightM > AirborneMinM) ? ViewKind.Air : ViewKind.Surface;
}

// The [Runtime] switches of the local battle weather (README "Local battle
// weather"), parsed once; a bad value takes the default and is reported once.
internal sealed class LocalWeatherOptions
{
    internal bool AllBattles = true, Aircraft = true, Clouds;
    internal double AirSeaMaxM = 1500;
    internal bool FollowCentre;
    internal readonly List<string> Bad = new List<string>();

    // option(name, fallback): Policy.TextOption over the ini lines.
    internal static LocalWeatherOptions Parse(Func<string, string, string> option)
    {
        var o = new LocalWeatherOptions();
        bool Flag(string name, bool def)
        {
            string v = (option(name, def ? "1" : "0") ?? "").Trim();
            if (v == "1") return true;
            if (v == "0") return false;
            o.Bad.Add(name + "=" + v + " (0 or 1; " + (def ? "1" : "0") + " used)");
            return def;
        }
        o.AllBattles = Flag("LocalWeatherAllBattles", true);
        o.Aircraft = Flag("LocalWeatherAircraft", true);
        o.Clouds = Flag("LocalWeatherClouds", false);
        string m = (option("LocalWeatherAirSeaMaxM", "1500") ?? "").Trim();
        if (double.TryParse(m, NumberStyles.Float, CultureInfo.InvariantCulture, out double metres) && metres >= 0 && metres <= 20000) o.AirSeaMaxM = metres;
        else o.Bad.Add("LocalWeatherAirSeaMaxM=" + m + " (0..20000 m; 1500 used)");
        string f = (option("LocalWeatherFollow", "view") ?? "").Trim().ToLowerInvariant();
        if (f == "centre" || f == "center") o.FollowCentre = true;
        else if (f != "view") o.Bad.Add("LocalWeatherFollow=" + f + " (view or centre; view used)");
        return o;
    }

    public override string ToString() =>
        (AllBattles ? "every Dynamic Campaign Mod battle" : "battles of campaigns with placed storms") + ", following the " + (FollowCentre ? "battle centre" : "view") +
        (Aircraft ? ", aircraft views hold the sea above " + AirSeaMaxM.ToString("0", CultureInfo.InvariantCulture) + " m and fog above the fog top" : "") +
        (Clouds ? ", clouds follow (one step per " + LocalWeatherHysteresis.CloudDwellSeconds.ToString("0", CultureInfo.InvariantCulture) + " s)" : ", clouds held");
}

// Battle geometry the diagnostics print. Inside a battle the game's geo and
// DCM's are the same numbers: DCM's MissionWriter.Point writes a unit's
// position as (lon - centre lon) * 60, (lat - centre lat) * 60 nm from
// MapCenter, and the game reads that back flat at 60 nm per degree on both
// axes (Utils.RelativeNMToGeo: nm * 27.5594959 Unity units, then
// GeoPosFromRelativeOffset: / 1653.5697936 units per degree), with no
// cos(latitude). LocalWeatherTests checks both constants in the IL.
internal static class LocalWeatherGeo
{
    internal const double NmPerDegree = 60;

    // East and north nm from the battle centre, on the game's flat battle frame.
    internal static void OffsetNm(double centreLat, double centreLon, double lat, double lon, out double eastNm, out double northNm)
    {
        eastNm = StormMapGeometry.NormalLon(lon - centreLon) * NmPerDegree;
        northNm = (lat - centreLat) * NmPerDegree;
    }

    internal static void FromOffsetNm(double centreLat, double centreLon, double eastNm, double northNm, out double lat, out double lon)
    {
        lat = centreLat + northNm / NmPerDegree;
        lon = StormMapGeometry.NormalLon(centreLon + eastNm / NmPerDegree);
    }
}
