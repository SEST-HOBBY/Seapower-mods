R10.36 paired stern towed-decoy test

The existing two flared outlets are already positioned in the correct general reference-photo location: low on the port side of the transom, beneath the aft CIWS. Retained their mesh placement and the adjacent hatch clearance. Exact real-world coordinates are not established from the photograph.

Both outlets now have native DecoySystem entries. Each cable attachment is centered on its measured modeled bore, just aft of the rolled lip. Stowed positions are moved 3 metres forward of the local transom, inside the hull, instead of leaving the stowed body at the opening. The engine handles deployment, cable payout, trailing behavior and retraction; fixed collars do not rotate or require hinge animations. No additional visible doors are supported by the reference photo.

Uses the existing Euromod SLQ-25A Nixie asset as a gameplay stand-in for the Japanese system. It is not a claim that Hyuga carries US Nixie hardware. Preserves the previous 579m cable setting, 50ft depth, 3m/s retraction, sink setting and 5-25 knot deployment limits. These are existing gameplay values, not verified Hyuga specifications. Adds a second functional decoy to match the paired outlets. The separate expendable noisemaker system is unchanged.

Reference: https://wporep.com/jmsdf/ddh-181/ (firsthand ship visit; photograph identifies the paired stern openings as anti-torpedo decoy outlets).

Checks passed: 64-point bore-ring measurements for each opening, attachment centering, valid referenced Euromod decoy file, unchanged geometry/materials/textures, unchanged torpedo/VLS/CIWS/radar/sonar/flag/rigging/equipment and named class variants. Only the DecoySystems configuration changed among existing runtime files. Native deployment has not been verified in-game.

Test underway at 10-15 knots: deploy the towed decoy(s), inspect both outlet/cable attachments and confirm that retraction draws the bodies back into the stern without floating beside it. Check during gentle turns. Both Hyuga and Ise use this configuration.

Replace the previous DDH181_Hyuga_SeaPower_Config folder; do not merge. No direct game installation performed.
