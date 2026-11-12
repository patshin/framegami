"""V0.4 image coverage and provenance checks in actual headless Chromium.
Standalone HTML uses a test origin for URL parsing; no remote network or real user storage is claimed.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
R=Path(__file__).resolve().parents[1]
O=R/'evidence/v0.4'
O.mkdir(parents=True,exist_ok=True)
html=(R/'IRO-preview.html').read_text(encoding='utf-8').replace('"base":"./"','"base":"https://iro.test/"')
checks=[]
def check(name,value):
    assert value,name
    checks.append({'name':name,'status':'PASS'})
    print('PASS',name,flush=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':920})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html,wait_until='load')
    check('24 initial cards',page.locator('.style-card').count()==24)
    check('85 of 213 gallery visual coverage','85/213' in page.locator('.research-notice').inner_text())
    check('Montage and procedural preview counts disclosed','10 张拼图裁切' in page.locator('.research-notice').inner_text() and '8 张 B00 程序化预览' in page.locator('.research-notice').inner_text())
    page.locator('#status-filter').select_option('images')
    check('85 images filter results','85 条结果' in page.locator('#result-count').inner_text())
    while page.locator('[data-action="more"]').count():
        page.locator('[data-action="more"]').click()
    check('85 visual cards are visible',page.locator('.style-card').count()==85)
    check('85 visual references, no duplicated image URLs',page.locator('.style-card img').evaluate_all('(es)=>es.length===85&&new Set(es.map(e=>e.src)).size===85'))
    check('10 montage cards and 8 featured procedural cards labeled',page.locator('.style-card .status-tag').evaluate_all('(es)=>es.filter(e=>e.textContent.includes("拼图临时示意")).length===10&&es.filter(e=>e.textContent.includes("算法预览")).length===8'))
    for sid in ['matte-gouache','pixel-dither','shonen-ink','silver-age-comic','ink-crosshatch','expressionist','soft-focus-optical','film-color-negative','webtoon-clean','watercolor-dry']:
        check('Provisional image appears: '+sid,page.locator(f'[data-card="{sid}"] img').count()==1)
    page.screenshot(path=str(O/'gallery-overview.png'),full_page=False)
    # Navigate to one provisional style: cannot claim B00 pair, prompt evidence, or independent generation.
    page.locator('[data-card="matte-gouache"] [data-nav="style"]').first.click()
    check('No B00 split for montage crop',page.locator('.split-view').count()==0)
    check('Provisional label on detail','拼图裁切参考' in page.locator('.detail-tags').inner_text())
    check('Explicit original-mismatch caveat','不同于 B00' in page.locator('.visual-note').inner_text())
    check('Provisional source is not an exact prompt test','未经当前提示词实测' in page.locator('.visual-note').inner_text())
    page.screenshot(path=str(O/'provisional-detail.png'),full_page=False)
    # Compare a mixed pair: no same-original caption or synced zoom claim.
    page.locator('[data-compare="matte-gouache"]').first.click()
    page.locator('[data-nav="atlas"]').first.click()
    page.locator('[data-compare="pixar-inspired-3d"]').first.click()
    page.locator('[data-action="open-compare"]').click()
    check('Mixed-source comparison shown',page.locator('.compare-column').count()==2)
    check('Mixed-source warning visible','图片来源可能不同' in page.locator('.page-heading').inner_text())
    check('No false synced-zoom control',page.locator('#compare-zoom').count()==0)
    check('Provisional sample is identified','拼图裁切示意' in page.locator('.compare-column').first.inner_text())
    page.screenshot(path=str(O/'mixed-source-compare.png'),full_page=False)
    # Known same-input pair must retain true original-result functionality.
    page.locator('[data-action="clear-compare"]').first.click()
    page.locator('[data-nav="atlas"]').first.click()
    page.locator('[data-compare="pixar-inspired-3d"]').first.click()
    page.locator('[data-compare="pixel-16bit"]').first.click()
    page.locator('[data-action="open-compare"]').click()
    check('Same-input comparison zoom remains',page.locator('#compare-zoom').count()==1)
    check('Same-input comparison has two image columns',page.locator('.zoom-window img').count()==2)
    page.locator('[data-nav="atlas"]').first.click()
    page.locator('[data-card="pixar-inspired-3d"] [data-nav="style"]').first.click()
    check('B00 original-result split still works',page.locator('.split-view img').count()==2)
    check('Split slider remains present',page.locator('#split-range').count()==1)
    # A procedural study permits B00 splitting but must explicitly disclaim image-model validation.
    page.locator('[data-nav="atlas"]').first.click()
    page.locator('[data-card="pixel-cga"] [data-nav="style"]').first.click()
    check('Procedural B00 original comparison works',page.locator('.split-view img').count()==2)
    check('Procedural original-result label discloses method','程序化预览' in page.locator('.range-control').first.inner_text())
    check('Procedural warning is explicit','不是 ImageGen 模型生成' in page.locator('.visual-note').inner_text())
    page.screenshot(path=str(O/'procedural-detail.png'),full_page=False)
    # Missing & actual-verification filters do not count provisional images.
    page.locator('[data-nav="atlas"]').first.click()
    page.locator('#status-filter').select_option('missing-images')
    check('128 styles remain with no image','128 条结果' in page.locator('#result-count').inner_text())
    check('Missing-image cards remain abstract',page.locator('.style-card img').count()==0)
    page.locator('#status-filter').select_option('examples')
    check('Strict prompt-verified gallery remains empty',page.locator('.style-card').count()==0)
    # Standalone preview retains embedded image data without server dependencies.
    page.locator('#status-filter').select_option('images')
    check('All preview images use embedded data URLs',page.locator('.style-card img').evaluate_all('(es)=>es.length===24&&es.every(e=>e.src.startsWith("data:image/webp;base64,"))'))
    for width,height in [(390,844),(768,1024)]:
        page.set_viewport_size({'width':width,'height':height})
        check(f'No horizontal overflow on {width}px',page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'))
    check('No page script errors',errors==[])
    browser.close()
report={'browser':'Chromium headless; standalone data-embedded preview; no live deployment','passes':len(checks),'failures':0,'checks':checks,'independentStyleShowcases':67,'montageDerivedProvisional':10,'proceduralStudies':8,'untouched':128}
(O/'browser-v04-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False,indent=2),flush=True)
