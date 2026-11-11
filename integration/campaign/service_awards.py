"""Native SEST campaign awards, commander nations and real-award representations.

The game's own rules, read from Seapower-Scripts.dll (0.8.7-261107) as IL:

- [CommanderSettings] CommanderNations is split on '|'. For each nation key N
  the commander screen reads CommanderNameDefaultN, CommanderNamePoolN (a
  Names_ section of language_<xx>/ui.ini; SEST adds pools for the nations
  the game has none for, NAME_POOLS), NavyNameN, NavyEmblemN and
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
import textwrap

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
        'RLC1': ('Pilot in the Water', (2028, 11, 24), 'in Pilot in the Water'),
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
# nation the story can put in command of the group. Southern Watch and
# Southern Reach are Australian-led coalition groups. They offer the navies
# whose hulls the allied fleet sells (allied_fleet.py) and Japan's, whose ASW
# group is in the story (SW10), and since the owner's plan of 10 Nov 2026
# New Zealand's, the Tasman story's own navy, and Canada's. Keys are the
# game's own (language_en/nations.ini): the discount and the award selectors
# compare them with the units' Nation=, so 'New Zealand' or 'South Korea'
# with a space would match nothing. Red Line is a PLAN group. Sulu Line is
# Philippine-led; the Thai detachment and the single RAN frigate serve under
# it, and a Thai or Australian officer may be appointed to command it.
NATIONS = {
    'sest-southern-watch': ('Australia', 'US', 'UK', 'Japan', 'NewZealand', 'France', 'Canada',
                            'South_Korea', 'Spain', 'Italy', 'Germany', 'Netherlands', 'Norway',
                            'Denmark'),
    'sest-southern-reach': ('Australia', 'US', 'UK', 'Japan', 'NewZealand', 'France', 'Canada',
                            'South_Korea', 'Spain', 'Italy', 'Germany', 'Netherlands', 'Norway',
                            'Denmark'),
    'sest-red-line': ('China',),
    'sest-sulu-line': ('Philippines', 'Thailand', 'Australia'),
}
# Adjective and article for a citation, the rules page and RIBBONS.txt.
ADJECTIVE = {'Australia': ('Australian', 'an'), 'US': ('American', 'an'), 'UK': ('British', 'a'),
             'Japan': ('Japanese', 'a'), 'China': ('Chinese', 'a'), 'Philippines': ('Philippine', 'a'),
             'NewZealand': ('New Zealand', 'a'), 'France': ('French', 'a'), 'Canada': ('Canadian', 'a'),
             'South_Korea': ('South Korean', 'a'), 'Spain': ('Spanish', 'a'), 'Italy': ('Italian', 'an'),
             'Germany': ('German', 'a'), 'Netherlands': ('Dutch', 'a'), 'Norway': ('Norwegian', 'a'),
             'Denmark': ('Danish', 'a'), 'Thailand': ('Thai', 'a'),
             # No campaign offers a Russian commander yet; the key is the game's
             # Russia, which SEST Collection Fixes now registers modern Russian
             # hulls to (its RU_REREGISTER), so a future one reads 'a Russian commander'.
             'Russia': ('Russian', 'a')}

# Every SEST ladder puts the NATO grades OF-D..OF-9 at levels 1-10, the levels
# the Australian ladder uses for the same grades: Commander (OF-4) 5, Captain
# (OF-5) 6, Commodore (OF-6) 7. The campaigns start at 5 (Southern Watch), 6
# (Southern Reach), 7 (Sulu Line) and 8 (Red Line). The game ships rank
# insignia for three navies only, so the image field is empty, as in Red
# Line and Sulu Line.
GRADES = ('OF-D', 'OF-1', 'OF-2', 'OF-3', 'OF-4', 'OF-5', 'OF-6', 'OF-7', 'OF-8', 'OF-9')


def _ladder(*ranks):
    """Ten 'Title,ABBR' strings, junior first -> an [OfficerRanks] value:
    title, abbreviation, grade, level and an empty insignia."""
    if len(ranks) != len(GRADES):
        raise ValueError(f'a ladder has {len(GRADES)} ranks, not {len(ranks)}')
    return '|'.join(f'{rank},{grade},{level},' for level, (rank, grade) in enumerate(zip(ranks, GRADES), 1))


# Royal Navy officer ranks.
UK_RANKS = ('Midshipman,MID,OF-D,1,|Sub-Lieutenant,SLT,OF-1,2,|Lieutenant,LT,OF-2,3,|'
            'Lieutenant Commander,LT CDR,OF-3,4,|Commander,CDR,OF-4,5,|Captain,CAPT,OF-5,6,|'
            'Commodore,CDRE,OF-6,7,|Rear Admiral,RADM,OF-7,8,|Vice Admiral,VADM,OF-8,9,|'
            'Admiral,ADM,OF-9,10,')
# The other navies' ladders were researched for the owner's plan of 10 Nov
# 2026 from each navy's published titles: NZDF 'Our ranks'; Ley 39/2007 art.
# 21.2 for the Armada; the German presidential order of 30 Aug 2021; Danish
# order no. 294 of 24 March 2010; the ROK Military Personnel Management Act,
# art. 3; and for the rest Wikipedia's NATO rank tables, which cite each
# navy's own pages. Where a navy has no OF-D rank the nearest cadet title
# fills level 1, and where it lists two OF-1 ranks the senior one takes level
# 2. Navies that use only their own language keep their own titles and
# official accents (Latin-1, which the English UI draws: stock unit names
# ship 'Andalucía F72' and 'Snøgg'). Korea and Thailand publish English
# titles; the game font has no Hangul or Thai. The Royal Thai Navy has no
# one-star rank: a Captain on the special grade, which ranks above a
# Captain, is placed at OF-6, level 7, the Sulu Line starting level. Several
# abbreviations are the navies' conventional forms, not read from an
# official list.
NEWZEALAND_RANKS = _ladder(
    'Midshipman,MID', 'Sub Lieutenant,SLT', 'Lieutenant,LT', 'Lieutenant Commander,LTCDR',
    'Commander,CDR', 'Captain,CAPT', 'Commodore,CDRE', 'Rear Admiral,RADM', 'Vice Admiral,VADM',
    'Admiral,ADM')
FRANCE_RANKS = _ladder(
    'Aspirant,ASP', 'Enseigne de vaisseau de 1re classe,EV1', 'Lieutenant de vaisseau,LV',
    'Capitaine de corvette,CC', 'Capitaine de frégate,CF', 'Capitaine de vaisseau,CV',
    'Contre-amiral,CA', 'Vice-amiral,VA', "Vice-amiral d'escadre,VAE", 'Amiral,AL')
CANADA_RANKS = _ladder(
    'Naval Cadet,NCdt', 'Sub-Lieutenant,SLt', 'Lieutenant(N),Lt(N)', 'Lieutenant-Commander,LCdr',
    'Commander,Cdr', 'Captain(N),Capt(N)', 'Commodore,Cmdre', 'Rear-Admiral,RAdm',
    'Vice-Admiral,VAdm', 'Admiral,Adm')
SOUTH_KOREA_RANKS = _ladder(
    'Midshipman,MIDN', 'Lieutenant Junior Grade,LTJG', 'Lieutenant,LT', 'Lieutenant Commander,LCDR',
    'Commander,CDR', 'Captain,CAPT', 'Rear Admiral (Lower Half),RDML', 'Rear Admiral,RADM',
    'Vice Admiral,VADM', 'Admiral,ADM')
SPAIN_RANKS = _ladder(
    'Guardiamarina,GM', 'Alférez de navío,AN', 'Teniente de navío,TN', 'Capitán de corbeta,CC',
    'Capitán de fragata,CF', 'Capitán de navío,CN', 'Contralmirante,CA', 'Vicealmirante,VA',
    'Almirante,ALM', 'Almirante general,AG')
ITALY_RANKS = _ladder(
    'Aspirante guardiamarina,ASP GM', 'Sottotenente di vascello,STV', 'Tenente di vascello,TV',
    'Capitano di corvetta,CC', 'Capitano di fregata,CF', 'Capitano di vascello,CV',
    'Contrammiraglio,CA', 'Ammiraglio di divisione,AMM DIV', 'Ammiraglio di squadra,AMM SQ',
    'Ammiraglio,AMM')
GERMANY_RANKS = _ladder(
    'Oberfähnrich zur See,OFähnr zS', 'Oberleutnant zur See,OLt zS', 'Kapitänleutnant,KptLt',
    'Korvettenkapitän,KKpt', 'Fregattenkapitän,FKpt', 'Kapitän zur See,Kpt zS',
    'Flottillenadmiral,FltlAdm', 'Konteradmiral,KAdm', 'Vizeadmiral,VAdm', 'Admiral,Adm')
NETHERLANDS_RANKS = _ladder(
    'Adelborst,ADB', 'Luitenant ter zee der 2de klasse,LTZ2',
    'Luitenant ter zee der 2de klasse oudste categorie,LTZ2OC', 'Luitenant ter zee der 1ste klasse,LTZ1',
    'Kapitein-luitenant ter zee,KLTZ', 'Kapitein ter zee,KTZ', 'Commandeur,CDR', 'Schout-bij-nacht,SBN',
    'Vice-admiraal,VADM', 'Luitenant-admiraal,LADM')
NORWAY_RANKS = _ladder(
    'Kadett,KAD', 'Løytnant,LT', 'Kapteinløytnant,KLT', 'Orlogskaptein,OK', 'Kommandørkaptein,KK',
    'Kommandør,KOM', 'Flaggkommandør,FKOM', 'Kontreadmiral,KADM', 'Viseadmiral,VADM', 'Admiral,ADM')
DENMARK_RANKS = _ladder(
    'Kadet,KAD', 'Premierløjtnant,PL', 'Kaptajnløjtnant,KL', 'Orlogskaptajn,OK', 'Kommandørkaptajn,KK',
    'Kommandør,KD', 'Flotilleadmiral,FLADM', 'Kontreadmiral,KADM', 'Viceadmiral,VADM', 'Admiral,ADM')
THAILAND_RANKS = _ladder(
    'Naval Cadet,NCDT', 'Lieutenant Junior Grade,LTJG', 'Lieutenant,LT', 'Lieutenant Commander,LCDR',
    'Commander,CDR', 'Captain,CAPT', 'Captain (Special Grade),CAPT (SG)', 'Rear Admiral,RADM',
    'Vice Admiral,VADM', 'Admiral,ADM')

# The settings a nation needs when a campaign's own COMMANDER text does not
# define it. US, Japan and Australia are the stock Pacific Strike values (its
# default names, pools, navies, emblems and rank ladders; Australia's row
# serves Sulu Line, whose own text defines only the Philippines). The others
# use a stock [Names_X] pool where the game ships one, or a SEST pool
# (NAME_POOLS below), and an emblem build_pack.write_emblems draws from the
# SEST gallery's public-domain flag set (build_pack.SEST_EMBLEMS): `commons`
# names the file it came from and `about` says what it shows, for SOURCES.txt.
# A naval ensign where the set has one; otherwise the national flag, which is
# the ensign itself for France, Canada, South Korea, the Netherlands and Spain
# (flown with the arms), and is said not to be for Germany, Norway, Denmark
# and Thailand. Default names are the research's: built from the nation's
# pool and searched against serving officers, or the game's own (Germany's
# Moritz Ehlers is the stock file's unused default).
_EMBLEMS = 'ui/campaign/navy_emblems/'
NATION_SETTINGS = {
    'US': dict(name='Alex Morgan', pool='Names_USA', navy='United States Navy',
               emblem=_EMBLEMS + 'usn_emblem.png', ranks=None),
    'UK': dict(name='Julian Northcott', pool='Names_UK', navy='Royal Navy',
               emblem=_EMBLEMS + 'sest_rn_emblem.png', ranks=UK_RANKS,
               commons='File:Naval ensign of the United Kingdom.svg', about='the White Ensign'),
    'Japan': dict(name='Hiroshi Watanabe', pool='Names_Japan', navy='Japan Maritime Self-Defense Force',
                  emblem=_EMBLEMS + 'jmsdf_emblem.png', ranks=None),
    'Australia': dict(name='Grant Morrison', pool='Names_Australia', navy='Royal Australian Navy',
                      emblem=_EMBLEMS + 'ran_emblem.png', ranks=None),
    'NewZealand': dict(name='Rawiri Tipene', pool='Names_NewZealand', navy='Royal New Zealand Navy',
                       emblem=_EMBLEMS + 'sest_rnzn_emblem.png', ranks=NEWZEALAND_RANKS,
                       commons='File:Naval Ensign of New Zealand.svg', about='the New Zealand naval ensign'),
    'France': dict(name='Arnaud Vasseur', pool='Names_France', navy='Marine nationale',
                   emblem=_EMBLEMS + 'sest_mn_emblem.png', ranks=FRANCE_RANKS,
                   commons='File:Flag of France.svg',
                   about='the French national flag, which the Marine nationale flies as its ensign'),
    'Canada': dict(name='Denis Arsenault', pool='Names_Canada', navy='Royal Canadian Navy',
                   emblem=_EMBLEMS + 'sest_rcn_emblem.png', ranks=CANADA_RANKS,
                   commons='File:Flag of Canada.svg',
                   about='the Canadian national flag, which the Royal Canadian Navy flies as its ensign'),
    # Given name first, as the pool generates it and as stock writes
    # 'Hiroshi Watanabe' (10 Nov 2026; it was 'Han Seongjin').
    'South_Korea': dict(name='Seongjin Han', pool='Names_South_Korea', navy='Republic of Korea Navy',
                        emblem=_EMBLEMS + 'sest_rokn_emblem.png', ranks=SOUTH_KOREA_RANKS,
                        commons='File:Flag of South Korea.svg',
                        about='the South Korean national flag, which the Republic of Korea Navy flies '
                              'as its ensign'),
    'Spain': dict(name='Gonzalo Iglesias Prieto', pool='Names_Spain', navy='Armada Española',
                  emblem=_EMBLEMS + 'sest_armada_emblem.png', ranks=SPAIN_RANKS,
                  commons='File:Flag of Spain.svg',
                  about='the Spanish national flag with the arms, which the Armada flies as its ensign'),
    'Italy': dict(name='Corrado Mariani', pool='Names_Italy', navy='Marina Militare',
                  emblem=_EMBLEMS + 'sest_mm_emblem.png', ranks=ITALY_RANKS,
                  commons='File:Naval ensign of Italy.svg', about='the Italian naval ensign'),
    'Germany': dict(name='Moritz Ehlers', pool='Names_Germany', navy='Deutsche Marine',
                    emblem=_EMBLEMS + 'sest_dm_emblem.png', ranks=GERMANY_RANKS,
                    commons='File:Flag of Germany.svg',
                    about='the German national flag. The Deutsche Marine\'s ensign is the federal '
                          'service flag, with the federal arms, swallow-tailed; the gallery set has no '
                          'file for it'),
    'Netherlands': dict(name='Joost Brouwer', pool='Names_Netherlands', navy='Koninklijke Marine',
                        emblem=_EMBLEMS + 'sest_km_emblem.png', ranks=NETHERLANDS_RANKS,
                        commons='File:Flag of the Netherlands.svg',
                        about='the Dutch national flag, which the Koninklijke Marine flies as its ensign'),
    'Norway': dict(name='Eivind Brekke', pool='Names_Norway', navy='Sjøforsvaret',
                   emblem=_EMBLEMS + 'sest_rnon_emblem.png', ranks=NORWAY_RANKS,
                   commons='File:Flag of Norway.svg',
                   about='the Norwegian national flag. The naval ensign is its swallow-tailed form '
                         'with a tongue; the gallery set has no file for it'),
    'Denmark': dict(name='Mads Holm Kristensen', pool='Names_Denmark', navy='Søværnet',
                    emblem=_EMBLEMS + 'sest_rdn_emblem.png', ranks=DENMARK_RANKS,
                    commons='File:Flag of Denmark.svg',
                    about='the Danish national flag. The naval ensign, the Orlogsflag, is its '
                          'swallow-tailed form in a deeper red; the gallery set has no file for it'),
    'Thailand': dict(name='Suphachai Kaeokham', pool='Names_Thailand', navy='Royal Thai Navy',
                     emblem=_EMBLEMS + 'sest_rtn_emblem.png', ranks=THAILAND_RANKS,
                     commons='File:Flag of Thailand.svg',
                     about='the Thai national flag. The Royal Thai Navy\'s ensign adds a white '
                           'elephant on a red disc at its centre; the gallery set has no file for it'),
}

# Emblems a campaign's own COMMANDER text names rather than a row above
# (Sulu Line's Philippine Navy, Red Line's PLA Navy), credited the same way
# in SOURCES.txt: build_pack.SEST_EMBLEMS draws them from the gallery set.
CAMPAIGN_EMBLEMS = {
    'sest_pn_emblem.png': dict(commons='File:Flag of the Philippines.svg',
                               about='the Philippine national flag, which the Philippine Navy flies as '
                                     'its ensign'),
    'sest_plan_emblem.png': dict(commons='File:Naval Ensign of China.svg',
                                 about='the Chinese naval ensign'),
}


def emblem_credits(slug, commander=''):
    """[(file, navy, about, commons)] for every SEST emblem (sest_*) a
    NavyEmblem key of the campaign's commander text names, in the order the
    text names them: what build_pack.write_emblems draws. The text is the
    campaign's commander_settings.ini; without one, the nations
    NATION_SETTINGS adds. An emblem with no credit stops the build."""
    text = _nations(commander or '', base_slug(slug))
    values = _section(text, 'CommanderSettings')
    credits = {row['emblem'].rsplit('/', 1)[1]: row for row in NATION_SETTINGS.values() if row.get('commons')}
    credits.update(CAMPAIGN_EMBLEMS)
    out, seen = [], set()
    # The pattern build_pack.write_emblems draws from.
    for nation, path in re.findall(r'^NavyEmblem(\w+)=(ui/campaign/navy_emblems/sest_[^\s]+)$', text, re.M):
        name = path.rsplit('/', 1)[1]
        if name in seen:
            continue
        seen.add(name)
        if name not in credits:
            raise ValueError(f'{slug}: NavyEmblem{nation} names {name}, which no NATION_SETTINGS row '
                             'or CAMPAIGN_EMBLEMS entry credits')
        row = credits[name]
        out.append((name, values.get('NavyName' + nation, '').strip(), row['about'], row['commons']))
    return out


# SEST name pools for the nations the game ships none for (stock
# language_en/ui.ini has [Names_X] for Argentina, Australia, Canada, China,
# France, Germany, India, Iran, Iraq, Italy, Japan, Norway, Pakistan, South
# Africa, Soviet, Spain, UK and USA). build_pack writes them to
# language_en/sest_name_pools.ini in the campaign pack. The game merges
# language files key by key across the load order whatever the file is
# called (Southern Watch build notes, the loading-screen tips), so these
# sections add to the stock pools and replace none: a section stock already
# has stops the build (name_pools_text). The stock format: three
# comma-separated lists with no spaces, ASCII, male names, 50 each; '_' for
# no middle names, as stock Names_Japan. From the research of 10 Nov 2026:
# Korean given names in Revised Romanization, surnames in their customary
# passport forms (2015 census top 50, Kim first); New Zealand English names
# with Maori names, macrons dropped as stock drops diacritics; Dutch
# particles joined in the stock South African style (vanDerMerwe); Danish
# letters folded as stock Names_Norway folds them; Thai names in the Royal
# Thai General System. Whether a pool the commander screen draws from comes
# out given name or surname first is a PC check.
NAME_POOLS = {
    'Names_NewZealand': (
        'James,Christopher,Benjamin,Aaron,Luke,Adam,Peter,Joseph,Thomas,William,John,Michael,Daniel,David,'
        'Matthew,Andrew,Mark,Richard,Scott,Craig,Shane,Nathan,Hayden,Bradley,Jamie,Samuel,Nicholas,Jonathan,'
        'Timothy,Simon,Paul,Grant,Brendon,Blair,Hamish,Cameron,Duncan,Kieran,Wiremu,Rawiri,Hemi,Tamati,Tane,'
        'Mikaere,Matiu,Ihaia,Kahu,Manaia,Hone,Rangi',
        'James,John,Michael,David,Andrew,Peter,Robert,William,Thomas,Richard,Paul,Mark,Daniel,Matthew,'
        'Christopher,Stephen,Alexander,Edward,George,Charles,Ian,Scott,Craig,Grant,Hamish,Alan,Bruce,Graham,'
        'Kenneth,Murray,Neil,Ross,Stuart,Malcolm,Anthony,Joseph,Patrick,Francis,Henry,Lee,Wiremu,Rawiri,Hemi,'
        'Tamati,Hone,Rangi,Matiu,Tane,Mikaere,Ihaia',
        'Smith,Williams,Wilson,Brown,Taylor,Jones,Thompson,Anderson,Walker,Campbell,Stewart,Robinson,Clark,'
        'Mitchell,Scott,Young,King,Martin,White,Harris,Hall,Wright,Watson,Edwards,Hughes,Kelly,Ryan,Murray,'
        'Reid,Fraser,Ross,Robertson,Johnston,Cameron,Ngata,Parata,Tipene,Henare,Tamihana,Hohepa,Rewiti,'
        'Herewini,Paki,Karaka,Kereama,Nikora,Waaka,Tomoana,Leota,Fifita'),
    'Names_South_Korea': (
        'Jihun,Hyeonu,Seongmin,Seonghyeon,Minsu,Junyeong,Junho,Mingyu,Donghyeon,Seunghyeon,Jeonghun,'
        'Seonghun,Jinho,Minho,Seongho,Seongjin,Jeongho,Sanghun,Yeongjin,Hyeonjun,Junhyeok,Seungmin,Minjae,'
        'Sangmin,Jaehun,Jaehyeon,Jaeho,Sangho,Taehun,Taeho,Jongmin,Jonghyeon,Yongjun,Sanghyeon,Jaeyeong,'
        'Hyeongjun,Seungho,Donghun,Daehyeon,Jeongmin,Minseok,Hyeonseok,Wonseok,Changmin,Seokjin,Jaemin,Jinu,'
        'Taehyeon,Junseok,Jaewon',
        '_',
        'Kim,Lee,Park,Jung,Choi,Cho,Kang,Jang,Yoon,Lim,Shin,Yoo,Han,Oh,Seo,Jeon,Kwon,Hwang,Ahn,Song,Hong,'
        'Yang,Ko,Moon,Son,Bae,Baek,Heo,Noh,Nam,Shim,Ha,Joo,Koo,Kwak,Sung,Woo,Cha,Jin,Min,Ryu,Na,Ji,Um,Byun,'
        'Chae,Won,Bang,Cheon,Kong'),
    'Names_Netherlands': (
        'Jeroen,Dennis,Martijn,Mark,Robert,Michael,Kevin,Jan,Johan,Sander,Bas,Niels,Thijs,Joost,Wouter,'
        'Maarten,Pieter,Bart,Koen,Joris,Arjen,Remco,Erik,Marco,Rob,Ruben,Stefan,Tim,Thomas,Patrick,Richard,'
        'Vincent,Edwin,Rick,Jasper,Gijs,Ivo,Frank,Michiel,Rutger,Sjoerd,Willem,Hugo,Tom,Menno,Floris,Laurens,'
        'Peter,Paul,Erwin',
        'Johannes,Hendrik,Willem,Jan,Pieter,Cornelis,Jacobus,Gerardus,Adrianus,Antonius,Petrus,Franciscus,'
        'Hubertus,Theodorus,Wilhelmus,Marinus,Arie,Dirk,Klaas,Gerrit,Hendrikus,Johan,Martinus,Nicolaas,'
        'Paulus,Bernardus,Leonardus,Josephus,Albert,Frederik,Karel,Maarten,Jeroen,Thomas,Michiel,Robert,Erik,'
        'Frank,Marc,Bart,Sander,Joost,Floris,Laurens,Rutger,Arjen,Wouter,Bas,Koen,Daan',
        'deJong,Jansen,deVries,vanDenBerg,vanDijk,Bakker,Janssen,Visser,Smit,Meijer,deBoer,Mulder,deGroot,'
        'Bos,Vos,Peters,Hendriks,vanLeeuwen,Dekker,Brouwer,deWit,Dijkstra,Smits,deGraaf,vanDerMeer,Kok,'
        'Jacobs,deHaan,Vermeulen,vanDenHeuvel,vanDerVeen,vanDenBroek,deBruijn,vanDerHeijden,Schouten,vanBeek,'
        'Willems,vanVliet,vanDeVen,Hoekstra,Maas,Verhoeven,Koster,vanDam,Prins,Blom,Huisman,Kramer,Postma,'
        'Kuipers'),
    'Names_Denmark': (
        'Peter,Michael,Lars,Jens,Thomas,Henrik,Soren,Christian,Martin,Jan,Niels,Anders,Morten,Jesper,Mads,'
        'Rasmus,Mikkel,Kasper,Jacob,Jonas,Simon,Nicolai,Kristian,Daniel,Brian,Kenneth,Allan,Dennis,Claus,Kim,'
        'Rene,Bo,Steen,Torben,Ole,Per,Hans,Poul,Erik,Klaus,Carsten,Frank,Bjarne,Lasse,Esben,Troels,Rune,'
        'Jeppe,Ulrik,Steffen',
        'Peter,Michael,Lars,Jens,Thomas,Henrik,Soren,Christian,Martin,Niels,Anders,Morten,Mads,Rasmus,'
        'Mikkel,Jacob,Kristian,Erik,Hans,Ole,Per,Poul,Frederik,Emil,Johan,Carl,Aksel,Bo,Kim,Jan,Steen,Claus,'
        'Kasper,Simon,Ulrik,Holm,Skov,Lund,Bach,Dahl,Krogh,Juul,Friis,Bech,Kjaer,Damgaard,Toft,Lykke,Bruun,'
        'Munk',
        'Nielsen,Jensen,Hansen,Pedersen,Andersen,Christensen,Larsen,Sorensen,Rasmussen,Jorgensen,Petersen,'
        'Madsen,Kristensen,Olsen,Thomsen,Christiansen,Poulsen,Johansen,Moller,Mortensen,Knudsen,Jakobsen,'
        'Jacobsen,Mikkelsen,Olesen,Frederiksen,Laursen,Henriksen,Lund,Schmidt,Eriksen,Holm,Kristiansen,'
        'Clausen,Simonsen,Svendsen,Andreasen,Iversen,Ostergaard,Jeppesen,Vestergaard,Lauridsen,Nissen,'
        'Mogensen,Jespersen,Kjaer,Norgaard,Dahl,Skov,Bach'),
    'Names_Thailand': (
        'Somchai,Prasoet,Sombun,Somsak,Narong,Wichai,Suchat,Anan,Chatchai,Kittisak,Natthaphong,Thanakon,'
        'Worawut,Phongsak,Surasak,Sutthiphong,Wirot,Aphichat,Ekkachai,Chakkrit,Kriangkrai,Nopphadon,Phairot,'
        'Sakda,Suphachai,Surachai,Thawatchai,Thirawat,Thanawat,Wanchai,Wirachai,Yutthana,Anucha,Prasit,'
        'Pricha,Sarawut,Chaiwat,Sombat,Somphong,Chaloemchai,Sitthichai,Thiraphong,Wirayut,Phonchai,Chirawat,'
        'Siriphong,Watcharaphon,Kittiphong,Chanchai,Thongchai',
        '_',
        'Sisuk,Thongdi,Bunma,Kaeokham,Chanthong,Saengthong,Phromma,Suksawat,Charoensuk,Thongkham,Wongkham,'
        'Suwannarat,Rungrueang,Kaeomani,Bunyuen,Chaiyasit,Sukprasoet,Thongsuk,Siwong,Inthawong,Saengsuwan,'
        'Bunrueang,Chaiwong,Sirisuk,Duangdi,Kongkaeo,Phuangmali,Suksombun,Charoenrat,Panyasiri,Wongkaeo,'
        'Rueangsi,Khamsuk,Bunsong,Saisuwan,Chuenchom,Thongprasoet,Rattanaphon,Siriwat,Phongphan,Chantharat,'
        'Kaeosai,Prasoetsuk,Sukkasem,Thongyu,Bunthong,Saengchan,Wongthai,Inkaeo,Chaisiri'),
}
NAME_POOL_FILE = 'language_en/sest_name_pools.ini'
STOCK_UI = ROOT / 'mods-source/_vanilla/original/language_en/ui.ini'


def name_pools_text():
    """language_en/sest_name_pools.ini: the SEST [Names_X] sections. A
    section the stock ui.ini already has would overwrite the game's own pool
    key by key, so it stops the build."""
    stock = set(re.findall(r'^\[(Names_\w+)\]', STOCK_UI.read_text(encoding='utf-8-sig'), re.M))
    lines = ['# SEST commander name pools for the nations the game ships none for.',
             '# Language files merge key by key across the load order, so these',
             '# sections add to the game\'s own [Names_X] pools and replace none.',
             '# integration/campaign/service_awards.py (NAME_POOLS) writes this file.']
    for section, (first, middle, last) in NAME_POOLS.items():
        if section in stock:
            raise ValueError(f'{section} is a stock pool; a SEST file must not overwrite it')
        lines += ['', f'[{section}]', f'FirstNames={first}', f'MiddleNames={middle}', f'LastNames={last}']
    return '\n'.join(lines) + '\n'


def unknown_pools(commander):
    """The CommanderNamePool values a commander_settings text names that
    neither the stock ui.ini nor NAME_POOLS defines."""
    stock = set(re.findall(r'^\[(Names_\w+)\]', STOCK_UI.read_text(encoding='utf-8-sig'), re.M))
    named = re.findall(r'^CommanderNamePool\w+=(.+?)\s*$', commander, re.M)
    return sorted({p for p in named if p not in stock and p not in NAME_POOLS})


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
# Runtime mission ribbons. SEST's beta runtime grants these, the game never
# does: MissionAwards.cs (Runtime 1.6.5, beta R13, on
# feature/runtime-mission-awards-20261110) reads a key the game ignores,
#   [Mission<N>] SestRuntimeRibbonAwards=<spec>[|<spec>...]
#   <spec> = <ribbonId>[,<NationKey>...]?<term>[&<term>...]
#   <term> = objective:<ObjectiveId>=completed|failed|cancelled|notfailed
#          | result>=<MissionDebriefViewModel.Result name> | nolaunch | rescued>=<1-999>
# so Runtime 1.6.4 (R12) and the standard build never grant them, and
# MissionAwards=0 in plugins/sest_runtime.ini switches them off. The runtime
# adds its rows after the native completion gate, so every runtime ribbon
# also needs the mission complete at its RequiredResult, as the native ones
# do; a spec repeats no result term for that. nolaunch: no weapon launched
# and no gun round fired by any unit of the player's task force, failed
# launches included; noisemakers, chaff, decoys (MOSS), sonobuoys, CIWS
# rounds, paratroopers and fuel tanks do not count. rescued: the debrief's
# survivors rescued, which counts anyone the task force lifts from a raft,
# so a citation says survivors, never whom. Each id has a [Ribbon_<id>]
# definition, which the runtime reads, and stays out of [TaskForceRibbons]
# RibbonIds, which the developer ribbon catalogue and its grant read.
# The owner's decisions of 11 Nov 2026: Red Line only, its own fictional
# ribbons, any commander, two awards. RL05's is the stricter companion of
# its completion ribbon (sest_undersea_operations), granted beside it.
# code -> (dict(id, name, why, stripes, terms[, nations]), ...)
RUNTIME = {
    'sest-red-line': {
        'RL05': (dict(id='sest_silent_passage', name='Silent Passage Ribbon',
                      terms=(('objective', 'Passage', 'completed'), ('nolaunch',)),
                      why='For taking the submarine through the barrier to the forward box in Under the '
                          'Convergence without launching a weapon, in command of {TaskForceName}',
                      stripes=(('#0E1A2B', 6), ('#B94A48', 1), ('#2F5D50', 3), ('#9AA7B0', 8), ('#2F5D50', 3),
                               ('#B94A48', 1), ('#0E1A2B', 6))),),
        'RLC1': (dict(id='sest_personnel_recovery', name='Personnel Recovery Ribbon',
                      terms=(('objective', 'Pilot', 'completed'), ('rescued', 1)),
                      why='For completing Pilot in the Water with survivors recovered from the sea, in '
                          'command of {TaskForceName}',
                      stripes=(('#2A3244', 4), ('#B94A48', 2), ('#E8E4D8', 2), ('#D9773A', 12), ('#E8E4D8', 2),
                               ('#B94A48', 2), ('#2A3244', 4))),),
    },
}
RUNTIME_KEY = 'SestRuntimeRibbonAwards'
# MissionDebriefViewModel.Result in value order, Incomplete (0) to
# DecisiveVictory (17), as MissionAwardsTests.cs:237-240 pins it on the beta
# (language_en/ui.ini lists the same 18 Result_ names, best first).
RESULTS = ('Incomplete', 'CompleteDefeat', 'CrushingDefeat', 'DecisiveDefeat', 'MajorDefeat', 'Defeat',
           'MinorDefeat', 'MarginalDefeat', 'TechnicalDefeat', 'PyrrhicVictory', 'Draw', 'CostlyVictory',
           'MarginalVictory', 'MinorVictory', 'Victory', 'SignificantVictory', 'MajorVictory',
           'DecisiveVictory')
OBJECTIVE_STATES = ('completed', 'failed', 'cancelled', 'notfailed')
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
    # --- Canada (Meritorious Service Decorations Regulations; gg.ca order
    # of precedence) ---------------------------------------------------------
    # Both decorations are open to members of allied forces serving with or
    # in conjunction with the Canadian Forces, with no rank limit; the cross
    # is the higher. Widths are the Regulations' (s.4(5)), the blue sampled
    # from the official gg.ca photograph (ART_NOTES).
    'ca_meritorious_service_medal_military': dict(
        nation='Canada', name='Meritorious Service Medal (Military Division)', type='PersonalDecoration',
        precedence=35,
        art=(('#023A9C', 2.333), ('#FFFFFF', 2.5), ('#023A9C', 1), ('#FFFFFF', 2.5), ('#023A9C', 15.333),
             ('#FFFFFF', 2.5), ('#023A9C', 1), ('#FFFFFF', 2.5), ('#023A9C', 2.333)), ranks=(1, 10),
        merit='For a military activity performed in a highly professional manner and to a very high standard '
              'that brought benefit and honour to the Canadian Armed Forces as commander of {TaskForceName}',
        source='https://www.gg.ca/en/honours/canadian-honours/meritorious-service-decorations-civil-division/regulations'),
    'ca_meritorious_service_cross_military': dict(
        nation='Canada', name='Meritorious Service Cross (Military Division)', type='PersonalDecoration',
        precedence=32,
        art=(('#023A9C', 2.333), ('#FFFFFF', 6), ('#023A9C', 15.333), ('#FFFFFF', 6), ('#023A9C', 2.333)),
        ranks=(1, 10),
        merit='For a military activity performed in an outstandingly professional manner and to an uncommonly '
              'high standard that brought considerable benefit and great honour to the Canadian Armed Forces '
              'as commander of {TaskForceName}',
        source='https://www.gg.ca/en/honours/canadian-honours/meritorious-service-decorations-civil-division/regulations'),
    # The campaign star, granted at SR10 as the AFEM and the AOSM-IP are (the
    # owner's decision of 10 Nov 2026): a representation for the fictional
    # operation. The DND medal page gives the ribbon, red 8 | white 2 |
    # light grey 12 | white 2 | red 8 mm, and the current rule, 14 days of
    # approved service in a specified theatre in the presence of an armed
    # enemy. The citation names no real theatre or operation.
    'ca_general_campaign_star_expedition': dict(
        nation='Canada', name='General Campaign Star - Expedition', type='ServiceAward', precedence=43,
        art=(('#8C1B1D', 8), ('#FFFFFF', 2), ('#BFB7AA', 12), ('#FFFFFF', 2), ('#8C1B1D', 8)), ranks=(1, 10),
        service_days=14,
        merit='For 14 days of service in the presence of an armed enemy with {TaskForceName}',
        source='https://www.canada.ca/en/department-national-defence/services/medals/medals-chart-index/'
               'general-campaign-star-expedition-gcs-exp.html'),
    # --- New Zealand (NZDF honours pages and order of wear) ---------------
    # The DSD recognises command and leadership in an operational
    # environment, for all ranks and for allied members serving alongside
    # the NZDF; the MNZM, above every decoration in the NZ order of wear,
    # is the climax award. `ranks` is OF-3 to OF-5, the grades military
    # MNZMs go to in practice (the research's 4-6 are game levels). The
    # NZOSM's qualifying service includes seven days on a ship in an
    # operational area against a credible military threat. The NZ Antarctic
    # Medal (not for general service in Antarctica) and the Officer grade
    # are not granted.
    'nz_distinguished_service_decoration': dict(
        nation='NewZealand', name='New Zealand Distinguished Service Decoration', type='PersonalDecoration',
        precedence=59,
        art=(('#2A3D58', 6.33), ('#ECC662', 2.13), ('#B7313E', 15.08), ('#ECC662', 2.13), ('#2A3D58', 6.33)),
        ranks=(1, 10),
        merit='For distinguished military service through exceptional devotion to duty, judgement and '
              'leadership in the conduct of a military operation as commander of {TaskForceName}',
        source='https://www.nzdf.mil.nz/medals-and-service-records/medals-and-awards/explore-medals-and-awards/'
               'the-new-zealand-distinguished-service-decoration/'),
    'nz_member_order_of_merit': dict(
        nation='NewZealand', name='Member of the New Zealand Order of Merit', type='PersonalDecoration',
        precedence=35, art=(('#C74F4E', 1),), ranks=(3, 5),
        merit='For meritorious service to the Crown and the nation as commander of {TaskForceName}',
        source='https://www.nzdf.mil.nz/medals-and-service-records/medals-and-awards/explore-medals-and-awards/'
               'member-of-the-new-zealand-order-of-merit-mnzm/'),
    'nz_operational_service_medal': dict(
        nation='NewZealand', name='New Zealand Operational Service Medal', type='ServiceAward', precedence=81,
        art=(('#FFFFFF', 2.72), ('#000000', 1.58), ('#FFFFFF', 2.21), ('#000000', 6.47), ('#FFFFFF', 2.21),
             ('#000000', 1.61), ('#FFFFFF', 2.21), ('#000000', 6.47), ('#FFFFFF', 2.21), ('#000000', 1.58),
             ('#FFFFFF', 2.72)), ranks=(1, 10), service_days=7,
        merit="For seven days' operational service at sea against a credible military threat with "
              "{TaskForceName}",
        source='https://www.nzdf.mil.nz/medals-and-service-records/medals-and-awards/explore-medals-and-awards/'
               'new-zealand-operational-service-medal-nzosm/'),
    # --- France (Grande Chancellerie; Legifrance could not be opened) ------
    # Chevalier is the entry grade of both orders and keeps the strip a
    # plain ribbon. The ONM normally comes after about 15 years' service, the
    # Legion of Honour after about 20; appointments for military personnel
    # in operations abroad are made outside the quota.
    'fr_chevalier_ordre_national_du_merite': dict(
        nation='France', name='Knight of the National Order of Merit', type='PersonalDecoration',
        precedence=25, art=(('#5E8DBA', 1),), ranks=(3, 5),
        merit='For distinguished merit in the service of the nation as commander of {TaskForceName}',
        source='https://en.wikipedia.org/wiki/Ordre_national_du_M%C3%A9rite'),
    'fr_chevalier_legion_d_honneur': dict(
        nation='France', name='Knight of the Legion of Honour', type='PersonalDecoration',
        precedence=10, art=(('#AD1710', 1),), ranks=(4, 5),
        merit='For eminent merit in the service of the nation as commander of {TaskForceName}',
        source='https://en.wikipedia.org/wiki/Legion_of_Honour'),
    # --- South Korea (Decorations Act; Enforcement Decree, Annex 2) --------
    # Annex 2 gives the widths of a 38 mm ribbon and names the white; the
    # ribbon bar of both carries a taegeuk. The Samil Medal is the order
    # grade colonels and lieutenant colonels receive. The Act bars two
    # awards for one merit; a medal and an order in one campaign is the
    # game's convention.
    'kr_national_security_medal': dict(
        nation='South_Korea', name='National Security Medal', type='PersonalDecoration', precedence=30,
        art=(('#E6A947', 17.5), ('#FFFFFF', 3), ('#E6A947', 17.5)), device='taegeuk', ranks=(1, 5),
        merit='For distinguished merit in the cause of national security as commander of {TaskForceName}',
        source='https://www.sanghun.go.kr/nation/pojangDetail.html'),
    'kr_order_of_national_security_merit_samil': dict(
        nation='South_Korea', name='Order of National Security Merit, Samil Medal', type='PersonalDecoration',
        precedence=15,
        art=(('#DEB389', 2), ('#FFFFFF', 1.5), ('#DEB389', 2), ('#FFFFFF', 1.5), ('#DEB389', 24),
             ('#FFFFFF', 1.5), ('#DEB389', 2), ('#FFFFFF', 1.5), ('#DEB389', 2)), device='taegeuk',
        ranks=(4, 5),
        merit='For outstanding meritorious service in the interest of national security as commander of '
              '{TaskForceName}',
        source='https://www.sanghun.go.kr/nation/hunjangDetail.html'),
    # --- Spain (RD 1040/2003; RD 336/2018; Orden DEF/1315/2021) ------------
    # The Cruz class is for every grade below oficial general. The white
    # distinction rewards extraordinary merit outside a UN or international
    # organisation's mandate, as in this ad-hoc coalition; the red needs
    # valour and command in an operation involving armed force, so it is the
    # climax award. The campaign medal needs 30 days in the zone of
    # operations of a coalition operation abroad.
    'es_cruz_merito_naval_distintivo_blanco': dict(
        nation='Spain', name='Cross of Naval Merit with White Distinction', type='PersonalDecoration',
        precedence=32, art=(('#AF0B19', 7.5), ('#FCBD00', 15), ('#AF0B19', 7.5)), ranks=(1, 5),
        merit='For distinguished services of extraordinary merit in the performance of military duties '
              'as commander of {TaskForceName}',
        source='https://www.boe.es/buscar/act.php?id=BOE-A-2003-17107'),
    'es_cruz_merito_naval_distintivo_rojo': dict(
        nation='Spain', name='Cross of Naval Merit with Red Distinction', type='PersonalDecoration',
        precedence=20, art=(('#AF0B19', 13.125), ('#FCBD00', 3.75), ('#AF0B19', 13.125)), ranks=(1, 5),
        merit='For valour and significant qualities of command in the skilful direction and employment of '
              'own forces in an armed operation as commander of {TaskForceName}',
        source='https://www.boe.es/buscar/act.php?id=BOE-A-2003-17107'),
    'es_medalla_de_campana': dict(
        nation='Spain', name='Spanish Campaign Medal', type='ServiceAward', precedence=95,
        art=(('#1D256E', 3), ('#D12424', 1.25), ('#FBE307', 2.5), ('#D12424', 1.25), ('#1D256E', 14),
             ('#D12424', 1.25), ('#FBE307', 2.5), ('#D12424', 1.25), ('#1D256E', 3)), ranks=(1, 10),
        service_days=30,
        merit="For 30 days' service in the zone of operations of a coalition operation abroad with "
              "{TaskForceName}",
        source='https://www.boe.es/buscar/act.php?id=BOE-A-2018-7834'),
    # --- Germany (VerdOrdenStat; StiftEinsatzMedBWErl 2025) ----------------
    # The Cross of Honour in Gold is the Bundeswehr's merit award after 20
    # years' service (an officer of 25 years may already hold it; a grade is
    # not given twice). The Federal Cross of Merit on Ribbon is the Federal
    # President's order, senior to it. The bronze deployment medal needs 30
    # days abroad on a deployment; its clasp would name the deployment.
    'de_ehrenkreuz_der_bundeswehr_gold': dict(
        nation='Germany', name='Cross of Honour of the Bundeswehr in Gold', type='PersonalDecoration',
        precedence=38, art=(('#DDA61C', 3.6), ('#C1382B', 3.6), ('#414141', 17.6), ('#C1382B', 3.6),
                            ('#DDA61C', 3.6)), device='gold_cross', ranks=(3, 6),
        merit='For loyal service and exemplary fulfilment of duty as commander of {TaskForceName}',
        source='https://en.wikipedia.org/wiki/Badge_of_Honour_of_the_Bundeswehr'),
    'de_verdienstkreuz_am_bande': dict(
        nation='Germany', name='Federal Cross of Merit on Ribbon', type='PersonalDecoration', precedence=12,
        art=(('#B7A967', 1.41), ('#2A2A2A', 1.18), ('#B7A967', 1.41), ('#B10303', 24), ('#B7A967', 1.41),
             ('#2A2A2A', 1.18), ('#B7A967', 1.41)), ranks=(1, 10),
        merit='For outstanding services to the Federal Republic of Germany as commander of {TaskForceName}',
        source='https://www.gesetze-im-internet.de/verdordenstat/'),
    'de_einsatzmedaille_bundeswehr_bronze': dict(
        nation='Germany', name='Bundeswehr Deployment Medal in Bronze', type='ServiceAward', precedence=90,
        art=(('#1F1F22', 2.69), ('#A32636', 3.17), ('#CAAF63', 3.17), ('#A32636', 13.94), ('#CAAF63', 3.17),
             ('#A32636', 3.17), ('#1F1F22', 2.69)), ranks=(1, 10), service_days=30,
        merit="For 30 days' service abroad on a deployment of the Bundeswehr with {TaskForceName}",
        source='https://www.gesetze-im-internet.de/stifteinsatzmedbwerl_2025/'),
    # --- Denmark (Chief of Defence circulars CIR1H 9077 and 9074, 2010) ----
    # Both medals are the Chief of Defence's, for defence personnel and, on
    # a special effort, foreigners; no grade limit or service period. The
    # Excellent Service medal is the higher.
    'dk_defence_medal_meritorious_service': dict(
        nation='Denmark', name='Defence Medal for Meritorious Service', type='PersonalDecoration',
        precedence=40,
        art=(('#C02020', 1.6), ('#FFFFFF', 1.6), ('#C02020', 1.6), ('#FFFFFF', 1.6), ('#C02020', 19.2),
             ('#FFFFFF', 1.6), ('#C02020', 1.6), ('#FFFFFF', 1.6), ('#C02020', 1.6)), ranks=(1, 10),
        merit='For a meritorious effort for the Danish Defence as commander of {TaskForceName}',
        source='https://www.retsinformation.dk/eli/retsinfo/2010/9077'),
    'dk_defence_medal_excellent_service': dict(
        nation='Denmark', name='Defence Medal for Excellent Service', type='PersonalDecoration',
        precedence=30,
        art=(('#FFFFFF', 5.12), ('#C02020', 7.04), ('#FFFFFF', 7.68), ('#C02020', 7.04), ('#FFFFFF', 5.12)),
        ranks=(1, 10),
        merit='For an extraordinary effort in the service of the Danish Defence as commander of '
              '{TaskForceName}',
        source='https://www.retsinformation.dk/eli/retsinfo/2010/9074'),
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
# How each code-drawn real-award strip was measured, where SOURCES.txt
# should say more than the published stripe order. Colours are sampled from
# images; a white or black the source names is drawn pure.
ART_NOTES = {
    'ca_meritorious_service_medal_military': (
        'widths from the Regulations, s.4(5)(b); the blue sampled from the official gg.ca '
        'photograph of the cross'),
    'ca_meritorious_service_cross_military': (
        'widths from the Regulations, s.4(5)(a); the blue sampled from the official gg.ca '
        'photograph of the cross'),
    'ca_general_campaign_star_expedition': (
        'widths as specified by Canada (DND medal page); colours sampled from a Commons image'),
    'nz_distinguished_service_decoration': (
        'proportions measured from an image (the official NZDF photograph), as the Royal Warrant '
        'could not be read; colours sampled from it'),
    'nz_member_order_of_merit': 'plain red ochre, sampled from the official NZDF photograph',
    'nz_operational_service_medal': (
        'proportions measured from an image (the official NZDF photograph); black and white as '
        'the NZDF names them'),
    'fr_chevalier_ordre_national_du_merite': (
        'plain blue, the median of a Commons photograph of a Chevalier ribbon, as France publishes '
        'no colour value'),
    'fr_chevalier_legion_d_honneur': (
        'plain red, the median of the public-domain Commons photograph of the Chevalier insignia'),
    'kr_national_security_medal': (
        'widths from the Enforcement Decree, Annex 2 (38 mm); the yellow sampled from the official '
        'Ministry of the Interior and Safety photograph, the white drawn pure as the Annex names it; '
        'the ribbon bar\'s taegeuk drawn in the national flag\'s red and blue, about 8.6 mm, its '
        'size measured from that photograph'),
    'kr_order_of_national_security_merit_samil': (
        'widths from the Enforcement Decree, Annex 2 (38 mm); the light yellow sampled from the '
        'official Ministry of the Interior and Safety photograph, the white drawn pure as the Annex '
        'names it; the ribbon bar\'s taegeuk drawn in the national flag\'s red and blue'),
    'es_cruz_merito_naval_distintivo_blanco': (
        'the national colours in the flag\'s order and proportions, RD 1040/2003 art. 53.5, on the '
        '30 mm ribbon; colours from the flag\'s official values, RD 441/1981'),
    'es_cruz_merito_naval_distintivo_rojo': (
        'widths from RD 1040/2003 art. 53.2, the yellow one eighth of the 30 mm ribbon; the decree '
        'gives no colours, so the flag\'s official values (RD 441/1981) are used'),
    'es_medalla_de_campana': (
        'widths from RD 336/2018 art. 6.1.d; colours sampled from the official annex drawing '
        '(BOE-A-2024-24344); drawn without the operation\'s silver rectangle, as the operation is '
        'fictional'),
    'de_ehrenkreuz_der_bundeswehr_gold': (
        'proportions and colours measured from a drawing (Wikimedia Commons), as no official widths '
        'are published; the gold miniature cross on the ribbon bar drawn plain'),
    'de_verdienstkreuz_am_bande': (
        'red with a gold-black-gold edge, as the statute (art. 3(2)) gives it; proportions and '
        'colours measured from a drawing (Wikimedia Commons)'),
    'de_einsatzmedaille_bundeswehr_bronze': (
        'black, red and gold as the decree names them, in the order en.wikipedia describes; '
        'proportions and colours measured from a drawing (Wikimedia Commons); drawn without the '
        'clasp, as the deployment is fictional'),
    'dk_defence_medal_meritorious_service': (
        'red with two narrow white stripes each side, as the circular (CIR1H 9077, s. 2) gives '
        'it; proportions and the red measured from a public-domain drawing (Wikimedia Commons), as '
        'no official image could be reached; white drawn pure'),
    'dk_defence_medal_excellent_service': (
        'white with two broad red stripes, as the circular (CIR1H 9074, s. 2) gives it; proportions '
        'and the red measured from a public-domain drawing (Wikimedia Commons), as no official image '
        'could be reached; white drawn pure'),
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
        'SW08': ('australian_commendation_distinguished_service', 'navy_commendation_medal', 'uk_obe_military',
                 'ca_meritorious_service_medal_military', 'nz_distinguished_service_decoration',
                 'fr_chevalier_ordre_national_du_merite', 'kr_national_security_medal',
                 'es_cruz_merito_naval_distintivo_blanco', 'de_ehrenkreuz_der_bundeswehr_gold',
                 'dk_defence_medal_meritorious_service'),
        'SW12': ('australian_distinguished_service_cross', 'bronze_star_medal', 'uk_distinguished_service_order',
                 'jmsdf_first_class_commendation', 'ca_meritorious_service_cross_military',
                 'nz_member_order_of_merit', 'fr_chevalier_legion_d_honneur',
                 'kr_order_of_national_security_merit_samil', 'es_cruz_merito_naval_distintivo_rojo',
                 'de_verdienstkreuz_am_bande', 'dk_defence_medal_excellent_service',
                 'australian_meritorious_unit_citation'),
    },
    'sest-southern-reach': {
        'SR10': ('sest_aosm_indo_pacific', 'armed_forces_expeditionary_medal',
                 'ca_general_campaign_star_expedition', 'nz_operational_service_medal',
                 'es_medalla_de_campana', 'de_einsatzmedaille_bundeswehr_bronze'),
        'SR12': ('australian_commendation_distinguished_service', 'navy_commendation_medal', 'uk_obe_military',
                 'ca_meritorious_service_medal_military', 'nz_distinguished_service_decoration',
                 'fr_chevalier_ordre_national_du_merite', 'kr_national_security_medal',
                 'es_cruz_merito_naval_distintivo_blanco', 'de_ehrenkreuz_der_bundeswehr_gold',
                 'dk_defence_medal_meritorious_service'),
        'TS09': ('australian_distinguished_service_cross', 'legion_of_merit', 'uk_distinguished_service_order',
                 'jmsdf_first_class_commendation', 'ca_meritorious_service_cross_military',
                 'nz_member_order_of_merit', 'fr_chevalier_legion_d_honneur',
                 'kr_order_of_national_security_merit_samil', 'es_cruz_merito_naval_distintivo_rojo',
                 'de_verdienstkreuz_am_bande', 'dk_defence_medal_excellent_service'),
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


def award_nations(slug):
    """(nations, unit awards): the offered nations whose commanders a
    campaign grants national awards, in its offer order, and the names of
    the host's unit awards every commander's group receives. The rules
    page and RIBBONS.txt say the other offered nations' commanders receive
    the fictional ribbons and the unit award only."""
    slug = base_slug(slug)
    granted = [REAL[rid] for rid in grants(slug) if rid in REAL]
    nations = {row['nation'] for row in granted if row['nation']}
    return ([n for n in NATIONS.get(slug, ()) if n in nations],
            [row['name'] for row in granted if not row['nation']])


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


def runtime_grants(slug):
    """{award id: mission code} for the runtime ribbons (RUNTIME). An id is
    granted at one mission, and never by the game as well."""
    slug = base_slug(slug)
    native, out = grants(slug), {}
    for code, rows in RUNTIME.get(slug, {}).items():
        _mission(slug, code)
        for row in rows:
            rid = row['id']
            if rid in native:
                raise ValueError(f'{slug}: {rid} is a native award; a runtime ribbon must not repeat one')
            if rid in out:
                raise ValueError(f'{slug}: {rid} is granted twice')
            out[rid] = code
    return out


def catalogue(slug):
    """Every definition a campaign carries: what it grants, then what earlier
    builds granted (RETIRED), then the runtime ribbons (RUNTIME), keyed by
    id."""
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
    # A performance ribbon ranks after the campaign's completion ribbon (120)
    # and before its operation ribbons (130).
    for rid, code in runtime_grants(slug).items():
        if rid in out:
            raise ValueError(f'{slug}: {rid} is already defined')
        row = next(r for r in RUNTIME[slug][code] if r['id'] == rid)
        out[rid] = dict(name=row['name'], type='CampaignAward', precedence=125, reference='Fictional',
                        recipient='commander', stripes=row['stripes'], mission=code,
                        citation=row['why'] + '. ' + FICTIONAL, runtime=True)
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
    # A runtime ribbon is defined but not listed: RibbonIds is the developer
    # catalogue, whose grant would hand it out on any build.
    listed = [rid for rid in ids if definitions.get(rid, {}).get('runtime')]
    if listed:
        raise ValueError(f'{slug}: RibbonIds lists the runtime ribbon {", ".join(listed)}')
    ids.extend(rid for rid, row in definitions.items() if rid not in ids and not row.get('runtime'))
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
    elif device == 'taegeuk':
        # The red-over-blue taegeuk of the Korean ribbon bars, 26 of the
        # bar's 30 px (about 8.6 of its 10 mm), in the flag's colours.
        red, blue, r = '#CD2E3A', '#0047A0', 13
        draw.pieslice((70 - r, 17.5 - r, 70 + r, 17.5 + r), 180, 360, fill=red)
        draw.pieslice((70 - r, 17.5 - r, 70 + r, 17.5 + r), 0, 180, fill=blue)
        h = r / 2
        draw.ellipse((70 - r, 17.5 - h, 70, 17.5 + h), fill=red)
        draw.ellipse((70, 17.5 - h, 70 + r, 17.5 + h), fill=blue)
        draw.ellipse((70 - r, 17.5 - r, 70 + r, 17.5 + r), outline='#8A6D14', width=1)
    elif device == 'gold_cross':
        # The gold miniature Cross of Honour on the black centre: a cross
        # pattee 20 px across, its arms widening to the ends.
        gold, edge, cx, cy, a, w0, w1 = '#D9B44A', '#8A6D14', 70, 17.5, 10, 2, 6
        draw.polygon([(cx - w0, cy - w0), (cx - w1, cy - a), (cx + w1, cy - a), (cx + w0, cy - w0),
                      (cx + a, cy - w1), (cx + a, cy + w1), (cx + w0, cy + w0), (cx + w1, cy + a),
                      (cx - w1, cy + a), (cx - w0, cy + w0), (cx - a, cy + w1), (cx - a, cy - w1)],
                     fill=gold, outline=edge)
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


def sources_text(slug, commander=''):
    """This campaign's art/ribbons/SOURCES.txt: what each picture is.
    `commander` is the campaign's commander_settings.ini text, whose SEST
    emblems the file credits (emblem_credits)."""
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
            if rid in ART_NOTES:
                lines += textwrap.wrap(ART_NOTES[rid] + '.', width=88, initial_indent='    ',
                                       subsequent_indent='    ')
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
                  'green, light blue, green, a yellow centre - match the Defence description and the',
                  'Australian Operational Service Medal (Indo-Pacific) Instrument 2024, approved',
                  '12 January 2025.']
    emblems = emblem_credits(slug, commander)
    if emblems:
        lines += ['', f'Commander emblem{"s" if len(emblems) != 1 else ""} in {_EMBLEMS}, scaled by '
                  'build_pack.py from the SEST', 'gallery flag set (Wikimedia Commons, public domain; '
                  'credited in Gallery/VISUAL_CREDITS.txt):']
        for name, navy, about, commons in emblems:
            lines += textwrap.wrap(f'{name} - {navy}: {about}.',
                                   width=88, initial_indent='  ', subsequent_indent='    ')
            lines.append(f'    Source: {commons}')
    real = [(rid, row) for rid, row in rows.items() if row['reference'] != 'Fictional' and row.get('source')]
    if real:
        lines += ['', 'Award facts (criteria, ribbon design, precedence):']
        lines += [f'  {row["name"]}: {row["source"]}' for _rid, row in real]
    lines += ['', 'Every real-award citation says it is a game award for a fictional operation,',
              'not a real honour.']
    return '\n'.join(lines) + '\n'


def render(campaign_directory, slug, commander=''):
    """Draw the strips, copy the sourced AOSM strip unaltered and write the
    campaign's SOURCES.txt, crediting the emblems `commander` (the
    campaign's commander_settings.ini text) names."""
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
    (folder / 'SOURCES.txt').write_text(sources_text(slug, commander), encoding='utf-8')


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


def _runtime_term(term, objectives, where):
    """One condition as MissionAwards.ParseTerm reads it. An objective must
    be one of the mission's own, spelt as it is."""
    kind, *args = term
    if kind == 'objective' and len(args) == 2:
        oid, state = args
        if oid not in objectives:
            raise ValueError(f'{where}: the mission has no objective {oid!r} ({", ".join(objectives) or "none"})')
        if state not in OBJECTIVE_STATES:
            raise ValueError(f'{where}: an objective is {"|".join(OBJECTIVE_STATES)}, not {state!r}')
        return f'objective:{oid}={state}'
    if kind == 'result' and len(args) == 1 and args[0] in RESULTS:
        return f'result>={args[0]}'
    if kind == 'nolaunch' and not args:
        return 'nolaunch'
    if kind == 'rescued' and len(args) == 1 and type(args[0]) is int and 1 <= args[0] <= 999:
        return f'rescued>={args[0]}'
    raise ValueError(f'{where}: {term!r} is not a runtime award condition')


def runtime_mission_awards(slug, mission):
    """The specs of a mission's SestRuntimeRibbonAwards key, in RUNTIME's
    grammar. The build stops on an objective the mission does not have, an
    unknown condition, an id the game grants too, a nation the campaign
    does not offer, or a value the game's ini reader would cut."""
    slug = base_slug(slug)
    code = mission.get('code', 'SW' + mission.get('num', ''))
    rows = RUNTIME.get(slug, {}).get(code, ())
    if not rows:
        return []
    granted = runtime_grants(slug)
    objectives = [row[0] for row in mission.get('objectives', ())]
    out = []
    for row in rows:
        rid, where = row['id'], f'{slug} {code} {row["id"]}'
        if granted.get(rid) != code or not re.fullmatch(r'[a-z0-9_]+', rid):
            raise ValueError(f'{where}: not a runtime ribbon of this mission')
        nations = tuple(row.get('nations', ()))
        for nation in nations:
            if nation not in NATIONS.get(slug, ()):
                raise ValueError(f'{where}: {nation} is not a nation the campaign offers')
        if not row['terms']:
            raise ValueError(f'{where}: a spec needs a condition')
        terms = [_runtime_term(term, objectives, where) for term in row['terms']]
        out.append(rid + ''.join(',' + n for n in nations) + '?' + '&'.join(terms))
    value = '|'.join(out)
    # IniHandler ends a value at ';', and '#' and '//' open comments too
    # (MissionAwards.cs:32); the runtime refuses more than 32 specs or 4096
    # characters (:47).
    if any(mark in value for mark in (';', '#', '//')) or len(value) > 4096 or len(out) > 32:
        raise ValueError(f'{slug} {code}: {RUNTIME_KEY} value would not reach the runtime whole: {value!r}')
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
