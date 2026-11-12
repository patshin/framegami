/** Mock CLI tests: no GitHub writes or credentials; only fail-closed branches. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {root} from '../scripts/validate.mjs';
const results=[];
for(const [scenario,status] of [['no-auth',2],['existing',3],['forbidden',4],['network',4],['cancel',0]])test(`deploy safety: ${scenario} cannot create or overwrite a repository`,()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'iro-deploy-test-')),log=path.join(dir,'calls.txt');
 const stub=`#!/usr/bin/env bash\nprintf '%s\\n' "$*" >> "$IRO_TEST_LOG"\nif [[ "$1 $2" == 'auth status' ]]; then [[ "$IRO_TEST_SCENARIO" != 'no-auth' ]]; exit; fi\nif [[ "$1 $2" == 'api user' ]]; then if [[ "$4" == '.login' ]]; then echo iro-fixture; else echo 12345; fi; exit 0; fi\nif [[ "$1 $2" == 'api --include' ]]; then case "$IRO_TEST_SCENARIO" in existing) echo 'HTTP/2.0 200 OK'; exit 0;; forbidden) echo 'HTTP/2.0 403 Forbidden'; exit 1;; network) echo 'Network not available'; exit 1;; *) echo 'HTTP/2.0 404 Not Found'; exit 1;; esac; fi\necho 'UNEXPECTED_WRITE_OR_OTHER_ACTION'; exit 99\n`;
 fs.writeFileSync(path.join(dir,'gh'),stub,{mode:0o755});
 try{const env={...process.env,PATH:dir+path.delimiter+process.env.PATH,IRO_TEST_LOG:log,IRO_TEST_SCENARIO:scenario};delete env.IRO_CONFIRM_CREATE;const r=spawnSync('bash',[root+'/scripts/deploy-github.sh','iro-fixture'],{env,input:'CANCEL\n',encoding:'utf8'});assert.equal(r.status,status,r.stdout+r.stderr);const calls=fs.readFileSync(log,'utf8');assert(!calls.includes('repo create'));assert(!calls.includes('--method POST'));results.push({scenario,status:'PASS',writes:0});}
 finally{fs.rmSync(dir,{recursive:true,force:true});}
});
test.after(()=>fs.writeFileSync(root+'/docs/deploy-safety-results.json',JSON.stringify({kind:'MOCK_CLI_NO_REMOTE_EXECUTION',tests:results.length,results},null,2)+'\n'));
