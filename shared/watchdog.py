"""Recover missing research or publishing, not merely failed workflow statuses."""
import argparse,datetime as dt,json,subprocess,sys,urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo
IST=ZoneInfo('Asia/Kolkata')
ACTIVE={'queued','in_progress','pending','waiting','requested'}
def timestamp(value):
    try:
        t=dt.datetime.fromisoformat(value.replace('Z','+00:00'));return t if t.tzinfo else None
    except (ValueError,TypeError,AttributeError):return None

def decide(repository,live,runs,cfg,now,inventory):
    if any(r.get('status') in ACTIVE for r in runs):return 'wait','Engine already active; no duplicate dispatch.'
    recovery=[r for r in runs if r.get('display_title','').startswith('Recovery ·') and timestamp(r.get('created_at')) and 0<=(now-timestamp(r['created_at'])).total_seconds()<86400]
    pool=repository.get('run',{}).get('openingPool',{});last=timestamp(pool.get('lastReplenishedAt'));counts=inventory(repository,cfg,now)
    interval=2700 if counts['bufferShortfall'] else 21600
    due=not last or not 0<=(now-last).total_seconds()<interval
    local=now.astimezone(IST);scan_day=repository.get('run',{}).get('scanDateIst') or repository.get('run',{}).get('checkedOn')
    daily_missing=local.hour>=9 and scan_day!=local.date().isoformat()
    needed='scan' if due or daily_missing else 'publish' if repository!=live else None
    if needed:
        if len(recovery)>=3:return 'alert','Three recovery attempts in 24 hours; operator review required.'
        if any((now-timestamp(r['created_at'])).total_seconds()<1500 for r in recovery):return 'wait','Recovery cooldown: 25 minutes.'
        return (needed,'Employer refresh or daily discovery is due; workflow success alone does not establish freshness.' if needed=='scan' else 'Committed research differs from live data; publish without repeating discovery.')
    return 'healthy',f'{counts["reviewedOpen"]} confirmed assessments; current repository matches live data.'

def gh(*args):return subprocess.check_output(['gh',*args],text=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    if a.repo not in ['arun-john-alt/nixon-job-engine','arun-john-alt/sivanesh-job-engine']:raise SystemExit('Unexpected repository')
    sys.path.insert(0,str(Path.cwd()/'scripts'));from opening_pool import inventory
    # Raw media handles repository datasets above 1 MiB; no base64-size trap.
    repository=json.loads(gh('api',f'repos/{a.repo}/contents/site/data/jobs.json?ref=main','-H','Accept: application/vnd.github.raw+json'))
    cfg=json.loads(gh('api',f'repos/{a.repo}/contents/config/search.json?ref=main','-H','Accept: application/vnd.github.raw+json'))
    runs=json.loads(gh('api',f'repos/{a.repo}/actions/workflows/engine.yml/runs?per_page=100'))['workflow_runs']
    now=dt.datetime.now(dt.timezone.utc)
    if len(runs)==100 and timestamp(runs[-1]['created_at']) and (now-timestamp(runs[-1]['created_at'])).total_seconds()<86400:raise SystemExit('Run history requires pagination; refusing uncertain retry count')
    try:
        req=urllib.request.Request(f'https://arun-john-alt.github.io/{a.repo.split("/")[1]}/data/jobs.json?watchdog={int(now.timestamp())}',headers={'Cache-Control':'no-cache'})
        with urllib.request.urlopen(req,timeout=20) as response:live=json.load(response)
    except Exception:live=None
    action,reason=decide(repository,live,runs,cfg,now,inventory);print(json.dumps(dict(action=action,reason=reason)))
    if not a.dry_run and action in ('scan','publish'):print(gh('workflow','run','engine.yml','--repo',a.repo,'-f','scan='+str(action=='scan').lower(),'-f','recovery=true'))
    if action=='alert':raise SystemExit(1)
