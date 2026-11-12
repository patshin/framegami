#!/usr/bin/env python3
"""Deterministic B00 visual studies. These are NOT AI model outputs.

Optional authoring-only dependencies: Pillow, numpy, opencv-python.
The static website itself has no Python runtime requirement.
"""
from pathlib import Path
import argparse
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / 'public' / 'examples'
W, H = 1200, 900
STYLES = (
 'pixel-1bit', 'pixel-cga', 'pixel-ascii-mosaic', 'cmyk-halftone',
 'line-density', 'contour-topography', 'thermal-palette',
 'chromatic-glitch', 'pixel-sorting', 'op-art-contours',
)


def fit_original():
    im = Image.open(ROOT / 'public' / 'benchmark' / 'B00-original.png').convert('RGB')
    return im.resize((W, H), Image.Resampling.LANCZOS)


def pixel_1bit(im):
    low = np.asarray(im.convert('L').resize((200, 150), Image.Resampling.BOX), dtype=np.float32)
    bayer = np.array([[0,48,12,60,3,51,15,63],[32,16,44,28,35,19,47,31],[8,56,4,52,11,59,7,55],[40,24,36,20,43,27,39,23],[2,50,14,62,1,49,13,61],[34,18,46,30,33,17,45,29],[10,58,6,54,9,57,5,53],[42,26,38,22,41,25,37,21]],dtype=np.float32)
    yy, xx = np.indices(low.shape)
    cutoff = 127 + (bayer[yy%8,xx%8]-31.5)*2.15
    bits = (low > cutoff).astype(np.uint8)
    r = np.where(bits[...,None]>0, np.array([240,232,210]), np.array([21,28,31])).astype(np.uint8)
    return Image.fromarray(r).resize((W,H), Image.Resampling.NEAREST)


def pixel_cga(im):
    low = np.asarray(im.resize((240,180),Image.Resampling.BOX),dtype=np.float32)
    gray = .299*low[...,0]+.587*low[...,1]+.114*low[...,2]
    # Authentic 4-color CGA cyan/magenta/white/black look, ordered contrast
    bayer=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32)
    yy,xx=np.indices(gray.shape)
    adjusted=np.clip(gray+(bayer[yy%4,xx%4]-7.5)*5.4,0,255)
    tone=np.minimum((adjusted//64).astype(np.int32),3)
    palette=np.array([[14,19,31],[255,80,194],[40,233,237],[246,246,240]],dtype=np.uint8)
    arr=palette[tone]
    return Image.fromarray(arr,'RGB').resize((W,H),Image.Resampling.NEAREST)


def ascii_mosaic(im):
    canvas=Image.new('RGB',(W,H),(13,23,28))
    draw=ImageDraw.Draw(canvas)
    fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
    font=ImageFont.truetype(fontpath,12) if Path(fontpath).exists() else ImageFont.load_default()
    cw,ch=9,14
    grid=np.asarray(im.resize((W//cw,H//ch),Image.Resampling.BOX),dtype=np.uint8)
    lum=(.2126*grid[...,0]+.7152*grid[...,1]+.0722*grid[...,2])/255.
    glyphs=' .,:;ox%#@'
    for row in range(grid.shape[0]):
        for col in range(grid.shape[1]):
            level=int(lum[row,col]*(len(glyphs)-1))
            char=glyphs[level]
            c=grid[row,col].astype(np.float32)
            color=tuple(np.clip(c*.72+np.array([82,80,62]),80,255).astype('uint8'))
            draw.text((col*cw,row*ch-2),char,font=font,fill=color)
    return canvas


def cmyk_halftone(im):
    cmyk=im.convert('CMYK').split()
    masks=[]
    # Independent screen angles evoke traditional offset-printing separations.
    for plane,angle in zip(cmyk,(15,75,0,45)):
        # Expand before screen rotation and crop after inverse rotation:
        # this avoids empty triangular corners in the printed image.
        rotated=plane.rotate(angle,resample=Image.Resampling.BILINEAR,expand=True,fillcolor=0)
        rw,rh=rotated.size
        mask=Image.new('L',(rw,rh),0)
        draw=ImageDraw.Draw(mask)
        sample=np.asarray(rotated.resize((rw//11,rh//11),Image.Resampling.BOX),dtype=np.uint8)
        for row in range(sample.shape[0]):
            for col in range(sample.shape[1]):
                ink=sample[row,col]/255.
                radius=5.4*math.sqrt(ink)
                if radius>.5:
                    cx,cy=col*11+5.5,row*11+5.5
                    draw.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=255)
        restored=mask.rotate(-angle,resample=Image.Resampling.BILINEAR,expand=True,fillcolor=0)
        left=(restored.width-W)//2
        top=(restored.height-H)//2
        masks.append(restored.crop((left,top,left+W,top+H)))
    return Image.merge('CMYK',masks).convert('RGB')


def line_density(im):
    gray=np.asarray(im.convert('L'),dtype=np.uint8)
    sketch=np.full((H,W,3),246,dtype=np.uint8)
    # Ink line-width and density respond to underlying local darkness.
    for y in range(1,H,5):
        row=gray[y]
        for x in range(0,W,3):
            val=int(row[x])
            if val<220:
                intensity=(255-val)/255
                thick=3 if intensity>.43 else 2
                ink=np.array([25,42,43]) if intensity>.45 else np.array([70,94,94])
                sketch[y:y+thick,x:min(W,x+3)]=ink
    edge=cv2.Canny(gray,70,150)
    sketch[edge>0]=[31,48,49]
    return Image.fromarray(sketch)


def contour_topography(im):
    gray=np.array(im.convert('L'),dtype=np.uint8)
    smooth=cv2.GaussianBlur(gray,(9,9),2)
    out=np.empty((H,W,3),dtype=np.uint8)
    # Soft terrain background plus level-set lines from image values.
    out[:,:,0]=np.clip(232-(smooth*.26),0,255).astype('uint8')
    out[:,:,1]=np.clip(233-(smooth*.29),0,255).astype('uint8')
    out[:,:,2]=np.clip(212-(smooth*.25),0,255).astype('uint8')
    for level in range(22,234,14):
        binary=(smooth>=level).astype('uint8')*255
        contours,_=cv2.findContours(binary,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
        if contours:
            cv2.drawContours(out,contours,-1,(61,93,88),1,lineType=cv2.LINE_AA)
    edge=cv2.Canny(smooth,55,125)
    out[edge>0]=[48,79,82]
    return Image.fromarray(out)


def thermal_palette(im):
    bgr=cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2BGR)
    gray=cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY)
    # Artistic mapped tones only; NOT a heat measurement.
    v=cv2.equalizeHist(gray)
    colored=cv2.applyColorMap(v,cv2.COLORMAP_TURBO)
    edges=cv2.Canny(gray,70,165)
    colored[edges>0]=(colored[edges>0]*.42).astype('uint8')
    return Image.fromarray(cv2.cvtColor(colored,cv2.COLOR_BGR2RGB))


def chromatic_glitch(im):
    arr=np.array(im,dtype=np.uint8)
    r=np.roll(arr[:,:,0],10,axis=1)
    b=np.roll(arr[:,:,2],-9,axis=1)
    out=np.stack([r,arr[:,:,1],b],axis=2)
    rng=np.random.default_rng(61308)
    for _ in range(28):
        y=int(rng.integers(0,H-1)); tall=int(rng.integers(1,19)); shift=int(rng.integers(-95,96))
        y2=min(H,y+tall)
        out[y:y2]=np.roll(out[y:y2],shift,axis=1)
    for y in range(0,H,4): out[y,:]=(out[y,:]*.88).astype('uint8')
    for _ in range(10):
        x=int(rng.integers(0,W-120)); y=int(rng.integers(0,H-12))
        wide=int(rng.integers(20,160)); tall=int(rng.integers(2,16))
        out[y:y+tall,x:x+wide,1]=np.minimum(255,out[y:y+tall,x:x+wide,1].astype('int')+75).astype('uint8')
    return Image.fromarray(out)


def pixel_sorting(im):
    arr=np.array(im,dtype=np.uint8)
    out=arr.copy()
    rng=np.random.default_rng(81211)
    for yy in range(40,H-20,3):
        if rng.random()>.56: continue
        line=out[yy].copy()
        lum=.2126*line[:,0]+.7152*line[:,1]+.0722*line[:,2]
        # Sorting only selected high-value runs preserves recognizable subjects.
        mask=lum>rng.integers(104,165)
        starts=np.where(np.diff(np.concatenate([[False],mask,[False]]).astype('int'))==1)[0]
        ends=np.where(np.diff(np.concatenate([[False],mask,[False]]).astype('int'))==-1)[0]
        for start,end in zip(starts,ends):
            if end-start<14: continue
            order=np.argsort(lum[start:end])
            sortedline=line[start:end][order]
            extent=int(rng.integers(4,13))
            out[yy:yy+extent,start:end]=sortedline
    return Image.fromarray(out)


def op_art_contours(im):
    gray=np.array(im.convert('L').resize((W,H)),dtype=np.float32)/255
    yy,xx=np.mgrid[0:H,0:W]
    # Alternating contour stripes displaced by the source's luminance/shape.
    phase=(yy/9.2)+2.2*gray+0.3*np.sin(xx/18.0)+.06*np.sin(yy/47+xx/35)
    stripe=np.sin(phase*math.pi*2)
    edge=cv2.Canny(np.asarray(im.convert('L')),65,170)>0
    white=stripe>0
    white[edge]=False
    r=np.where(white,236,22).astype('uint8')
    g=np.where(white,237,28).astype('uint8')
    b=np.where(white,222,36).astype('uint8')
    return Image.fromarray(np.stack([r,g,b],axis=2))

METHODS={
 'pixel-1bit':pixel_1bit, 'pixel-cga':pixel_cga, 'pixel-ascii-mosaic':ascii_mosaic,
 'cmyk-halftone':cmyk_halftone, 'line-density':line_density,
 'contour-topography':contour_topography, 'thermal-palette':thermal_palette,
 'chromatic-glitch':chromatic_glitch,'pixel-sorting':pixel_sorting,
 'op-art-contours':op_art_contours,
}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--only',nargs='*',choices=STYLES)
    args=ap.parse_args()
    im=fit_original()
    OUTPUT.mkdir(parents=True,exist_ok=True)
    for name in args.only or STYLES:
        art=METHODS[name](im).convert('RGB')
        if art.size != (W,H): raise ValueError(f'Invalid size for {name}: {art.size}')
        art.save(OUTPUT/(name+'.webp'),'WEBP',quality=87,method=5)
        art.resize((480,360),Image.Resampling.LANCZOS).save(OUTPUT/(name+'.thumb.webp'),'WEBP',quality=78,method=5)
        print(name,'ok')

if __name__=='__main__':main()
