"""Regression checks for the five audit findings; no provider requests."""
from copy import deepcopy
from pathlib import Path
import json
import unittest
from unittest.mock import patch

import coach
import engine
import test_app
from ui_helpers import week_ics
from verification import verify_live


class AuditFixTests(unittest.TestCase):
    def accepted_state(self, direction='harder'):
        state = engine.new_state()
        state['safety_result'] = 'cleared'
        state['plan'] = engine.make_week(state['profile'], 'cleared', start_date='2026-10-19')
        strength = [a for a in state['plan']['activities'] if a['section'] == 'strength']
        engine.start_activity(state, strength[0]['id'])
        while not state['session_done']:
            item = state['plan']['exercises'][state['cursor']]
            engine.log_set(state, item['id'], item['reps'], 6, 0)
        for exercise_id, change in [('sit_to_stand', direction), ('hip_hinge', 'harder')]:
            state['pending_change'] = engine.progress(state['plan'], state['logs'], exercise_id, change)
            engine.accept_pending_change(state)
        return state, strength[1]

    def test_later_pain_revokes_conflicting_target_and_requires_approval(self):
        for direction in ('harder', 'same'):
            with self.subTest(direction=direction):
                state, second = self.accepted_state(direction)
                engine.start_activity(state, second['id'])
                engine.log_set(state, 'sit_to_stand', 10, 6, 4)
                self.assertEqual(state['pain_reviews'], ['sit_to_stand'])
                self.assertEqual(engine.prescription(state['plan'], 'sit_to_stand')['reps'], 10)
                self.assertEqual(engine.prescription(state['next_plan'], 'sit_to_stand')['reps'], 10)
                self.assertEqual(engine.prescription(state['next_plan'], 'hip_hinge')['reps'], 11)
                accepted = [e for e in state['events'] if e['event'] == 'accepted']
                self.assertTrue(accepted[0]['revoked'])
                self.assertFalse(accepted[1].get('revoked', False))
                for invalid in ('same', 'harder'):
                    with self.assertRaises(ValueError):
                        engine.progress(state['plan'], state['logs'], 'sit_to_stand', invalid)
                state['pending_change'] = engine.progress(state['plan'], state['logs'], 'sit_to_stand', 'easier')
                with self.assertRaises(ValueError):
                    engine.accept_pending_change(state)
                self.assertEqual(state['pain_reviews'], ['sit_to_stand'])
                engine.finish_activity(state, skipped=True)
                before = deepcopy(state)
                with self.assertRaisesRegex(ValueError, 'Approve an easier'):
                    engine.start_next_week(state)
                self.assertEqual(state, before)
                state['pending_change'] = engine.progress(state['plan'], state['logs'], 'sit_to_stand', 'easier')
                engine.decline_pending_change(state)
                with self.assertRaises(ValueError):
                    engine.start_next_week(state)
                state['pending_change'] = engine.progress(state['plan'], state['logs'], 'sit_to_stand', 'easier')
                engine.accept_pending_change(state)
                self.assertEqual(state['pain_reviews'], [])
                self.assertEqual(engine.prescription(state['plan'], 'sit_to_stand')['reps'], 10)
                engine.start_next_week(state)
                self.assertEqual(engine.prescription(state['plan'], 'sit_to_stand')['reps'], 9)
                self.assertEqual(engine.prescription(state['plan'], 'hip_hinge')['reps'], 11)
                self.assertEqual(engine.prescription(state['history'][0], 'sit_to_stand')['reps'], 10)

    def test_low_pain_and_already_easier_decisions_are_preserved(self):
        for direction, pain, expected in [('harder', 3, 11), ('easier', 4, 9)]:
            with self.subTest(direction=direction, pain=pain):
                state, second = self.accepted_state(direction)
                engine.start_activity(state, second['id'])
                engine.log_set(state, 'sit_to_stand', 10, 6, pain)
                self.assertFalse(state.get('pain_reviews'))
                engine.finish_activity(state, skipped=True)
                engine.start_next_week(state)
                self.assertEqual(engine.prescription(state['plan'], 'sit_to_stand')['reps'], expected)

    def test_calendar_ids_separate_fresh_weeks_but_survive_rescheduling(self):
        first = engine.make_week(engine.MARIA, 'cleared', start_date='2026-10-19')
        other = engine.make_week(engine.MARIA, 'cleared', start_date='2026-11-02')
        uids = lambda plan: {line for line in week_ics(plan).splitlines() if line.startswith('UID:')}
        self.assertFalse(uids(first) & uids(other))
        moved = engine.choose_days(first, {'strength': [1, 4], 'yoga': [0, 3], 'brain': [2, 6], 'relaxation': [4, 6]})
        self.assertEqual(uids(first), uids(moved))
        self.assertEqual(week_ics(first), week_ics(first))

    def test_finished_partial_activity_is_not_labelled_in_progress(self):
        helper = test_app.AppTests()
        at = helper.screened()
        helper.open_activity(at, 'strength')
        activity_id = at.session_state['zinc']['active_activity']
        test_app.button(at, 'Done set').click().run()
        at.radio(key='page').set_value('Your week').run()
        self.assertTrue(any('<span class="status-chip">In progress</span>' in m.value for m in at.markdown))
        at.button(key='start_' + activity_id).click().run()
        test_app.button(at, 'Skip / end this activity').click().run()
        at.radio(key='page').set_value('Your week').run()
        self.assertFalse(at.exception)
        self.assertTrue(any('<span class="status-chip">Ended early</span>' in m.value for m in at.markdown))
        self.assertFalse(any('<span class="status-chip">In progress</span>' in m.value for m in at.markdown))
        self.assertEqual(at.button(key='start_' + activity_id).label, 'Review')

    def test_provider_gate_reaches_real_accept_ui_with_fake_provider(self):
        secret_path = test_app.ROOT.parent / '.streamlit/secrets.toml'
        report_path = test_app.ROOT / 'verification/live-model.json'
        original_exists, original_read, original_write = Path.exists, Path.read_text, Path.write_text
        reports = []
        def exists(path):
            return True if path == secret_path else original_exists(path)
        def read(path, *args, **kwargs):
            if path == secret_path:
                return 'GEMINI_API_KEY="offline-fixture"\nMODEL="offline-fixture"'
            return original_read(path, *args, **kwargs)
        def write(path, value, *args, **kwargs):
            if path == report_path:
                reports.append(json.loads(value))
                return len(value)
            return original_write(path, value, *args, **kwargs)
        def provider(message, context, secrets):
            context.call('get_plan', {})
            context.call('get_last_session', {})
            context.call('propose_change', {'exercise_id': 'sit_to_stand', 'direction': 'harder'})
            return 'Keep going steadily.'
        with patch.object(Path, 'exists', exists), patch.object(Path, 'read_text', read), patch.object(Path, 'write_text', write), patch.object(coach, 'run_model', provider):
            report, code = verify_live.main()
        self.assertEqual(code, 0, report)
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['stage'], 'complete')
        self.assertEqual(report['prescriptions']['active_after_rollover'], 11)
        self.assertEqual(len(reports), 1)

    def test_revoked_goal_is_explained_and_hidden_from_active_adjustments(self):
        state, second = self.accepted_state()
        engine.start_activity(state, second['id'])
        engine.log_set(state, 'sit_to_stand', 10, 6, 4)
        engine.finish_activity(state, skipped=True)
        state['welcomed'] = True
        at = test_app.AppTests().screened()
        at.session_state['zinc'] = state
        at.radio(key='page').set_value('Progress').run()
        self.assertFalse(at.exception)
        self.assertTrue(any('Later pain cancelled' in warning.value for warning in at.warning))
        adjustments = next(frame.value for frame in at.dataframe if 'Next-week count' in frame.value.columns)
        self.assertEqual(list(adjustments['Exercise']), ['Hip hinge'])
        self.assertTrue(any(e.get('revoked') for e in at.session_state['zinc']['events']))
