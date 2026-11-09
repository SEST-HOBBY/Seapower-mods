"""World geometry, logistics and command-progression acceptance checks."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'integration/world-sandbox'

class WorldOperationsRealism(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = json.loads((HERE/'SEST_World_Campaign/dynamic_campaigns/sest-world-regions-2028/campaign.json').read_text())
        cls.spec = json.loads((HERE/'world-operations-2028.json').read_text())
        cls.bases = {b['id']: b for b in cls.world['bases']}

    def test_muharraq_and_other_fields_use_reviewed_land_positions(self):
        from global_land_mask import globe
        for fix in self.spec['corrections']:
            b = self.bases[fix['id']]
            lat, lon = fix.get('placement',fix['point'])
            self.assertAlmostEqual(b['lat'],lat)
            self.assertAlmostEqual(((b['lon']+180)%360)-180,lon)
            self.assertEqual([b['field']['lat'],b['field']['lon']],[b['lat'],b['lon']])
            self.assertTrue(globe.is_land(lat,lon),fix['id'])
        m=self.bases['me_bahrain_muharraq_airfield']
        self.assertAlmostEqual(m['lat'],26+16/60+15/3600,places=5)
        self.assertAlmostEqual(m['lon'],50+38/60+1/3600,places=5)
        self.assertAlmostEqual(m['field']['heading'],122.62)
        self.assertAlmostEqual(self.bases['home_rus_severomorsk3']['lat'],68.866669)

    def test_added_fields_are_usable_and_do_not_create_extra_armies_or_income(self):
        from global_land_mask import globe
        self.assertEqual(len(self.spec['sites']),40)
        self.assertEqual(sum(b['id'].startswith('ops_') for b in self.world['bases']),40)
        self.assertEqual(len(self.world['forces']),293)
        for site in self.spec['sites']:
            b=self.bases[site['base']['id']];source=self.bases[b['supplyFrom']]
            self.assertTrue(source['depot']);self.assertEqual(source['side'],b['side'])
            self.assertEqual(b['income'],0);self.assertEqual(b['startShare'],0.25)
            self.assertFalse(b.get('depot'));self.assertFalse(b.get('shipyard'));self.assertNotIn('production',b)
            self.assertTrue(globe.is_land(b['lat'],((b['lon']+180)%360)-180),b['id'])
            self.assertGreaterEqual(b['lon'],-100);self.assertLessEqual(b['lon'],258)
            self.assertFalse(any(f['base']==b['id'] for f in self.world['forces']))

    def test_eight_stages_give_small_early_goals_and_reachable_catalogue(self):
        self.assertEqual(self.world['ranks']['blue'],self.world['ranks']['red'])
        for side in ['blue','red']:
            stages=self.world['ranks'][side];thresholds=[r['renown'] for r in stages]
            self.assertEqual(thresholds,[0,300,800,1600,2800,4500,7000,10500])
            entries=[e for e in self.world['catalogue'] if e['side']==side]
            self.assertEqual({r['tier'] for r in entries},set(range(8)))
            self.assertTrue(all(0<=e['tier']<len(stages) for e in entries))
            self.assertTrue(any(e['tier']==0 and e.get('aircraft') for e in entries))
            self.assertTrue(any(e['tier']==0 and not e.get('aircraft') for e in entries))
        self.assertEqual(self.world['ai']['startTier'],7)

    def test_realism_briefing_and_original_coalitions_remain_explicit(self):
        text=json.dumps(self.world['story'])
        self.assertIn('SUSTAINMENT',text);self.assertIn('Victory is not required',text)
        self.assertNotIn('SEST research',text);self.assertNotIn('This is a sandbox',text)
        original=json.loads((HERE/'SEST_World_Campaign/legacy_campaigns/sest-world-sandbox/campaign.json').read_text())
        self.assertEqual([s['nations'] for s in self.world['sides']],[s['nations'] for s in original['sides']])
        self.assertEqual(self.world['replenishment']['usn_tao_kaiser'],original['replenishment']['usn_tao_kaiser'])
        self.assertEqual(self.world['convoys'],original['convoys'])

if __name__=='__main__': unittest.main()
