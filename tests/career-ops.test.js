import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import * as engine from '../site/engine.js';import * as co from '../site/career-ops.js';import {companyLogo,productCompany} from '../site/companies.js';
const trial=JSON.parse(fs.readFileSync(new URL('../site/data/career-ops.json',import.meta.url)));
const raw=JSON.parse(fs.readFileSync(new URL('../site/data/jobs.json',import.meta.url)));
const fresh=()=>raw.jobs.map(j=>({...j,lastConfirmedOpenAt:new Date().toISOString(),availabilityHold:false}));
test('real scanner provenance and independent review required',()=>{
 assert.equal(co.validateTrial(trial).recommendations.length,2);
 for(const alter of [t=>t.upstream.commit='invented',t=>t.recommendations[0].rating=3.9,t=>t.candidateUrls=[],t=>t.recommendations[0].confidence='High',t=>t.recommendations.push(t.recommendations[0])]){const bad=structuredClone(trial);alter(bad);assert.throws(()=>co.validateTrial(bad));}
});
test('trial hides changed descriptions, unreviewed, stale and closed vacancies',()=>{
 const jobs=fresh();const cohort=co.trialJobs(trial,jobs,25);assert.equal(cohort.length,2);
 for(const patch of [{employerDescriptionHash:'changed'},{analysisStatus:'needs-review',score:[]},{verification:'closed'},{lastConfirmedOpenAt:'2020-01-01T00:00:00Z'},{discoveryEligible:false}])assert.equal(co.trialJobs(trial,cohort.map(j=>({...j,...patch})),25).length,0);
 assert.equal(co.compareTrial(trial,jobs,25).overlap,2);
});
const code=fs.readFileSync(new URL('../site/app.js',import.meta.url),'utf8').split("document.addEventListener('click'")[0].replace(/^import .*;\n/gm,'');
test('actual app isolates Career Ops without changing regular Jobs and keeps both scores',()=>{
 const c=vm.createContext({...engine,...co,companyLogo,productCompany,document:{},location:{hostname:'localhost'},setTimeout,clearTimeout});
 vm.runInContext(code+'\nD=validateDataset('+JSON.stringify({...raw,jobs:fresh()})+');C=validateTrial('+JSON.stringify(trial)+');',c);
 const main=vm.runInContext('eligible().length',c);assert.ok(main>2);
 assert.equal(vm.runInContext("view='careerops';eligible().length",c),2);
 const html=vm.runInContext('eligible().map(j=>card(j)).join(\'\')+careerOpsHeader()+careerOpsReview(eligible()[0])',c);
 assert.match(html,/\d+% match/);assert.match(html,/Career Ops 4\.\d\/5/);assert.match(html,/Low confidence/);assert.match(html,/evaluation|assessments|assessment/i);
 vm.runInContext("D.jobs.forEach(j=>j.lastConfirmedOpenAt='2020-01-01T00:00:00Z');filter.archived=true",c);
 assert.equal(vm.runInContext('eligible().length',c),0);
 vm.runInContext("view='jobs';filter.archived=false;D.jobs.forEach(j=>j.lastConfirmedOpenAt=new Date().toISOString())",c);assert.equal(vm.runInContext('eligible().length',c),main);
});

test('independent trial vacancy can add coverage without becoming a regular match',()=>{
 const jobs=fresh();const seed=jobs.find(j=>j.id===trial.recommendations[0].jobId);const extra={...seed,id:'independent-trial-job',applyUrl:'https://jobs.lever.co/example/independent'};
 const t=structuredClone(trial);t.jobs=[extra];t.candidateUrls.push(extra.applyUrl);t.recommendations.push({...t.recommendations[0],jobId:extra.id,discoveredUrl:extra.applyUrl});
 const valid=co.validateTrial(t);assert.equal(co.trialJobs(valid,jobs,25).length,3);const counts=co.compareTrial(valid,jobs,25);assert.equal(counts.careerOps-counts.overlap,1);
 const merged=[...jobs,{...extra,careerOpsOnly:true}];assert.equal(co.compareTrial(valid,merged,25).main,counts.main);assert.equal(co.compareTrial(valid,merged,25).overlap,2);
});
