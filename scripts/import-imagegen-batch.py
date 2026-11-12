#!/usr/bin/env python3
"""Deterministically import source imagegen files as research-only same-scene previews.

Input JSON: {"batch_id":"...", "date":"YYYY-MM-DD", "records":[
 {"id":"catalog-id", "src":"/absolute/path.png", "generation_id":"uuid",
  "note_zh":"...", "note_en":"..."}]}

Images remain distinct from exact-prompt evidence. No API calls.
"""
import sys, json, hashlib, re
from pathlib import Path
from PIL import Image, ImageOps

root = Path(__file__).resolve().parent.parent

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save_img(src, dst, max_size, quality):
    with Image.open(src) as im:
        im=im.convert('RGB')
        w,h=im.size
        if not (w>100 and h>100): raise ValueError(f'image too small: {src}')
        resized=ImageOps.contain(im,max_size,Image.Resampling.LANCZOS)
        dst.parent.mkdir(parents=True,exist_ok=True)
        resized.save(dst,format='WEBP',quality=quality,method=6)
        return resized.size

def run(mpath):
    manifest=json.loads(Path(mpath).read_text(encoding='utf8'))
    catalog_p=root/'data/catalog.json'
    benchmark_p=root/'data/benchmark.json'
    catalog=json.loads(catalog_p.read_text(encoding='utf8'))
    bench=json.loads(benchmark_p.read_text(encoding='utf8'))
    by={s['id']:s for s in catalog}
    seen=set()
    before={s['id'] for s in catalog if any(e.get('displayApproved') for e in s.get('illustrations',[]))}
    source_hashes={e.get('sourceOutputSha256') for s in catalog for e in s.get('illustrations',[])}
    plan=[]
    for rec in manifest['records']:
        sid=rec['id'];src=Path(rec['src'])
        if sid not in by or sid in seen: raise ValueError(f'unknown/duplicate id {sid}')
        if not src.is_file(): raise FileNotFoundError(src)
        if not re.match(r'^\d{4}-\d{2}-\d{2}$',manifest['date']):raise ValueError('invalid date')
        sourcehash=sha(src)
        if sourcehash in source_hashes: raise ValueError(f'Image already assigned: {src}')
        if not rec.get('generation_id'):raise ValueError(f'missing generation ID for {sid}')
        seen.add(sid);source_hashes.add(sourcehash)
        plan.append((sid,src,sourcehash,rec))
    results=[]
    for sid,src,sourcehash,rec in plan:
        s=by[sid]
        base=f'examples/{sid}'
        full_rel=f'{base}.webp';thumb_rel=f'{base}.thumb.webp'
        # New AI examples are featured; prior procedural assets stay intact with new suffix.
        displaced=[]
        for old in s.get('illustrations',[]):
            if old.get('path')==full_rel:
                oldpath=root/'public'/full_rel
                oldthumb=root/'public'/thumb_rel
                if not (oldpath.exists() and oldthumb.exists()):raise ValueError('displaced asset missing')
                new_rel=f'{base}.procedural-v1.webp';new_thumb=f'{base}.procedural-v1.thumb.webp'
                if (root/'public'/new_rel).exists():raise ValueError('archive already exists')
                oldpath.rename(root/'public'/new_rel)
                oldthumb.rename(root/'public'/new_thumb)
                old['path']=new_rel;old['thumbnailPath']=new_thumb
                displaced.append(old)
        full=root/'public'/full_rel;thumb=root/'public'/thumb_rel
        w,h=save_img(src,full,(1200,900),88)
        tw,th=save_img(src,thumb,(480,360),79)
        if abs(w/h-4/3)>0.003:raise ValueError(f'not 4:3 for {sid}: {w}x{h}')
        new={
           'id':f'showcase-{sid}-20261020','styleId':sid,'accepted':False,'displayApproved':True,
           'path':full_rel,'thumbnailPath':thumb_rel,'width':w,'height':h,
           'thumbnailWidth':tw,'thumbnailHeight':th,'aspectRatio':'4:3',
           'model':'chatgpt','lang':'en','kind':'same-input-showcase',
           'sourceOutputSha256':sourcehash,'outputSha256':sha(full),'thumbnailSha256':sha(thumb),
           'promptVersion':s['version'],'originalId':'B00','originalSha256':bench['sha256'],
           'requestKind':'standalone-same-scene-generation','singleIndependentOutput':True,
           'environment':'ChatGPT image generation tool; same-scene reference, exact B00 edit provenance not independently verified',
           'generationId':rec['generation_id'],'date':manifest['date'],
           'reviewer':'assistant visual check','reviewNote':{'zh':rec['note_zh'],'en':rec['note_en']},
           'promptVerified':False,'actualSubmittedPromptCaptured':False,
           'sourceReferenceStatus':'visual-similarity-to-B00; not certified pixel-identical source edit'
        }
        # preserve any historical procedural record, but feature the new generated standalone asset
        s['illustrations']=[new]+s.get('illustrations',[])
        s['promptEvidence']='showcase-only'
        s['limits']['zh']='已补入同场景的 AI 独立展示图，但尚未取得与本站预设 Prompt 逐字一致的验证证据；不保证是 B00 原图的严格编辑。'
        s['limits']['en']='A separately generated same-scene showcase is available. The exact catalog prompt has not been verified, nor is the B00 edit input independently confirmed.'
        results.append({'style_id':sid,'generation_id':rec['generation_id'],'source_sha256':sourcehash,'path':full_rel,'image_sha256':sha(full),'prior_procedural_replaced':bool(displaced)})
    after={s['id'] for s in catalog if any(e.get('displayApproved') for e in s.get('illustrations',[]))}
    bench['illustratedStyles']=len(after)
    bench['note']={
      'zh':'B00 原图已接入。图库含独立 AI 风格展示图、拼图临时预览及程序化预览，按来源明确区分。独立图的精确 Prompt 与源图输入尚未逐条验证。',
      'en':'The B00 benchmark is integrated. Images include separate AI showcases, montage-derived provisional previews, and procedural studies; exact prompt and original-image input evidence remains unverified.'
    }
    catalog_p.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    benchmark_p.write_text(json.dumps(bench,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    evid=root/'evidence'/f"{manifest['batch_id']}.json";evid.parent.mkdir(parents=True,exist_ok=True)
    evid.write_text(json.dumps({'batch_id':manifest['batch_id'],'date':manifest['date'],'originalSha256':bench['sha256'],'newStyleCoverage':len(after-before),'stylePreviewUpgrades':len(before&set(seen)),'records':results,'disclaimer':'Independently generated example images; NOT exact prompt or proven B00 image edit tests.'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(f"{len(results)} AI images imported; newly illustrated {len(after-before)}; upgrades {len(before&set(seen))}; illustrated {len(after)}/{len(catalog)}")

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: import-imagegen-batch.py /path/manifest.json')
    run(sys.argv[1])
