"""Offline Chromium smoke: newly imported B00-like standalone AI images are correctly indexed.
The remote model generation and final deployment are not verified by this test.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
R=Path(__file__).resolve().parents[1]
HTML=(R/'IRO-preview.html').read_text(encoding='utf-8').replace('"base":"./"','"base":"https://iro.test/"')
styles=['egg-tempera','sanguine-chalk','ink-stipple','etching-line','rinpa-gold','city-pop-airbrush','pixel-1bit','patchwork','hammered-metal','thermal-palette']
checks=[]
def check(name,ok):
 assert ok,name
 checks.append(name)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1366,'height':850}); errors=[]
 page.on('pageerror',lambda exc:errors.append(str(exc)))
 page.set_content(HTML,wait_until='load')
 page.locator('#status-filter').select_option('images')
 while page.locator('[data-action="more"]').count():page.locator('[data-action="more"]').click()
 for sid in styles:
  card=page.locator(f'[data-card="{sid}"]')
  check(sid+' card exists',card.count()==1)
  check(sid+' output loads',card.locator('img').evaluate('(el)=>el.complete && el.naturalWidth>0'))
  check(sid+' labeled independent same-scene', '独立生成' in card.locator('.cover-label').inner_text())
 card=page.locator('[data-card="egg-tempera"]')
 card.locator('[data-nav="style"]').click()
 check('unverified separate image does not claim B00 strict edit',page.locator('.split-view').count()==0)
 check('source caveat visible','未证明 B00 原图' in page.locator('.visual-note').inner_text())
 check('full image appears in detail',page.locator('.large-cover img').evaluate('(el)=>el.complete && el.naturalWidth>0'))
 page.locator('[data-nav="atlas"]').first.click()
 page.locator('#status-filter').select_option('images')
 while page.locator('[data-action="more"]').count():page.locator('[data-action="more"]').click()
 page.locator('[data-card="pixel-1bit"] [data-nav="style"]').click()
 check('updated 1-bit AI image now featured',page.locator('.large-cover .cover-label').count()==1 and '独立生成' in page.locator('.large-cover .cover-label').inner_text())
 check('replaced procedural sample not falsely displayed as B00 edit',page.locator('.split-view').count()==0)
 check('no script errors',not errors)
 b.close()
output=R/'evidence'/'browser-85-batch.json'
output.write_text(json.dumps({'passed':len(checks),'checks':checks,'scope':'Offline demo media DOM only; no deployed or prompt-model verification'},ensure_ascii=False,indent=2)+'\n')
print('PASS',len(checks),'offline media-mapping checks')
