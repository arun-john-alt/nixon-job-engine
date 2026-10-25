import datetime as dt,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
 s=importlib.util.spec_from_file_location(name,ROOT/'shared'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class AssessmentTests(unittest.TestCase):
 def setUp(self):
  self.m=module('pipeline','pipeline.py');self.p=json.loads((ROOT/'config/evidence-profile.json').read_text())
 def item(self,text):return dict(title='Senior QA Engineer',description=text+' '+('Responsibilities and requirements for this position. '*35))
 def test_short_description_not_scored(self):self.assertIsNone(self.m.assess(dict(title='QA',description='Python testing'),self.p))
 def test_explicitly_not_required_skill_not_a_gap(self):
  self.assertNotIn('java',self.m.hits('Java is not required; Python required',['java','python']))
 def test_title_alone_not_enough(self):self.assertIsNone(self.m.assess(self.item('Marketing and sales'),self.p))
 def test_unconfirmed_skills_reduce_score(self):
  a=self.m.assess(self.item('Test automation Python Selenium Jenkins networking'),self.p)
  b=self.m.assess(self.item('Test automation Python Selenium Jenkins networking Java Playwright Terraform'),self.p)
  self.assertLess(b['total'],a['total']);self.assertIn('java',b['hardGaps'][0].lower())
 def test_experience_gap_visible(self):
  a=self.m.assess(self.item('Test automation with 15 years experience Python'),self.p);self.assertTrue(any('15' in s for s in a['hardGaps']))
 def test_workday_does_not_use_get_cache(self):
  class Engine:
   def api_url(*args):raise AssertionError('Workday must use its live connector')
  self.assertEqual(self.m.cache_urls({'kind':'workday'},{},Engine()),[])
 def test_weights_and_bounds(self):
  a=self.m.assess(self.item('Test automation Python Robot Framework Selenium Jenkins Git REST API networking'),self.p)
  self.assertEqual(sum(s['weight'] for s in a['score']),100)
  self.assertTrue(all(0<=s['points']<=s['weight'] for s in a['score']))
 def test_reliability_not_claimed_after_one_run(self):
  m=module('health','health.py');d={'run':{}};self.assertEqual(m.record(d)['status'],'observing');self.assertEqual(d['run']['reliability']['observationDays'],1)
 def test_one_broken_connector_does_not_abort(self):
  import sys;sys.path.insert(0,str(ROOT/'scripts'));m=module('employers','employers.py');m.collect_board=lambda *a: (_ for _ in ()).throw(ValueError('failure'))
  b={'company':'Example'};self.assertEqual(m.safe_collect(b,{},None)[3],'Connector error: ValueError')
