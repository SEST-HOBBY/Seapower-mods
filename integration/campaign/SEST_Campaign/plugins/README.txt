SEST MENU BACKGROUND

What this folder does: it plays the SEST film behind Sea Power's main menu
in place of the game's own, and shows SEST photographs in place of every
other backdrop picture: loading screens and the backdrops behind the
scenario, campaign and Mod Manager pages. Scenario, campaign and briefing
pictures and maps stay as their authors made them.

  SEST.MenuBackground.dll  the plugin. Anchor Chain (installed by SETUP)
                           starts it when the game starts.
  sest_menu.mp4            the film: eleven SEST Gallery photographs,
                           no text, darkened, looping, no sound.
  sest_menu.ini            Enabled=0 turns it all off; Backdrops=0 puts
                           the game's backdrops back;
                           Pictures=0 turns off the [SEST Pictures] lines
                           it writes to Player.log; TileGuard=0 turns off
                           the campaign map's tile guard (below).
  MENU_CREDITS.txt         who took each photograph, and the licence.

It also guards the campaign map: after a mission, drawing a map tile while
the mission is still unloading can fail and bring up the game's error box.
The plugin skips that one tile instead.

Without Anchor Chain the plugin never runs and the menu is the game's own.
If the film cannot be played, the plugin puts the game's own film back.
Source: integration/menu-background/ in github.com/SEST-HOBBY/Seapower-mods
