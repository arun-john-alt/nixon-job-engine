import runpy,subprocess,unittest
from pathlib import Path
from unittest.mock import patch
SCRIPT=Path(__file__).resolve().parents[1]/'shared/publish_data.py'
class PublicationTests(unittest.TestCase):
 def simulate(self,conflict=False):
  commands=[];pushes=0
  def fake(args,check=True):
   nonlocal pushes
   commands.append(args);code=0
   if args[:3]==('git','diff','--quiet'):code=1
   if args[:2]==('git','push'):
    pushes+=1;code=1 if pushes==1 else 0
   if conflict and args[:3]==('git','rebase','origin/main'):code=1
   if check and code:raise subprocess.CalledProcessError(code,args)
   return subprocess.CompletedProcess(args,code)
  with patch('subprocess.run',fake):
   if conflict:
    with self.assertRaises(SystemExit):runpy.run_path(str(SCRIPT))
   else:runpy.run_path(str(SCRIPT))
  return commands
 def test_concurrent_code_rebased_revalidated_never_forced(self):
  calls=self.simulate();self.assertIn(('git','rebase','origin/main'),calls)
  self.assertTrue(any('scripts/build.py' in c for c in calls))
  self.assertFalse(any('--force' in c for c in calls))
  self.assertEqual(sum(c[:2]==('git','push') for c in calls),2)
 def test_conflicting_data_aborted_without_second_push(self):
  calls=self.simulate(True);self.assertIn(('git','rebase','--abort'),calls)
  self.assertEqual(sum(c[:2]==('git','push') for c in calls),1)
