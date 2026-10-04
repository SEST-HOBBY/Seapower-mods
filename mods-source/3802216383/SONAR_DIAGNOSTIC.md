R10.28 sonar ping clip fix

Hyuga and Ise referenced audio/environment/Sonar-LF. No stock vessel references that clip, and a byte-name scan of installed resources.assets found zero Sonar-LF occurrences and one Sonar-MF occurrence. The supplied Asahi and native Ticonderoga use audio/environment/Sonar-MF.
Changed only SonarAudioClip from Sonar-LF to Sonar-MF in both vessel configurations. Underwater-only audibility remains Below. No forced or continuous audio added. Sonar detection performance and all visual fixes retained.
Offline reference comparison, one-field vessel diff, unchanged sensor-definition check and ZIP integrity passed. In-game active ping playback remains to be tested. This addresses the missing clip reference; it does not establish that the separate contact-detection concern is resolved.
Replace the previous folder; do not merge. Test active sonar near the ship with the camera underwater, then turn active sonar off to check that pings stop. No direct game installation performed.
