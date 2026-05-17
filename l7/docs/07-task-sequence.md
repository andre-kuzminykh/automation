# Лекция 7 — Последовательность задач

Декомпозиция:
**Эпик (фича) → задача (должна пройти тесты) → подзадача (имеет AC).**

Все задачи внутри фазы можно решать в любом порядке, но **переход к
следующей фазе только после прохождения тестов предыдущей**.

---

## Фаза 0 — Скелет репозитория

| #   | Задача                                                       | Подзадачи (AC = Acceptance Criteria)                                                                                                | Тесты                  |
|-----|--------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|------------------------|
| 0.1 | Создать `l7/data/slides.json`                                | AC1: файл валиден по схеме; AC2: 50 записей; AC3: каждая имеет id/title/narration                                                   | T-U-SR-1, T-U-SR-2     |
| 0.2 | Создать `l7/data/slides.schema.json`                         | AC1: schema-validate проходит на `slides.json`; AC2: ломается на удалении `narration`                                                | T-U-SR-5               |
| 0.3 | Создать `l7/data/config.json`                                | AC1: содержит hedra, gcloud, git, output блоки; AC2: API-ключ через env                                                              | —                      |
| 0.4 | `.gitignore` обновлён (.env, .venv, secrets/)                | AC1: `git check-ignore .env` возвращает 0                                                                                            | grep-сканер            |
| 0.5 | `l7/docs/` — все 7 документов фреймворка                     | AC1: все 7 файлов созданы; AC2: links между ними рабочие                                                                              | manual review          |

Готовность фазы: `python -c "import json; json.load(open('l7/data/slides.json'))"` ok, репо чистый.

---

## Фаза 1 — Сервис (бэкенд)

| #   | Задача                                                  | Подзадачи (AC)                                                                                              | Тесты                                  |
|-----|---------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|----------------------------------------|
| 1.1 | `l7/service/retry.py`                                   | AC1: backoff 2/4/8/16; AC2: не ретраит 4xx≠429; AC3: учёт бюджета                                            | T-U-RT-1..4                            |
| 1.2 | `l7/service/logging_setup.py`                           | AC1: JSON-структура на stderr; AC2: маска `sk_***` в полях `api_key`/`Authorization`                         | T-U-HC-5                               |
| 1.3 | `l7/service/hedra_client.py`                            | AC1: методы create_asset/upload_binary/submit/get_status/download; AC2: использует retry.py; AC3: env-ключ   | T-U-HC-1..5                            |
| 1.4 | `l7/service/slide_repository.py`                        | AC1: load+validate; AC2: text_sha256; AC3: исключение `SlidesSchemaError` при поломке                        | T-U-SR-1..5                            |
| 1.5 | `l7/service/manifest_store.py`                          | AC1: write_atomic (tmp+rename); AC2: merge_slide_result не теряет соседей; AC3: utf-8 без BOM                | T-U-MS-1..4                            |
| 1.6 | `l7/service/git_publisher.py`                           | AC1: add+commit+push в нужную ветку; AC2: retry 4x backoff; AC3: проверка 500 MB                              | T-I-GIT-1..5                           |
| 1.7 | `l7/service/generate.py` (CLI)                          | AC1: 50 слайдов; AC2: idempotent skip; AC3: --regenerate, --limit, --from, --to; AC4: summary                | T-I-GP-1..6                            |
| 1.8 | `l7/service/requirements.txt`                           | AC1: pinned versions; AC2: только `requests` и стандарт                                                       | pip install passes                     |
| 1.9 | `l7/service/bootstrap.sh`                               | AC1: apt installs; AC2: venv+pip; AC3: idempotent; AC4: печатает READY                                       | smoke на dev VM                        |

Готовность фазы: все unit/integration тесты зелёные, dry-run на 3 фейк-слайдах создаёт 3 mp4-заглушки в temp.

---

## Фаза 2 — Плеер (фронт)

| #   | Задача                                                  | Подзадачи (AC)                                                                                              | Тесты                              |
|-----|---------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|------------------------------------|
| 2.1 | Скелет HTML (head, Tailwind, body, прогресс-бар)        | AC1: загрузка без CSS-варнингов; AC2: brand colors определены                                                | T-E-UI-1 (header)                  |
| 2.2 | 50 слайдов с инфографикой (по таблице)                  | AC1: 50 `.slide-container`; AC2: id="slide-0..49"; AC3: содержание совпадает с title/narration               | NR-F3-1 grep-проверка              |
| 2.3 | JS-навигация (kb / mouse / swipe / прогресс)            | AC1: → ← Space Enter; AC2: touch swipe; AC3: контекст-меню отключён                                          | T-E-UI-2, T-E-UI-9                 |
| 2.4 | Видео-bubble (HTML + CSS)                               | AC1: `#video-bubble`+`#bubble-video`; AC2: overlay+loader; AC3: фикс. позиция/стартовый угол                  | T-E-UI-1                           |
| 2.5 | JS видео-логика (src per slide, play/pause, errors)     | AC1: `videoSrcFor(idx)`= `videos/${idx+1}.mp4`; AC2: pause/play overlay; AC3: error → placeholder            | T-E-UI-2, T-E-UI-5, T-E-UI-7       |
| 2.6 | JS drag-and-snap + localStorage                         | AC1: mouse+touch drag; AC2: snap к границам 16px; AC3: persisted position                                     | T-E-UI-4                           |
| 2.7 | PDF-режим (`?pdf=1` / `#pdf`)                           | AC1: все слайды видимы; AC2: bubble скрыт; AC3: print css                                                     | T-E-UI-6                           |
| 2.8 | Прогресс-бар                                            | AC1: width = (cur+1)/50*100%                                                                                  | T-E-UI-8                           |

Готовность фазы: открытие l7/index.html в Chrome — листается, видео меняется (с фейками), drag работает, PDF-режим работает.

---

## Фаза 3 — Конвейер «реальный Hedra» (на gcloud VM)

| #   | Задача                                            | Подзадачи (AC)                                                                                            | Тесты               |
|-----|---------------------------------------------------|-----------------------------------------------------------------------------------------------------------|---------------------|
| 3.1 | Скачать `avatar.jpg` локально                      | AC1: файл существует; AC2: ≤ 1 MB; AC3: dimensions ≥ 512×512                                              | manual              |
| 3.2 | Запуск `bootstrap.sh` на `human-1`                 | AC1: READY; AC2: `python3 --version` ≥ 3.10; AC3: `ffmpeg -version` ok                                    | smoke               |
| 3.3 | Прогон 1 слайда (--limit 1)                        | AC1: `videos/1.mp4` ≥ 100 KB; AC2: воспроизводится; AC3: лицо аватара совпадает с фото                     | T-E-RH-1, T-E-RH-2  |
| 3.4 | Полный прогон 50 слайдов                           | AC1: 50 mp4; AC2: 0 failed; AC3: ≤ 4 часа полного времени                                                  | T-E-RH-3            |
| 3.5 | Coммит и push в ветку                              | AC1: 1 коммит; AC2: видео доступны на raw.githubusercontent через 1-2 мин                                  | T-I-GIT-1..4        |

Готовность фазы: ветка `claude/setup-gcloud-video-service-XKVf0` содержит 50 mp4, `l7/index.html` показывает их.

---

## Фаза 4 — Контроль качества

| #   | Задача                                          | Подзадачи (AC)                                                                                        | Тесты               |
|-----|-------------------------------------------------|-------------------------------------------------------------------------------------------------------|---------------------|
| 4.1 | Прогон Playwright E2E локально                  | AC1: все T-E-UI-* зелёные; AC2: visual diff пройден                                                   | T-E-UI-*            |
| 4.2 | Lighthouse desktop                              | AC1: Performance ≥ 80; AC2: Accessibility ≥ 90                                                        | NFR-F3-1, NFR-F3-4  |
| 4.3 | Спот-проверка озвучек                           | AC1: ручной просмотр 5 случайных слайдов; AC2: соответствие тексту и аватару                          | manual              |
| 4.4 | README обновлён                                 | AC1: команда быстрого запуска; AC2: ссылка на gcloud SSH; AC3: ссылка на лекцию                       | review              |

---

## Последовательность по дням (оценка)

| День | Что делаем                                                    | Артефакт                                       |
|------|----------------------------------------------------------------|------------------------------------------------|
| 1    | Фаза 0 + декомпозиция (этот документ)                          | docs/ + data/                                  |
| 2    | Фаза 1 (сервис) + unit/integration тесты                       | service/ + tests/                              |
| 3    | Фаза 2 (плеер)                                                  | index.html                                     |
| 4    | Фаза 3 на gcloud — 1 пробный + 50 mp4 (часа 3-4 ожидания API)  | videos/, manifest.json, push                   |
| 5    | Фаза 4 — QA, доводки                                            | review                                         |

---

## Definition of Done

Лекция готова, когда:

1. Все тесты из `06-tests.md` зелёные (или явно помечены как «manual smoke»).
2. `l7/videos/{1..50}.mp4` лежат в ветке и весят суммарно ≤ 500 MB.
3. `l7/index.html` открывается в браузере и играет видео при листании.
4. `l7/data/manifest.json` имеет 50 записей со статусом `ok` (или мотивированные `failed`).
5. Нет секретов в коммитах, `.gitignore` корректен.
6. `l7/service/README.md` объясняет, как воспроизвести прогон с нуля.
