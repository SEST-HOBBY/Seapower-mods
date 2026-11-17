"""Final installed coverage, quantity boundaries and source preservation."""
from pathlib import Path
import csv
import io
import json
import re
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'integration'))
from common import costs
from common.cost_completion import (build_complete,Definitions,info,render_complete,render_config,
                                    reports,CATEGORY_RE,select_model)


class CompleteCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maps=json.loads((ROOT/'integration/combat-costs/mappings.json').read_text())
        cls.baseline,cls.base=costs._build(ROOT,cls.maps)
        cls.result,cls.context=build_complete(ROOT,cls.maps)
        cls.defs=Definitions(ROOT)
        cls.rows={(r['kind'],r['id'].casefold()):r for r in cls.result['completion']['rows']}

    def test_every_resolved_reference_has_both_prices(self):
        expected={(kind,uid) for (kind,uid) in self.defs.chains}
        self.assertEqual(set(self.rows),expected)
        for key,row in self.rows.items():
            with self.subTest(item=key):
                self.assertIsNotNone(costs.price(row['historical']))
                self.assertIsNotNone(costs.price(row['current']))
                self.assertTrue(CATEGORY_RE.fullmatch(row['category']))

    def test_preexisting_usable_fields_are_never_changed(self):
        for kind,units in self.base['units'].items():
            hist=info(kind)[2]
            for uid in units:
                own=self.defs.sections(kind,uid).get('general',{})
                for label,field in [('historical',hist),('current','CurrentYearCost')]:
                    value=costs.price(costs.resolve_field(own,self.base['merged'][kind],uid,field))
                    if value is not None:
                        self.assertEqual(costs.price(self.rows[kind,uid][label]),value,(kind,uid,field))

    def test_checked_land_estimates_precede_the_models(self):
        land=self.maps['land']
        self.assertEqual(len(land),15)
        for item in land:
            row=self.rows['land',item['target'].casefold()]
            with self.subTest(item=item['target']):
                self.assertEqual(row['current'],item['estimate']['current'])
                self.assertEqual(row['category'],item['category'])
                if item['estimate']['historical']:
                    self.assertEqual(row['historical'],item['estimate']['historical'])
                else:   # a checked current-only price is backcast, never paired with a model figure
                    self.assertEqual(row['field_methods']['historical'],'CPI backcast of checked current price')
                    self.assertLessEqual(costs.price(row['historical']),costs.price(row['current']))
        with self.assertRaises(ValueError):
            build_complete(ROOT,dict(self.maps,land=[dict(land[0],target='no_such_land_unit')]))

    def test_all_backlog_ids_are_accounted_for_without_calling_estimates_confirmed(self):
        text=(ROOT/'docs/combat-costs/not-yet-confirmed.md').read_text()
        backlog=re.findall(r'^\| `([^`]+)`',text,re.M)
        self.assertEqual((len(backlog),len(set(backlog))),(381,377))
        ids={uid for kind,uid in self.rows}
        self.assertFalse([uid for uid in backlog if uid.casefold() not in ids])
        self.assertNotIn('confirmed',self.rows['weapon','sest_aim-424']['field_methods']['current'])

    def test_expendables_have_countable_valid_categories(self):
        for uid,category in [('usn_ssq-53h','Sonobuoy'),('all_air_chaff_standard','Decoy'),
                             ('usn_adc_mk2_noisemaker','Decoy'),('sest_agr-30_pod','Pod'),
                             ('usn_tank_610_f-18','Fuel tank')]:
            self.assertEqual(self.rows['weapon',uid]['category'],category)
            self.assertGreater(costs.price(self.rows['weapon',uid]['current']),0)

    def test_dummy_processes_are_explicitly_included_and_people_are_not_priced(self):
        for uid in ['chaff_dircm','all_pilot','usaf_pilot_f-15c','usn_laser']:
            row=self.rows['weapon',uid]
            self.assertEqual(row['category'],'Ignore',uid)
            self.assertEqual(row['disposition'],'included or non-procured',uid)
            self.assertEqual(costs.price(row['current']),0,uid)

    def test_laser_guided_projectile_is_not_confused_with_a_laser_beam(self):
        model,_=select_model('weapon','new_155mm_laser',{'general':{'type':'Projectile','mass':'45'}})
        self.assertNotEqual(model,'none')

    def test_hand_launched_mini_uav_is_a_small_uav_not_a_fighter(self):
        # fr_aliaca (Charles De Gaulle & Modern French Navy, 28 Oct 2026): EmptyMass=13.0,
        # Role=Recon and no "uav" in its id, so the fighter proxy ($75M) took it.
        model,_=select_model('aircraft','fr_aliaca',{'general':{'unittype':'Aircraft','emptymass':'13.0','role':'Recon'}})
        self.assertEqual(model,'small_uav')
        row=self.rows['aircraft','fr_aliaca']
        self.assertEqual(row['completion']['model'],'small_uav')
        self.assertEqual(costs.price(row['current']),2000000)

    def test_pod_is_hardware_not_seven_missiles(self):
        pod=self.rows['weapon','sest_agr-30_pod']
        missile=self.rows['weapon','sest_agr-30']
        self.assertEqual(costs.price(pod['current']),25000)
        self.assertEqual(costs.price(missile['current']),150000)
        self.assertNotEqual(costs.price(pod['current']),7*costs.price(missile['current']))

    def test_no_cross_name_mapping_for_modern_supply_and_anzac(self):
        for uid in ['ran_aor_supply','ran_ffh_anzac']:
            model=self.rows['vessel',uid]['completion']
            self.assertIsNone(model['source'])
            self.assertEqual(model['confidence'],'rough model')

    def test_model_ranges_and_sources_are_explicit(self):
        for row in self.rows.values():
            if row['field_methods']['current']=='existing usable value preserved':continue
            self.assertLessEqual(costs.price(row['current_low']),costs.price(row['current']))
            self.assertGreaterEqual(costs.price(row['current_high']),costs.price(row['current']))
            self.assertIn(row['completion']['source_id'],self.result['completion']['sources'])

    def test_generated_extension_is_exact_final_selected_data(self):
        for kind,entries in self.result['extensions'].items():
            text=render_complete(kind,self.result)
            parsed=costs.parse_ini(text)
            if kind!='land':self.assertTrue(text.startswith('#!extend systems/'+info(kind)[1]+'.ini\n'))
            for uid,values in entries.items():
                self.assertEqual(parsed[uid],{k.casefold():v for k,v in values.items()},(kind,uid))
            self.assertNotRegex(text,r'(?m)^(?:Type|Mass|MaxLaunchRange|UnitType|AmmoPoints|Cost)=',text)

    def test_config_only_exposes_categories_and_retains_other_preferences(self):
        parsed=costs.parse_ini(render_config(ROOT,self.result))
        self.assertEqual(set(parsed),{'weaponcategories'})
        order=parsed['weaponcategories']['order'].split(',')
        self.assertTrue(all(x in order for x in ['Decoy','Gun','Pod','Fuel tank','Sonobuoy']))
        self.assertEqual(len(order),len(set(order)))

    def test_rebuild_is_deterministic_and_reports_complete_references(self):
        md,table=reports(self.result)
        rows=list(csv.DictReader(io.StringIO(table)))
        self.assertEqual(len(rows),len(self.rows))
        self.assertTrue(all(r['historical_usd']!='' and r['current_usd']!='' for r in rows))
        self.assertEqual(reports(self.result),(md,table))
        self.assertIn('not independently confirmed procurement quotes',md)

    def test_category_validator_matches_tracker_character_rule(self):
        item={'target':'x','basis':'test','category':'SAM/','estimate':{'current':'1','current_year':'2026','current_method':'model estimate'},'sources':[{'title':'test','url':'https://example.org'}]}
        with self.assertRaises(ValueError):costs.estimate_fields('weapon',item)

    def test_b21_raider_is_priced_as_a_bomber_with_its_rounds_mapped(self):
        # B-21 Raider (3821992229, in the order since the 28 Oct 2026 export): Role=HeavyBomber,Bomber
        # and no bomber rule in select_model, so without its mapping the fighter proxy ($75M) took it.
        row=self.rows['aircraft','usaf_b-21_raider']
        self.assertEqual((row['historical'],row['current']),('550000000','692000000'))
        self.assertEqual(row['field_methods']['current'],'existing usable value preserved')
        for uid,donor in [('usaf_b21_agm-158b','usn_agm-158b-2'),('usaf_b21_agm-158c','b-2_lrasm'),
                          ('usaf_b21_gbu-31','usn_gbu-31v1'),('usaf_b21_gbu-38','usn_gbu-38_10')]:
            row,source=self.rows['weapon',uid],self.rows['weapon',donor]
            self.assertEqual((row['historical'],row['current']),(source['historical'],source['current']),uid)
            self.assertEqual(row['field_sources']['current'],'reviewed catalog mapping: '+donor,uid)
        # No tracker Mk 82 exists and the 24 Oct check would not copy SEST's usn_mk-82 donor:
        # the general-purpose bomb model, labelled, as on the game's Mk 82 Snakeye.
        mk82=self.rows['weapon','usaf_b21_mk-82']
        self.assertEqual((mk82['completion']['model'],mk82['field_methods']['current']),('unguided_bomb','rough model'))
        # Its byte-identical usn_steelfin_air loses to Steelfin's own copy, which keeps its price.
        self.assertEqual(self.rows['weapon','usn_steelfin_air']['owner'],'3820576916')

    def test_090_units_take_their_class_from_the_catalog_not_a_wrong_model(self):
        # Sea Power 0.9.0 (11 Nov 2026) added 103 units and rounds. With no carrier, cruiser or
        # landing-ship rule under those names the merchant proxy ($75M) took Invincible, the
        # Veinticinco de Mayo, the Belgrano and the Round Table ships, and the generic destroyer,
        # frigate and submarine proxies took classes the tracker author's catalog already prices
        # under The Royal Navy mod's ids.
        for kind,uid,donor,category in [
                ('vessel','rn_cvs_invincible','rn_cv_invincible','CVL'),
                ('vessel','ara_cv_veinticinco_de_mayo','ran_majestic','CVL'),
                ('vessel','ara_cl_belgrano','wp_kr_sverdlov','CL'),
                ('vessel','rn_lsl_roundtable','ran_lsh_tobruk','LST'),
                ('vessel','rn_ddg_sheffield','rn_ff_type42','DDG'),
                ('vessel','rn_ff_broadsword','rn_type22b12','FF'),
                ('vessel','rn_ssn_churchill','rn_churchill_class_ssn','SSN'),
                ('vessel','usn_ss_balao_guppy_ii','ae_ss_s32','SS'),
                ('aircraft','rn_sea_king_has5','rn_sea_king','Aircraft'),
                ('aircraft','usn_s-2e','ran_s2','Aircraft'),
                ('weapon','rn_seaslug_mk2','rn_seaslug_2','SAM')]:
            row,source=self.rows[kind,uid],self.base['merged'][kind][donor.casefold()]
            with self.subTest(item=uid):
                self.assertEqual((row['historical'],row['current']),
                                 (source[info(kind)[2].casefold()],source['currentyearcost']))
                self.assertEqual(row['field_sources']['current'],'reviewed catalog mapping: '+donor)
                self.assertEqual(row['category'],category)
                self.assertIsNone(row['completion'])   # no proxy model had to fill a field

    def test_a_copy_directive_unit_is_listed_and_priced(self):
        # 0.9.0 is the first game version whose own files use #!copy: the Leaf tanker, the Narwal
        # and the Victor K.2 have no [General] of their own, and until 13 Nov 2026 the inventory
        # passed over such a file, so the tracker had no price for them or for nine mod units.
        for uid,source,category,price in [('rn_ao_leaf','civ_ms_sealift_pacific','AO','117000000'),
                                          ('ara_agi_narwal','civ_fv_sterntrawler_b','AGI','15400000')]:
            row=self.rows['vessel',uid]
            self.assertEqual((row['current'],row['category']),(price,category),uid)
            self.assertEqual(row['field_sources']['current'],'reviewed catalog mapping: '+source,uid)
        # A copy reads its source's type: the tanker Victor is the bomber's airframe.
        tanker,bomber=self.rows['aircraft','raf_victor_k2'],self.rows['aircraft','raf_victor']
        self.assertEqual((tanker['historical'],tanker['current']),(bomber['historical'],bomber['current']))
        self.assertEqual(self.defs.sections('aircraft','raf_victor_k2')['general']['unittype'],'Aircraft')
        self.assertEqual(self.defs.sections('aircraft','raf_victor_k2')['ai']['role'],'Tanker')
        # The mods' copies cost what their sources cost.
        k5=self.rows['vessel','usn_usv_k5_kraken']
        for uid in ('usn_usv_k5_kraken_owa','usn_usv_k5_kraken_steelfin','usn_usv_k5_kraken_strike'):
            self.assertEqual((self.rows['vessel',uid]['historical'],self.rows['vessel',uid]['current']),
                             (k5['historical'],k5['current']),uid)
        hill,steelfin=self.rows['vessel','usn_cg_bunker_hill'],self.rows['vessel','usn_cg_steelfin']
        self.assertEqual((steelfin['historical'],steelfin['current']),(hill['historical'],hill['current']))
        for uid,source in [('usn_uuv_dive_ld_mcm','usn_uuv_dive_ld'),('usn_uuv_dive_xl_100m','usn_uuv_dive_xl'),
                           ('usn_asv_saronic_corsair_steelfin','usn_asv_saronic_corsair_missile')]:
            self.assertEqual(self.rows['vessel',uid]['current'],self.rows['vessel',source]['current'],uid)
        self.assertEqual(self.rows['weapon','usn_steelfin_boat']['current'],self.rows['weapon','usn_steelfin']['current'])

    def test_a_copy_directive_is_read_as_the_game_reads_it(self):
        base=costs.base_reference
        self.assertEqual(base('#!copy vessels/civ_fv_sterntrawler_b.ini\n[AI]\nRole=Spy\n'),'vessels/civ_fv_sterntrawler_b.ini')
        self.assertEqual(base('# note\n#!COPY vessels\\a.ini , vessels/b.ini\n[AI]\n'),'vessels\\a.ini')
        self.assertEqual(base('#!copy vessels/a.ini   ; the hull\n'),'vessels/a.ini')
        self.assertIsNone(base('[General]\nType=Missile\n#!copy ammunition/a.ini\n'))   # after a section: not a directive
        self.assertIsNone(base('#!copy\n[General]\n'))
        self.assertIsNone(base('#!copying vessels/a.ini\n'))
        # An #!alias base, read from any line, still comes first.
        self.assertEqual(base('#!copy vessels/a.ini\n[General]\n#!alias vessels/b.ini\n'),'vessels/b.ini')

    def test_a_catalog_key_in_a_folder_is_named_by_its_file(self):
        # [rn_harrier_gr3/rn_wessex] is the tracker author's Wessex ("Wessex / H-34", 600,000 and
        # 6,700,000) kept in a folder named for a Harrier. The family rule read the whole key, so
        # seven Harriers and AV-8As, the game's new GR.3 among them, cost what a Wessex costs.
        catalog=self.base['merged']['aircraft']
        self.assertIn('rn_harrier_gr3/rn_wessex',catalog)
        self.assertFalse([key for key in catalog if re.search(r'harrier|av[-_]?8a',key.rsplit('/',1)[-1])])
        for uid in ('raf_gr3','rn_harrier_gr3','rn_sea_harrier','rn_sea_harrier_early','ran_sea_harrier84','spa_av-8a','usmc_av-8a'):
            row=self.rows['aircraft',uid]
            with self.subTest(item=uid):
                self.assertEqual((row['completion']['model'],row['field_methods']['current']),('fighter','rough model'))
                self.assertIsNone(row['completion']['source'])
        # A folder still does not hide the file: the Seahawk family finds its donor as before.
        self.assertEqual(self.rows['aircraft','s-70b-2_seahawk']['field_sources']['current'],'reviewed catalog mapping: ran_s-70b-2_seahawk')

    def test_090_names_the_rules_could_not_read(self):
        for kind,uid,sections,model in [
                # The wartime air-dropped Mark 13 weighs 1,000 kg, so the modern heavyweight proxy ($4M) took it.
                ('weapon','usn_mk13',{'general':{'type':'Torpedo','mass':'1000'}},'ww2_torpedo'),
                ('weapon','usn_mk-48',{'general':{'type':'Torpedo','mass':'1600'}},'heavy_torpedo'),
                # Type 182 is a towed body like Nixie, not an expendable.
                ('weapon','rn_type_182_decoy',{'general':{'type':'Noisemaker'}},'towed_decoy'),
                # Matra Type 155: eighteen or twenty 68 mm tubes.
                ('weapon','fr_type155_sneb',{'general':{'type':'Container'}},'large_pod'),
                ('weapon','rn_type_155',{'general':{'type':'Container'}},'large_pod'),
                # Bandeirante family and Skyvan: light utility twins, not combat aircraft.
                ('aircraft','civ_e100',{'general':{'unittype':'Aircraft'}},'civil_light'),
                ('aircraft','fab_c-95',{'general':{'unittype':'Aircraft'}},'civil_light'),
                ('aircraft','ara_p-95',{'general':{'unittype':'Aircraft'}},'civil_light'),
                ('aircraft','raf_sc-7',{'general':{'unittype':'Aircraft'}},'civil_light'),
                ('aircraft','wp_tu-95',{'general':{'unittype':'Aircraft'}},'fighter'),
                # Grass strips and a forward operating base are not full airbases.
                ('land','flk_goose_green',{'general':{'landunitsubtype':'Airbase'}},'small_airbase'),
                ('land','flk_pebble_island',{'general':{'landunitsubtype':'Airbase'}},'small_airbase'),
                ('land','flk_san_carlos_fob',{'general':{'landunitsubtype':'Airbase'}},'small_airbase'),
                ('land','flk_stanley',{'general':{'landunitsubtype':'Airbase'}},'airbase')]:
            with self.subTest(item=uid):
                self.assertEqual(select_model(kind,uid,sections)[0],model)
        self.assertEqual(costs.price(self.rows['weapon','usn_mk13']['current']),250000)
        self.assertEqual(costs.price(self.rows['land','flk_goose_green']['current']),50000000)


class PriceParity(unittest.TestCase):
    def test_shared_csharp_and_python_precedence_cases(self):
        path=ROOT/'integration/runtime-fixes/tests/cost_precedence.tsv'
        for row in csv.DictReader(path.read_text().splitlines(),delimiter='\t'):
            own,entry,global_={},{},{}
            for out,key,value in [(own,'CurrentYearCost',row['inline']),(entry,'CurrentYearCost',row['catalog']),
                (global_,'OverrideInline',row['global']),(entry,'OverrideInline',row['entry']),
                (entry,'OverrideCurrentYearCost',row['field_override'])]:
                if value!='~':out[key.casefold()]='' if value=='EMPTY' else value
            expected=None if row['expected']=='~' else '' if row['expected']=='EMPTY' else row['expected']
            self.assertEqual(costs.resolve_field(own,{'costs':global_,'round':entry},'round','CurrentYearCost'),expected,row['name'])


if __name__=='__main__':unittest.main()
