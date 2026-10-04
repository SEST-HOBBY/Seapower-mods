R10.35 torpedo tube animation and launch alignment test

Located the existing triple launchers in the aft side recesses beneath the boat bays. Separated 1,716 original cover faces into six independently hinged covers; retained existing UVs and materials. Added dark inner tube sleeves. Upper covers swing up and lower covers down, each opening/closing in 1.2 seconds. Hinge motion is a model-informed approximation; not a surveyed HOS-303 mechanism.

Moved the complete tube clusters 25 cm aft within the existing openings after a 324mm diameter clearance check found the forward jamb obstructed the forward-most torpedo on each side. Hull opening and recess geometry are unchanged. Covers, bores, and launch origins all use the same adjusted tube coordinates. The modeled tube axes are approximately +/-41.069 degrees from the bow.

Each launcher now has three native tube containers, with one attachment per container, its own muzzle position, fixed yaw, and open/close hatch references. Native fixed-container torpedo orientation follows the Baleares configuration; torpedo hatch hooks follow Delfin. MK32 reload timing (300 seconds) and magazine ammunition/capacity (12 Mk54 ship torpedoes) retained. Launcher damage colliders moved from amidships to the actual aft mounts; shared magazine damage region moved aft. Exact real magazine geometry is not known.

Checks passed: valid OBJ indices; original texture/UV/normal preservation; all unaffected model groups unchanged; closed covers reconstruct their original shape at adjusted positions; correct references for all six hatch animations; unchanged VLS/radar/sonar/aircraft/CIWS/crane/flag/rigging and class variants. 17 rays per tube sample the 324mm diameter launch envelope for 20 metres, all clear of the assembled geometry with covers open. Closed/open previews inspected on both sides. This does not simulate ballistic drop, fins, game collision logic or runtime firing order.

In-game test required: order three torpedo launches to a port-side target and three to starboard; verify the matching cover opens and each torpedo emerges from its tube, then enters the water. Check reload/close behavior. Both Hyuga and Ise share the fix. No live game verification performed.

Replace the previous DDH181_Hyuga_SeaPower_Config folder; do not merge. Retains R10.34 Hyūga Class with Hyūga and Ise named variants. No direct game installation performed.
