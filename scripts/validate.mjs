import fs from 'node:fs';
import {validateDataset} from '../site/engine.js';
const data=validateDataset(JSON.parse(fs.readFileSync(new URL('../site/data/jobs.json',import.meta.url),'utf8')));
console.log(`Validated ${data.jobs.length} public jobs.`);

import {validateTrial} from '../site/career-ops.js';
const trial=validateTrial(JSON.parse(fs.readFileSync(new URL('../site/data/career-ops.json',import.meta.url),'utf8')));
for(const r of trial.recommendations)if(![...data.jobs,...trial.jobs].some(j=>j.id===r.jobId))throw new Error('Missing Career Ops job reference: '+r.jobId);
console.log('Validated Career Ops trial provenance.');
