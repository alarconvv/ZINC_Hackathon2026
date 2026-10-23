import unittest
from copy import deepcopy
import activities,engine
from test_engine import ready
class WeeklyTests(unittest.TestCase):
 def activity(self,s,section):
  a=next(a for a in s['plan']['activities'] if a['section']==section)
  return engine.start_activity(s,a['id'])
 def test_schedule_focus(self):
  s=ready();base=deepcopy(s['plan']['activities'])
  self.assertEqual({a['section'] for a in base},{'strength','yoga','brain','relaxation'})
  s['profile']['toggles']={'yoga':True,'brain':True}
  plan=engine.make_week(s['profile'],'cleared')
  self.assertEqual(len(plan['activities']),len(base)+3)
  self.assertEqual(plan['days'],s['plan']['days'])
 def test_resume_and_duplicate_completion(self):
  s=ready();a=self.activity(s,'strength');engine.log_set(s,'sit_to_stand',10,6,0)
  b=self.activity(s,'yoga');engine.log_yoga(s,3,0)
  engine.start_activity(s,a['id'])
  self.assertEqual(s['set_index'],1)
  engine.start_activity(s,b['id']);self.assertEqual(b['pose_index'],1)
  engine.finish_activity(s,skipped=True);self.assertEqual(b['status'],'partial')
  with self.assertRaises(ValueError):engine.log_yoga(s,3,0)
 def test_reasoning_bank_rules(self):
  self.assertEqual(len(activities.PUZZLES),24)
  self.assertEqual(activities.next_level(1,[True]*3),2)
  self.assertEqual(activities.next_level(2,[False]*2),1)
  self.assertEqual(activities.next_level(4,[True]*3),4)
  s=ready();a=self.activity(s,'brain')
  for _ in range(3):engine.answer_puzzle(s,engine.current_puzzle(s)['answer'])
  self.assertEqual(s['brain_level'],2);self.assertEqual(s['brain_streak'],[])
  for _ in range(2):engine.answer_puzzle(s,-100)
  self.assertEqual(s['brain_level'],1);self.assertTrue(a['finished'])
  with self.assertRaises(ValueError):engine.answer_puzzle(s,0)
 def test_relaxation_and_stop(self):
  s=ready();a=self.activity(s,'relaxation');engine.finish_activity(s,minutes=5)
  self.assertEqual(a['completed_minutes'],5)
  with self.assertRaises(ValueError):engine.finish_activity(s,minutes=5)
  engine.stop(s)
  with self.assertRaises(ValueError):self.activity(s,'yoga')
 def test_staging_and_rollover(self):
  s=ready();a=self.activity(s,'strength')
  while not s['session_done']:
   i=s['plan']['exercises'][s['cursor']];engine.log_set(s,i['id'],i['reps'],6,0)
  s['pending_change']=engine.progress(s['plan'],s['logs'],'sit_to_stand','harder')
  engine.accept_pending_change(s)
  self.assertEqual(s['plan']['exercises'][0]['reps'],10)
  self.assertEqual(s['next_plan']['exercises'][0]['reps'],11)
  engine.start_next_week(s)
  self.assertEqual(s['plan']['week'],2);self.assertEqual(s['plan']['exercises'][0]['base_reps'],11)
  self.assertEqual(len(s['history']),1);self.assertEqual(len(s['logs']['sessions']),12)
  with self.assertRaises(ValueError):engine.progress(s['plan'],s['logs'],'sit_to_stand','harder')
 def test_yoga_pain_partial(self):
  s=ready();a=self.activity(s,'yoga');engine.log_yoga(s,4,5)
  self.assertEqual(a['status'],'partial');self.assertTrue(a['finished'])
  self.assertTrue(all('Seated' in p['version'] for p in s['plan']['yoga']))
