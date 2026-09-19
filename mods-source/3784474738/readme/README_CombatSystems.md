# Euromod CombatSystems – AC Pack, Version 1

54 neue CombatSystem-Profile und 139 Schiffszuordnungen. Die Definitionen orientieren sich an `original/systems/combatsystems.ini` und der installierten `Seapower-Scripts.dll`. Alle Zahlen sind Spielabstimmung relativ zum Basisspiel, keine realen Reaktionszeiten oder geheimen Leistungsangaben.

## Inhalt und Einbindung

- `systems/combatsystems.ini`: additive Profile mit eindeutigem `AC_`-Präfix.
- `vessels_overwrite/*_CombatSystems_OVWR.ini`: je Schiff ein natives `#!extend vessels/<name>.ini`, das genau einen CombatSystem-Verweis setzt.
- `language_overwrite/CombatSystems_systemgroups_OVWR.ini`: lesbare technische Systemnamen für alle neun vorhandenen Sprachdateien.
- [Vollständige Zuordnungsliste](CombatSystems_assignments.md), dazu `CombatSystems_assignments.json` mit Quellpfaden und Prüfsummen.

Abgedeckt sind die vorhandenen Pakete Modern US Navy/Burke Upload, Modern German Navy, Dutch Navy, Modern Italian Navy, JMSDF, Scandinavian Navy, Modern British Navy und Modern French Navy. Lokale Entwicklungskopien wurden bevorzugt und zusätzliche Schiffs-IDs aus ihren Workshop-Gegenstücken mit aufgenommen. Das Euromod-Hauptpaket liefert gemeinsam verwendete Sensoren und Waffen, aber keine eigenen `vessels`-Dateien. Andere Flottenpakete sowie separate Radar-Testschiffe gehören nicht zu dieser ersten Fassung.

Die Originalschiffe, Sensoren, Launcher, Munitionsdefinitionen und DLLs werden nicht verändert. Die Workshop-Perry MLU hatte bereits `AEGIS_Mk7`; dieser Verweis wird gezielt durch das eigene Perry-MLU-Profil ersetzt. Die lokale Perry besaß noch keinen CombatSystem-Verweis.

Das AC Pack muss aktiviert sein, ebenso das jeweilige Schiffspaket. Fehlende Zielschiffe werden durch die Erweiterungsdateien nicht neu angelegt. Die Systemdefinitionen werden virtuell zusammengeführt. Wegen der INI- und Modifier-Caches nach der Installation das Spiel neu starten; eine bereits laufende Mission wird durch das Ablegen nicht nachträglich aktualisiert. Die Mod-Ladereihenfolge wird nicht verändert.

## Aus der DLL abgeleitete Funktionsweise

Untersucht wurden insbesondere `CombatSystem.LoadFromInI`, `ObjectBaseLoader.LoadCombatSystems`, `ReactionTime`, `ObjectBase.TotalSolutionChannels`, `ObjectBase.LoadSignalProcessingOffset`, `SensorUtils.ReadAquisitionTime`, `Utils.openVirtualIniFile` und `IniHandler.ScanForModifierFiles`.

`CombatSystem.LoadFromInI` liest `SystemName` aus der Schiffsektion. Danach öffnet es die virtuelle Datei `systems/combatsystems.ini` und liest diese sechs Werte aus der gleichnamigen Systemsektion:

| Schlüssel | Tatsächliche Verwendung |
|---|---|
| `ReactionTime` | Reaktionsband; symbolische Werte werden über die Tabelle `TargetAquisitionTime` in `systems/sensors.ini` aufgelöst. Numerische Sekunden sind ebenfalls unterstützt. |
| `DatalinkTier` | Wird zur Laufzeit auf 0–5 begrenzt. Ab Tier 3 können fremde Tracks ausgewertet werden. Tier 6/7 erzeugt keine zusätzliche Fähigkeit. |
| `DatalinkSource` | Steuert, ob die Einheit als Datenlinkquelle genutzt werden darf; Sensor- und weitere Laufzeitbedingungen bleiben wirksam. |
| `SignalProcessingBonus` | Wird zum SignalProcessingOffset addiert und beeinflusst vorhandene Sensorverarbeitung; kein isolierter AEGIS-Leistungswert. Hier immer 0. |
| `CICSlots` | Kapazität des gehaltenen Lagebildes, mit Laufzeit-Untergrenze `2 * TotalSolutionChannels()`. |
| `EvaluationSlots` | Zahl gleichzeitig möglicher Orientierungs-/Bewertungsvorgänge; keine zusätzlichen Raketen- oder Beleuchtungskanäle. |

Das aktuelle Basisspiel setzt VerySlow=80, Slow=50, Medium=30, Fast=15 und VeryFast=7. Die Tabelle ist modifizierbar; die Profile verwenden bewusst dieselben symbolischen Werte. Das Reaktionsband ist nicht identisch mit der gesamten Zeit bis zum Schuss. Crew, gewählte Reaktions-/OODA-Optionen, Sensorerfassung, Waffen und Datenlink wirken zusätzlich. Die nominale Orientierungszeit entspricht `NewContactProcessTime * UnitBandSeconds / 15`.

Bei mehreren CombatSystems nimmt der Loader das schnellste positive Reaktionsband und jeweils die höchsten Datalink-/CIC-/Evaluation-Werte; SignalProcessing-Boni werden addiert und DatalinkSource wird logisch verodert. Deshalb wird hier genau ein Profil pro Schiff verwendet. Nationale `CombatSystem1_<Nation>`-Sektionen würden Vorrang vor `CombatSystem1` haben; in den erfassten Quelldateien wurden keine gefunden.

Das vorhandene `eu_AEGIS_BL5/9/10` ist ein Sensor mit RadioCommand-/Lenkkanälen. Es bleibt bestehen. Das neue `AC_AEGIS_BL5/9/10` ist der zusätzliche native CombatSystem-Verweis. Namensähnlichkeit allein macht diese beiden Systemarten nicht austauschbar.

## Abstimmung und Grenzen

| Beispiel | ReactionTime | CICSlots | EvaluationSlots | DatalinkTier |
|---|---|---:|---:|---:|
| Basisspiel AEGIS_Mk7 | VeryFast | 100 | 4 | 5 |
| AC_AEGIS_BL5 | VeryFast | 120 | 4 | 5 |
| AC_AEGIS_BL9 | VeryFast | 160 | 6 | 5 |
| AC_AEGIS_BL10 | VeryFast | 200 | 8 | 5 |
| AC_F124_CMS | VeryFast | 120 | 5 | 5 |
| AC_9LV_F123_MLU | VeryFast | 96 | 5 | 5 |
| AC_K130_CMS_B1 | Fast | 32 | 3 | 5 |
| AC_K130_CMS_B2 | Fast | 48 | 4 | 5 |

Die AEGIS-Zuordnung folgt vorrangig dem tatsächlich vorhandenen `eu_AEGIS_BL*`-Sensor, nicht allein der Jahreszahl im Dateinamen. Auch ältere, vom Mod pauschal als BL5 oder BL9 ausgestattete Varianten behalten diese Gruppierung. Ein BL9-Profil für eine Datei mit früher Jahreszahl ist daher keine Behauptung über den historischen Softwarestand jedes realen Schiffes. Für das frühe Arleigh-Konzept und die Spruances werden die vorhandenen Basisspielprofile AEGIS_Mk7 bzw. NTDS_TAS wiederverwendet.

CICSlots sind kein hartes Track-Limit: besonders `eu_GPS_Receiver`, taktische PCs und andere Mod-Lenksensoren können über ihre hohen TargetChannels eine erheblich größere Untergrenze erzwingen, sofern sie einem einsatzfähigen Waffensystem zugeordnet sind. Die gestaffelten EvaluationSlots bleiben deshalb ein wesentlicher Unterschied. Es werden weder die Sensor-Kanäle reduziert noch künstlich sehr große CIC-Zahlen vergeben, um diesen Mechanismus zu überholen.

MLU-, Zukunfts- und Konzeptprofile orientieren sich am im Mod dargestellten Ausrüstungsstand. Die Werte und teilweise die funktionalen Familienbezeichnungen sind ausdrücklich Annahmen für das Spiel. Kleine Boote und Hilfsschiffe erhalten ein lokales Lagebild. U-Boote erhalten drei generische Entwicklungsstufen mit lokalem Plot und ohne kontinuierliche Datenlinkveröffentlichung. Das ist eine konservative Spielabstraktion, keine Behauptung, dass reale U-Boote keine Datenfunkgeräte besitzen. Sonarleitfähigkeit und Torpedolenkung bleiben bei den vorhandenen Systemen.

Neue CombatSystems schaffen keine CEC-, BMD-, Suchradar-, Raketenlenk- oder Überhorizontfähigkeiten, die nicht bereits durch die übrigen Spieldaten vorhanden sind. Sie können auch die automatische Punkteberechnung beeinflussen: die DLL enthält einen `PointValueOodaScorer`, der die CombatSystem-Profile berücksichtigt.

## Quellen für Systemfamilien

Die Quellen belegen Systemfamilien und Integrationsrollen. Die INI-Zahlen stammen ausschließlich aus der oben erläuterten Spielabstimmung.

- [US Navy: AEGIS Weapon System](https://www.navy.mil/Resources/Fact-Files/Display-FactFiles/Article/2166739/aegis/aegis-weapon-system/) – Baseline 10 und SPY-6/Flight III.
- [US Navy: Mobile Bay Baseline 9](https://www.navy.mil/Press-Office/News-Stories/Article/2253467/uss-mobile-bay-tests-new-aegis-weapon-system/) – Beispiel einer BL9-Modernisierung.
- [ATLAS: ANCS](https://www.atlas-elektronik.com/solutions/surface-vessel-systems/ancsr.html) – F125 und skalierbares Combat Management.
- [Saab: 9LV CMS in Deutschland](https://www.saab.com/de/markets/germany/cms) und [9LV Naval Combat Systems](https://www.saab.com/contentassets/669f85167100453889741aff1fb6cd2d/9lv-naval-combat-systems.pdf) – deutsche Modernisierung und Visby-Familie.
- [Leonardo: IMDEX 2023](https://www.leonardo.com/documents/15646808/25561215/LDO_IMDEX_Pressnote_ENG_02_05.pdf?t=1683015581210) – ATHENA Mk2 und PPA.
- [Terma: C-Flex](https://www.terma.com/products/maritime/c-flex-light-combat/) – Iver Huitfeldt und skalierbare Führungsfunktionen.
- [BAE Systems: Combat Management Systems](https://www.baesystems.com/en-uk/product/combat-management-systems) – Royal-Navy-CMS-Familie und Plattformrollen; keine rückwirkende Gleichsetzung aller alten Fits mit dem aktuellen INTeACT.
- [Naval Group: Systems](https://www.naval-group.com/en/systems) und [Yearbook 2023–2024](https://www.naval-group.com/sites/default/files/2024-06/Yearbook%20Naval%20Group%202023-2024%20EN_0.pdf) – SETIS-Familie und Entwicklung aus dem FREMM-System.

## Prüfung

Die neuen INIs wurden mit den unveränderten Parser- und typisierten Lesemethoden der installierten DLL in einem isolierten Testprozess gelesen. Nur zwei Unity-Pfadabfragen im statischen Initialisierer wurden in einer reinen Speicherkopie ersetzt, weil die Unity-Engine im Testprozess nicht läuft. Es wurde keine veränderte DLL auf Platte geschrieben oder in das Spiel geladen. Der Test prüft 54 neue Profile, 139 Zuordnungen und alle sechs Feldtypen bzw. Systemreferenzen.

Zusätzlich werden Zielpfade, eindeutige Namen, Quellprüfsummen, ausschließlich zwei CombatSystem-Sektionen je Overlay, unveränderte übrige Schiffsdaten und Paketprüfsummen geprüft. Ein Gefechtstest im laufenden Spiel ist noch nicht erfolgt; die Zahlen sind eine erste abstimmbare Fassung.

Zum Rückbau ausschließlich die in `CombatSystems_files.json` genannten Dateien entfernen. Andere Inhalte des AC Packs bleiben bestehen. Entwicklungsdateien und IL-Auszüge liegen separat in `CustomSonarAudio/CombatSystemsWork`.
