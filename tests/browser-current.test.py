"""Current image-source UX smoke in Chromium (offline HTML, no live deployment)."""
from pathlib import Path
import json, shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]
catalog=json.loads((R/'data/catalog.json').read_text(encoding='utf-8'))
active=[s for s in catalog if any(v.get('displayApproved') for v in s.get('illustrations',[]))]
montage=[s for s in active if any(v.get('displayApproved') and v.get('kind')=='montage-derived-preview' for v in s['illustrations'])]
procedural=[s for s in active if any(v.get('displayApproved') and v.get('kind')=='procedural-style-study' for v in s['illustrations'])]
html=(R/'IRO-preview.html').read_text(encoding='utf-8').replace('"base":"./"','"base":"https://iro.test/"')
checks=[]
def check(name,okay):
    if not okay:raise AssertionError(name)
    checks.append(name)
with sync_playwright() as p:
    system_chromium=shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome')
    launch_args={'headless':True,'args':['--no-sandbox']}
    if system_chromium:launch_args['executable_path']=system_chromium
    b=p.chromium.launch(**launch_args)
    page=b.new_page(viewport={'width':1440,'height':900})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html,wait_until='domcontentloaded',timeout=60000)
    check('initial cards',page.locator('.style-card').count()==24)
    notice=page.locator('.research-notice').inner_text()
    check('live coverage',f'{len(active)}/{len(catalog)}' in notice)
    page.locator('#status-filter').select_option('images')
    while page.locator('[data-action="more"]').count():page.locator('[data-action="more"]').click()
    check('all illustrated styles',page.locator('.style-card').count()==len(active))
    check('all image cards have files',page.locator('.style-card img').count()==len(active))
    if montage:
        sid=montage[0]['id']
        page.locator(f'[data-card="{sid}"] [data-nav="style"]').first.click()
        check('montage not compared against B00',page.locator('.split-view').count()==0)
        montage_note=page.locator('.visual-note').inner_text()
        check('montage clearly disclosed',('拼图' in montage_note and '不是独立' in montage_note) or ('montage' in montage_note.lower() and 'not' in montage_note.lower()))
        page.locator('[data-nav="atlas"]').first.click()
    if procedural:
        sid=procedural[0]['id']
        page.locator(f'[data-card="{sid}"] [data-nav="style"]').first.click()
        note=page.locator('.visual-note').inner_text()
        check('procedural warning',('B00' in note and '不是 ImageGen' in note) or ('deterministic' in note.lower() and 'not' in note.lower()))
    check('no script errors',not errors)
    b.close()
print('PASS',len(checks),'offline browser checks; no live deployment claimed')
