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
