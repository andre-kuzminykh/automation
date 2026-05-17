# Лекция 7 — Тесты и трассировка к требованиям

Пирамида: **Unit → Integration → E2E**.
Каждый тест связан с одним или несколькими ID `NR-Fx-y` / `NFR-Fx-y`.
У одного требования может быть несколько тестов.

| Уровень    | Где живут                       | Что тестируем                              |
|------------|---------------------------------|--------------------------------------------|
| Unit       | `l7/tests/unit/`                | Чистые функции / классы без I/O.           |
| Integration| `l7/tests/integration/`         | Пайплайн с mocked Hedra / mocked git.      |
| E2E        | `l7/tests/e2e/`                 | Полный прогон + браузерные UI-проверки.    |

---

## 1. Unit-тесты

### 1.1 `tests/unit/test_slide_repository.py`

| Test ID    | Что проверяет                                                                | Покрывает              |
|------------|------------------------------------------------------------------------------|------------------------|
| T-U-SR-1   | Все 50 слайдов имеют `id`, `title`, `narration`.                              | NR-F2-1, NR-F2-2       |
| T-U-SR-2   | `id` уникален и идёт 1..50.                                                   | NR-F2-2                |
| T-U-SR-3   | `text_sha256(narration)` детерминирован для одного и того же текста.          | NR-F2-3                |
| T-U-SR-4   | При отсутствии `narration` репозиторий бросает `SlidesSchemaError`.           | UC-F2-1-1, NR-F2-2     |
| T-U-SR-5   | JSON-schema валидация совпадает с поведением loader'а.                        | NFR-F2-1               |

### 1.2 `tests/unit/test_manifest_store.py`

| Test ID    | Что проверяет                                                          | Покрывает         |
|------------|------------------------------------------------------------------------|-------------------|
| T-U-MS-1   | `write_atomic(d)` создаёт `tmp` и переименовывает в финальный путь.    | NR-F2-4           |
| T-U-MS-2   | Если процесс упал между tmp и rename — старый manifest не сломан.      | NR-F2-4, NFR-F1-6 |
| T-U-MS-3   | UTF-8 без BOM, отступ 2, ключи отсортированы.                          | NFR-F2-2          |
| T-U-MS-4   | `merge_slide_result(...)` не теряет соседние слайды.                   | NR-F2-5           |

### 1.3 `tests/unit/test_retry.py`

| Test ID    | Что проверяет                                                          | Покрывает                |
|------------|------------------------------------------------------------------------|--------------------------|
| T-U-RT-1   | На статусах 429/500/502/503/504 ретраит до 4 раз.                       | NR-F1-6                  |
| T-U-RT-2   | Backoff = 2/4/8/16 секунд (с допустимым джиттером ≤ 1с).                | NR-F1-6, NFR-F1-5        |
| T-U-RT-3   | На 4xx (кроме 429) ретрая нет, исключение поднимается сразу.            | NR-F1-6                  |
| T-U-RT-4   | Бюджет одной попытки ≤ NFR-F1-5 (тайм-аут учитывается).                 | NFR-F1-5                 |

### 1.4 `tests/unit/test_hedra_client_mocked.py`

| Test ID    | Что проверяет                                                          | Покрывает                          |
|------------|------------------------------------------------------------------------|------------------------------------|
| T-U-HC-1   | `create_image_asset` шлёт POST на `/assets` с `type=image`.            | NR-F1-1, UC-F1-1-1                 |
| T-U-HC-2   | `upload_asset_binary` шлёт POST на `/assets/{id}/upload`, multipart.   | NR-F1-1, UC-F1-1-2                 |
| T-U-HC-3   | `submit_generation` шлёт POST с моделью «Hedra Avatar 540p», 1:1, aisala.| NR-F1-2, UC-F1-1-3                 |
| T-U-HC-4   | `get_generation_status` маппит ответ Hedra на enum (`complete/failed/in_progress`). | NR-F1-3, UC-F1-1-4   |
| T-U-HC-5   | `X-API-KEY` берётся из `os.environ["HEDRA_API_KEY"]` и НЕ логируется.  | NFR-F1-4                           |

---

## 2. Integration-тесты (mock Hedra)

### 2.1 `tests/integration/test_generate_pipeline_mock_hedra.py`

| Test ID    | Что проверяет                                                                                  | Покрывает                            |
|------------|------------------------------------------------------------------------------------------------|--------------------------------------|
| T-I-GP-1   | Прогон 3 слайдов: все три попадают в `videos/`, manifest `status=ok`.                          | NR-F1-1..F1-5, NR-F2-5               |
| T-I-GP-2   | Повторный прогон без изменения текста делает `skip` на всех трёх (idempotency).                | NR-F1-9, UC-F1-2-1                   |
| T-I-GP-3   | `--regenerate 2` форсирует только слайд 2; 1 и 3 остаются нетронутыми.                         | NR-F1-7, UC-F1-2-2                   |
| T-I-GP-4   | Если mock отдаёт `failed` на слайде 2 — слайды 1 и 3 успешны, exit code = 1.                   | NR-F1-5, NR-F1-8                     |
| T-I-GP-5   | Summary в stdout содержит `OK / SKIPPED / FAILED` со списком id.                               | NR-F1-8, UC-F1-3-1                   |
| T-I-GP-6   | Manifest пишется атомарно (между слайдами падение → старый manifest валиден).                  | NR-F2-4, NFR-F1-6                    |

### 2.2 `tests/integration/test_git_publisher.py` (фикстура — временный bare-репо)

| Test ID    | Что проверяет                                                                                  | Покрывает                       |
|------------|------------------------------------------------------------------------------------------------|---------------------------------|
| T-I-GIT-1  | `git_publisher.publish(videos)` создаёт ровно 1 коммит на пачку файлов.                         | NR-F4-1, UC-F4-1-1              |
| T-I-GIT-2  | Push идёт на `claude/setup-gcloud-video-service-XKVf0` (branch из config).                      | NR-F4-2                         |
| T-I-GIT-3  | При сбое сети push ретраится 4 раза с backoff 2/4/8/16.                                         | NR-F4-3                         |
| T-I-GIT-4  | Сообщение коммита соответствует шаблону `feat(l7): add hedra-generated videos for lecture 7`. | NFR-F4-2 (формат)               |
| T-I-GIT-5  | Превышение 500 MB → FATAL, push не делается.                                                    | NFR-F4-1                        |

---

## 3. E2E-тесты

### 3.1 `tests/e2e/test_one_slide_real_hedra.py` (manual / ondemand)

Запускается с реальным `HEDRA_API_KEY`. Не в CI по умолчанию.

| Test ID    | Что проверяет                                                                                  | Покрывает                            |
|------------|------------------------------------------------------------------------------------------------|--------------------------------------|
| T-E-RH-1   | Реальный прогон 1 слайда (10-20 секунд текста) даёт `videos/1.mp4` > 100 KB, MP4-валидный.    | NR-F1-1..F1-5, NFR-F1-1              |
| T-E-RH-2   | `voice_id=aisala`, `model="Hedra Avatar 540p"`, 1:1 — параметры реально приняты Hedra.         | NR-F1-2                              |
| T-E-RH-3   | `manifest.slides["1"].status == "ok"` и `file_sha256` совпадает с фактическим файлом.          | NR-F2-5                              |

### 3.2 `tests/e2e/test_html_player_playwright.py`

Запускает локальный HTTP-сервер, открывает `l7/index.html` в headless-Chromium,
подкладывает 3 фейковых mp4.

| Test ID    | Что проверяет                                                                       | Покрывает                |
|------------|-------------------------------------------------------------------------------------|--------------------------|
| T-E-UI-1   | Стартовый рендер: slide-0 видимый, `#bubble-video[src*="videos/1.mp4"]`.            | NR-F3-1, UC-F3-1-1       |
| T-E-UI-2   | ArrowRight: currentSlide=1, src = `videos/2.mp4`.                                   | NR-F3-2, UC-F3-1-2       |
| T-E-UI-3   | На последнем слайде ArrowRight не двигает.                                          | UC-F3-1-3                |
| T-E-UI-4   | Drag bubble → координата в localStorage, после reload восстанавливается.            | NR-F3-5, UC-F3-2-1..2-2  |
| T-E-UI-5   | Клик по bubble ставит/снимает паузу.                                                | NR-F3-6                  |
| T-E-UI-6   | `?pdf=1`: все 50 слайдов видимы, `#video-bubble` имеет `display:none`.              | NR-F3-7, UC-F3-4-1       |
| T-E-UI-7   | При отсутствии mp4 bubble показывает placeholder, страница не падает.               | NFR-F3-6                 |
| T-E-UI-8   | Прогресс-бар = 100% на slide-49.                                                    | NR-F3-8                  |
| T-E-UI-9   | Свайп влево/вправо переключает слайд на мобильной эмуляции.                         | NR-F3-4                  |

---

## 4. Матрица «требование → тесты»

Каждое требование должно быть покрыто хотя бы одним тестом.

| Требование    | Тесты                                                  |
|---------------|--------------------------------------------------------|
| NR-F1-1       | T-U-HC-1, T-U-HC-2, T-I-GP-1, T-E-RH-1                 |
| NR-F1-2       | T-U-HC-3, T-E-RH-2                                     |
| NR-F1-3       | T-U-HC-4, T-I-GP-1                                     |
| NR-F1-4       | T-I-GP-1, T-E-RH-1                                     |
| NR-F1-5       | T-I-GP-4                                               |
| NR-F1-6       | T-U-RT-1, T-U-RT-2, T-U-RT-3                           |
| NR-F1-7       | T-I-GP-3                                               |
| NR-F1-8       | T-I-GP-4, T-I-GP-5                                     |
| NR-F1-9       | T-I-GP-2                                               |
| NR-F1-10      | T-U-HC-*                                               |
| NFR-F1-1      | T-E-RH-1                                               |
| NFR-F1-2      | T-U-HC-5 (логи), JSON-формат проверяется регрессией    |
| NFR-F1-3      | CI-конфиг: matrix Python 3.10/3.11/3.12                |
| NFR-F1-4      | T-U-HC-5                                               |
| NFR-F1-5      | T-U-RT-2, T-U-RT-4                                     |
| NFR-F1-6      | T-U-MS-2, T-I-GP-6                                     |
| NR-F2-1       | T-U-SR-1                                               |
| NR-F2-2       | T-U-SR-1, T-U-SR-2, T-U-SR-4                           |
| NR-F2-3       | T-U-SR-3                                               |
| NR-F2-4       | T-U-MS-1, T-U-MS-2, T-I-GP-6                           |
| NR-F2-5       | T-U-MS-4, T-I-GP-1, T-E-RH-3                           |
| NFR-F2-1      | T-U-SR-5                                               |
| NFR-F2-2      | T-U-MS-3                                               |
| NR-F3-1       | T-E-UI-1, статический parser проверяет 50 контейнеров  |
| NR-F3-2       | T-E-UI-2                                               |
| NR-F3-3       | T-E-UI-2 (клавиатура), частично T-E-UI-9               |
| NR-F3-4       | T-E-UI-9                                               |
| NR-F3-5       | T-E-UI-4                                               |
| NR-F3-6       | T-E-UI-5                                               |
| NR-F3-7       | T-E-UI-6                                               |
| NR-F3-8       | T-E-UI-8                                               |
| NFR-F3-1      | Lighthouse PWA-checks в CI (опционально)               |
| NFR-F3-2      | T-E-UI-9 (mobile width)                                |
| NFR-F3-3      | визуальный snapshot (Playwright screenshot diff)        |
| NFR-F3-4      | axe-core в Playwright                                  |
| NFR-F3-5      | T-E-UI-5                                               |
| NFR-F3-6      | T-E-UI-7                                               |
| NR-F4-1       | T-I-GIT-1                                              |
| NR-F4-2       | T-I-GIT-2                                              |
| NR-F4-3       | T-I-GIT-3                                              |
| NFR-F4-1      | T-I-GIT-5                                              |
| NFR-F4-2      | T-I-GIT-4                                              |
| NFR-F4-3      | T-I-GIT-1                                              |
| NR-F5-1       | smoke-тест на dev VM (manual)                          |
| NR-F5-2       | smoke-тест на dev VM (manual)                          |
| NR-F5-3       | smoke-тест на dev VM (manual)                          |
| NFR-F5-1      | grep-сканер git-истории (CI)                           |
| NFR-F5-2      | README + checklist при ревью                           |
| NFR-F5-3      | хронометраж bootstrap.sh (вывод в логи)                |
| NFR-F5-4      | sudo-less проверка в bootstrap.sh                      |

---

## 5. Что НЕ тестируется в MVP

* Бесшовная ротация ключа Hedra без рестарта (out of scope).
* Точность речи синтеза (это SLA Hedra, не наш).
* Цветовая идентичность аватара (мы не оптимизируем JPEG, доверяем Hedra).
* Качество визуальной инфографики на каждом слайде (визуально-ручная проверка).
