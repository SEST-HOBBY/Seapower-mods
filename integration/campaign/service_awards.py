"""Native SEST campaign awards, commander nations and real-award representations.

The game's own rules, read from Seapower-Scripts.dll (0.8.7-261107) as IL:

- [CommanderSettings] CommanderNations is split on '|'. For each nation key N
  the commander screen reads CommanderNameDefaultN, CommanderNamePoolN (a
  Names_ section of language_<xx>/ui.ini), NavyNameN, NavyEmblemN and
  [OfficerRanks] N (rank,abbreviation,grade,level,insignia; five fields, an
  empty insignia allowed). CommanderDefaultNation is listed first.
- CommitCommander writes TaskForceCommanderNation and refuses once
  TaskForceCommanderCommitted is set, so a commander already in a save keeps
  the nation it has. Nothing here edits a save.
- The same-nation discount follows TaskForceCommanderNationOverride when it
  is set (the Service Record offers it only in the game's Unrestricted mode,
  All nations by default) and the commander's nation otherwise. The rules
  page says so for every nation a campaign offers (build_pack.campaign_rules).
- [Mission] TaskForceModeRibbonAwards: '|' between awards, ',' before nation
  selectors. A spec with no selector goes to any commander; a selector is
  compared with the committed nation, ignoring case. Awards are granted only
  when the mission is complete at its RequiredResult or better.
- Ribbon_<id> keys read: Name_en, ImagePath, MedalImagePath, Precedence,
  Type, ReferenceSource, CitationTitle_en, CitationIssuingBody_en,
  CitationIssuance_en, CitationAwardName_en, CitationAuthority_en,
  CitationRecipient_en, CitationDate_en, CitationSignatureName_en,
  CitationSignatureTitle_en, CitationSealImagePath, CitationType,
  CitationTemplatePath and CitationText_en (USA/Japan/Australia variants
  too). StripeColors, StripeWidths and SourceUrl are not read: they are kept
  as a record of how each code-drawn strip was made. An empty CitationDate_en
  shows '26 JUNE 1985', so every award here carries its mission's date.

Real award names and pictures are represented for fictional 2028-2029
operations. The criteria quoted are the real ones; the qualification is the
game's, and every real-award citation says it is not a real honour. Each
campaign's art/ribbons/SOURCES.txt lists the pictures and the award sources.
"""
from datetime import date
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = ROOT / 'mods-source/_vanilla/original/campaigns/pacific-strike-task-force/commander_settings.ini'
STOCK = 'campaigns/pacific-strike-task-force/art/'

CAMPAIGNS = {
    'sest-southern-watch': ('southern_watch_service', 'Southern Watch Service Ribbon', 'Southern Watch', ('#123A58', '#DCE6E8', '#317E8C', '#D9B65B', '#317E8C', '#DCE6E8', '#123A58')),
    'sest-southern-reach': ('southern_reach_service', 'Southern Reach Service Ribbon', 'Southern Reach / Tasman Shield', ('#243B65', '#E1E8EF', '#87B4CE', '#E1E8EF', '#243B65')),
    'sest-red-line': ('red_line_service', 'Red Line Service Ribbon', 'Red Line', ('#2A3244', '#B94A48', '#D8BD6D', '#B94A48', '#2A3244')),
    'sest-sulu-line': ('sulu_line_service', 'Sulu Line Service Ribbon', 'Sulu Line', ('#164B4D', '#E5D7A6', '#405D86', '#E5D7A6', '#164B4D')),
}

# The missions that grant an award: code -> (title, date, how a citation
# names it). mission_awards() stops the build if a mission's title or date
# moves away from this table, so a citation can never name the wrong mission
# or carry the wrong date.
MISSIONS = {
    'sest-southern-watch': {
        'SW05': ('Weapons Free', (2028, 11, 2), 'in Weapons Free'),
        'SW08': ('The Open Door', (2028, 11, 13), 'in The Open Door'),
        'SW12': ('The First Ship Through', (2028, 11, 28), 'during Southern Watch, through The First Ship Through'),
    },
    'sest-southern-reach': {
        'SR01': ('Southern Departure', (2028, 12, 6), 'in Southern Departure'),
        'SR04': ('Macquarie Passage', (2028, 12, 15), 'in Macquarie Passage'),
        'SR10': ('Southern Line', (2029, 1, 6), 'during Southern Reach, through Southern Line'),
        'SR12': ('Turning North', (2029, 1, 14), 'during Southern Reach, through Turning North'),
        'TS09': ('The Southern Convoy', (2029, 2, 19), 'during Tasman Shield, in The Southern Convoy'),
        'TS12': ('Southern Cross', (2029, 3, 2), 'during Tasman Shield, through Southern Cross'),
    },
    'sest-red-line': {
        'RL03': ('The Other Picture', (2028, 11, 19), 'in The Other Picture'),
        'RL05': ('Under the Convergence', (2028, 12, 27), 'in Under the Convergence'),
        'RL06': ('The Quiet Side', (2029, 1, 19), 'during Red Line, through The Quiet Side'),
    },
    'sest-sulu-line': {
        'SL04': ('Service at Sea', (2028, 11, 2), 'in Service at Sea'),
        'SL05': ('Celebes Gate', (2028, 11, 9), 'in Celebes Gate'),
        'SL06': ('The Aborlan Battery', (2028, 11, 16), 'in The Aborlan Battery'),
        'SL07': ('Balabac Strait', (2028, 11, 23), 'during Sulu Line, through Balabac Strait'),
    },
}
FINAL = {'sest-southern-watch': 'SW12', 'sest-southern-reach': 'TS12',
         'sest-red-line': 'RL06', 'sest-sulu-line': 'SL07'}
# The first day of the authored operation, for the two 30-day service medals.
FIRST = {'sest-southern-reach': 'SR01'}

# Commander nations each campaign offers: its own default first, then every
# nation the story can put in command of the group whose ships the player can
# buy and whose ranks, names, emblem and awards could be sourced. Southern
# Watch and Southern Reach are Australian-led coalition groups; the allied
# fleet sells US, British and Japanese hulls and Japan's ASW group is in the
# story (SW10). Red Line is a PLAN group and Sulu Line a Philippine-led one;
# the Thai detachment and the single RAN frigate there serve under it.
NATIONS = {
    'sest-southern-watch': ('Australia', 'US', 'UK', 'Japan'),
    'sest-southern-reach': ('Australia', 'US', 'UK', 'Japan'),
    'sest-red-line': ('China',),
    'sest-sulu-line': ('Philippines',),
}
# Adjective and article for a citation, the rules page and RIBBONS.txt.
ADJECTIVE = {'Australia': ('Australian', 'an'), 'US': ('American', 'an'), 'UK': ('British', 'a'),
             'Japan': ('Japanese', 'a'), 'China': ('Chinese', 'a'), 'Philippines': ('Philippine', 'a')}

# Royal Navy officer ranks with NATO grades, at the levels the Australian
# ladder uses for the same grades (Commander 5, Captain 6, Commodore 7). The
# game ships no Royal Navy insignia, so the image field is empty, as in Red
# Line and Sulu Line.
UK_RANKS = ('Midshipman,MID,OF-D,1,|Sub-Lieutenant,SLT,OF-1,2,|Lieutenant,LT,OF-2,3,|'
            'Lieutenant Commander,LT CDR,OF-3,4,|Commander,CDR,OF-4,5,|Captain,CAPT,OF-5,6,|'
            'Commodore,CDRE,OF-6,7,|Rear Admiral,RADM,OF-7,8,|Vice Admiral,VADM,OF-8,9,|'
            'Admiral,ADM,OF-9,10,')
# The settings a nation needs when a campaign's own COMMANDER text does not
# define it. US and Japan are the stock Pacific Strike values (its default
# Japanese name, pools, navies, emblems and rank ladders). The UK uses the
# stock [Names_UK] pool and the Royal Navy's White Ensign, drawn by
# build_pack.write_emblems from the SEST gallery's public-domain flag set.
NATION_SETTINGS = {
    'US': dict(name='Alex Morgan', pool='Names_USA', navy='United States Navy',
               emblem='ui/campaign/navy_emblems/usn_emblem.png', ranks=None),
    'UK': dict(name='Julian Northcott', pool='Names_UK', navy='Royal Navy',
               emblem='ui/campaign/navy_emblems/sest_rn_emblem.png', ranks=UK_RANKS),
    'Japan': dict(name='Hiroshi Watanabe', pool='Names_Japan', navy='Japan Maritime Self-Defense Force',
                  emblem='ui/campaign/navy_emblems/jmsdf_emblem.png', ranks=None),
}

# Fictional operation ribbons: code -> (id, name, citation, stripes). The
# ids are stable; each strip has its own centre colour so the rack reads.
MILESTONES = {
    'sest-southern-watch': {
        'SW05': ('sest_northern_lifeline', 'Timor Corridor Ribbon',
                 'For completing Weapons Free and holding the Timor corridor in command of {TaskForceName}',
                 (('#123A58', 4), ('#3E9C88', 10), ('#F2F2EC', 2), ('#C8642B', 4), ('#F2F2EC', 2), ('#3E9C88', 10), ('#123A58', 4))),
        'SW08': ('sest_archipelago_operations', 'Archipelago Operations Ribbon',
                 'For completing The Open Door, the relief window over the Biak enclave, in command of {TaskForceName}',
                 (('#123A58', 3), ('#6B4E9B', 6), ('#DCE6E8', 2), ('#2C6E49', 12), ('#DCE6E8', 2), ('#6B4E9B', 6), ('#123A58', 3))),
    },
    'sest-southern-reach': {
        'SR12': ('sest_antarctic_lifeline', 'Antarctic Resupply Ribbon',
                 'For completing the Antarctic resupply voyages through Turning North in command of {TaskForceName}',
                 (('#F4F6F8', 4), ('#243B65', 2), ('#8FC1E3', 14), ('#243B65', 2), ('#F4F6F8', 4))),
        'TS09': ('sest_southern_convoy', 'Southern Convoy Ribbon',
                 'For completing The Southern Convoy and bringing its merchant hulls through in command of {TaskForceName}',
                 (('#243B65', 5), ('#B8312F', 3), ('#E1E8EF', 3), ('#1F6F78', 8), ('#E1E8EF', 3), ('#B8312F', 3), ('#243B65', 5))),
    },
    'sest-red-line': {
        'RL03': ('sest_contact_intelligence', 'Contact Intelligence Ribbon',
                 'For completing The Other Picture and bringing the collection aircraft home in command of {TaskForceName}',
                 (('#2A3244', 4), ('#B94A48', 3), ('#4A78A8', 14), ('#B94A48', 3), ('#2A3244', 4))),
        'RL05': ('sest_undersea_operations', 'Undersea Operations Ribbon',
                 'For completing Under the Convergence and its detached submarine operation in command of {TaskForceName}',
                 (('#0E1A2B', 6), ('#B94A48', 2), ('#2F5D50', 12), ('#B94A48', 2), ('#0E1A2B', 6))),
    },
    'sest-sulu-line': {
        'SL04': ('sest_fleet_sustainment', 'Fleet Sustainment Ribbon',
                 'For completing Service at Sea, the task group\'s replenishment at sea, in command of {TaskForceName}',
                 (('#164B4D', 4), ('#E5D7A6', 3), ('#8A5A2B', 12), ('#E5D7A6', 3), ('#164B4D', 4))),
        'SL06': ('sest_littoral_operations', 'Littoral Operations Ribbon',
                 'For completing The Aborlan Battery and reopening the island road in command of {TaskForceName}',
                 (('#405D86', 4), ('#E5D7A6', 2), ('#164B4D', 4), ('#C9643B', 8), ('#164B4D', 4), ('#E5D7A6', 2), ('#405D86', 4))),
    },
}
COMPLETION = 'For completing the {operation} campaign in command of {{TaskForceName}}, through {final}'
FICTIONAL = 'Fictional SEST campaign award.'
REAL_NOTE = 'Game award for a fictional operation; not a real honour.'

# Real awards. nation=None is the host nation's unit award, granted to the
# task group whatever the commander's nation (the group is the host's). ranks
# is the NATO OF range the real award fits in practice; the tests hold each
# grant to it at the campaign's starting rank. art: 'stock:<path>' references
# an installed Sea Power picture; a tuple of (colour, width) stripes is drawn
# by render(); 'aosm' copies the CC0 strip. A device is drawn over the strip.
REAL = {
    # --- Australia (Governor-General; Defence honours pages) --------------
    'australian_distinguished_service_cross': dict(
        nation='Australia', name='Australian Distinguished Service Cross', type='PersonalDecoration', precedence=11,
        art='stock:ribbons/australian_distinguished_service_cross_ribbon.png',
        medal='stock:medals/australian_distinguished_service_cross_medal.png', ranks=(1, 10),
        merit='For distinguished command and leadership in warlike operations as commander of {TaskForceName}',
        source='https://www.defence.gov.au/sites/default/files/2025-01/Fact-Sheet-Distinguished-Service-Cross.pdf'),
    'australian_commendation_distinguished_service': dict(
        nation='Australia', name='Commendation for Distinguished Service', type='PersonalDecoration', precedence=35,
        art=(('#A4402B', 1),), device='federation_star', ranks=(1, 10),
        merit='For distinguished performance of duties in warlike operations as commander of {TaskForceName}',
        source='https://www.defence.gov.au/adf-members-families/honours-awards/australian-awards/commendation-distinguished-service'),
    'australian_meritorious_unit_citation': dict(
        nation=None, host='Australia', name='Australian Meritorious Unit Citation', type='UnitAward', precedence=78,
        art=(('#CFA94A', 1),), device='silver_frame', ranks=None,
        merit='For sustained outstanding service in warlike operations by {TaskForceName}',
        source='https://www.pmc.gov.au/honours-and-symbols/list-australian-honours/meritorious-unit-citation'),
    'sest_aosm_indo_pacific': dict(
        nation='Australia', name='Australian Operational Service Medal - Indo-Pacific', type='ServiceAward', precedence=100,
        art='aosm', ranks=(1, 10), service_days=30,
        merit="For 30 days' operational service with {TaskForceName}",
        source='https://www.defence.gov.au/adf-members-families/honours-awards/australian-awards/australian-operational-service-medal-indo-pacific'),
    # --- United States (SECNAV M-1650.1; 32 CFR 578; TIOH) -----------------
    'legion_of_merit': dict(
        nation='US', name='Legion of Merit', type='PersonalDecoration', precedence=13,
        art=(('#FFFFFF', 4), ('#A6192E', 80), ('#FFFFFF', 4)), ranks=(5, 10),
        merit='For exceptionally meritorious conduct in the performance of outstanding service as commander of {TaskForceName}',
        source='https://www.govinfo.gov/content/pkg/CFR-2002-title32-vol3/html/CFR-2002-title32-vol3-sec578-8.htm'),
    'bronze_star_medal': dict(
        nation='US', name='Bronze Star Medal', type='PersonalDecoration', precedence=30,
        art='stock:ribbons/bronze_star_medal_ribbon.png', ranks=(1, 10),
        merit='For meritorious achievement in connection with operations against an armed enemy as commander of {TaskForceName}',
        source='https://uscode.house.gov/us/usc/t10/s1133/'),
    'navy_commendation_medal': dict(
        nation='US', name='Navy and Marine Corps Commendation Medal', type='PersonalDecoration', precedence=40,
        art='stock:ribbons/navy_commendation_medal_ribbon.png', ranks=(1, 10),
        merit='For meritorious achievement as commander of {TaskForceName}',
        source='https://www.secnav.navy.mil/doni/SECNAV%20Manuals1/1650.1.pdf'),
    'armed_forces_expeditionary_medal': dict(
        nation='US', name='Armed Forces Expeditionary Medal', type='ServiceAward', precedence=98,
        art=(('#007A33', 6), ('#FFCD00', 6), ('#6B4226', 6), ('#000000', 6), ('#5B9BD5', 14), ('#001489', 4),
             ('#FFFFFF', 4), ('#BA0C2F', 4), ('#5B9BD5', 14), ('#000000', 6), ('#6B4226', 6), ('#FFCD00', 6),
             ('#007A33', 6)), ranks=(1, 10), service_days=30,
        merit='For 30 days of service with {TaskForceName} in operations against foreign armed opposition',
        source='https://www.archives.gov/federal-register/codification/executive-order/10977.html'),
    # --- United Kingdom (London Gazette order of wear; MOD) ----------------
    'uk_distinguished_service_order': dict(
        nation='UK', name='Distinguished Service Order', type='PersonalDecoration', precedence=12,
        art=(('#1C2D5A', 3), ('#C8102E', 22.6), ('#1C2D5A', 3)), ranks=(1, 10),
        merit='For highly successful command and leadership during active operations as commander of {TaskForceName}',
        source='https://www.thegazette.co.uk/London/issue/62529/supplement/326/data.pdf'),
    'uk_obe_military': dict(
        nation='UK', name='Officer of the Order of the British Empire (Military)', type='PersonalDecoration', precedence=14,
        art=(('#B9BDC4', 3), ('#E39FAB', 15.25), ('#B9BDC4', 1.5), ('#E39FAB', 15.25), ('#B9BDC4', 3)), ranks=(3, 5),
        merit='For distinguished service as commander of {TaskForceName}',
        source='https://www.royalnavy.mod.uk/news/2024/december/30/20241230-new-years-and-op-honours'),
    # --- Japan (自衛隊法施行規則; 表彰等に関する訓令) ---------------------------
    # The picture is the game's own JMSDF Defense Memorial Cordon. The colours
    # of cordon No. 2 (worn by 1st Class Commendation recipients) could not
    # be checked, so the stock picture is used and said to be stock.
    'jmsdf_first_class_commendation': dict(
        nation='Japan', name='1st Class Commendation (Defense Memorial Cordon)', type='PersonalDecoration', precedence=20,
        art='stock:ribbons/jmsdf_defense_memorial_cordon_ribbon.png', ranks=(1, 10),
        merit='For conspicuous merit as commander of {TaskForceName}',
        source='http://www.clearing.mod.go.jp/kunrei_data/a_fd/1955/ax19550810_00049_000.pdf'),
    # --- Philippines (AFP Awards and Decorations Manual, AFPR G 131-054) ---
    'ph_distinguished_service_star': dict(
        nation='Philippines', name='Distinguished Service Star', type='PersonalDecoration', precedence=12,
        art=(('#1F2F6B', 33), ('#C8102E', 34), ('#1F2F6B', 33)), ranks=(1, 10),
        merit='For eminently meritorious and valuable service in a position of great responsibility as commander of {TaskForceName}',
        source='https://en.wikipedia.org/wiki/Distinguished_Service_Star'),
    'ph_military_merit_medal': dict(
        nation='Philippines', name='Military Merit Medal', type='PersonalDecoration', precedence=30,
        art=(('#00843D', 34), ('#C8102E', 4), ('#00843D', 5), ('#C8102E', 4), ('#00843D', 5), ('#C8102E', 4), ('#00843D', 34)),
        ranks=(1, 10),
        merit='For meritorious service in support of military action as commander of {TaskForceName}',
        source='https://en.wikipedia.org/wiki/Military_Merit_Medal_(Philippines)'),
    'ph_presidential_unit_citation': dict(
        nation=None, host='Philippines', name='Philippine Republic Presidential Unit Citation', type='UnitAward', precedence=70,
        art=(('#0038A8', 33), ('#FFFFFF', 34), ('#CE1126', 33)), device='gold_frame', ranks=None,
        merit='For extraordinary meritorious service by {TaskForceName}',
        source='https://www.afpc.af.mil/Fact-Sheets/Display/Article/421896/philippine-presidential-unit-citation/'),
}
# Definitions an earlier test build granted and this one does not (the NAM is
# for O-4 and below; the US unit citations do not belong to an Australian
# group). Kept so a record earned with that build still shows; never granted.
RETIRED = {
    'navy_achievement_medal': dict(
        nation='US', name='Navy and Marine Corps Achievement Medal', type='PersonalDecoration', precedence=50,
        art='stock:ribbons/navy_achievement_medal_ribbon.png', ranks=(1, 3),
        merit='For professional achievement while serving with {TaskForceName}',
        missions={'sest-southern-watch': 'SW05', 'sest-southern-reach': 'SR04'},
        source='https://www.secnav.navy.mil/doni/SECNAV%20Manuals1/1650.1.pdf'),
    'navy_unit_commendation': dict(
        nation='US', name='Navy Unit Commendation', type='UnitAward', precedence=75,
        art='stock:ribbons/navy_unit_commendation_ribbon.png', ranks=None,
        merit='For outstanding service by {TaskForceName}',
        missions={'sest-southern-watch': 'SW12', 'sest-southern-reach': 'TS09'},
        source='https://www.secnav.navy.mil/doni/SECNAV%20Manuals1/1650.1.pdf'),
    'meritorious_unit_commendation': dict(
        nation='US', name='Meritorious Unit Commendation', type='UnitAward', precedence=80,
        art='stock:ribbons/meritorious_unit_commendation_ribbon.png', ranks=None,
        merit='For meritorious service by {TaskForceName}',
        missions={'sest-southern-reach': 'TS12'},
        source='https://www.secnav.navy.mil/doni/SECNAV%20Manuals1/1650.1.pdf'),
}

# What each mission grants beyond its milestone and the final completion
# ribbon. A modest set per nation: a lesser personal award mid-campaign, the
# senior one at the climax, the operational service medal where the real one
# has a service period, and the host nation's unit award to the group.
GRANTS = {
    'sest-southern-watch': {
        'SW08': ('australian_commendation_distinguished_service', 'navy_commendation_medal', 'uk_obe_military'),
        'SW12': ('australian_distinguished_service_cross', 'bronze_star_medal', 'uk_distinguished_service_order',
                 'jmsdf_first_class_commendation', 'australian_meritorious_unit_citation'),
    },
    'sest-southern-reach': {
        'SR10': ('sest_aosm_indo_pacific', 'armed_forces_expeditionary_medal'),
        'SR12': ('australian_commendation_distinguished_service', 'navy_commendation_medal', 'uk_obe_military'),
        'TS09': ('australian_distinguished_service_cross', 'legion_of_merit', 'uk_distinguished_service_order',
                 'jmsdf_first_class_commendation'),
        'TS12': ('australian_meritorious_unit_citation',),
    },
    'sest-sulu-line': {
        'SL05': ('ph_military_merit_medal',),
        'SL07': ('ph_distinguished_service_star', 'ph_presidential_unit_citation'),
    },
}


def base_slug(slug):
    return slug.removesuffix('-open')


def award_id(slug):
    row = CAMPAIGNS.get(base_slug(slug))
    return 'sest_' + row[0] if row else None


def commander_nations(slug, commander=''):
    """The nation keys a campaign offers, its default first."""
    slug = base_slug(slug)
    own = _section(commander, 'CommanderSettings').get('CommanderNations', '')
    nations = [n.strip() for n in own.split('|') if n.strip()]
    for nation in NATIONS.get(slug, ()):
        if nation not in nations:
            nations.append(nation)
    return tuple(nations)


def describe(nation):
    """'an Australian commander', 'a British commander'."""
    adjective, article = ADJECTIVE.get(nation, (nation, 'a'))
    return f'{article} {adjective} commander'


def citation_date(when):
    return f'{when[2]} {date(*when).strftime("%B")} {when[0]}'


def _section(text, name):
    m = re.search(r'(?ms)^\[' + re.escape(name) + r'\][^\n]*\n(.*?)(?=^\[|\Z)', text)
    return dict((k.strip(), v) for k, v in re.findall(r'^([^=\n;#]+)=(.*)$', m[1], re.M)) if m else {}


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


def _nations(text, slug):
    """Offer the campaign's commander nations. The default nation, its
    starting rank and anything the text already sets stay as they are."""
    if slug not in NATIONS:
        return text
    native = NATIVE.read_text(encoding='utf-8-sig')
    nations = commander_nations(slug, text)
    text = _set(text, 'CommanderSettings', 'CommanderNations', '|'.join(nations))
    for nation in nations:
        values = _section(text, 'CommanderSettings')
        row = NATION_SETTINGS.get(nation)
        if row is None:
            continue
        for key, value in (('CommanderNameDefault', row['name']), ('CommanderNamePool', row['pool']),
                           ('NavyName', row['navy']), ('NavyEmblem', row['emblem'])):
            if key + nation not in values:
                text = _set(text, 'CommanderSettings', key + nation, value)
        if nation not in _section(text, 'OfficerRanks'):
            ranks = row['ranks'] or _section(native, 'OfficerRanks')[nation]
            text = _set(text, 'OfficerRanks', nation, ranks)
    return text


def _mission(slug, code):
    try:
        return MISSIONS[slug][code]
    except KeyError:
        raise ValueError(f'{slug}: no mission table entry for {code}') from None


def grants(slug):
    """{award id: mission code} - where each award is granted. Each id is
    granted at one mission per campaign."""
    slug = base_slug(slug)
    out = {}
    if slug in CAMPAIGNS:
        out[award_id(slug)] = FINAL[slug]
    for code, row in MILESTONES.get(slug, {}).items():
        out[row[0]] = code
    for code, ids in GRANTS.get(slug, {}).items():
        for rid in ids:
            if rid in out:
                raise ValueError(f'{slug}: {rid} is granted twice')
            out[rid] = code
    return out


def catalogue(slug):
    """Every definition a campaign carries: what it grants, then what earlier
    builds granted (RETIRED), keyed by id."""
    slug = base_slug(slug)
    if slug not in CAMPAIGNS:
        return {}
    short, name, operation, colours = CAMPAIGNS[slug]
    final = _mission(slug, FINAL[slug])
    out = {award_id(slug): dict(
        name=name, type='CampaignAward', precedence=120, reference='Fictional', recipient='commander',
        stripes=tuple((c, 20) for c in colours), mission=FINAL[slug],
        citation=COMPLETION.format(operation=operation.replace(' / ', ' and '), final=final[0]) + '. ' + FICTIONAL)}
    for code, (rid, title, why, stripes) in MILESTONES[slug].items():
        out[rid] = dict(name=title, type='CampaignAward', precedence=130, reference='Fictional',
                        recipient='commander', stripes=stripes, mission=code, citation=why + '. ' + FICTIONAL)
    for rid, code in grants(slug).items():
        if rid in out:
            continue
        out[rid] = _real(slug, rid, REAL[rid], code)
    for rid, row in RETIRED.items():
        if slug in row['missions'] and rid not in out:
            out[rid] = dict(_real(slug, rid, row, row['missions'][slug]), retired=True)
    return out


def _real(slug, rid, row, code):
    context = _mission(slug, code)[2]
    nation = row['nation'] or row['host']
    out = dict(row, reference=nation, mission=code,
               recipient='unit' if row['type'] == 'UnitAward' else 'commander',
               citation=f'{row["merit"]} {context}. {REAL_NOTE}')
    art = row['art']
    if isinstance(art, str) and art.startswith('stock:'):
        out['image'] = STOCK + art[len('stock:'):]
    elif art == 'aosm':
        out['image'] = None
    else:
        out['stripes'] = art
    if row.get('medal'):
        out['medal_image'] = STOCK + row['medal'][len('stock:'):]
    return out


def commander_settings(text, slug):
    """Merge nations and definitions without removing existing IDs, citations
    or commanders. The output is the same however often it is applied."""
    slug = base_slug(slug)
    definitions = catalogue(slug)
    if not definitions:
        return text
    text = _nations(text, slug)
    current = _section(text, 'TaskForceRibbons').get('RibbonIds', '')
    ids = [i.strip() for i in re.split(r'[|,]', current) if i.strip()]
    ids.extend(rid for rid in definitions if rid not in ids)
    text = _set(text, 'TaskForceRibbons', 'RibbonIds', '|'.join(ids))
    for rid, row in definitions.items():
        if _section(text, 'Ribbon_' + rid):
            continue
        image = row.get('image') or f'campaigns/{slug}/art/ribbons/{rid}.png'
        when = _mission(slug, row['mission'])[1]
        data = dict(Type=row['type'], Precedence=row['precedence'], Name_en=row['name'], ImagePath=image)
        if row.get('medal_image'):
            data['MedalImagePath'] = row['medal_image']
        data.update(CitationIssuingBody_en='SEST Scenario Awards Board',
                    CitationIssuance_en='records the award of the',
                    CitationAwardName_en=row['name'], CitationAuthority_en='to',
                    CitationRecipient_en='{TaskForceName}' if row['recipient'] == 'unit' else '{CommanderRank} {CommanderName}',
                    CitationText_en=row['citation'], CitationDate_en=citation_date(when),
                    CitationSignatureName_en='Campaign Operations Staff',
                    CitationSignatureTitle_en='Scenario Awards Board', ReferenceSource=row['reference'])
        if row.get('stripes'):
            data['StripeColors'] = '|'.join(c for c, _w in row['stripes'])
            data['StripeWidths'] = '|'.join(f'{w:g}' for _c, w in row['stripes'])
        if row.get('source'):
            data['SourceUrl'] = row['source']
        text = text.rstrip() + f'\n\n[Ribbon_{rid}]\n' + ''.join(f'{k}={v}\n' for k, v in data.items())
    return text


# ------------------------------------------------------------------ art
def _star(draw, cx, cy, outer, inner, fill, outline):
    """A seven-pointed Federation Star."""
    import math
    points = []
    for i in range(14):
        r = outer if i % 2 == 0 else inner
        a = -math.pi / 2 + i * math.pi / 7
        points.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(points, fill=fill, outline=outline)


def _strip(stripes, device=None):
    """A 140x36 ribbon strip, the size of the native campaign pictures:
    stripes in proportion to their widths, a thin frame and woven lines."""
    from PIL import Image, ImageDraw
    image = Image.new('RGBA', (140, 36), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    total = sum(w for _c, w in stripes)
    run = 0
    for colour, width in stripes:
        left = round(2 + 136 * run / total)
        run += width
        draw.rectangle((left, 3, round(2 + 136 * run / total), 32), fill=colour)
    if device == 'federation_star':
        # Nickel-silver row of flames, 22 of the ribbon's 32 mm, tapering
        # from the centre, with the 7 mm Federation Star on it.
        silver = '#C9CDD1'
        draw.polygon([(23, 18), (70, 15), (117, 18), (70, 21)], fill=silver, outline='#8C939A')
        _star(draw, 70, 18, 10, 4.6, silver, '#8C939A')
    elif device == 'silver_frame':
        # Rhodium-plated frame with flames from its outer edges round an
        # old-gold bar, and the Federation Star at the centre.
        silver, edge = '#D3D7DB', '#8C939A'
        draw.rectangle((2, 3, 138, 32), outline=silver, width=5)
        draw.rectangle((2, 3, 138, 32), outline=edge, width=1)
        draw.rectangle((7, 8, 133, 27), outline=edge, width=1)
        for x in range(10, 132, 8):
            draw.polygon([(x, 3), (x + 4, 0), (x + 8, 3)], fill=silver, outline=edge)
            draw.polygon([(x, 32), (x + 4, 35), (x + 8, 32)], fill=silver, outline=edge)
        _star(draw, 70, 17.5, 8, 3.7, silver, edge)
    elif device == 'gold_frame':
        draw.rectangle((2, 3, 138, 32), outline='#C9A227', width=3)
        draw.rectangle((2, 3, 138, 32), outline='#8A6D14', width=1)
    if device not in ('silver_frame', 'gold_frame'):
        draw.rectangle((1, 2, 138, 33), outline='#B0B4B8', width=1)
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    stitches = ImageDraw.Draw(overlay)
    for y in range(5, 32, 3):
        stitches.line((3, y, 136, y), fill=(255, 255, 255, 22))
    return Image.alpha_composite(image, overlay)


def sources_text(slug):
    """This campaign's art/ribbons/SOURCES.txt: what each picture is."""
    slug = base_slug(slug)
    rows = catalogue(slug)
    title = CAMPAIGNS[slug][2]
    lines = [f'SEST award artwork - {title}', '',
             'Code-drawn strips (integration/campaign/service_awards.py). No AI imagery;',
             'nothing traced. Real-award strips follow the published stripe order and',
             'proportions closely enough to be recognised; they are representations.']
    for rid, row in rows.items():
        if row.get('stripes'):
            kind = ('fictional SEST design' if row['reference'] == 'Fictional' else
                    f'representation of the {ADJECTIVE.get(row["reference"], (row["reference"], ""))[0]} award')
            lines.append(f'  {rid}.png - {row["name"]}: {kind}')
    stock = [(rid, row) for rid, row in rows.items() if row.get('image')]
    if stock:
        lines += ['', 'Installed Sea Power pictures referenced by path, not copied into this pack:']
        lines += [f'  {row["image"]} - {row["name"]}' + (' (no longer granted)' if row.get('retired') else '')
                  for rid, row in stock]
    if 'sest_aosm_indo_pacific' in rows:
        lines += ['', 'sest_aosm_indo_pacific.png - Australian Operational Service Medal - Indo-Pacific',
                  'Author: Nford24. CC0 1.0 Universal Public Domain Dedication.',
                  'Source: https://commons.wikimedia.org/wiki/File:Australian_Operational_Service_Medal_-_Indo-Pacific.png',
                  'Copied without modification (897 bytes). Its stripes - deep blue edges as wide as the',
                  'green, light blue, green, a yellow centre - match the Defence description.']
    if any(n in NATION_SETTINGS and NATION_SETTINGS[n]['emblem'].rsplit('/', 1)[1].startswith('sest_')
           for n in NATIONS.get(slug, ())):
        lines += ['', 'Royal Navy emblem (ui/campaign/navy_emblems/sest_rn_emblem.png): the White Ensign,',
                  'from the SEST gallery flag set (File:Naval ensign of the United Kingdom.svg, Wikimedia',
                  'Commons, public domain; credited in Gallery/VISUAL_CREDITS.txt), scaled by build_pack.py.']
    real = [(rid, row) for rid, row in rows.items() if row['reference'] != 'Fictional' and row.get('source')]
    if real:
        lines += ['', 'Award facts (criteria, ribbon design, precedence):']
        lines += [f'  {row["name"]}: {row["source"]}' for _rid, row in real]
    lines += ['', 'Every real-award citation says it is a game award for a fictional operation,',
              'not a real honour.']
    return '\n'.join(lines) + '\n'


def render(campaign_directory, slug):
    """Draw the strips, copy the sourced AOSM strip unaltered and write the
    campaign's SOURCES.txt."""
    slug = base_slug(slug)
    folder = Path(campaign_directory) / 'art/ribbons'
    folder.mkdir(parents=True, exist_ok=True)
    for rid, row in catalogue(slug).items():
        if row.get('image'):
            continue  # an installed Sea Power picture
        path = folder / (rid + '.png')
        if rid == 'sest_aosm_indo_pacific':
            shutil.copyfile(HERE / 'assets/ribbons/aosm_indo_pacific.png', path)
            continue
        _strip(row['stripes'], row.get('device')).save(path)
    (folder / 'SOURCES.txt').write_text(sources_text(slug), encoding='utf-8')


def mission_awards(slug, mission, final=False):
    """Native grammar: award IDs separated by pipes; nations after commas.

    Every mission the award table names is held to it here - its title and
    date are what the citations print - and a 30-day service medal to the
    operation's first day."""
    slug = base_slug(slug)
    if slug not in CAMPAIGNS:
        return []
    code = mission.get('code', 'SW' + mission.get('num', ''))
    if final and code != FINAL[slug]:
        raise ValueError(f'{slug}: the final mission is {code}, the award table says {FINAL[slug]}')
    ids = ([award_id(slug)] if final else []) + [rid for rid, at in grants(slug).items()
                                                  if at == code and rid != award_id(slug)]
    for rid in ids:
        days = REAL.get(rid, {}).get('service_days')
        if days and 'date' in mission:
            start = date(*_mission(slug, FIRST[slug])[1])
            if (date(*mission['date']) - start).days < days:
                raise ValueError(f'{rid}: a {days}-day service medal must follow {days} campaign days')
    row = MISSIONS[slug].get(code)
    if row and (mission.get('key', row[0]) != row[0] or tuple(mission.get('date', row[1])) != tuple(row[1])):
        raise ValueError(f'{slug} {code}: the mission is {mission.get("key")!r} on {mission.get("date")}, '
                         f'the award table says {row[0]!r} on {row[1]} - update MISSIONS')
    out = []
    for rid in ids:
        nation = REAL.get(rid, {}).get('nation')
        if nation and nation not in NATIONS.get(slug, ()):
            raise ValueError(f'{slug}: {rid} is for {nation}, which the campaign does not offer')
        out.append(rid + (',' + nation if nation else ''))
    return out


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
