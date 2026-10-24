from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest
import engine
ROOT=Path(__file__).resolve().parents[1]
def button(at,label):return next(b for b in at.button if b.label==label)
def checkbox(at,label):return next(c for c in at.checkbox if c.label==label)
class AppTests(unittest.TestCase):
 def fresh(self):
  at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
  button(at,'Try the demo with Maria').click().run()
  checkbox(at,'I am using fictional information for this prototype.').check()
  button(at,'Continue to safety').click().run()
  self.assertFalse(at.exception)
  return at
 def screened(self,chest=False):
  at=self.fresh()
  for r in at.radio:r.set_value('Yes' if chest and r.label==engine.QUESTIONS['chest'] else 'No')
  button(at,'Continue to focus').click().run()
  if not chest:button(at,'Create my complete week').click().run()
  self.assertFalse(at.exception)
  return at
 def open_activity(self,at,section):
  at.radio(key='page').set_value('Your week').run()
  a=next(a for a in at.session_state['zinc']['plan']['activities'] if a['section']==section)
  at.button(key='start_'+a['id']).click().run()
  self.assertFalse(at.exception)
 def test_complete_journey_and_history(self):
  at=self.screened()
  self.assertEqual({a['section'] for a in at.session_state['zinc']['plan']['activities']},{'strength','yoga','brain','relaxation'})
  self.open_activity(at,'strength')
  while not at.session_state['zinc']['session_done']:button(at,'Done set').click().run()
  self.assertEqual(len(at.session_state['zinc']['logs']['sessions']),12)
  at.radio(key='page').set_value('Coach').run()
  at.selectbox[1].set_value('harder');button(at,'Preview adjustment').click().run()
  button(at,'Accept for next week').click().run()
  s=at.session_state['zinc']
  self.assertEqual(s['plan']['exercises'][0]['reps'],10)
  self.assertEqual(s['next_plan']['exercises'][0]['reps'],11)
  self.open_activity(at,'yoga')
  for _ in range(5):button(at,'Done pose').click().run()
  self.open_activity(at,'brain')
  for _ in range(5):
   puzzle=engine.current_puzzle(at.session_state['zinc'])
   at.number_input[0].set_value(puzzle['answer']);button(at,'Check answer').click().run()
  self.open_activity(at,'relaxation')
  button(at,'I completed my breathing practice').click().run()
  at.radio(key='page').set_value('Progress').run()
  self.assertFalse(at.exception)
  at.radio(key='page').set_value('Overview').run()
  button(at,'Start next week').click().run()
  self.assertEqual(at.session_state['zinc']['plan']['week'],2)
  self.assertEqual(len(at.session_state['zinc']['history']),1)
  at.radio(key='page').set_value('Progress').run();at.selectbox[0].set_value(1).run()
  self.assertFalse(at.exception)
 def test_back_preserves_answers(self):
  at=self.fresh()
  for r in at.radio:r.set_value('No')
  button(at,'Back to profile').click().run()
  self.assertEqual(at.text_input[0].value,'Maria')
  button(at,'Continue to safety').click().run()
  self.assertTrue(all(r.value=='No' for r in at.radio))
 def test_screen_blocks(self):
  at=self.screened(True)
  self.assertIsNone(at.session_state['zinc']['plan']);self.assertTrue(at.error)
 def test_stop_blocks_all(self):
  at=self.screened();button(at,'■ Stop').click().run()
  self.assertTrue(at.session_state['zinc']['stopped']);self.assertFalse(at.exception)
 def test_historical_reasoning_level_stays_in_selected_week(self):
  at=self.screened()
  state=at.session_state['zinc']
  for week in (1,2):
   activity=next(a for a in state['plan']['activities'] if a['section']=='brain')
   engine.start_activity(state,activity['id'])
   for _ in range(5):engine.answer_puzzle(state,engine.current_puzzle(state)['answer'])
   if week==1:engine.start_next_week(state)
  self.assertEqual(state['brain_level'],4)
  at.radio(key='page').set_value('Progress').run()
  at.selectbox[0].set_value(1).run()
  self.assertTrue(any('Last recorded reasoning level: 2 / 4' in m.value for m in at.markdown))
  self.assertFalse(at.exception)
 def test_brain_feedback_belongs_to_its_activity(self):
  at=self.screened()
  state=at.session_state['zinc']
  brain=[a for a in state['plan']['activities'] if a['section']=='brain']
  self.open_activity(at,'brain')
  puzzle=engine.current_puzzle(state)
  at.number_input[0].set_value(puzzle['answer']);button(at,'Check answer').click().run()
  self.assertTrue(any('Correct.' in info.value for info in at.info))
  engine.start_activity(state,brain[1]['id']);at.run()
  self.assertFalse(any('Correct.' in info.value for info in at.info))
  engine.start_activity(state,brain[0]['id']);at.run()
  self.assertTrue(any('Correct.' in info.value for info in at.info))
  self.assertFalse(at.exception)
 def test_missing_key(self):
  at=self.screened();at.radio(key='page').set_value('Coach').run()
  at.pills[0].set_value('Weekly check-in').run()
  self.assertIn('fallback',at.session_state['zinc']['messages'][-1]['text'])
  self.assertFalse(at.exception)
if __name__=='__main__':unittest.main()
