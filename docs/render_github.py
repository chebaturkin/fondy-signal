"""Render the repository cover and scene gallery from local product sources.

Build the site and start site/serve.py on port 8799 before running this file.
Requires the same Playwright/Chromium installation as site/verify.py.
"""
from __future__ import annotations

import base64
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"


def data_uri(path: str, mime: str) -> str:
    encoded = base64.b64encode((ROOT / path).read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


fonts = "".join(
    f"@font-face{{font-family:'{family}';src:url('{data_uri(path, 'font/woff2')}') format('woff2');font-weight:{weight};}}"
    for family, path, weight in (
        ("EF Dela", "brand-kit/fonts/dela-gothic-one.woff2", "400"),
        ("EF Onest", "brand-kit/fonts/onest-variable.woff2", "100 900"),
    )
)
logo = data_uri("brand-kit/assets/favicons/signal-logo.svg", "image/svg+xml")
mascot = data_uri("brand-kit/assets/mascot/fondy-greeting-color-light.svg", "image/svg+xml")
cover = f'''<!doctype html><html lang="ru"><meta charset="utf-8"><style>
{fonts}
*{{box-sizing:border-box}}html,body{{margin:0;width:1280px;height:560px;background:#fff8ed}}
body{{position:relative;padding:48px 64px;color:#24221f;overflow:hidden;font-family:'EF Onest',sans-serif}}
.logo{{width:184px;height:auto;display:block}}
h1{{margin:42px 0 0;font:400 91px/1.04 'EF Dela',sans-serif;letter-spacing:-4px}}
h1 span{{color:#2457ff}}
p{{margin:27px 0 0;font-size:21px;line-height:1.55;letter-spacing:-.2px}}
.figure{{position:absolute;right:64px;top:116px;width:386px;height:368px}}
.figure:before{{content:'';position:absolute;inset:5px 0 -5px;background:#e9edff;border-radius:46% 54% 42% 48%;transform:rotate(-7deg)}}
.figure:after{{content:'';position:absolute;left:70px;right:54px;bottom:0;height:16px;background:#cbd4fa;border-radius:50%}}
.fondy{{position:absolute;z-index:1;left:23px;bottom:7px;width:340px}}
.wave{{position:absolute;right:40px;top:119px;width:435px;height:380px;color:#ff6b35}}
</style><img class="logo" src="{logo}" alt="signal">
<h1>передать<br><span>сигнал.</span></h1>
<p>знаки, пауза, записка и ритм.<br>fondy побудет рядом.</p>
<div class="figure"><img class="fondy" src="{mascot}" alt="fondy"></div>
<svg class="wave" viewBox="0 0 435 380" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round"><path d="m38 88-14-7m24-15-6-16M390 72l13-11m-2 29 20-2"/></g></svg>
</html>'''
styles = (ROOT / "site/base.css").read_text() + (ROOT / "site/sections/workshop.css").read_text()
scene_styles = f'''{styles}\n{fonts}
html,body{{width:860px;height:440px;overflow:hidden;margin:0;scroll-behavior:auto}}
body{{display:grid;place-items:center;padding:28px;background:#fff8ed}}
.github-scene{{width:100%;min-width:0}}
.github-scene>div{{margin-top:0}}
*{{animation:none!important;transition:none!important}}
'''
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    art = browser.new_page(viewport={"width": 1280, "height": 560}, device_scale_factor=1)
    art.set_content(cover, wait_until="load")
    art.evaluate("document.fonts.ready")
    assert art.locator("img").evaluate_all("nodes => nodes.every(node => node.complete && node.naturalWidth > 0)")
    art.screenshot(path=str(OUT / "signal-cover.png"))

    source = browser.new_page(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
    response = source.goto("http://127.0.0.1:8799/", wait_until="networkidle")
    assert response and response.status == 200
    for token in ("pulse", "spark", "wave", "anchor"):
        source.locator(f'.token-choice[data-token="{token}"]').click()
    art.set_viewport_size({"width": 860, "height": 440})
    for mode in ("signal", "pause", "letter", "rhythm"):
        source.locator(f'[role="tab"][data-workshop-mode="{mode}"]').click()
        if mode == "letter":
            source.locator('[data-letter-note]').fill("я рядом. можно без слов.")
            source.locator('[data-note-token="wave"]').click()
            source.locator('[data-letter-submit]').click()
        if mode == "rhythm":
            for key in ("1", "4", "2", "3", "1", "2", "4", "1"):
                source.keyboard.press(key)
        source.locator("h1").click()
        source.evaluate("window.scrollTo(0, 0)")
        source.screenshot(path=str(OUT / f"signal-{mode}.png"), full_page=True)
        markup = source.locator(f'.{mode}-layout').evaluate("""node => {
            const clone = node.cloneNode(true);
            const fields = node.querySelectorAll('textarea');
            clone.querySelectorAll('textarea').forEach((field, index) => {
                field.textContent = fields[index].value;
            });
            return clone.outerHTML;
        }""")
        art.set_content(f'<!doctype html><html lang="ru"><meta charset="utf-8"><style>{scene_styles}</style><main class="github-scene">{markup}</main></html>')
        art.evaluate("document.fonts.ready")
        assert not art.evaluate("document.documentElement.scrollWidth > innerWidth || document.documentElement.scrollHeight > innerHeight")
        art.screenshot(path=str(OUT / f"signal-gallery-{mode}.png"))
    source.locator('[role="tab"][data-workshop-mode="signal"]').click()
    source.locator("h1").click()
    source.evaluate("window.scrollTo(0, 0)")
    source.screenshot(path=str(OUT / "signal-preview.png"), full_page=True)
    source.set_viewport_size({"width": 390, "height": 844})
    source.evaluate("window.scrollTo(0, 0)")
    source.screenshot(path=str(OUT / "signal-mobile.png"), full_page=True)
    browser.close()
print("Rendered signal cover and four scene previews in docs/.")
