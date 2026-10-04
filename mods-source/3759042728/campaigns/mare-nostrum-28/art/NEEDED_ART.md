# Arte pendiente — Mare Nostrum '28

Los siguientes archivos son PLACEHOLDERS (copiados de Pacific Strike). Sustituir por
arte propio manteniendo el MISMO nombre de archivo y formato PNG.

| Archivo | Uso | Ideal |
|---------|-----|-------|
| `00_campaign_background.png` | (pendiente crear) fondo de campaña | mapa del Mediterráneo 2028 / flota europea. Ahora se usa mn28_intro_map.png como fondo |
| ~~`mn28_intro_map.png`~~ | Prólogo slide 1 "El Fin del Paraguas" | ✅ HECHO (arte propio del usuario) |
| ~~`mn28_greenmarch.png`~~ | Prólogo slide 2 "La Nueva Marcha Verde" | ✅ HECHO (arte propio del usuario) |
| ~~`mn28_command.jpg`~~ | Prólogo slide 3 "El Mando" | ✅ HECHO (arte propio del usuario) |
| `bkg_tile_message.png` | mosaico del evento en el timeline | icono/tile de comunicado |
| `mn28_01_sheet.png` | ficha de la Misión 1 (Aguas Turbias) | escena de fragata F-100 en el Alborán |
| `mn28_act2_a.png` | Interludio Acto II slide 1 (ahora reusa mn28_intro_map.png) | Francia+Italia se unen: CdG + Cavour/Garibaldi, banderas europeas |
| `mn28_act2_b.png` | Interludio Acto II slide 2 (ahora reusa mn28_04_sheet.png) | Mediterráneo central, ofensiva, sombra rusa al este |

## Pendiente por misión/acto (según se vayan creando)
- Ficha por misión: `mn28_02_sheet.png` ... `mn28_10_sheet.png`
- Imágenes de eventos de acto (noticias del embargo, sitreps, el Incidente).
- Insignias de rango europeas propias (ahora usan las de EEUU como placeholder en
  commander_settings.ini).
- Emblemas de armada por nación (ui/campaign/navy_emblems/).

## Notas
- Las referencias de imagen en los XML de evento usan `Assets[<nombre_sin_extension>]`
  y el AssetsPath del bloque de misión en campaign.ini.
- Formato: PNG. Fichas de misión ~ 848 KB / grandes; tiles pequeños.
