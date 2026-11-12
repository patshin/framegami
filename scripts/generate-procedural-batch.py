from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw
import numpy as np, json,hashlib, pathlib, datetime
R=pathlib.Path(__file__).resolve().parents[1]
catp=R/'data/catalog.json'; bp=R/'data/benchmark.json'
cat=json.loads(catp.read_text()); bench=json.loads(bp.read_text())
base=Image.open(R/'public'/bench['path']).convert('RGB').resize((1200,900))
A=np.array(base).astype(np.float32)/255
lum=np.dot(A,[.299,.587,.114]); rng=np.random.default_rng(440)
styles=['photocopy-zine','stencil-cut','bleach-bypass','salt-print','platinum-print','pinhole','split-tone-duotone','watercolor-negative','lithograph-crayon','aquatint']
def save_image(a):return Image.fromarray(np.uint8(np.clip(a,0,1)*255),'RGB')
notes={
'photocopy-zine':('高反差黑白复印颗粒与复印机噪点','High contrast photocopy toner and dither texture'),
'stencil-cut':('限色剪贴模板及清晰套色色块','Limited stencil color and crisp masked shapes'),
'bleach-bypass':('降低饱和度并增强反差的跳漂摄影效果','Reduced saturation and higher contrast bleach-bypass study'),
'salt-print':('盐纸印相的暖棕与柔和暗部','Warm sepia salt-print tonal treatment'),
'platinum-print':('铂金印相的柔和深灰阶','Smooth platinum monochrome tonal scale'),
'pinhole':('针孔成像的边缘暗角与柔焦','Soft focus, vignette, and lensless pinhole treatment'),
'split-tone-duotone':('明暗两色摄影双色调','Duotone shadow/highlight photographic palette'),
'watercolor-negative':('以留白轮廓与叠层色块表现负形水彩','Negative-space watercolor inspired layered color reduction'),
'lithograph-crayon':('石版蜡笔感颗粒排点与柔和印刷质感','Crayon lithograph-inspired granular print marks'),
'aquatint':('水纹蚀刻版的分级灰调与蚀刻颗粒','Aquatint-inspired granular tonal areas')}
for i,sid in enumerate(styles):
 if sid=='photocopy-zine':
  noise=rng.normal(0,.06,lum.shape); q=np.clip((lum+noise-.48)*4+.5,0,1);q=(q>.52).astype(float);o=np.repeat(q[:,:,None],3,axis=2)
 elif sid=='stencil-cut':
  q=np.floor(lum*4)/3; pal=np.array([[.12,.19,.25],[.34,.49,.48],[.85,.65,.40],[.97,.90,.72]]);o=pal[np.clip((q*3).astype(int),0,3)]
 elif sid=='bleach-bypass':
  gray=np.repeat(lum[:,:,None],3,axis=2);o=np.clip(((A*.44+gray*.56)-.5)*1.38+.5,0,1)
 elif sid=='salt-print':
  o=np.stack([.95*lum+.03,.77*lum+.09,.58*lum+.13],axis=2);o=np.clip(o*.91+.09,0,1)
 elif sid=='platinum-print':
  v=np.clip(lum**.92,0,1);o=np.stack([v*.94+.025,v*.935+.03,v*.90+.05],axis=2)
 elif sid=='pinhole':
  im=base.filter(ImageFilter.GaussianBlur(2.4));y,x=np.ogrid[-1:1:900j,-1:1:1200j];v=np.maximum(.48,1-.42*(x*x+y*y));o=np.asarray(im)/255*v[:,:,None]
 elif sid=='split-tone-duotone':
  t=lum[:,:,None];o=(1-t)*np.array([.09,.22,.37])+t*np.array([.95,.77,.56])
 elif sid=='watercolor-negative':
  q=np.round(lum*6)/6;mask=(lum>.78)[:,:,None];o=np.where(mask,.98,A*.78+.22*q[:,:,None]);o=np.clip(o,0,1)
 elif sid=='lithograph-crayon':
  grain=rng.normal(0,.052,lum.shape);o=np.clip(A*.72+lum[:,:,None]*.28+grain[:,:,None],0,1)
 elif sid=='aquatint':
  grain=rng.normal(0,.06,lum.shape);v=np.clip(np.round(lum*7)/7+grain,0,1);o=np.stack([v*.94+.03,v*.87+.06,v*.77+.1],axis=2)
 img=save_image(o);thumb=img.resize((480,360),Image.Resampling.LANCZOS)
 full=R/'public/examples'/f'{sid}.webp';small=R/'public/examples'/f'{sid}.thumb.webp';full.parent.mkdir(exist_ok=True)
 img.save(full,'WEBP',quality=86,method=6);thumb.save(small,'WEBP',quality=78,method=6)
 def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
 s=next(x for x in cat if x['id']==sid);assert not s.get('illustrations'),sid
 zh,en=notes[sid]
 s['illustrations']=[{'id':'proc-'+sid,'styleId':sid,'kind':'procedural-style-study','accepted':False,'displayApproved':True,'promptVerified':False,'path':f'examples/{sid}.webp','thumbnailPath':f'examples/{sid}.thumb.webp','width':1200,'height':900,'thumbnailWidth':480,'thumbnailHeight':360,'aspectRatio':'4:3','outputSha256':h(full),'thumbnailSha256':h(small),'sourceOutputSha256':h(full),'originalId':'B00','originalSha256':bench['sha256'],'referenceAssociation':'deterministic processing of exact B00 file','model':'local-procedural','lang':'en','generationId':'proc-batch85-'+sid,'requestKind':'deterministic-computer-graphics','singleIndependentOutput':False,'promptVersion':s['version'],'environment':'Python Pillow and NumPy, no image-generation model','date':'2026-11-02','reviewer':'automated visual inspection pending','toolSourcePath':'scripts/generate-procedural-batch.py','reviewNote':{'zh':zh,'en':en}}]
bench['illustratedStyles']=sum(bool(x.get('illustrations')) for x in cat)
catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n');bp.write_text(json.dumps(bench,ensure_ascii=False,indent=2)+'\n')
print('styles:',bench['illustratedStyles'])
