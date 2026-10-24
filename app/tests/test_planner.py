from copy import deepcopy
import unittest
import engine
import progress_board


class PlannerTests(unittest.TestCase):
    def state(self, supported=False):
        state = engine.new_state()
        state['safety_result'] = 'limits' if supported else 'cleared'
        state['plan'] = engine.make_week(state['profile'], state['safety_result'], start_date='2026-10-19')
        return state

    def test_choose_days_keeps_baseline_and_does_not_mutate_input(self):
        state = self.state()
        original = deepcopy(state['plan'])
        choices = {'strength': [1, 4], 'yoga': [0, 3], 'brain': [2, 6], 'relaxation': [4, 6]}
        plan = engine.choose_days(state['plan'], choices)
        self.assertEqual(state['plan'], original)
        self.assertEqual(plan['days'], ['Tue', 'Fri'])
        self.assertEqual([a['date'] for a in plan['activities'] if a['section'] == 'strength'], ['2026-10-20', '2026-10-23'])
        choices['strength'] = [0]
        with self.assertRaises(ValueError): engine.choose_days(state['plan'], choices)

    def test_reschedule_preserves_identity_feedback_and_resume(self):
        state = self.state()
        activity = next(a for a in state['plan']['activities'] if a['section'] == 'yoga')
        engine.start_activity(state, activity['id'])
        engine.log_yoga(state, 5, 1)
        saved = deepcopy(engine.active_session(state))
        engine.change_schedule(state, activity_id=activity['id'], day=2)
        resumed = engine.start_activity(state, activity['id'])
        self.assertEqual(resumed['date'], '2026-10-21')
        self.assertEqual(resumed['pose_index'], 1)
        self.assertEqual(resumed['session_id'], saved['session_id'])
        self.assertEqual(resumed['feedback'], saved['feedback'])

    def test_invalid_edits_are_atomic_and_finished_activity_is_locked(self):
        state = self.state()
        activity = next(a for a in state['plan']['activities'] if a['section'] == 'yoga')
        before = deepcopy(state)
        for change in (dict(activity_id=activity['id'], day=5), dict(section='strength', day=6), dict(section='brain', day=True), dict(activity_id=activity['id'], remove=True)):
            with self.assertRaises(ValueError): engine.change_schedule(state, **change)
            self.assertEqual(state, before)
        engine.start_activity(state, activity['id'])
        engine.finish_activity(state, skipped=True)
        before = deepcopy(state)
        with self.assertRaises(ValueError): engine.change_schedule(state, activity_id=activity['id'], day=2)
        self.assertEqual(state, before)

    def test_optional_extra_does_not_lower_baseline_completion(self):
        state = self.state()
        for activity in state['plan']['activities']:
            state['activity_sessions'][activity['id']] = {**activity, 'status': 'completed', 'finished': True}
        engine.change_schedule(state, section='relaxation', day=2)
        board = progress_board.summarize(state['plan'], state['activity_sessions'])
        self.assertEqual(board['percent'], 100)
        self.assertEqual((board['extra_done'], board['extra_total']), (0, 1))
        extra = next(a for a in state['plan']['activities'] if a['optional'])
        engine.change_schedule(state, activity_id=extra['id'], remove=True)
        self.assertEqual(len(state['plan']['activities']), 8)

    def test_strength_spacing_frequency_and_supported_limits(self):
        state = self.state()
        engine.change_schedule(state, section='strength', day=5)
        self.assertEqual(len(state['plan']['days']), 3)
        with self.assertRaises(ValueError): engine.change_schedule(state, section='strength', day=2)
        state = self.state(supported=True)
        with self.assertRaises(ValueError): engine.change_schedule(state, section='strength', day=5)

    def test_schedule_carries_forward_without_losing_staged_prescription(self):
        state = self.state()
        strength = next(a for a in state['plan']['activities'] if a['section'] == 'strength')
        engine.start_activity(state, strength['id'])
        while not state['session_done']:
            item = state['plan']['exercises'][state['cursor']]
            engine.log_set(state, item['id'], item['reps'], 6, 1)
        state['pending_change'] = engine.progress(state['plan'], state['logs'], 'sit_to_stand', 'harder')
        engine.accept_pending_change(state)
        engine.change_schedule(state, section='relaxation', day=2)
        self.assertEqual(engine.prescription(state['next_plan'], 'sit_to_stand')['reps'], 11)
        self.assertEqual(engine.prescription(state['plan'], 'sit_to_stand')['reps'], 10)
        previous = deepcopy(state['plan'])
        engine.start_next_week(state)
        self.assertEqual(state['history'][-1], previous)
        self.assertEqual(sum(a['optional'] for a in state['plan']['activities']), 1)
        self.assertEqual(engine.prescription(state['plan'], 'sit_to_stand')['reps'], 11)
        self.assertTrue(all(a['id'].startswith('w2-') for a in state['plan']['activities']))

    def test_previous_sunday_blocks_following_monday_strength(self):
        state = self.state()
        choices = {'strength': [2, 6], 'yoga': [1, 5], 'brain': [1, 5], 'relaxation': [1, 5]}
        state['plan'] = engine.choose_days(state['plan'], choices)
        engine.start_next_week(state)
        sunday = next(a for a in state['plan']['activities'] if a['section'] == 'strength' and a['date'].endswith('01'))
        with self.assertRaises(ValueError): engine.change_schedule(state, activity_id=sunday['id'], day=0)

    def test_stop_blocks_calendar_edits(self):
        state = self.state()
        engine.stop(state)
        before = deepcopy(state)
        with self.assertRaises(ValueError): engine.change_schedule(state, section='yoga', day=2)
        self.assertEqual(state, before)


class PlannerUITests(unittest.TestCase):
    def test_custom_onboarding_add_move_remove_and_next_action(self):
        from test_app import AppTests, button
        at = AppTests().fresh()
        for radio in at.radio: radio.set_value('No')
        button(at, 'Continue to focus').click().run()
        at.multiselect(key='choose_strength_days').set_value(['Tue', 'Fri'])
        button(at, 'Create my complete week').click().run()
        self.assertEqual(at.session_state['zinc']['plan']['days'], ['Tue', 'Fri'])
        button(at, 'Start next activity').click().run()
        self.assertEqual(at.session_state['page'], 'Train')
        at.radio(key='page').set_value('Your week').run()
        at.selectbox[0].set_value('relaxation')
        at.selectbox[1].set_value('Wed')
        button(at, 'Add to my week').click().run()
        extra = next(a for a in at.session_state['zinc']['plan']['activities'] if a['optional'])
        self.assertEqual(extra['date'], '2026-10-21')
        # Target the form for the specific extra, not one of the baseline move controls.
        remove = next(b for b in at.button if b.label == 'Remove optional activity')
        remove.click().run()
        self.assertFalse(any(a['optional'] for a in at.session_state['zinc']['plan']['activities']))
        self.assertFalse(at.exception)
