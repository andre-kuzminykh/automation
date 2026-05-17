# Лекция 7 — Use Cases в формате BDD Gherkin

Каждый Use Case — это атомарный ответ системы на действие из User Flow.
Идентификатор: `UC-F{feature}-{story}-{n}`.
Связь требований к каждому UC — в `03-requirements.md`.

---

## F1 — Сервис генерации видео

### UC-F1-1-1 — Загрузка аватар-фото в Hedra Asset Library
```gherkin
Feature: Avatar image asset upload
  Background:
    Given Hedra API base URL is "https://api.hedra.com/web-app/public"
    And X-API-KEY header is set from $HEDRA_API_KEY
    And avatar image is located at "l7/data/avatar.jpg"

  Scenario: Successful image asset creation
    When the service POSTs to "/assets" with type="image" and name="lecture7-avatar"
    Then the response status is 200
    And the body contains "id" of the created asset
    And the asset id is cached in data/manifest.json under "avatar_asset_id"

  Scenario: Image upload failure (5xx)
    Given Hedra returns 503 on first attempt
    When the service POSTs to "/assets"
    Then it retries up to 4 times with exponential backoff (2s, 4s, 8s, 16s)
    And if all retries fail, the pipeline aborts with exit code 2
```

### UC-F1-1-2 — Привязка бинарного файла к ассету
```gherkin
Scenario: Upload binary content to asset
  Given an asset id from UC-F1-1-1
  When the service POSTs the binary jpeg to "/assets/{id}/upload"
  Then the response status is 200
  And avatar_asset_id is marked as ready in manifest
```

### UC-F1-1-3 — Создание видео-генерации для слайда
```gherkin
Scenario: Submit video generation
  Given an asset id of avatar
  And voice_id "aisala"
  And resolution "540p" and aspect_ratio "1:1"
  And narration text from slides.json[id=N].narration
  When the service POSTs to "/generations" with model "Hedra Avatar 540p"
  Then the response contains "id" (generation_id)
  And manifest[slide=N].status = "submitted"
```

### UC-F1-1-4 — Поллинг статуса генерации
```gherkin
Scenario: Poll until completion
  Given a generation_id
  When the service GETs "/generations/{id}/status" every 5s
  Then it accepts terminal statuses "complete" or "failed"
  And it gives up after 600s (10 minutes per slide)

  Scenario: Hedra returns "complete"
    Given status = "complete"
    When response contains video_url
    Then the service downloads it to l7/videos/{slide_id}.mp4

  Scenario: Hedra returns "failed"
    Given status = "failed"
    Then manifest[slide=N].status = "failed"
    And manifest[slide=N].error = response.error
    And pipeline continues with next slide
```

### UC-F1-2-1 — Идемпотентный skip уже готовых слайдов
```gherkin
Scenario: Skip slides that already have valid video file
  Given file "l7/videos/N.mp4" exists
  And file_sha256 matches manifest[slide=N].file_sha256
  And manifest[slide=N].text_sha256 matches sha256(slides[N].narration)
  When the service iterates slides
  Then it logs "skip slide N: already up to date"
  And does NOT call Hedra
```

### UC-F1-2-2 — Принудительная перегенерация
```gherkin
Scenario: --regenerate flag forces re-creation
  Given CLI flag --regenerate "17,28"
  When the service iterates slides
  Then slides 17 and 28 are regenerated even if files exist
  And other slides follow idempotent skip rule
```

### UC-F1-3-1 — Сводка по окончании
```gherkin
Scenario: Summary report
  When the pipeline finishes
  Then it prints to stdout: "OK: {n_ok} / SKIPPED: {n_skip} / FAILED: {n_fail}"
  And if n_fail > 0 it lists failed slide ids
  And exit code is 0 if n_fail == 0 else 1
```

---

## F2 — Конвейер «слайды → видео»

### UC-F2-1-1 — Валидация slides.json при старте
```gherkin
Scenario: Reject malformed slides.json
  Given slides.json missing required field "narration" on slide 5
  When the service starts
  Then it prints "ERROR: slide 5 missing 'narration'"
  And exits with code 3 BEFORE calling Hedra
```

### UC-F2-2-1 — Обновление манифеста после каждого слайда
```gherkin
Scenario: Atomic manifest update
  Given a successful generation of slide N
  When the service writes manifest
  Then it writes to manifest.json.tmp first
  And atomically renames to manifest.json
  So a crash mid-run never leaves a corrupt manifest
```

---

## F3 — Интерактивный плеер

### UC-F3-1-1 — Загрузка первого слайда с видео
```gherkin
Scenario: Initial render
  Given user opens l7/index.html
  When DOMContentLoaded fires
  Then slide-0 has class "opacity-100"
  And #bubble-video.src equals "videos/1.mp4"
  And video is muted on first load (browser autoplay policy)
```

### UC-F3-1-2 — Переключение слайда меняет источник видео
```gherkin
Scenario: Slide change syncs video src
  Given currentSlide = 5
  When user presses ArrowRight
  Then currentSlide becomes 6
  And #bubble-video.src is set to "videos/7.mp4"   # (5+1+1 = 7, since slide-N maps to (N+1).mp4)
  And the new video starts playing
```

### UC-F3-1-3 — Конец списка не уводит за пределы
```gherkin
Scenario: End-of-deck guard
  Given currentSlide = 49 (last)
  When user presses ArrowRight
  Then currentSlide stays 49
  And video src does NOT change
```

### UC-F3-2-1 — Drag-and-snap bubble
```gherkin
Scenario: Drag bubble to corner
  Given bubble at position (100,100)
  When user drags it to (50, viewport_height - 50)
  Then bubble snaps to bottom-left corner with 16px margin
  And new position is saved to localStorage["bubble_pos"]
```

### UC-F3-2-2 — Восстановление позиции из localStorage
```gherkin
Scenario: Restore previous position
  Given localStorage["bubble_pos"] = '{"x":12,"y":20}'
  When user reopens index.html
  Then bubble appears at (12,20)
```

### UC-F3-3-1 — Pause/play по клику
```gherkin
Scenario: Toggle playback
  Given video is playing
  When user clicks bubble
  Then video pauses
  And play-icon overlay becomes visible

  When user clicks again
  Then video resumes
  And overlay hides after 1500ms
```

### UC-F3-3-2 — Лоадер при буферизации
```gherkin
Scenario: Buffering indicator
  Given video emits "waiting" event
  When 100ms elapse without "playing"
  Then #video-loader becomes visible
  And it hides on "playing" event
```

### UC-F3-3-3 — Видео не найдено (404)
```gherkin
Scenario: Missing mp4
  Given videos/17.mp4 does not exist on server
  When slide-16 is shown
  Then video element fires "error"
  And loader hides
  And bubble shows placeholder icon
  And a console warning is logged: "video missing: videos/17.mp4"
```

### UC-F3-4-1 — PDF-режим
```gherkin
Scenario: PDF export mode
  Given URL contains ?pdf=1 OR location.hash == "#pdf"
  When DOM is ready
  Then body has class "pdf-export-mode"
  And all 50 slides have opacity:1
  And #video-bubble is hidden
  And @page CSS forces landscape A4
```

---

## F4 — Git публикация

### UC-F4-1-1 — Один коммит на пачку видео
```gherkin
Scenario: Commit all generated videos together
  Given videos 1..50 generated successfully
  When the service runs post-hook
  Then it executes "git add l7/videos/"
  And creates a single commit with message
    "feat(l7): add hedra-generated videos for lecture 7 (50 slides)"
  And pushes to "claude/setup-gcloud-video-service-XKVf0"
```

### UC-F4-2-1 — Проверка размера файлов
```gherkin
Scenario: Reject overly large mp4
  Given a generated mp4 file > 25 MB
  When the size check runs
  Then a warning is printed
  And a recompression suggestion is logged:
    "ffmpeg -i videos/{id}.mp4 -vcodec libx264 -crf 28 -preset slow videos/{id}.mp4"
```

---

## F5 — Развёртывание

### UC-F5-1-1 — Bootstrap скрипт
```gherkin
Scenario: One-shot environment setup
  Given a fresh Debian VM accessible via gcloud SSH
  When user runs "bash l7/service/bootstrap.sh"
  Then python3, pip, git, ffmpeg are installed
  And requirements.txt is installed via pip
  And the script prints "READY"
```

### UC-F5-2-1 — Секреты не в репо
```gherkin
Scenario: Reject committed secrets
  Given a file matching ".env" or "*.key" or "secrets/*"
  When user attempts to git add it
  Then .gitignore prevents inclusion
  And a pre-commit hook (optional) verifies absence of "sk_hedra_" in staged diff
```

---

## Сводная таблица UC → User Story

| UC                | Story         |
|-------------------|---------------|
| UC-F1-1-1..1-4    | US-F1-1       |
| UC-F1-2-1..2-2    | US-F1-2       |
| UC-F1-3-1        | US-F1-3       |
| UC-F2-1-1        | US-F2-1       |
| UC-F2-2-1        | US-F2-2       |
| UC-F3-1-1..1-3   | US-F3-1       |
| UC-F3-2-1..2-2   | US-F3-2       |
| UC-F3-3-1..3-3   | US-F3-3       |
| UC-F3-4-1        | US-F3-4       |
| UC-F4-1-1        | US-F4-1       |
| UC-F4-2-1        | US-F4-2       |
| UC-F5-1-1        | US-F5-1       |
| UC-F5-2-1        | US-F5-2       |
