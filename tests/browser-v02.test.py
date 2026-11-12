"""Additional Chromium DOM regressions. In-memory rendering; test-only storage.
No browser policy is disabled. Actual HTTP delivery is tested separately by Node.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'IRO-preview.html').read_text().replace('"base":"./"','"base":"https://iro.test/"')
shim="""<script>window.__store={};window.__downloadBlobs=[];Object.defineProperty(window,'localStorage',{value:{getItem(k){return window.__store[k]??null},setItem(k,v){window.__store[k]=String(v)},removeItem(k){delete window.__store[k]}},configurable:true});const origURL=URL.createObjectURL.bind(URL);URL.createObjectURL=b=>{window.__downloadBlobs.push(b);return origURL(b);};</script>"""
html=html.replace('<script>window.IRO_CONFIG=',shim+'<script>window.IRO_CONFIG=')
checks=[]
def check(name,value):
 assert value,name
 checks.append({'name':name,'status':'PASS'})
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html,wait_until='load')
 page.locator('[data-treatment="restyle"]').click()
 check('preserve-composition mode has 202 entries','202' in page.locator('#result-count').inner_text())
 page.locator('[data-treatment="lab"]').click()
 check('lab mode has exactly 11 actual reinterpretations',page.locator('.style-card').count()==11)
 check('treatment mode persists in preview URL','treatment=lab' in page.evaluate('location.hash'))
 page.locator('[data-action="export-results"]').click()
 text=page.evaluate('window.__downloadBlobs.at(-1).text()')
 check('batch export contains only the 11 selected prompts',text.count('Status: UNTESTED_TEXT_ADAPTATION')==11 and '## 盒装收藏手办' in text)
 page.locator('[data-treatment="all"]').click()
 page.locator('[data-compare="pixar-inspired-3d"]').first.click()
 page.locator('[data-compare="shin-hanga"]').first.click()
 page.locator('[data-action="open-compare"]').click()
 check('comparison URL carries its real selected IDs','ids=pixar-inspired-3d%2Cshin-hanga' in page.evaluate('location.hash'))
 page.locator('[data-model="gemini"]').click();page.locator('#compare-lang').select_option('en')
 check('comparison URL carries model and prompt language','model=gemini' in page.evaluate('location.hash') and 'pl=en' in page.evaluate('location.hash'))
 page.locator('[data-action="export-compare"]').click()
 text=page.evaluate('window.__downloadBlobs.at(-1).text()')
 check('comparison export matches selected language and model',text.count('Status: UNTESTED_TEXT_ADAPTATION')==2 and 'Using the uploaded image' in text)
 page.locator('[data-action="share-compare"]').click()
 check('standalone preview does not invent a public comparison URL','单文件预览' in page.locator('#toast').inner_text())
 page.locator('[data-nav="atlas"]').first.click()
 page.locator('[data-nav="style"][data-id="shin-hanga"]').first.click()
 check('untested selected model is explicit in details','此版本待实测' in page.locator('.detail-tags').inner_text())
 page.locator('[data-export-style="shin-hanga"]').click()
 recipe=page.evaluate('window.__downloadBlobs.at(-1).text()')
 page.locator('.sidebar [data-nav="custom"]').click()
 page.locator('#import-file').set_input_files({'name':'iro-shin-hanga.json','mimeType':'application/json','buffer':recipe.encode()})
 page.locator('[data-dialog-action="confirm-import"]').click()
 check('a style exported by the app can actually be imported',page.locator('.custom-card').count()==1)
 check('imported original is safely a local custom recipe','LOCAL ONLY' in page.locator('.source-meta').inner_text() or '仅本地' in page.locator('.source-meta').inner_text())
 page.locator('[data-edit-custom]').first.click()
 page.locator('#work-text').fill('My edited woodblock prompt: preserve the original scene.')
 page.locator('[data-action="update-custom"]').click()
 page.locator('.sidebar [data-nav="custom"]').click()
 check('saving an existing custom recipe updates only that record',page.locator('.custom-card').count()==1 and 'My edited woodblock' in page.locator('.custom-card').inner_text())
 page.locator('[data-action="new-custom"]').click()
 page.locator('#work-text').fill('A soft gouache picture based on the uploaded original.')
 page.locator('[data-action="save-custom"]').click()
 page.locator('#custom-name').fill('My gouache')
 page.locator('#custom-tags').fill('温柔，portrait,<img onerror=alert(1)>')
 page.locator('[data-dialog-action="save-custom"]').click()
 page.locator('.sidebar [data-nav="custom"]').click()
 check('custom tags are shown as escaped text','<img onerror=alert(1)>' in page.locator('.custom-tags').last.inner_text() and page.locator('.custom-tags img').count()==0)
 page.locator('[data-action="export"]').click()
 backup=json.loads(page.evaluate('window.__downloadBlobs.at(-1).text()'))
 check('backup retains tags and prompt edits',backup['custom'][-1]['tags']==['温柔','portrait','<img onerror=alert(1)>'] and 'My edited woodblock' in backup['custom'][0]['prompt'])
 # Verify all stores are attempted when real writes fail. This hook only exists in test HTML.
 fault=html.replace("renderShell();renderPage();if(storageWarning)","window.__testAccess={persist,readLocal,state};renderShell();renderPage();if(storageWarning)")
 other=b.new_page(viewport={'width':390,'height':844});other.set_content(fault,wait_until='load')
 outcome=other.evaluate("""()=>{localStorage.setItem=()=>{throw new Error('quota')};const x=window.__testAccess;x.state.custom=[{id:'custom-x',name:'x',prompt:'p'}];x.state.compare=['shin-hanga'];x.persist();return {custom:x.readLocal('custom',[]),compare:x.readLocal('compare',[])};}""")
 check('storage failure still saves the custom record in session fallback',outcome['custom'][0]['id']=='custom-x')
 check('storage failure still saves comparisons in session fallback',outcome['compare']==['shin-hanga'])
 # Model-specific evidence selection is covered with synthetic pure-unit fixtures.
 # DOM checks never use test fixtures as gallery examples.
 for width in [320,390,768,1440]:
  page.set_viewport_size({'width':width,'height':900})
  page.locator('[data-nav="atlas"]').first.click()
  check(f'atlas has no overflow at {width}px',not page.evaluate('document.documentElement.scrollWidth>innerWidth'))
 page.emulate_media(reduced_motion='reduce')
 check('reduced-motion mode disables smooth document scrolling',page.evaluate("getComputedStyle(document.documentElement).scrollBehavior")=='auto')
 check('new interactions have no JavaScript errors',errors==[])
 b.close()
summary={'environment':'Chromium in-memory DOM; instrumented localStorage and Blob capture; NOT live deployment','tests':len(checks),'passed':len(checks),'failed':0,'checks':checks}
(ROOT/'docs/browser-v02-results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='checks'},ensure_ascii=False,indent=2))
