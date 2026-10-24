"""Cross-section acceptance checks for the V261023 fictional prototype."""
from copy import deepcopy
from datetime import date
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
import coach
import engine
from test_app import ROOT, button, checkbox
from test_engine import ready


class AcceptanceTests(unittest.TestCase):
    def onboard(self, create=True):
        at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30).run()
        button(at, 'Try the demo with Maria').click().run()
        checkbox(at, 'I am using fictional information for this prototype.').check()
        button(at, 'Continue to safety').click().run()
        for radio in at.radio:
            radio.set_value('No')
        button(at, 'Continue to focus').click().run()
        if create:
            button(at, 'Create my complete week').click().run()
        self.assertFalse(at.exception)
        return at

    def start(self, state, section, index=0):
        activity = [a for a in state['plan']['activities'] if a['section'] == section][index]
        return engine.start_activity(state, activity['id'])

    def open(self, at, section):
        at.radio(key='page').set_value('Your week').run()
        activity = next(a for a in at.session_state['zinc']['plan']['activities'] if a['section'] == section)
        at.button(key='start_' + activity['id']).click().run()
        self.assertFalse(at.exception)

    def test_focus_combinations_add_only_documented_sunday_sections(self):
        baseline = ready()['plan']
        for yoga, brain, expected in [(False, False, []), (True, False, ['yoga']),
                                     (False, True, ['brain', 'relaxation']),
                                     (True, True, ['brain', 'relaxation', 'yoga'])]:
            with self.subTest(yoga=yoga, brain=brain):
                profile = deepcopy(engine.MARIA)
                profile['toggles'] = {'yoga': yoga, 'brain': brain}
                plan = engine.make_week(profile, 'cleared', start_date=date(2026, 10, 19))
                self.assertEqual(plan['days'], baseline['days'])
                self.assertEqual(sorted(a['section'] for a in plan['activities'] if a['date'] == '2026-10-25'), expected)
                self.assertEqual({a['section'] for a in plan['activities']}, {'strength', 'yoga', 'brain', 'relaxation'})
                self.assertEqual(len({a['id'] for a in plan['activities']}), len(plan['activities']))
                self.assertTrue(all(a['date'] and a['week'] == 1 for a in plan['activities']))

    def test_focus_back_navigation_preserves_all_answers_and_date(self):
        at = self.onboard(create=False)
        checkbox(at, 'Extra yoga').check()
        checkbox(at, 'Extra brain and relaxation').check()
        at.date_input[0].set_value(date(2026, 11, 2))
        button(at, 'Back to safety').click().run()
        self.assertTrue(all(r.value == 'No' for r in at.radio))
        button(at, 'Back to profile').click().run()
        self.assertEqual(at.text_input[0].value, 'Maria')
        self.assertEqual(at.multiselect[0].value, ['knees'])
        button(at, 'Continue to safety').click().run()
        button(at, 'Continue to focus').click().run()
        self.assertTrue(checkbox(at, 'Extra yoga').value)
        self.assertTrue(checkbox(at, 'Extra brain and relaxation').value)
        self.assertEqual(at.date_input[0].value, date(2026, 11, 2))
        button(at, 'Create my complete week').click().run()
        self.assertEqual(at.session_state['zinc']['plan']['start_date'], '2026-11-02')
        self.assertFalse(at.exception)

    def test_symptom_form_locks_every_activity_and_coach_without_network(self):
        for section in ('strength', 'yoga', 'brain', 'relaxation'):
            with self.subTest(section=section):
                at = self.onboard()
                self.open(at, section)
                at.text_input[0].set_value('I feel dizzy')
                with patch.object(coach, 'run_model', side_effect=AssertionError('No network after symptoms')):
                    button(at, 'Check symptoms').click().run()
                    state = at.session_state['zinc']
                    self.assertTrue(state['stopped'])
                    self.assertIsNone(state['pending_change'])
                    self.assertNotEqual(coach.coach_turn('Help with my week', state), coach.FALLBACK)
                    for candidate in state['plan']['activities']:
                        with self.assertRaises(ValueError):
                            engine.start_activity(state, candidate['id'])
                self.assertFalse(at.exception)
                self.assertFalse(any(b.label == 'Weekly check-in' for b in at.button))

    def test_mixed_status_board_across_two_weeks(self):
        at = self.onboard()
        state = at.session_state['zinc']
        self.start(state, 'strength')
        item = state['plan']['exercises'][0]
        engine.log_set(state, item['id'], item['reps'], 6, 1)
        engine.finish_activity(state, skipped=True)
        self.start(state, 'yoga')
        engine.finish_activity(state, skipped=True)
        self.start(state, 'brain')
        for _ in range(5):
            engine.answer_puzzle(state, engine.current_puzzle(state)['answer'])
        self.start(state, 'relaxation')
        engine.finish_activity(state, minutes=5)
        original = deepcopy(state['activity_sessions'])
        engine.start_next_week(state)
        self.start(state, 'relaxation')
        engine.finish_activity(state, skipped=True)
        at.radio(key='page').set_value('Progress').run()
        self.assertEqual(len(at.selectbox[0].options), 2)
        self.assertTrue(all(option.startswith('Week ') for option in at.selectbox[0].options))
        at.selectbox[0].set_value(1).run()
        board = at.dataframe[0].value
        self.assertEqual(board['Status'].value_counts().to_dict(), {'not started': 4, 'completed': 2, 'partial': 1, 'skipped': 1})
        text = ' '.join(x.value for x in at.markdown)
        self.assertIn('Relaxation: 5 self-reported minutes', text)
        self.assertIn('Reasoning accuracy: 100%', text)
        for key, session in original.items():
            self.assertEqual(at.session_state['zinc']['activity_sessions'][key], session)
        at.selectbox[0].set_value(2).run()
        self.assertEqual(at.dataframe[0].value['Status'].value_counts().to_dict(), {'not started': 7, 'skipped': 1})
        self.assertIn('Relaxation: 0 self-reported minutes', ' '.join(x.value for x in at.markdown))
        self.assertFalse(at.exception)

    def test_relaxation_lengths_skip_and_accessible_instructions(self):
        for minutes in (3, 5):
            at = self.onboard()
            self.open(at, 'relaxation')
            at.radio[1].set_value(minutes).run()
            markup = ' '.join(m.value for m in at.markdown)
            self.assertIn('prefers-reduced-motion:reduce', markup)
            self.assertIn('animation:breathe 10s', markup)
            self.assertIn('Breathe in for five seconds and out for five seconds', markup)
            button(at, 'I completed my breathing practice').click().run()
            state = at.session_state['zinc']
            first = state['activity_sessions'][state['active_activity']]
            self.assertEqual(first['completed_minutes'], minutes)
            self.assertEqual(first['status'], 'completed')
            second = self.start(state, 'relaxation', index=1)
            engine.finish_activity(state, skipped=True)
            self.assertEqual(second['completed_minutes'], 0)
            self.assertEqual(second['status'], 'skipped')
            self.assertFalse(at.exception)

    def test_reruns_do_not_repeat_submitted_work(self):
        at = self.onboard()
        for section, label in [('strength', 'Done set'), ('yoga', 'Done pose'), ('brain', 'Check answer')]:
            self.open(at, section)
            if section == 'brain':
                at.number_input[0].set_value(engine.current_puzzle(at.session_state['zinc'])['answer'])
            button(at, label).click().run()
            before = deepcopy(at.session_state['zinc']['activity_sessions'])
            logs = deepcopy(at.session_state['zinc']['logs'])
            at.run()
            self.assertEqual(before, at.session_state['zinc']['activity_sessions'])
            self.assertEqual(logs, at.session_state['zinc']['logs'])
        self.open(at, 'relaxation')
        button(at, 'I completed my breathing practice').click().run()
        before = deepcopy(at.session_state['zinc']['activity_sessions'])
        at.run()
        self.assertEqual(before, at.session_state['zinc']['activity_sessions'])
        self.assertFalse(at.exception)

    def test_coach_reads_mixed_activity_history_without_mutating_plan(self):
        state = ready()
        self.start(state, 'yoga')
        engine.log_yoga(state, 3, 0)
        engine.finish_activity(state, skipped=True)
        self.start(state, 'brain')
        engine.answer_puzzle(state, engine.current_puzzle(state)['answer'])
        engine.finish_activity(state, skipped=True)
        self.start(state, 'relaxation')
        engine.finish_activity(state, minutes=3)
        before = deepcopy(state['plan'])
        def runner(message, context, secrets):
            plan = context.call('get_plan', {})
            history = context.call('get_last_session', {})
            self.assertEqual(plan['plan'], before)
            self.assertEqual({a['section'] for a in history['activities']}, {'yoga', 'brain', 'relaxation'})
            self.assertEqual(history['activities'][-1]['completed_minutes'], 3)
            plan['plan']['week'] = 999
            return 'Your week includes yoga, reasoning practice and a calm breathing routine.'
        reply = coach.coach_turn('Explain my complete week', state, runner=runner)
        self.assertNotEqual(reply, coach.FALLBACK)
        self.assertEqual(state['plan'], before)
        self.assertIsNone(state['pending_change'])

    def test_missing_configuration_is_local_labelled_fallback(self):
        state = ready()
        with patch.object(coach, 'run_model', wraps=coach.run_model):
            self.assertEqual(coach.coach_turn('Check my week', state, secrets={}), coach.FALLBACK)
        event = state['events'][-1]
        self.assertEqual(event['event'], 'fallback')
        self.assertGreaterEqual(event['elapsed_s'], 0)
        self.assertIsNone(state['pending_change'])

    def test_ui_reset_clears_history_and_requires_new_screen(self):
        at = self.onboard()
        self.open(at, 'relaxation')
        button(at, 'I completed my breathing practice').click().run()
        at.radio(key='page').set_value('Overview').run()
        button(at, 'Start next week').click().run()
        self.assertEqual(len(at.session_state['zinc']['history']), 1)
        button(at, 'Load Maria').click().run()
        state = at.session_state['zinc']
        for key in ('plan', 'safety_result', 'next_plan', 'pending_change'):
            self.assertIsNone(state[key])
        for key in ('history', 'activity_sessions', 'events', 'messages', 'screening_answers'):
            self.assertFalse(state[key])
        self.assertEqual(state['onboarding_step'], 0)
        self.assertFalse(state['logs']['sessions'])
        self.assertFalse(at.exception)


if __name__ == '__main__':
    unittest.main()
