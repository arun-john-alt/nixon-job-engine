import datetime as dt,importlib.util,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('shared_directory',ROOT/'shared/company_sources.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class DirectoryTests(unittest.TestCase):
 def test_large_directory_is_unique_and_public(self):
  rows=json.loads((ROOT/'shared/company-catalog.json').read_text())['companies']
  self.assertGreaterEqual(len(rows),600);self.assertEqual(len(rows),len({r['id'] for r in rows}))
  for r in rows:self.assertTrue(m.scan.valid_url(r['careerUrl'],{m.urls.urlsplit(r['careerUrl']).hostname}))
 def test_unchecked_companies_precede_rechecks(self):
  now=dt.datetime.now(dt.timezone.utc);rows=[{'id':'old'},{'id':'new'}]
  chosen,_=m.choose(rows,{'companies':{'old':{}}},1,now);self.assertEqual(chosen,[{'id':'new'}])
 def test_homepage_uses_actual_career_link_and_learns_board(self):
  calls=[]
  class Fetcher:
   def __init__(self,cfg):pass
   def page(self,url):
    calls.append(url)
    if url=='https://example.org/':return '<a href="/join-us">Careers</a>','HTTP 200'
    if url=='https://example.org/join-us':return '<a href="https://jobs.lever.co/example">Jobs</a>','HTTP 200'
    raise AssertionError('Guessed or untrusted URL')
  with patch.object(m.scan,'Fetcher',Fetcher):
   _,record,_=m.inspect_company({'id':'x','name':'Example','careerUrl':'https://example.org/','entryType':'company-homepage'},{'allowedHosts':[]},dt.datetime.now(dt.timezone.utc))
  self.assertEqual(record['status'],'ats-linked');self.assertEqual(record['boards'][0]['slug'],'example');self.assertNotIn('https://example.org/careers',calls)
 def test_broken_company_isolated(self):
  with patch.object(m.scan,'Fetcher',side_effect=ValueError('bad page')):
   _,record,items=m.inspect_company({'name':'Example','careerUrl':'https://example.org/'},{'allowedHosts':[]},dt.datetime.now(dt.timezone.utc))
  self.assertEqual(record['status'],'blocked-or-unavailable');self.assertEqual(items,[])
 def test_retired_feed_has_primary_evidence_and_career_watch(self):
  retired=json.loads((ROOT/'shared/retired-sources.json').read_text())['sources'][0]
  self.assertIn('jobBoard=null',retired['reason']);self.assertTrue(all(u.startswith('https://') for u in retired['evidenceUrls']))
