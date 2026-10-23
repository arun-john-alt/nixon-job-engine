import datetime as dt
import json
import unittest
from unittest.mock import patch
from scripts import company_sources as sources, scan
NOW=dt.datetime(2026,10,23,tzinfo=dt.timezone.utc)
CAT=[{'id':str(i),'name':'Company '+str(i),'careerUrl':'https://employer.example/careers/'+str(i)} for i in range(3)]
class CompanySourcesTests(unittest.TestCase):
    def test_rotates_and_backs_off_failed_sources(self):
        first,next_index=sources.choose(CAT,{},2,NOW)
        self.assertEqual([x['id'] for x in first],['0','1'])
        prior={'nextIndex':next_index,'companies':{'0':{'nextCheckAt':(NOW+dt.timedelta(hours=12)).isoformat()}}}
        second,_=sources.choose(CAT,prior,2,NOW)
        self.assertEqual([x['id'] for x in second],['2','1'])
        self.assertEqual(sources.choose([],{},2,NOW),([],0))
    def test_ats_identity_comes_from_public_employer_link(self):
        self.assertEqual(sources.board_from_link('https://jobs.ashbyhq.com/example/abc','Example')['slug'],'example')
        self.assertEqual(sources.board_from_link('https://careers.smartrecruiters.com/Example','Example')['kind'],'smart')
        board=sources.board_from_link('https://example.wd5.myworkdayjobs.com/en-US/External/job/Chennai/QA_R123','Example')
        self.assertEqual(board['site'],'External');self.assertEqual(board['host'],'example.wd5.myworkdayjobs.com')
        for u in ['http://jobs.lever.co/example','https://jobs.lever.co.evil.test/example','https://user:password@jobs.lever.co/example','https://jobs.lever.co:444/example','https://[bad','https://jobs.lever.co:broken/example']:
            self.assertIsNone(sources.board_from_link(u,'Example'),u)
    def test_blocked_pages_remain_unknown_and_do_not_change_jobs(self):
        class Blocked:
            def __init__(self,cfg):pass
            def page(self,url):return None,'Skipped: robots disallow'
        job={'id':'old','applyUrl':'https://employer.example/job/123','analysisStatus':'reviewed','score':[1]}
        data={'jobs':[dict(job)]}
        with patch.object(scan,'Fetcher',Blocked):sources.discover(data,{'allowedHosts':[]},CAT[:1],now=NOW)
        self.assertEqual(data['jobs'],[job]);self.assertEqual(data['run']['companyDiscovery']['companies']['0']['status'],'blocked-or-unavailable')
    def test_directory_metadata_never_proves_a_live_vacancy(self):
        class Directory:
            def __init__(self,cfg):pass
            def page(self,url):return '<h1>QA Lead Chennai Apply now</h1>','HTTP 200'
        data={'jobs':[]}
        with patch.object(scan,'Fetcher',Directory):sources.discover(data,{'allowedHosts':[]},CAT[:1],now=NOW)
        self.assertFalse(data['jobs']);self.assertEqual(data['run']['companyDiscovery']['companies']['0']['status'],'needs-adapter')
    def test_expanded_software_titles_keep_location_and_junior_gates(self):
        for title in ['Software Development Engineer in Test','QE Lead','Network Validation Engineer']:
            self.assertTrue(scan.is_relevant(title,'Chennai','8-10 years'),title)
            self.assertFalse(scan.is_relevant(title,'Bengaluru','8-10 years'),title)
        self.assertFalse(scan.is_relevant('Junior Software Development Engineer in Test','Chennai','1-2 years'))
