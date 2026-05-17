# l7/service — генерация видео через Hedra на gcloud VM

Скрипт `generate.py` берёт `l7/data/slides.json`, `l7/data/avatar.jpg`,
голос `aisala`, модель «Hedra Avatar 540p» (1:1) и кладёт 50 mp4
в `l7/videos/`. После — коммитит и пушит их в ветку
`claude/setup-gcloud-video-service-XKVf0`.

Полный фреймворк требований и тестов лежит в `l7/docs/`.

## TL;DR — запуск на VM

```bash
gcloud compute ssh human-1 \
  --project=i-crossbar-433120-v3 \
  --zone=europe-west1-b

# на VM
bash <(curl -sL https://raw.githubusercontent.com/andre-kuzminykh/automation/claude/setup-gcloud-video-service-XKVf0/l7/service/bootstrap.sh)

cd ~/automation
source .venv/bin/activate
export HEDRA_API_KEY=sk_hedra_2nH_wGiV6G3rYDAxZeOq9Qs0BNai68nvullGOPQyMOyP1mDWCUU_VNwueZ5KE5Ot
# (или подтяните из gcloud secret manager — не коммитьте ключ в git)

# скачать референсное фото аватара (один раз)
curl -L "https://i.ibb.co/VcCKP5Kg/photo-2026-05-18-01-41-54.jpg" -o l7/data/avatar.jpg

# пробный прогон — 1 слайд
python -m l7.service.generate --lecture l7 --limit 1

# боевой прогон — все 50
python -m l7.service.generate --lecture l7
```

## CLI флаги

| Флаг                    | Что делает                                            |
|-------------------------|-------------------------------------------------------|
| `--lecture l7`          | какую лекцию обрабатывать                              |
| `--config PATH`         | альтернативный config.json                             |
| `--limit N`             | только первые N слайдов из выборки                     |
| `--from N --to M`       | прогнать только slide_id ∈ [N..M]                      |
| `--regenerate 1,7,12`   | принудительно пересоздать эти id (игнорирует skip)     |
| `--dry-run`             | спланировать и выйти, никаких сетевых вызовов          |
| `--no-git`              | не делать `git add/commit/push` после генерации        |
| `--poll-interval 5`     | пауза между опросами статуса (сек)                     |
| `--poll-timeout 600`    | максимальное время ожидания одного слайда (сек)        |

## Идемпотентность

Скрипт пропускает слайды, для которых:
* `videos/{id}.mp4` существует;
* `manifest.json[id].status == "ok"`;
* `manifest.json[id].text_sha256 == sha256(narration)`.

Если поменяли текст в `slides.json` — `text_sha256` меняется и слайд
будет перегенерирован при следующем запуске.

## Структура артефактов

```
l7/
├── data/
│   ├── slides.json         # 50 текстов
│   ├── avatar.jpg          # фото для Hedra
│   └── manifest.json       # ← создаётся скриптом, статус каждого слайда
└── videos/
    ├── 1.mp4               # ← создаются скриптом
    ├── 2.mp4
    └── ...
```

## Безопасность

* `HEDRA_API_KEY` — **только** через env (`os.environ`).
* `.gitignore` исключает `.env`, `*.key`, `secrets/`.
* Логи маскируют токены (`sk_hedra_...` → `sk_***`).
* Коммитим только данные/код, секреты — нет.

## Тестирование

```bash
# unit + integration
python -m pytest l7/tests/unit l7/tests/integration

# e2e с реальной Hedra (требует HEDRA_API_KEY, ondemand)
HEDRA_API_KEY=... python -m pytest l7/tests/e2e/test_one_slide_real_hedra.py

# e2e UI (playwright)
python -m pytest l7/tests/e2e/test_html_player_playwright.py
```
