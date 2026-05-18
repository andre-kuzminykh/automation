#!/usr/bin/env python3
"""Build l7/index.html in the aisala/ai-agents-corp/6 design style.

Every slide is hand-crafted with content matching its narration.
Final slide opens a 10-question quiz modal.

Run:
    python3 l7/scripts/build_aisala_style.py
"""

from __future__ import annotations

import html as _html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SLIDES_PATH = ROOT / "l7/data/slides.json"
OUT_PATH = ROOT / "l7/index.html"

# ----------------------------- helpers ---------------------------------------
def e(s: str) -> str:
    return _html.escape(s, quote=True)


def H(text: str, accent: str = "") -> str:
    if accent and accent in text:
        b, _, a = text.partition(accent)
        return (f'<h2 class="text-xl sm:text-3xl md:text-5xl font-black '
                f'mb-3 md:mb-6 text-center text-black leading-tight">'
                f'{e(b)}<span class="text-solar">{e(accent)}</span>{e(a)}</h2>')
    return (f'<h2 class="text-xl sm:text-3xl md:text-5xl font-black '
            f'mb-3 md:mb-6 text-center text-black leading-tight">{e(text)}</h2>')


def S(text: str) -> str:
    return (f'<p class="text-center text-black/60 mb-4 md:mb-8 '
            f'text-[11px] md:text-xl font-medium max-w-3xl mx-auto">{e(text)}</p>')


def P(text: str) -> str:
    return (f'<div class="bg-solar text-black font-black text-center '
            f'text-[11px] md:text-base rounded-2xl p-3 md:p-4 max-w-4xl mx-auto w-full">{e(text)}</div>')


def L(text: str) -> str:
    """Section label (uppercase, gray)."""
    return (f'<p class="text-[10px] md:text-xs font-bold uppercase '
            f'tracking-widest text-black/40 mb-3 md:mb-4 text-center">{e(text)}</p>')


def C(icon: str, label: str, *, dark: bool = False) -> str:
    """Centered card (icon above, label below)."""
    if dark:
        return (f'<div class="bg-black border-2 border-solar rounded-2xl '
                f'p-2 md:p-4 text-center shadow-xl text-white">'
                f'<i class="{icon} text-solar text-lg md:text-2xl mb-1 md:mb-2"></i>'
                f'<p class="font-black text-[10px] md:text-sm text-solar">{e(label)}</p></div>')
    return (f'<div class="bg-white border border-grayBase rounded-2xl '
            f'p-2 md:p-4 text-center shadow-sm">'
            f'<i class="{icon} text-solar text-lg md:text-2xl mb-1 md:mb-2"></i>'
            f'<p class="font-bold text-[10px] md:text-sm">{e(label)}</p></div>')


def R(icon: str, label: str, *, dark: bool = False) -> str:
    """Row card (icon left, label right) — works for longer labels."""
    if dark:
        return (f'<div class="bg-black border-2 border-solar rounded-2xl '
                f'p-3 md:p-4 shadow-xl text-white flex items-center gap-2 md:gap-3">'
                f'<i class="{icon} text-solar text-lg md:text-2xl shrink-0"></i>'
                f'<p class="font-black text-[11px] md:text-sm text-solar">{e(label)}</p></div>')
    return (f'<div class="bg-white border border-grayBase rounded-2xl '
            f'p-3 md:p-4 shadow-sm flex items-center gap-2 md:gap-3">'
            f'<i class="{icon} text-solar text-lg md:text-2xl shrink-0"></i>'
            f'<p class="font-bold text-[11px] md:text-sm">{e(label)}</p></div>')


def grid(cards: list[str], cols: str = "grid-cols-2 md:grid-cols-3") -> str:
    return (f'<div class="grid {cols} gap-2 md:gap-3 max-w-5xl mx-auto '
            f'w-full mb-3 md:mb-6">{"".join(cards)}</div>')


def two_cards(left_label: str, left_items: list[tuple[str, str]],
              right_label: str, right_items: list[tuple[str, str]]) -> str:
    """Light vs dark side-by-side cards with icon+text lists."""
    lh = "".join(
        f'<li class="flex items-center gap-2 md:gap-3"><i class="{i} text-solar shrink-0 text-base md:text-lg"></i><span>{e(t)}</span></li>'
        for i, t in left_items)
    rh = "".join(
        f'<li class="flex items-center gap-2 md:gap-3"><i class="{i} text-solar shrink-0 text-base md:text-lg"></i><span>{e(t)}</span></li>'
        for i, t in right_items)
    return (
        '<div class="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4 w-full max-w-5xl mx-auto mb-3 md:mb-4">'
        '<div class="bg-white border border-grayBase rounded-[20px] md:rounded-3xl p-4 md:p-6 shadow-sm">'
        f'<p class="text-[10px] md:text-xs font-bold uppercase tracking-widest text-black/40 mb-3 md:mb-4">{e(left_label)}</p>'
        f'<ul class="space-y-1.5 md:space-y-2 text-[12px] md:text-sm font-medium text-black/80">{lh}</ul></div>'
        '<div class="bg-black border-2 border-solar rounded-[20px] md:rounded-3xl p-4 md:p-6 shadow-xl text-white">'
        f'<p class="text-[10px] md:text-xs font-bold uppercase tracking-widest text-solar/70 mb-3 md:mb-4">{e(right_label)}</p>'
        f'<ul class="space-y-1.5 md:space-y-2 text-[12px] md:text-sm font-medium text-white/85">{rh}</ul></div></div>'
    )


def numbered(items: list[str], cols: str = "md:grid-cols-2") -> str:
    cells = "".join(
        f'<div class="bg-white border border-grayBase rounded-2xl p-2 md:p-4 shadow-sm flex items-start gap-2 md:gap-3">'
        f'<div class="w-7 h-7 md:w-9 md:h-9 bg-solar rounded-full flex items-center justify-center text-black font-black text-[11px] md:text-sm shrink-0">{i+1}</div>'
        f'<p class="font-bold text-[11px] md:text-sm leading-snug pt-0.5 md:pt-1">{e(t)}</p></div>'
        for i, t in enumerate(items))
    return f'<div class="grid grid-cols-1 {cols} gap-2 md:gap-3 max-w-5xl mx-auto w-full mb-3 md:mb-6">{cells}</div>'


def quote(kicker: str, main: str, tail: str) -> str:
    return (
        '<div class="w-full max-w-4xl mx-auto bg-black border-2 border-solar rounded-[24px] md:rounded-[32px] p-4 md:p-10 shadow-[0_0_40px_rgba(53,240,199,0.25)] text-white text-center mb-3 md:mb-6">'
        f'<p class="text-[10px] md:text-xs font-bold uppercase tracking-widest text-solar/70 mb-2 md:mb-4">{e(kicker)}</p>'
        f'<p class="text-lg md:text-3xl lg:text-4xl font-black text-solar leading-tight mb-2 md:mb-5">{e(main)}</p>'
        f'<p class="text-white/70 text-[11px] md:text-base font-medium">{e(tail)}</p></div>'
    )


def pyramid(rows: list[str]) -> str:
    n = len(rows)
    boxes = []
    for i, row in enumerate(rows):
        width = 65 + i * (30 / max(1, n - 1))
        bg = "bg-grayBase/40" if i < n - 1 else "bg-solar"
        boxes.append(
            f'<div class="{bg} border border-grayBase rounded-xl md:rounded-2xl py-2 px-3 md:py-3 md:px-5 flex items-center gap-2 md:gap-3" style="width:{width:.0f}%">'
            f'<div class="w-7 h-7 md:w-8 md:h-8 shrink-0 rounded-lg md:rounded-xl bg-white flex items-center justify-center text-black font-black text-xs md:text-base border border-grayBase">{i+1}</div>'
            f'<p class="text-[11px] md:text-base font-bold leading-tight text-black">{e(row)}</p></div>')
    return f'<div class="flex flex-col items-center gap-1.5 md:gap-3 w-full max-w-3xl mx-auto mb-3 md:mb-6">{"".join(boxes)}</div>'


def wrap(idx: int, comment: str, body: str, *, dark: bool = False) -> str:
    bg = " bg-black text-white" if dark else ""
    state = "opacity-100 translate-y-0" if idx == 0 else "opacity-0 pointer-events-none translate-y-8"
    return (f'\n    <!-- СЛАЙД {idx+1}: {comment} -->\n'
            f'    <div class="slide-container px-3 sm:px-6 md:px-12 {state}{bg}" id="slide-{idx}">\n'
            f'        <div class="content-z max-w-6xl w-full">\n{body}\n'
            f'        </div>\n    </div>\n')


# ============================== SLIDES =======================================
def s1():  # Title — AI as company change
    body = (
        '<div class="flex justify-center mb-3 md:mb-8">'
        '<div class="bg-grayBase/30 border border-grayBase rounded-full px-3 py-1 md:px-4 md:py-2 shadow-sm">'
        '<p class="text-black font-bold uppercase tracking-widest text-[9px] md:text-sm m-0">Лекция 7: AI-трансформация компании</p>'
        '</div></div>'
        '<h1 class="text-xl sm:text-4xl md:text-5xl lg:text-[60px] font-black mb-2 md:mb-6 leading-tight tracking-tight text-black text-center">'
        'Люди, машины и <span class="text-solar">новая логика управления</span></h1>'
        '<p class="text-black/70 font-bold text-[11px] md:text-2xl mb-2 md:mb-4 max-w-3xl mx-auto text-center">Как компания становится гибридной системой</p>'
        '<p class="text-black/50 font-medium text-[10px] md:text-base mb-4 md:mb-8 max-w-3xl mx-auto text-center">AI меняет не только процессы — AI меняет само устройство компании</p>'
        + grid([
            C("ph-fill ph-target", "Решения"),
            C("ph-fill ph-shield-check", "Ответственность"),
            C("ph-fill ph-flow-arrow", "Процессы"),
            C("ph-fill ph-graduation-cap", "Обучение"),
            C("ph-fill ph-eye", "Внимание"),
            C("ph-fill ph-users-three", "Гибрид", dark=True),
        ], "grid-cols-3 md:grid-cols-6")
        + P("Человеческая → Гибридная → AI-First компания")
    )
    return wrap(0, "Титульный — AI как изменение компании", body)


def s2():  # Главная идея
    body = (
        H("Главная идея лекции", "лекции")
        + S("AI-агенты меняют компанию не только технически, но и организационно")
        + two_cards(
            "Раньше — человеческая система",
            [("ph-fill ph-user", "Люди думают"),
             ("ph-fill ph-user-gear", "Люди принимают решения"),
             ("ph-fill ph-check-square", "Люди контролируют"),
             ("ph-fill ph-shield-check", "Люди отвечают")],
            "Теперь — гибридная",
            [("ph-fill ph-magnifying-glass", "AI анализирует данные"),
             ("ph-fill ph-lightbulb", "AI предлагает варианты"),
             ("ph-fill ph-lightning", "AI выполняет действия"),
             ("ph-fill ph-warning", "AI отслеживает отклонения")])
        + P("Часть работы делают люди, часть — AI, часть готовится машиной и утверждается человеком")
    )
    return wrap(1, "Главная идея", body)


def s3():  # Новый главный вопрос
    body = (
        H("Новый главный вопрос", "вопрос")
        + S("«Как внедрить AI?» — уже недостаточно. Спрашивать нужно про управление гибридной системой")
        + '<div class="bg-grayBase/40 border border-grayBase rounded-2xl p-3 md:p-5 max-w-4xl mx-auto w-full mb-3 md:mb-5 text-center"><p class="text-[10px] md:text-xs font-bold uppercase tracking-widest text-black/40 mb-1 md:mb-2">Старый вопрос</p><p class="text-sm md:text-xl font-bold text-black/50 line-through">Как нам внедрить AI?</p></div>'
        + L("Новые вопросы")
        + grid([
            R("ph-fill ph-robot", "Где AI может действовать сам?"),
            R("ph-fill ph-eye", "Где человек должен контролировать?"),
            R("ph-fill ph-gavel", "Где обязательно финальное слово человека?"),
            R("ph-fill ph-shield-check", "Кто отвечает за результат?", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + P("Не просто подключить AI, а встроить в работу компании так, чтобы стало сильнее")
    )
    return wrap(2, "Новый главный вопрос", body)


def s4():  # ИИ не просто автоматизация
    body = (
        H("ИИ — не просто автоматизация", "автоматизация")
        + S("Автоматизация ускоряет старую логику. AI меняет саму логику процесса")
        + two_cards(
            "Автоматизация",
            [("ph-fill ph-fast-forward", "Ускоряет существующий шаг"),
             ("ph-fill ph-arrows-clockwise", "Заменяет ручную операцию"),
             ("ph-fill ph-clock-counter-clockwise", "Та же логика, быстрее")],
            "Искусственный интеллект",
            [("ph-fill ph-brain", "Анализирует ситуацию"),
             ("ph-fill ph-graph", "Находит закономерности"),
             ("ph-fill ph-lightbulb", "Предлагает решения"),
             ("ph-fill ph-eye", "Контролирует отклонения")])
        + P("Меняется не только скорость, но и сама логика процесса")
    )
    return wrap(3, "ИИ — не просто автоматизация", body)


def s5():  # Почему старые подходы не работают
    body = (
        H("Почему старые подходы перестают работать", "перестают работать")
        + S("Можно технически внедрить AI и остаться старой компанией")
        + L("Что обычно остаётся прежним")
        + grid([
            C("ph-fill ph-clipboard-text", "Должностные инструкции"),
            C("ph-fill ph-chart-bar", "Старые KPI"),
            C("ph-fill ph-graduation-cap", "Обучение «как раньше»"),
            C("ph-fill ph-warning", "Размытая ответственность", dark=True),
        ], "grid-cols-2 md:grid-cols-4")
        + '<div class="bg-black border-2 border-solar rounded-2xl p-3 md:p-4 max-w-4xl mx-auto w-full text-white text-center mb-3"><p class="font-black text-[11px] md:text-base text-solar">KPI измеряют занятость, не эффект. Обучение учит кнопкам, а не работе по-новому</p></div>'
        + P("Внедрение AI — это не IT-проект. Это управленческая трансформация")
    )
    return wrap(4, "Почему старые подходы не работают", body)


def s6():  # Внедрение ИИ = управленческая трансформация
    body = (
        H("Внедрение ИИ — это управленческая трансформация", "трансформация")
        + S("Купили инструмент, подключили модель, запустили пилот — это ещё не изменение")
        + quote("Ключевой переход",
                "AI входит не в вакуум — в живую организацию",
                "С людьми, ответственностью, привычками и управленческой логикой")
        + L("Что должно пересобраться")
        + grid([
            C("ph-fill ph-user-circle-gear", "Роли"),
            C("ph-fill ph-flow-arrow", "Процессы"),
            C("ph-fill ph-scroll", "Правила"),
            C("ph-fill ph-graduation-cap", "Обучение"),
            C("ph-fill ph-chart-line-up", "Показатели", dark=True),
        ], "grid-cols-3 md:grid-cols-5")
        + P("Иначе AI будет работать сбоку от реального бизнеса")
    )
    return wrap(5, "Управленческая трансформация", body)


def s7():  # Что такое гибридная система
    body = (
        H("Что такое гибридная система", "гибридная система")
        + S("Человек и AI в одном процессе, но с разными функциями")
        + two_cards(
            "Человек",
            [("ph-fill ph-compass", "Задаёт цель"),
             ("ph-fill ph-scroll", "Определяет правила"),
             ("ph-fill ph-warning-octagon", "Принимает рискованные решения"),
             ("ph-fill ph-shield-check", "Отвечает за последствия")],
            "AI",
            [("ph-fill ph-database", "Анализирует данные"),
             ("ph-fill ph-gear", "Выполняет операции"),
             ("ph-fill ph-graph", "Ищет закономерности"),
             ("ph-fill ph-eye", "Следит за отклонениями")])
        + P("Не замена человека — правильное распределение работы между человеком и машиной")
    )
    return wrap(6, "Гибридная система", body)


def s8():  # Результат создаётся взаимодействием
    body = (
        H("Результат создаётся взаимодействием", "взаимодействием")
        + S("Ценность появляется в связке, а не отдельно у человека или AI")
        + two_cards(
            "Слабая модель",
            [("ph-fill ph-x-circle", "AI просто «добавили» в процесс"),
             ("ph-fill ph-x-circle", "Эффект ждут сам собой"),
             ("ph-fill ph-x-circle", "Роли не описаны"),
             ("ph-fill ph-x-circle", "Ответственность размыта")],
            "Сильная модель",
            [("ph-fill ph-check", "Кто ставит задачу"),
             ("ph-fill ph-check", "Кто готовит решение"),
             ("ph-fill ph-check", "Кто проверяет результат"),
             ("ph-fill ph-check", "Кто принимает финальное решение"),
             ("ph-fill ph-check", "Кто отвечает за последствия")])
        + P("Взаимодействие AI и человека должно быть специально спроектировано")
    )
    return wrap(7, "Результат через взаимодействие", body)


def s9():  # Было: человеческая
    body = (
        H("Было: человеческая организация", "человеческая")
        + S("Человек был главным центром смысла, решения и контроля")
        + pyramid([
            "Человек принимает решение",
            "Человек согласовывает",
            "Человек контролирует",
            "Человек делает",
            "Человек отвечает",
        ])
        + '<div class="bg-black border-2 border-solar rounded-2xl p-3 md:p-4 max-w-4xl mx-auto w-full text-white text-center mb-3"><p class="font-black text-[11px] md:text-base text-solar">Естественное ограничение — человеческое внимание</p></div>'
        + P("Компания упирается не только в нехватку людей, но и в их способность обрабатывать сложность")
    )
    return wrap(8, "Было: человеческая", body)


def s10():  # Стало: гибридная
    body = (
        H("Стало: гибридная организация", "гибридная")
        + S("AI становится внешним слоем мышления компании")
        + pyramid([
            "AI: рутина и мониторинг",
            "AI: первичный анализ",
            "AI: подготовка вариантов",
            "Человек: цели и правила",
            "Человек: ответственность",
        ])
        + '<div class="bg-black border-2 border-solar rounded-2xl p-3 md:p-4 max-w-4xl mx-auto w-full text-white text-center mb-3"><p class="font-black text-[11px] md:text-base text-solar">Не компания без людей — компания, где мышление усилено машиной</p></div>'
        + P("AI расширяет возможности, направление всё равно задаёт человек")
    )
    return wrap(9, "Стало: гибридная", body)


def s11():  # Новая роль человека
    body = (
        H("Новая роль человека", "человека")
        + S("Человек не исчезает. Его роль становится важнее — но другой")
        + numbered([
            "Задавать цели",
            "Формулировать правила",
            "Определять границы автономности AI",
            "Отвечать за последствия",
        ])
        + '<div class="bg-black border-2 border-solar rounded-2xl p-3 md:p-4 max-w-4xl mx-auto w-full text-white text-center mb-3"><p class="font-black text-[11px] md:text-base text-solar">Не просто выполнять задачи внутри процесса — проектировать саму логику работы</p></div>'
        + P("Человек становится архитектором и оператором системы")
    )
    return wrap(10, "Новая роль человека", body)


def s12():  # Гибридность != полная автоматизация
    body = (
        H("Гибридность — не полная автоматизация", "не полная автоматизация")
        + S("Разница в том, остаётся человек в процессе или нет")
        + two_cards(
            "Полная автоматизация",
            [("ph-fill ph-user-minus", "Человек полностью вне процесса"),
             ("ph-fill ph-robot", "Только машинная логика"),
             ("ph-fill ph-warning", "Допустима лишь там, где нет смыслов и этики")],
            "Гибридность",
            [("ph-fill ph-users-three", "Функции и ответственность распределены"),
             ("ph-fill ph-lightning", "AI: скорость, масштаб, мониторинг"),
             ("ph-fill ph-user-focus", "Человек: цель, этика, риск, выбор"),
             ("ph-fill ph-shield-check", "Ответственность перед клиентом и обществом")])
        + P("Не «что можно автоматизировать полностью?», а «где AI действует, где человек обязан остаться?»")
    )
    return wrap(11, "Гибридность ≠ автоматизация", body)


def s13():  # Где человек остаётся главным
    body = (
        H("Где человек остаётся главным", "главным")
        + S("Четыре зоны, в которых нельзя отдавать решение алгоритму")
        + grid([
            R("ph-fill ph-compass", "Постановка целей — ради чего существует бизнес"),
            R("ph-fill ph-warning-octagon", "Рискованные решения с серьёзными последствиями"),
            R("ph-fill ph-scales", "Этика — не всё эффективное допустимо"),
            R("ph-fill ph-shield-check", "Ответственность перед клиентом, командой, регулятором", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + P("«Так решил алгоритм» — не ответ ни клиенту, ни регулятору")
    )
    return wrap(12, "Где человек главный", body)


def s14():  # Где ИИ объективно сильнее
    body = (
        H("Где ИИ объективно сильнее", "сильнее")
        + S("Зоны, в которых AI делает работу лучше человека")
        + grid([
            R("ph-fill ph-database", "Большие объёмы данных и документов"),
            R("ph-fill ph-magnifying-glass", "Поиск слабых сигналов и закономерностей"),
            R("ph-fill ph-arrows-clockwise", "Повторяемые рутинные действия"),
            R("ph-fill ph-eye", "Постоянный круглосуточный мониторинг", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + P("Человек устаёт и отвлекается — AI мониторит непрерывно")
    )
    return wrap(13, "Где ИИ сильнее", body)


def s15():  # Режимы самостоятельности
    body = (
        H("Режимы самостоятельности ИИ", "самостоятельности")
        + S("Четыре уровня — от полной проверки человеком до соавторства")
        + '<div class="grid grid-cols-1 md:grid-cols-2 gap-2 md:gap-4 max-w-5xl mx-auto w-full mb-3 md:mb-6">'
        + ''.join(
            f'<div class="bg-white border border-grayBase rounded-2xl p-3 md:p-5 shadow-sm">'
            f'<div class="flex items-center gap-2 md:gap-3 mb-1 md:mb-3">'
            f'<div class="w-8 h-8 md:w-11 md:h-11 bg-solar rounded-full flex items-center justify-center text-black font-black text-[12px] md:text-base">{n}</div>'
            f'<h3 class="font-black text-[12px] md:text-lg">{e(t)}</h3></div>'
            f'<p class="text-[11px] md:text-sm text-black/60">{e(d)}</p></div>'
            for n, t, d in [
                ("1", "AI предлагает, человек решает", "Самый безопасный режим: сложные и рискованные задачи"),
                ("2", "AI действует, человек контролирует", "Повторяемые процессы с понятными правилами"),
                ("3", "AI действует самостоятельно", "Низкие риски, понятные сценарии, возможность остановить"),
                ("4", "Соавторство", "Человек и AI вместе создают документ, анализ, стратегию"),
            ])
        + '</div>'
        + P("Главная задача управления — определить, где какой режим допустим")
    )
    return wrap(14, "Режимы самостоятельности", body)


def s16():  # Где допустима автономность
    body = (
        H("Где допустима автономность ИИ", "автономность")
        + S("Не там, где хочется ускориться, а там, где безопасно")
        + numbered([
            "Сценарии понятны",
            "Риски низкие",
            "Правила описаны заранее",
            "Действия логируются",
            "Есть способ остановить систему",
            "Есть порядок разбора ошибок",
        ])
        + P("Управляемый режим внутри заранее определённых границ — не свобода алгоритма делать что угодно")
    )
    return wrap(15, "Где допустима автономность", body)


def s17():  # Управление = управление границей
    body = (
        H("Управление изменениями — это управление границей", "границей")
        + S("Где AI, где человек — и эта граница не задаётся раз и навсегда")
        + quote("Главная задача",
                "Провести границу между человеком и AI",
                "И постоянно её перепроектировать по мере роста доверия")
        + L("По мере роста доверия граница смещается")
        + grid([
            R("ph-fill ph-question", "Что доверить машине?"),
            R("ph-fill ph-check-square", "Что контролирует человек?"),
            R("ph-fill ph-gavel", "Где финальное слово руководителя?"),
            R("ph-fill ph-hand-palm", "Где человек не должен мешать?", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + P("Управление изменениями — это постоянное проектирование ответственности")
    )
    return wrap(16, "Управление границей", body)


def s18():  # Если граница не определена
    body = (
        H("Если граница не определена", "не определена")
        + S("Два опасных сценария — и оба разрушают управляемость")
        + two_cards(
            "Сценарий 1 — страх",
            [("ph-fill ph-warning", "Люди боятся пользоваться AI"),
             ("ph-fill ph-question", "Не понимают, за что отвечают"),
             ("ph-fill ph-pause-circle", "Используют формально и осторожно")],
            "Сценарий 2 — хаос",
            [("ph-fill ph-warning", "Решения перекладывают на алгоритм"),
             ("ph-fill ph-x-circle", "Ответственность размывается"),
             ("ph-fill ph-warning-octagon", "Компания теряет управляемость")])
        + L("Любая AI-система должна отвечать")
        + grid([
            R("ph-fill ph-user-check", "Кто решает"),
            R("ph-fill ph-eye", "Кто проверяет"),
            R("ph-fill ph-hand-palm", "Кто вмешивается"),
            R("ph-fill ph-shield-check", "Кто отвечает за последствия", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + P("Без чёткой границы — либо парализованность, либо хаос")
    )
    return wrap(17, "Если граница не определена", body)


def s19():  # ИИ как усилитель управляемости
    body = (
        H("ИИ как усилитель управляемости", "усилитель")
        + S("Больше сигналов, быстрее реакция, шире контекст для решений")
        + grid([
            C("ph-fill ph-broadcast", "Больше сигналов"),
            C("ph-fill ph-lightning", "Быстрее реакция"),
            C("ph-fill ph-warning", "Раньше видны риски"),
            C("ph-fill ph-binoculars", "Шире контекст"),
        ], "grid-cols-2 md:grid-cols-4")
        + '<div class="bg-black border-2 border-solar rounded-2xl p-4 md:p-6 max-w-4xl mx-auto w-full text-white text-center mb-3 md:mb-4"><p class="font-black text-[11px] md:text-base text-solar">Не вручную собирать разрозненную информацию — а видеть, где процесс идёт нормально, где появляется риск, а где нужно вмешательство человека</p></div>'
        + P("Команда удерживает больше процессов одновременно — без перегрева")
    )
    return wrap(18, "ИИ как усилитель", body)


def s20():  # Как меняется решение
    body = (
        H("Как меняется управленческое решение", "решение")
        + S("От опыта и интуиции — к гипотезе, данным, моделированию")
        + numbered([
            "Формулируется гипотеза",
            "Собираются данные",
            "Моделируются варианты",
            "AI готовит рекомендации",
            "AI показывает риски и последствия",
            "Человек принимает финальное решение",
        ], "md:grid-cols-3")
        + P("Руководитель должен понять, на каких данных решение, какие ограничения у AI, какую ответственность берёт компания")
    )
    return wrap(19, "Как меняется решение", body)


def s21():  # Руководитель как модератор
    body = (
        H("Руководитель как модератор интеллекта", "модератор")
        + S("Не единственный источник ответа, а архитектор мышления системы")
        + quote("Сильный руководитель сегодня",
                "Не тот, кто быстрее даёт готовый ответ",
                "А тот, кто строит среду, где лучшие ответы появляются быстрее и качественнее")
        + L("Что он делает")
        + grid([
            R("ph-fill ph-question", "Задаёт правильный вопрос"),
            R("ph-fill ph-list-checks", "Определяет критерии выбора"),
            R("ph-fill ph-flag-banner", "Обозначает границы допустимого"),
            R("ph-fill ph-gavel", "Принимает финальное решение", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + P("AI расширяет поле вариантов — руководитель определяет, какие допустимы")
    )
    return wrap(20, "Руководитель как модератор", body)


def s22():  # ИИ как внешний слой мышления
    body = (
        H("ИИ как внешний слой мышления", "слой мышления")
        + S("Расширяет внимание, память и способность удерживать много процессов")
        + pyramid([
            "Удерживает контекст",
            "Сравнивает варианты",
            "Возвращает к прошлым решениям",
            "Замечает отклонения",
            "Подсвечивает слабые сигналы",
        ])
        + '<div class="bg-black border-2 border-solar rounded-2xl p-3 md:p-4 max-w-4xl mx-auto w-full text-white text-center mb-3"><p class="font-black text-[11px] md:text-base text-solar">Правильный AI снижает шум, а не увеличивает его</p></div>'
        + P("Если стало больше отчётов и уведомлений — это плохой результат внедрения")
    )
    return wrap(21, "ИИ как внешний слой", body)


def s23():  # Руководитель как архитектор внимания
    body = (
        H("Руководитель как архитектор внимания", "архитектор")
        + S("В AI-первой компании руководитель проектирует систему внимания")
        + numbered([
            "Какие сигналы действительно важны",
            "Какие отклонения требуют реакции",
            "Какие решения необратимы",
            "Где AI справляется сам",
            "Где человек обязан вмешаться",
        ])
        + P("Конкурентное преимущество — у компании, у которой быстрее и точнее мышление")
    )
    return wrap(22, "Архитектор внимания", body)


def s24():  # Новый тип труда
    body = (
        H("ИИ внедряет новый тип труда", "новый тип труда")
        + S("Ценность человека смещается от исполнения к проектированию")
        + two_cards(
            "Старая модель",
            [("ph-fill ph-clipboard-text", "Получил задачу"),
             ("ph-fill ph-hammer", "Сделал руками"),
             ("ph-fill ph-paper-plane-right", "Передал результат"),
             ("ph-fill ph-check-square", "Руководитель проверил")],
            "Гибридная модель",
            [("ph-fill ph-target", "Поставить цель"),
             ("ph-fill ph-scroll", "Задать ограничения"),
             ("ph-fill ph-toggle-right", "Выбрать режим автономности AI"),
             ("ph-fill ph-eye", "Проверить результат"),
             ("ph-fill ph-gavel", "Принять решение")])
        + P("Работа теперь — это не только «сделать руками»")
    )
    return wrap(23, "Новый тип труда", body)


def s25():  # Почему эффект не появляется сам
    body = (
        H("Почему эффект не появляется сам", "не появляется сам")
        + S("Технология внедрена, но организационная модель не изменилась")
        + L("Что ломается без перестройки")
        + grid([
            R("ph-fill ph-user-circle-minus", "Сотрудник не понимает, за что отвечает"),
            R("ph-fill ph-question", "Руководитель не знает, как оценивать результат"),
            R("ph-fill ph-bug", "ИТ отвечает за внедрение, но не за бизнес-эффект"),
            R("ph-fill ph-buildings", "Бизнес ждёт результата, не меняя процесс", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + P("Эффект от AI нужно не ждать — его нужно проектировать")
    )
    return wrap(24, "Эффект не появляется сам", body)


def s26():  # Роль ≠ должность
    body = (
        H("Роль — это не должность", "не должность")
        + S("Должность — название в структуре. Роль — логика ответственности")
        + two_cards(
            "Должность",
            [("ph-fill ph-identification-card", "Название в структуре"),
             ("ph-fill ph-buildings", "Привязка к департаменту"),
             ("ph-fill ph-clock", "Часто статична")],
            "Роль",
            [("ph-fill ph-flow-arrow", "Логика ответственности"),
             ("ph-fill ph-user-check", "Кто за что отвечает"),
             ("ph-fill ph-gavel", "Кто принимает решение"),
             ("ph-fill ph-scroll", "По каким правилам действует"),
             ("ph-fill ph-shield-check", "Где финальная ответственность")])
        + P("AI может анализировать и действовать, но ответственность — за человеком")
    )
    return wrap(25, "Роль ≠ должность", body)


def s27():  # Новые роли в компании
    body = (
        H("Новые роли в гибридной компании", "новые роли")
        + S("Старой ролевой модели уже недостаточно")
        + grid([
            R("ph-fill ph-flow-arrow", "Владелец гибридного процесса"),
            R("ph-fill ph-blueprint", "Архитектор автоматизации"),
            R("ph-fill ph-medal-military", "Бизнес-владелец результата"),
            R("ph-fill ph-shield-warning", "Владелец риска"),
            R("ph-fill ph-trophy", "AI-чемпион"),
            R("ph-fill ph-users-three", "Команда", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + P("Появляются зоны ответственности, которых раньше не было явно")
    )
    return wrap(26, "Новые роли", body)


def s28():  # Владелец процесса + архитектор
    body = (
        H("Владелец гибридного процесса и архитектор автоматизации", "и архитектор")
        + S("Две ключевые роли — на разном уровне абстракции")
        + two_cards(
            "Владелец процесса",
            [("ph-fill ph-flow-arrow", "Как реально работает процесс с AI"),
             ("ph-fill ph-question", "Что отдать AI, что оставить человеку"),
             ("ph-fill ph-check-square", "Где нужен контроль"),
             ("ph-fill ph-chart-line-up", "Как измерить эффект")],
            "Архитектор автоматизации",
            [("ph-fill ph-blueprint", "Связка людей, агентов, данных, систем"),
             ("ph-fill ph-toggle-right", "Где AI помогает / автономен"),
             ("ph-fill ph-stop-circle", "Где система обязана остановиться"),
             ("ph-fill ph-plugs-connected", "Интеграции с корпоративными системами")])
        + P("Один смотрит вглубь процесса, другой — на систему целиком")
    )
    return wrap(27, "Владелец процесса + архитектор", body)


def s29():  # Бизнес-владелец + риск + чемпион
    body = (
        H("Бизнес-владелец, владелец риска и ИИ-чемпион", "три роли")
        + S("Три роли, без которых эффект от AI не появится")
        + grid([
            '<div class="bg-white border border-grayBase rounded-2xl p-3 md:p-5 shadow-sm">'
            '<div class="flex items-center gap-2 md:gap-3 mb-1 md:mb-3"><i class="ph-fill ph-medal-military text-solar text-lg md:text-2xl"></i><h3 class="font-black text-[12px] md:text-lg">Бизнес-владелец</h3></div>'
            '<p class="text-[11px] md:text-sm text-black/60">Отвечает не за пилот, а за эффект — быстрее, дешевле, качественнее</p></div>',
            '<div class="bg-white border border-grayBase rounded-2xl p-3 md:p-5 shadow-sm">'
            '<div class="flex items-center gap-2 md:gap-3 mb-1 md:mb-3"><i class="ph-fill ph-shield-warning text-solar text-lg md:text-2xl"></i><h3 class="font-black text-[12px] md:text-lg">Владелец риска</h3></div>'
            '<p class="text-[11px] md:text-sm text-black/60">Юридические, этические, репутационные, операционные последствия</p></div>',
            '<div class="bg-black border-2 border-solar rounded-2xl p-3 md:p-5 shadow-xl text-white">'
            '<div class="flex items-center gap-2 md:gap-3 mb-1 md:mb-3"><i class="ph-fill ph-trophy text-solar text-lg md:text-2xl"></i><h3 class="font-black text-[12px] md:text-lg text-solar">AI-чемпион</h3></div>'
            '<p class="text-[11px] md:text-sm text-white/70">Помогает команде освоить новый способ работы — превращает AI в норму</p></div>',
        ], "grid-cols-1 md:grid-cols-3")
        + P("AI превращается из внешней технологии в норму ежедневной работы")
    )
    return wrap(28, "Бизнес-владелец, риск, чемпион", body)


def s30():  # Матрица компетенций
    body = (
        H("Матрица компетенций", "Матрица")
        + S("Не просто знание инструмента — умение работать вместе с AI")
        + numbered([
            "Правильно поставить задачу",
            "Задать ограничения",
            "Понимать, где AI ошибается",
            "Проверять результат",
            "Интерпретировать рекомендации",
            "Давать обратную связь",
            "Понимать свою ответственность",
        ])
        + P("Матрица — разная для руководителей, владельцев процессов, архитекторов, сотрудников")
    )
    return wrap(29, "Матрица компетенций", body)


def s31():  # Регламент ≠ бюрократия
    body = (
        H("Регламент — это не бюрократия", "не бюрократия")
        + S("Способ сохранить управляемость и безопасность при появлении AI")
        + L("На какие вопросы отвечает регламент")
        + grid([
            R("ph-fill ph-user-check", "Кто может запускать агента"),
            R("ph-fill ph-pencil", "Кто меняет правила его работы"),
            R("ph-fill ph-database", "Какие данные можно использовать"),
            R("ph-fill ph-check-square", "Когда обязана проверка человеком"),
            R("ph-fill ph-warning-octagon", "Что делать при ошибке"),
            R("ph-fill ph-stop-circle", "Кто может остановить систему", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + P("Хороший регламент не тормозит — он делает масштабирование безопасным")
    )
    return wrap(30, "Регламент", body)


def s32():  # ИИ не нейтрален
    body = (
        H("ИИ не нейтрален", "не нейтрален")
        + S("AI всегда отражает человеческие управленческие выборы")
        + grid([
            R("ph-fill ph-database", "Работает на данных, которые кто-то выбрал"),
            R("ph-fill ph-target", "Оптимизирует цели, которые кто-то задал"),
            R("ph-fill ph-chart-bar", "Использует показатели, которые кто-то признал важными"),
            R("ph-fill ph-flag-banner", "Действует в границах, которые кто-то разрешил", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + P("За каждым решением AI стоят решения людей")
    )
    return wrap(31, "ИИ не нейтрален", body)


def s33():  # Ответственность нельзя переложить
    body = (
        H("Ответственность нельзя переложить на алгоритм", "нельзя переложить")
        + S("Если решение повлияло на людей и деньги — отвечают люди")
        + L("У каждого AI-сценария должны быть владельцы")
        + grid([
            R("ph-fill ph-medal-military", "Бизнес-результат"),
            R("ph-fill ph-shield-warning", "Риск"),
            R("ph-fill ph-eye", "Проверка спорных решений"),
            R("ph-fill ph-stop-circle", "Остановка системы"),
            R("ph-fill ph-clipboard-text", "Разбор ошибок", dark=True),
        ], "grid-cols-2 md:grid-cols-5")
        + '<div class="bg-black border-2 border-solar rounded-2xl p-3 md:p-4 max-w-4xl mx-auto w-full text-white text-center mb-3"><p class="font-black text-[11px] md:text-base text-solar">«Это не мы, это алгоритм» — не примет ни клиент, ни регулятор</p></div>'
        + P("AI помогает принимать решения, но не несёт ответственность вместо компании")
    )
    return wrap(32, "Ответственность", body)


def s34():  # Этика — это процесс
    body = (
        H("Этика — это процесс", "процесс")
        + S("Не декларация на сайте, а встроенные в работу механизмы")
        + grid([
            R("ph-fill ph-list-bullets", "Журнал действий агента"),
            R("ph-fill ph-eye", "Проверка человеком в критичных случаях"),
            R("ph-fill ph-stop-circle", "Возможность ручной остановки"),
            R("ph-fill ph-magnifying-glass", "Порядок разбора инцидентов"),
            R("ph-fill ph-arrows-counter-clockwise", "Правила обновления моделей"),
            R("ph-fill ph-user-circle-gear", "Понятные зоны ответственности", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + P("Доверие появляется не от обещаний, а от прозрачности")
    )
    return wrap(33, "Этика — процесс", body)


def s35():  # Показатели гибридной системы
    body = (
        H("Показатели гибридной системы", "Показатели")
        + S("Меряем не объём активности, а эффект для системы")
        + two_cards(
            "Старые показатели",
            [("ph-fill ph-clock", "Сколько часов потрачено"),
             ("ph-fill ph-clipboard-text", "Сколько задач выполнено"),
             ("ph-fill ph-files", "Сколько документов обработано"),
             ("ph-fill ph-cursor-click", "Сколько действий сделал сотрудник")],
            "Новые показатели",
            [("ph-fill ph-lightning", "Скорость решений"),
             ("ph-fill ph-shield-check", "Меньше ошибок и переделок"),
             ("ph-fill ph-chart-line-up", "Стабильность и предсказуемость"),
             ("ph-fill ph-currency-circle-dollar", "Снижение затрат · рост выручки")])
        + P("Не «сколько мы сделали», а «насколько лучше стала работать система»")
    )
    return wrap(34, "Показатели гибридной системы", body)


def s36():  # Метрики не должны конфликтовать
    body = (
        H("Метрики человека и ИИ не должны конфликтовать", "не должны конфликтовать")
        + S("Если AI оптимизирует одно, а человека оценивают по другому — сопротивление неизбежно")
        + two_cards(
            "Конфликт",
            [("ph-fill ph-warning", "AI улучшает качество"),
             ("ph-fill ph-warning", "Человека мерят только скоростью"),
             ("ph-fill ph-x-circle", "AI снижает риск"),
             ("ph-fill ph-x-circle", "Команду мотивируют только на продажи")],
            "Согласованность",
            [("ph-fill ph-check", "Скорость без потери качества"),
             ("ph-fill ph-check", "Рост объёма без ухудшения CX"),
             ("ph-fill ph-check", "Эффект без нарушения этики"),
             ("ph-fill ph-check", "Метрики согласованы на уровне процесса")])
        + P("Иначе люди будут не усиливать систему, а защищаться от неё")
    )
    return wrap(35, "Метрики не должны конфликтовать", body)


def s37():  # Автоматизация ≠ изменение
    body = (
        H("Автоматизация не равна изменению", "не равна изменению")
        + S("Пилот показывает, что технология работает. Это не доказывает, что компания умеет встраивать AI")
        + two_cards(
            "Вопрос автоматизации",
            [("ph-fill ph-question", "Что может сделать AI?"),
             ("ph-fill ph-flask", "Технический пилот"),
             ("ph-fill ph-check-circle", "Технология работает")],
            "Вопрос изменения",
            [("ph-fill ph-question", "Как должна измениться компания?"),
             ("ph-fill ph-users-three", "Роли, правила, обучение, KPI"),
             ("ph-fill ph-shield-check", "Принятие и ответственность"),
             ("ph-fill ph-trend-up", "Устойчивая ценность")])
        + P("Успешный пилот — это не финал, а вход в управленческую трансформацию")
    )
    return wrap(36, "Автоматизация ≠ изменение", body)


def s38():  # ИИ как портфель изменений
    body = (
        H("ИИ как портфель изменений", "портфель")
        + S("Не хаос экспериментов — а связанная со стратегией программа")
        + L("Каждый сценарий отвечает на стратегическую задачу")
        + grid([
            R("ph-fill ph-rocket-launch", "Ускорить выход на рынок"),
            R("ph-fill ph-currency-circle-dollar", "Снизить затраты"),
            R("ph-fill ph-trend-up", "Масштабироваться без роста штата"),
            R("ph-fill ph-smiley", "Улучшить клиентский опыт", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + P("Важен не сам факт эксперимента, а его вклад в стратегию")
    )
    return wrap(37, "Портфель изменений", body)


def s39():  # 7 контрольных вопросов
    body = (
        H("Контрольные вопросы перед запуском ИИ-сценария", "7 вопросов")
        + S("Защищают компанию от экспериментов ради экспериментов")
        + numbered([
            "Какую стратегическую цель он поддерживает?",
            "Какая исходная метрика процесса?",
            "Кто бизнес-владелец результата?",
            "Кто владелец риска?",
            "Где нужна проверка человеком?",
            "Какие данные доступны и можно ли их использовать?",
            "При каких условиях проект будет закрыт?",
        ])
        + P("Если на вопросы нет ответов — это демонстрация, а не AI-сценарий")
    )
    return wrap(38, "7 контрольных вопросов", body)


def s40():  # 6 фаз
    body = (
        H("Шесть фаз портфеля ИИ-изменений", "Шесть фаз")
        + S("Управляемый жизненный цикл — от поиска возможностей до закрытия")
        + numbered([
            "Поиск возможностей",
            "Приоритизация идей",
            "Пилот на реальном процессе",
            "Промышленная сборка",
            "Масштабирование",
            "Закрытие при отсутствии эффекта",
        ], "md:grid-cols-3")
        + '<div class="bg-black border-2 border-solar rounded-2xl p-3 md:p-4 max-w-4xl mx-auto w-full text-white text-center mb-3"><p class="font-black text-[11px] md:text-base text-solar">Закрытие — не провал. Это накопленное знание о том, где AI не работает</p></div>'
        + P("Без жизненного цикла портфель превращается в витрину пилотов")
    )
    return wrap(39, "6 фаз портфеля", body)


def s41():  # Ритм управления
    body = (
        H("Ритм управления изменениями", "Ритм")
        + S("AI-трансформация не управляется разовыми совещаниями")
        + grid([
            '<div class="bg-white border border-grayBase rounded-2xl p-3 md:p-5 shadow-sm"><p class="text-[10px] md:text-xs font-bold uppercase tracking-widest text-solar mb-1 md:mb-2">Каждую неделю</p><p class="font-black text-[12px] md:text-sm text-black/80">Сам процесс — где помогает AI, где исключения, где обходят</p></div>',
            '<div class="bg-white border border-grayBase rounded-2xl p-3 md:p-5 shadow-sm"><p class="text-[10px] md:text-xs font-bold uppercase tracking-widest text-solar mb-1 md:mb-2">Раз в две недели</p><p class="font-black text-[12px] md:text-sm text-black/80">Пилоты — эффект, принятие пользователей, риски</p></div>',
            '<div class="bg-white border border-grayBase rounded-2xl p-3 md:p-5 shadow-sm"><p class="text-[10px] md:text-xs font-bold uppercase tracking-widest text-solar mb-1 md:mb-2">Раз в месяц</p><p class="font-black text-[12px] md:text-sm text-black/80">Портфельный совет — что масштабировать, что закрыть</p></div>',
            '<div class="bg-black border-2 border-solar rounded-2xl p-3 md:p-5 shadow-xl text-white"><p class="text-[10px] md:text-xs font-bold uppercase tracking-widest text-solar mb-1 md:mb-2">Раз в квартал</p><p class="font-black text-[12px] md:text-sm text-solar">Стандарты, академия, регламенты, показатели</p></div>',
        ], "grid-cols-1 md:grid-cols-2")
        + P("Эксперименты быстрые, ошибки дешёвые, масштабирование управляемое")
    )
    return wrap(40, "Ритм управления", body)


def s42():  # Управление неопределённостью
    body = (
        H("ИИ-изменения — это управление неопределённостью", "неопределённостью")
        + S("Через гипотезы, а не веру в технологию")
        + quote("Жизненный цикл гипотезы",
                "Сформулировать → проверить → измерить → решить",
                "Масштабировать, доработать или закрыть — обе ветки нормальные")
        + '<div class="bg-black border-2 border-solar rounded-2xl p-3 md:p-4 max-w-4xl mx-auto w-full text-white text-center mb-3"><p class="font-black text-[11px] md:text-base text-solar">Настоящий провал — тащить проект без результата, без владельца, без принятия</p></div>'
        + P("Часть инициатив не даст эффекта — это нормально для управления неопределённостью")
    )
    return wrap(41, "Управление неопределённостью", body)


def s43():  # Бизнес-владелец изменения
    body = (
        H("Бизнес-владелец изменения", "Бизнес-владелец")
        + S("У каждого AI-изменения должен быть владелец со стороны бизнеса")
        + two_cards(
            "Кто НЕ может быть владельцем",
            [("ph-fill ph-x-circle", "IT"),
             ("ph-fill ph-x-circle", "Подрядчик"),
             ("ph-fill ph-x-circle", "Data-команда")],
            "За что отвечает бизнес-владелец",
            [("ph-fill ph-target", "Смысл и цель изменения"),
             ("ph-fill ph-users-three", "Люди и принятие"),
             ("ph-fill ph-chart-line-up", "Показатели и эффект"),
             ("ph-fill ph-trend-up", "Масштабирование")])
        + P("Без бизнес-владельца AI становится технической демонстрацией")
    )
    return wrap(42, "Бизнес-владелец изменения", body)


def s44():  # Сопротивление — нормальная реакция
    body = (
        H("Сопротивление — нормальная реакция", "нормальная реакция")
        + S("Не ошибка и не признак плохой культуры — реакция живой системы на изменение")
        + L("Сотрудник часто боится потерять")
        + grid([
            C("ph-fill ph-user-circle-gear", "Контроль"),
            C("ph-fill ph-medal", "Статус"),
            C("ph-fill ph-eye", "Понятность"),
            C("ph-fill ph-clipboard-text", "Привычную роль"),
            C("ph-fill ph-question", "Уверенность в будущем", dark=True),
        ], "grid-cols-2 md:grid-cols-5")
        + '<div class="bg-black border-2 border-solar rounded-2xl p-3 md:p-4 max-w-4xl mx-auto w-full text-white text-center mb-3"><p class="font-black text-[11px] md:text-base text-solar">Главный вопрос сотрудника очень простой: «Что изменится лично для меня?»</p></div>'
        + P("Пока человек не получил честный ответ — он формально соглашается, но работает по-старому")
    )
    return wrap(43, "Сопротивление", body)


def s45():  # Что нужно объяснить сотруднику
    body = (
        H("Что нужно объяснить сотруднику", "объяснить")
        + S("Принятие AI начинается не с доступа к инструменту, а с ясности")
        + numbered([
            "Что теперь делает AI?",
            "Что по-прежнему делает человек?",
            "За что отвечает сам сотрудник?",
            "Как меняется его роль?",
            "Как теперь оценивается результат?",
            "Кто отвечает, если AI ошибётся?",
        ], "md:grid-cols-3")
        + P("Без ответов — неопределённость, а за ней сопротивление")
    )
    return wrap(44, "Объяснить сотруднику", body)


def s46():  # Как работать с сопротивлением
    body = (
        H("Как работать с сопротивлением", "работать с сопротивлением")
        + S("Не подавлять приказом — переводить в управляемую форму")
        + numbered([
            "Признать сопротивление — это нормально",
            "Дать ясность по ответственности",
            "Показать личную пользу (меньше рутины · больше времени на сложное)",
            "Создать безопасную среду для практики",
            "Включить руководителей в практику первыми",
        ])
        + P("Если менеджеры сами не используют AI, команда не поверит, что это новая норма")
    )
    return wrap(45, "Работа с сопротивлением", body)


def s47():  # Средний менеджмент
    body = (
        H("Средний менеджмент и новая норма", "Средний менеджмент")
        + S("Ключевой слой AI-трансформации — переводчик стратегии в ежедневную работу")
        + L("Что менеджер объясняет команде")
        + grid([
            R("ph-fill ph-calendar-check", "Что меняется завтра утром"),
            R("ph-fill ph-robot", "Где AI помогает"),
            R("ph-fill ph-eye", "Где человек обязан проверить"),
            R("ph-fill ph-chart-line", "Как теперь оценивается работа"),
            R("ph-fill ph-warning", "Что делать при ошибке"),
            R("ph-fill ph-rocket", "Как использовать AI в реальных задачах", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + P("Если менеджер сам понимает AI и видит пользу — команда принимает изменение")
    )
    return wrap(46, "Средний менеджмент", body)


def s48():  # ИИ нельзя спустить сверху
    body = (
        H("ИИ нельзя спустить сверху", "нельзя спустить сверху")
        + S("Доступ, вебинар и письмо от руководства сами по себе не меняют поведение")
        + two_cards(
            "Что не работает",
            [("ph-fill ph-x-circle", "Доступ к инструменту"),
             ("ph-fill ph-x-circle", "Вебинар на час"),
             ("ph-fill ph-x-circle", "Письмо от руководства"),
             ("ph-fill ph-x-circle", "Лозунги «теперь все используют AI»")],
            "Что работает",
            [("ph-fill ph-check", "Пример руководителей"),
             ("ph-fill ph-check", "Реальная польза в работе"),
             ("ph-fill ph-check", "Практические кейсы"),
             ("ph-fill ph-check", "Видимый результат — быстрее, качественнее")])
        + P("Когда люди видят, что AI действительно помогает — сопротивление превращается в интерес")
    )
    return wrap(47, "Нельзя спустить сверху", body)


def s49():  # Метрики принятия
    body = (
        H("Метрики принятия и правильный KPI", "правильный KPI")
        + S("AI внедрён — не когда дали доступ, а когда изменилось поведение и результат")
        + two_cards(
            "Имитация активности",
            [("ph-fill ph-warning", "KPI = «использовал AI»"),
             ("ph-fill ph-clipboard-text", "Много запросов, мало смысла"),
             ("ph-fill ph-x-circle", "Результат работы не меняется"),
             ("ph-fill ph-eye-slash", "Возврат к старым способам")],
            "Глубина принятия",
            [("ph-fill ph-target", "С помощью AI улучшил процесс"),
             ("ph-fill ph-trend-up", "Доля принятых рекомендаций"),
             ("ph-fill ph-check-circle", "Качество и скорость реальных решений"),
             ("ph-fill ph-arrow-clockwise", "Не возвращается к старому")])
        + P("Правильный KPI — не «использовал AI», а «с помощью AI улучшил процесс»")
    )
    return wrap(48, "Правильный KPI", body)


def s50():  # AI-First обучающая система
    body = (
        H("Обучающая система AI-First компании", "AI-First")
        + S("Компания, которая быстрее работает, быстрее учится и лучше управляет сложностью")
        + grid([
            C("ph-fill ph-graduation-cap", "Академия"),
            C("ph-fill ph-chat-circle-text", "Обратная связь"),
            C("ph-fill ph-presentation", "Вебинары"),
            C("ph-fill ph-lightning", "Хакатоны"),
            C("ph-fill ph-scroll", "Регламенты"),
            C("ph-fill ph-brain", "Орг. память"),
            C("ph-fill ph-books", "Библиотека решений"),
            C("ph-fill ph-trophy", "Новая ценность", dark=True),
        ], "grid-cols-2 md:grid-cols-4")
        + '<div class="bg-black border-2 border-solar rounded-2xl p-4 md:p-6 max-w-4xl mx-auto w-full text-white text-center mb-3"><p class="font-black text-[12px] md:text-lg text-solar">AI не обесценивает человека. Он забирает операционную суету</p></div>'
        + P("Ценность человека смещается к суждению, смыслу, границам и ответственности")
    )
    return wrap(49, "AI-First компания", body)


def s51_test():  # Финальный — кнопка теста
    body = (
        '<div class="relative z-10 w-full text-center">'
        '<div class="bg-solar/10 border border-solar/40 rounded-full px-4 py-1.5 md:py-2 mx-auto shadow-sm mb-4 md:mb-8 inline-block">'
        '<p class="text-solar font-bold uppercase tracking-widest text-[8px] md:text-sm m-0">Итог лекции</p></div>'
        '<h2 class="text-xl sm:text-3xl md:text-4xl lg:text-[50px] font-black mb-4 md:mb-6 tracking-tight leading-tight">'
        'Человеческая → Гибридная →<br><span class="text-solar font-black">AI-First компания</span></h2>'
        '<p class="text-white/70 font-medium text-[11px] md:text-base mb-6 md:mb-10 max-w-3xl mx-auto">AI меняет не процессы — он меняет саму компанию. Гибридная система — это спроектированное взаимодействие человека и машины.</p>'
        '<p class="text-[10px] md:text-sm font-bold uppercase tracking-widest text-white/50 mb-3 md:mb-5">Зрелая AI-first компания должна быть</p>'
        '<div class="grid grid-cols-2 md:grid-cols-4 gap-1.5 md:gap-2 mb-6 md:mb-10 w-full max-w-5xl mx-auto">'
        + ''.join(f'<div class="bg-white/10 p-2 md:p-2.5 rounded-xl text-center text-[10px] md:text-sm font-bold border border-white/20">{e(t)}</div>'
                  for t in ["Гибридной", "Управляемой", "С чёткими границами", "С пересобранными ролями",
                            "С согласованными метриками", "С регулярным ритмом", "Обучающейся"])
        + '<div class="bg-solar text-black p-2 md:p-2.5 rounded-xl text-center text-[10px] md:text-sm font-black uppercase tracking-widest shadow-[0_0_15px_#35F0C7]">Этичной</div></div>'
        '<p class="text-[10px] md:text-sm font-bold uppercase tracking-widest text-white/50 mb-3">Проверьте понимание</p>'
        '<button id="open-quiz-btn" type="button" class="mt-2 md:mt-4 inline-flex items-center justify-center gap-2 md:gap-3 bg-solar text-black font-black text-sm md:text-xl px-6 md:px-10 py-3 md:py-5 rounded-full shadow-[0_0_30px_rgba(53,240,199,0.4)] hover:scale-105 transition-transform uppercase tracking-widest">'
        '<i class="ph-fill ph-graduation-cap text-lg md:text-2xl"></i>Пройти тест из 10 вопросов</button></div>'
    )
    return wrap(50, "Финальный — кнопка теста", body, dark=True)


# ----------------------------- footer ----------------------------------------
QUIZ_QUESTIONS = [
    {
        "q": "В чём главная идея лекции про AI-трансформацию компании?",
        "options": [
            "AI — это новый софт, который ускоряет существующие процессы",
            "AI меняет компанию организационно: роли, ответственность, метрики",
            "AI заменяет всех сотрудников",
            "AI — только инструмент для отдельных задач"
        ],
        "correct": 1,
        "explanation": "AI меняет компанию не только технически, но и организационно — пересобираются роли, процессы, правила, обучение и показатели. Это не IT-проект, а управленческая трансформация."
    },
    {
        "q": "Что такое гибридная организация?",
        "options": [
            "Компания, в которой все процессы автоматизированы",
            "Компания, где AI заменил большинство сотрудников",
            "Компания, где человек и AI участвуют в одном процессе, но выполняют разные функции",
            "Компания, в которой AI применяется только в IT"
        ],
        "correct": 2,
        "explanation": "Гибридная система — это компания, где человек задаёт цели, правила, отвечает за последствия, а AI анализирует данные, ищет закономерности и выполняет операции. Это не замена человека, а правильное распределение работы."
    },
    {
        "q": "В каких четырёх зонах человек обязан оставаться главным?",
        "options": [
            "Постановка целей, рискованные решения, этика, ответственность",
            "Программирование, дизайн, маркетинг, продажи",
            "Анализ данных, мониторинг, рутина, отчётность",
            "Работа с клиентами, HR, бухгалтерия, юр. отдел"
        ],
        "correct": 0,
        "explanation": "AI не должен решать, ради чего существует бизнес. Не должен принимать рискованные решения с серьёзными последствиями. Не должен подменять этический выбор. И не может нести ответственность вместо людей."
    },
    {
        "q": "Какие четыре режима самостоятельности AI существуют?",
        "options": [
            "Тестовый, продакшен, демо, отладочный",
            "Локальный, облачный, гибридный, кросс-доменный",
            "Только автоматический и только ручной",
            "AI предлагает / AI действует под контролем / AI действует сам / соавторство"
        ],
        "correct": 3,
        "explanation": "Зрелая компания не использует один универсальный режим. Для рискованных задач — AI только предлагает. Для повторяемых — действует под контролем. В понятных сценариях с низкими рисками — самостоятельно. Для документов и стратегий — соавторство с человеком."
    },
    {
        "q": "Что значит «управление изменениями = управление границей»?",
        "options": [
            "Нужно поставить firewall между AI и пользователями",
            "Нужно ограничить доступ к AI только топ-менеджменту",
            "Нужно постоянно перепроектировать, что доверять AI, а что контролирует человек",
            "Нужно отделить AI-команду от остального бизнеса"
        ],
        "correct": 2,
        "explanation": "Главная задача — не «что автоматизировать», а провести границу между человеком и AI. И эта граница не задаётся раз и навсегда — по мере роста доверия она меняется. Управление изменениями — это постоянное проектирование ответственности."
    },
    {
        "q": "Какие новые роли появляются в гибридной компании?",
        "options": [
            "Только AI-разработчик и data scientist",
            "Владелец процесса, архитектор автоматизации, бизнес-владелец результата, владелец риска, AI-чемпион",
            "Только IT-директор и CIO",
            "Только продакт-менеджер и UX-дизайнер"
        ],
        "correct": 1,
        "explanation": "Старой ролевой модели уже недостаточно. Появляются зоны ответственности, которых раньше не было: кто реально владеет гибридным процессом, кто проектирует автоматизацию, кто отвечает за эффект, за риски, и кто помогает команде принять новый способ работы."
    },
    {
        "q": "Почему «эффект от AI не появляется сам»?",
        "options": [
            "Потому что модели всегда плохо обучены",
            "Потому что компания внедряет технологию, но не меняет роли, метрики и процессы",
            "Потому что не хватает GPU",
            "Потому что AI слишком дорогой"
        ],
        "correct": 1,
        "explanation": "Инструмент появился, агент запущен, пилот проведён — но если роли, KPI и процессы остались прежними, сотрудники не понимают, за что отвечают они, а за что AI. Эффект от AI нужно не ждать, а проектировать."
    },
    {
        "q": "Какие показатели правильны для гибридной системы?",
        "options": [
            "Только количество запросов к AI",
            "Только количество выполненных задач",
            "Эффект: скорость решений, меньше ошибок, стабильность, экономика",
            "Только время работы сотрудника"
        ],
        "correct": 2,
        "explanation": "Старые метрики измеряли усилия — сколько часов и задач. В гибридной системе важнее не «сколько мы сделали», а «насколько лучше стала работать система»: скорость, ошибки, стабильность, выручка."
    },
    {
        "q": "Что главное в работе с сопротивлением сотрудников?",
        "options": [
            "Подавить приказом «теперь все используют AI»",
            "Признать сопротивление, дать ясность по ответственности, показать личную пользу, дать практику, включить руководителей",
            "Уволить тех, кто сопротивляется",
            "Игнорировать — само пройдёт"
        ],
        "correct": 1,
        "explanation": "Сопротивление — нормальная реакция живой системы. Главный вопрос сотрудника: «что изменится для меня?». Без честного ответа на него — формальное согласие, но работа по-старому."
    },
    {
        "q": "В чём правильный KPI использования AI?",
        "options": [
            "Количество запросов к AI в день",
            "Количество сотрудников с доступом",
            "Размер бюджета на AI",
            "«С помощью AI улучшил процесс» — глубина принятия, влияние на результат"
        ],
        "correct": 3,
        "explanation": "Если поощрять количество запросов, компания получит имитацию активности. Правильный KPI — не «использовал AI», а «с помощью AI улучшил процесс»: меняется ли поведение, принимаются ли рекомендации, влияет ли AI на реальные решения."
    },
]


def build_footer() -> str:
    quiz_json = json.dumps(QUIZ_QUESTIONS, ensure_ascii=False, indent=8)
    quiz_json = quiz_json.replace("\n", "\n        ")
    return f"""
<!-- =================== SLIDES END =================== -->

    <!-- Модальное окно теста -->
    <div id="quiz-modal" class="fixed inset-0 z-[10001] bg-black text-white hidden flex-col overflow-y-auto">
        <div class="w-full max-w-3xl mx-auto px-4 sm:px-6 md:px-10 py-8 md:py-14 flex flex-col min-h-full">
            <div class="flex items-center justify-between mb-6 md:mb-10 shrink-0">
                <div class="flex items-center gap-2 md:gap-3">
                    <div class="w-9 h-9 md:w-12 md:h-12 bg-solar rounded-full flex items-center justify-center shadow-md"><i class="ph-fill ph-graduation-cap text-lg md:text-2xl text-black"></i></div>
                    <div>
                        <p class="text-[10px] md:text-xs font-bold uppercase tracking-widest text-white/50">Финальный тест</p>
                        <p id="quiz-progress" class="text-sm md:text-lg font-black text-white">Вопрос 1 из 10</p>
                    </div>
                </div>
                <button id="quiz-close-btn" type="button" class="w-9 h-9 md:w-11 md:h-11 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-colors text-white"><i class="ph-bold ph-x text-lg md:text-2xl"></i></button>
            </div>

            <div class="w-full h-1 md:h-1.5 bg-white/10 rounded-full overflow-hidden mb-6 md:mb-10">
                <div id="quiz-progress-bar" class="h-full bg-solar rounded-full transition-all duration-300" style="width: 10%;"></div>
            </div>

            <div id="quiz-question-block" class="flex-1 flex flex-col">
                <h2 id="quiz-question-text" class="text-base sm:text-xl md:text-3xl font-black leading-tight mb-6 md:mb-10"></h2>
                <div id="quiz-options" class="flex flex-col gap-2 md:gap-3 mb-6 md:mb-8"></div>
                <div id="quiz-explanation" class="hidden bg-white/5 border border-white/10 rounded-[20px] md:rounded-3xl p-4 md:p-6 mb-6 md:mb-8">
                    <div class="flex items-center gap-2 md:gap-3 mb-2 md:mb-3">
                        <i id="quiz-explanation-icon" class="text-xl md:text-2xl"></i>
                        <h3 id="quiz-explanation-title" class="font-black text-sm md:text-lg"></h3>
                    </div>
                    <p id="quiz-explanation-text" class="text-[11px] md:text-base text-white/80 leading-snug md:leading-relaxed"></p>
                </div>
                <button id="quiz-next-btn" type="button" class="hidden bg-solar text-black font-black text-sm md:text-lg px-6 md:px-10 py-3 md:py-4 rounded-full shadow-lg hover:scale-[1.02] transition-transform uppercase tracking-widest self-start">
                    Далее <i class="ph-bold ph-arrow-right ml-1"></i>
                </button>
            </div>

            <div id="quiz-result-block" class="hidden flex-1 flex-col items-center justify-center text-center py-8">
                <div id="quiz-result-icon-wrap" class="w-20 h-20 md:w-28 md:h-28 rounded-full flex items-center justify-center mb-5 md:mb-8 shadow-2xl">
                    <i id="quiz-result-icon" class="text-4xl md:text-6xl"></i>
                </div>
                <p class="text-[10px] md:text-sm font-bold uppercase tracking-widest text-white/50 mb-2 md:mb-3">Ваш результат</p>
                <div class="mb-3 md:mb-5">
                    <span id="quiz-result-score" class="text-5xl md:text-7xl font-black text-solar"></span>
                    <span class="text-xl md:text-3xl font-black text-white/40"> / 10</span>
                </div>
                <h3 id="quiz-result-title" class="text-lg md:text-3xl font-black mb-2 md:mb-4"></h3>
                <p id="quiz-result-desc" class="text-xs md:text-base text-white/70 max-w-xl mx-auto mb-8 md:mb-10"></p>
                <div class="flex flex-col sm:flex-row gap-3 md:gap-4">
                    <button id="quiz-restart-btn" type="button" class="bg-solar text-black font-black text-sm md:text-base px-6 md:px-8 py-3 md:py-4 rounded-full shadow-lg hover:scale-[1.02] transition-transform uppercase tracking-widest">
                        <i class="ph-bold ph-arrow-clockwise mr-1"></i> Пройти ещё раз
                    </button>
                    <button id="quiz-finish-btn" type="button" class="bg-white/10 hover:bg-white/20 text-white font-bold text-sm md:text-base px-6 md:px-8 py-3 md:py-4 rounded-full transition-colors uppercase tracking-widest">
                        Закрыть
                    </button>
                </div>
            </div>
        </div>
    </div>

<script>
    document.addEventListener('DOMContentLoaded', () => {{
        const totalSlides = 51;
        let currentSlide = 0;
        const progressBar = document.getElementById('progress-bar');
        const body = document.body;
        const params = new URLSearchParams(window.location.search);
        const exportMode = params.has('pdf') || params.get('mode') === 'pdf' || window.location.hash === '#pdf';

        const video = document.getElementById('bubble-video');
        const videoOverlay = document.getElementById('video-overlay');
        const videoIcon = document.getElementById('video-icon');
        const videoLoader = document.getElementById('video-loader');

        let loadedIdx = -1;
        let overlayTimeout;

        // Final slide (50) has no video — it's the test launcher.
        function videoSrcFor(slideIdx) {{
            if (slideIdx >= 50) return null;
            return `videos/${{slideIdx + 1}}.mp4`;
        }}

        function triggerOverlayAutoFade() {{
            if (!videoOverlay || !video) return;
            videoOverlay.classList.remove('opacity-0');
            clearTimeout(overlayTimeout);
            if (!video.paused) overlayTimeout = setTimeout(() => videoOverlay.classList.add('opacity-0'), 1500);
        }}

        function setupVideoEvents() {{
            video.addEventListener('ended', () => {{ if (currentSlide < totalSlides - 1) nextSlide(); }});
            video.addEventListener('play', () => {{
                if (videoIcon) videoIcon.className = 'ph-fill ph-pause-circle text-4xl md:text-6xl drop-shadow-md';
                if (videoOverlay) videoOverlay.classList.add('opacity-0');
                clearTimeout(overlayTimeout);
                if (videoLoader) videoLoader.classList.add('opacity-0');
            }});
            video.addEventListener('playing', () => {{ if (videoLoader) videoLoader.classList.add('opacity-0'); }});
            video.addEventListener('waiting', () => {{ if (videoLoader) videoLoader.classList.remove('opacity-0'); }});
            video.addEventListener('pause', () => {{
                if (videoIcon) videoIcon.className = 'ph-fill ph-play-circle text-4xl md:text-6xl drop-shadow-md';
                if (videoOverlay) videoOverlay.classList.remove('opacity-0');
                clearTimeout(overlayTimeout);
            }});
            video.addEventListener('error', () => {{
                if (videoLoader) videoLoader.classList.add('opacity-0');
                showPlayPrompt();
            }});
        }}

        function updateProgress() {{
            if (!progressBar) return;
            progressBar.style.width = `${{((currentSlide + 1) / totalSlides) * 100}}%`;
        }}
        function showLoaderInstant() {{
            if (!videoLoader) return;
            videoLoader.style.transition = 'none';
            videoLoader.classList.remove('opacity-0');
            void videoLoader.offsetWidth;
            videoLoader.style.transition = '';
        }}
        function hideLoader() {{ if (videoLoader) videoLoader.classList.add('opacity-0'); }}
        function showPlayPrompt() {{
            if (videoOverlay) videoOverlay.classList.remove('opacity-0');
            if (videoIcon) videoIcon.className = 'ph-fill ph-play-circle text-4xl md:text-6xl drop-shadow-md';
        }}

        function switchVideo(slideIdx) {{
            if (!video) return;
            const targetSrc = videoSrcFor(slideIdx);
            // Final slide: hide bubble.
            const bubble = document.getElementById('video-bubble');
            if (targetSrc === null) {{
                if (bubble) bubble.style.display = 'none';
                try {{ video.pause(); }} catch (e) {{}}
                loadedIdx = slideIdx;
                return;
            }} else {{
                if (bubble && bubble.style.display === 'none') bubble.style.display = 'block';
            }}
            if (slideIdx === loadedIdx) return;
            showLoaderInstant();
            if (videoOverlay) videoOverlay.classList.add('opacity-0');
            video.src = targetSrc;
            loadedIdx = slideIdx;
            const playPromise = video.play();
            if (playPromise && playPromise.catch) {{
                playPromise.then(() => {{ hideLoader(); triggerOverlayAutoFade(); }})
                           .catch((err) => {{ console.warn('Video play failed:', err); hideLoader(); showPlayPrompt(); }});
            }}
        }}

        window.updateSlides = function() {{
            for (let i = 0; i < totalSlides; i++) {{
                const slide = document.getElementById(`slide-${{i}}`);
                if (!slide) continue;
                if (i === currentSlide) {{
                    slide.classList.remove('opacity-0', 'pointer-events-none', 'translate-y-8', '-translate-y-8');
                    slide.classList.add('opacity-100', 'translate-y-0');
                }} else if (i < currentSlide) {{
                    slide.classList.remove('opacity-100', 'translate-y-0', 'translate-y-8');
                    slide.classList.add('opacity-0', 'pointer-events-none', '-translate-y-8');
                }} else {{
                    slide.classList.remove('opacity-100', 'translate-y-0', '-translate-y-8');
                    slide.classList.add('opacity-0', 'pointer-events-none', 'translate-y-8');
                }}
            }}
            updateProgress();
            const navPrev = document.getElementById('nav-prev');
            const navNext = document.getElementById('nav-next');
            if (navPrev) navPrev.style.display = currentSlide === 0 ? 'none' : 'flex';
            if (navNext) navNext.style.display = currentSlide === totalSlides - 1 ? 'none' : 'flex';
            if (!exportMode) switchVideo(currentSlide);
        }};
        window.nextSlide = function() {{ if (currentSlide < totalSlides - 1) {{ currentSlide++; updateSlides(); }} }};
        window.prevSlide = function() {{ if (currentSlide > 0) {{ currentSlide--; updateSlides(); }} }};

        document.getElementById('start-overlay').addEventListener('click', function() {{
            this.style.opacity = '0';
            setTimeout(() => this.style.display = 'none', 500);
            if (!exportMode) {{
                document.getElementById('video-bubble').style.display = 'block';
                setupVideoEvents();
                video.muted = false;
                switchVideo(0);
            }}
        }});

        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
            else if (e.key === 'ArrowLeft') prevSlide();
        }});

        if (videoOverlay) {{
            videoOverlay.addEventListener('click', (e) => {{
                e.stopPropagation();
                if (video.paused) video.play().catch(() => showPlayPrompt());
                else video.pause();
            }});
        }}

        // Drag bubble
        const bubble = document.getElementById('video-bubble');
        let isDragging = false, currentX = 0, currentY = 0, initialX = 0, initialY = 0, xOffset = 0, yOffset = 0;
        bubble.addEventListener("mousedown", dragStart);
        document.addEventListener("mouseup", () => isDragging = false);
        document.addEventListener("mousemove", drag);
        bubble.addEventListener("touchstart", dragStart, {{passive: false}});
        document.addEventListener("touchend", () => isDragging = false);
        document.addEventListener("touchmove", drag, {{passive: false}});
        function dragStart(e) {{
            initialX = (e.type === "touchstart" ? e.touches[0].clientX : e.clientX) - xOffset;
            initialY = (e.type === "touchstart" ? e.touches[0].clientY : e.clientY) - yOffset;
            if (e.target === bubble || bubble.contains(e.target)) isDragging = true;
        }}
        function drag(e) {{
            if (!isDragging) return;
            e.preventDefault();
            currentX = (e.type === "touchmove" ? e.touches[0].clientX : e.clientX) - initialX;
            currentY = (e.type === "touchmove" ? e.touches[0].clientY : e.clientY) - initialY;
            xOffset = currentX; yOffset = currentY;
            bubble.style.transform = `translate3d(${{currentX}}px, ${{currentY}}px, 0)`;
        }}

        // Swipe nav
        let swipeStartX = 0, swipeStartY = 0, swipeActive = false;
        document.addEventListener('touchstart', (e) => {{
            if (bubble.contains(e.target)) {{ swipeActive = false; return; }}
            const navPrev = document.getElementById('nav-prev');
            const navNext = document.getElementById('nav-next');
            if ((navPrev && navPrev.contains(e.target)) || (navNext && navNext.contains(e.target))) {{ swipeActive = false; return; }}
            const quizModalEl = document.getElementById('quiz-modal');
            if (quizModalEl && !quizModalEl.classList.contains('hidden')) {{ swipeActive = false; return; }}
            swipeStartX = e.touches[0].clientX;
            swipeStartY = e.touches[0].clientY;
            swipeActive = true;
        }}, {{passive: true}});
        document.addEventListener('touchend', (e) => {{
            if (!swipeActive) return;
            swipeActive = false;
            const dx = e.changedTouches[0].clientX - swipeStartX;
            const dy = e.changedTouches[0].clientY - swipeStartY;
            if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.4) {{
                if (dx > 0) prevSlide(); else nextSlide();
            }}
        }}, {{passive: true}});

        if (exportMode) body.classList.add('pdf-export-mode');
        else updateSlides();

        // ==================== QUIZ ====================
        const quizQuestions = {quiz_json};

        let quizIndex = 0, quizScore = 0, quizAnswered = false;
        const quizModal = document.getElementById('quiz-modal');
        const quizQuestionText = document.getElementById('quiz-question-text');
        const quizOptions = document.getElementById('quiz-options');
        const quizExplanation = document.getElementById('quiz-explanation');
        const quizExplanationIcon = document.getElementById('quiz-explanation-icon');
        const quizExplanationTitle = document.getElementById('quiz-explanation-title');
        const quizExplanationText = document.getElementById('quiz-explanation-text');
        const quizNextBtn = document.getElementById('quiz-next-btn');
        const quizProgress = document.getElementById('quiz-progress');
        const quizProgressBar = document.getElementById('quiz-progress-bar');
        const quizQuestionBlock = document.getElementById('quiz-question-block');
        const quizResultBlock = document.getElementById('quiz-result-block');

        function openQuiz() {{
            quizIndex = 0; quizScore = 0; quizAnswered = false;
            quizModal.classList.remove('hidden');
            quizModal.classList.add('flex');
            quizQuestionBlock.classList.remove('hidden');
            quizQuestionBlock.classList.add('flex');
            quizResultBlock.classList.add('hidden');
            quizResultBlock.classList.remove('flex');
            renderQuestion();
            if (video && !video.paused) video.pause();
        }}
        function closeQuiz() {{ quizModal.classList.add('hidden'); quizModal.classList.remove('flex'); }}

        function renderQuestion() {{
            quizAnswered = false;
            const cur = quizQuestions[quizIndex];
            quizProgress.textContent = `Вопрос ${{quizIndex + 1}} из ${{quizQuestions.length}}`;
            quizProgressBar.style.width = `${{((quizIndex + 1) / quizQuestions.length) * 100}}%`;
            quizQuestionText.textContent = cur.q;
            quizOptions.innerHTML = '';
            cur.options.forEach((opt, i) => {{
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'quiz-option text-left bg-white/5 hover:bg-white/10 border border-white/10 rounded-[16px] md:rounded-2xl p-3 md:p-5 flex items-start gap-3 md:gap-4 transition-all text-white';
                btn.innerHTML = `
                    <span class="quiz-option-letter shrink-0 w-7 h-7 md:w-9 md:h-9 rounded-full border border-white/20 flex items-center justify-center text-[11px] md:text-sm font-black">${{String.fromCharCode(65 + i)}}</span>
                    <span class="quiz-option-text text-[12px] md:text-base font-medium leading-snug pt-0.5 md:pt-1">${{opt}}</span>
                `;
                btn.addEventListener('click', () => handleAnswer(i, btn));
                quizOptions.appendChild(btn);
            }});
            quizExplanation.classList.add('hidden');
            quizNextBtn.classList.add('hidden');
        }}

        function handleAnswer(chosenIdx, btnEl) {{
            if (quizAnswered) return;
            quizAnswered = true;
            const cur = quizQuestions[quizIndex];
            const buttons = quizOptions.querySelectorAll('.quiz-option');
            buttons.forEach((b, i) => {{
                b.disabled = true;
                b.classList.remove('hover:bg-white/10');
                if (i === cur.correct) {{
                    b.classList.remove('bg-white/5', 'border-white/10');
                    b.classList.add('bg-solar/20', 'border-solar');
                    const letter = b.querySelector('.quiz-option-letter');
                    letter.classList.remove('border-white/20');
                    letter.classList.add('bg-solar', 'text-black', 'border-solar');
                }} else if (i === chosenIdx) {{
                    b.classList.remove('bg-white/5', 'border-white/10');
                    b.classList.add('bg-red-500/15', 'border-red-500/60');
                    const letter = b.querySelector('.quiz-option-letter');
                    letter.classList.remove('border-white/20');
                    letter.classList.add('bg-red-500/80', 'text-white', 'border-red-500');
                }}
            }});
            const isCorrect = chosenIdx === cur.correct;
            if (isCorrect) quizScore++;
            quizExplanation.classList.remove('hidden');
            if (isCorrect) {{
                quizExplanationIcon.className = 'ph-fill ph-check-circle text-xl md:text-2xl text-solar';
                quizExplanationTitle.textContent = 'Верно!';
                quizExplanationTitle.className = 'font-black text-sm md:text-lg text-solar';
            }} else {{
                quizExplanationIcon.className = 'ph-fill ph-x-circle text-xl md:text-2xl text-red-400';
                quizExplanationTitle.textContent = 'Неверно — вот как правильно';
                quizExplanationTitle.className = 'font-black text-sm md:text-lg text-red-400';
            }}
            quizExplanationText.textContent = cur.explanation;
            quizNextBtn.classList.remove('hidden');
            if (quizIndex === quizQuestions.length - 1) {{
                quizNextBtn.innerHTML = 'Посмотреть результат <i class="ph-bold ph-arrow-right ml-1"></i>';
            }} else {{
                quizNextBtn.innerHTML = 'Далее <i class="ph-bold ph-arrow-right ml-1"></i>';
            }}
        }}

        function nextQuestion() {{
            if (!quizAnswered) return;
            if (quizIndex < quizQuestions.length - 1) {{ quizIndex++; renderQuestion(); }}
            else {{ showResults(); }}
        }}

        function showResults() {{
            quizQuestionBlock.classList.add('hidden');
            quizQuestionBlock.classList.remove('flex');
            quizResultBlock.classList.remove('hidden');
            quizResultBlock.classList.add('flex');
            const score = quizScore;
            document.getElementById('quiz-result-score').textContent = score;
            const resultIconWrap = document.getElementById('quiz-result-icon-wrap');
            const resultIcon = document.getElementById('quiz-result-icon');
            const resultTitle = document.getElementById('quiz-result-title');
            const resultDesc = document.getElementById('quiz-result-desc');
            let title, desc, iconClass, wrapClass;
            if (score >= 9) {{
                title = 'Превосходно!';
                desc = 'Вы отлично понимаете, как устроена AI-трансформация компании: гибридная система, новые роли, границы автономности, согласованные метрики, работа с сопротивлением.';
                iconClass = 'ph-fill ph-trophy text-black';
                wrapClass = 'bg-solar';
            }} else if (score >= 7) {{
                title = 'Отличный результат';
                desc = 'Вы уверенно владеете ключевыми принципами AI-первой компании. Пересмотрите блоки про режимы автономности, метрики принятия и работу с сопротивлением.';
                iconClass = 'ph-fill ph-medal text-solar';
                wrapClass = 'bg-solar/20 border-2 border-solar';
            }} else if (score >= 5) {{
                title = 'Неплохо, но есть над чем поработать';
                desc = 'Базу вы уловили, но стоит освежить разницу между автоматизацией и изменением, новые роли, контрольные вопросы перед запуском AI-сценария и метрики гибридной системы.';
                iconClass = 'ph-fill ph-chart-line-up text-solar';
                wrapClass = 'bg-white/10 border-2 border-solar/50';
            }} else {{
                title = 'Стоит вернуться к материалу';
                desc = 'AI-трансформация — это не IT-проект, а пересборка ролей, процессов и ответственности. Пересмотрите ключевые слайды и попробуйте ещё раз.';
                iconClass = 'ph-fill ph-book-open text-solar';
                wrapClass = 'bg-white/10 border-2 border-white/20';
            }}
            resultIconWrap.className = 'w-20 h-20 md:w-28 md:h-28 rounded-full flex items-center justify-center mb-5 md:mb-8 shadow-2xl ' + wrapClass;
            resultIcon.className = iconClass + ' text-4xl md:text-6xl';
            resultTitle.textContent = title;
            resultDesc.textContent = desc;
        }}

        document.getElementById('open-quiz-btn').addEventListener('click', openQuiz);
        document.getElementById('quiz-close-btn').addEventListener('click', closeQuiz);
        document.getElementById('quiz-finish-btn').addEventListener('click', closeQuiz);
        document.getElementById('quiz-restart-btn').addEventListener('click', openQuiz);
        quizNextBtn.addEventListener('click', nextQuestion);
    }});
</script>
</body>
</html>
"""


def main() -> int:
    slide_fns = [
        s1, s2, s3, s4, s5, s6, s7, s8, s9, s10,
        s11, s12, s13, s14, s15, s16, s17, s18, s19, s20,
        s21, s22, s23, s24, s25, s26, s27, s28, s29, s30,
        s31, s32, s33, s34, s35, s36, s37, s38, s39, s40,
        s41, s42, s43, s44, s45, s46, s47, s48, s49, s50,
        s51_test,
    ]
    parts = [HEAD]
    for fn in slide_fns:
        parts.append(fn())
    parts.append(build_footer())
    OUT_PATH.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {OUT_PATH} with {len(slide_fns)} slides")
    return 0


HEAD = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Лекция 7: Люди, машины и новая логика управления</title>
    <meta name="description" content="Лекция 7: AI-агенты меняют компанию организационно. Гибридная система, новые роли, метрики, governance.">
    <meta name="theme-color" content="#35F0C7">
    <meta property="og:type" content="website">
    <meta property="og:title" content="Лекция 7: Люди, машины и новая логика управления">
    <meta property="og:description" content="Как компания становится гибридной системой">
    <meta property="og:locale" content="ru_RU">
    <meta property="og:site_name" content="Anthropolis">

    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/@phosphor-icons/web"></script>

    <script>
        tailwind.config = { theme: { extend: {
            fontFamily: { sans: ['Montserrat', 'sans-serif'] },
            colors: { solar: '#35F0C7', grayBase: '#E9E9E9', black: '#000000', white: '#FFFFFF' }
        }}}
    </script>

<style>
    html { background: #ffffff !important; -webkit-tap-highlight-color: transparent; }
    body { user-select: none; overflow: hidden; background-color: #ffffff !important;
        margin: 0; width: 100vw; height: 100dvh; color: #000000; }
    .slide-container {
        transition: opacity 0.5s ease-in-out, transform 0.5s ease-in-out;
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        display: flex; flex-direction: column; justify-content: center;
        overflow-y: auto; overflow-x: hidden; background: #ffffff;
        -ms-overflow-style: none; scrollbar-width: none;
    }
    .slide-container::-webkit-scrollbar { display: none; }
    .content-z {
        position: relative; z-index: 10; margin: auto; width: 100%;
        padding: 0.5rem 0.75rem 115px 0.75rem;
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; min-height: 100%;
    }
    @media (min-width: 768px) { .content-z { padding: 2rem 2rem 4rem 2rem; } }

    @media (max-width: 767px) {
        .content-z h1 { margin-bottom: 0.5rem !important; }
        .content-z h2 { margin-bottom: 0.5rem !important; font-size: 1.05rem !important; line-height: 1.25 !important; }
        .content-z > div > p:first-of-type,
        .content-z > p:first-of-type,
        .content-z h2 + p { margin-bottom: 0.6rem !important; font-size: 0.68rem !important; line-height: 1.3 !important; }
        .content-z .mb-3, .content-z .mb-4, .content-z .mb-5, .content-z .mb-6,
        .content-z .mb-8, .content-z .mb-10, .content-z .mb-12, .content-z .mb-16 { margin-bottom: 0.5rem !important; }
        .content-z .mt-6, .content-z .mt-8, .content-z .mt-10 { margin-top: 0.5rem !important; }
        .content-z .gap-3, .content-z .gap-4, .content-z .gap-6, .content-z .gap-8 { gap: 0.35rem !important; }
        .content-z .p-4, .content-z .p-5, .content-z .p-6, .content-z .p-7, .content-z .p-8, .content-z .p-10 { padding: 0.65rem !important; }
        .content-z .py-5, .content-z .py-6 { padding-top: 0.55rem !important; padding-bottom: 0.55rem !important; }
        .content-z .space-y-2 > * + * { margin-top: 0.3rem !important; }
        .content-z .space-y-3 > * + * { margin-top: 0.35rem !important; }
    }

    .gradient-text { color: #35F0C7 !important; }
    .bg-solar-glow { box-shadow: 0 0 20px rgba(53, 240, 199, 0.3); }
    .bg-glow-1, .bg-glow-2 { position: absolute; border-radius: 50%; filter: blur(100px); z-index: 0; pointer-events: none; opacity: 0.4; }
    .bg-glow-1 { top: -10%; left: -10%; width: 50vw; height: 50vw; background: rgba(0,0,0,0.05) !important; }
    .bg-glow-2 { bottom: -10%; right: -10%; width: 40vw; height: 40vw; background: rgba(53,240,199,0.15) !important; }

    @keyframes pulse-slow { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.8; transform:scale(1.05); } }
    .animate-pulse-slow { animation: pulse-slow 4s ease-in-out infinite; }

    #video-bubble {
        position: fixed; bottom: clamp(1.5rem, 5vh, 3rem); right: clamp(1.5rem, 5vw, 4rem);
        width: clamp(140px, 22vw, 280px); height: clamp(140px, 22vw, 280px);
        border-radius: 50%;
        -webkit-mask-image: -webkit-radial-gradient(white, black);
        mask-image: radial-gradient(white, black);
        overflow: hidden; z-index: 9999;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
        background: #000; transition: opacity 0.3s ease;
    }
    @media (max-width: 768px) { #video-bubble { width: 96px; height: 96px; bottom: 12px; right: 12px; } }
    .video-wrapper { width: 100%; height: 100%; position: absolute; top:0; left:0; transform: scale(1.15); transform-origin: center center; }
    .video-wrapper video { width: 100%; height: 100%; position: absolute; top:0; left:0; object-fit: cover; border: none !important; background: #000; }

    body.pdf-export-mode { overflow: auto !important; height: auto !important; }
    body.pdf-export-mode .bg-glow-1, body.pdf-export-mode .bg-glow-2,
    body.pdf-export-mode #progress-container, body.pdf-export-mode .nav-arrow,
    body.pdf-export-mode #video-bubble, body.pdf-export-mode #start-overlay { display: none !important; }
    body.pdf-export-mode .slide-container { position: relative !important; height: auto !important; min-height: 100vh; opacity: 1 !important; transform: none !important; pointer-events: auto !important; overflow: visible !important; page-break-after: always; break-after: page; }
    @page { size: A4 landscape; margin: 10mm; }
    @media print {
        html, body { overflow: visible !important; height: auto !important; background: #ffffff !important; print-color-adjust: exact; }
        .bg-glow-1, .bg-glow-2, #progress-container, .nav-arrow, #video-bubble, #start-overlay { display: none !important; }
        .slide-container { position: relative !important; height: auto !important; min-height: 100vh; opacity: 1 !important; transform: none !important; page-break-after: always; break-after: page; }
    }
</style>
</head>
<body class="font-sans selection:bg-solar selection:text-black">

    <div id="start-overlay" class="fixed inset-0 z-[10000] bg-black text-white flex flex-col items-center justify-center cursor-pointer transition-opacity duration-500">
        <i class="ph-fill ph-play-circle text-[80px] md:text-[100px] text-solar mb-6 animate-pulse-slow"></i>
        <h2 class="text-2xl md:text-4xl font-black text-center px-4">Нажмите, чтобы начать</h2>
        <p class="text-sm md:text-base text-white/60 mt-4 font-medium">Включите звук · Видео переключает слайды</p>
    </div>

    <div id="video-bubble" class="cursor-grab" style="display: none; transform: translate3d(0,0,0);">
        <div class="video-wrapper"><video id="bubble-video" playsinline preload="auto"></video></div>
        <div id="video-overlay" class="absolute inset-0 flex flex-col items-center justify-center bg-black/40 opacity-0 transition-opacity text-white group z-20 cursor-pointer">
            <i id="video-icon" class="ph-fill ph-pause-circle text-4xl md:text-6xl drop-shadow-md transition-transform transform group-hover:scale-110"></i>
        </div>
        <div id="video-loader" class="absolute inset-0 flex items-center justify-center bg-black z-30 transition-opacity duration-300 opacity-0 pointer-events-none">
            <i class="ph-bold ph-spinner animate-spin text-4xl md:text-5xl text-solar"></i>
        </div>
    </div>

    <div class="bg-glow-1"></div>
    <div class="bg-glow-2"></div>

    <div id="progress-container" class="absolute bottom-0 left-0 h-1.5 bg-grayBase w-full z-50">
        <div id="progress-bar" class="h-full bg-solar w-0 transition-all duration-300"></div>
    </div>

    <div id="nav-prev" class="nav-arrow fixed top-1/2 left-2 md:left-6 z-50 cursor-pointer w-10 h-10 md:w-12 md:h-12 flex items-center justify-center bg-grayBase/80 hover:bg-solar rounded-full transition-colors transform -translate-y-1/2 text-black shadow-sm" onclick="prevSlide()">
        <i class="ph-bold ph-caret-left text-xl md:text-2xl"></i>
    </div>
    <div id="nav-next" class="nav-arrow fixed top-1/2 right-2 md:right-6 z-50 cursor-pointer w-10 h-10 md:w-12 md:h-12 flex items-center justify-center bg-grayBase/80 hover:bg-solar rounded-full transition-colors transform -translate-y-1/2 text-black shadow-sm" onclick="nextSlide()">
        <i class="ph-bold ph-caret-right text-xl md:text-2xl"></i>
    </div>

<!-- =================== SLIDES START =================== -->
"""

if __name__ == "__main__":
    raise SystemExit(main())
