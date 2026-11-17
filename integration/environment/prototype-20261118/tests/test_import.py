import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from import_openmeteo import make_grid,make_url,parse_response,convert
class ImportTests(unittest.TestCase):
    def test_urls_and_grid(self):
        self.assertEqual(len(make_grid('weddell',3,4)),12)
        url=make_url(-55,-36,'2025-09-14','2025-09-15','archive')
        self.assertIn('archive-api.open-meteo.com',url)
        self.assertIn('wind_speed_unit=ms',url)
        self.assertIn('cell_selection=sea',url)
    def test_validation(self):
        p={'hourly':{'time':['2025-09-14T00:00'],'cloud_cover':[90], 'precipitation':[0.3], 'wind_speed_10m':[12], 'wind_direction_10m':[260], 'pressure_msl':[989]},
           'hourly_units':{'cloud_cover':'%','precipitation':'mm','wind_speed_10m':'m/s','wind_direction_10m':'°','pressure_msl':'hPa'}}
        values=parse_response(p,-52,-38,'archive')
        self.assertEqual(values['readings'][0]['source_time_utc'],'2025-09-14T00:00Z')
        self.assertEqual(values['readings'][0]['values']['wind_speed_10m'],12.0)
        self.assertEqual(convert([values],'archive','2025-09-14','2025-09-15','weddell')['schema'],'mno.env.observations.v0.1')
        p['hourly_units']['wind_speed_10m']='km/h'
        with self.assertRaises(ValueError):parse_response(p,-52,-38,'archive')
if __name__=='__main__':unittest.main()
