from pathlib import Path
import json,threading,http.server,socketserver
from functools import partial
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'evidence/v0.3';O.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=socketserver.TCPServer(('127.0.0.1',0),partial(Handler,directory=str(R/'dist')))
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_address[1]}/'
results=[]
def check(name,value):
 assert value,name
 results.append({'name':name,'result':'PASS'});print('PASS',name,flush=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':1440,'height':1100},device_scale_factor=1)
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content((R/'IRO-preview.html').read_text(),wait_until='load')
 check('Initial 24 style entries render',page.locator('.style-card').count()==24)
 check('Gallery coverage is explicit 8 of 213','8 / 213' in page.locator('.research-notice').inner_text())
 check('No desktop horizontal overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
 page.screenshot(path=str(O/'desktop-gallery.png'),full_page=True)
 page.locator('[data-action="show-images"]').first.click();page.wait_for_load_state('networkidle')
 check('Image-only facet contains exactly eight independent styles',page.locator('.style-card').count()==8)
 # Lazy-loaded cards must be decoded before evaluating their image dimensions.
 for image in page.locator('.style-card img').all():
  image.scroll_into_view_if_needed();image.evaluate('(e)=>e.decode()')
 check('All eight case images decode',page.locator('.style-card img').evaluate_all('(es)=>es.length===8&&es.every(e=>e.naturalWidth>0)'))
 check('Generated assets are not assigned twice',page.locator('.style-card img').evaluate_all('(es)=>new Set(es.map(e=>e.src)).size===8'))
 page.evaluate('scrollTo({top:0,behavior:"instant"})');page.screenshot(path=str(O/'desktop-cases.png'),full_page=True)
 page.locator('.style-card [data-nav="style"][data-id="pixar-inspired-3d"]').first.click();page.wait_for_timeout(250)
 for image in page.locator('.split-view img').all():image.evaluate('(e)=>e.decode()')
 check('Original and generated style sample both appear',page.locator('.split-view img').count()==2)
 check('4 to 3 is preserved in the comparison',abs(page.locator('.split-view').evaluate('(e)=>e.clientWidth/e.clientHeight')-4/3)<.01)
 check('Image is not mislabeled as an exact prompt test','没有对应记录' in page.locator('.sample-evidence').text_content())
 page.locator('#split-range').evaluate('(e)=>{e.value=70;e.dispatchEvent(new Event("input",{bubbles:true}))}');check('Before-after slider moves',page.locator('#split-view').evaluate('(e)=>e.style.getPropertyValue("--split")')=='70%')
 page.locator('[data-model="gemini"]').click()
 check('Switching model retains visual sample without certifying model','此版本待实测' in page.locator('.detail-tags').inner_text() and page.locator('.split-view img').count()==2)
 page.locator('#detail-lang').select_option('en');check('English adapter remains available','Using the uploaded image' in page.locator('#detail-prompt').inner_text())
 page.screenshot(path=str(O/'desktop-detail.png'),full_page=True)
 page.locator('[data-favorite="pixar-inspired-3d"]').first.click()
 check('Favorite toggle remains usable in offline memory rendering',page.locator('[data-favorite="pixar-inspired-3d"]').first.get_attribute('aria-pressed')=='true')
 page.evaluate("history.replaceState(null,'','#en/compare/?ids=pixar-inspired-3d,pixel-16bit,watercolor-wet,impressionist&model=gemini&pl=en');window.dispatchEvent(new PopStateEvent('popstate'))")
 check('Shared comparison restores four style cases',page.locator('.zoom-window img').count()==4)
 for image in page.locator('.zoom-window img').all():image.evaluate('(e)=>e.decode()')
 check('All four comparison images decode',page.locator('.zoom-window img').evaluate_all('(es)=>es.every(e=>e.naturalWidth>0)'))
 page.locator('#compare-zoom').evaluate('(e)=>{e.value=1.8;e.dispatchEvent(new Event("input",{bubbles:true}))}');check('Synchronized zoom applies to all samples',page.locator('.zoom-window').evaluate_all('(es)=>es.every(e=>e.style.getPropertyValue("--zoom")==="1.8")'))
 page.screenshot(path=str(O/'desktop-compare.png'),full_page=True)
 page.evaluate("history.replaceState(null,'','#zh/?status=missing-images');window.dispatchEvent(new PopStateEvent('popstate'))")
 check('Missing cases remain explicit 205','205 条结果' in page.locator('#result-count').inner_text())
 check('Missing entries are not filled with other style images',page.locator('.style-card img').count()==0)
 page.evaluate("history.replaceState(null,'','#zh/?status=examples');window.dispatchEvent(new PopStateEvent('popstate'))")
 check('Verified-only filter cannot confuse sample illustrations with prompt tests',page.locator('.style-card').count()==0)
 # Native single-file navigation, no storage test substitute.
 file_page=context.new_page();file_errors=[];file_page.on('pageerror',lambda e:file_errors.append(str(e)))
 file_page.set_content((R/'IRO-preview.html').read_text(),wait_until='load')
 file_page.locator('[data-action="show-images"]').first.click()
 check('Standalone HTML exposes eight locally embedded cases',file_page.locator('.style-card img').count()==8)
 check('Standalone case src values are embedded data not missing sibling files',file_page.locator('.style-card img').evaluate_all('(es)=>es.every(e=>e.src.startsWith("data:image/webp"))'))
 for image in file_page.locator('.style-card img').all():
  image.scroll_into_view_if_needed();image.evaluate('(e)=>e.decode()')
 check('All standalone images decode without server',file_page.locator('.style-card img').evaluate_all('(es)=>es.every(e=>e.naturalWidth>0)'))
 for width,height in [(390,844),(768,1024)]:
  page.set_viewport_size({'width':width,'height':height});page.evaluate("history.replaceState(null,'','#zh/?status=images');window.dispatchEvent(new PopStateEvent('popstate'))")
  check(f'No horizontal overflow at {width}px',page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
  check(f'Eight cards available at {width}px',page.locator('.style-card').count()==8)
  page.evaluate('document.activeElement?.blur();scrollTo({top:0,behavior:"instant"})');page.wait_for_timeout(150)
  page.screenshot(path=str(O/f'cases-{width}.png'),full_page=True)
 check('No JavaScript errors in offline-rendered interaction journeys',not errors)
 check('No JavaScript errors in embedded-asset preview',not file_errors)
 browser.close()
server.shutdown();server.server_close()
report={'environment':'Chromium page.set_content with self-contained HTML and hash navigation. Browser HTTP navigation was blocked by administrator policy. No remote hosting or real browser-persistence acceptance is claimed; storage fallback is session-only here.','checks':results,'passed':len(results),'total':len(results),'images':8,'catalog':213,'missing':205}
(O/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
