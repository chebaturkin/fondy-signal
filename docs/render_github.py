"""Capture the README screenshots and scene gallery from the running workshop.

Build the site and start site/serve.py on port 8799 before running this file.
Requires the same Playwright/Chromium installation as site/verify.py.
"""
from __future__ import annotations

import base64
import argparse
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
styles = (ROOT / "site/base.css").read_text() + (ROOT / "site/sections/workshop.css").read_text()
scene_styles = f'''{styles}\n{fonts}
html,body{{width:860px;height:440px;overflow:hidden;margin:0;scroll-behavior:auto}}
body{{display:grid;place-items:center;padding:28px;background:#fff8ed}}
.github-scene{{width:100%;min-width:0}}
.github-scene>div{{margin-top:0}}
*{{animation:none!important;transition:none!important}}
'''
def render(language):
    OUT = ROOT / "docs" / ("en" if language == "en" else "")
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        art = browser.new_page(viewport={"width": 860, "height": 440}, device_scale_factor=1)
        source = browser.new_page(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
        response = source.goto("http://127.0.0.1:8799/?lang=" + language, wait_until="networkidle")
        assert response and response.status == 200
        for token in ("pulse", "spark", "wave", "anchor"):
            source.locator(f'.token-choice[data-token="{token}"]').click()
        art.set_viewport_size({"width": 860, "height": 440})
        for mode in ("signal", "pause", "letter", "rhythm"):
            source.locator(f'[role="tab"][data-workshop-mode="{mode}"]').click()
            if mode == "letter":
                source.locator('[data-letter-note]').fill("я рядом. можно без слов." if language == "ru" else "I'm here. words are optional.")
                source.locator('[data-note-token="wave"]').click()
                source.locator('[data-letter-submit]').click()
            if mode == "rhythm":
                for key in ("1", "4", "2", "3", "1", "2", "4", "1"):
                    source.keyboard.press(key)
            source.locator("h1").click()
            source.evaluate("window.scrollTo(0, 0)")
            markup = source.locator(f'.{mode}-layout').evaluate("""node => {
                const clone = node.cloneNode(true);
                const fields = node.querySelectorAll('textarea');
                clone.querySelectorAll('textarea').forEach((field, index) => {
                    field.textContent = fields[index].value;
                });
                return clone.outerHTML;
            }""")
            art.set_content(f'<!doctype html><html lang="{language}"><meta charset="utf-8"><style>{scene_styles}</style><main class="github-scene">{markup}</main></html>')
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture real Russian and English workshop previews.")
    parser.add_argument("--lang", choices=["ru", "en", "all"], default="all")
    args = parser.parse_args()
    for language in (["ru", "en"] if args.lang == "all" else [args.lang]):
        render(language)
    print("Rendered signal previews from the running workshop in both selected languages.")
