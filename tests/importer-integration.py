"""Integration smoke for image-pack importer. Requires Pillow, Node.js 20+.
Synthetic images are generated only in a temporary project and never shipped.
"""
from pathlib import Path
import tempfile,shutil,subprocess,io,json,zipfile,sys
from PIL import Image,ImageEnhance,ImageDraw
src=Path(__file__).resolve().parents[1]
wd=Path(tempfile.mkdtemp(prefix='iro_import_smoke_'))
proj=wd/'iro-style-atlas';proj.mkdir()
for folder in ['data','public','src','scripts','tests','evidence','docs','.github']:
    shutil.copytree(src/folder,proj/folder)
for filename in ['package.json','.gitignore']:
    shutil.copy2(src/filename,proj/filename)
# Use synthetic images ONLY within the sandbox clone to test importer mechanics; these are not product examples.
original=Image.open(src/'public/benchmark/B00-original.png').convert('RGB').resize((480,360))
def png(image):
    b=io.BytesIO();image.save(b,'PNG');return b.getvalue()
a=ImageEnhance.Color(original).enhance(.6)
b=ImageEnhance.Brightness(original).enhance(.85)
c=ImageEnhance.Contrast(original).enhance(1.25)
mont=Image.new('RGB',(960,360),(245,245,245));mont.paste(original,(0,0));mont.paste(b,(480,0))
for batch,items in [
    ('testbatch01',[{'style_id':'rural-handdrawn','file':'images/rural-handdrawn.png','source_type':'independent-ai','generation_id':'fixture-only-1','model':'chatgpt','language':'en','note_zh':'合成测试图像，无实际生成模型','note_en':'Synthetic importer test fixture, not a model output'}]),
    ('testbatch02',[{'style_id':'ligne-claire','file':'images/ligne-claire.png','source_type':'montage-crop','generation_id':'fixture-montage-only','model':'chatgpt','language':'en','montage_file':'montages/fixture.png','crop_box':[480,0,960,360],'source_panel_label':'second panel','note_zh':'合成拼图测试图像','note_en':'Synthetic montage test fixture'}]),
    ('testbatch03',[{'style_id':'line-density','file':'images/line-density.png','source_type':'independent-ai','generation_id':'fixture-only-3','model':'chatgpt','language':'en','note_zh':'用于升级归档验证的合成测试图','note_en':'Synthetic upgrade test fixture'}])
]:
    zip_path=wd/f'{batch}.zip'
    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('manifest.json',json.dumps({'schema':'iro-image-pack-v1','batch_id':batch,'date':'2026-11-03','images':items}))
        for item in items:
            im=a if item['style_id']=='rural-handdrawn' else c if item['style_id']=='line-density' else b
            z.writestr(item['file'],png(im))
        if batch=='testbatch02':z.writestr('montages/fixture.png',png(mont))
    cmd=[sys.executable,str(proj/'scripts/import-image-pack.py'),str(zip_path)]
    dry=subprocess.run(cmd+(['--upgrade-preview'] if batch=='testbatch03' else [])+['--dry-run'],cwd=proj,text=True,capture_output=True)
    print(batch,'dry-run',dry.returncode, dry.stdout[-250:],dry.stderr[-250:])
    assert dry.returncode==0
    run=subprocess.run(cmd+(['--upgrade-preview'] if batch=='testbatch03' else []),cwd=proj,text=True,capture_output=True)
    print(batch,'import',run.returncode,run.stdout[-250:],run.stderr[-250:])
    assert run.returncode==0
    cat=json.loads((proj/'data/catalog.json').read_text())
    cover=sum(any(y.get('displayApproved') for y in x.get('illustrations',[])) for x in cat)
    print('coverage:',cover)
    if batch=='testbatch03':
        old=next(s for s in cat if s['id']=='line-density')['illustrations']
        print('archive:',[(v.get('displayApproved'),v.get('kind'),v['path']) for v in old]);assert len(old)>=2 and old[1]['displayApproved'] is False
        assert (proj/'public'/old[1]['path']).is_file()
    assert cover=={'testbatch01':106,'testbatch02':107,'testbatch03':107}[batch]
    replay=subprocess.run(cmd,cwd=proj,text=True,capture_output=True)
    assert replay.returncode!=0 and 'already imported' in replay.stderr
result=subprocess.run(['npm','run','check'],cwd=proj,text=True,capture_output=True,timeout=120)
print('npm check',result.returncode,result.stdout[-1000:],result.stderr[-1000:])
assert result.returncode==0
print('ALL_IMPORT_SMOKE_PASSED',wd)
# For audit retain a brief log, then remove synthetic project to prevent accidental product use.
print('Synthetic images were restricted to a throwaway temporary project.')
shutil.rmtree(wd)
