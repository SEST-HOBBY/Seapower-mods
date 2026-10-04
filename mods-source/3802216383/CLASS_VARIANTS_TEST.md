R10.34 class variants test

Mission Editor: Japan > Vessels > Hyūga Class. Unit Name: Hyūga DDH-181 or Ise DDH-182. Service dates retained: 2009 and 2011 respectively; earlier scenario dates may filter the choices.

Uses one jmsdf_ddh_hyuga vessel definition and two native named variants. The redundant standalone Ise definition is removed from this package. Native HullnumberReference targets New_HullTexture and EmblemReference targets FlightDeck_Surface, replacing their main textures with the existing complete hull/deck textures for each ship. These reference slots are used for full identity textures; no UV repacking or texture resampling is involved. No AircraftEmblemTexture override is used.

Offline texture-difference/UV coverage check confirmed all differing identity pixels lie on the main hull and flight-deck surfaces. Hull-secondary and elevator surfaces do not sample differing pixels. Existing material properties, models, UVs, textures, weapons, animations, sensors, rigging, flag and equipment are unchanged. Both named variants retain the previous helicopter air group.

Offline configuration and preservation checks passed. In-game selector population and identity texture switching still need user testing: add both ships, check 181/182 hull and deck markings, then save and reload the mission.

Replace the previous DDH181_Hyuga_SeaPower_Config folder; do not merge, or the old standalone Ise entry will remain. Existing saved missions that use jmsdf_ddh_ise must have that unit reselected as Hyūga Class / Ise DDH-182. Existing Hyūga type identifier and Variant1 are retained. No direct game installation performed.
