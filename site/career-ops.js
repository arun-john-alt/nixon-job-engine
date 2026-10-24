import {scoreOf,isUnavailable,payGate} from './engine.js';
export function validateTrial(raw){
 if(raw?.schemaVersion!==1||raw?.upstream?.commit!=='2d6ed587e60cbb1aaaac7e3dd4a9f5b7b46a26af'||!Array.isArray(raw.candidateUrls)||!Array.isArray(raw.recommendations))throw new Error('Invalid Career Ops trial provenance');
 const ids=new Set();
 for(const r of raw.recommendations){
  if(!r.jobId||ids.has(r.jobId)||!raw.candidateUrls.includes(r.discoveredUrl)||!Number.isFinite(r.rating)||r.rating<4||r.rating>5||!r.rationale||!/^[a-f0-9]{64}$/.test(r.descriptionHash)||!['Low','Medium','High'].includes(r.confidence)||r.dimensions?.length!==5||r.dimensions.some(d=>!d.name||!d.evidence||!['supported','partial','unknown'].includes(d.status)))throw new Error('Invalid Career Ops recommendation');
  if(r.dimensions.filter(d=>d.status==='unknown').length>=2&&r.confidence!=='Low')throw new Error('Career Ops confidence must reflect missing evidence');
  ids.add(r.jobId);
 }
 return raw;
}
export function recommendation(trial,job){return trial?.recommendations.find(r=>r.jobId===job.id&&r.descriptionHash===job.employerDescriptionHash);}
export function trialJobs(trial,jobs,target){return jobs.filter(j=>recommendation(trial,j)&&scoreOf(j)!==null&&j.discoveryEligible!==false&&!isUnavailable(j)&&payGate(j,target)!=='Below target');}
export function compareTrial(trial,jobs,target){const main=jobs.filter(j=>scoreOf(j)!==null&&j.discoveryEligible!==false&&!isUnavailable(j)&&payGate(j,target)!=='Below target');const cohort=trialJobs(trial,jobs,target);return {main:main.length,careerOps:cohort.length,overlap:cohort.filter(j=>main.some(m=>m.id===j.id)).length};}
