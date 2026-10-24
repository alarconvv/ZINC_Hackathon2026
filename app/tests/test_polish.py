"""Presentation behavior with the same engine and safety controls."""
from copy import deepcopy
from streamlit.testing.v1 import AppTest
import test_app
from test_app import ROOT, button


import unittest


class PresentationFlowTests(unittest.TestCase):
    def test_welcome_get_started(self):
        at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30).run()
        self.assertFalse(at.session_state['zinc'].get('welcomed', False))
        button(at, 'Get started').click().run()
        self.assertTrue(at.session_state['zinc']['welcomed'])
        self.assertIsNone(at.session_state['zinc']['plan'])
        self.assertFalse(at.exception)

    def test_preferences_preserve_plan_and_about_loads_sources(self):
        at = test_app.AppTests().screened()
        original = deepcopy(at.session_state['zinc']['plan'])
        at.segmented_control(key='text_size').set_value('Large').run()
        at.toggle(key='high_contrast').set_value(True).run()
        self.assertEqual(at.session_state['zinc']['plan'], original)
        at.button(key='footer_about').click().run()
        self.assertFalse(at.exception)
        self.assertTrue(any('Evidence' in frame.value.columns for frame in at.dataframe))

    def test_stop_exists_on_every_page(self):
        at = test_app.AppTests().screened()
        for page in ['Overview', 'Your week', 'Train', 'Coach', 'Progress']:
            at.radio(key='page').set_value(page).run()
            self.assertFalse(at.exception)
            self.assertEqual(sum(b.label == '■ Stop' for b in at.button), 1)

    def test_typing_effect_cannot_render_model_images_or_html(self):
        from ui_helpers import inert_chunks
        payload = '![image](https://attacker.invalid/collect) <img src="https://attacker.invalid/">'
        shown = ''.join(inert_chunks(payload))
        self.assertNotIn('![image](', shown)
        self.assertNotIn('<img', shown)
        self.assertIn(r'\!\[image\]\(', shown)
        self.assertIn('&lt;img', shown)

    def test_rest_timer_and_summary_use_strength_logs(self):
        helper = test_app.AppTests()
        at = helper.screened()
        helper.open_activity(at, 'strength')
        button(at, 'Done set').click().run()
        self.assertFalse(at.exception)
        self.assertTrue(at.get('iframe'))
        button(at, 'Skip / end this activity').click().run()
        self.assertFalse(at.exception)
        self.assertTrue(any('1 set recorded' in m.value for m in at.markdown))
