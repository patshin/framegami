#!/usr/bin/env python3
"""Deterministic, disclosed B00 processing studies for ten visual techniques.

These are illustrative algorithmic studies, NOT model outputs and NOT proof of
style-prompt reproducibility. Run only when the ten styles have no illustrations.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import cv2
from scipy.spatial import Delaunay
from skimage.segmentation import slic, find_boundaries

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'data/catalog.json'; BENCH=ROOT/'data/benchmark.json'
styles=json.loads(CAT.read_text(encoding='utf-8'))
bench=json.loads(BENCH.read_text(encoding='utf-8'))
original=ROOT/'public'/bench['path']
assert hashlib.sha256(original.read_bytes()).hexdigest()==bench['sha256'],'B00 source mismatch'
size=(1200,900)
base=Image.open(original).convert('RGB').resize(size,Image.Resampling.LANCZOS)
arr=np.asarray(base).copy()
rng=np.random.default_rng(20261103)
H,W=arr.shape[:2]

def hash_file(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def fimage(a):return Image.fromarray(np.uint8(np.clip(a,0,255)), 'RGB')

def poster(a,div=32):return np.uint8(np.clip((a//div)*div+div//2,0,255))

def contour(a,low=60,high=130):
    gray=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)
    e=cv2.Canny(gray,low,high)
    return cv2.dilate(e,np.ones((2,2),np.uint8),iterations=1)

def cartoon(a,div=42,palette=None):
    small=cv2.resize(a,(600,450),interpolation=cv2.INTER_AREA)
    for _ in range(2):small=cv2.bilateralFilter(small,7,47,47)
    smooth=cv2.resize(small,(W,H),interpolation=cv2.INTER_LINEAR)
    q=poster(smooth,div)
    e=contour(a,80,160)
    q[e>0]=[45,38,35] if palette is None else palette
    return q

def triangles(a,step=33):
    coords=[]
    for y in range(0,H+1,step):
        for x in range(0,W+1,step):
            px=min(W-1,max(0,x+int(rng.integers(-8,9))))
            py=min(H-1,max(0,y+int(rng.integers(-8,9))))
            coords.append((px,py))
    coords +=[(0,0),(W-1,0),(W-1,H-1),(0,H-1)]
    pts=np.array(coords)
    tris=Delaunay(pts)
    image=Image.new('RGB',size,(240,231,213));d=ImageDraw.Draw(image)
    for tri in tris.simplices:
        xy=pts[tri];cx=int(xy[:,0].mean());cy=int(xy[:,1].mean())
        col=poster(a[cy,cx].reshape(1,1,3),24)[0,0]
        d.polygon([tuple(int(v) for v in p) for p in xy],fill=tuple(int(v) for v in col),outline=tuple(max(0,int(v)*7//8) for v in col))
    return np.asarray(image).copy()

def embossed_wood(a):
    gray=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY).astype(float)/255
    gy,gx=np.gradient(gray)
    relief=np.clip(.60+3.4*gx-2.7*gy,0,1)
    yy,xx=np.indices((H,W))
    grain=.027*np.sin(yy*.16+np.sin(xx*.019)*3)+.015*np.sin(yy*.048+xx*.010)
    v=np.clip(.62*gray+.38*relief+grain,0,1)
    out=np.stack([205*v+27,150*v+26,91*v+17],axis=-1)
    edges=contour(a,75,160)>0
    out[edges]=out[edges]*.48
    return out.astype('uint8')

def wild_color(a):
    # Saturated non-natural complementary color mapping, retaining shapes.
    lab=cv2.cvtColor(a,cv2.COLOR_RGB2LAB)
    h=cv2.cvtColor(a,cv2.COLOR_RGB2HSV)
    h[:,:,0]=np.uint8((h[:,:,0].astype(int)*1.36+31)%180)
    h[:,:,1]=np.uint8(np.clip(h[:,:,1].astype(float)*1.8+30,0,255))
    altered=cv2.cvtColor(h,cv2.COLOR_HSV2RGB)
    q=poster(cv2.bilateralFilter(altered,7,50,50),28)
    e=contour(a,100,190)
    q[e>0]=q[e>0]*.65
    return q

def fresco(a):
    t=cv2.GaussianBlur(a,(0,0),1.3).astype(float)
    light=np.dot(t,[.30,.59,.11])
    t=.69*t+.31*light[:,:,None]
    t=.90*t+.10*np.array([219,190,145])[None,None,:]
    noise=rng.normal(0,7,(H,W,1))
    y,x=np.indices((H,W))
    mineral=5*np.sin(x*.046+y*.022)+4*np.sin(y*.12-x*.005)
    t+=noise+mineral[:,:,None]
    return t

def kawaii(a):
    q=cartoon(a,47)
    q=np.clip(q.astype(float)*.68+np.array([255,240,237])[None,None,:]*.32,0,255).astype('uint8')
    # Subtle stationery-like ink outline and corner motifs, not presented as a true redraw.
    im=Image.fromarray(q); d=ImageDraw.Draw(im)
    for x,y,r in [(42,72,12),(1125,102,9),(1140,815,13),(60,830,10)]:
        for angle in range(0,360,72):
            th=np.deg2rad(angle);cx=x+int(np.cos(th)*r);cy=y+int(np.sin(th)*r)
            d.ellipse((cx-4,cy-4,cx+4,cy+4),fill=(244,167,171))
        d.ellipse((x-5,y-5,x+5,y+5),fill=(249,215,105))
    return np.asarray(im)

def silhouette(a):
    gray=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)
    val=cv2.GaussianBlur(gray,(0,0),2)
    # Paper-cut masses and thin internal cutouts keep subject context legible.
    binary=(val>140).astype('uint8')
    texture=np.stack([np.where(binary,244,38),np.where(binary,229,43),np.where(binary,208,51)],axis=-1).astype('uint8')
    edges=contour(a,55,130)>0
    texture[edges]=[33,38,44]
    return texture

def rubber(a):
    v=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)
    v=cv2.medianBlur(v,5)
    tone=np.digitize(v,[65,120,180,220])
    levels=np.array([35,78,128,187,241],np.uint8)[tone]
    e=contour(a,55,115)
    out=np.stack([np.clip(levels.astype(float)*1.05+11,0,255),np.clip(levels.astype(float)*.98+7,0,255),np.clip(levels.astype(float)*.83+4,0,255)],axis=-1).astype(np.uint8)
    out[e>0]=[24,22,20]
    return out

def mosaic(a):
    im=Image.new('RGB',size,(70,69,65));d=ImageDraw.Draw(im)
    step=10
    for y in range(0,H,step):
        for x in range(0,W,step):
            tile=a[y:min(H,y+step),x:min(W,x+step)]
            col=tuple(int(v) for v in tile.mean(axis=(0,1)))
            inset=int(rng.integers(1,3))
            d.rectangle((x+inset,y+inset,min(W-1,x+step-2),min(H-1,y+step-2)),fill=col)
            d.line((x+inset,y+inset,min(W-1,x+step-2),y+inset),fill=tuple(min(255,k+17) for k in col))
    return np.asarray(im)

def torn_paper(a):
    # Region-quantized colored paper with irregular torn edges.
    sm=cv2.resize(a,(600,450),interpolation=cv2.INTER_AREA)
    lab=slic(sm,n_segments=1100,compactness=14,start_label=0,channel_axis=-1)
    out=np.zeros_like(sm)
    avg=np.array([sm[lab==i].mean(axis=0) for i in range(lab.max()+1)])
    out[:]=np.uint8(avg[lab])
    bound=find_boundaries(lab,mode='thick')
    out[bound]=np.uint8(.45*out[bound]+.55*np.array([248,239,220]))
    t=cv2.resize(out,(W,H),interpolation=cv2.INTER_NEAREST)
    grain=rng.normal(0,3,(H,W,1))
    return np.clip(t.astype(float)+grain,0,255)

def soft_chibi(a):
    # Controlled mild face-area enlargement; reference study, not true character rigging.
    smooth=cartoon(a,48)
    xx,yy=np.meshgrid(np.arange(W),np.arange(H))
    cx,cy=556,264
    r=np.sqrt(((xx-cx)/225)**2+((yy-cy)/246)**2)
    factor=np.where(r<1,np.maximum(.77,1-.23*(1-r)**2),1)
    mx=cx+(xx-cx)*factor;my=cy+(yy-cy)*factor
    warped=cv2.remap(smooth,mx.astype('float32'),my.astype('float32'),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    return np.clip(warped*.84+np.array([252,226,216])[None,None,:]*.16,0,255)

process={
 'chibi-proportions':(soft_chibi,'Q版形状简化、面部局部放大；不等同于完整角色重绘','Chibi-inspired cartoonization and localized face enlargement; not a model redraw'),
 'ps1-lowpoly':(triangles,'明显三角面网格与有限色阶，近似早期多边形游戏画面','Triangulated color planes evoke early low-polygon game visuals'),
 'wood-carving':(embossed_wood,'木色明暗浮雕、刻痕与木纹示意','Wood-toned embossed relief with carving-like contours'),
 'fauvist':(wild_color,'高对比非自然颜色及大块鲜明色面','Non-natural saturated blocks of Fauvist-inspired color'),
 'fresco-plaster':(fresco,'柔和哑光设色与灰泥吸色颗粒','Matte muted color and mineral-like plaster granulation'),
 'kawaii-stationery':(kawaii,'柔和文具插画色块与简化线条','Pastel stationery-style cartoon simplification'),
 'silhouette-paper':(silhouette,'剪影块面及纸面镂空轮廓示意','Flat cut-paper silhouette shapes with internal cutouts'),
 'rubber-hose':(rubber,'黑白复古卡通块面和粗墨线，非角色骨骼形变','Rubber-hose-inspired inked retro cartoon tones, not rigged anatomy'),
 'mosaic-tesserae':(mosaic,'小尺度拼贴石片与深色勾缝','Small mosaic-tile color fields with dark grout'),
 'torn-paper':(torn_paper,'不规则撕纸区域与纸色分层','Irregular paper collage regions with pale fibrous gaps'),
}
script_hash=hash_file(Path(__file__))
for sid,(fn,zh,en) in process.items():
    style=next(v for v in styles if v['id']==sid)
    assert not style.get('illustrations'),sid+' already has an illustration'
    image=fimage(fn(arr))
    full=ROOT/'public/examples'/f'{sid}.webp'
    thumb=ROOT/'public/examples'/f'{sid}.thumb.webp'
    full.parent.mkdir(exist_ok=True,parents=True)
    image.save(full,'WEBP',quality=88,method=6)
    image.resize((480,360),Image.Resampling.LANCZOS).save(thumb,'WEBP',quality=79,method=6)
    style['illustrations']=[dict(id='procedural-v05-'+sid,styleId=sid,kind='procedural-style-study',
        accepted=False,displayApproved=True,promptVerified=False,
        path=f'examples/{sid}.webp',thumbnailPath=f'examples/{sid}.thumb.webp',
        width=1200,height=900,thumbnailWidth=480,thumbnailHeight=360,aspectRatio='4:3',
        outputSha256=hash_file(full),thumbnailSha256=hash_file(thumb),sourceOutputSha256=hash_file(full),
        originalId='B00',originalSha256=bench['sha256'],
        referenceAssociation='deterministic processing of exact B00 file',
        model='local-procedural',lang='en',generationId='procedural-v05-'+sid,
        requestKind='deterministic-computer-graphics',singleIndependentOutput=False,
        promptVersion=style['version'],environment='Python Pillow NumPy OpenCV SciPy scikit-image (non-AI)',
        date='2026-11-03',reviewer='technical algorithm QA (not image-model validation)',
        toolSourcePath='scripts/generate-procedural-v05.py',toolSourceSha256=script_hash,
        reviewNote={'zh':'程序化视觉参考：'+zh+'。不是 AI 生图，也未验证本条 Prompt。','en':'Procedural visual reference: '+en+'. Not AI-generated and not prompt-verified.'})]
bench['illustratedStyles']=sum(any(i.get('displayApproved') for i in s.get('illustrations',[])) for s in styles)
bench['proceduralStudies']=sum(any(i.get('displayApproved') and i.get('kind')=='procedural-style-study' for i in s.get('illustrations',[])) for s in styles)
bench['galleryStyles']=sum(any(i.get('displayApproved') and i.get('kind')=='same-input-showcase' for i in s.get('illustrations',[])) for s in styles)
bench['provisionalGalleryStyles']=sum(any(i.get('displayApproved') and i.get('kind')=='montage-derived-preview' for i in s.get('illustrations',[])) for s in styles)
CAT.write_text(json.dumps(styles,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
BENCH.write_text(json.dumps(bench,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Completed deterministic studies; illustrated styles:',bench['illustratedStyles'])
