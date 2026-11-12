"""Exercise the production static build under a repository prefix."""
import json
import os
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

root = Path(__file__).resolve().parents[1]
out = root / 'test-results'
out.mkdir(exist_ok=True)
catalog = json.loads((root / 'data/catalog.json').read_text())
server = subprocess.Popen(['node', '--input-type=module', '-e', """
import {createStaticServer} from './scripts/serve.mjs';
const server = createStaticServer({prefix:'/framegami'});
server.listen(0,'127.0.0.1',()=>console.log(server.address().port));
"""], cwd=root, stdout=subprocess.PIPE, text=True)
try:
    base = f'http://127.0.0.1:{int(server.stdout.readline())}/framegami/'
    with sync_playwright() as pw:
        for width,height in [(1920,1080),(1366,768),(375,667),(412,915)]:
            browser = pw.chromium.launch(executable_path=os.getenv('IRO_CHROME') or None)
            context = browser.new_context(viewport=dict(width=width,height=height),
                is_mobile=width<500,has_touch=width<500,permissions=['clipboard-read','clipboard-write'])
            page=context.new_page()
            errors=[]
            page.on('pageerror',lambda exc:errors.append(str(exc)))
            page.goto(base)
            expect(page.locator('.research-notice')).to_contain_text('213/213')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path=out/f'atlas-{width}.jpg')
            search=page.locator('#style-search')
            for term,sid in [('皮克斯','pixar-inspired-3d'),('watercolour','watercolor-wet')]:
                search.fill(term)
                expect(page.locator(f'[data-card="{sid}"]')).to_be_visible()
            search.fill('xyz-no-such-style')
            expect(page.locator('.empty-state')).to_be_visible()
            page.locator('[data-action="reset-search"]').click()
            nav=page.locator('.sidebar')
            if width<500:
                page.locator('[data-action="menu"]').click()
                nav=page.locator('#mobile-menu')
            nav.locator('[data-category="japan"]').click()
            if width<500:page.locator('[data-action="menu"]').click()
            nav.locator('[data-family="woodblock"]').click()
            expect(page.locator('.style-card')).to_have_count(4)
            page.locator('[data-nav="style"][data-id="shin-hanga"]').first.click()
            page.locator('[data-model="gemini"]').click()
            page.locator('#detail-lang').select_option('en')
            page.locator('[data-action="language"]').click()
            expect(page.locator('html')).to_have_attribute('lang','en')
            page.locator('[data-action="copy-detail"]').click()
            assert page.evaluate('navigator.clipboard.readText()')==page.locator('#detail-prompt').inner_text()
            page.locator('[data-favorite="shin-hanga"]').first.click()
            page.reload()
            expect(page.locator('[data-favorite="shin-hanga"]').first).to_have_attribute('aria-pressed','true')
            page.screenshot(path=out/f'detail-{width}.jpg')
            page.goto(base+'en/workbench/')
            page.locator('#work-text').fill('Keep the ink texture.')
            page.reload()
            expect(page.locator('#work-text')).to_have_value('Keep the ink texture.')
            page.locator('[data-action="save-custom"]').click()
            page.locator('#custom-name').fill('Ink study')
            page.locator('[data-dialog-action="save-custom"]').click()
            page.goto(base+'en/custom/')
            expect(page.get_by_text('Ink study',exact=True).first).to_be_visible()
            if width==1366:
                for s in catalog:
                    sample=next(i for i in s['illustrations'] if i['displayApproved'])
                    page.goto(base+'zh/style/'+s['id']+'/')
                    image=page.locator('img[src$="/'+sample['path']+'"]').first
                    image.evaluate('img => img.decode()')
                    assert image.evaluate('img=>img.naturalWidth')==sample['width']
                    page.evaluate('async url=>{const img=new Image();img.src=url;await img.decode()}',base+sample['thumbnailPath'])
                    if sample['kind']=='montage-derived-preview':
                        assert page.locator('.split-view').count()==0
                page.goto(base+'en/compare/?ids=shin-hanga,rural-handdrawn')
                expect(page.locator('.compare-column')).to_have_count(2)
            assert not errors, errors
            browser.close()
            print('PASS',width,height,flush=True)
finally:
    server.terminate()
    server.wait()
