"""Regression gates for activity isolation and deterministic history."""
from copy import deepcopy
from datetime import date, datetime, timedelta
import unittest
from unittest.mock import patch
import engine
from test_engine import ready


class EngineRegressions(unittest.TestCase):
    def start(self, state, section):
        activity = next(a for a in state['plan']['activities'] if a['section'] == section)
        return engine.start_activity(state, activity['id'])

    def test_strength_callback_cannot_mutate_other_activity(self):
        for section in ('yoga', 'brain', 'relaxation'):
            with self.subTest(section=section):
                state = ready()
                self.start(state, section)
                before = deepcopy(state)
                with self.assertRaises(ValueError):
                    engine.log_set(state, 'sit_to_stand', 10, 6, 0)
                self.assertEqual(state, before)

    def test_strength_sessions_have_distinct_identity_and_resume(self):
        state = ready()
        first = self.start(state, 'strength')
        engine.log_set(state, 'sit_to_stand', 10, 6, 0)
        activity = [a for a in state['plan']['activities'] if a['section'] == 'strength'][1]
        second = engine.start_activity(state, activity['id'])
        self.assertNotEqual(first['session_id'], second['session_id'])
        self.assertEqual(state['set_index'], 0)
        engine.log_set(state, 'sit_to_stand', 10, 5, 0)
        self.assertEqual(state['logs']['sessions'][0]['session_id'], first['session_id'])
        self.assertEqual(state['logs']['sessions'][1]['session_id'], second['session_id'])
        self.assertIs(engine.start_activity(state, first['activity_id']), first)
        self.assertEqual(state['set_index'], 1)

    def test_week_dates_use_monday_and_eastern_clock(self):
        with patch('engine.datetime') as clock:
            clock.now.return_value = datetime(2026, 10, 25, 23, 30)
            plan = engine.make_week(deepcopy(engine.MARIA), 'cleared')
            self.assertEqual(str(clock.now.call_args.args[0]), 'America/New_York')
            self.assertEqual(plan['start_date'], '2026-10-19')
        with self.assertRaises(ValueError):
            engine.make_week(deepcopy(engine.MARIA), 'cleared', start_date=date(2026, 10, 23))
        for activity in plan['activities']:
            self.assertEqual(date.fromisoformat(activity['date']).weekday(), int(activity['id'].rsplit('-', 1)[1]))

    def test_apply_change_dates_follow_new_week(self):
        state = ready()
        engine.log_set(state, 'sit_to_stand', 10, 6, 0)
        proposal = engine.progress(state['plan'], state['logs'], 'sit_to_stand', 'harder')
        changed = engine.apply_change(state['plan'], state['logs'], proposal)
        self.assertEqual(date.fromisoformat(changed['start_date']), date.fromisoformat(state['plan']['start_date']) + timedelta(days=7))
        self.assertTrue(all(a['week'] == 2 and a['id'].startswith('w2-') for a in changed['activities']))

    def test_clearance_and_boolean_boundaries(self):
        for field in ('clinician_clearance', 'mci'):
            profile = deepcopy(engine.MARIA)
            profile.update(age=80, **{field: 'False'})
            with self.assertRaises(ValueError):
                engine.make_week(profile, 'cleared')
        state = ready()
        self.start(state, 'relaxation')
        before = deepcopy(state)
        for kwargs in ({'minutes': 3.0}, {'skipped': 'False'}):
            with self.assertRaises(ValueError):
                engine.finish_activity(state, **kwargs)
            self.assertEqual(before, state)

    def test_rollover_preserves_three_weeks_of_independent_logs(self):
        state = ready()
        ids = []
        for week in range(1, 4):
            activity = self.start(state, 'strength')
            ids.append(activity['session_id'])
            while not state['session_done']:
                item = state['plan']['exercises'][state['cursor']]
                engine.log_set(state, item['id'], item['reps'], 6, 0)
            state['pending_change'] = engine.progress(state['plan'], state['logs'], 'sit_to_stand', 'harder')
            engine.accept_pending_change(state)
            self.assertEqual(state['plan']['exercises'][0]['reps'], 9 + week)
            engine.start_next_week(state)
            with self.assertRaises(ValueError):
                engine.progress(state['plan'], state['logs'], 'sit_to_stand', 'harder')
        self.assertEqual(len(set(ids)), 3)
        self.assertEqual(len(state['history']), 3)
        self.assertEqual(len(state['logs']['sessions']), 36)
        self.assertEqual(state['plan']['exercises'][0]['reps'], 13)

    def test_legacy_unfinished_strength_blocks_rollover(self):
        state = ready()
        engine.log_set(state, 'sit_to_stand', 10, 6, 0)
        with self.assertRaises(ValueError):
            engine.start_next_week(state)
        self.assertEqual(state['history'], [])

    def test_version_boolean_does_not_pass_proposal_validation(self):
        state = ready()
        engine.log_set(state, 'sit_to_stand', 10, 6, 0)
        proposal = engine.progress(state['plan'], state['logs'], 'sit_to_stand', 'harder')
        proposal['plan_version'] = True
        self.assertFalse(engine.check_change(state['plan'], state['logs'], proposal)[0])

    def test_historical_puzzle_level_survives_future_adaptation(self):
        state = ready()
        first = self.start(state, 'brain')
        self.assertEqual(first['answers'], [])
        for _ in range(5):
            engine.answer_puzzle(state, engine.current_puzzle(state)['answer'])
        self.assertEqual([a['level_after'] for a in first['answers']], [1, 1, 2, 2, 2])
        historical = deepcopy(first['answers'])
        engine.start_next_week(state)
        second = self.start(state, 'brain')
        self.assertEqual(second['answers'], [])
        for _ in range(5):
            engine.answer_puzzle(state, engine.current_puzzle(state)['answer'])
        self.assertGreater(state['brain_level'], historical[-1]['level_after'])
        self.assertEqual(first['answers'], historical)

    def test_plan_does_not_alias_profile_or_prior_week(self):
        profile = deepcopy(engine.MARIA)
        plan = engine.make_week(profile, 'cleared')
        profile['toggles']['yoga'] = True
        profile['limits'].clear()
        self.assertFalse(plan['toggles']['yoga'])
        self.assertIn('Seated', plan['yoga'][0]['version'])
        state = ready()
        self.start(state, 'relaxation')
        engine.finish_activity(state, minutes=3)
        prior = deepcopy(state['plan'])
        engine.start_next_week(state)
        state['plan']['exercises'][0]['reps'] = 999
        state['plan']['yoga'][0]['version'] = 'changed'
        self.assertEqual(state['history'][0], prior)
