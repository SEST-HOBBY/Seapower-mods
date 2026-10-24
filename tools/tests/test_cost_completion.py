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
