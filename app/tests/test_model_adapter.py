"""Exercise the real SDK response/tool shapes with a fake network client."""
import importlib.util
import unittest
from unittest.mock import patch
import coach
import engine

try:
    HAS_SDK = importlib.util.find_spec('google.genai') is not None
except ModuleNotFoundError:
    HAS_SDK = False


@unittest.skipUnless(HAS_SDK, 'Install google-genai to run adapter tests')
class AdapterTests(unittest.TestCase):
    def test_real_adapter_tool_loop(self):
        from google.genai import types
        from types import SimpleNamespace
        s = engine.new_state()
        s['safety_result'] = 'cleared'
        s['plan'] = engine.make_week(s['profile'], 'cleared')
        engine.log_set(s, 'sit_to_stand', 10, 6, 1)
        responses = [
            types.Content(role='model', parts=[
                types.Part(function_call=types.FunctionCall(name='get_plan', args={}, id='read-plan')),
                types.Part(function_call=types.FunctionCall(name='get_last_session', args={}, id='read-feedback'))]),
            types.Content(role='model', parts=[types.Part(function_call=types.FunctionCall(
                name='propose_change', id='proposal', args={'exercise_id': 'sit_to_stand', 'direction': 'harder'}))]),
            types.Content(role='model', parts=[types.Part.from_text(text='You are building a steady routine. Review your pending proposal below.')])]
        captured = []
        def generate(**kwargs):
            self.assertTrue(all(c.role in ('user', 'model') for c in kwargs['contents']))
            for content in kwargs['contents']:
                if any(p.function_response for p in content.parts or []):
                    self.assertEqual(content.role, 'user')
            captured.append(kwargs)
            return SimpleNamespace(candidates=[SimpleNamespace(content=responses.pop(0))])
        client = SimpleNamespace(models=SimpleNamespace(generate_content=generate))
        with patch('google.genai.Client') as factory:
            factory.return_value.__enter__.return_value = client
            reply = coach.coach_turn('Check in', s, {'GEMINI_API_KEY': 'fictional-test-key', 'MODEL': 'test-model'})
        self.assertNotEqual(reply, coach.FALLBACK)
        self.assertEqual(len(captured), 3)
        self.assertEqual(s['pending_change']['proposed'], 11)
        self.assertEqual(s['plan']['version'], 1)
        declarations = captured[0]['config'].tools[0].function_declarations
        self.assertEqual({d.name for d in declarations}, {'get_plan', 'get_last_session', 'propose_change'})
        self.assertTrue(captured[0]['config'].automatic_function_calling.disable)
        self.assertEqual([p.function_response.id for c in captured[-1]['contents'] for p in c.parts or [] if p.function_response], ['read-plan', 'read-feedback', 'proposal'])


if __name__ == '__main__':
    unittest.main()
