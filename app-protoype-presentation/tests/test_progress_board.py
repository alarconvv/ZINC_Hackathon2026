import unittest
from copy import deepcopy
import engine
import progress_board


class ProgressBoardTests(unittest.TestCase):
    def state(self):
        s = engine.new_state(engine.MARIA)
        s['safety_result'] = 'cleared'
        s['plan'] = engine.make_week(s['profile'], 'cleared', start_date='2026-10-19')
        return s

    def test_counts_partial_and_historical_week_without_mutation(self):
        s = self.state()
        first, second = s['plan']['activities'][:2]
        s['activity_sessions'][first['id']] = {**first, 'status': 'completed'}
        s['activity_sessions'][second['id']] = {**second, 'status': 'partial'}
        before = deepcopy(s)
        board = progress_board.summarize(s['plan'], s['activity_sessions'])
        self.assertEqual(board['done'], 1)
        self.assertEqual(board['partial'], 1)
        self.assertEqual(sum(board['daily']), 1)
        self.assertEqual(s, before)
        self.assertIn('Oct 19', progress_board.date_range(s['plan']))
        self.assertIn('Monday: 1', progress_board.activity_chart(board))

    def test_empty_week_has_no_invented_progress(self):
        s = self.state()
        board = progress_board.summarize(s['plan'], {})
        self.assertEqual(board['percent'], 0)
        self.assertEqual(board['daily'], [0]*7)
        self.assertEqual(progress_board.feedback_rows(s, s['plan']), [])

    def test_feedback_keeps_context_and_excludes_other_weeks(self):
        s = self.state()
        activity = next(a for a in s['plan']['activities'] if a['section'] == 'strength')
        s['logs']['sessions'] = [dict(week=1, activity_id=activity['id'], exercise_id='sit_to_stand', set=1, pain=2, effort=6),
                                 dict(week=2, activity_id='other', exercise_id='sit_to_stand', set=1, pain=8, effort=9)]
        rows = progress_board.feedback_rows(s, s['plan'])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['Date'], activity['date'])
        self.assertEqual(rows[0]['Movement'], 'Sit to stand')
