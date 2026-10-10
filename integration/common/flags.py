"""Enemy flags for the 2028 missions: the nation a hull or squadron file
registers, mapped onto the flag the side actually flies it under.

Why (6 Oct 2026): the player asked for the enemy in the south Indo-Pacific
missions to stop showing Iranian and other out-of-theatre flags. A mission
unit with no Nation= of its own takes the flag its unit file registers, and
the collection's modern Russian hulls, aircraft and batteries register
`Soviet` (the USSR flag, in 2028), while the fast attack craft, Shahed and
Sejjil launchers and the auxiliary the Meridian network operates register
`Iran`. The story has them Russian Federation and Meridian Maritime Group
respectively, so the builders and the mission pass set Nation= to say so:

  Soviet / USSR  -> Russia    the Russian Federation flag the collection's
                              flag table already carries (flag_russia2)
  Iran           -> Meridian  the Meridian Maritime Group's own flag, which
                              SEST Collection Fixes registers (ui/flag/sest/
                              meridian.png, nations.ini name)

Nothing else is remapped: a unit that registers China, Vietnam, Terrorists or
Pirates keeps it, and an explicit Nation= in the mission data always wins
(Sulu Line files the Meridian hulls under Panama on purpose: a flag of
convenience). Red Line, played from the Chinese bridge, puts the coalition
on the enemy side; none of its hulls register Soviet or Iran, so the rule
touches nothing there.
"""

FLAG_FOR = {"soviet": "Russia", "ussr": "Russia", "iran": "Meridian"}

# Units whose own flag says less than the story does, whatever their file
# registers: the Shahed and Sejjil launchers register Soviet in one copy and
# Iran in another and are the Meridian network's in every 2028 mission; the
# HY-4 coastal launcher registers Iran and is a Chinese battery.
UNIT_FLAGS = {"shahed_tel_black": "Meridian", "shahed_tel_white": "Meridian",
              "wp_sejjil_tel": "Meridian", "pla_hy-4_launcher": "China"}

# The nation the Collection Fixes flag table and nations.ini add for it.
MERIDIAN = ("Meridian", "Meridian Maritime Group", "meridian")


def flag_for(registered, uid=None):
    """The flag to set for unit `uid` that registers `registered`, or None
    to leave the unit's own."""
    if uid and uid.lower() in UNIT_FLAGS:
        return UNIT_FLAGS[uid.lower()]
    if not registered:
        return None
    return FLAG_FOR.get(registered.strip().lower())
