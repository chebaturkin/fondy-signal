# работа над signal

signal работает целиком в браузере. правки интерфейса делаются в `site/sections`, логика состояния находится в `site/lib`, а персонаж, логотип, фавикон и шрифты хранятся в `brand-kit`.

перед отправкой изменений пересобери сайт и запусти проверки:

```bash
python3 site/build.py
python3 -m pytest -q site/tests
node --test site/tests/test_workshop_state.mjs site/tests/test_workshop_contract.mjs
```

для проверки в браузере запусти `python3 site/serve.py --port 8799`, затем `python3 site/verify.py`.

не редактируй `site/assets`, `site/index.html` и `site/public` вручную: это результаты сборки. сохраняй относительные пути, управление с клавиатуры и поведение при `prefers-reduced-motion: reduce`. не добавляй секреты, сетевые зависимости или трекинг.
