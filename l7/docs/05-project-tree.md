# Лекция 7 — Дерево проекта

```
automation/                                  # корневой репозиторий
└── l7/                                      # пакет лекции 7
    ├── index.html                           # 50 слайдов + video-bubble (F3)
    ├── README.md                            # быстрый запуск, скачивание видео
    │
    ├── data/                                # источник правды
    │   ├── slides.json                      # 50 слайдов: id, title, narration
    │   ├── slides.schema.json               # JSON-schema для валидации
    │   ├── config.json                      # endpoint, model, voice, paths
    │   ├── avatar.jpg                       # фото для Hedra (скачан с ibb)
    │   └── manifest.json                    # output: статус каждого слайда (создаётся скриптом)
    │
    ├── videos/                              # output: 50 mp4 (создаются скриптом)
    │   ├── 1.mp4
    │   ├── 2.mp4
    │   └── ...
    │
    ├── service/                             # бэкенд (Python CLI)
    │   ├── __init__.py
    │   ├── generate.py                      # CLI entrypoint (F1)
    │   ├── hedra_client.py                  # HTTP-обёртка над api.hedra.com
    │   ├── slide_repository.py              # чтение/валидация slides.json
    │   ├── manifest_store.py                # атомарная запись manifest.json
    │   ├── git_publisher.py                 # git add/commit/push с retry
    │   ├── logging_setup.py                 # structured JSON logs
    │   ├── retry.py                         # backoff helper
    │   ├── bootstrap.sh                     # gcloud VM bootstrap (F5)
    │   ├── requirements.txt                 # pip deps
    │   └── README.md                        # запуск сервиса
    │
    ├── tests/                               # пирамида тестов (см. 06-tests.md)
    │   ├── unit/
    │   │   ├── test_slide_repository.py
    │   │   ├── test_manifest_store.py
    │   │   ├── test_retry.py
    │   │   └── test_hedra_client_mocked.py
    │   ├── integration/
    │   │   ├── test_generate_pipeline_mock_hedra.py
    │   │   └── test_git_publisher.py
    │   ├── e2e/
    │   │   ├── test_one_slide_real_hedra.py    # требует HEDRA_API_KEY
    │   │   └── test_html_player_playwright.py  # ставит mp4-фейки, проверяет UI
    │   └── fixtures/
    │       ├── slides_3.json
    │       ├── hedra_responses.json
    │       └── avatar.jpg
    │
    └── docs/                                # эта декомпозиция
        ├── 01-features-stories.md
        ├── 02-use-cases-bdd.md
        ├── 03-requirements.md
        ├── 04-architecture.md
        ├── 05-project-tree.md
        ├── 06-tests.md
        └── 07-task-sequence.md
```

## Размеры и лимиты

| Что                | Лимит / ожидание                                 |
|--------------------|--------------------------------------------------|
| `slides.json`      | ~30 KB (50 слайдов с дословным текстом)          |
| `avatar.jpg`       | ~500 KB (рекомендуется 1024×1024, JPEG q=85)     |
| Одно видео         | 540p 1:1, 30-90 сек, ~3-10 MB                    |
| Все 50 видео       | ~150-500 MB (попадает в обычный git, без LFS)    |
| `manifest.json`    | ~10 KB                                           |

## Что попадает в git, что нет

| Путь                          | В git? | Причина                                  |
|-------------------------------|--------|------------------------------------------|
| `l7/index.html`               | ✅     | страница лекции                          |
| `l7/data/slides.json`         | ✅     | источник правды                          |
| `l7/data/slides.schema.json`  | ✅     | контракт                                  |
| `l7/data/config.json`         | ✅     | конфиг без секретов                       |
| `l7/data/avatar.jpg`          | ✅     | референс-фото для Hedra (опубликовать ок) |
| `l7/data/manifest.json`       | ✅     | финальный артефакт прогона                |
| `l7/videos/*.mp4`             | ✅     | артефакты, нужны странице                 |
| `l7/service/**`               | ✅     | код                                      |
| `l7/tests/**`                 | ✅     | код                                      |
| `l7/docs/**`                  | ✅     | документация                             |
| `.venv/`, `__pycache__/`      | ❌     | сборочный мусор                          |
| `.env`, `*.key`, `secrets/`   | ❌     | секреты                                  |
| `.tmp/`, `*.log`              | ❌     | логи прогонов                            |
