# Лекция 7 — Архитектура

Порядок по фреймворку:
1. Клиентская часть (UX/UI).
2. ИИ-сервисы и промты.
3. Бэкенд-сервисы.
4. ER-диаграмма данных + DFD.
5. Инфраструктура.
6. Дерево проекта.

---

## 1. Клиентская часть — UX и UI

### 1.1 UX (как пользователь движется по странице)

Вытаскивается напрямую из UF-F3-1..3-4.

```
открытие index.html
        ↓
рендер слайда 0 (титул) + автозагрузка videos/1.mp4 в bubble
        ↓
[ → / клик / свайп ]
        ↓
переход на slide-N (N = 1..49)
        ↓
bubble.src ← videos/(N+1).mp4
        ↓
[опционально] drag bubble в угол → snap + сохранить позицию
        ↓
[опционально] клик по bubble → pause/play
        ↓
[опционально] ?pdf=1 → разворачивание всех 50 слайдов для печати
```

### 1.2 UI (компоненты страницы)

| Компонент          | Назначение                                                              | Покрывает NR    |
|--------------------|-------------------------------------------------------------------------|-----------------|
| `.slide-container` | 50 контейнеров `slide-0..slide-49`. Один активен.                       | NR-F3-1         |
| `#progress-bar`    | Полоска внизу, показывает текущую позицию.                              | NR-F3-8         |
| `#video-bubble`    | Drag-and-drop контейнер для `<video id="bubble-video">`.                | NR-F3-5         |
| `#video-overlay`   | Полупрозрачный слой с иконкой play/pause.                               | NR-F3-6         |
| `#video-loader`    | Чёрный лоадер во время буферизации.                                     | UC-F3-3-2       |
| `body.pdf-export-mode` | Класс, переключающий вёрстку на печатный вид.                       | NR-F3-7         |
| Декорат. фон       | `bg-glow-1`, `bg-glow-2` — фирменное свечение.                          | NFR-F3-3        |

### 1.3 Слайд-инфографики (визуальные паттерны)

50 слайдов используют ротацию ~10 «инфо-шаблонов», как в `l6` и в примере `aisala/6`:

1. **Title** — большой заголовок + чипы перехода `Человек → Гибрид → AI-First`.
2. **Сравнение «Было / Стало»** — две колонки с разной иконографикой.
3. **Карточная сетка 3×2 / 4×1** — для «зон ответственности», «фаз», «вопросов».
4. **Stack пирамида** — для «слоёв организации» (UI / контекст / решения / ответственность).
5. **Сценарии 1–4** — карточки с номером и значком (режимы самостоятельности).
6. **Boundary** — две колонки с линией-разделителем по центру (граница человек/AI).
7. **Loop / cycle** — круговая схема (фазы портфеля, ритм).
8. **Quote / formula** — крупная цитата на градиенте (финальный вывод).
9. **Checklist** — список с галочками (7 контрольных вопросов).
10. **Roles board** — карточки ролей с аватарами (новые роли).

Цвета: brand purple `#7c3aed`, brand orange `#f97316`, акценты — blue / pink в градиенте.
Иконки — Phosphor Icons (`<i class="ph-fill ph-xxx">`).

---

## 2. ИИ-сервисы и промты

В системе один ИИ-сервис: **Hedra (Avatar 540p)**.

### 2.1 Hedra Avatar 540p — text + image → talking-head video

| Параметр           | Значение                                                |
|--------------------|---------------------------------------------------------|
| Endpoint base      | `https://api.hedra.com/web-app/public`                  |
| Auth               | Header `X-API-KEY: $HEDRA_API_KEY`                      |
| Модель             | `Hedra Avatar 540p`                                     |
| Разрешение         | `540p`                                                  |
| Aspect ratio       | `1:1`                                                   |
| Голос              | `aisala` (preset)                                       |
| Источник аватара   | загруженный JPEG (URL: `i.ibb.co/VcCKP5Kg/...jpg`)      |
| Источник речи      | поле `text` запроса = `slides[i].narration`             |

#### 2.1.1 Промт (text payload)

Hedra использует Voice-TTS, отдельного «system prompt» нет. Единственный
текстовый ввод — это **дословный narration** из `slides.json`. Никаких
системных добавок / обёрток — текст в видео должен совпадать со слайдом.

#### 2.1.2 Промты для (опциональной) генерации иллюстраций слайдов

Не входит в MVP. Закладываем расширение: если позже понадобится Midjourney/Imagen
для визуальных иллюстраций на слайды, схема промта:

```
You are creating a 1024x1024 educational illustration for a corporate AI-transformation course.
Style: minimalist, flat, brand colors purple #7c3aed and orange #f97316, generous white space, no text on image.
Topic: «{slide.title}»
Concept: {slide.narration first 3 sentences}
```

Этот ИИ-сервис в MVP не используется — инфографика рисуется HTML/Tailwind руками.

---

## 3. Бэкенд-сервисы

### 3.1 VideoGenerationService (Python CLI)

Оркестратор. Точка входа — `l7/service/generate.py`.

**Ответственность:** прочитать `slides.json`, обеспечить `avatar.jpg`, для каждого слайда
сделать цикл «submit → poll → download → write manifest».

**Входы:** CLI-аргументы, `slides.json`, `config.json`, `HEDRA_API_KEY`.
**Выходы:** `videos/{1..50}.mp4`, `data/manifest.json`, exit code.

### 3.2 HedraClient

Тонкая обёртка над HTTP API Hedra. Только сетевые вызовы.

| Метод                              | Endpoint                       | Возвращает              |
|------------------------------------|--------------------------------|-------------------------|
| `create_image_asset(name)`         | POST `/assets`                 | `asset_id`              |
| `upload_asset_binary(asset_id, p)` | POST `/assets/{id}/upload`     | `200 OK`                |
| `submit_generation(...)`           | POST `/generations`            | `generation_id`         |
| `get_generation_status(id)`        | GET  `/generations/{id}/status`| `{status, video_url}`   |
| `download(url, path)`              | GET  `url`                     | `bytes → file`          |

Все методы используют общий `_request` с retry/backoff (NR-F1-6).

### 3.3 SlideRepository

Читает `slides.json`, валидирует по схеме, выдаёт итератор слайдов.
Считает `text_sha256`.

### 3.4 ManifestStore

Атомарная запись `data/manifest.json` через tmp+rename (NR-F2-4).

### 3.5 GitPublisher

Делает `git add`, `git commit`, `git push -u origin <branch>` с retry. (US-F4-1)

### 3.6 Зависимости между сервисами

```
CLI generate.py
   ├─→ SlideRepository (slides.json)
   ├─→ HedraClient (api.hedra.com)
   ├─→ ManifestStore (data/manifest.json)
   └─→ GitPublisher (origin)
```

---

## 4. ER-диаграмма данных

Данные хранятся как JSON в репозитории — собственной БД нет.

```
            ┌─────────────────────────┐
            │        Lecture          │
            │─────────────────────────│
            │ id (PK)        : "l7"   │
            │ title          : str    │
            │ subtitle       : str    │
            │ language       : "ru"   │
            └────────────┬────────────┘
                         │ 1
                         │
                         │ N
            ┌────────────┴────────────┐
            │         Slide           │
            │─────────────────────────│
            │ id        (PK)  : 1..50 │
            │ title           : str   │
            │ narration       : str   │
            │ text_sha256     : str   │
            └────────────┬────────────┘
                         │ 1
                         │
                         │ 0..N
            ┌────────────┴────────────┐
            │     GenerationJob       │
            │─────────────────────────│
            │ slide_id (FK)   : int   │
            │ hedra_generation_id     │
            │ status          : enum  │
            │ submitted_at    : ts    │
            │ finished_at     : ts    │
            │ error           : str?  │
            └────────────┬────────────┘
                         │ 0..1
                         │
            ┌────────────┴────────────┐
            │       VideoFile         │
            │─────────────────────────│
            │ slide_id (FK)   : int   │
            │ path            : str   │
            │ file_sha256     : str   │
            │ size_bytes      : int   │
            │ duration_sec    : float │
            └─────────────────────────┘

            ┌─────────────────────────┐
            │        Asset            │
            │─────────────────────────│
            │ id (PK from Hedra) : str│
            │ kind     : "image"      │
            │ name     : str          │
            │ local_path : str        │
            └─────────────────────────┘
```

Конкретный сериализованный вид — `data/slides.json`, `data/manifest.json`.

### Пример `manifest.json`

```json
{
  "lecture_id": "l7",
  "avatar_asset_id": "asset_abc",
  "voice_id": "aisala",
  "generated_at": "2026-05-18T10:23:00Z",
  "slides": {
    "1": {
      "status": "ok",
      "hedra_generation_id": "gen_x9",
      "text_sha256": "...",
      "file_sha256": "...",
      "duration_sec": 47.3,
      "generated_at": "2026-05-18T10:00:11Z",
      "error": null
    }
  }
}
```

---

## 5. DFD (Data Flow Diagram)

```
   slides.json                avatar.jpg
       │                          │
       ▼                          ▼
  SlideRepository           local read
       │                          │
       ▼                          ▼
  ┌──────────────────────────────────────────────────┐
  │            VideoGenerationService                 │
  │                                                   │
  │   for each slide:                                 │
  │      ┌── text_sha256 → manifest check (skip?)     │
  │      └── HedraClient                              │
  │             │                                     │
  │             ├── POST /assets         ─┐           │
  │             ├── POST /assets/{}/up   ─┼─► api.hedra.com
  │             ├── POST /generations    ─┤           │
  │             ├── GET  /gen/{}/status  ─┤           │
  │             └── GET  video_url       ─┘           │
  │                                                   │
  │   → write videos/{id}.mp4                         │
  │   → ManifestStore.write_atomic()                  │
  └─────────────────┬─────────────────────────────────┘
                    │
                    ▼
        videos/1.mp4 .. 50.mp4   manifest.json
                    │                 │
                    └───────┬─────────┘
                            ▼
                      GitPublisher
                            │
                            ▼
                  origin / branch (GitHub)
                            │
                            ▼
                  l7/index.html → <video src="videos/N.mp4">
                            │
                            ▼
                       Слушатель (браузер)
```

---

## 6. Инфраструктура

### 6.1 Среды

| Среда     | Где                                                              | Зачем                              |
|-----------|------------------------------------------------------------------|------------------------------------|
| dev       | gcloud VM `human-1` (`europe-west1-b`, `i-crossbar-433120-v3`)   | Реальные вызовы Hedra, генерация   |
| ci        | GitHub Actions (по желанию, не в MVP)                            | Юнит-тесты, валидация slides.json  |
| serving   | GitHub Pages / Raw GitHub                                        | Раздача `l7/index.html` + `videos/`|

### 6.2 Сетевые требования

* Исходящий HTTPS: `api.hedra.com:443`, `github.com:443`.
* Исходящий HTTPS: `i.ibb.co` или другой источник аватар-фото (можно скачать заранее в репо).

### 6.3 Безопасность

* `HEDRA_API_KEY` — только через ENV или gcloud Secret Manager.
* `.gitignore` отсекает `.env`, `*.key`, `secrets/`.
* Логи не содержат полного ключа (маска `sk_***`).

### 6.4 Наблюдаемость

* JSON-логи в stderr.
* `manifest.json` — единственное хранилище состояния.

---

## 7. Дерево проекта (см. `05-project-tree.md`)

Развёрнутая структура каталогов и файлов — отдельным документом, чтобы не дублировать.
