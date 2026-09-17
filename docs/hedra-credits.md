# Hedra credits — operating rules

Everything here is measured from this repo's own runs, not from marketing pages.
Where a published figure disagrees, the measured one is what actually got billed.

## 1. The unit cost

| | |
|---|---|
| Measured burn | **3.74 credits per second** of finished video (540p, 1:1, incl. Hedra TTS) |
| Video render alone | 3.52 credits/s |
| Hedra TTS alone | ~12 credits per slide (~0.2 credits/s) |
| A ~55 s circle | **~207 credits ≈ $1.08** |
| Credit price | $0.00521 (Professional: $75 = 14,400 credits) |

Derived from: workspace 58237 (the original account) went 5189 → 5 credits while producing 25 videos
(app 1-2, l1 3/4/5/32, l3 1-19) totalling 1387 s.

Hedra publishes 3.00 credits/s for 540p Character-3. We measure 3.52 for the
render. Budget on 3.74 — the published rate has consistently under-predicted.

### Estimating before you spend

Speech rate differs by language — do not use the Russian figure for English:

| Language | chars/sec | measured over |
|---|---|---|
| Russian, speed 0.75 | **13.9** | 23 videos (l3 1-19, levels), 17,812 chars → 1,286 s |
| English, speed 0.75 | **17.2** | 36 videos (mte), 28,285 chars → 1,648 s |

English runs ~24% faster per character, so the same word count yields a video
about a fifth shorter. A Russian narration of ~780 chars lands at ~56 s; its
English translation of the same length lands at ~45 s.

```
seconds  ≈ characters / 13.9   (ru)   |   characters / 17.2   (en)
credits  ≈ seconds * 3.74
dollars  ≈ credits * 0.00521
```

Per 1000 characters: ~269 credits / $1.40 in Russian, ~218 credits / $1.13 in
English.

Check any lecture before running it:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0,'.')
from l7.service.slide_repository import SlideRepository
LECTURE, RATE = "l3/data/slides.json", 13.9   # 17.2 for English
c = sum(len(s.narration) for s in SlideRepository(LECTURE).iter_slides())
sec = c / RATE
print(f"{c} chars -> ~{sec:.0f} s -> ~{sec*3.74:.0f} credits -> ${sec*3.74*75/14400:.2f}")
PY
```

## 2. Which pool gets billed

**`workspace_id` must be sent on every generation.** Without it Hedra bills a
default pool that is always empty, and returns `402 Available: 0` while the
dashboard shows thousands of credits. This cost a full debugging session.

It lives in `<lecture>/data/config.json` under `hedra.workspace_id`, or
`--workspace-id`. It must name a workspace the API key's account actually owns —
`--check-credits` now says so explicitly when it does not, and a mismatch is a
`403 PERMISSION_DENIED: "User does not have access to workspace"`, not a 402.

The workspace changed once already: the original account's pool was 58237; the
account funded in Sept 2026 uses **340608**. When the key changes, the workspace
almost certainly changes with it — check both together, never one alone.

**An exported `HEDRA_API_KEY` beats `~/.hedra_key`.** Writing a new key to the
file while a stale one is still exported is a silent no-op: the run keeps
hitting the old account. Start every session with:

```bash
unset HEDRA_API_KEY
python3 -m l7.service.generate --lecture l3 --check-credits | tail -25
```

The first log line names the key source and a masked fingerprint. Confirm it is
the key you meant before spending anything.

## 3. Order of consumption, and what expires

- Monthly plan credits are consumed **first**; credit-pack credits only after
  the monthly allowance is gone.
- **Monthly credits do not roll over** — they reset to the plan amount each
  billing cycle. Unspent ones are simply lost.
- **Credit-pack credits do not expire** and roll over indefinitely while the
  account stays subscribed. Cancelling locks you out of them until you
  resubscribe.

Practical consequence: spend the monthly 14,400 before the cycle closes; the
pack keeps. Never let a cycle lapse with a big unspent monthly balance while the
pack sits untouched — that is the one way to actually lose money here.

## 4. What burns credits and what does not

| Event | Billed? |
|---|---|
| `402 INSUFFICIENT_BALANCE` rejection | No — refused before billing |
| `422` payload rejection | No |
| Accepted generation that later fails server-side | Assume yes |
| Re-running a slide whose text is unchanged | No — skipped via `text_sha256` |
| `--regenerate <id>` | **Yes, full price**, every time |

Regeneration is where this project's money went: l1 was re-rendered whole for
1:1/540p, then slides 0, 3, 4, 5, 7, 15, 20, 32 again for the AI naming change.
Each pass was full price. Settle wording and format *before* rendering, not
after.

## 5. Levers that actually matter

- **Duration is the only real driver.** Cost is linear in seconds. Cutting a
  750-character narration to 600 saves ~40 credits — the same as any clever
  setting change.
- **540p vs 720p is 2×.** Stay at 540p. `hedra.resolution` in config.
- **Never send `duration_ms`.** With `audio_id` present, Hedra derives length
  from the audio. Passing `duration_ms` forces that exact length and pads with
  silence — 2-minute videos for 30 s of speech, at 2× the price. The client
  deliberately omits it; keep it that way.
- **Moving TTS to ElevenLabs is not a saving.** Hedra's TTS is 12 credits
  (~$0.06) per slide, 4.4% of the total. ElevenLabs charges ~$0.18 per 800-char
  narration on Creator. The render is 96% of the cost and stays in Hedra either
  way. The `--tts-provider elevenlabs` path exists for voice quality, not price.

## 6. Before every run

```bash
cd ~/automation
unset HEDRA_API_KEY
git pull --rebase origin claude/setup-gcloud-video-service-XKVf0
python3 -m l7.service.generate --lecture l3 --check-credits | tail -25   # right account?
bash l3/run_one.sh 20                                                   # one slide, listen
PAR=4 bash l3/run_parallel.sh 20 40                                     # then the rest
```

`run_parallel.sh` reads the balance up front and refuses to start when it cannot
render anything, stops on the first `INSUFFICIENT_BALANCE` instead of grinding
through every remaining slide, and ends with the exact ids that are missing.
Override the estimate when the real per-slide cost is known:

```bash
COST_PER_SLIDE=207 PAR=4 bash l3/run_parallel.sh 20 40
```

## 7. Reference: what the work costs

At 3.74 credits/s and $0.00521/credit:

| | Credits | USD |
|---|---|---|
| One ~55 s circle | 207 | $1.08 |
| l3 remaining (slides 20-40, 15,960 chars) | ~4,290 | ~$22 |
| A full 40-slide lecture | ~8,300 | ~$43 |
| Re-rendering all 331 existing videos | ~68,000 | ~$355 |
| $100 credit pack buys | ~19,200 | ~92 circles / ~86 min |

The $100 figure assumes packs price credits like the plan. Confirm the real
number with `--check-credits` after the top-up lands — that reading is
authoritative and any estimate here is not.
