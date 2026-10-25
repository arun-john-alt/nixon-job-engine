"""Publish only research data; reconcile concurrent commits without force pushes."""
import subprocess,sys
from pathlib import Path

def run(*args,check=True):return subprocess.run(args,check=check).returncode
paths=[str(p) for p in [Path('site/data/jobs.json'),Path('site/data/career-ops.json')] if p.exists()]
if run('git','diff','--quiet','--',*paths,check=False)==0:raise SystemExit()
run('git','config','user.name','github-actions[bot]');run('git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
run('git','add','--',*paths);run('git','commit','-m','data: refresh employer-job discovery and coverage')
for attempt in range(3):
    if run('git','push','origin','HEAD:main',check=False)==0:break
    run('git','fetch','origin','main')
    if run('git','rebase','origin/main',check=False):
        run('git','rebase','--abort',check=False)
        raise SystemExit('Concurrent research update conflicts; retained diagnostics, no data overwritten. Watchdog will retry.')
    # A concurrent code change must be validated before this artifact is deployed.
    run('node','--test',*[str(p) for p in Path('tests').glob('*.test.js')])
    run('node','scripts/validate.mjs');run(sys.executable,'scripts/build.py')
else:raise SystemExit('Concurrent updates prevented publishing after three safe attempts.')
