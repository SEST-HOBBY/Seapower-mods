ExtendedGuidance 0.10.28 - remote target information

HasDataLink on native sensors controls taskforce sharing. EG consumes only eligible measured observations already in the receiving taskforce plot; submerged/local-only restrictions remain native. DatalinkGuidance describes a missile uplink and is separate. No new INI key is required.

ARH/IR launch and midcourse support may use a remote ranged track. Local sensor assignments remain strict; remote measurements do not authorize another local sensor, foreign uplink or foreign terminal director. Explicit TrackSource selection remains binding.

DL support requires a compatible assigned own transmitter and available channels. Command modes retain their actual missile-tracking requirement. Without midcourse updates, remote launch requires TargetRequired=False, InertialGuidance=True and a bounded predicted seeker capture area. No continuing target updates are invented.

SARH remote launch requires a compatible own illuminator with a plausible signal/geometry forecast at illumination start and interception. Planning includes slew, acquisition and update time plus 2 seconds reserve. Current channels must be available; this is not a guaranteed future reservation. Actual terminal illumination is still required. An illumination-only connection cannot deliver midcourse target updates.

The forecast uses measured target motion and a bounded constant-speed estimate; native launch/kinematic limits remain. It is not a detailed CEC network protocol/latency model. Two position observations are required; timestamps and covariance are retained. Stale/ESM-only contacts cannot open the remote launch path.

Validated offline against current public and stable fixtures. In-game acceptance remains pending.
