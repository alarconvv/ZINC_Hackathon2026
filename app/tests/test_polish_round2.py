"""Round-two presentation checks; no safety or progression changes."""
import tempfile
import unittest
from pathlib import Path
import engine
import activities
from ui_helpers import movement_art


class ArtworkTests(unittest.TestCase):
    def test_every_exercise_and_pose_has_art_or_accessible_fallback(self):
        items = [(item.get('image') or item['id'], item['name']) for item in engine.catalog()]
        for supported in (False, True):
            items += [('yoga_' + pose['id'], pose['name']) for pose in activities.yoga_content(engine.MARIA, supported)]
        for basename, label in items:
            with self.subTest(basename=basename):
                art = movement_art(basename, label)
                self.assertTrue('<img ' in art or 'role="img"' in art)
                with tempfile.TemporaryDirectory() as folder:
                    fallback = movement_art(basename, label, image_dir=folder)
                    self.assertIn('role="img"', fallback)
                    self.assertIn(label, fallback)

    def test_raster_precedence_and_svg_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for suffix in ('.png', '.webp', '.svg'):
                (directory / ('pose' + suffix)).write_bytes(b'fixture')
            for suffix, mime in (('.png', 'image/png'), ('.webp', 'image/webp'), ('.svg', 'image/svg+xml')):
                self.assertIn('data:' + mime, movement_art('pose.svg', '<pose>', image_dir=folder))
                self.assertIn('&lt;pose&gt;', movement_art('pose.svg', '<pose>', image_dir=folder))
                (directory / ('pose' + suffix)).unlink()
            self.assertIn('role="img"', movement_art('pose', 'Pose', image_dir=folder))


class FirstRunTests(unittest.TestCase):
    def test_guide_dismissal_preserves_plan_and_does_not_repeat(self):
        from copy import deepcopy
        from test_app import AppTests, button
        at = AppTests().screened()
        self.assertTrue(any('How ZINC works' in m.value for m in at.markdown))
        before = deepcopy(at.session_state['zinc']['plan'])
        button(at, 'Got it').click().run()
        self.assertTrue(at.session_state['zinc']['tour_done'])
        self.assertEqual(before, at.session_state['zinc']['plan'])
        at.radio(key='page').set_value('Your week').run()
        at.radio(key='page').set_value('Overview').run()
        self.assertFalse(any('How ZINC works' in m.value for m in at.markdown))
        button(at, 'Start next week').click().run()
        self.assertFalse(any('How ZINC works' in m.value for m in at.markdown))
        self.assertFalse(at.exception)


    def test_demo_sidebar_and_header_controls_do_not_conflict(self):
        from streamlit.testing.v1 import AppTest
        from test_app import ROOT
        at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30)
        at.query_params['demo'] = '1'
        at.run()
        self.assertFalse(at.exception)
        self.assertEqual(sum(b.label == 'Load Maria' for b in at.button), 2)
        at.button(key='load_maria').click().run()
        self.assertFalse(at.exception)
        self.assertFalse(at.session_state['zinc'].get('fictional_confirmed', False))
