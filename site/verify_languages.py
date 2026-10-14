"""Exercise both languages, live draft preservation and portable cards locally."""
import os
from pathlib import Path
from playwright.sync_api import expect, sync_playwright

BASE = os.environ.get('SIGNAL_URL', 'http://127.0.0.1:8799/')
OUT = Path(__file__).resolve().parent / 'previews' / 'workshop'
OUT.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(locale='en-US', reduced_motion='reduce')
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(BASE + '?lang=en&keep=1', wait_until='networkidle')
    expect(page.locator('html')).to_have_attribute('lang', 'en')
    assert 'send a' in page.locator('h1').inner_text()
    for token in ['pulse', 'spark']:
        page.locator(f'.token-choice[data-token="{token}"]').click()
    notice = page.locator('[data-workshop-status]').inner_text()
    page.locator('[data-language="en"]').click()
    assert page.locator('[data-workshop-status]').inner_text() == notice
    page.locator('[role="tab"][data-workshop-mode="letter"]').click()
    page.locator('[data-letter-note]').fill('мои слова остаются моими')
    before = page.evaluate('JSON.stringify(window.__signalWorkshop.getState())')
    before_hash = page.evaluate('location.hash')
    page.locator('[data-language="ru"]').click()
    expect(page.locator('html')).to_have_attribute('lang', 'ru')
    assert page.locator('[data-letter-note]').input_value() == 'мои слова остаются моими'
    assert page.evaluate('JSON.stringify(window.__signalWorkshop.getState())') == before
    assert page.evaluate('location.hash') == before_hash and 'keep=1' in page.url
    page.locator('[data-letter-submit]').click()
    page.locator('[data-language="en"]').click()
    assert page.locator('[data-envelope-note]').inner_text() == 'мои слова остаются моими'
    with page.expect_download() as info:
        page.locator('[data-workshop-action="portable"]').click()
    file = OUT / 'language-card.html'
    info.value.save_as(file)
    portable = file.read_text()
    assert '<html lang="en">' in portable and 'мои слова остаются моими' in portable
    assert 'a card from fondy' in portable and 'открытка из мастерской' not in portable
    # Slow assets must not mix export languages or scene state.
    page.evaluate("""() => {
        const original = window.fetch.bind(window);
        window.fetch = async (...args) => {
            if (String(args[0]).includes('signal-logo.svg')) {
                window.__exportWaiting = true;
                await new Promise(resolve => { window.__releaseExport = resolve; });
            }
            return original(...args);
        };
    }""")
    with page.expect_download() as delayed:
        page.locator('[data-workshop-action="portable"]').click()
        page.wait_for_function('window.__exportWaiting === true')
        page.locator('[data-language="ru"]').click()
        page.locator('[role="tab"][data-workshop-mode="signal"]').click()
        page.evaluate('window.__releaseExport()')
    delayed_file = OUT / 'language-card-delayed.html'
    delayed.value.save_as(delayed_file)
    delayed_html = delayed_file.read_text()
    assert '<html lang="en">' in delayed_html
    assert '<title id="export-title">fold a note</title>' in delayed_html
    assert 'мои слова остаются моими' in delayed_html
    assert 'открытка из мастерской' not in delayed_html
    page.locator('[data-language="en"]').click()
    page.goto(BASE, wait_until='networkidle')
    expect(page.locator('html')).to_have_attribute('lang', 'en')
    for lang in ['ru', 'en']:
        page.locator(f'[data-language="{lang}"]').click()
        for width in [320, 390, 768, 1440]:
            page.set_viewport_size({'width': width, 'height': 960})
            for mode in ['signal', 'pause', 'letter', 'rhythm']:
                page.locator(f'[role="tab"][data-workshop-mode="{mode}"]').click()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (lang, width, mode)
        page.locator('[role="tab"][data-workshop-mode="pause"]').click()
        page.locator('[data-pause-step="1"]').click()
        assert '1 / 4' in page.locator('[data-pause-progress-label]').inner_text()
    for locale, expected in [('ru-RU', 'ru'), ('en-US', 'en'), ('de-DE', 'en')]:
        context = browser.new_context(locale=locale)
        fresh = context.new_page()
        fresh.goto(BASE, wait_until='networkidle')
        expect(fresh.locator('html')).to_have_attribute('lang', expected)
        context.close()
    context = browser.new_context(locale='en-US')
    context.add_init_script("Object.defineProperty(window, 'localStorage', {get(){throw new Error('blocked')}})")
    fresh = context.new_page()
    fresh.goto(BASE, wait_until='networkidle')
    fresh.locator('[data-language="ru"]').click()
    expect(fresh.locator('html')).to_have_attribute('lang', 'ru')
    assert not errors, errors
    browser.close()
print('languages passed: preference, draft and hash preservation, card export, four scenes, 32 layouts and blocked storage')
