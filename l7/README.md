# Лекция 7 — Люди, машины и новая логика управления

Интерактивная веб-лекция (50 слайдов) + говорящий аватар-«пузырь»,
синхронизированный со слайдами через Hedra (Avatar 540p, голос `aisala`).

```
       ┌────────────────────────────┐
       │  l7/index.html             │ ← 50 слайдов + draggable video bubble
       └─────────────┬──────────────┘
                     │ <video src="videos/N.mp4">
       ┌─────────────▼──────────────┐
       │  l7/videos/{1..50}.mp4     │ ← Hedra-сгенерированные ролики
       └─────────────┬──────────────┘
                     │ генерирует
       ┌─────────────▼──────────────┐
       │  l7/service/generate.py    │ ← Python CLI, запускается на gcloud VM
       └─────────────┬──────────────┘
                     │ читает
       ┌─────────────▼──────────────┐
       │  l7/data/slides.json       │ ← источник правды (50 текстов)
       │  l7/data/avatar.jpg        │ ← фото для синтеза
       └────────────────────────────┘
```

## Открыть лекцию

* `l7/index.html` — открыть в браузере, кликнуть «Начать».
* `l7/index.html?pdf=1` — режим экспорта в PDF (все слайды вертикально).

Управление:
* `→`, `Space`, `Enter`, левый клик, свайп влево — следующий слайд.
* `←`, `Backspace`, правый клик, свайп вправо — предыдущий.
* Видео-«пузырь» можно тащить — позиция сохраняется в `localStorage`.
* Клик по пузырю — pause/play.

## Сгенерировать/обновить видео

```bash
gcloud compute ssh human-1 --project=i-crossbar-433120-v3 --zone=europe-west1-b

# на VM:
bash <(curl -sL https://raw.githubusercontent.com/andre-kuzminykh/automation/claude/setup-gcloud-video-service-XKVf0/l7/service/bootstrap.sh)
cd ~/automation
source .venv/bin/activate
export HEDRA_API_KEY=sk_hedra_...    # из gcloud secret manager или env
curl -L "https://i.ibb.co/VcCKP5Kg/photo-2026-05-18-01-41-54.jpg" -o l7/data/avatar.jpg
python3 -m l7.service.generate --lecture l7
```

Подробнее: [`l7/service/README.md`](./service/README.md).

## Обновить слайды

1. Отредактировать `l7/data/slides.json` (`narration` или `title`).
2. (Опционально) скорректировать `LAYOUT_TABLE` в `l7/scripts/build_html.py`,
   если хочется другой инфо-шаблон для конкретного слайда.
3. Перегенерировать страницу: `python3 l7/scripts/build_html.py`.
4. Перегенерировать видео (только изменённые): запуск `generate.py` сам
   обнаружит изменение `text_sha256` и пересоздаст нужные MP4.

## Документация

`l7/docs/` — полная декомпозиция (фичи → user stories → user flows →
BDD-юзкейсы → NR/NFR с ID → архитектура → тесты → план задач):

* `01-features-stories.md`
* `02-use-cases-bdd.md`
* `03-requirements.md`
* `04-architecture.md`
* `05-project-tree.md`
* `06-tests.md`
* `07-task-sequence.md`

## Тесты

```bash
python3 -m pytest l7/tests/unit l7/tests/integration -q
```

Сегодня: 25 / 25 зелёных.
