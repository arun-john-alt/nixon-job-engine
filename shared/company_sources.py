"""Bounded, parallel employer discovery. Directory membership never proves hiring."""
import datetime as dt,json,re,urllib.parse as urls
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
try:from scripts import scan,employers,availability
except ModuleNotFoundError:import scan,employers,availability
ROOT=Path(__file__).resolve().parents[1]

def board_from_link(url,company):
    try:u=urls.urlsplit(url);port=u.port
    except (ValueError,TypeError):return None
    parts=u.path.strip('/').split('/')
    if u.scheme!='https' or u.username or u.password or port not in (None,443):return None
    kind={'jobs.lever.co':'lever','jobs.ashbyhq.com':'ashby','jobs.smartrecruiters.com':'smart','careers.smartrecruiters.com':'smart','boards.greenhouse.io':'greenhouse','job-boards.greenhouse.io':'greenhouse'}.get(u.hostname)
    if kind and re.fullmatch(r'[A-Za-z0-9_-]+',parts[0]):return dict(company=company,kind=kind,slug=parts[0])
    if re.fullmatch(r'[a-z0-9-]+\.wd\d+\.myworkdayjobs\.com',u.hostname or ''):
        if re.fullmatch(r'[a-z]{2}-[A-Z]{2}',parts[0]):parts=parts[1:]
        if parts and re.fullmatch(r'[A-Za-z0-9_-]+',parts[0]):return dict(company=company,kind='workday',host=u.hostname,slug=u.hostname.split('.')[0],site=parts[0],searchTerms=['Chennai','remote India'])
    return None

def choose(catalog,previous,limit,now):
    if not catalog:return [],0
    start=int(previous.get('nextIndex',0))%len(catalog);chosen=[];index=start
    # Unchecked companies precede rechecks so a large directory cannot starve.
    order=[(start+i)%len(catalog) for i in range(len(catalog))]
    order.sort(key=lambda i:catalog[i]['id'] in previous.get('companies',{}))
    for index in order:
        row=catalog[index];old=previous.get('companies',{}).get(row['id'],{})
        try:due=dt.datetime.fromisoformat(old['nextCheckAt'])<=now
        except (KeyError,TypeError,ValueError):due=True
        if due:chosen.append(row)
        if len(chosen)>=limit:break
    return chosen,(index+1)%len(catalog)

def inspect_company(company,cfg,now):
    url=company['careerUrl'];host=urls.urlsplit(url).hostname
    found=[];candidates=[];status='Not checked';text=None;page=None;is_kula=False
    aliases={host,host[4:] if host and host.startswith('www.') else 'www.'+str(host)}
    try:
        if not scan.valid_url(url,{host}):raise ValueError('Invalid catalog URL')
        fetcher=scan.Fetcher({**cfg,'allowedHosts':list(set(cfg['allowedHosts'])|aliases),'maxPageFetches':4})
        text,status=fetcher.page(url)
        if text:
            page=scan.Page();page.feed(text)
            # Follow only actual employer-owned career links; never guess /careers.
            if company.get('entryType')=='company-homepage':
                links=[urls.urljoin(url,h) for h in page.links if re.search(r'(?:careers?|join-us|work-with-us|jobs)(?:[/?#]|$)',h,re.I)]
                for target in links[:3]:
                    board=board_from_link(target,company['name'])
                    if board:found.append(board);continue
                    if not scan.valid_url(target,aliases):continue
                    body,code=fetcher.page(target)
                    if body:url,text,status=target,body,code;page=scan.Page();page.feed(body);break
            for link in [url]+[urls.urljoin(url,h) for h in page.links]:
                board=board_from_link(link,company['name'])
                if board and board not in found:found.append(board)
            is_kula=urls.urlsplit(url).hostname=='careers.kula.ai'
            links=list(dict.fromkeys(scan.canonical(urls.urljoin(url,h)) for h in page.links if (re.search(r'/(?:jobs?|careers|positions|openings)/',h,re.I) or is_kula and re.search(r'/[^/]+/\d+-',h)) and scan.ROLE.search(urls.unquote(h))))
            for target in [url]+[x for x in links if scan.valid_url(x,aliases)][:3]:
                body,code=(text,status) if target==url else fetcher.page(target)
                if not body:continue
                detail=scan.Page();detail.feed(body);nodes=list(scan.job_nodes(detail.jsonld))
                if len(nodes)!=1:continue
                item=scan.extract(nodes[0],target,company['name'],now.date().isoformat())
                if not item:continue
                state,reason=availability.decision(item,body,code,target,scan)
                if state!='open':continue
                stamp=min(now,getattr(fetcher,'oldest',None) or now).isoformat(timespec='seconds')
                item.update(availabilityStatus='open',availabilityReason=reason,lastConfirmedOpenAt=stamp,availabilityCheckedAt=stamp,availabilityHold=False,availabilityEvidenceUrl=target)
                candidates.append((item,scan.plain(nodes[0].get('description',''))))
    except Exception as exc:status='Company inspection error: '+type(exc).__name__;text=None
    state='blocked-or-unavailable' if not text else 'ats-linked' if found else 'structured-vacancy-checked' if candidates else 'no-openings-published' if re.search(r'no open (?:roles|positions)|no (?:current|open) vacancies',' '.join(page.text),re.I) else 'career-list-checked' if is_kula and page.links else 'needs-adapter'
    record=dict(company=company['name'],careerUrl=url,entryType=company.get('entryType','career-page'),checkedAt=now.isoformat(timespec='seconds'),status=state,fetchStatus=status,boards=found,atsKinds=sorted({b['kind'] for b in found}),nextCheckAt=(now+dt.timedelta(hours=6 if text else 12)).isoformat(timespec='seconds'))
    return company,record,candidates

def discover(data,cfg,catalog,limit=10,now=None,on_candidate=None):
    now=now or dt.datetime.now(dt.timezone.utc);previous=data.setdefault('run',{}).get('companyDiscovery',{})
    chosen,cursor=choose(catalog,previous,max(1,min(1000,limit)),now)
    catalog_ids={c['id'] for c in catalog};states={k:v for k,v in previous.get('companies',{}).items() if k in catalog_ids};boards=[];added=0
    known={(b['kind'],b['slug'].casefold()) for b in cfg.get('employerBoards',[])+cfg.get('reserveEmployerBoards',[])}
    existing={scan.canonical(j['applyUrl']) for j in data['jobs']}
    with ThreadPoolExecutor(max_workers=min(10,max(1,cfg.get('companyConcurrency',6)))) as pool:
        results=pool.map(lambda c:inspect_company(c,cfg,now),chosen)
        for company,record,candidates in results:
            states[company['id']]=record
            for board in record['boards']:
                key=(board['kind'],board['slug'].casefold())
                if key not in known:boards.append(board);known.add(key)
            for item,description in candidates:
                if on_candidate:on_candidate(item,description)
                key=scan.canonical(item['applyUrl'])
                if key in existing:continue
                if any(item['requisition'] and item['requisition']==j.get('requisition') and employers.norm(item['company'])==employers.norm(j['company']) for j in data['jobs']):continue
                data['jobs'].append(item);existing.add(key);added+=1
    report=dict(catalogSize=len(catalog),checkedThisRun=len(chosen),everChecked=len(states),nextIndex=cursor,newLeads=added,linkedBoards=len(boards),checkedAt=now.isoformat(timespec='seconds'),companies=states)
    report['connectedCompanies']=sum(s['status'] in ('ats-linked','structured-vacancy-checked','career-list-checked') for s in states.values());report['blockedCompanies']=sum(s['status']=='blocked-or-unavailable' for s in states.values());report['adapterGaps']=sum(s['status']=='needs-adapter' for s in states.values())
    data['run']['companyDiscovery']=report
    summary=dict(source='Chennai company catalog',status=f'{len(states)}/{len(catalog)} companies checked; {added} new leads this run',detail=f'{len(chosen)} company/career entries attempted with robots checks. {report["connectedCompanies"]} connected; {report["blockedCompanies"]} blocked/unavailable; {report["adapterGaps"]} need adapters. Unchecked directory entries are research targets, not verified hiring.')
    data['run']['coverage']=[summary]+[c for c in data['run'].get('coverage',[]) if c['source']!=summary['source']]
    return report
