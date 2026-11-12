import fs from 'node:fs';
import path from 'node:path';
import {root,readJSON,validateCatalog} from './validate.mjs';
import {escapeHTML,composePrompt,getDisplaySample,sampleSourceLabel,VERSION} from '../src/core.mjs';
const result=validateCatalog();if(result.errors.length)throw new Error(result.errors.join('\n'));
const out=path.join(root,'dist');fs.rmSync(out,{recursive:true,force:true});fs.mkdirSync(path.join(out,'assets'),{recursive:true});
const styles=readJSON('data/catalog.json'),categories=readJSON('data/categories.json'),sources=readJSON('data/sources.json'),benchmark=readJSON('data/benchmark.json');
const safeJSON=x=>JSON.stringify(x).replace(/</g,'\\u003c').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');
const data={styles,categories,sources,benchmark,stats:result.stats,version:VERSION};
const repo=(process.env.GITHUB_REPOSITORY||'').split('/')[1]||'';
const requestedBase=process.env.SITE_BASE_PATH??(repo&&!repo.endsWith('.github.io')?'/'+repo+'/':'/');
if(!/^\/(?:[A-Za-z0-9._-]+\/)*$/.test(requestedBase)||requestedBase.split('/').some(s=>s==='.'||s==='..'))throw new Error('Invalid SITE_BASE_PATH');
const siteBase=requestedBase;
// Standalone previews embed only accepted assets; research artwork never becomes evidence.
const embeddedAssets={};
for(const file of [benchmark.path,...styles.flatMap(s=>s.examples.filter(e=>e.accepted).map(e=>e.path)),...styles.flatMap(s=>(s.illustrations||[]).filter(e=>e.displayApproved).map(e=>e.path))].filter(Boolean)){
 const p=path.join(root,'public',file),mime={'.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp'}[path.extname(file)];
 if(mime&&fs.existsSync(p))embeddedAssets[file]='data:'+mime+';base64,'+fs.readFileSync(p).toString('base64');
}
const shared=fs.readFileSync(path.join(root,'src/core.mjs'),'utf8').replace(/^export /gm,'');
const app=shared+'\n'+fs.readFileSync(path.join(root,'src/app.js'),'utf8');
const css=fs.readFileSync(path.join(root,'src/styles.css'),'utf8');
fs.writeFileSync(path.join(out,'assets/app.js'),app);
fs.writeFileSync(path.join(out,'assets/styles.css'),css);
fs.writeFileSync(path.join(out,'assets/catalog.js'),'window.IRO_DATA='+safeJSON(data)+';');
if(fs.existsSync(path.join(root,'public')))fs.cpSync(path.join(root,'public'),out,{recursive:true});
fs.writeFileSync(path.join(out,'.nojekyll'),'');
const favicon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#f5f3ed"/><rect x="42" y="10" width="10" height="44" rx="2" fill="#ad3f35"/><path d="M14 15h12v34H14z" fill="#26312b"/></svg>';
fs.writeFileSync(path.join(out,'assets/favicon.svg'),favicon);
const owner = process.env.GITHUB_REPOSITORY_OWNER || 'patshin';
const publicBase = new URL(repo ? siteBase : '/framegami/', `https://${owner}.github.io`);
const sitemap = new Set();
function renderHTML(lang,page='atlas',id='',rel='./',preview=false){
 const s=styles.find(x=>x.id===id), title=(s?s.name[lang]+' — ':'')+(lang==='zh'?'Framegami｜图生图风格图鉴':'Framegami · Image-to-image Style Atlas');
 const config={lang,page,id,base:rel,preview};
 const text = s ? s.technique[lang] : lang==='zh'
   ? '213 种图生图风格，每种都有示例图和可复制的中英文提示词。'
   : '213 image-to-image styles, with visual examples and copyable prompts in English and Chinese.';
 const sample = s && getDisplaySample(s);
 const suffix = s ? `style/${id}/` : page==='atlas' ? '' : page+'/';
 const url = language => new URL(language+'/'+suffix, publicBase).href;
 const indexable = !preview && ['atlas','style','about'].includes(page);
 if(indexable) sitemap.add(url(lang));
 const image = new URL(sample?.path || `demo/atlas-${lang}.jpg`, publicBase).href;
 const meta = `<meta name="robots" content="${indexable?'index,follow':'noindex,follow'}">
<link rel="canonical" href="${url(lang)}">
${['zh','en'].map(l=>`<link rel="alternate" hreflang="${l}" href="${url(l)}">`).join('')}
<meta property="og:type" content="website"><meta property="og:site_name" content="Framegami">
<meta property="og:title" content="${escapeHTML(title)}"><meta property="og:description" content="${escapeHTML(text)}">
<meta property="og:url" content="${url(lang)}"><meta property="og:image" content="${image}">
<meta name="twitter:card" content="summary_large_image">`;
 const fallback=s?`<h1>${escapeHTML(s.name[lang])}</h1><p>${escapeHTML(s.technique[lang])}</p>${sample?`<img src="${rel}${sample.path}" alt="${escapeHTML(s.name[lang])}" width="${sample.width}" height="${sample.height}">`:''}<p>${sampleSourceLabel(sample,lang)}</p><pre style="white-space:pre-wrap">${escapeHTML(composePrompt(s,'chatgpt',lang))}</pre>`:page==='about'?`<h1>${lang==='zh'?'关于 Framegami':'About Framegami'}</h1><p><a href="https://github.com/patshin/framegami/blob/main/evidence/image-coverage.json">${lang==='zh'?'示例图来源':'Image sources'}</a> · <a href="https://github.com/patshin/framegami/blob/main/CONTENT-LICENSE.md">${lang==='zh'?'内容许可':'Content license'}</a></p>`:page!=='atlas'?`<p>${lang==='zh'?'请启用 JavaScript 使用此功能。':'Enable JavaScript to use this feature.'}</p>`:`<h1>${escapeHTML(title)}</h1><p>${escapeHTML(text)}</p>${styles.map(s=>`<a href="${rel}${lang}/style/${s.id}/">${escapeHTML(s.name[lang])}</a>`).join('')}`;
 return `<!doctype html>\n<html lang="${lang==='zh'?'zh-CN':'en'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="${escapeHTML(text)}"><meta name="theme-color" content="#f5f3ed">${meta}<meta http-equiv="Content-Security-Policy" content="default-src 'self' data: blob:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'none'; object-src 'none'; base-uri 'self'; form-action 'none'"><title>${escapeHTML(title)}</title>${preview?`<style>${css}</style>`:`<link rel="icon" href="${rel}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="${rel}assets/styles.css">`}</head><body><a id="skip-link" class="skip-link" href="#main">${lang==='zh'?'跳到内容':'Skip to content'}</a><header id="site-head" class="site-head"></header><div class="site-layout"><aside id="sidebar" class="sidebar" aria-label="${lang==='zh'?'风格分类':'Style categories'}"></aside><main id="main" class="main" tabindex="-1"><div class="skeleton">${lang==='zh'?'正在打开风格图鉴…':'Opening the atlas…'}</div></main></div><div id="compare-tray" class="compare-tray" hidden></div><div id="toast" class="toast" role="status" aria-live="polite"></div><dialog id="mobile-menu" class="nav-dialog" aria-label="${lang==='zh'?'导航菜单':'Navigation menu'}"></dialog><dialog id="action-dialog"></dialog><input id="import-file" type="file" accept="application/json,.json" hidden><noscript><section class="no-js">${fallback}</section><style>.site-layout,.site-head{display:none}</style></noscript><script>window.IRO_CONFIG=${safeJSON(config)};</script>${preview?`<script>window.IRO_DATA=${safeJSON({...data,embeddedAssets})};</script><script>${app.replace(/<\/script/gi,'<\\/script')}</script>`:`<script src="${rel}assets/catalog.js" defer></script><script src="${rel}assets/app.js" defer></script>`}</body></html>`;
}
let routes=0;
function writeRoute(route,lang,page,id=''){const file=path.join(out,route,'index.html');fs.mkdirSync(path.dirname(file),{recursive:true});const depth=route.split('/').filter(Boolean).length,rel=depth?'../'.repeat(depth):'./';fs.writeFileSync(file,renderHTML(lang,page,id,rel));routes++;}
writeRoute('','zh','atlas');
for(const lang of ['zh','en']){
 writeRoute(lang,lang,'atlas');
 for(const page of ['about','workbench','favorites','custom','compare'])writeRoute(lang+'/'+page,lang,page);
 for(const s of styles)writeRoute(lang+'/style/'+s.id,lang,'style',s.id);
}
// A 404 can be served at ANY nested path by Pages. It must not depend on relative app assets.
const errorPage=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'"><title>404 — Framegami</title><style>body{background:#f5f3ed;color:#222a29;font:16px/1.8 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:0;padding:12vh 8vw}main{max-width:640px;margin:auto;border-top:1px solid #dcded5;padding-top:32px}small{letter-spacing:3px;color:#6b716c}h1{font-family:serif;font-size:clamp(32px,6vw,54px);font-weight:500;line-height:1.3}p{color:#6b716c}a{display:inline-block;margin:12px 12px 0 0;padding:10px 18px;border:1px solid #dcded5;color:inherit;text-decoration:none}a:focus-visible{outline:2px solid #2f625f;outline-offset:4px}</style></head><body><main><small>Framegami / 404</small><h1>找不到这个页面<br>Page not found</h1><a href="${siteBase}zh/">返回中文图鉴 →</a><a href="${siteBase}en/">English atlas →</a></main></body></html>`;
fs.writeFileSync(path.join(out,'404.html'),errorPage);
fs.writeFileSync(path.join(root,'IRO-preview.html'),renderHTML('zh','atlas','','./',true));
// Export all six text adaptations from the same compiler used by the browser.
const prompts=path.join(root,'prompts');fs.rmSync(prompts,{force:true,recursive:true});
for(const model of ['chatgpt','gemini','flux'])for(const lang of ['zh','en']){
 const dir=path.join(prompts,model,lang);fs.mkdirSync(dir,{recursive:true});
 for(const s of styles)fs.writeFileSync(path.join(dir,s.id+'.md'),`# ${s.name[lang]}\n\nIRO ID: ${s.id}\nVersion: ${s.version}\nModel target: ${model}\nLanguage: ${lang}\nStatus: UNTESTED RESEARCH DRAFT\n\n${composePrompt(s,model,lang)}\n`);
}
fs.writeFileSync(path.join(out,'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${[...sitemap].map(loc=>`<url><loc>${loc}</loc></url>`).join('\n')}</urlset>\n`);
fs.writeFileSync(path.join(out,'robots.txt'),'User-agent: *\nAllow: /\nSitemap: '+new URL('sitemap.xml',publicBase).href+'\n');
fs.writeFileSync(path.join(out,'build-info.json'),JSON.stringify({version:VERSION,...result.stats,showcases:styles.filter(s=>(s.illustrations||[]).some(x=>x.displayApproved)).length,independentShowcases:styles.filter(s=>getDisplaySample(s)?.kind==='same-input-showcase').length,provisionalMontagePreviews:styles.filter(s=>getDisplaySample(s)?.kind==='montage-derived-preview').length,proceduralStudies:styles.filter(s=>getDisplaySample(s)?.kind==='procedural-style-study').length,routes,status:'RESEARCH_PREVIEW_NOT_CONTENT_COMPLETE',deploymentStatus:'not-observed-by-build',siteBase},null,2));
console.log(`Built ${routes} static routes and ${styles.length*6} model/language text exports. ${result.stats.examples} validated examples and ${styles.filter(s=>(s.illustrations||[]).some(x=>x.displayApproved)).length} showcase styles. No third-party build dependencies.`);
