SEST MENU BACKGROUND

What this folder does: it plays the SEST film behind Sea Power's main menu
in place of the game's own, and shows SEST photographs in place of every
other backdrop picture: loading screens, the scenario, campaign and Mod
Manager pages, and campaign and mission title pictures.

  SEST.MenuBackground.dll  the plugin. Anchor Chain (installed by SETUP)
                           starts it when the game starts.
  sest_menu.mp4            the film: eleven SEST Gallery photographs,
                           no text, darkened, looping, no sound.
  sest_menu.ini            Enabled=0 turns it all off; Backdrops=0 and
                           CampaignArt=0 put the game's pictures back;
                           Pictures=0 turns off the [SEST Pictures] lines
                           it writes to Player.log.
  MENU_CREDITS.txt         who took each photograph, and the licence.

Without Anchor Chain the plugin never runs and the menu is the game's own.
If the film cannot be played, the plugin puts the game's own film back.
Source: integration/menu-background/ in github.com/SEST-HOBBY/Seapower-mods
