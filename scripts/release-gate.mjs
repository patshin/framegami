// This gate separates technical readiness from the requested content-complete release.
import fs from 'node:fs';
import {validateCatalog,readJSON,root} from './validate.mjs';
import {VERSION} from '../src/core.mjs';
const result=validateCatalog(),b=readJSON('data/benchmark.json'),styles=readJSON('data/catalog.json');
const missing=[];
if(result.errors.length)missing.push('CATALOG_VALIDATION_FAILED');
if(!b.path||!b.sha256)missing.push('STANDALONE_B00_ORIGINAL_MISSING');
if(styles.some(s=>!s.examples.some(e=>e.accepted===true&&e.model==='chatgpt'&&e.promptVersion===s.version)))missing.push('CHATGPT_EXAMPLE_MISSING_FOR_ONE_OR_MORE_STYLES');
const report={version:VERSION,decision:missing.length?'RESEARCH_PREVIEW_ONLY':'CONTENT_EVIDENCE_GATE_PASSED',stats:result.stats,blockers:missing,remoteDeployment:'NOT_PERFORMED',visualQuality:'NOT_ESTABLISHED_BY_CODE_TESTS',allowedAsResearchPreview:!result.errors.length,completeProduct:false};
fs.writeFileSync(root+'/docs/release-gate.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
if(result.errors.length||missing.length&&!process.argv.includes('--allow-research-preview'))process.exitCode=2;
