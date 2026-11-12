import fs from 'node:fs';
import {readJSON,root,validateCatalog} from './validate.mjs';
import {getDisplaySample,getAcceptedExample} from '../src/core.mjs';

const catalog=readJSON('data/catalog.json'), validation=validateCatalog();
if(validation.errors.length)throw new Error(validation.errors.join('\n'));
const entries=catalog.map(s=>{
  const image=getDisplaySample(s);
  const kind=image?.kind;
  const provisional=kind==='montage-derived-preview';
  const procedural=kind==='procedural-style-study';
  const independent=kind==='same-input-showcase'||image?.accepted===true;
  return {
    styleId:s.id,name:s.name,
    status:!image?'MISSING_IMAGE':provisional?'PROVISIONAL_MONTAGE_CROP':procedural?'PROCEDURAL_B00_STUDY_NOT_AI_GENERATED':independent?'INDEPENDENT_SHOWCASE_PROMPT_UNVERIFIED':'UNCLASSIFIED_PREVIEW',
    imagePath:image?.path??null,
    generationId:image?.generationId??null,
    imageSource:provisional?'cropped-generated-montage':procedural?'deterministic-B00-processing':independent?'separate-generated-image':'none',
    independentlyGenerated:independent,
    promptVerified:!!getAcceptedExample(s)
  };
});
const count=(predicate)=>entries.filter(predicate).length;
const report={
  total:catalog.length,
  withImages:count(x=>!!x.imagePath),
  independentShowcases:count(x=>x.independentlyGenerated),
  provisionalMontageCrops:count(x=>x.imageSource==='cropped-generated-montage'),
  proceduralStudies:count(x=>x.imageSource==='deterministic-B00-processing'),
  missing:count(x=>!x.imagePath),
  exactPromptValidated:count(x=>x.promptVerified),
  retainedProceduralStudyRecords:catalog.reduce((n,s)=>n+(s.illustrations||[]).filter(x=>x.kind==='procedural-style-study').length,0),
  previewCoverageComplete:entries.every(x=>x.imagePath),
  complete:entries.every(x=>x.independentlyGenerated),
  entries
};
fs.mkdirSync(root+'/evidence',{recursive:true});
fs.writeFileSync(root+'/evidence/image-coverage.json',JSON.stringify(report,null,2)+'\n');
console.log(`${report.withImages}/${report.total} style entries have visual previews (${report.independentShowcases} independently generated, ${report.provisionalMontageCrops} montage crops, ${report.proceduralStudies} deterministic procedural studies). Missing images: ${report.missing}. Exact-prompt validation: ${report.exactPromptValidated}.`);
if(process.argv.includes('--require-complete')&&!report.complete){
  console.error('213 independent-style image completion gate NOT met; provisional crops cannot satisfy this gate.');
  process.exitCode=2;
}
