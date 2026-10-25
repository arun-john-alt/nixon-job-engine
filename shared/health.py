"""Seven-day operational observations; no fabricated uptime or guaranteed supply."""
import argparse,datetime as dt,json
from pathlib import Path

def record(data,now=None):
    now=now or dt.datetime.now(dt.timezone.utc);run=data.setdefault('run',{});health=run.get('sharedPipeline',{});pool=run.get('openingPool',{})
    samples=run.get('reliability',{}).get('samples',[])
    samples.append(dict(checkedAt=now.isoformat(timespec='seconds'),status=health.get('status','missing'),sourceFailures=health.get('sourceFailures',0),reviewedOpen=pool.get('reviewedOpen',0),shortfall=pool.get('shortfall',20)))
    cutoff=(now-dt.timedelta(days=7)).isoformat();samples=[s for s in samples if s['checkedAt']>=cutoff][-200:]
    days=len({s['checkedAt'][:10] for s in samples})
    run['reliability']={'observationDays':days,'requiredDays':7,'status':'observing' if days<7 else 'review-required','samples':samples,'note':'Seven-day trial records actual runs and shortfalls. Deployment success is checked separately in GitHub; scan success is not deployment success.'}
    run['coverage']=[{'source':'Reliability trial','status':f'{days}/7 days observed','detail':f'{len(samples)} completed discovery observations retained. Source errors and opening shortfalls are recorded. A separate hourly watchdog retries missing or failed workflows; GitHub scheduling remains best-effort.'}]+[c for c in run.get('coverage',[]) if c['source']!='Reliability trial']
    return run['reliability']
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path.cwd());a=p.parse_args();path=a.root/'site/data/jobs.json';data=json.loads(path.read_text());print(record(data)['status']);path.write_text(json.dumps(data,indent=2)+'\n')
