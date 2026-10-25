"""Measure actual calendar-day observations. Simulations never count as uptime."""
import argparse,datetime as dt,json
from pathlib import Path
from zoneinfo import ZoneInfo
IST=ZoneInfo('Asia/Kolkata')

def parse(value):
    try:
        t=dt.datetime.fromisoformat(value.replace('Z','+00:00'));return t if t.tzinfo else None
    except (ValueError,AttributeError,TypeError):return None

def summarize(samples,now):
    recent=[];by_day={}
    for sample in samples:
        stamp=parse(sample.get('checkedAt'))
        if stamp and 0<=(now-stamp).total_seconds()<=7*86400:
            recent.append(sample);by_day.setdefault(stamp.astimezone(IST).date(),[]).append(sample)
    today=now.astimezone(IST).date();expected={today-dt.timedelta(days=i) for i in range(7)}
    observed=expected.intersection(by_day);complete=len(observed)==7
    shortfall_days=sum(any(s.get('shortfall',20)>0 for s in by_day[d]) for d in observed)
    error_days=sum(any(s.get('sourceFailures',0)>0 for s in by_day[d]) for d in observed)
    times=sorted(parse(s['checkedAt']) for s in recent);gaps=[(b-a).total_seconds()/3600 for a,b in zip(times,times[1:])]
    return dict(observationDays=len(observed),requiredDays=7,status='observing' if not complete else 'needs-attention' if shortfall_days or error_days else 'ready-for-deployment-review',daysBelowMinimum=shortfall_days,daysWithSourceErrors=error_days,longestObservedGapHours=round(max(gaps,default=0),2),missingIstDates=sorted(d.isoformat() for d in expected-observed),samples=recent[-200:],note='Calendar-day observations use IST and real timestamps. Test simulations do not count. Review GitHub deployment history separately before accepting the trial.')

def record(data,now=None):
    now=now or dt.datetime.now(dt.timezone.utc);run=data.setdefault('run',{});health=run.get('sharedPipeline',{});pool=run.get('openingPool',{})
    samples=run.get('reliability',{}).get('samples',[])
    samples.append(dict(checkedAt=now.isoformat(timespec='seconds'),status=health.get('status','missing'),sourceFailures=health.get('sourceFailures',0),reviewedOpen=pool.get('reviewedOpen',0),shortfall=pool.get('shortfall',20),newRelevantVacancies=run.get('employerDiscovery',{}).get('newLeads',0)))
    report=summarize(samples,now);run['reliability']=report
    days=report['observationDays'];run['coverage']=[{'source':'Reliability trial','status':f'{days}/7 IST days observed','detail':f'{len(report["samples"])} real observations. {report["daysBelowMinimum"]} days with opening shortfalls; {report["daysWithSourceErrors"]} days with source errors. Missing days cannot count as success. Cloud watchdog plus an existing Mac-based Codex follow-up provide recovery; no new external hosting login is configured.'}]+[c for c in run.get('coverage',[]) if c['source']!='Reliability trial']
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path.cwd());a=p.parse_args();path=a.root/'site/data/jobs.json';data=json.loads(path.read_text());print(record(data)['status']);path.write_text(json.dumps(data,indent=2)+'\n')
