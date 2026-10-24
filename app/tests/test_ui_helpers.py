import unittest
from ui_helpers import nice_date, nice_range


class PresentationTests(unittest.TestCase):
    def test_dates(self):
        self.assertEqual(nice_date('2026-10-19'), 'Mon, Oct 19')
        self.assertEqual(nice_range('2026-10-19', '2026-10-25'), 'Oct 19 – 25')
        self.assertEqual(nice_range('2026-10-26', '2026-11-01'), 'Oct 26 – Nov 1')
        self.assertEqual(nice_range('2026-12-28', '2027-01-03'), 'Dec 28, 2026 – Jan 3, 2027')
