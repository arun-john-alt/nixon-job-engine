import unittest,datetime as dt
from scripts.career_ops import due,candidates
class CareerOpsTests(unittest.TestCase):
 def test_daily_ist_gate(self):
  self.assertFalse(due({},dt.datetime(2026,10,25,3,0,tzinfo=dt.timezone.utc)))
  self.assertTrue(due({},dt.datetime(2026,10,25,4,0,tzinfo=dt.timezone.utc)))
  self.assertFalse(due({'discovery':{'scanDateIst':'2026-10-25'}},dt.datetime(2026,10,25,4,0,tzinfo=dt.timezone.utc)))
 def test_queue_accepts_only_receipted_https_urls(self):
  r={'added_urls':['https://example.org/job','javascript:bad']}
  rows=candidates(r,'- [ ] https://example.org/job | Employer | QA Lead | Chennai\n- [ ] https://unrelated.org/job | Fake | Fake | Chennai\n- [ ] javascript:bad | Fake | Fake | Chennai')
  self.assertEqual(len(rows),1);self.assertEqual(rows[0]['title'],'QA Lead')
