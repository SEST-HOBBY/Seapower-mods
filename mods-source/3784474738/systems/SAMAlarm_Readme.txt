SAM alarm mapping
File: systems/AlarmAudioClip_Mapping.ini
Restart Sea Power after edits.
US default: US_SAM_Siren.wav. US.SAM.2005-2200: Incoming_US.wav.
The 2005 cutoff is a game preset for modern warning equipment, not a universal SAM retrofit date.
US PAC-3 site and standalone launcher have explicit Incoming_US.wav overrides.
Precedence: [NATION.SAM.Unit.MODEL] clip > narrowest NATION.SAM.FIRST-LAST > nation default.
MODEL is the exact unit INI stem. ServiceEntryYear in a model section without a clip overrides the native variant/refit date.
Example:
[US.SAM.Unit.usa_sam_site_pac-3_small]
IncomingAlarmAudioClip=audio/alarms/Incoming_US.wav

Siren: siren2001.wav by guitarguy1985, CC0-1.0.
https://freesound.org/people/guitarguy1985/sounds/87962/
https://creativecommons.org/publicdomain/zero/1.0/
Source is the public HQ MP3 preview, not the original WAV.
Processed: mono 48 kHz PCM16, excerpt, filters, loop crossfade and level normalization. Recorded outdoor ambience retained.
This is a generic US mechanical siren, not a verified original HAWK or Patriot alarm.

2.6.4: A fresh positioned local unit track now qualifies even without a shared
taskforce report. Stale/positionless contacts remain excluded. Temporary bounded
DiagnosticLogging is enabled in the alarm mapping for the current test mission.
