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

SEST's two other plugins share this folder:

  SEST.RuntimeFixes.dll    SEST Runtime Fixes 1.5.0. SEST_RUNTIME_README.txt
  SEST_RUNTIME_README.txt  says what it does; sest_runtime.ini turns its
  sest_runtime.ini         corrections off one at a time.
  SEST.ContactsFix.dll     SEST UI Follow-up 1.4.2, for players of Contact
                           Log: its window no longer opens or closes on the
                           time-control keys; its pop-out to a second
                           screen (with Pop-Out Windows) is corrected;
                           Group Manager gets a Stock UI / Enhanced UI
                           switch; the live F11 cost report reuses each
                           mission's price lists instead of rereading them
                           twice a second; Quick Load moves (below). It
                           writes timing lines to Player.log every 30
                           seconds. It works only beside this exact
                           SEST.RuntimeFixes.dll, Contact Log 1.0.1 and Sea
                           Power 0.8.7 (Build 261021); with anything else it
                           writes one "inactive" line to Player.log and
                           changes nothing.

Quick Load moves to Ctrl+F9 where SEST UI Follow-up is on. Each time the
game loads its key bindings, a Quick Load key of F9 alone (the game's
default) becomes Ctrl+F9; any other Quick Load key is kept. F9 alone then
no longer quick-loads. It opens Contacts only if you set Contact Log's key
to F9 yourself (ToggleWindow under [Input] in
BepInEx\config\com.seapower.contactlog.cfg); SETUP does not. Pressing
Accept in the game's Options saves Ctrl+F9 in the game's controls.ini, and
it stays there after the pack or Contact Log is removed: then set Quick Load
back to F9 in Options if you want it.
Source: integration/runtime-fixes/ and integration/ui-followup/
