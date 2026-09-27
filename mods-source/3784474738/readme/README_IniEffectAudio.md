# INI effect audio (MultiStageMissiles 1.7.1)

Add an audio section to the **particle effect .ini**, alongside [Main], [Emission], etc. This works for effects created by the native INI particle factory, including hit/explosion effects, exhausts and subemitters. No missile staging keys are required.

The installed CustomAudioLoader loads custom PCM 16-bit WAV files through the normal game resource API. Put a file such as audio/effects/my_explosion.wav inside an enabled mod and use its mod-relative path, including .wav. Use mono for a point source. Built-in game audio resource names also work. Restart the game after changing cached effect INIs.

~~~ini
[Audio]
Clip=audio/effects/my_explosion.wav
Volume=0.8
MinDistance=50
MaxDistance=5000
Loop=False
Delay=0
FinishOnStop=True
~~~

The example filename is a placeholder: supply your own WAV. Each effect instance plays its own sound. Native sounds are not muted or replaced, so do not add the same sound twice through other effect settings.

| Key | Default | Meaning |
|---|---|---|
| Clip | empty | Game audio resource or custom WAV path. An empty/missing value disables the layer. |
| Volume | 1 | Gain from 0 to 1, before the game's SFX/master volume. |
| MinDistance | 20 | Metres from the listener/camera within which the sound has full configured volume; positive. |
| MaxDistance | 2000 | Metres where volume reaches zero; greater than MinDistance, up to 1,000,000. |
| Loop | False | Repeat while this particle system emits. |
| Trigger | Emission | Emission waits for this system's first live particle, including particle start delays. Play starts when the system is playing, useful for an empty carrier emitter. |
| Delay | 0 | Additional mission seconds after the trigger, 0..3600. Pending sound is cancelled when the effect ends. |
| Pitch | 1 | Playback pitch/speed, 0.1..3. Independent of game time acceleration; no Doppler shift. |
| FadeIn | 0 | Fade in over 0..60 playback seconds. |
| FadeOut | 0.15 | Fade out over 0..60 playback seconds when stopped with the effect. |
| FinishOnStop | True | Let a non-looping clip finish at the effect's last position after the effect ends. False fades it out instead. Loops always stop. |

Attenuation is linear between MinDistance and MaxDistance; there is no sound beyond MaxDistance. Distances are metres, independent of the visual effect's scale. They are camera/listener distances, not sensor detection ranges.

For a continuous jet:

~~~ini
[Audio]
Clip=audio/effects/my_jet.wav
Volume=0.6
MinDistance=10
MaxDistance=1500
Loop=True
FadeIn=0.2
FadeOut=0.4
~~~

For layers, use [Audio1] through [Audio8], each with the same keys. Gaps are allowed. [Audio], if present, is an additional layer. For example, an initial crack and a delayed rumble can use different clips, Delay and MaxDistance.

Place audio on the main effect when it should play once per explosion. A subemitter's Emission trigger fires once per activation, not once per emitted particle. A loop stops when its own particle system stops emitting, even if smoke particles remain visible.

Audio pauses with the game. Delay follows mission time; clip playback, FadeIn and FadeOut use playback seconds so fast-forward does not raise the pitch. There is no automatic sound-propagation delay or terrain occlusion. Audio playback positions are transient and not restored from save files.

Missing clips or invalid audio values produce a bounded [IniEffectAudio] warning and skip only that sound layer. No audio is played while caching the source prefab. Sounds use the existing scene SFX mixer; the feature does not create an audio manager in the main menu.

Set Debug=True in an audio section for bounded prefab/instance and playback diagnostics, including source signal level, mixer volume and listener distance. Remove it or use False after troubleshooting.
