"""Run the pinned upstream scanner without credentials; publish an explicit review queue."""
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
TRIAL=ROOT/'site/data/career-ops.json'
PIN='2d6ed587e60cbb1aaaac7e3dd4a9f5b7b46a26af'

def due(trial,now=None):
    local=(now or dt.datetime.now(dt.timezone.utc)).astimezone(ZoneInfo('Asia/Kolkata'))
    return local.hour>=9 and trial.get('discovery',{}).get('scanDateIst')!=local.date().isoformat()

def candidates(receipt,pipeline):
    allowed=set(receipt['added_urls']);rows=[]
    for line in pipeline.splitlines():
        if not line.startswith('- [ ] '):continue
        parts=line[6:].split(' | ')
        if len(parts)<4 or parts[0] not in allowed:continue
        if not re.match(r'^https://[^\s]+$',parts[0]):continue
        rows.append(dict(url=parts[0],company=parts[1][:200],title=parts[2][:300],location=parts[3][:300]))
    return rows

def scan(upstream):
    upstream=Path(upstream).resolve()
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=upstream,text=True).strip()!=PIN:raise ValueError('Unexpected upstream revision')
    trial=json.loads(TRIAL.read_text());now=dt.datetime.now(dt.timezone.utc)
    with tempfile.TemporaryDirectory(prefix='nixon-career-ops-') as temp:
        root=Path(temp);(root/'config').mkdir()
        (root/'portals.yml').write_text((ROOT/'config/career-ops/portals.json').read_text())
        (root/'config/profile.yml').write_text((ROOT/'config/career-ops/profile.json').read_text())
        env={'PATH':os.environ['PATH'],'CAREER_OPS_ROOT':str(root),'CAREER_OPS_HTTP_TIMEOUT_MS':'15000'}
        result=subprocess.run(['node','scan.mjs','--json','--quiet'],cwd=upstream,env=env,text=True,capture_output=True,timeout=1200)
        if result.returncode not in (0,2):raise RuntimeError('Upstream scanner failed; previous results retained')
        receipt=json.loads(result.stdout)
        if receipt.get('version')!='careerops.scan.receipt@1' or not isinstance(receipt.get('added_urls'),list) or receipt.get('scanned',0)==0:raise ValueError('Invalid or empty scan receipt')
        queue=candidates(receipt,(root/'data/pipeline.md').read_text())
        trial['discovery']={'checkedAt':now.isoformat(timespec='seconds'),'scanDateIst':now.astimezone(ZoneInfo('Asia/Kolkata')).date().isoformat(),'status':'partial' if receipt.get('errors') else 'success','scanned':receipt['scanned'],'skipped':receipt['skipped'],'examined':receipt['found'],'candidateCount':len(queue),'sourceFailures':len(receipt.get('errors',[])),'candidates':queue}
        trial['refresh']='Employer discovery runs daily at 9 AM IST in GitHub Actions. Codex evaluation runs separately on this Mac; review freshness is shown independently. Unconfirmed or stale vacancies are hidden.'
        TRIAL.write_text(json.dumps(trial,ensure_ascii=False,indent=2)+'\n')
        print(f"Career Ops: {len(queue)} candidates from {receipt['scanned']} sources; evaluation is a separate step.")

def audit():
    try:from scripts import availability,scan as scanner
    except ModuleNotFoundError:import availability;import scan as scanner
    trial=json.loads(TRIAL.read_text())
    if trial.get('jobs'):
        availability.audit({'jobs':trial['jobs']},json.loads((ROOT/'config/search.json').read_text()),scanner)
        TRIAL.write_text(json.dumps(trial,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('command',choices=['due','scan','audit']);p.add_argument('--upstream');a=p.parse_args()
    if a.command=='due':
        value=due(json.loads(TRIAL.read_text())) or os.environ.get('GITHUB_EVENT_NAME')=='workflow_dispatch'
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write(f'career_ops_due={str(value).lower()}\n')
    elif a.command=='scan':scan(a.upstream)
    else:audit()
