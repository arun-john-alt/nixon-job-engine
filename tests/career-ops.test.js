import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import * as engine from '../site/engine.js';import * as co from '../site/career-ops.js';import {companyLogo,productCompany} from '../site/companies.js';
// Behaviour fixtures are independent of employers closing/changing real vacancies.
// Production data is validated separately and may legitimately yield zero picks.
const liveTrial=JSON.parse(fs.readFileSync(new URL('../site/data/career-ops.json',import.meta.url)));
const liveRaw=JSON.parse(fs.readFileSync(new URL('../site/data/jobs.json',import.meta.url)));
const weights=[35,20,20,15,10];
const raw={schemaVersion:2,updatedAt:'2026-10-27',run:{},jobs:Array.from({length:3},(_,i)=>({
 id:'fixture-job-'+i,company:'Fixture Employer '+i,title:'QA Engineer',applyUrl:'https://example.com/jobs/'+i,
 employerDescriptionHash:String(i+1).repeat(64),analysisStatus:'reviewed',verification:'live',discoveryEligible:true,
 score:weights.map((weight,n)=>({name:'Dimension '+n,weight,points:weight-2,reason:'Synthetic evidence for behaviour tests'})),salary:{kind:'unknown'},
}))};
const trial={schemaVersion:1,evaluatedAt:'2026-10-27',upstream:{commit:'2d6ed587e60cbb1aaaac7e3dd4a9f5b7b46a26af',repository:'https://github.com/career-ops-hq/career-ops',version:'fixture'},
 scan:{date:'2026-10-27',scanned:1,skipped:0,added:2,found:2},method:'Synthetic assessment fixture',refresh:'Fixture only',exclusions:[],jobs:[],
 candidateUrls:raw.jobs.slice(0,2).map(j=>j.applyUrl),recommendations:raw.jobs.slice(0,2).map(j=>({jobId:j.id,discoveredUrl:j.applyUrl,descriptionHash:j.employerDescriptionHash,rating:4.1,confidence:'Low',rationale:'Synthetic recommendation',
 dimensions:['CV match','North Star alignment','Compensation','Cultural signals','Red flags'].map((name,i)=>({name,evidence:'Synthetic dimension evidence',status:i<2?'supported':'unknown'}))}))};
const fresh=()=>raw.jobs.map(j=>({...j,lastConfirmedOpenAt:new Date().toISOString(),availabilityHold:false}));
test('live research permits recommendations to close without blocking publication',()=>{
 const valid=co.validateTrial(liveTrial),jobs=engine.validateDataset(liveRaw).jobs;
 const picks=co.trialJobs(valid,jobs,25);
 assert.ok(picks.every(j=>!engine.isUnavailable(j)&&co.recommendation(valid,j)));
 const closed=j=>({...j,verification:'closed'});
 assert.equal(co.trialJobs({...valid,jobs:valid.jobs.map(closed)},jobs.map(closed),25).length,0);
});
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
