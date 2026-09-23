#!/usr/bin/env python3
"""Publish ONLY site/. Private files and repository internals are never copied."""
from pathlib import Path
import json
import shutil
import re
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'site';target=ROOT/'dist'
allowed={'index.html','styles.css','app.js','engine.js','resume.js','favicon.svg','data/jobs.json','companies.js'}
allowed.update({'assets/companies/extreme.png', 'assets/companies/company.svg', 'assets/companies/miratech.png', 'assets/companies/kla.png', 'assets/companies/ust.svg', 'assets/companies/logitech.png', 'assets/companies/kumaran.png', 'assets/companies/epam.png', 'assets/companies/omnissa.png', 'assets/companies/hcltech.png', 'assets/companies/virtusa.png', 'assets/companies/arista.png', 'assets/companies/viasat.png'})
allowed.update({'assets/companies/'+key+'.png' for key in ['amazon','jitterbit','hydsoft','ingram','netgear']})
allowed.update({'assets/companies/'+key+'.png' for key in ['tactive','nokia','yipitdata','madecard','saaf','wpp','xerago','novature']})
actual={p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
extra=actual-allowed
if extra:raise SystemExit('Unexpected public files: '+', '.join(sorted(extra)))
if any(p.is_symlink() for p in source.rglob('*')):raise SystemExit('No symbolic links allowed in public output.')
data=json.loads((source/'data/jobs.json').read_text())
if data.get('schemaVersion')!=2:raise SystemExit('Invalid data schema version')
blocked={'currentCtcLpa','master','notes','email','phone','applications','drafts','versions','confirmedCtcLpa','payEvidence'}
def check(value):
    if isinstance(value,dict):
        bad=blocked.intersection(value)
        if bad:raise SystemExit('Private fields in public dataset: '+str(bad))
        for v in value.values():check(v)
    elif isinstance(value,list):
        for v in value:check(v)
check(data)
if target.exists():shutil.rmtree(target)
shutil.copytree(source,target)
(target/'.nojekyll').write_text('')
print('Public build complete:',target)
print('Privacy gate passed: public files only; no private workspace fields.')
