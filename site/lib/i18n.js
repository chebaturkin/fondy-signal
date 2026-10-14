/* Local authored translations. User note content never passes through this dictionary. */
(function (root, factory) {
  const messages = root.SignalMessages || (typeof module === 'object' && module.exports ? require('./messages.json') : {});
  const api = factory(messages);
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.SignalI18n = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (translations) {
  let language = 'en';
  const preferenceKey = 'signal-language';
  function resolveLanguage(search, saved, languages) {
    const explicit = new URLSearchParams(search).get('lang');
    if (explicit === 'ru' || explicit === 'en') return explicit;
    if (saved === 'ru' || saved === 'en') return saved;
    for (const value of languages || []) {
      const primary = value.toLowerCase().split('-')[0];
      if (primary === 'ru' || primary === 'en') return primary;
    }
    return 'en';
  }
  function t(message, values = {}, locale = language) {
    const plain = String(message).trim();
    const source = String(message);
    const text = locale === 'ru' ? source : translations[source] ?? (translations[plain] ? source.replace(plain, translations[plain]) : source);
    return text.replace(/\{(\w+)\}/g, (match, name) => String(values[name] ?? match));
  }
  function applyBindings(scope = document) {
    scope.querySelectorAll('[data-i18n-parts]').forEach(node => {
      const parts = JSON.parse(node.dataset.i18nParts);
      const nodes = [...node.childNodes].filter(child => child.nodeType === 3 && child.textContent.trim());
      nodes.forEach((child, index) => { if (parts[index] !== undefined) child.textContent = t(parts[index]); });
    });
    for (const attribute of ['aria-label', 'title', 'placeholder', 'content', 'alt']) {
      scope.querySelectorAll('[data-i18n-' + attribute + ']').forEach(node => node.setAttribute(attribute, t(node.getAttribute('data-i18n-' + attribute))));
    }
  }
  function updateControls() {
    document.documentElement.lang = language;
    document.querySelectorAll('[data-language]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.language === language)));
  }
  function setLanguage(next) {
    if (!['ru', 'en'].includes(next)) return;
    const changed = language !== next;
    language = next;
    try { localStorage.setItem(preferenceKey, next); } catch (_) { /* Keep working without storage. */ }
    try { const url = new URL(location.href); url.searchParams.set('lang', next); history.replaceState(null, '', url); } catch (_) { /* Local file or blocked history. */ }
    if (!changed) { updateControls(); return; }
    applyBindings(); updateControls();
    window.dispatchEvent(new CustomEvent('signal:languagechange'));
  }
  function init() {
    let saved = null;
    try { saved = localStorage.getItem(preferenceKey); } catch (_) { /* Use browser preference. */ }
    language = resolveLanguage(location.search, saved, navigator.languages || [navigator.language]);
    applyBindings(); updateControls();
    document.querySelectorAll('[data-language]').forEach(button => button.addEventListener('click', () => setLanguage(button.dataset.language)));
  }
  return { translations, resolveLanguage, t, applyBindings, setLanguage, init, getLanguage: () => language };
});
