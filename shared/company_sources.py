"""Bounded company-first discovery; catalog membership never proves a vacancy."""
import datetime as dt
import json
import re
import urllib.parse as urls
from pathlib import Path
try:
    from scripts import scan, employers, availability
except ModuleNotFoundError:
    import scan, employers, availability
ROOT=Path(__file__).resolve().parents[1]

def board_from_link(url,company):
    try:
        u=urls.urlsplit(url);port=u.port
    except (ValueError,TypeError):return None
    parts=u.path.strip('/').split('/')
    if u.scheme!='https' or u.username or u.password or port not in (None,443):return None
    kind={'jobs.lever.co':'lever','jobs.ashbyhq.com':'ashby','jobs.smartrecruiters.com':'smart','careers.smartrecruiters.com':'smart','boards.greenhouse.io':'greenhouse','job-boards.greenhouse.io':'greenhouse'}.get(u.hostname)
    if kind and re.fullmatch(r'[A-Za-z0-9_-]+',parts[0]):return {'company':company,'kind':kind,'slug':parts[0]}
    if re.fullmatch(r'[a-z0-9-]+\.wd\d+\.myworkdayjobs\.com',u.hostname or ''):
        if re.fullmatch(r'[a-z]{2}-[A-Z]{2}',parts[0]):parts=parts[1:]
        if parts and re.fullmatch(r'[A-Za-z0-9_-]+',parts[0]):return {'company':company,'kind':'workday','host':u.hostname,'slug':u.hostname.split('.')[0],'site':parts[0],'searchTerms':['Chennai','remote India']}
    return None

def choose(catalog,previous,limit,now):
    if not catalog:return [],0
    start=int(previous.get('nextIndex',0))%len(catalog);chosen=[];index=start
    for step in range(len(catalog)):
        index=(start+step)%len(catalog);row=catalog[index]
        old=previous.get('companies',{}).get(row['id'],{})
        try:due=dt.datetime.fromisoformat(old['nextCheckAt'])<=now
        except (KeyError,TypeError,ValueError):due=True
        if due:chosen.append(row)
        if len(chosen)>=limit:break
    return chosen,(index+1)%len(catalog)

def discover(data,cfg,catalog,limit=10,now=None):
    now=now or dt.datetime.now(dt.timezone.utc);stamp=now.isoformat(timespec='seconds')
    previous=data.setdefault('run',{}).get('companyDiscovery',{})
    chosen,cursor=choose(catalog,previous,max(1,min(30,limit)),now)
    states=dict(previous.get('companies',{}));boards=[];added=0
    known={(b['kind'],b['slug'].casefold()) for b in cfg.get('employerBoards',[])+cfg.get('reserveEmployerBoards',[])}
    existing={scan.canonical(j['applyUrl']) for j in data['jobs']}
    for company in chosen:
        url=company['careerUrl'];host=urls.urlsplit(url).hostname
        if not scan.valid_url(url,{host}):raise ValueError('Invalid catalog URL')
        aliases={host,host[4:] if host.startswith('www.') else 'www.'+host}
        fetcher=scan.Fetcher({**cfg,'allowedHosts':list(set(cfg['allowedHosts'])|aliases),'maxPageFetches':4})
        text,status=fetcher.page(url);found=[];structured=0
        if text:
            page=scan.Page();page.feed(text)
            for link in [url]+[urls.urljoin(url,h) for h in page.links]:
                board=board_from_link(link,company['name'])
                if board:
                    key=(board['kind'],board['slug'].casefold())
                    if key not in known:boards.append(board);known.add(key)
                    found.append(board)
            links=list(dict.fromkeys(scan.canonical(urls.urljoin(url,h)) for h in page.links if re.search(r'/(?:jobs?|careers|positions|openings)/',h,re.I) and scan.ROLE.search(urls.unquote(h))))
            for target in [url]+[x for x in links if scan.valid_url(x,{host})][:3]:
                body,code=(text,status) if target==url else fetcher.page(target)
                if not body:continue
                detail=scan.Page();detail.feed(body);nodes=list(scan.job_nodes(detail.jsonld))
                if len(nodes)!=1:continue
                item=scan.extract(nodes[0],target,company['name'],now.date().isoformat())
                if not item:continue
                state,reason=availability.decision(item,body,code,target,scan)
                if state!='open':continue
                structured+=1;key=scan.canonical(item['applyUrl'])
                if key in existing:continue
                if any(item['requisition'] and item['requisition']==j.get('requisition') and employers.norm(item['company'])==employers.norm(j['company']) for j in data['jobs']):continue
                item.update(availabilityStatus='open',availabilityReason=reason,lastConfirmedOpenAt=stamp,availabilityCheckedAt=stamp,availabilityHold=False,availabilityEvidenceUrl=target)
                data['jobs'].append(item);existing.add(key);added+=1
        state='blocked-or-unavailable' if not text else 'ats-linked' if found else 'structured-vacancy-checked' if structured else 'no-openings-published' if text and re.search(r'no open (?:roles|positions)|no (?:current|open) vacancies', ' '.join(page.text), re.I) else 'needs-adapter'
        states[company['id']]={'company':company['name'],'careerUrl':url,'checkedAt':stamp,'status':state,'fetchStatus':status,'boards':found,'atsKinds':sorted({b['kind'] for b in found}),'nextCheckAt':(now+dt.timedelta(hours=6 if text else 12)).isoformat(timespec='seconds')}
    if boards:
        local={**cfg,'employerBoards':boards,'allowedHosts':list(set(cfg['allowedHosts'])|{b['host'] for b in boards if b['kind']=='workday'})}
        old_report=data['run'].get('employerDiscovery');old_coverage=list(data['run'].get('coverage',[]))
        before=len(data['jobs']);employers.discover(data,local,scan);added+=len(data['jobs'])-before
        seen={c.get('source') for c in data['run'].get('coverage',[])}
        data['run']['coverage']+= [c for c in old_coverage if c.get('source') not in seen]
        if old_report:data['run']['employerDiscovery']=old_report
    report={'catalogSize':len(catalog),'checkedThisRun':len(chosen),'everChecked':len(states),'nextIndex':cursor,'newLeads':added,'linkedBoards':len(boards),'checkedAt':stamp,'companies':states}
    report['connectedCompanies']=sum(s['status'] in ('ats-linked','structured-vacancy-checked') for s in states.values())
    report['blockedCompanies']=sum(s['status']=='blocked-or-unavailable' for s in states.values())
    report['adapterGaps']=sum(s['status']=='needs-adapter' for s in states.values())
    data['run']['companyDiscovery']=report
    summary={'source':'Chennai company catalog','status':f'{len(states)}/{len(catalog)} companies checked; {added} new leads this run','detail':f'{len(chosen)} career pages attempted. Employer-linked ATS feeds and exact structured vacancies checked. Blocked pages and pages needing adapters remain explicit coverage gaps. Catalog membership does not prove a suitable vacancy. New jobs require full-description match review.'}
    data['run']['coverage']=[summary]+[c for c in data['run'].get('coverage',[]) if c.get('source')!=summary['source']]
    return report

if __name__=='__main__':
    path=ROOT/'site/data/jobs.json';data=json.loads(path.read_text());cfg=json.loads((ROOT/'config/search.json').read_text());catalog=json.loads((ROOT/'config/company-catalog.json').read_text())['companies']
    report=discover(data,cfg,catalog,cfg.get('companyDiscoveryBatch',10))
    path.write_text(json.dumps(data,ensure_ascii=True,indent=2)+'\n');print({k:v for k,v in report.items() if k!='companies'})
