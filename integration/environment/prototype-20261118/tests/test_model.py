import sys
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'tools'))
from environment_model import generate_grid,bilinear,field_at,wrap_lon,eval_route,great_circle_nm
from patch_vanilla_mission import patch,PRESET,cloud_code,state_from_grid
class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.env=generate_grid(ticks=4)
    def test_grid_dimensions_and_units(self):
        for fr in self.env['frames']:
            for name,values in fr['fields'].items():
                self.assertEqual(len(values),91*46,name)
                self.assertTrue(all(v is not None for v in values))
    def test_deterministic(self):self.assertEqual(generate_grid(ticks=2),generate_grid(ticks=2))
    def test_wrap_antimeridian(self):
        self.assertAlmostEqual(wrap_lon(181),-179)
        self.assertAlmostEqual(bilinear(self.env,1,-52,-180,'wave_m'),bilinear(self.env,1,-52,180,'wave_m'))
    def test_cyclone_advects(self):
        self.assertNotEqual(bilinear(self.env,0,-54,-49,'pressure_hpa'),bilinear(self.env,1,-54,-49,'pressure_hpa'))
    def test_bounded(self):
        for lat in (-80,-60,-10,0,53,82):
            for lon in (-179,-49,5,180):
                x=field_at(lat,lon,10)
                self.assertLessEqual(x['cloud_pct'],100)
                self.assertGreaterEqual(x['ice_pct'],0)
                self.assertLess(x['wave_m'],14)
    def test_route_lengths(self):
        route=eval_route(self.env,[[-54,-60],[-56,-50],[-64,-46]],0)
        self.assertGreater(route['distance_nm'],100)
        self.assertIn(route['access'],('restricted','caution','open'))
    def test_patch_preserves_other_triggers_and_updates_counter(self):
        fixture='''[General]\nType=Scenario\n[Language_en]\nName=Fixture\nDescription=Default\n[Environment]\nDate=1985,1,1\nTime=12,0\nSeaState=3\nClouds=Clear\nClouds=Broken\n[Mission]\nNumberOfTriggers=2\n[Trigger1]\nName=Victory\nCondition_Type=Time\nCondition_Time=10\nAction_EndMission=True\n[Trigger2]\nName=OriginalWeather\nCondition_Type=Time\nCondition_Time=800\nAction_SetClouds=Overcast\n'''
        result,meta=patch(fixture,PRESET[:4],300)
        self.assertIn('NumberOfTriggers=5',result)
        self.assertEqual(result.count('Clouds=Broken\n'),1)
        self.assertIn('Action_EndMission=True',result)
        self.assertIn('Disabled=True',result)
        self.assertIn('Action_SetThunderstorm=True',result)
        self.assertEqual(meta['new_trigger_count'],3)
        self.assertEqual(meta['total_number_of_triggers'],5)
    def test_patch_rejects_invalid(self):
        with self.assertRaises(ValueError):patch('[Environment]\nSeaState=3\n',PRESET)
    def test_weather_code(self):self.assertEqual(cloud_code(94),'Overcast')
if __name__=='__main__':unittest.main()
