Provided by CustomAudioLoader.dll. Use the Alarms option under Custom Audio Loader in AC Pack Settings and restart the game.

Naval alarm assignment
File: systems/AlarmAudioClip_Mapping.ini
Restart Sea Power after changes.
Priority: [US.Ship.Unit.MODEL] clip > matching year range > [US] clip.
MODEL is the exact vessel INI filename without .ini; operator nation still applies.
The narrowest matching year range wins. Unknown years use the national default.
To correct a variant/refit date, set ServiceEntryYear=1960 in its model section
without ShipAlarmAudioClip. Use the hull's service-entry year where known.
The native fallback is the loaded variant ServiceDate, not guaranteed hull build year.
Example:
[US.Ship.Unit.example_destroyer]
ServiceEntryYear=1960

US defaults: through 1964 Stromberg; from 1965 AN/SIA-114B.
1965 is a configurable approximation based on the dated AN/SIA-114B manual;
it is not evidence of a simultaneous fleet-wide change. Early/later refits need overrides.
Nimitz and Ford model exceptions use the remastered Nimitz General Alarm.
This is a sound proxy for the family, not a dated original recording for every hull.
US spoken sequence: recorded pipe and announcement, 0.5 s gap, 15 s alarm, 2 s pause,
then repeat the announcement and alarm once. Existing nation/year/model tones remain.
ShipAlarmRepeatCount counts extra rounds: 0 once, 1 twice, 2 three total, -1 unlimited.
ShipAlarmPauseSeconds is the gap AFTER a complete announcement + alarm round.
ShipAlarmDurationSeconds=0 plays the original tone length; positive seconds loop/trim it.
ShipAnnouncementGapSeconds is the gap between the full speech clip and tone.
ShipAnnouncementVolume is a relative multiplier (0..1) of Settings.Volume.
ShipAnnouncementAudioClip is the generic GQ voice; an empty value disables speech.
ShipMissileAnnouncementAudioClip is used only for a fresh hostile incoming missile
contact at the start of the formation episode. The selected reason is then retained.
New contacts do not restart a round. Configured finite spoken rounds finish even if
the threat clears; infinite repetitions stop after the existing quiet hold.
No speech configured: legacy current-threat gate and native tone duration remain.
A missing speech clip falls back to the generic voice or tone alone.
Speech/duration keys inherit nation -> selected sound profile. For a model-specific
speech override, include ShipAlarmAudioClip in that model profile as well.
Repeat count and round pause also inherit Settings. Other speech keys have the defaults
above (speech unset, volume 1, gap 0.5, tone duration 0).
Formations share rounds; the longest round and largest pause set the next start.
Pause freezes both source playback and sequence timing. Phase transitions run each frame;
contact checks retain CheckIntervalSeconds. ShipRearmQuietSeconds controls rearming.

US_Navy_GeneralQuarters.wav contains the recorded attention pipe, full synthetic
reference-style GQ announcement and recorded handset hang-up. The complete text includes
route of travel and material condition Zebra. _Missiles.wav adds the inbound missile
reason and is assigned by ShipMissileAnnouncementAudioClip.
Prepared but unassigned: _Aircraft.wav, _SurfaceShips.wav, _Submarines.wav and _Torpedoes.wav.
All six variants use the final reference-style voice set, short outdoor reverberation
and horn-loudspeaker processing, with matched loudness. Original recorded speech is
not inserted into the announcements. Restart the game to clear cached older clips.
Pipe reference: https://www.youtube.com/watch?v=TyVzeh7rHlM
Playback is local shipboard crew audio from a separate spatial source on the vessel.
It does not replace basegame player-facing voice lines, voice files or voice routing.
Pilothouse can process the owned speech and tone as own-ship announcements. Its manual
GQ command remains independently triggered; no shared GQ state is introduced here.

Source: https://www.policeinterceptor.com/navysounds.htm

Historical UK/Japan assignments and China proxy (2026-11-14):
UK: through 1959 Action Stations bugle; from 1960 existing Illustrious electronic alarm.
Royal Navy documents the bugle on larger warships into the 1950s. Applying this to
all eligible early ships and using 1960 as the boundary are gameplay approximations.
Centaur/Hermes/Albion model-family exceptions keep the bugle after later refits.
Japan: through 1979 traditional Take Your Stations bugle; from 1980 existing JMSDF alarm.
The 1980 boundary was explicitly selected by the user as an approximate game setting;
it is NOT a documented fleet-wide transition. Unknown dates retain the national default.
Takatsuki 1984 and Tachikaze-family model exceptions keep the traditional call.
Tachikaze is a class-wide approximation, including later Sawakaze; the current model
mapping cannot distinguish individual hull variants. No individual build year is invented.
The native year remains variant ServiceDate where no model exception is present.
Soviet/Russia/China: the same user-selected Soviet collector-bell proxy, not a verified
universal naval combat alarm and not an authentic Chinese recording.

Both new bugles are recorded performances, not wartime onboard recordings. Sources:
UK performance, lirbugler: https://www.youtube.com/watch?v=ElYTrdLu41k
Japan performance, Take Your Stations: https://www.youtube.com/watch?v=p_2q0GEYQ6o
UK historical evidence:
https://www.royalnavy.mod.uk/news/2021/april/18/20210418-action-stations
Existing modern UK: https://www.policeinterceptor.com/navysounds.htm
Existing modern Japan: https://www.youtube.com/watch?v=M-ROP3_KWXU
Bell: https://www.youtube.com/watch?v=asrKlWBpQhE

Audio: 48 kHz mono PCM16 WAV, complete calls with retained recorded reverberation,
gentle filtering, matched levels, short edge fades. No synthesized replacement tones.
Original recordings are not modified. No public redistribution clearance is asserted.
Cadence and camera-distance attenuation remain controlled by [Settings].
New assignment/asset checks are offline; restart and audition in game are still required.


Royal Navy announcements
The modern UK profile plays three general-alarm bursts, followed by the full
Action Stations announcement and its selected reason, once per alarm episode.
ShipAlarmFirst=True puts the tone before the announcement (default False).
ShipTorpedoAnnouncementAudioClip selects a full initial torpedo announcement.
A detected, fresh, hostile actual torpedo approaching and aimed at the protected
ship can select it. MOSS and other decoys do not count. With both missile and
torpedo reasons present, each ship tries torpedo, missile, then generic speech.
The selected reason is fixed when the sequence begins. New contacts do not
interrupt speech or create extra warning announcements during the episode.
Existing quiet-time rearming still applies; no new warning scheduler is added.

The AirThreat file currently uses the existing inbound-missile trigger.
Aircraft-specific triggering remains unimplemented, as with the prepared US
aircraft announcement. Other combat uses the generic Action Stations message.
The torpedo wording is a plain-language game approximation, not asserted as a
verified Royal Navy standard announcement. Historical UK bugle profiles retain
no modern NBCD announcement. ShipAlarmRepeatCount=0 means one complete sequence;
1 means two. US ordering and repetitions are unchanged.


Alarm loudness calibration (2026-11-15)
The runtime announcement set and mapped quiet alarm clips were raised toward
-13 LUFS integrated, with true peaks at or below -1 dBTP. Processing uses
constant gain and, only where required, an oversampled peak limiter. Clip
lengths, pipe and handset cues, recorded cadence and reverberation are retained.
Already louder Incoming_US and airfield loop files were not boosted; the
airfield release tail retains its original level relative to the loop.
[Settings] Volume is now 1 instead of 0.35 (removes 9.12 dB attenuation).
Camera-distance attenuation and Pilothouse processing still apply. These are
spatial Sfx sources, while native player-facing voices are non-spatial Voice
sources: equal file loudness is not a guarantee of equal level at a distance.
Comparison: 34 non-silent native US/UK samples, speaker medians -11.16,
-12.12 and -13.13 LUFS. Original voice files and all DLLs are untouched.
Full game restart required for cached clips and configuration. Verification
is offline asset/config analysis; in-game listening acceptance is pending.


German Navy profiles (2026-11-15)
Germany ships through 1989: Soviet_Ship_Bell.wav proxy, then the German-only
announcement "Besatzung auf Gefechtsstation!". Unknown dates use this same
conservative national default. The Bremen model explicitly retains this profile.
From 1990: German_Navy_GeneralAlarm.wav, then the German announcement. An
inbound-missile reason selects "Air Warning Red! Besatzung auf Gefechtsstation!".
Generic combat and torpedo reasons keep the German-only announcement.
There is no separate aircraft-attack trigger. The reason remains fixed for the
current alarm episode. Both profiles play once (ShipAlarmRepeatCount=0).

The 1990 boundary is user-selected, not a documented fleet-wide introduction.
The available game year is variant ServiceDate; this is not the mission year
or necessarily the true hull build year. Exact model overrides take precedence.
The new tone is reconstructed at approximately 900.8 Hz from the supplied
1.15-second Hamburg video excerpt: 10 seconds active, followed by a short
reverberation tail. That excerpt comes from a man-overboard scene, so its use
as the combat alarm is a game approximation. Speech and tone remain separate.
ShipAlarmDurationSeconds=0 preserves the complete tone and reverb; setting 10
would cut its tail. A 0.25-second gap follows before the announcement.

New files are mono 48 kHz PCM16 WAV, approximately -13 LUFS with peaks below
-1 dBTP. German synthetic voice with PA coloration and short reverberation.
Player-facing basegame voices are unchanged; camera attenuation, Alarms switch
and Pilothouse treatment continue through the existing CustomAudioLoader.
Phrase evidence: https://www.bundeswehr.de/de/auftrag/einsaetze/unifil-air-warning-red-korvette-gefecht-4912134
Model: https://huggingface.co/hvoss-techfak/F5-TTS-German (CC-BY-NC-4.0).
Full restart required. Asset and mapping checks are offline; no live audition.
