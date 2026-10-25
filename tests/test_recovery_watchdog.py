import datetime as dt,importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('watchdog',Path(__file__).resolve().parents[1]/'shared/watchdog.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class WatchdogTests(unittest.TestCase):
 def setUp(self):
  self.now=dt.datetime(2026,10,25,6,tzinfo=dt.timezone.utc);self.data={'run':{'scanDateIst':'2026-10-25','openingPool':{'lastReplenishedAt':'2026-10-25T05:55:00+00:00'}}};self.inv=lambda *a:{'bufferShortfall':1,'reviewedOpen':24}
 def decide(self,runs=None,live=None):return m.decide(self.data,self.data if live is None else live,runs or [],{},self.now,self.inv)[0]
 def test_stale_research_recovers_even_after_successful_publish(self):
  self.data['run']['openingPool']['lastReplenishedAt']='2026-10-25T03:00:00+00:00';self.assertEqual(self.decide([{'status':'completed','conclusion':'success'}]),'scan')
 def test_user_dispatches_do_not_exhaust_recovery_budget(self):
  runs=[{'display_title':'Engine','created_at':'2026-10-25T05:00:00+00:00'}]*20;self.assertEqual(self.decide(runs),'healthy')
 def test_recovery_limit_and_cooldown(self):
  runs=[{'display_title':'Recovery · engine','created_at':'2026-10-25T05:00:00+00:00'}]*3;self.assertEqual(self.decide(runs),'alert')
  runs=[{'display_title':'Recovery · engine','created_at':'2026-10-25T05:50:00+00:00'}];self.assertEqual(self.decide(runs),'wait')
 def test_live_mismatch_only_publishes(self):self.assertEqual(self.decide(live={'run':{}}),'publish')
 def test_active_run_prevents_dispatch(self):self.assertEqual(self.decide([{'status':'in_progress'}]),'wait')
