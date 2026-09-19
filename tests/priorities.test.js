import test from 'node:test';import assert from 'node:assert/strict';
import {priorityCompare,validateDataset} from '../site/engine.js';import {productCompany} from '../site/companies.js';
const source={label:'Employer',url:'https://example.com/job/1'};
const job=(id,extra={})=>({id,company:'KLA',roleLevel:'individual',locationEligibility:'chennai',salary:{kind:'unknown'},analysisStatus:'reviewed',score:[{points:20},{points:15},{points:15},{points:10},{points:10}],...extra});
const salary=n=>({kind:'employer-disclosed',basis:'Annual CTC',minLpa:n,maxLpa:n+5,sources:[source]});
test('priority order is product, management, comparable salary, location, then fit',()=>{
 const rows=[job('services',{company:'Virtusa',roleLevel:'manager',salary:salary(80)}),job('ic',{salary:salary(60)}),job('remote',{roleLevel:'manager',locationEligibility:'remote-india',salary:salary(30)}),job('chennai',{roleLevel:'manager',salary:salary(30)}),job('better-pay',{roleLevel:'manager',locationEligibility:'remote-india',salary:salary(40)})];
 assert.deepEqual(rows.sort(priorityCompare).map(j=>j.id),['better-pay','chennai','remote','ic','services']);
});
test('third-party and base salary are not ranked as confirmed annual CTC',()=>{
 const known=job('known',{salary:salary(25)});
 for(const sal of [{kind:'unknown',maxLpa:100},{kind:'third-party',basis:'Annual CTC',minLpa:100,sources:[source]},{kind:'employer-disclosed',basis:'Annual base pay',minLpa:100,sources:[source]},{kind:'employer-disclosed',basis:'Annual CTC',minLpa:100,sources:[]}])assert.ok(priorityCompare(known,job('other',{salary:sal}))<0);
});
test('product badge is not assigned to a services firm, distributor, or unknown company',()=>{
 for(const name of ['Virtusa','EPAM Systems','Hydsoft','Ingram Micro','Unknown','__proto__'])assert.equal(productCompany(name),null);
 for(const name of ['KLA','Amazon','Jitterbit','NETGEAR'])assert.match(productCompany(name).url,/^https:/);
});
test('reviewed management and remote eligibility survive schema validation',()=>{
 const raw={schemaVersion:2,jobs:[{...job('test-one',{roleLevel:'manager',locationEligibility:'remote-india'}),title:'QA Manager',applyUrl:'https://example.com/job/1',score:[]}]};
 const j=validateDataset(raw).jobs[0];assert.equal(j.roleLevel,'manager');assert.equal(j.locationEligibility,'remote-india');
 raw.jobs[0].roleLevel='executive';raw.jobs[0].locationEligibility='remote friendly';const unknown=validateDataset(raw).jobs[0];assert.equal(unknown.roleLevel,'individual');assert.equal(unknown.locationEligibility,'unknown');
});
