# signal companion implementation plan

**Goal:** apply the author's October 14 feedback to the existing local workshop.

**Architecture:** preserve the state codec and scene actions. Replace the presentation around a single sticky mascot, with source-only HTML/CSS changes and a small runtime message update. Rebuild generated assets normally.

**Tech stack:** HTML, CSS, native JavaScript, Python builder, Playwright.

- [x] Extend `site/verify.py` with companion visibility, scene messages, and all-scene responsive checks. Confirm the missing companion assertion fails.
- [x] Replace the hero and navigation in `site/sections/workshop.html`; retain existing scene hooks, group labels and tab semantics. Remove scene indices and duplicate mascot images.
- [x] Replace `site/sections/workshop.css` with a warm, softly rounded layout and responsive sticky companion. Keep focus, touch controls, drag feedback and reduced motion.
- [x] Add matching vector logo and favicon using the local typeface and an original folded pulse mark. Keep media local and build-managed.
- [x] Update companion messages and authored UI/export copy in `site/sections/workshop.js`; update metadata in `site/build.py`. Do not change state identifiers or user text.
- [x] Run build, pytest, node tests and browser verification; inspect desktop/mobile and all four scenes. Check subpath operation and exported files. Update stale product documentation and screenshots.

Validation: 2 Python tests and 9 Node tests pass. Browser verification covers five viewport sizes, all four scenes and 11 interaction groups. Additional checks confirm nested-path assets, a 1400×900 PNG and offline HTML with embedded logo, mascot and fonts. Independent source and browser review found no actionable issues.
