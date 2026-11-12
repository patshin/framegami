/** Pure shared logic. No network access and no browser globals. */
export const VERSION = '0.4.0-image-work-in-progress';
export const MODELS = ['chatgpt', 'gemini', 'flux'];
export const LANGS = ['zh', 'en'];
export const MAX_IMPORT_BYTES = 2 * 1024 * 1024;
export const MAX_CUSTOM = 500;
export function escapeHTML(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
export function normalize(value) {
  return String(value ?? '').normalize('NFKC').toLowerCase().replace(/[-_]+/g, ' ').replace(/\s+/g, ' ').trim();
}
export function oneEditAway(a, b) {
  if (a === b) return true;
  if (Math.abs(a.length-b.length)>1) return false;
  let i=0,j=0,errors=0;
  while(i<a.length && j<b.length) {
    if(a[i]===b[j]) {i++;j++;continue;}
    if(++errors>1) return false;
    if(a.length>b.length) i++; else if(b.length>a.length) j++; else {
      if(a[i]===b[j+1]&&a[i+1]===b[j]) {i+=2;j+=2;} else {i++;j++;}
    }
  }
  return errors+(i<a.length||j<b.length?1:0)<=1;
}
export function queryTerms(value) {
  let q=normalize(value).replace(/watercolour/g,'watercolor').replace(/日系|日本风/g,'japan ').replace(/皮克斯风/g,'pixar ').replace(/像素风|像素画/g,'pixel ').replace(/水彩风|水彩画/g,'watercolor ').replace(/油画风/g,'oil ');
  return q.split(' ').filter(Boolean);
}
export function buildSearchIndex(styles, categories) {
  const cats=new Map(categories.map(x=>[x.id,x]));
  return styles.map(s=> {
    const c=cats.get(s.category);
    const family=c?.families[s.family]??[];
    return {s, name:normalize(Object.values(s.name).join(' ')), aliases:normalize(s.aliases.join(' ')),
      category:normalize([c?.zh,c?.en,...family,...s.tags].join(' ')),
      body:normalize(Object.values(s.technique).join(' '))};
  });
}
export function hasDisplaySample(style){return !!((style?.examples||[]).some(x=>x.accepted===true)||(style?.illustrations||[]).some(x=>x.displayApproved===true&&x.path));}
export const hasDisplayExample=hasDisplaySample;
export function getDisplaySample(style, model=null, lang=null){return (style?.examples||[]).find(x=>x.accepted===true&&x.promptVersion===style.version&&(!model||x.model===model)&&(!lang||x.lang===lang))||(style?.illustrations||[]).find(x=>x.displayApproved===true&&(!model||!x.model||x.model===model)&&(!lang||!x.lang||x.lang===lang))||(style?.illustrations||[]).find(x=>x.displayApproved===true)||null;}
export const getDisplayExample=getDisplaySample;

export function searchStyles(index, options={}) {
  const {q='',category='',family='',tag='',status='all',sort='editorial',lang='zh',favorites=null,treatment='all'}=options;
  const terms=queryTerms(q);
  const matches=[];
  for(const x of index) {
    const s=x.s;
    if(treatment==='restyle' && s.preservation==='reinterpret') continue;
    if(treatment==='lab' && s.preservation!=='reinterpret') continue;
    if(category && s.category!==category) continue;
    if(family && s.family!==family) continue;
    if(tag && !s.tags.includes(tag)) continue;
    if(status==='examples' && !s.examples.some(e=>e.accepted===true)) continue;
    if(status==='draft' && s.examples.some(e=>e.accepted===true)) continue;
    if(status==='images' && !hasDisplaySample(s)) continue;
    if(status==='missing-images' && hasDisplaySample(s)) continue;
    if(favorites && !favorites.has(s.id)) continue;
    let score=0, ok=true;
    for(const term of terms) {
      if(x.name.includes(term)) score+=9;
      else if(x.aliases.includes(term)) score+=7;
      else if(x.category.includes(term)) score+=4;
      else if(x.body.includes(term)) score+=1;
      else if(/^[a-z]{4,}$/.test(term)&& (x.name+' '+x.aliases).split(/[^a-z]+/).some(w=>oneEditAway(w,term))) score+=2;
      else {ok=false;break;}
    }
    if(ok) matches.push({s,score});
  }
  const collator=new Intl.Collator(lang==='zh'?'zh-Hans':'en',{numeric:true});
  matches.sort((a,b)=> sort==='name'?collator.compare(a.s.name[lang],b.s.name[lang]):sort==='category'?a.s.category.localeCompare(b.s.category)||a.s.order-b.s.order:(b.score-a.score||a.s.order-b.s.order));
  return matches.map(x=>x.s);
}
export function composePrompt(style, model='chatgpt', lang='en', options={}) {
  if(!style || !MODELS.includes(model)||!LANGS.includes(lang)) throw new Error('Invalid prompt request');
  const {background='keep',palette='style',detail='balanced',extra=''}=options;
  const changed=style.preservation==='reinterpret';
  const zh=lang==='zh';
  const identity=zh?'保留主体身份、年龄、发型、衣着特征、表情、物体数量及相互关系；不要添加原图没有的角色、文字、品牌或故事。':'Preserve identities, ages, hairstyles, clothing cues, expressions, object counts and relationships. Do not introduce new characters, text, brands or story events.';
  const structure=changed ? (zh?'本任务明确允许按下面的风格要求重构构图或展示容器；在此之外不要任意改变内容。':'This treatment explicitly permits the composition or presentation-container changes described below; do not make unrelated content changes.') : (zh?'保持原图主体位置、姿势、遮挡关系、镜头方向和画幅比例。若材质或抽象程度与微小细节保留冲突，优先保持主体轮廓与身份线索。':'Keep subject placement, poses, occlusion, camera direction and aspect ratio. Where material or abstraction conflicts with tiny details, prioritize recognizable silhouettes and identity cues.');
  const bg=(changed&&background==='keep')?(zh?'按目标改造方式统一处理人物、宠物与新的展示形式，不保留与新形式冲突的照片背景。':'Coherently treat people, pets and the requested presentation; do not retain a photographic background that conflicts with the specified transformation.'):background==='simplify'?(zh?'背景仍在原位置并保留主要建筑和物件，只减少琐碎细节；不要更换地点。':'Keep the background and its main architecture and objects in place, simplifying only minor detail; do not change the location.'):background==='blank'?(zh?'用户选择了背景留白：允许移除非主体背景，以统一浅色纸面代替。此选项会改变背景。':'The user explicitly chose a blank background: remove non-subject scenery and use a consistent pale ground. This option changes the background.'):(zh?'人物、宠物、物体和背景都采用同一套视觉语言，不能只给人脸套风格、其余仍是照片。':'Apply one coherent visual language to people, pets, objects and background; do not restyle only the face and leave an unrelated photographic setting.');
  const pal=palette==='source'?(zh?'在目标媒介允许范围内保留原图大色块关系；若风格严格限色，保留明暗与区域关系而非额外添加颜色。':'Retain source color relationships where the medium permits. For a strictly limited palette, preserve value and region relationships rather than adding colors.'):palette==='mono'?(zh?'将目标风格转为统一单色明暗版本，不改变场景结构；这是用户自定义变体。':'Use a unified monochrome value treatment without changing scene structure; this is a user-customized variant.'):(zh?'配色遵循该风格的媒介要求；避免为了好看而新增原图没有的事物。':'Let the target medium guide color; do not add new objects merely for visual appeal.');
  const det=detail==='rich'?(zh?'保留可读的次级细节，但不能牺牲媒介真实感和主体轮廓。':'Retain readable secondary details without sacrificing the medium or main silhouettes.'):detail==='simple'?(zh?'减少次要纹理，以清楚的形体和有限层次为主。':'Reduce secondary texture and prioritize clear forms and a limited tonal hierarchy.'):(zh?'细节有主次，重要身份特征清楚，背景不过度抢眼。':'Balance detail: keep identifying features clear and the background subordinate.');
  const ext=String(extra).trim().slice(0,8000);
  if(model==='flux') return [zh?`将提供图片的视觉表现改为「${style.name.zh}」，不是生成另一张内容无关的图片。`:`Change the provided image's visual treatment to ${style.name.en}; do not create an unrelated scene.`,style.technique[lang],identity,structure,bg,pal,det,zh?`避免：${style.avoid.zh}`:`Avoid: ${style.avoid.en}`,ext].filter(Boolean).join('\n\n');
  if(model==='gemini') return [zh?`使用上传图片作为内容参考，将整幅图重新绘制为「${style.name.zh}」。`:`Using the uploaded image as the content reference, redraw the entire image as ${style.name.en}.`,zh?`保持内容\n${identity}\n${structure}`:`CONTENT TO PRESERVE\n${identity}\n${structure}`,zh?`具体视觉变化\n${style.technique.zh}\n${bg}\n${pal}\n${det}`:`VISUAL CHANGES\n${style.technique.en}\n${bg}\n${pal}\n${det}`,zh?`限制\n${style.avoid.zh}`:`CONSTRAINTS\n${style.avoid.en}`,ext?(zh?'用户额外要求\n':'ADDITIONAL USER DIRECTION\n')+ext:'',zh?'输出一张完整图像，不输出解释、拼图或多版本对照。':'Return one complete image, not an explanation, contact sheet or multi-version comparison.'].filter(Boolean).join('\n\n');
  return [zh?`使用上传图片作为唯一内容参考，把整幅画面重新绘制为「${style.name.zh}」。这是图像编辑／风格迁移，不是基于图片描述重新创作无关场景。`:`Use the uploaded image as the sole content reference and redraw the whole scene as ${style.name.en}. This is image editing and style transfer, not a new scene loosely inspired by a description.`,identity+'\n'+structure,zh?`视觉语言\n${style.technique.zh}`:`VISUAL LANGUAGE\n${style.technique.en}`,bg+'\n'+pal+'\n'+det,zh?`避免的偏差\n${style.avoid.zh}`:`FAILURE MODES TO AVOID\n${style.avoid.en}`,ext?(zh?'用户额外要求\n':'ADDITIONAL USER DIRECTION\n')+ext:'',changed?(zh?'输出一张符合指定展示方式的完整作品；只有该条目明确要求的边框、盒子或版式可以出现，不加额外标题、水印或多版本比较。':'Output one coherent work in the specified presentation. Only frames, boxes or layouts explicitly required by this recipe are allowed; add no unrelated titles, watermarks or variant comparisons.'):(zh?'输出一张完整、协调的作品，不添加标题、水印、边框、比较拼图或多版本。若原图本来有必要的文字，不擅自改写其含义。':'Output one complete coherent artwork without added titles, watermarks, frames, comparison montages or variants. Where essential text already exists in the source, do not invent a different meaning.')].filter(Boolean).join('\n\n');
}
export function validateImport(data, knownIds=new Set()) {
  if(!data||typeof data!=='object'||Array.isArray(data)) throw new Error('Expected an Framegami backup object / 需要 Framegami 备份对象');
  // A recipe exported by this application must also round-trip through Import.
  if(data.schema==='iro-recipe/v1') {
    if(typeof data.prompt!=='string'||!data.prompt.trim()||data.prompt.length>20000) throw new Error('Invalid recipe prompt / 提示词无效');
    const name=typeof data.name==='string'?data.name:(data.name?.[LANGS.includes(data.lang)?data.lang:'en']||data.name?.zh||data.name?.en);
    if(typeof name!=='string'||!name.trim()||name.length>120) throw new Error('Invalid recipe name / 名称无效');
    const key=typeof data.id==='string'&&/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(data.id)?data.id.slice(0,60):'imported';
    return validateImport({schema:'iro-backup/v1',favorites:[],custom:[{id:'custom-recipe-'+key,name,prompt:data.prompt,model:data.model,lang:data.lang,tags:data.tags}]},knownIds);
  }
  if(data.schema!=='iro-backup/v1') throw new Error('Unsupported backup version / 不支持的备份版本');
  if(!Array.isArray(data.favorites)||!Array.isArray(data.custom)) throw new Error('Missing arrays / 备份字段不完整');
  if(data.custom.length>MAX_CUSTOM||data.favorites.length>10000) throw new Error('Backup too large / 条目过多');
  const custom=data.custom.map((x,i)=> {
    if(!x||typeof x!=='object'||typeof x.name!=='string'||!x.name.trim()||x.name.length>120||typeof x.prompt!=='string'||!x.prompt.trim()||x.prompt.length>20000) throw new Error(`Invalid custom recipe ${i+1} / 自定义条目无效`);
    return {id:typeof x.id==='string'&&/^custom-[\w-]{1,80}$/.test(x.id)?x.id:`custom-import-${i}`,name:x.name.trim(),prompt:x.prompt,model:MODELS.includes(x.model)?x.model:'chatgpt',lang:LANGS.includes(x.lang)?x.lang:'en',createdAt:typeof x.createdAt==='string'?x.createdAt.slice(0,40):'',tags:normalizeTags(x.tags)};
  });
  const ids=new Set();
  for(const x of custom) {if(ids.has(x.id)) throw new Error('Duplicate custom ID / 自定义编号重复');ids.add(x.id);}
  return {favorites:[...new Set(data.favorites.filter(x=>typeof x==='string'&&knownIds.has(x)))],custom};
}
export function mergeBackup(existing, incoming) {
  const m=new Map(existing.custom.map(x=>[x.id,x]));
  for(const x of incoming.custom) {
    if(m.has(x.id) && (m.get(x.id).prompt!==x.prompt||m.get(x.id).name!==x.name)) {
      let i=1,base=x.id.slice(0,68),id=base+'-copy'; while(m.has(id)) id=base+'-copy-'+i++;
      m.set(id,{...x,id});
    } else m.set(x.id,x);
  }
  if(m.size>MAX_CUSTOM) throw new Error('Too many custom recipes / 自定义条目超过上限');
  return {favorites:[...new Set([...existing.favorites,...incoming.favorites])],custom:[...m.values()]};
}
export function safeHTTPS(url) {
  try {const u=new URL(url);return u.protocol==='https:'&& !u.username&&!u.password?u.href:null;} catch {return null;}
}
export function normalizeCompare(ids, knownIds) {
  return [...new Set(ids.filter(x=>typeof x==='string'&&knownIds.has(x)))].slice(0,4);
}
export function readQuery(search) {
  const p=new URLSearchParams(search);
  return {q:(p.get('q')||'').slice(0,300),category:p.get('category')||'',family:p.get('family')||'',tag:p.get('tag')||'',treatment:['all','restyle','lab'].includes(p.get('treatment'))?p.get('treatment'):'all',status:['all','draft','examples','images','missing-images'].includes(p.get('status'))?p.get('status'):'all',sort:['editorial','name','category'].includes(p.get('sort'))?p.get('sort'):'editorial'};
}

/** User tags are plain text, bounded and never interpreted as markup. */
export function normalizeTags(value) {
  const list=Array.isArray(value)?value:typeof value==='string'?value.split(/[,，;；]/):[];
  return [...new Set(list.filter(x=>typeof x==='string').map(x=>x.trim().slice(0,40)).filter(Boolean))].slice(0,12);
}
/** Select only evidence for the requested model AND prompt language/version. */
export function getAcceptedExample(style, model=null, lang=null) {
  return (style?.examples||[]).find(x=>x.accepted===true&&x.promptVersion===style.version&&(!model||x.model===model)&&(!lang||x.lang===lang))||null;
}

export function normalizePromptOptions(value={}) {
  const v=value&&typeof value==='object'&&!Array.isArray(value)?value:{};
  return {background:['keep','simplify','blank'].includes(v.background)?v.background:'keep',palette:['style','source','mono'].includes(v.palette)?v.palette:'style',detail:['balanced','rich','simple'].includes(v.detail)?v.detail:'balanced',extra:typeof v.extra==='string'?v.extra.slice(0,8000):''};
}
export function exportPromptCollection(entries, model='chatgpt', lang='en') {
  if(!MODELS.includes(model)||!LANGS.includes(lang))throw new Error('Invalid export target');
  const head=lang==='zh'?'# Framegami｜图生图风格图鉴 — 提示词选集\n\n每个条目的验证状态单独标注。请将自己的同一张原图重新上传至目标工具；本站不代传图片。':'# Framegami Style Atlas — Prompt collection\n\nValidation is recorded per entry. Upload the same original to your chosen model; this site does not transfer images.';
  return head+'\n\n'+entries.map(s=>`## ${s.name[lang]}\n\nID: ${s.id} · Prompt v${s.version} · ${model} / ${lang}\nStatus: ${getAcceptedExample(s,model,lang)?'SINGLE_EXAMPLE_AVAILABLE':'UNTESTED_TEXT_ADAPTATION'}\n\n${composePrompt(s,model,lang)}\n`).join('\n---\n\n');
}
export function readComparisonQuery(search, knownIds) {
  const p=new URLSearchParams(search);
  return {ids:p.has('ids')?normalizeCompare(p.get('ids').split(','),knownIds):null,model:MODELS.includes(p.get('model'))?p.get('model'):null,lang:LANGS.includes(p.get('pl'))?p.get('pl'):null};
}
