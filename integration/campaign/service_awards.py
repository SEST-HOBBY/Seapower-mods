"""Native SEST campaign awards and sourced national award representations.

Native mission completion/RequiredResult and commander nation govern grants.
Real award names/art are represented with explicit fictional scenario citations;
this does not declare a real government operation eligible for an actual medal.
"""
from datetime import date
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = ROOT / 'mods-source/_vanilla/original/campaigns/pacific-strike-task-force/commander_settings.ini'
CAMPAIGNS = {
    'sest-southern-watch': ('southern_watch_service', 'Southern Watch Service Ribbon', 'Southern Watch', ('#123A58', '#DCE6E8', '#317E8C', '#D9B65B', '#317E8C', '#DCE6E8', '#123A58')),
    'sest-southern-reach': ('southern_reach_service', 'Southern Reach Service Ribbon', 'Southern Reach / Tasman Shield', ('#243B65', '#E1E8EF', '#87B4CE', '#E1E8EF', '#243B65')),
    'sest-red-line': ('red_line_service', 'Red Line Service Ribbon', 'Red Line', ('#2A3244', '#B94A48', '#D8BD6D', '#B94A48', '#2A3244')),
    'sest-sulu-line': ('sulu_line_service', 'Sulu Line Service Ribbon', 'Sulu Line', ('#164B4D', '#E5D7A6', '#405D86', '#E5D7A6', '#164B4D')),
}
# Stable native IDs. Milestones recognise the authored operation's completion;
# they do not claim an unrecorded zero-loss, rescue or ROE condition.
MILESTONES = {
    'sest-southern-watch': {
        'SW05': ('sest_northern_lifeline', 'Northern Lifeline Ribbon', 'completing Weapons Free and maintaining the northern sea-lane operation'),
        'SW08': ('sest_archipelago_operations', 'Archipelago Operations Ribbon', 'completing The Open Door and its coordinated archipelago operation'),
    },
    'sest-southern-reach': {
        'SR12': ('sest_antarctic_lifeline', 'Antarctic Lifeline Ribbon', 'completing the Antarctic chapter through Turning North'),
        'TS09': ('sest_southern_convoy', 'Southern Convoy Ribbon', 'completing The Southern Convoy operation'),
    },
    'sest-red-line': {
        'RL03': ('sest_contact_intelligence', 'Contact Intelligence Ribbon', 'completing The Other Picture operation'),
        'RL05': ('sest_undersea_operations', 'Undersea Operations Ribbon', 'completing The Quiet Side operation'),
    },
    'sest-sulu-line': {
        'SL04': ('sest_fleet_sustainment', 'Fleet Sustainment Ribbon', 'completing the campaign resupply operation'),
        'SL06': ('sest_littoral_operations', 'Littoral Operations Ribbon', 'completing the coastal-battery and convoy operation'),
    },
}
REAL = {
    'australian_distinguished_service_cross': dict(nation='Australia', name='Australian Distinguished Service Cross', precedence=11,
        source='https://www.defence.gov.au/adf-members-families/honours-awards/australian-awards/distinguished-service-cross',
        reference='Australia', recipient='commander', native='australian_distinguished_service_cross',
        meaning='The real decoration recognises distinguished command and leadership in warlike operations.'),
    'sest_aosm_indo_pacific': dict(nation='Australia', name='Australian Operational Service Medal - Indo-Pacific', precedence=100,
        source='https://www.defence.gov.au/adf-members-families/honours-awards/australian-awards/australian-operational-service-medal-indo-pacific',
        reference='Australia', recipient='commander', native=None,
        meaning='Real eligibility requires qualifying duty on a declared operation, normally 30 eligible days. SEST uses its fictional operational assignment and authored campaign calendar.'),
    'navy_achievement_medal': dict(nation='US', name='Navy and Marine Corps Achievement Medal', precedence=50,
        source='https://www.secnav.navy.mil/DONi/manuals-secnav.aspx', reference='USN', recipient='commander', native='navy_achievement_medal',
        meaning='The real award recognises qualifying meritorious achievement or service under US naval award rules.'),
    'navy_commendation_medal': dict(nation='US', name='Navy and Marine Corps Commendation Medal', precedence=40,
        source='https://www.secnav.navy.mil/DONi/manuals-secnav.aspx', reference='USN', recipient='commander', native='navy_commendation_medal',
        meaning='The real award recognises qualifying meritorious service, achievement or heroism under US naval award rules.'),
    'navy_unit_commendation': dict(nation='US', name='Navy Unit Commendation', precedence=75,
        source='https://www.secnav.navy.mil/DONi/manuals-secnav.aspx', reference='USN', recipient='unit', native='navy_unit_commendation',
        meaning='The real award is a unit citation for qualifying outstanding service or heroism, not an individual decoration.'),
    'meritorious_unit_commendation': dict(nation='US', name='Meritorious Unit Commendation', precedence=80,
        source='https://www.secnav.navy.mil/DONi/manuals-secnav.aspx', reference='USN', recipient='unit', native='meritorious_unit_commendation',
        meaning='The real award is a unit citation for qualifying meritorious unit service.'),
}
NATIONAL_MISSIONS = {
    'sest-southern-watch': {
        'SW05': ('navy_achievement_medal',),
        'SW08': ('navy_commendation_medal',),
        'SW12': ('australian_distinguished_service_cross', 'navy_unit_commendation'),
    },
    'sest-southern-reach': {
        'SR04': ('navy_achievement_medal',),
        'SR10': ('sest_aosm_indo_pacific',),
        'SR12': ('navy_commendation_medal',),
        'TS09': ('australian_distinguished_service_cross', 'navy_unit_commendation'),
        'TS12': ('meritorious_unit_commendation',),
    },
}


def base_slug(slug):
    return slug.removesuffix('-open')


def award_id(slug):
    row = CAMPAIGNS.get(base_slug(slug))
    return 'sest_' + row[0] if row else None


def _section(text, name):
    m = re.search(r'(?ms)^\[' + re.escape(name) + r'\][^\n]*\n(.*?)(?=^\[|\Z)', text)
    return dict(re.findall(r'^([^=\n]+)=(.*)$', m[1], re.M)) if m else {}


def _set(text, section, key, value):
    m = re.search(r'(?ms)^\[' + re.escape(section) + r'\][^\n]*\n(.*?)(?=^\[|\Z)', text)
    if not m:
        return text.rstrip() + f'\n\n[{section}]\n{key}={value}\n'
    body = m[1]
    if re.search(r'^' + re.escape(key) + r'=', body, re.M):
        body = re.sub(r'^' + re.escape(key) + r'=.*$', lambda _: key + '=' + value, body, flags=re.M)
    else:
        body = body.rstrip() + f'\n{key}={value}\n\n'
    return text[:m.start(1)] + body + text[m.end(1):]


def _us_option(text, slug):
    if slug not in NATIONAL_MISSIONS:
        return text
    native = NATIVE.read_text(encoding='utf-8-sig')
    values = _section(text, 'CommanderSettings')
    nations = [n for n in re.split(r'[|,]', values.get('CommanderNations', 'Australia')) if n]
    if 'US' not in nations:
        nations.append('US')
    text = _set(text, 'CommanderSettings', 'CommanderNations', '|'.join(nations))
    # Default nation/rank and already committed commander records are retained.
    for key, value in {'CommanderNameDefaultUS': 'Alex Morgan', 'CommanderNamePoolUS': 'Names_USA',
                       'NavyNameUS': 'United States Navy', 'NavyEmblemUS': 'ui/campaign/navy_emblems/usn_emblem.png'}.items():
        if key not in values:
            text = _set(text, 'CommanderSettings', key, value)
    if 'US' not in _section(text, 'OfficerRanks'):
        text = _set(text, 'OfficerRanks', 'US', _section(native, 'OfficerRanks')['US'])
    return text


def catalogue(slug):
    slug = base_slug(slug)
    if slug not in CAMPAIGNS:
        return {}
    short, name, operation, colours = CAMPAIGNS[slug]
    out = {award_id(slug): dict(name=name, colours=colours, type='CampaignAward', precedence=120,
            reference='Fictional', recipient='commander', citation=f'For completing command service during {operation}. This fictional SEST service award records campaign completion.')}
    for index, (_code, (rid, title, why)) in enumerate(MILESTONES[slug].items()):
        accent = '#D9B65B' if index == 0 else '#8AB1C2'
        pattern = (colours[0], accent, colours[2], '#DCE6E8', colours[2], accent, colours[0])
        out[rid] = dict(name=title, colours=pattern, type='CampaignAward', precedence=130,
            reference='Fictional', recipient='commander', citation=f'For {why}. Granted after the native required mission result; no unrecorded performance condition is claimed.')
    native = NATIVE.read_text(encoding='utf-8-sig')
    for rid in dict.fromkeys(r for ids in NATIONAL_MISSIONS.get(slug, {}).values() for r in ids):
        row = dict(REAL[rid])
        source = _section(native, 'Ribbon_' + row['native']) if row['native'] else {}
        row.update(type=source.get('Type', 'ServiceAward'), image=source.get('ImagePath'), medal=source.get('MedalImagePath'))
        # Some stock MedalImagePaths are pre-written 1985 citation sheets.
        # Use our modern scenario citation rather than showing those sheets.
        if row['medal'] and 'citation' in row['medal'].lower():
            row['medal'] = None
        codes = [code for code, ids in NATIONAL_MISSIONS[slug].items() if rid in ids]
        extra = (' The authored assignment begins 6 December 2028; SR10 is 6 January 2029, at least 30 campaign days later.'
                 if rid == 'sest_aosm_indo_pacific' else '')
        row['citation'] = (f'SEST fictional-operation representation of {row["name"]}, for command service in {operation}. '
                           f'Scenario qualification: complete {" / ".join(codes)} with its required native result as a {row["nation"]} commander.'
                           + extra + ' ' + row['meaning'] +
                           ' The SEST operation is fictional; this in-game citation is not an actual government award or declaration of eligibility.')
        out[rid] = row
    return out


def commander_settings(text, slug):
    """Merge definitions without removing existing IDs, citations or commanders."""
    slug = base_slug(slug)
    definitions = catalogue(slug)
    if not definitions:
        return text
    text = _us_option(text, slug)
    current = _section(text, 'TaskForceRibbons').get('RibbonIds', '')
    ids = [i.strip() for i in re.split(r'[|,]', current) if i.strip()]
    ids.extend(rid for rid in definitions if rid not in ids)
    text = _set(text, 'TaskForceRibbons', 'RibbonIds', '|'.join(ids))
    for rid, row in definitions.items():
        if _section(text, 'Ribbon_' + rid):
            continue
        image = row.get('image') or f'campaigns/{slug}/art/ribbons/{rid}.png'
        data = dict(Type=row['type'], Precedence=row['precedence'], Name_en=row['name'], ImagePath=image,
                    CitationIssuingBody_en='SEST Scenario Awards Board', CitationIssuance_en='recognises',
                    CitationAwardName_en=row['name'], CitationAuthority_en='To',
                    CitationRecipient_en='{TaskForceName}' if row['recipient'] == 'unit' else '{CommanderRank} {CommanderName}',
                    CitationText_en=row['citation'], CitationSignatureName_en='Campaign Operations Staff',
                    CitationSignatureTitle_en='Scenario Awards Board', ReferenceSource=row['reference'])
        if row.get('medal'):
            data['MedalImagePath'] = row['medal']
        if row.get('colours'):
            data['StripeColors'] = '|'.join(row['colours'])
            data['StripeWidths'] = '|'.join(['20'] * len(row['colours']))
        if row.get('source'):
            data['SourceUrl'] = row['source']
        text = text.rstrip() + f'\n\n[Ribbon_{rid}]\n' + ''.join(f'{k}={v}\n' for k, v in data.items())
    return text


def render(campaign_directory, slug):
    """Render fictional strips; copy the sourced AOSM strip without alteration."""
    from PIL import Image, ImageDraw
    slug = base_slug(slug)
    if slug in NATIONAL_MISSIONS:
        credits = Path(campaign_directory) / 'art/ribbons/SOURCES.txt'
        credits.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / 'assets/ribbons/SOURCES.txt', credits)
    for rid, row in catalogue(slug).items():
        if row.get('image'):
            continue  # References an installed native game asset.
        path = Path(campaign_directory) / 'art/ribbons' / (rid + '.png')
        path.parent.mkdir(parents=True, exist_ok=True)
        if rid == 'sest_aosm_indo_pacific':
            shutil.copyfile(HERE / 'assets/ribbons/aosm_indo_pacific.png', path)
            continue
        image = Image.new('RGBA', (140, 36), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        colours = row['colours']
        for index, colour in enumerate(colours):
            draw.rectangle((round(2 + 136 * index / len(colours)), 3,
                            round(2 + 136 * (index + 1) / len(colours)), 32), fill=colour)
        draw.rectangle((1, 2, 138, 33), outline='#B0B4B8', width=1)
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        stitches = ImageDraw.Draw(overlay)
        for y in range(5, 32, 3):
            stitches.line((3, y, 136, y), fill=(255, 255, 255, 22))
        Image.alpha_composite(image, overlay).save(path)


def mission_awards(slug, mission, final=False):
    """Native grammar: award IDs separated by pipes; nations after commas."""
    slug = base_slug(slug)
    if slug not in CAMPAIGNS:
        return []
    code = mission.get('code', 'SW' + mission.get('num', ''))
    result = [award_id(slug)] if final else []
    milestone = MILESTONES[slug].get(code)
    if milestone:
        result.append(milestone[0])
    for rid in NATIONAL_MISSIONS.get(slug, {}).get(code, ()):
        if rid == 'sest_aosm_indo_pacific':
            # Fail if an author moves this scripted service milestone earlier.
            if (date(*mission['date']) - date(2028, 12, 6)).days < 30:
                raise ValueError('AOSM scenario service milestone must follow 30 campaign days')
        result.append(rid + ',' + REAL[rid]['nation'])
    return result


def final_mission_awards(campaign_text, slug):
    rid = award_id(slug)
    if not rid:
        return campaign_text
    for section in reversed(list(re.finditer(r'(?ms)^\[Mission\d+\][^\n]*\n(.*?)(?=^\[|\Z)', campaign_text))):
        body = section[1]
        if 'TaskForceModeFinalMission=True' not in body:
            continue
        match = re.search(r'^TaskForceModeRibbonAwards=(.*)$', body, re.M)
        specs = [x.strip() for x in match[1].split('|') if x.strip()] if match else []
        if rid not in [x.split(',')[0] for x in specs]:
            specs.append(rid)
        line = 'TaskForceModeRibbonAwards=' + '|'.join(specs)
        body = re.sub(r'^TaskForceModeRibbonAwards=.*$', lambda _: line, body, flags=re.M) if match else body.rstrip() + '\n' + line + '\n'
        return campaign_text[:section.start(1)] + body + campaign_text[section.end(1):]
    raise ValueError('Campaign has no explicit native final mission: ' + slug)
