"""Red Line must offer real engagements without sacrificing protected units."""
import unittest

import build_pack as bp
import test_build_pack as fixtures
from test_build_pack import small_mission, rendered


class RedLinePacing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=next(s for s in bp.campaign_specs() if s['SLUG']=='sest-red-line')
        cls.missions={m['code']:m for m in spec['MISSIONS']}

    def test_opening_pair_are_shorter_and_have_scripted_shooters(self):
        for code,limit in [('RL01',40),('RL02',55)]:
            m=self.missions[code]
            self.assertEqual(m['minutes'],limit)
            attacks=[a for u in m['units'] for a in u.get('attacks',[])]
            self.assertGreaterEqual(len(attacks),2)
            self.assertLessEqual(min(a[0] for a in attacks),10)
            self.assertTrue(all(a[0]>=bp.OPENING_QUIET_MIN for a in attacks))

    def test_alpha_classification_cannot_hold_up_carrier_defence(self):
        m=self.missions['RL01']
        self.assertNotIn('after',m['victory'])
        self.assertEqual(m['resolve']['Trail'],('classify','red_sub',1))
        kill=next(t for t in m['victory']['also'] if t['kind']=='destroyed')
        self.assertEqual(set(kill['units']),{'raider_e','raider_ne'})
        self.assertEqual(kill['min_units'],2)

    def test_tanker_has_a_guaranteed_airborne_asw_search(self):
        m=self.missions['RL02']
        air=[u for u in m['units'] if u['side']=='blue' and u['type']=='plan_z-18f']
        self.assertEqual(len(air),1)
        self.assertNotIn('slot',air[0])
        self.assertEqual(air[0]['loadout'],'ASW')
        self.assertEqual(next(u for u in m['units'] if u['station']=='red_air')['side'],'neutral')
        golf=next(u for u in m['units'] if u.get('name')=='Contact GOLF')
        self.assertEqual([(a[0],a[1],a[2]) for a in golf['attacks']],[(10,'usn_mk48_7','tanker'),(18,'usn_mk48_7','tanker')])

    def test_golf_consequence_and_datum_are_preserved(self):
        m=self.missions['RL02'];later=self.missions['RL04']
        self.assertEqual(m['reveal_if'][0]['variable'],'RLO1GolfDatum')
        self.assertEqual(m['reveal_if'][0]['time'],900)
        self.assertEqual(m['flags'][0]['name'],'RL02GolfSunk')
        golf=next(u for u in later['units'] if u.get('name')=='Contact GOLF')
        self.assertEqual(golf['spawn_if'],('RL02GolfSunk','IsFalse'))
        self.assertFalse(any('red_sub' in (f.get('units') or []) for f in later['fatal']))

    def test_protected_observers_are_not_on_the_attackers_taskforce(self):
        refs={'RL01':['red_sub','red_air','triton','wedgetail'],
              'RL02':['red_air'],'RL03':['convoy','jmsdf','growler','rivet'],
              'RL04':['red_air','red_sub']}
        for code,stations in refs.items():
            for u in self.missions[code]['units']:
                if u['station'] in stations:
                    self.assertEqual(u['side'],'neutral',(code,u['station']))
                    self.assertEqual(u.get('weapons','Hold'),'Hold',(code,u['station']))
                    self.assertNotIn('attacks',u)

    def test_interceptors_are_released_after_preparation_and_will_attack(self):
        for code in ['RL03','RLO2']:
            fighters=[u for u in self.missions[code]['units'] if u['station']=='red_air']
            self.assertEqual(len(fighters),2)
            for u in fighters:
                self.assertEqual(u['enter'],8)
                self.assertEqual(u['weapons'],'Free')
                self.assertTrue(u['attacks'])
                self.assertTrue(all(a[0]>u['enter'] for a in u['attacks']))

    def test_other_picture_does_not_require_cap_purchases_or_a_long_ship_search(self):
        m=self.missions['RL03']
        fixed=[u for u in m['units'] if u['side']=='blue' and u['type']=='plan_j-15' and not u.get('slot')]
        self.assertEqual(len(fixed),2)
        self.assertEqual(m['victory']['station'],'eye')
        self.assertNotIn('after',m['victory'])
        self.assertEqual(m['resolve']['Names'],('classify',['convoy#1','jmsdf#1','jmsdf#2'],3))

    def test_withdrawal_has_two_simultaneous_problems(self):
        m=self.missions['RL04']
        self.assertEqual(m['resolve']['Spoiler'],('destroy','spoiler',1))
        qship=next(u for u in m['units'] if u['station']=='qship')
        self.assertEqual(qship['attacks'][0][2],'group#2')
        self.assertIn('Supply',{f['objective'] for f in m['fatal']})

    def test_one_compact_stealth_crossing_is_retained(self):
        m=self.missions['RL05']
        self.assertEqual(m['minutes'],60)
        self.assertIn('Unseen',{f['objective'] for f in m['fatal']})
        self.assertFalse(any(u.get('attacks') for u in m['units']))
        self.assertLess(bp.nm_between(m['stations']['boat']['at'],m['victory']['at']),13)

    def test_tender_defence_replaces_the_long_idle_decoy(self):
        m=self.missions['RL06']
        self.assertEqual(m['minutes'],45)
        self.assertEqual(m['victory']['after']['after_minutes'],8)
        self.assertNotIn('Unseen',{f['objective'] for f in m['fatal']})
        self.assertTrue({'Tender','Boat'} <= {f['objective'] for f in m['fatal']})
        self.assertEqual(next(u for u in m['units'] if u['station']=='qship')['attacks'][0][2],'tender')

    def test_combat_exits_wait_for_detected_incoming_weapons(self):
        for code in ['RL01','RL02','RL03','RL04','RL06','RLO2']:
            self.assertIn({'kind':'no_incoming'},self.missions[code]['victory']['also'])
        m=small_mission(victory=dict(small_mission()['victory'],also=[dict(kind='time',after_minutes=20),dict(kind='no_incoming')]))
        win=rendered(m)['Objective met']
        self.assertIn('Condition_Condition3_Type=NoIncomingWeapons',win)
        self.assertIn('Condition_Condition3_Taskforce=Taskforce1',win)
        self.assertIn('ConditionsCompleted=<Condition1> AND <Condition2> AND <Condition3>',win)


class TimedStrikes(unittest.TestCase):
    def setUp(self):
        # Reuse the small real coastline/loaded-054A fixture, not a mock
        # weapon catalog that could accept nonexistent ammunition.
        self.fixture=fixtures.DefectorEscortFeatures()
        self.fixture.setUp()

    def place(self,attacks,**over):
        shooter=self.fixture.frigate([],attacks=attacks,**over)
        m=self.fixture.mission([self.fixture.ANZAC,self.fixture.CORVETTE,self.fixture.Z9,shooter])
        return self.fixture.place(m)

    def test_native_timed_strike_resolves_the_allocated_target(self):
        placed,*_=self.place([(8,'plan_yj-83a','defector',2),(12,'plan_yj-83a','defector',1)])
        keys=self.fixture.sections(placed)['Taskforce2Vessel1']
        self.assertEqual(keys['Attack'],'Taskforce1Vessel2,480,plan_yj-83a,2|Taskforce1Vessel2,720,plan_yj-83a,1')
        self.assertEqual(keys['OverrideWeaponStatus'],'Tight')
        self.assertNotIn(bp.TARGET_MARK,keys['Attack'])

    def test_loaded_torpedo_room_is_a_real_scripted_store(self):
        self.assertIn('usn_mk48_7',bp.scripted_stores('usn_ssn_virginia_2027',{}))

    def test_invalid_or_unfair_strikes_are_rejected(self):
        bad=[(1,'plan_yj-83a','defector',1),(80,'plan_yj-83a','defector',1),
             (float('nan'),'plan_yj-83a','defector',1),(True,'plan_yj-83a','defector',1),
             (8,'not_loaded','defector',1),(8,'plan_yj-83a','defector',0),
             (8,'plan_yj-83a','defector',True),(8,'plan_yj-83a','helo',1)]
        for strike in bad:
            with self.subTest(strike=strike),self.assertRaises(SystemExit):self.place([strike])

    def test_a_disabled_shooter_cannot_receive_an_earlier_order(self):
        with self.assertRaises(SystemExit):self.place([(8,'plan_yj-83a','defector',1)],enter=8)

    def test_all_authored_strike_rounds_exist_in_the_selected_fits(self):
        for m in RedLinePacing.missions.values():
            for u in m['units']:
                if not u.get('attacks'):continue
                _,keys,_=bp.resolve(dict(u,mission=m['key']),m['date'][0])
                for a in u['attacks']:self.assertIn(a[1],bp.scripted_stores(u['type'],keys))


if __name__=='__main__':unittest.main()
