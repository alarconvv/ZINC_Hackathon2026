import unittest
from ui_helpers import nice_date, nice_range


class PresentationTests(unittest.TestCase):
    def test_dates(self):
        self.assertEqual(nice_date('2026-10-19'), 'Mon, Oct 19')
        self.assertEqual(nice_range('2026-10-19', '2026-10-25'), 'Oct 19 – 25')
        self.assertEqual(nice_range('2026-10-26', '2026-11-01'), 'Oct 26 – Nov 1')
        self.assertEqual(nice_range('2026-12-28', '2027-01-03'), 'Dec 28, 2026 – Jan 3, 2027')


class CalendarTests(unittest.TestCase):
    def test_calendar_roundtrip_and_stable_ids(self):
        from ui_helpers import week_ics
        from test_engine import ready
        from datetime import date, timedelta
        plan = ready()['plan']
        content = week_ics(plan)
        self.assertEqual(content, week_ics(plan))
        self.assertNotIn('\n', content.replace('\r\n', ''))
        self.assertTrue(all(len(line.encode()) <= 75 for line in content.split('\r\n')))
        lines = content.replace('\r\n ', '').split('\r\n')
        events, current = [], None
        for line in lines:
            if line == 'BEGIN:VEVENT': current = {}
            elif line == 'END:VEVENT': events.append(current); current = None
            elif current is not None:
                key, value = line.split(':', 1)
                current[key] = value
        self.assertEqual(len(events), len(plan['activities']))
        self.assertEqual(len({e['UID'] for e in events}), len(events))
        for event, activity in zip(events, plan['activities']):
            self.assertEqual(event['DTSTART;VALUE=DATE'], activity['date'].replace('-', ''))
            day = date.fromisoformat(activity['date']) + timedelta(days=1)
            self.assertEqual(event['DTEND;VALUE=DATE'], day.strftime('%Y%m%d'))
            self.assertIn(str(activity['minutes']), event['DESCRIPTION'])
