import test from 'node:test';
import assert from 'node:assert/strict';
import i18n from '../lib/i18n.js';

test('language links and saved choice precede browser preferences', () => {
  assert.equal(i18n.resolveLanguage('?other=1&lang=ru', 'en', ['en-US']), 'ru');
  assert.equal(i18n.resolveLanguage('?lang=fr', 'ru', ['en-US']), 'ru');
  assert.equal(i18n.resolveLanguage('', null, ['de-DE', 'ru-RU']), 'ru');
  assert.equal(i18n.resolveLanguage('', null, ['en-US', 'ru']), 'en');
  assert.equal(i18n.resolveLanguage('', null, ['de']), 'en');
});
test('scene messages and interpolation are localized without touching user content', () => {
  assert.equal(i18n.t('знак {index}: {name}', { index: 2, name: 'мои слова' }, 'en'), 'sign 2: мои слова');
  assert.equal(i18n.t('сигнал пока пустой', {}, 'en'), 'your signal is empty');
  assert.equal(i18n.t('сигнал пока пустой', {}, 'ru'), 'сигнал пока пустой');
  assert.ok(Object.values(i18n.translations).every(value => value.trim() && !/[—–]/.test(value)));
});

test('every message preserves its interpolation tokens', () => {
  const tokens = value => [...value.matchAll(/\{[^{}]+\}/g)].map(match => match[0]).sort();
  for (const [source, translated] of Object.entries(i18n.translations)) {
    assert.deepEqual(tokens(translated), tokens(source), source);
  }
});
