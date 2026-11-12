#!/usr/bin/env python3
"""Import IRO image packs by canonical style ID. No network/API usage.

python3 scripts/import-image-pack.py ASSETS.zip --dry-run
python3 scripts/import-image-pack.py ASSETS.zip [--upgrade-preview]
"""
import argparse, hashlib, io, json, re, stat, sys, zipfile
from datetime import date
from pathlib import Path, PurePosixPath
from PIL import Image, ImageOps, ImageFile, ImageChops, ImageStat

ROOT=Path(__file__).resolve().parents[1]
MAX_PACK_BYTES=400*1024*1024
MAX_MEMBER_BYTES=30*1024*1024
MAX_TOTAL_UNCOMPRESSED=700*1024*1024
MAX_PIXELS=40_000_000
IMG_EXTS={'.png','.jpg','.jpeg','.webp'}
Image.MAX_IMAGE_PIXELS=MAX_PIXELS
ImageFile.LOAD_TRUNCATED_IMAGES=False

def digest(data): return hashlib.sha256(data).hexdigest()
def safe_path(s):
    if not isinstance(s,str) or not s or '\\' in s or '\x00' in s or s.startswith('/'):
        raise ValueError('Unsafe path')
    parts=s.split('/')
    if any(p in ('','.','..') for p in parts):raise ValueError('Unsafe path: '+s)
    return s

def read_image(data,name):
    if len(data)>MAX_MEMBER_BYTES:raise ValueError('Oversized image: '+name)
    with Image.open(io.BytesIO(data)) as img:
        if img.width<200 or img.height<200 or img.width*img.height>MAX_PIXELS:
            raise ValueError('Invalid image dimensions: '+name)
        img.load()
        return ImageOps.exif_transpose(img).convert('RGB')

def webp(image,bounds,quality):
    output=ImageOps.contain(image,bounds,Image.Resampling.LANCZOS)
    buf=io.BytesIO();output.save(buf,'WEBP',quality=quality,method=6)
    return buf.getvalue(),output.size

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('pack')
    ap.add_argument('--dry-run',action='store_true')
    ap.add_argument('--upgrade-preview',action='store_true',help='Replace active montage/procedural preview with independent AI image, archiving old files')
    args=ap.parse_args()
    archive=Path(args.pack)
    if not archive.is_file() or archive.stat().st_size>MAX_PACK_BYTES:raise ValueError('Missing or oversized pack')
    catalog_path=ROOT/'data/catalog.json';bench_path=ROOT/'data/benchmark.json'
    catalog=json.loads(catalog_path.read_text('utf-8'))
    bench=json.loads(bench_path.read_text('utf-8'))
    styles={s['id']:s for s in catalog}
    used={i.get('sourceOutputSha256') for s in catalog for i in s.get('illustrations',[])}
    used.discard(None)
    with zipfile.ZipFile(archive) as z:
        members=z.infolist()
        if len(members)>260:raise ValueError('Too many archive members')
        names=set();total=0
        for entry in members:
            n=safe_path(entry.filename)
            if n in names:raise ValueError('Duplicate archive name: '+n)
            names.add(n)
            if stat.S_ISLNK(entry.external_attr>>16):raise ValueError('Symlink not permitted')
            total+=entry.file_size
            if total>MAX_TOTAL_UNCOMPRESSED or entry.file_size>MAX_MEMBER_BYTES:raise ValueError('Excessive archive expansion')
        if 'manifest.json' not in names or z.getinfo('manifest.json').file_size>1_000_000:
            raise ValueError('Missing/oversized manifest.json')
        m=json.loads(z.read('manifest.json'))
        batch=m.get('batch_id','')
        if m.get('schema')!='iro-image-pack-v1' or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{2,80}',batch):
            raise ValueError('Invalid pack schema or batch_id')
        run_date=m.get('date','');date.fromisoformat(run_date)
        evidence_dir=ROOT/'evidence/imported-packs'/batch
        if evidence_dir.exists():raise ValueError('Batch ID already imported; choose a new ID')
        records=m.get('images')
        if not isinstance(records,list) or not (1<=len(records)<=120):
            raise ValueError('images must contain 1–120 records')
        plan=[];seen=set()
        for rec in records:
            if not isinstance(rec,dict):raise ValueError('Invalid record')
            sid=rec.get('style_id')
            if not isinstance(sid,str) or sid not in styles or sid in seen:raise ValueError('Unknown/duplicate style_id')
            seen.add(sid)
            source_type=rec.get('source_type')
            if source_type not in ('independent-ai','montage-crop'):raise ValueError('Unsupported source_type')
            if rec.get('prompt_verified') is True or rec.get('accepted') is True:raise ValueError('A style preview cannot claim prompt validation')
            if rec.get('model') not in ('chatgpt','gemini','flux') or rec.get('language') not in ('zh','en'):
                raise ValueError('Explicit supported model/language required')
            gid=rec.get('generation_id','')
            if not isinstance(gid,str) or not (1<=len(gid)<=150):raise ValueError('Generation ID required')
            for field in ('note_zh','note_en'):
                if not isinstance(rec.get(field),str) or not (2<=len(rec[field])<=800):
                    raise ValueError('Bilingual review notes required')
            file=safe_path(rec.get('file'))
            if not file.startswith('images/') or Path(file).suffix.lower() not in IMG_EXTS or file not in names:
                raise ValueError('Invalid/missing image: '+str(file))
            raw=z.read(file);rawhash=digest(raw)
            if rawhash in used:raise ValueError('One source image cannot be reused for multiple styles')
            used.add(rawhash)
            img=read_image(raw,file)
            full,(w,h)=webp(img,(1200,900),87)
            thumb,(tw,th)=webp(img,(480,360),78)
            old=next((i for i in styles[sid].get('illustrations',[]) if i.get('displayApproved')),None)
            if old and not (args.upgrade_preview and source_type=='independent-ai' and old.get('kind') in ('procedural-style-study','montage-derived-preview')):
                raise ValueError('Style already illustrated: '+sid)
            extra={};montage=None
            if source_type=='montage-crop':
                mp=safe_path(rec.get('montage_file'))
                if not mp.startswith('montages/') or Path(mp).suffix.lower() not in IMG_EXTS or mp not in names:
                    raise ValueError('Original montage missing')
                montage=z.read(mp)
                original=read_image(montage,mp)
                box=rec.get('crop_box')
                if not isinstance(box,list) or len(box)!=4 or not all(type(n)==int and n>=0 for n in box):
                    raise ValueError('Invalid crop_box')
                x0,y0,x1,y1=box
                if not (x0<x1<=original.width and y0<y1<=original.height):raise ValueError('Crop outside montage')
                target=original.crop((x0,y0,x1,y1))
                if target.size!=img.size:target=target.resize(img.size,Image.Resampling.LANCZOS)
                if max(ImageStat.Stat(ImageChops.difference(target,img)).mean)>24:
                    raise ValueError('Image does not match claimed source montage crop')
                if not isinstance(rec.get('source_panel_label'),str) or not rec['source_panel_label'].strip():raise ValueError('Missing montage panel label')
                extra={'cropBox':box,'sourcePanelLabel':rec['source_panel_label'][:120]}
            # No mutation before every record has passed validation.
            plan.append(dict(sid=sid,rec=rec,raw=raw,rawhash=rawhash,full=full,thumb=thumb,w=w,h=h,tw=tw,th=th,old=old,extra=extra,montage=montage))
    for p in plan:
        sid=p['sid'];old=p['old']
        for fn in (f'{sid}.webp',f'{sid}.thumb.webp'):
            target=ROOT/'public/examples'/fn
            if target.exists() and not old:raise FileExistsError(target)
        if old:
            for field,suffix in [('path','.webp'),('thumbnailPath','.thumb.webp')]:
                oldpath=old.get(field)
                if oldpath in (f'examples/{sid}.webp',f'examples/{sid}.thumb.webp'):
                    dest=ROOT/'public/examples'/f'{sid}.archived-{batch}-{old["kind"]}{suffix}'
                    if dest.exists():raise FileExistsError(dest)
    print(f'VALID: {len(plan)} records; existing visual coverage {sum(any(i.get("displayApproved") for i in s.get("illustrations",[])) for s in catalog)}/213')
    if args.dry_run:
        print('DRY RUN — no project files changed')
        return
    # Save original file bytes separately from WebP derivatives for later audit.
    evidence_dir.mkdir(parents=True)
    for p in plan:
        sid=p['sid'];rec=p['rec'];old=p['old'];style=styles[sid]
        oldlist=style.get('illustrations',[])
        if old:
            old['displayApproved']=False
            for field,suffix in [('path','.webp'),('thumbnailPath','.thumb.webp')]:
                rel=old.get(field)
                if rel in (f'examples/{sid}.webp',f'examples/{sid}.thumb.webp'):
                    target=ROOT/'public/examples'/f'{sid}.archived-{batch}-{old["kind"]}{suffix}'
                    (ROOT/'public'/rel).rename(target)
                    old[field]=f'examples/{target.name}'
        rawpath=evidence_dir/f'{sid}-original{Path(rec["file"]).suffix.lower()}'
        rawpath.write_bytes(p['raw'])
        fullpath=ROOT/'public/examples'/f'{sid}.webp'
        thumbpath=ROOT/'public/examples'/f'{sid}.thumb.webp'
        fullpath.write_bytes(p['full']);thumbpath.write_bytes(p['thumb'])
        illustration=dict(id=f'imported-{batch}-{sid}',styleId=sid,kind='same-input-showcase' if rec['source_type']=='independent-ai' else 'montage-derived-preview',
          accepted=False,displayApproved=True,promptVerified=False,
          path=f'examples/{sid}.webp',thumbnailPath=f'examples/{sid}.thumb.webp',
          width=p['w'],height=p['h'],thumbnailWidth=p['tw'],thumbnailHeight=p['th'],aspectRatio=f'{p["w"]}:{p["h"]}',
          sourceOutputSha256=p['rawhash'],sourceImagePath=str(rawpath.relative_to(ROOT)),
          outputSha256=digest(p['full']),thumbnailSha256=digest(p['thumb']),
          promptVersion=style['version'],model=rec['model'],lang=rec['language'],
          generationId=rec['generation_id'],date=run_date,reviewer='batch handoff; human visual review required',
          environment=str(rec.get('environment','image-generation model; original image input not independently verified'))[:400],
          reviewNote={'zh':rec['note_zh'],'en':rec['note_en']},
          singleIndependentOutput=rec['source_type']=='independent-ai',actualSubmittedPromptCaptured=False,
          sourceReferenceStatus='same-scene illustration, not exact image-edit proof')
        if rec['source_type']=='independent-ai':
            illustration.update(requestKind='standalone-same-scene-generation',originalId='B00',originalSha256=bench['sha256'])
        else:
            montagepath=evidence_dir/f'{sid}-montage{Path(rec["montage_file"]).suffix.lower()}'
            montagepath.write_bytes(p['montage'])
            illustration.update(requestKind='crop-from-montage',originalId=None,originalSha256=None,
              sourceMontagePath=str(montagepath.relative_to(ROOT)),sourceMontageSha256=digest(p['montage']),
              sourceCropPath=str(rawpath.relative_to(ROOT)),**p['extra'])
        style['illustrations']=[illustration]+oldlist
        style['promptEvidence']='showcase-only'
        style['limits']['zh']='本条展示图未经过当前 Prompt 逐字复现验证；请以具体媒介特征为参考。'
        style['limits']['en']='This showcase is not a strict reproduction test of the current prompt; use it as a visual technique reference.'
    bench['illustratedStyles']=sum(any(i.get('displayApproved') for i in s.get('illustrations',[])) for s in catalog)
    catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    bench_path.write_text(json.dumps(bench,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (evidence_dir/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('IMPORTED',len(plan),'— visual coverage',bench['illustratedStyles'],'/213')
    print('Run: npm run check')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('IMAGE PACK IMPORT FAILED:',exc,file=sys.stderr)
        sys.exit(1)
