#!/usr/bin/env python3
"""Generate l7/index.html from l7/data/slides.json.

The script keeps the visual identity of the existing l7 (brand purple + orange,
Inter, Phosphor icons) and adds the draggable video-bubble from the
example aisala/ai-agents-corp/6 example.

Each slide picks an HTML template based on a small categorisation table
maintained inside this file. The narration text from slides.json drives
both the visible "punchline" and the synced Hedra video file.

Regenerate after editing slides.json:
    python3 l7/scripts/build_html.py
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SLIDES_PATH = ROOT / "l7/data/slides.json"
OUT_PATH = ROOT / "l7/index.html"


# ---------------------------------------------------------------------------
# Layout table: slide_id -> template name + optional accent
# ---------------------------------------------------------------------------
LAYOUT_TABLE: dict[int, dict] = {
    1: {"tpl": "title"},
    2: {
        "tpl": "two_col",
        "left": "Было — только люди",
        "right": "Стало — + ИИ-агенты",
        "left_items": [
            ("ph-fill ph-user", "Люди думают"),
            ("ph-fill ph-user-gear", "Люди принимают решения"),
            ("ph-fill ph-check-square", "Люди контролируют"),
            ("ph-fill ph-shield-check", "Люди отвечают за результат"),
        ],
        "right_items": [
            ("ph-fill ph-magnifying-glass", "ИИ анализирует данные"),
            ("ph-fill ph-sparkle", "ИИ предлагает варианты"),
            ("ph-fill ph-lightning", "ИИ выполняет действия"),
            ("ph-fill ph-warning", "ИИ отслеживает отклонения"),
        ],
    },
    3: {"tpl": "numbered", "items": [
        "Где AI может действовать сам?",
        "Где человек должен контролировать?",
        "Где обязательно финальное решение человека?",
        "Кто отвечает за результат?",
    ]},
    4: {
        "tpl": "two_col",
        "left": "Автоматизация",
        "right": "Искусственный интеллект",
        "left_items": [
            ("ph-fill ph-fast-forward", "Ускоряет существующий шаг"),
            ("ph-fill ph-arrows-clockwise", "Заменяет ручную операцию"),
            ("ph-fill ph-clock-counter-clockwise", "Та же логика, быстрее"),
        ],
        "right_items": [
            ("ph-fill ph-brain", "Анализирует ситуацию"),
            ("ph-fill ph-graph", "Находит закономерности"),
            ("ph-fill ph-lightbulb", "Предлагает решения"),
            ("ph-fill ph-eye", "Контролирует отклонения"),
        ],
    },
    5: {"tpl": "grid3", "items": [
        ("ph-fill ph-warning",       "Старые KPI",        "Меряют занятость, не эффект"),
        ("ph-fill ph-clipboard-text","Старые роли",       "Должностные инструкции отстали"),
        ("ph-fill ph-graduation-cap","Старое обучение",   "Учит кнопкам, а не работе по-новому"),
    ]},
    6: {"tpl": "quote", "kicker": "Внедрение ИИ",
        "main": "Это не IT-проект.",
        "tail": "Это управленческая трансформация всей системы."},
    7: {
        "tpl": "two_col",
        "left": "Человек",
        "right": "AI",
        "left_items": [
            ("ph-fill ph-compass", "Задаёт цель"),
            ("ph-fill ph-scroll", "Определяет правила"),
            ("ph-fill ph-warning-octagon", "Принимает рискованные решения"),
            ("ph-fill ph-shield-check", "Отвечает за последствия"),
        ],
        "right_items": [
            ("ph-fill ph-database", "Анализирует данные"),
            ("ph-fill ph-gear", "Выполняет операции"),
            ("ph-fill ph-graph", "Ищет закономерности"),
            ("ph-fill ph-eye", "Следит за отклонениями"),
        ],
    },
    8: {"tpl": "quote", "kicker": "Сильная модель",
        "main": "Ценность появляется в связке.",
        "tail": "Кто ставит, кто готовит, кто проверяет, кто решает, кто отвечает."},
    9: {"tpl": "pyramid", "title": "Человеческая организация",
        "rows": ["Люди думают", "Люди делают", "Люди контролируют", "Люди отвечают"]},
    10: {"tpl": "pyramid", "title": "Гибридная организация",
         "rows": ["AI: рутина и мониторинг", "AI: первичный анализ", "Человек: цели и правила", "Человек: ответственность"]},
    11: {"tpl": "numbered", "items": [
        "Задавать цели",
        "Формулировать правила",
        "Определять границы автономности AI",
        "Отвечать за последствия",
    ]},
    12: {
        "tpl": "two_col",
        "left": "Полная автоматизация",
        "right": "Гибридность",
        "left_items": [
            ("ph-fill ph-user-minus", "Человек полностью вне процесса"),
            ("ph-fill ph-robot", "Только машинная логика"),
            ("ph-fill ph-warning", "Подходит лишь там, где нет смыслов и этики"),
        ],
        "right_items": [
            ("ph-fill ph-users-three", "Функции и ответственность распределены"),
            ("ph-fill ph-lightning", "AI: скорость, масштаб, повторяемость"),
            ("ph-fill ph-user-focus", "Человек: цель, этика, риск, ответственность"),
        ],
    },
    13: {"tpl": "grid4", "items": [
        ("ph-fill ph-compass",       "Постановка целей",     "AI предлагает, человек выбирает направление"),
        ("ph-fill ph-warning-octagon","Рискованные решения", "Где последствия — последнее слово человека"),
        ("ph-fill ph-scales",        "Этика",                "Эффективное ≠ допустимое"),
        ("ph-fill ph-shield-check",  "Ответственность",      "«Так решил алгоритм» — не ответ"),
    ]},
    14: {"tpl": "grid4", "items": [
        ("ph-fill ph-database",       "Большие данные",       "Документы, переписки, транзакции"),
        ("ph-fill ph-magnifying-glass","Поиск закономерностей","Слабые сигналы и связи"),
        ("ph-fill ph-arrows-clockwise","Рутина по правилам",  "Быстрее и стабильнее"),
        ("ph-fill ph-eye",            "Круглосуточный контроль","AI не устаёт"),
    ]},
    15: {"tpl": "modes", "items": [
        ("1", "AI предлагает, человек решает",  "Для сложных и рискованных задач"),
        ("2", "AI действует, человек контролирует", "Повторяемые процессы с правилами"),
        ("3", "AI действует самостоятельно",    "Низкие риски, понятные сценарии"),
        ("4", "Соавторство",                    "Документ/анализ/стратегия вместе"),
    ]},
    16: {"tpl": "numbered", "items": [
        "Сценарии понятны",
        "Риски низкие",
        "Правила описаны заранее",
        "Действия логируются",
        "Есть способ остановить систему",
        "Есть порядок разбора ошибок",
    ]},
    17: {"tpl": "quote", "kicker": "Главная задача",
         "main": "Провести границу между человеком и AI.",
         "tail": "И постоянно её перепроектировать по мере роста доверия."},
    18: {
        "tpl": "two_col",
        "left": "Сценарий 1 — страх",
        "right": "Сценарий 2 — хаос",
        "left_items": [
            ("ph-fill ph-warning", "Люди боятся пользоваться AI"),
            ("ph-fill ph-question", "Не понятно, за что отвечает человек"),
            ("ph-fill ph-pause-circle", "AI используют формально и осторожно"),
        ],
        "right_items": [
            ("ph-fill ph-warning", "Решения перекладывают на алгоритм"),
            ("ph-fill ph-x-circle", "Ответственность размывается"),
            ("ph-fill ph-warning-octagon", "Компания теряет управляемость"),
        ],
    },
    19: {"tpl": "quote", "kicker": "AI расширяет управляемость",
         "main": "Больше сигналов. Раньше реакция.",
         "tail": "Шире контекст для решений."},
    20: {"tpl": "cycle", "items": [
        "Гипотеза", "Сбор данных", "Моделирование", "AI готовит варианты", "Человек выбирает", "Ответственность",
    ]},
    21: {"tpl": "quote", "kicker": "Сильный руководитель сегодня",
         "main": "Не тот, кто быстрее даёт готовый ответ.",
         "tail": "А тот, кто строит среду, где лучшие ответы появляются быстрее."},
    22: {"tpl": "pyramid", "title": "AI как внешний слой мышления",
         "rows": ["Удерживает контекст", "Сравнивает варианты", "Замечает отклонения", "Подсвечивает слабые сигналы"]},
    23: {"tpl": "numbered", "items": [
        "Какие сигналы действительно важны",
        "Какие отклонения требуют реакции",
        "Какие решения необратимы",
        "Где AI справляется сам",
        "Где человек обязан вмешаться",
    ]},
    24: {
        "tpl": "two_col",
        "left": "Старая модель труда",
        "right": "Гибридная модель труда",
        "left_items": [
            ("ph-fill ph-clipboard-text", "Получил задачу"),
            ("ph-fill ph-hammer", "Сделал руками"),
            ("ph-fill ph-paper-plane-right", "Передал результат"),
            ("ph-fill ph-check-square", "Руководитель проверил"),
        ],
        "right_items": [
            ("ph-fill ph-target", "Поставить цель"),
            ("ph-fill ph-scroll", "Задать ограничения"),
            ("ph-fill ph-toggle-right", "Выбрать режим автономности AI"),
            ("ph-fill ph-check-circle", "Проверить и принять решение"),
        ],
    },
    25: {"tpl": "grid3", "items": [
        ("ph-fill ph-user-circle-minus","Сотрудник",  "Не понимает, за что отвечает"),
        ("ph-fill ph-target",          "Руководитель","Не знает, как мерить результат"),
        ("ph-fill ph-buildings",       "Бизнес",     "Ждёт эффекта, не меняя процесс"),
    ]},
    26: {"tpl": "quote", "kicker": "Должность ≠ роль",
         "main": "Роль — это логика ответственности.",
         "tail": "AI может действовать, но ответственность — у человека."},
    27: {"tpl": "grid4", "items": [
        ("ph-fill ph-flow-arrow",    "Владелец гибридного процесса", "Знает, как процесс работает с AI"),
        ("ph-fill ph-blueprint",     "Архитектор автоматизации",     "Проектирует связку людей, агентов, данных"),
        ("ph-fill ph-medal-military","Бизнес-владелец результата",   "Отвечает за эффект, не за пилот"),
        ("ph-fill ph-shield-warning","Владелец риска",               "Видит юридические и этические последствия"),
    ]},
    28: {
        "tpl": "two_col",
        "left": "Владелец гибридного процесса",
        "right": "Архитектор автоматизации",
        "left_items": [
            ("ph-fill ph-flow-arrow", "Что отдать AI, что оставить человеку"),
            ("ph-fill ph-check-square", "Где нужен контроль человеком"),
            ("ph-fill ph-chart-line-up", "Как измерить эффект процесса"),
        ],
        "right_items": [
            ("ph-fill ph-blueprint", "Связка людей, агентов, данных, систем"),
            ("ph-fill ph-toggle-right", "Где AI помогает, где автономен"),
            ("ph-fill ph-stop-circle", "Где система обязана остановиться"),
        ],
    },
    29: {"tpl": "grid3", "items": [
        ("ph-fill ph-medal-military","Бизнес-владелец результата","Эффект, метрики, масштабирование"),
        ("ph-fill ph-shield-warning","Владелец риска",           "Юридические, этические, операционные"),
        ("ph-fill ph-trophy",        "AI-чемпион",               "Превращает AI в норму ежедневной работы"),
    ]},
    30: {"tpl": "numbered", "items": [
        "Ставить задачу правильно",
        "Задавать ограничения",
        "Понимать, где AI ошибается",
        "Проверять результат",
        "Интерпретировать рекомендации",
        "Давать обратную связь",
        "Понимать свою ответственность",
    ]},
    31: {"tpl": "quote", "kicker": "Регламент — это не бюрократия",
         "main": "Это управляемость и безопасность.",
         "tail": "Хороший регламент не тормозит — он делает масштабирование возможным."},
    32: {"tpl": "numbered", "items": [
        "Данные выбраны людьми",
        "Цели заданы людьми",
        "Показатели определены людьми",
        "Границы разрешены людьми",
        "→ За каждым решением AI стоит решение человека",
    ]},
    33: {"tpl": "quote", "kicker": "Кто отвечает?",
         "main": "Не «алгоритм».",
         "tail": "Бизнес-владелец, владелец риска, человек, который может остановить систему."},
    34: {"tpl": "numbered", "items": [
        "Журнал действий агента",
        "Проверка человеком в критичных случаях",
        "Ручная остановка системы",
        "Порядок разбора инцидентов",
        "Правила обновления моделей",
        "Понятные зоны ответственности",
    ]},
    35: {
        "tpl": "two_col",
        "left": "Старые показатели",
        "right": "Показатели гибридной системы",
        "left_items": [
            ("ph-fill ph-clock", "Сколько часов потрачено"),
            ("ph-fill ph-clipboard-text", "Сколько задач выполнено"),
            ("ph-fill ph-files", "Сколько документов обработано"),
        ],
        "right_items": [
            ("ph-fill ph-lightning", "Скорость решений"),
            ("ph-fill ph-shield-check", "Меньше ошибок и переделок"),
            ("ph-fill ph-trend-up", "Эффект для системы, а не активность"),
        ],
    },
    36: {
        "tpl": "two_col",
        "left": "Конфликт метрик",
        "right": "Согласованные метрики",
        "left_items": [
            ("ph-fill ph-warning", "AI улучшает качество"),
            ("ph-fill ph-warning", "Человека мерят только скоростью"),
            ("ph-fill ph-x-circle", "Сопротивление неизбежно"),
        ],
        "right_items": [
            ("ph-fill ph-check-circle", "Скорость без потери качества"),
            ("ph-fill ph-check-circle", "Рост объёма без ухудшения CX"),
            ("ph-fill ph-check-circle", "Эффект без нарушения этики"),
        ],
    },
    37: {
        "tpl": "two_col",
        "left": "Автоматизация",
        "right": "Изменение",
        "left_items": [
            ("ph-fill ph-question", "Что может сделать AI?"),
            ("ph-fill ph-flask", "Технический пилот"),
            ("ph-fill ph-check-circle", "Технология работает"),
        ],
        "right_items": [
            ("ph-fill ph-question", "Как должна измениться компания?"),
            ("ph-fill ph-users-three", "Роли, правила, обучение, KPI"),
            ("ph-fill ph-trend-up", "AI создаёт устойчивую ценность"),
        ],
    },
    38: {"tpl": "grid4", "items": [
        ("ph-fill ph-rocket-launch","Ускорить выход на рынок",     "Time-to-market"),
        ("ph-fill ph-currency-dollar","Снизить затраты",            "Unit economics"),
        ("ph-fill ph-trend-up",      "Масштабироваться без роста штата","Scale without headcount"),
        ("ph-fill ph-smiley",        "Улучшить клиентский опыт",    "CX, NPS"),
    ]},
    39: {"tpl": "numbered", "items": [
        "Какую стратегическую цель поддерживает?",
        "Какая исходная метрика процесса?",
        "Кто бизнес-владелец результата?",
        "Кто владелец риска?",
        "Где нужна проверка человеком?",
        "Какие данные доступны?",
        "При каких условиях проект будет закрыт?",
    ]},
    40: {"tpl": "cycle", "items": [
        "Поиск возможностей", "Приоритизация", "Пилот", "Промышленная сборка", "Масштабирование", "Закрытие при отсутствии эффекта",
    ]},
    41: {"tpl": "numbered", "items": [
        "Каждую неделю — сам процесс",
        "Раз в две недели — пилоты",
        "Раз в месяц — портфельный совет",
        "Раз в квартал — стандарты, академия, регламенты",
    ]},
    42: {"tpl": "quote", "kicker": "AI-проект через гипотезу",
         "main": "Сформулировать → проверить → измерить → решить.",
         "tail": "Закрыть проект без эффекта — это успех, а не провал."},
    43: {"tpl": "quote", "kicker": "Бизнес-владелец",
         "main": "Не IT, не подрядчик, не data-команда.",
         "tail": "Без бизнес-владельца AI остаётся демонстрацией."},
    44: {"tpl": "quote", "kicker": "Сопротивление",
         "main": "Нормальная реакция, не ошибка культуры.",
         "tail": "Главный вопрос сотрудника: «что изменится для меня?»"},
    45: {"tpl": "numbered", "items": [
        "Что теперь делает AI?",
        "Что по-прежнему делает человек?",
        "За что отвечает сотрудник?",
        "Как меняется его роль?",
        "Как теперь оценивается результат?",
        "Кто отвечает, если AI ошибётся?",
    ]},
    46: {"tpl": "numbered", "items": [
        "Признать сопротивление",
        "Дать ясность по ответственности",
        "Показать личную пользу",
        "Создать безопасную среду для практики",
        "Включить руководителей в практику",
    ]},
    47: {"tpl": "quote", "kicker": "Средний менеджмент",
         "main": "Переводчик стратегии в ежедневную работу.",
         "tail": "Если менеджер не использует AI — команда не поверит."},
    48: {"tpl": "quote", "kicker": "AI не спускают сверху",
         "main": "Принятие появляется из практики.",
         "tail": "Особенно — из примера руководителей."},
    49: {
        "tpl": "two_col",
        "left": "Имитация активности",
        "right": "Глубина принятия",
        "left_items": [
            ("ph-fill ph-warning", "KPI = «использовал AI»"),
            ("ph-fill ph-clipboard-text", "Много запросов, мало смысла"),
            ("ph-fill ph-x-circle", "Результат работы не меняется"),
        ],
        "right_items": [
            ("ph-fill ph-target", "С AI — лучше процесс"),
            ("ph-fill ph-trend-up", "Какую долю рекомендаций принимают"),
            ("ph-fill ph-check-circle", "Качество и скорость реальных решений"),
        ],
    },
    50: {"tpl": "pyramid", "title": "AI-First компания и новая ценность человека",
         "rows": [
             "Академия и обучение по ролям",
             "Обратная связь — AI учится у компании",
             "Регламенты и организационная память",
             "Ценность человека: суждение, смысл, границы, ответственность",
         ]},
}


def esc(text: str) -> str:
    return html.escape(text, quote=True)


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
def render_title(slide: dict, layout: dict) -> str:
    return f"""
        <div class="content-z text-center w-full max-w-6xl px-2 md:px-4 flex flex-col items-center justify-center h-full">
            <div class="bg-gradient-to-r from-purple-50 to-orange-50 border border-purple-100 rounded-xl p-2 md:p-5 max-w-3xl w-full shadow-sm mb-3 md:mb-10">
                <p class="text-purple-600 font-semibold uppercase tracking-widest text-[9px] md:text-xs mb-0.5 md:mb-1.5"><i class="ph-fill ph-book-open"></i> Лекция 7 — AI-трансформация компании</p>
                <h2 class="text-xs md:text-xl font-bold text-gray-800 leading-tight">Как компания становится гибридной системой</h2>
            </div>
            <h1 class="text-3xl md:text-6xl lg:text-[70px] font-black mb-4 md:mb-12 leading-[1.15] tracking-tight text-gray-900 drop-shadow-sm flex flex-col items-center">
                <span class="pb-0.5 md:pb-1">Люди, машины</span>
                <span class="gradient-text pb-1 md:pb-2">и новая логика</span>
                <span class="gradient-text pb-1 md:pb-2">управления</span>
            </h1>
            <div class="flex flex-col md:flex-row items-center gap-2 md:gap-3 text-gray-600 mt-2 md:mt-4">
                <div class="flex items-center gap-1.5 md:gap-2 bg-gray-50 px-3 py-1.5 md:px-4 md:py-2 rounded-lg md:rounded-xl border border-gray-200">
                    <i class="ph-fill ph-user text-purple-500 text-sm md:text-base"></i>
                    <span class="font-bold text-xs md:text-sm">Человеческая</span>
                </div>
                <i class="ph-bold ph-arrow-right text-lg md:text-2xl text-orange-400 hidden md:inline"></i>
                <i class="ph-bold ph-arrow-down text-lg text-orange-400 md:hidden"></i>
                <div class="flex items-center gap-1.5 md:gap-2 bg-purple-50 px-3 py-1.5 md:px-4 md:py-2 rounded-lg md:rounded-xl border border-purple-200">
                    <i class="ph-fill ph-users-three text-purple-600 text-sm md:text-base"></i>
                    <span class="font-bold text-xs md:text-sm text-purple-800">Гибридная</span>
                </div>
                <i class="ph-bold ph-arrow-right text-lg md:text-2xl text-orange-400 hidden md:inline"></i>
                <i class="ph-bold ph-arrow-down text-lg text-orange-400 md:hidden"></i>
                <div class="flex items-center gap-1.5 md:gap-2 bg-gradient-to-r from-purple-600 to-orange-500 text-white px-3 py-1.5 md:px-4 md:py-2 rounded-lg md:rounded-xl shadow-md">
                    <i class="ph-fill ph-robot text-sm md:text-base"></i>
                    <span class="font-bold text-xs md:text-sm">AI-First</span>
                </div>
            </div>
            <p class="mt-3 md:mt-8 font-bold text-sm md:text-base lg:text-lg text-gray-800 bg-white px-4 md:px-6 py-2 md:py-3 rounded-xl border border-gray-200 shadow-sm text-center max-w-3xl">
                ИИ меняет не только процессы — <span class="gradient-text">ИИ меняет саму компанию</span>
            </p>
        </div>
    """


def _heading(slide: dict, accent: str | None = None) -> str:
    title = esc(slide["title"])
    if accent and accent in title:
        title = title.replace(accent, f'<span class="gradient-text">{accent}</span>', 1)
    return (
        '<h2 class="text-xl md:text-3xl lg:text-5xl font-black '
        'mb-4 md:mb-8 text-center text-gray-900 leading-tight px-2">'
        f'{title}</h2>'
    )


def _punch(slide: dict) -> str:
    """Footer punchline wrapper — tighter on mobile."""
    return (
        '<p class="font-bold text-xs md:text-base lg:text-lg text-gray-800 '
        'bg-white px-4 md:px-6 py-2 md:py-3 rounded-xl border border-gray-200 '
        'shadow-sm text-center max-w-3xl">'
        f'{_punchline(slide)}</p>'
    )


def _punchline(slide: dict) -> str:
    """A short tail derived from the last sentence of narration."""
    narration = slide["narration"].strip()
    # last sentence
    for sep in ("». ", ". "):
        if sep in narration:
            tail = narration.rsplit(sep, 1)[-1]
            if len(tail) < 220:
                return esc(tail).rstrip(".") + "."
    return esc(narration[-220:]) + "…"


_DEFAULT_LEFT_ITEMS = [
    ("ph-fill ph-x-circle", "Только люди / устаревшая логика"),
    ("ph-fill ph-x-circle", "Ускорение без новой роли человека"),
    ("ph-fill ph-x-circle", "Старые KPI, инструкции, обучение"),
]
_DEFAULT_RIGHT_ITEMS = [
    ("ph-fill ph-check-circle", "Гибрид: человек + AI в одном процессе"),
    ("ph-fill ph-check-circle", "Новая роль человека — цели, границы, ответственность"),
    ("ph-fill ph-check-circle", "Метрики эффекта, а не активности"),
]


def _render_col_items(items, *, side: str) -> str:
    if side == "left":
        item_cls = "bg-white p-2 md:p-3 rounded-lg md:rounded-xl shadow-sm flex items-start gap-2 md:gap-3 border border-gray-100"
        icon_cls = "text-gray-400 text-base md:text-lg mt-0.5"
        text_cls = "text-gray-700"
    else:
        item_cls = "bg-white p-2 md:p-3 rounded-lg md:rounded-xl shadow-sm flex items-start gap-2 md:gap-3 border border-purple-100"
        icon_cls = "text-purple-500 text-base md:text-lg mt-0.5"
        text_cls = "text-purple-900"
    rows = []
    for icon, text in items:
        rows.append(
            f'<li class="{item_cls}"><i class="{icon} {icon_cls}"></i><span class="{text_cls}">{esc(text)}</span></li>'
        )
    return "\n                        ".join(rows)


def render_two_col(slide: dict, layout: dict) -> str:
    left_items = layout.get("left_items") or _DEFAULT_LEFT_ITEMS
    right_items = layout.get("right_items") or _DEFAULT_RIGHT_ITEMS
    return f"""
        <div class="content-z max-w-6xl h-full flex flex-col items-center justify-center">
            {_heading(slide)}
            <div class="flex flex-col md:flex-row items-stretch gap-3 md:gap-6 w-full max-w-5xl mb-3 md:mb-8">
                <div class="flex-1 bg-gray-50 border border-gray-200 p-3 md:p-6 rounded-2xl md:rounded-3xl">
                    <h3 class="font-bold text-gray-400 uppercase tracking-widest mb-2 md:mb-4 text-xs md:text-sm text-center">{esc(layout.get('left','Было'))}</h3>
                    <div class="h-0.5 md:h-1 w-10 md:w-12 bg-gradient-to-r from-gray-300 to-gray-200 mx-auto mb-2 md:mb-4 rounded-full"></div>
                    <ul class="text-xs md:text-sm flex flex-col gap-1.5 md:gap-2">
                        {_render_col_items(left_items, side="left")}
                    </ul>
                </div>
                <div class="flex items-center justify-center -my-1 md:my-0">
                    <i class="ph-bold ph-arrow-right text-3xl md:text-4xl text-purple-400 hidden md:block"></i>
                    <i class="ph-bold ph-arrow-down text-2xl md:text-4xl text-purple-400 md:hidden"></i>
                </div>
                <div class="flex-1 bg-purple-50 border border-purple-200 p-3 md:p-6 rounded-2xl md:rounded-3xl shadow-lg">
                    <h3 class="font-bold text-purple-600 uppercase tracking-widest mb-2 md:mb-4 text-xs md:text-sm text-center">{esc(layout.get('right','Стало'))}</h3>
                    <div class="h-0.5 md:h-1 w-10 md:w-12 bg-gradient-to-r from-purple-400 to-orange-400 mx-auto mb-2 md:mb-4 rounded-full"></div>
                    <ul class="text-xs md:text-sm flex flex-col gap-1.5 md:gap-2">
                        {_render_col_items(right_items, side="right")}
                    </ul>
                </div>
            </div>
            {_punch(slide)}
        </div>
    """


def render_numbered(slide: dict, layout: dict) -> str:
    items = layout.get("items") or []
    rows = "".join(
        f"""
                <li class="bg-white p-2 md:p-4 rounded-xl md:rounded-2xl shadow-sm border border-purple-100 flex items-start gap-2 md:gap-3">
                    <div class="w-7 h-7 md:w-9 md:h-9 text-xs md:text-base shrink-0 rounded-lg md:rounded-xl bg-gradient-to-br from-purple-500 to-orange-500 text-white font-black flex items-center justify-center shadow">{i+1}</div>
                    <p class="text-xs md:text-base text-gray-800 mt-0.5 md:mt-1">{esc(text)}</p>
                </li>"""
        for i, text in enumerate(items)
    )
    return f"""
        <div class="content-z max-w-5xl h-full flex flex-col items-center justify-center">
            {_heading(slide)}
            <ul class="grid grid-cols-1 md:grid-cols-2 gap-2 md:gap-4 w-full mb-3 md:mb-8">{rows}
            </ul>
            {_punch(slide)}
        </div>
    """


def render_grid3(slide: dict, layout: dict) -> str:
    items = layout.get("items") or []
    cards = "".join(
        f"""
            <div class="bg-white p-3 md:p-5 rounded-2xl md:rounded-3xl shadow-md border border-purple-100 flex flex-row md:flex-col items-center md:text-center gap-3 md:gap-0">
                <div class="w-10 h-10 md:w-12 md:h-12 shrink-0 rounded-xl md:rounded-2xl bg-gradient-to-br from-purple-500 to-orange-500 text-white flex items-center justify-center md:mb-3 shadow-lg"><i class="{icon} text-base md:text-xl"></i></div>
                <div>
                  <h3 class="font-black text-gray-900 text-sm md:text-lg leading-tight md:mb-1">{esc(title)}</h3>
                  <p class="text-xs md:text-sm text-gray-600">{esc(desc)}</p>
                </div>
            </div>"""
        for icon, title, desc in items
    )
    return f"""
        <div class="content-z max-w-6xl h-full flex flex-col items-center justify-center">
            {_heading(slide)}
            <div class="grid grid-cols-1 md:grid-cols-3 gap-2 md:gap-5 w-full mb-3 md:mb-8">{cards}
            </div>
            {_punch(slide)}
        </div>
    """


def render_grid4(slide: dict, layout: dict) -> str:
    items = layout.get("items") or []
    cards = "".join(
        f"""
            <div class="bg-white p-3 md:p-5 rounded-2xl md:rounded-3xl shadow-md border border-purple-100 flex items-start gap-3 md:gap-4">
                <div class="w-9 h-9 md:w-12 md:h-12 shrink-0 rounded-xl md:rounded-2xl bg-gradient-to-br from-purple-500 to-orange-500 text-white flex items-center justify-center shadow-lg"><i class="{icon} text-base md:text-xl"></i></div>
                <div>
                    <h3 class="font-black text-gray-900 text-sm md:text-base leading-tight mb-0.5">{esc(title)}</h3>
                    <p class="text-xs md:text-sm text-gray-600">{esc(desc)}</p>
                </div>
            </div>"""
        for icon, title, desc in items
    )
    return f"""
        <div class="content-z max-w-6xl h-full flex flex-col items-center justify-center">
            {_heading(slide)}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2 md:gap-5 w-full mb-3 md:mb-8">{cards}
            </div>
            {_punch(slide)}
        </div>
    """


def render_quote(slide: dict, layout: dict) -> str:
    return f"""
        <div class="content-z max-w-5xl h-full flex flex-col items-center justify-center">
            {_heading(slide)}
            <div class="bg-gradient-to-br from-purple-600 via-pink-500 to-orange-500 p-1 md:p-1.5 rounded-2xl md:rounded-3xl shadow-2xl w-full max-w-3xl mb-3 md:mb-6">
                <div class="bg-white px-4 py-5 md:px-10 md:py-12 rounded-2xl md:rounded-[20px] text-center">
                    <p class="text-purple-600 font-semibold uppercase tracking-widest text-[10px] md:text-xs mb-2 md:mb-3">{esc(layout.get('kicker',''))}</p>
                    <p class="text-lg md:text-3xl lg:text-4xl font-black gradient-text leading-tight mb-2 md:mb-4">{esc(layout.get('main',''))}</p>
                    <p class="text-gray-700 text-sm md:text-base lg:text-lg">{esc(layout.get('tail',''))}</p>
                </div>
            </div>
            {_punch(slide)}
        </div>
    """


def render_pyramid(slide: dict, layout: dict) -> str:
    rows = layout.get("rows") or []
    n = len(rows)
    boxes = ""
    palette = ["from-purple-50 to-purple-100", "from-purple-100 to-pink-100",
               "from-pink-100 to-orange-100", "from-orange-100 to-orange-200",
               "from-orange-200 to-orange-300"]
    for i, row in enumerate(rows):
        width = 65 + i * (30 / max(1, n - 1))
        color = palette[i % len(palette)]
        boxes += f"""
            <div class="bg-gradient-to-r {color} border border-purple-100 rounded-xl md:rounded-2xl shadow-sm py-2 px-3 md:py-3 md:px-5 flex items-center gap-2 md:gap-3"
                 style="width:{width:.0f}%">
                <div class="w-7 h-7 md:w-8 md:h-8 shrink-0 rounded-lg md:rounded-xl bg-white flex items-center justify-center text-purple-700 font-black text-xs md:text-base border border-purple-100">{i+1}</div>
                <p class="text-xs md:text-base font-bold text-gray-900 leading-tight">{esc(row)}</p>
            </div>"""
    return f"""
        <div class="content-z max-w-5xl h-full flex flex-col items-center justify-center">
            {_heading(slide)}
            <p class="text-purple-600 font-semibold uppercase tracking-widest text-[10px] md:text-xs mb-2 md:mb-4">{esc(layout.get('title',''))}</p>
            <div class="flex flex-col items-center gap-1.5 md:gap-3 w-full mb-3 md:mb-8">{boxes}
            </div>
            {_punch(slide)}
        </div>
    """


def render_modes(slide: dict, layout: dict) -> str:
    items = layout.get("items") or []
    cards = "".join(
        f"""
            <div class="bg-white p-3 md:p-5 rounded-2xl md:rounded-3xl shadow-md border-2 border-purple-200 relative ml-4 md:ml-0">
                <div class="absolute -top-3 -left-4 md:-top-4 md:-left-4 w-9 h-9 md:w-12 md:h-12 bg-gradient-to-br from-purple-600 to-orange-500 text-white rounded-xl md:rounded-2xl flex items-center justify-center text-base md:text-xl font-black shadow-lg border-2 md:border-4 border-white">{num}</div>
                <h3 class="font-black text-purple-900 mt-1 md:mt-2 mb-0.5 md:mb-1 text-sm md:text-base leading-tight pl-6 md:pl-10">{esc(title)}</h3>
                <p class="text-xs md:text-sm text-gray-600 pl-6 md:pl-10">{esc(desc)}</p>
            </div>"""
        for num, title, desc in items
    )
    return f"""
        <div class="content-z max-w-6xl h-full flex flex-col items-center justify-center">
            {_heading(slide)}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-5 w-full mb-3 md:mb-8 pl-2 md:pl-0">{cards}
            </div>
            {_punch(slide)}
        </div>
    """


def render_cycle(slide: dict, layout: dict) -> str:
    items = layout.get("items") or []
    n = len(items)
    cards = "".join(
        f"""
            <div class="bg-white p-2 md:p-4 rounded-xl md:rounded-2xl shadow-md border border-purple-100 flex items-center gap-2 md:gap-3 min-w-0">
                <div class="w-8 h-8 md:w-10 md:h-10 text-xs md:text-base shrink-0 rounded-lg md:rounded-xl bg-gradient-to-br from-purple-500 to-orange-500 text-white flex items-center justify-center font-black shadow">{i+1}</div>
                <p class="text-xs md:text-base font-bold text-gray-900 leading-tight">{esc(text)}</p>
            </div>"""
        for i, text in enumerate(items)
    )
    return f"""
        <div class="content-z max-w-6xl h-full flex flex-col items-center justify-center">
            {_heading(slide)}
            <div class="grid grid-cols-2 md:grid-cols-3 gap-2 md:gap-4 w-full mb-3 md:mb-8">{cards}
            </div>
            {_punch(slide)}
        </div>
    """


TPL_FUNCS = {
    "title": render_title,
    "two_col": render_two_col,
    "numbered": render_numbered,
    "grid3": render_grid3,
    "grid4": render_grid4,
    "quote": render_quote,
    "pyramid": render_pyramid,
    "modes": render_modes,
    "cycle": render_cycle,
}


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------
HEAD = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Лекция 7: Люди, машины и новая логика управления</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <!-- Phosphor Icons -->
    <script src="https://unpkg.com/@phosphor-icons/web"></script>

    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Inter', 'sans-serif'] },
                    colors: {
                        brand: { purple: '#7c3aed', orange: '#f97316' }
                    }
                }
            }
        }
    </script>

<style>
    html { background: #ffffff !important; }
    body {
        user-select: none; overflow: hidden; background-color: #ffffff !important;
        margin: 0; width: 100vw; height: 100vh;
    }
    .slide-container {
        transition: opacity 0.4s ease-in-out, transform 0.4s ease-in-out;
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        display: flex; flex-direction: column; justify-content: center;
        overflow-y: auto; overflow-x: hidden; background: #ffffff;
        -ms-overflow-style: none; scrollbar-width: none;
        /* Bottom padding keeps the punchline above the fixed video bubble. */
        padding-bottom: 168px;
    }
    @media (min-width: 768px) {
        .slide-container { padding-bottom: 0; }
    }
    .slide-container::-webkit-scrollbar { display: none; }
    .content-z {
        position: relative; z-index: 10; margin: auto; width: 100%;
        padding-top: 1rem; padding-bottom: 1.5rem;
    }
    @media (min-width: 768px) { .content-z { padding-top: 2rem; padding-bottom: 2rem; } }
    .gradient-text {
        background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-image: linear-gradient(to right, #7c3aed, #f97316);
    }
    .gradient-bg { background-image: linear-gradient(135deg, #7c3aed, #f97316); }
    .bg-glow-1 {
        position: absolute; top: -20%; left: -10%; width: 80vw; height: 80vw; max-width: 800px; max-height: 800px;
        background: radial-gradient(circle, rgba(124,58,237,0.04) 0%, rgba(255,255,255,0) 70%); z-index: 0; pointer-events: none;
    }
    .bg-glow-2 {
        position: absolute; bottom: -20%; right: -10%; width: 60vw; height: 60vw; max-width: 600px; max-height: 600px;
        background: radial-gradient(circle, rgba(249,115,22,0.04) 0%, rgba(255,255,255,0) 70%); z-index: 0; pointer-events: none;
    }

    /* Video bubble (synced with current slide) — pattern from aisala/ai-agents-corp/6.
       Phone: 130×130 in lower-right with tight margin; tablet+ scales up. */
    #video-bubble {
        position: fixed; right: 12px; bottom: 16px; width: 130px; height: 130px;
        border-radius: 9999px; overflow: hidden; box-shadow: 0 14px 40px rgba(124,58,237,0.22);
        z-index: 100; cursor: grab; touch-action: none; background: #fff;
        border: 2px solid rgba(124,58,237,0.18);
    }
    @media (min-width: 480px) { #video-bubble { width: 160px; height: 160px; right: 16px; bottom: 20px; } }
    @media (min-width: 768px) { #video-bubble { width: 200px; height: 200px; right: 24px; bottom: 28px; } }
    @media (min-width: 1280px){ #video-bubble { width: 220px; height: 220px; } }
    #video-bubble:active { cursor: grabbing; }
    .video-wrapper { position: relative; width: 100%; height: 100%; }
    .video-wrapper video {
        position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block;
    }

    /* PDF Mode */
    body.pdf-export-mode { overflow: auto !important; height: auto !important; }
    body.pdf-export-mode .bg-glow-1, body.pdf-export-mode .bg-glow-2,
    body.pdf-export-mode #progress-container, body.pdf-export-mode #video-bubble { display: none !important; }
    body.pdf-export-mode .slide-container {
        position: relative !important; width: 100% !important; min-height: 100vh; height: auto !important;
        opacity: 1 !important; transform: none !important; pointer-events: auto !important; overflow: visible !important;
        page-break-after: always; break-after: page; break-inside: avoid;
    }
    @page { size: A4 landscape; margin: 10mm; }
    @media print {
        html, body { overflow: visible !important; height: auto !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .bg-glow-1, .bg-glow-2, #progress-container, #video-bubble { display: none !important; }
        .slide-container {
            position: relative !important; width: 100% !important; min-height: 100vh; height: auto !important;
            opacity: 1 !important; transform: none !important; pointer-events: auto !important; overflow: visible !important;
            page-break-after: always; break-after: page; break-inside: avoid;
        }
    }
</style>
</head>
<body class="text-gray-900 font-sans">

    <!-- Decorative background -->
    <div class="bg-glow-1"></div>
    <div class="bg-glow-2"></div>

    <!-- Progress bar -->
    <div id="progress-container" class="absolute bottom-0 left-0 h-1.5 bg-gray-100 w-full z-50">
        <div id="progress-bar" class="h-full gradient-bg w-0 transition-all duration-300"></div>
    </div>

    <!-- Draggable video bubble -->
    <div id="video-bubble" class="cursor-grab" style="display:none;" aria-label="Лекционный аватар">
        <div class="video-wrapper">
            <video id="bubble-video" playsinline preload="auto" muted></video>
        </div>
        <div id="video-overlay" class="absolute inset-0 flex flex-col items-center justify-center bg-black/40 opacity-0 transition-opacity text-white group z-20 cursor-pointer pointer-events-none">
            <i id="video-icon" class="ph-fill ph-pause-circle text-4xl md:text-6xl drop-shadow-md"></i>
        </div>
        <div id="video-loader" class="absolute inset-0 flex items-center justify-center bg-black/40 z-30 transition-opacity duration-300 opacity-0 pointer-events-none">
            <i class="ph-bold ph-circle-notch text-white text-4xl animate-spin"></i>
        </div>
        <div id="video-fallback" class="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-purple-100 to-orange-100 z-10 text-purple-700">
            <i class="ph-fill ph-user-circle text-5xl"></i>
            <p class="text-[10px] uppercase tracking-widest mt-1 font-bold">aisala</p>
        </div>
    </div>

    <!-- Start overlay (browser autoplay-policy gate) -->
    <div id="start-overlay" class="fixed inset-0 z-[200] flex flex-col items-center justify-center bg-white/95 backdrop-blur-sm">
        <div class="bg-gradient-to-br from-purple-600 via-pink-500 to-orange-500 p-1 rounded-3xl shadow-2xl">
            <div class="bg-white px-8 py-10 rounded-[22px] text-center max-w-md">
                <div class="w-14 h-14 mx-auto mb-3 rounded-2xl bg-gradient-to-br from-purple-500 to-orange-500 text-white flex items-center justify-center shadow"><i class="ph-fill ph-play-circle text-3xl"></i></div>
                <h2 class="text-2xl font-black gradient-text mb-2">Лекция 7</h2>
                <p class="text-gray-700 text-sm mb-5">Люди, машины и новая логика управления</p>
                <button id="start-btn" class="bg-gradient-to-r from-purple-600 to-orange-500 text-white font-bold px-6 py-3 rounded-2xl shadow hover:shadow-lg transition">Начать</button>
            </div>
        </div>
    </div>

"""


SCRIPT = """
<script>
    document.addEventListener('DOMContentLoaded', () => {
        const totalSlides = TOTAL_SLIDES_PLACEHOLDER;
        let currentSlide = 0;
        const progressBar = document.getElementById('progress-bar');
        const body = document.body;
        const params = new URLSearchParams(window.location.search);
        const exportMode = params.has('pdf') || params.get('mode') === 'pdf' || window.location.hash === '#pdf';

        // ---------- Slide navigation ---------------------------------------
        function updateProgress() {
            if (!progressBar) return;
            progressBar.style.width = `${((currentSlide + 1) / totalSlides) * 100}%`;
        }

        function updateSlides() {
            for (let i = 0; i < totalSlides; i++) {
                const slide = document.getElementById(`slide-${i}`);
                if (!slide) continue;
                if (i === currentSlide) {
                    slide.classList.remove('opacity-0', 'pointer-events-none', 'translate-y-8', '-translate-y-8');
                    slide.classList.add('opacity-100', 'translate-y-0');
                } else if (i < currentSlide) {
                    slide.classList.remove('opacity-100', 'translate-y-0', 'translate-y-8');
                    slide.classList.add('opacity-0', 'pointer-events-none', '-translate-y-8');
                } else {
                    slide.classList.remove('opacity-100', 'translate-y-0', '-translate-y-8');
                    slide.classList.add('opacity-0', 'pointer-events-none', 'translate-y-8');
                }
            }
            updateProgress();
            updateVideoForSlide();
        }

        function showAllSlidesForPdf() {
            body.classList.add('pdf-export-mode');
            for (let i = 0; i < totalSlides; i++) {
                const slide = document.getElementById(`slide-${i}`);
                if (!slide) continue;
                slide.classList.remove('opacity-0', 'pointer-events-none', 'translate-y-8', '-translate-y-8');
                slide.classList.add('opacity-100');
                slide.style.transform = 'none';
                slide.style.pointerEvents = 'auto';
            }
            if (progressBar) progressBar.style.width = '100%';
        }

        function restoreInteractiveMode() {
            body.classList.remove('pdf-export-mode');
            for (let i = 0; i < totalSlides; i++) {
                const slide = document.getElementById(`slide-${i}`);
                if (!slide) continue;
                slide.style.transform = '';
                slide.style.pointerEvents = '';
            }
            updateSlides();
        }

        function nextSlide() { if (currentSlide < totalSlides - 1) { currentSlide++; updateSlides(); } }
        function prevSlide() { if (currentSlide > 0) { currentSlide--; updateSlides(); } }

        // ---------- Video bubble -------------------------------------------
        const bubble = document.getElementById('video-bubble');
        const video = document.getElementById('bubble-video');
        const overlay = document.getElementById('video-overlay');
        const videoIcon = document.getElementById('video-icon');
        const loader = document.getElementById('video-loader');
        const fallback = document.getElementById('video-fallback');

        function videoSrcFor(slideIdx) { return `videos/${slideIdx + 1}.mp4`; }

        function showFallback(show) {
            if (!fallback) return;
            fallback.style.display = show ? 'flex' : 'none';
        }

        function updateVideoForSlide() {
            if (!video || exportMode) return;
            const target = videoSrcFor(currentSlide);
            if (video.dataset.currentSrc === target) return;
            video.dataset.currentSrc = target;
            try { video.pause(); } catch (e) { /* ignore */ }
            video.src = target;
            showFallback(true);
            video.load();
            const p = video.play();
            if (p && p.catch) p.catch(() => { /* autoplay blocked → fallback shown */ });
        }

        if (video) {
            video.addEventListener('loadeddata', () => showFallback(false));
            video.addEventListener('playing',    () => { showFallback(false); loader.classList.add('opacity-0'); });
            video.addEventListener('waiting',    () => loader.classList.remove('opacity-0'));
            video.addEventListener('error',      () => { showFallback(true); loader.classList.add('opacity-0'); console.warn('video missing:', video.src); });
            video.addEventListener('play',       () => { videoIcon.className = 'ph-fill ph-pause-circle text-4xl md:text-6xl drop-shadow-md'; });
            video.addEventListener('pause',      () => { videoIcon.className = 'ph-fill ph-play-circle text-4xl md:text-6xl drop-shadow-md'; overlay.classList.remove('opacity-0'); });
            video.addEventListener('ended',      () => { videoIcon.className = 'ph-fill ph-play-circle text-4xl md:text-6xl drop-shadow-md'; overlay.classList.remove('opacity-0'); });
        }

        if (overlay) {
            overlay.style.pointerEvents = 'auto';
            overlay.addEventListener('click', (e) => {
                e.stopPropagation();
                if (!video) return;
                if (video.paused) video.play().catch(() => {});
                else video.pause();
            });
        }

        // ---------- Drag-and-snap ------------------------------------------
        const SNAP_MARGIN = 16;
        let dragging = false, startX = 0, startY = 0, baseX = 0, baseY = 0, moved = false;

        function loadPos() {
            try {
                const raw = localStorage.getItem('l7_bubble_pos');
                if (!raw) return;
                const p = JSON.parse(raw);
                if (typeof p.x === 'number' && typeof p.y === 'number') {
                    bubble.style.right = 'auto'; bubble.style.bottom = 'auto';
                    bubble.style.left = `${p.x}px`; bubble.style.top = `${p.y}px`;
                }
            } catch (_) { /* ignore */ }
        }
        function savePos() {
            const r = bubble.getBoundingClientRect();
            localStorage.setItem('l7_bubble_pos', JSON.stringify({ x: r.left, y: r.top }));
        }

        function pointerDown(ev) {
            dragging = true; moved = false;
            const p = ev.touches ? ev.touches[0] : ev;
            startX = p.clientX; startY = p.clientY;
            const r = bubble.getBoundingClientRect();
            baseX = r.left; baseY = r.top;
            bubble.style.right = 'auto'; bubble.style.bottom = 'auto';
            ev.preventDefault();
        }
        function pointerMove(ev) {
            if (!dragging) return;
            const p = ev.touches ? ev.touches[0] : ev;
            const dx = p.clientX - startX, dy = p.clientY - startY;
            if (Math.abs(dx) + Math.abs(dy) > 4) moved = true;
            bubble.style.left = `${baseX + dx}px`;
            bubble.style.top  = `${baseY + dy}px`;
        }
        function pointerUp(ev) {
            if (!dragging) return;
            dragging = false;
            const r = bubble.getBoundingClientRect();
            const w = window.innerWidth, h = window.innerHeight;
            const snapX = (r.left + r.width / 2) < w / 2 ? SNAP_MARGIN : (w - r.width - SNAP_MARGIN);
            const snapY = Math.min(Math.max(SNAP_MARGIN, r.top), h - r.height - SNAP_MARGIN);
            bubble.style.left = `${snapX}px`; bubble.style.top = `${snapY}px`;
            savePos();
        }

        bubble.addEventListener('mousedown', pointerDown);
        window.addEventListener('mousemove', pointerMove);
        window.addEventListener('mouseup',   pointerUp);
        bubble.addEventListener('touchstart', pointerDown, { passive: false });
        window.addEventListener('touchmove',  pointerMove, { passive: false });
        window.addEventListener('touchend',   pointerUp);

        // ---------- Print / PDF --------------------------------------------
        window.addEventListener('beforeprint', () => showAllSlidesForPdf());
        window.addEventListener('afterprint',  () => { if (!exportMode) restoreInteractiveMode(); });
        if (exportMode) { showAllSlidesForPdf(); bubble.style.display = 'none'; return; }

        // ---------- Input --------------------------------------------------
        window.addEventListener('keydown', (e) => {
            if (['ArrowRight', ' ', 'Enter', 'PageDown'].includes(e.key)) nextSlide();
            else if (['ArrowLeft', 'PageUp', 'Backspace'].includes(e.key)) prevSlide();
        });
        window.addEventListener('mousedown', (e) => {
            if (e.target.closest('#video-bubble') || e.target.closest('#video-overlay') || e.target.closest('#start-overlay') || e.target.closest('button') || e.target.closest('a')) return;
            if (e.button === 0) nextSlide();
            if (e.button === 2) prevSlide();
        });
        window.addEventListener('contextmenu', e => { if (!e.target.closest('#video-bubble')) e.preventDefault(); });

        let touchStartX = 0;
        window.addEventListener('touchstart', e => { touchStartX = e.changedTouches[0].screenX; }, { passive: true });
        window.addEventListener('touchend',   e => {
            if (e.target.closest('#video-bubble')) return;
            const dx = e.changedTouches[0].screenX - touchStartX;
            if (Math.abs(dx) > 50) { dx < 0 ? nextSlide() : prevSlide(); }
        }, { passive: true });

        // ---------- Start gate ---------------------------------------------
        document.getElementById('start-btn').addEventListener('click', () => {
            document.getElementById('start-overlay').style.display = 'none';
            bubble.style.display = 'block';
            if (video) { video.muted = false; video.play().catch(() => {}); }
            loadPos();
            updateVideoForSlide();
        });

        updateSlides();
    });
</script>

</body>
</html>
"""


def render_slide(slide: dict) -> str:
    layout = LAYOUT_TABLE.get(slide["id"], {"tpl": "two_col"})
    tpl = layout["tpl"]
    fn = TPL_FUNCS.get(tpl, render_two_col)
    return fn(slide, layout)


def main() -> int:
    data = json.loads(SLIDES_PATH.read_text(encoding="utf-8"))
    slides = data["slides"]
    parts = [HEAD]
    for idx, slide in enumerate(slides):
        cls = "opacity-100 translate-y-0" if idx == 0 else "opacity-0 pointer-events-none translate-y-8"
        parts.append(f'    <!-- СЛАЙД {slide["id"]}: {esc(slide["title"])} -->\n')
        parts.append(
            f'    <div class="slide-container px-4 md:px-12 {cls}" id="slide-{idx}">\n'
        )
        parts.append(render_slide(slide))
        parts.append("    </div>\n\n")
    parts.append(SCRIPT.replace("TOTAL_SLIDES_PLACEHOLDER", str(len(slides))))
    OUT_PATH.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {OUT_PATH} with {len(slides)} slides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
