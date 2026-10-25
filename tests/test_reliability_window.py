import datetime as dt,importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('reliability',Path(__file__).resolve().parents[1]/'shared/health.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ReliabilityTests(unittest.TestCase):
 def test_many_runs_on_one_day_do_not_fake_a_week(self):
  now=dt.datetime(2026,10,25,8,tzinfo=dt.timezone.utc)
  samples=[dict(checkedAt=(now-dt.timedelta(minutes=i)).isoformat(),shortfall=0) for i in range(20)]
  self.assertEqual(m.summarize(samples,now)['observationDays'],1)
 def test_ist_midnight_not_utc_midnight(self):
  now=dt.datetime(2026,10,25,1,tzinfo=dt.timezone.utc)
  samples=[dict(checkedAt=t,shortfall=0) for t in ['2026-10-24T20:00:00+00:00','2026-10-25T01:00:00+00:00']]
  self.assertEqual(m.summarize(samples,now)['observationDays'],1)
 def test_seven_days_ready_for_review_not_automatic_certification(self):
  now=dt.datetime(2026,10,25,8,tzinfo=dt.timezone.utc)
  samples=[dict(checkedAt=(now-dt.timedelta(days=i)).isoformat(),shortfall=0) for i in range(7)]
  self.assertEqual(m.summarize(samples,now)['status'],'ready-for-deployment-review')
 def test_shortfall_does_not_pass(self):
  now=dt.datetime(2026,10,25,8,tzinfo=dt.timezone.utc)
  samples=[dict(checkedAt=(now-dt.timedelta(days=i)).isoformat(),shortfall=1) for i in range(7)]
  self.assertEqual(m.summarize(samples,now)['status'],'needs-attention')
 def test_future_and_naive_timestamps_do_not_count(self):
  now=dt.datetime.now(dt.timezone.utc)
  self.assertEqual(m.summarize([{'checkedAt':(now+dt.timedelta(days=1)).isoformat()},{'checkedAt':'2026-10-25T10:00:00'}],now)['observationDays'],0)
