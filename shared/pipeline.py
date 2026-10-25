"""Shared cloud discovery, evidence assessment and run accounting. No private input."""
import argparse, datetime as dt, hashlib, importlib.util, json, os, re, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
VERSION='1.0.0'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def hits(text,terms):
    result=[]
    for term in terms:
        pattern=r'(?<!\w)'+re.escape(term)+r'(?!\w)'
        if not re.search(pattern,text,re.I):continue
        if re.search(r'no\s+'+pattern+r'\s+(?:experience\s+)?required|'+pattern+r'\s+(?:is\s+)?not required',text,re.I):continue
        result.append(term)
    return result

def assess(item,profile):
    """Score only full descriptions; never infer candidate skills from job wording."""
    desc=item['description'];title=item['title'];text=desc.lower()
    if len(desc.split())<100:return None
    responsibilities=hits(text,profile['responsibilities']);tools=hits(text,profile['tools']);domains=hits(text,profile['domains']);gaps=hits(text,profile['unconfirmed'])
    if not responsibilities:return None
    # Reject explicit minimum experience far above the confirmed dated profile.
    years=[int(m) for m in re.findall(r'(\d{1,2})\s*(?:\+|to\s*\d+|[-–]\s*\d+)?\s*years?\s*(?:of\s+)?(?:relevant\s+|professional\s+)?experience',text)]
    minimum=max(years,default=0);over=max(0,minimum-profile['years'])
    if over>2:gaps.append(f'Advertised experience {minimum} years exceeds confirmed {profile["years"]} years')
    manager=bool(re.search(r'\bmanager|head of|people lead',title,re.I))
    if manager and not profile['peopleManager']:gaps.append('People-management scope requires confirmation')
    categories=[('Responsibilities',35,min(30,12+len(responsibilities)*3),'; '.join(responsibilities)),
      ('Tools and analysis',20,min(18,4+len(tools)*3),'; '.join(tools) or 'No confirmed tool overlap found'),
      ('Experience and seniority',20,max(3,16-int(over*3)-(5 if manager and not profile['peopleManager'] else 0)),f'Confirmed dated experience: {profile["years"]} years; advertised minimum extracted: {minimum or "not stated"}. Role scope needs confirmation.'),
      ('Industry',15,min(13,5+len(domains)*3),'; '.join(domains) or 'Employer domain overlap not established'),
      ('Location',10,10,'Employer lists Chennai region or explicitly eligible fully remote India')]
    # Missing specialist skills reduce fit rather than being silently treated as supported.
    penalty=min(12,len(gaps)*2);categories[1]=(categories[1][0],20,max(0,categories[1][2]-penalty),categories[1][3])
    score=[dict(name=n,weight=w,points=p,reason=r) for n,w,p,r in categories]
    return dict(score=score,hardGaps=[x+' — not confirmed in candidate evidence' if 'years' not in x and 'scope' not in x else x for x in gaps],supported=responsibilities+tools+domains,total=sum(x['points'] for x in score))

def install_cache(scan,path):
    original=scan.Fetcher;path.mkdir(parents=True,exist_ok=True)
    class Cached(original):
        def __init__(self,cfg):super().__init__(cfg);self.oldest=None
        def request(self,url,headers=None,payload=None):
            # Cache only approved public GETs without credentials; robots rules are still evaluated by each profile.
            allowed=payload is None and not any(k.lower() in ('authorization','cookie','x-subscription-token','x-api-key') for k in (headers or {})) and scan.valid_url(url,self.hosts,True)
            key=path/(hashlib.sha256(url.encode()).hexdigest()+'.json');now=dt.datetime.now(dt.timezone.utc)
            if allowed and key.exists():
                try:
                    cached=json.loads(key.read_text());stamp=dt.datetime.fromisoformat(cached['checkedAt'])
                    if 0<=(now-stamp).total_seconds()<2700:
                        self.oldest=min(self.oldest or stamp,stamp);return cached['body'],cached['status']
                except (ValueError,KeyError):pass
            body,status=super().request(url,headers,payload)
            if allowed and body and status=='HTTP 200':
                key.write_text(json.dumps(dict(checkedAt=now.isoformat(),body=body,status=status)))
                self.oldest=min(self.oldest or now,now)
            return body,status
    scan.Fetcher=Cached
    return original

def cache_urls(board,item,engine):
    return [] if board['kind']=='workday' else [engine.api_url(board['kind'],board['slug']),item.get('api','')]

def approve_board_hosts(cfg,boards):
    approved={b['host'] for b in boards if b.get('kind')=='workday' and re.fullmatch(r'[a-z0-9-]+\.wd\d+\.myworkdayjobs\.com',b.get('host',''))}
    cfg['allowedHosts']=list(set(cfg['allowedHosts'])|approved)

def run(root,cache,directory_limit=None):
    sys.path.insert(0,str(root/'scripts'));import scan
    engine=load('shared_employers',HERE/'employers.py')
    profile=json.loads((root/'config/evidence-profile.json').read_text());cfg=json.loads((root/'config/search.json').read_text())
    cfg['employerBoards']=json.loads((HERE/'registry.json').read_text())['boards'];cfg['employerConcurrency']=4
    retired=json.loads((HERE/'retired-sources.json').read_text())['sources']
    retired_keys={(r['board']['kind'],r['board']['slug'].casefold()) for r in retired}
    def retired_board(board):return (board['kind'],board['slug'].casefold()) in retired_keys
    approve_board_hosts(cfg,cfg['employerBoards'])
    path=root/'site/data/jobs.json';data=json.loads(path.read_text());original=install_cache(scan,cache)
    previous_watch=data.get('run',{}).get('retiredSourceWatch',{})
    today=dt.datetime.now(dt.timezone.utc).date().isoformat();watch={}
    for row in retired:
        board=row['board'];key=board['kind']+':'+board['slug'];old=previous_watch.get(key,{})
        current=old if old.get('checkedOn')==today else None
        if current is None:
            fetcher=scan.Fetcher({**cfg,'allowedHosts':list(set(cfg['allowedHosts'])|engine.API_HOSTS|engine.JOB_HOSTS)})
            blob,status=engine.get_json(fetcher,engine.api_url(board['kind'],board['slug']))
            current={'checkedOn':today,'status':status,'recovered':isinstance(blob,dict) and isinstance(blob.get('jobs'),list)}
        watch[key]=current
        if current['recovered']:
            cfg['employerBoards'].append(board);retired_keys.discard((board['kind'],board['slug'].casefold()))
    data.setdefault('run',{})['retiredSourceWatch']=watch
    retired=[r for r in retired if (r['board']['kind'],r['board']['slug'].casefold()) in retired_keys]
    sources=load('shared_company_sources',HERE/'company_sources.py')
    from opening_pool import inventory
    current=inventory(data,cfg)['reviewedOpen'];direct=[]
    sources.employers=engine
    try:sources.discover(data,cfg,json.loads((HERE/'company-catalog.json').read_text())['companies'],limit=directory_limit or (60 if current<20 else 40 if current<35 else 20),on_candidate=lambda job,description:direct.append((job,description)))
    except Exception as exc:
        data.setdefault('run',{}).setdefault('companyDiscovery',{}).setdefault('companies',{})
        data['run'].setdefault('coverage',[]).append({'source':'Career directory discovery','status':'Incomplete','detail':'Directory error: '+type(exc).__name__+'; registered employer feeds continue.'})
    known={(b['kind'],b['slug'],b.get('site','')) for b in cfg['employerBoards']}
    # Learn supported employer boards from actual discovered vacancy routes.
    for job in data['jobs']:
        if job.get('company') in ('Employer to verify','Employer unverified'):continue
        board=sources.board_from_link(job.get('applyUrl',''),job['company'])
        if board:
            key=(board['kind'],board['slug'],board.get('site',''))
            if key not in known and not retired_board(board):cfg['employerBoards'].append(board);known.add(key)

    for state in data['run']['companyDiscovery']['companies'].values():
        fixed_boards=[]
        for board in state.get('boards',[]):
            if board['kind']=='workday' and re.fullmatch(r'[a-z]{2}-[a-z]{2}',board.get('site',''),re.I):
                board=sources.board_from_link(state.get('careerUrl',''),board['company'])
                if not board or re.fullmatch(r'[a-z]{2}-[a-z]{2}',board.get('site',''),re.I):continue
            fixed_boards.append(board)
            key=(board['kind'],board['slug'],board.get('site',''))
            if key not in known and not retired_board(board):cfg['employerBoards'].append(board);known.add(key)

        state['boards']=fixed_boards
    def item_key(url):return engine.exact_key(url) or ('url',scan.canonical(url))
    approve_board_hosts(cfg,cfg['employerBoards'])
    base_collect=engine.collect_board;assessed={};source_states=[]
    for job,description in direct:
        item={'url':job['applyUrl'],'title':job['title'],'description':description}
        assessed[item_key(item['url'])]=(item,assess(item,profile))
    def collect(board,cfg,scan):
        # Track the actual evidence timestamp, including a reused cloud cache.
        result=base_collect(board,cfg,scan)
        for item in result[2]:
            stamps=[]
            for url in cache_urls(board,item,engine):
                key=cache/(hashlib.sha256(url.encode()).hexdigest()+'.json')
                if key.exists():
                    try:stamps.append(json.loads(key.read_text())['checkedAt'])
                    except (ValueError,KeyError):pass
            if stamps:item['confirmedAt']=min(stamps)
            assessed[item_key(item['url'])]=(item,assess(item,profile))
        return result
    engine.collect_board=collect
    safe=engine.safe_collect
    def tracked_safe(board,cfg,scan):
        result=safe(board,cfg,scan)
        source_states.append(dict(company=board['company'],kind=board['kind'],slug=board['slug'],site=board.get('site',''),status=result[3],postings=len(result[1]),relevant=len(result[2])))
        return result
    engine.safe_collect=tracked_safe
    report=engine.discover(data,cfg,scan)
    checked={(r['kind'],r['slug'],r.get('site','')):r for r in source_states}
    company_report=data['run']['companyDiscovery']
    for state in company_report['companies'].values():
        boards=state.get('boards',[])
        if not boards:continue
        state['validatedBoards']=[b for b in boards if checked.get((b['kind'],b['slug'],b.get('site','')),{}).get('status') in ('Complete','Search complete')]
        if state['validatedBoards']:state['status']='ats-linked'
        else:state['status']='feed-unavailable'
    company_report['connectedCompanies']=sum(r['status'] in ('ats-linked','structured-vacancy-checked','career-list-checked') for r in company_report['companies'].values())
    new=0
    for job in data['jobs']:
        pair=assessed.get(item_key(job['applyUrl']))
        if not pair or re.search(r'\.(?:com|io|net)$',job.get('company','')):continue
        item,result=pair
        if not result:continue
        # Preserve reviewed human/agent assessments while description hashes match.
        if job.get('analysisStatus')=='reviewed' and not job.get('assessmentMethod','').startswith('rules'):continue
        job.update(analysisStatus='needs-review' if result['total']<55 else 'reviewed',score=result['score'],hardGaps=result['hardGaps'],assessmentMethod='rules-v1-full-description',assessmentTier='weak' if result['total']<55 else 'strong' if result['total']>=80 and not result['hardGaps'] else 'consider',reviewNote='Automated evidence assessment from the full employer description and confirmed profile facts. Keyword overlap is a conservative heuristic; mandatory requirements and role scope need candidate confirmation. Salary is assessed separately.',ats={'supported':result['supported'],'confirm':result['hardGaps'],'unsupported':[]})
        job['summary']=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[public contact omitted]', item['description'][:1100]);job['resumeEdits']=[];new+=1
    stamp=dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    failures=[s for s in source_states if s['status'] not in ('Complete','Search complete')]
    health=dict(version=VERSION,checkedAt=stamp,status='partial' if failures else 'success',boards=len(source_states),workingSources=len(source_states)-len(failures),sourceFailures=len(failures),assessed=new,sources=sorted(source_states,key=lambda s:s['company']))
    health['retiredSources']=retired
    data.setdefault('run',{})['sharedPipeline']=health
    data['run']['coverage']=[{'source':'Retired employer feeds','status':f'{len(retired)} retired feeds; checked daily for recovery','detail':'Made Card posting API and public embed no longer publish a board. Its official careers page remains in the company directory. This is not evidence that individual vacancies were filled.'}]+[c for c in data['run'].get('coverage',[]) if c['source']!='Retired employer feeds']
    data['run']['coverage']=[{'source':'Shared discovery and assessment','status':f'{len(source_states)} sources; {new} full-description assessments','detail':f'{len(failures)} sources incomplete or unavailable. Both sites use the same source registry and connector code. Assessment runs in GitHub without a Mac or model API key; human Career Ops review is supplemental.'}]+[c for c in data['run'].get('coverage',[]) if c['source']!='Shared discovery and assessment']
    data['updatedAt']=stamp[:10]
    path.write_text(json.dumps(data,ensure_ascii=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in health.items() if k!='sources'}))
    scan.Fetcher=original
    return health

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--directory-limit',type=int);p.add_argument('--cache',type=Path,default=Path('/tmp/job-engine-public-cache'));a=p.parse_args();run(a.root.resolve(),a.cache,a.directory_limit)
