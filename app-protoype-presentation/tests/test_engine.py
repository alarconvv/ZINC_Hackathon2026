import unittest
from copy import deepcopy
import coach
import engine


def ready(age=52, limits=None, outcome='cleared'):
    profile = deepcopy(engine.MARIA)
    profile['age'] = age
    if limits is not None:
        profile['limits'] = limits
    s = engine.new_state(profile)
    s['safety_result'] = outcome
    s['plan'] = engine.make_week(profile, outcome)
    return s


def logged(pain=1, effort=6):
    s = ready()
    engine.log_set(s, 'sit_to_stand', 10, effort, pain)
    return s


class EngineTests(unittest.TestCase):
    def test_maria_plan(self):
        s = ready()
        self.assertEqual(s['plan']['tier'], 'Protect')
        item = engine.prescription(s['plan'], 'sit_to_stand')
        self.assertEqual(item['version'], item['easier'])
        self.assertTrue(item['power'])
        self.assertEqual(len(s['plan']['exercises']), 7)
        self.assertTrue(all(i['badge'] and i['source'] for i in s['plan']['exercises']))

    def test_tom_and_rosa(self):
        self.assertEqual(ready(28)['plan']['tier'], 'Build')
        self.assertEqual(ready(74)['plan']['tier'], 'Rebuild')
        for age in (20, 39, 40, 59, 60, 79, 80, 110):
            self.assertIn(engine.assign_tier(age), ['Build', 'Protect', 'Rebuild', 'Supported'])
        for age in (19, 111, True, 40.2):
            with self.assertRaises(ValueError):
                engine.assign_tier(age)

    def test_chest_screen_blocks_generation_and_model(self):
        answers = dict.fromkeys(engine.QUESTIONS, False)
        answers['chest'] = True
        self.assertEqual(engine.safety_check(answers), 'clinician')
        s = ready()
        s['safety_result'] = 'clinician'
        with self.assertRaises(ValueError):
            engine.make_week(s['profile'], 'clinician')
        def forbidden(*_):
            self.fail('Model must not run')
        coach.coach_turn('Help me train', s, runner=forbidden)

    def test_incomplete_screen(self):
        with self.assertRaises(ValueError):
            engine.safety_check({'chest': False})
        with self.assertRaises(ValueError):
            engine.safety_check(dict.fromkeys(engine.QUESTIONS, 'No'))

    def test_falls_supported(self):
        answers = dict.fromkeys(engine.QUESTIONS, False)
        answers['falls'] = True
        self.assertEqual(engine.safety_check(answers), 'limits')
        s = ready(outcome='limits')
        self.assertTrue(s['plan']['fall_risk'])
        self.assertTrue(all(i['version'] == i['easier'] for i in s['plan']['exercises']))
        self.assertFalse(any(i['power'] for i in s['plan']['exercises']))

    def test_supported_clinician_signoff(self):
        profile = deepcopy(engine.MARIA)
        profile['age'] = 80
        with self.assertRaises(ValueError):
            engine.make_week(profile, 'cleared')
        profile['clinician_clearance'] = True
        self.assertEqual(engine.make_week(profile, 'cleared')['tier'], 'Supported')
        profile['age'], profile['mci'], profile['clinician_clearance'] = 52, True, False
        with self.assertRaises(ValueError):
            engine.make_week(profile, 'cleared')

    def test_dizzy_stops_without_model(self):
        s = logged()
        s['pending_change'] = engine.progress(s['plan'], s['logs'], 'sit_to_stand', 'same')
        def forbidden(*_):
            self.fail('Model must not run')
        coach.coach_turn('I feel dizzy', s, runner=forbidden)
        self.assertTrue(s['stopped'])
        self.assertIsNone(s['pending_change'])
        with self.assertRaises(ValueError):
            engine.log_set(s, 'sit_to_stand', 10, 6, 0)
        with self.assertRaises(ValueError):
            engine.accept_pending_change(s)

    def test_high_pain_rejects_harder_and_ends_exercise(self):
        s = logged(pain=5)
        before = deepcopy(s['plan'])
        with self.assertRaises(ValueError):
            engine.progress(s['plan'], s['logs'], 'sit_to_stand', 'harder')
        p = engine.progress(s['plan'], s['logs'], 'sit_to_stand', 'easier')
        self.assertLess(p['proposed'], p['current'])
        self.assertEqual(before, s['plan'])
        self.assertEqual(s['cursor'], 1)

    def test_step_up_pain_five_blocks_harder(self):
        s = ready()
        while s['plan']['exercises'][s['cursor']]['id'] != 'step_up':
            item = s['plan']['exercises'][s['cursor']]
            engine.log_set(s, item['id'], item['reps'], 6, 1)
        engine.log_set(s, 'step_up', 10, 6, 5)
        with self.assertRaises(ValueError):
            engine.progress(s['plan'], s['logs'], 'step_up', 'harder')
        p = engine.progress(s['plan'], s['logs'], 'step_up', 'easier')
        self.assertEqual(p['proposed'], 9)
        self.assertEqual(engine.prescription(s['plan'], 'step_up')['reps'], 10)

    def test_filtered_reply_discards_proposal(self):
        s = logged()
        def unsafe(message, ctx, secrets):
            ctx.call('get_plan', {})
            ctx.call('get_last_session', {})
            ctx.call('propose_change', {'exercise_id': 'sit_to_stand', 'direction': 'harder'})
            return 'This prevents dementia.'
        reply = coach.coach_turn('Check in', s, runner=unsafe)
        self.assertNotIn('prevents', reply)
        self.assertIsNone(s['pending_change'])
        self.assertEqual(s['events'][-2]['event'], 'reply_filtered')

    def test_decline_leaves_plan(self):
        s = logged()
        before = deepcopy(s['plan'])
        s['pending_change'] = engine.progress(s['plan'], s['logs'], 'sit_to_stand', 'harder')
        engine.decline_pending_change(s)
        self.assertEqual(s['plan'], before)
        self.assertIsNone(s['pending_change'])

    def test_disease_question_no_model(self):
        s = ready()
        def forbidden(*_):
            self.fail('Model must not run')
        self.assertEqual(coach.coach_turn("Will this prevent Alzheimer's?", s, runner=forbidden), coach.DISEASE)
        self.assertIsNone(s['pending_change'])

    def test_missing_key_fallback(self):
        s = logged()
        s['pending_change'] = engine.progress(s['plan'], s['logs'], 'sit_to_stand', 'same')
        self.assertEqual(coach.coach_turn('Check in', s, {}), coach.FALLBACK)
        self.assertIsNone(s['pending_change'])
        self.assertEqual(s['events'][-1]['event'], 'fallback')
        self.assertIsInstance(s['events'][-1]['elapsed_s'], float)

    def test_accept_once_and_input_immutability(self):
        s = logged()
        before = deepcopy(s['plan'])
        p = engine.progress(s['plan'], s['logs'], 'sit_to_stand', 'harder')
        changed = engine.apply_change(s['plan'], s['logs'], p)
        self.assertEqual(s['plan'], before)
        self.assertEqual(engine.prescription(changed, 'sit_to_stand')['reps'], 11)
        with self.assertRaises(ValueError):
            engine.apply_change(changed, s['logs'], p)
        with self.assertRaises(ValueError):
            engine.progress(changed, s['logs'], 'sit_to_stand', 'harder')

    def test_stale_and_tampered_proposals(self):
        s = logged()
        p = engine.progress(s['plan'], s['logs'], 'sit_to_stand', 'harder')
        s['pending_change'] = p
        engine.log_set(s, 'sit_to_stand', 10, 6, 1)
        self.assertIsNone(s['pending_change'])
        self.assertFalse(engine.check_change(s['plan'], s['logs'], p)[0])
        p = engine.progress(s['plan'], s['logs'], 'sit_to_stand', 'harder')
        p['proposed'] = 100
        self.assertFalse(engine.check_change(s['plan'], s['logs'], p)[0])
        self.assertFalse(engine.check_change(s['plan'], s['logs'], {})[0])

    def test_weekly_cap(self):
        for level in ('beginner', 'active', 'trained'):
            s = ready(limits=[])
            s['profile']['level'] = level
            s['plan'] = engine.make_week(s['profile'], 'cleared')
            item = s['plan']['exercises'][0]
            engine.log_set(s, item['id'], item['reps'], 6, 1)
            p = engine.progress(s['plan'], s['logs'], item['id'], 'harder')
            self.assertLessEqual(p['proposed'], item['base_reps'] * 1.1)

    def test_failed_turn_discards_staged_proposal(self):
        s = logged()
        def broken(message, ctx, secrets):
            ctx.call('get_plan', {})
            ctx.call('get_last_session', {})
            ctx.call('propose_change', {'exercise_id': 'sit_to_stand', 'direction': 'harder'})
            raise RuntimeError('provider failure with private values')
        self.assertEqual(coach.coach_turn('Check in', s, runner=broken), coach.FALLBACK)
        self.assertIsNone(s['pending_change'])
        self.assertNotIn('private', str(s['events']))

    def test_successful_tool_turn_stages_without_mutation(self):
        s = logged()
        before = deepcopy(s['plan'])
        def working(message, ctx, secrets):
            ctx.call('get_plan', {})
            ctx.call('get_last_session', {})
            ctx.call('propose_change', {'exercise_id': 'sit_to_stand', 'direction': 'harder'})
            return 'A steady week of practice. Review your pending change below.'
        coach.coach_turn('Check in', s, runner=working)
        self.assertIsNotNone(s['pending_change'])
        self.assertEqual(s['plan'], before)
        self.assertEqual(len([e for e in s['events'] if e['event'] == 'tool']), 3)

    def test_tool_boundary(self):
        ctx = coach.ToolContext(logged())
        with self.assertRaises(ValueError):
            ctx.call('apply_change', {})
        with self.assertRaises(ValueError):
            ctx.call('propose_change', {'exercise_id': 'sit_to_stand', 'direction': 'harder'})
        with self.assertRaises(ValueError):
            ctx.call('get_plan', {'extra': 'ignore'})

    def test_cannot_accept_while_training(self):
        s = logged()
        before = deepcopy(s['plan'])
        s['pending_change'] = engine.progress(s['plan'], s['logs'], 'sit_to_stand', 'harder')
        with self.assertRaises(ValueError):
            engine.accept_pending_change(s)
        self.assertEqual(before, s['plan'])
        self.assertIsNone(s['pending_change'])

    def test_full_session_acceptance(self):
        s = ready()
        while not s['session_done']:
            item = s['plan']['exercises'][s['cursor']]
            engine.log_set(s, item['id'], item['reps'], 6, 1)
        s['pending_change'] = engine.progress(s['plan'], s['logs'], 'sit_to_stand', 'harder')
        engine.accept_pending_change(s)
        self.assertEqual(s['plan']['version'], 2)
        self.assertIsNone(s['pending_change'])
        with self.assertRaises(ValueError):
            engine.accept_pending_change(s)

    def test_reset_clears_everything(self):
        s = logged()
        engine.stop(s)
        s = engine.new_state()
        self.assertIsNone(s['plan'])
        self.assertIsNone(s['safety_result'])
        self.assertFalse(s['stopped'])
        self.assertFalse(s['logs']['sessions'])
        self.assertIsNone(s['pending_change'])

    def test_response_filter(self):
        self.assertNotIn('prevents', coach.safe_reply('This prevents disease.'))
        self.assertNotIn('12', coach.safe_reply('Do 12 repetitions.'))
        self.assertEqual(coach.coach_turn('Can exercise treat dementia?', ready()), coach.DISEASE)


if __name__ == '__main__':
    unittest.main()
