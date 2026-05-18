#!/usr/bin/env python3
"""Build new_7/index.html — Лекция 7 в стиле 1-в-1 с aisala/ai-agents-corp/6.

Каждый из 50 слайдов прорабатывается отдельно ниже в виде функции sN().
Финал — слайд 51 с кнопкой запуска теста и модальное окно с 10
вопросами по содержанию лекции.

Запуск:
    python3 new_7/scripts/build.py
"""
from __future__ import annotations

import html as _html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "new_7/index.html"


def e(s: str) -> str:
    return _html.escape(s, quote=True)


# ============================== HEAD =========================================
HEAD = r"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Лекция 7: Люди, машины и новая логика управления</title>
    <meta name="description" content="Лекция 7: AI-трансформация компании. Гибридная система, новые роли, метрики, governance, работа с сопротивлением.">
    <meta name="theme-color" content="#35F0C7">

    <meta property="og:type" content="website">
    <meta property="og:title" content="Лекция 7: Люди, машины и новая логика управления">
    <meta property="og:description" content="Как компания становится гибридной системой">
    <meta property="og:locale" content="ru_RU">
    <meta property="og:site_name" content="Anthropolis">

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Лекция 7: Люди, машины и новая логика управления">
    <meta name="twitter:description" content="Как компания становится гибридной системой">

    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/@phosphor-icons/web"></script>

    <script>
        tailwind.config = {
            theme: { extend: {
                fontFamily: { sans: ['Montserrat', 'sans-serif'] },
                colors: { solar: '#35F0C7', grayBase: '#E9E9E9', black: '#000000', white: '#FFFFFF' }
            }}
        }
    </script>

<style>
    html { background: #ffffff !important; -webkit-tap-highlight-color: transparent; }
    body { user-select: none; overflow: hidden; background-color: #ffffff !important; margin: 0; width: 100vw; height: 100dvh; color: #000000; }
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
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        min-height: 100%;
    }
    @media (min-width: 768px) { .content-z { padding: 2rem 2rem 4rem 2rem; } }

    @media (max-width: 767px) {
        .content-z h1 { margin-bottom: 0.5rem !important; }
        .content-z h2 { margin-bottom: 0.5rem !important; font-size: 1.05rem !important; line-height: 1.25 !important; }
        .content-z > div > p:first-of-type,
        .content-z > p:first-of-type,
        .content-z h2 + p { margin-bottom: 0.6rem !important; font-size: 0.68rem !important; line-height: 1.3 !important; }
        .content-z .mb-4, .content-z .mb-5, .content-z .mb-6, .content-z .mb-8, .content-z .mb-10, .content-z .mb-12, .content-z .mb-16 {
            margin-bottom: 0.6rem !important;
        }
        .content-z .mt-6, .content-z .mt-8, .content-z .mt-10 { margin-top: 0.6rem !important; }
        .content-z .gap-3, .content-z .gap-4, .content-z .gap-6, .content-z .gap-8 { gap: 0.4rem !important; }
        .content-z .p-4, .content-z .p-5, .content-z .p-6, .content-z .p-7, .content-z .p-8, .content-z .p-10 { padding: 0.7rem !important; }
        .content-z .py-5, .content-z .py-6 { padding-top: 0.6rem !important; padding-bottom: 0.6rem !important; }
        .content-z .space-y-2 > * + * { margin-top: 0.3rem !important; }
        .content-z .space-y-3 > * + * { margin-top: 0.4rem !important; }
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
        <p class="text-sm md:text-base text-white/60 mt-4 font-medium">Включите звук · Видео будет переключать слайды</p>
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


# ============================ helpers ========================================
def H(text: str, accent: str) -> str:
    if accent in text:
        b, _, a = text.partition(accent)
        return (f'<h2 class="text-xl sm:text-3xl md:text-5xl font-black '
                f'mb-4 md:mb-6 text-center text-black">{e(b)}<span class="text-solar">'
                f'{e(accent)}</span>{e(a)}</h2>')
    return (f'<h2 class="text-xl sm:text-3xl md:text-5xl font-black '
            f'mb-4 md:mb-6 text-center text-black">{e(text)}</h2>')


def S(text: str) -> str:
    return (f'<p class="text-center text-black/60 mb-6 md:mb-10 '
            f'text-[11px] md:text-xl font-medium max-w-3xl mx-auto">{e(text)}</p>')


def punch(text: str) -> str:
    return (f'<div class="bg-solar text-black font-black text-center '
            f'text-[11px] md:text-base rounded-2xl p-3 md:p-4 max-w-4xl mx-auto w-full">'
            f'{e(text)}</div>')


def label(text: str) -> str:
    return (f'<p class="text-[10px] md:text-xs font-bold uppercase '
            f'tracking-widest text-black/40 mb-3 md:mb-4 text-center">{e(text)}</p>')


def card_center(icon: str, text: str, dark: bool = False) -> str:
    if dark:
        return (f'<div class="bg-black border-2 border-solar rounded-2xl '
                f'p-2 md:p-4 text-center shadow-xl text-white">'
                f'<i class="{icon} text-solar text-lg md:text-2xl mb-1 md:mb-2"></i>'
                f'<p class="font-black text-[10px] md:text-sm text-solar">{e(text)}</p></div>')
    return (f'<div class="bg-white border border-grayBase rounded-2xl '
            f'p-2 md:p-4 text-center shadow-sm">'
            f'<i class="{icon} text-solar text-lg md:text-2xl mb-1 md:mb-2"></i>'
            f'<p class="font-bold text-[10px] md:text-sm">{e(text)}</p></div>')


def card_row(icon: str, text: str, dark: bool = False) -> str:
    if dark:
        return (f'<div class="bg-black border-2 border-solar rounded-2xl '
                f'p-3 md:p-4 shadow-xl text-white flex items-center gap-2 md:gap-3">'
                f'<i class="{icon} text-solar text-lg md:text-2xl shrink-0"></i>'
                f'<p class="font-black text-[11px] md:text-sm text-solar">{e(text)}</p></div>')
    return (f'<div class="bg-white border border-grayBase rounded-2xl '
            f'p-3 md:p-4 shadow-sm flex items-center gap-2 md:gap-3">'
            f'<i class="{icon} text-solar text-lg md:text-2xl shrink-0"></i>'
            f'<p class="font-bold text-[11px] md:text-sm">{e(text)}</p></div>')


def grid_cards(cards: list[str], cols: str) -> str:
    return (f'<div class="grid {cols} gap-2 md:gap-3 max-w-5xl mx-auto '
            f'w-full mb-3 md:mb-6">{"".join(cards)}</div>')


def two_panel(left_label: str, left_items: list[tuple[str, str]],
              right_label: str, right_items: list[tuple[str, str]]) -> str:
    """Light vs dark side-by-side panels (как в aisala/6 slide-3, slide-5)."""
    li = "".join(
        f'<li class="flex items-center gap-2 md:gap-3">'
        f'<i class="{ic} text-solar shrink-0 text-base md:text-lg"></i>'
        f'<span>{e(tx)}</span></li>'
        for ic, tx in left_items)
    ri = "".join(
        f'<li class="flex items-center gap-2 md:gap-3">'
        f'<i class="ph-bold ph-check text-solar shrink-0"></i>{e(tx)}</li>'
        for _, tx in right_items)
    return (
        '<div class="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4 '
        'w-full max-w-5xl mx-auto mb-3 md:mb-4">'
        '<div class="bg-white border border-grayBase rounded-[20px] '
        'md:rounded-3xl p-4 md:p-6 shadow-sm">'
        f'<p class="text-[10px] md:text-xs font-bold uppercase tracking-widest '
        f'text-black/40 mb-3 md:mb-4">{e(left_label)}</p>'
        f'<ul class="space-y-1.5 md:space-y-2 text-[12px] md:text-sm '
        f'font-medium text-black/80">{li}</ul></div>'
        '<div class="bg-black border-2 border-solar rounded-[20px] '
        'md:rounded-3xl p-4 md:p-6 shadow-xl text-white">'
        f'<p class="text-[10px] md:text-xs font-bold uppercase tracking-widest '
        f'text-solar/70 mb-3 md:mb-4">{e(right_label)}</p>'
        f'<ul class="space-y-1.5 md:space-y-2 text-[12px] md:text-sm '
        f'font-medium text-white/80">{ri}</ul></div></div>'
    )


def three_panel(title1: str, items1: list[tuple[str, str]],
                title2: str, items2: list[tuple[str, str]],
                title3: str, items3: list[tuple[str, str]]) -> str:
    """3-card grid с одной чёрной (последней) — как aisala/6 slide-6."""
    def block(t, items, dark=False):
        bg = ('bg-black border-2 border-solar text-white' if dark
              else 'bg-white border border-grayBase')
        icon_color = 'bg-solar text-black' if dark else 'bg-grayBase text-black'
        title_cls = 'font-black text-sm md:text-lg' + (' text-solar' if dark else '')
        body_cls = 'text-[11px] md:text-sm ' + ('text-white/70' if dark else 'text-black/70')
        rows = ''.join(f'<p class="{body_cls}">{e(x[1])}</p>' for x in items)
        return (
            f'<div class="{bg} rounded-[20px] md:rounded-3xl p-4 md:p-5 shadow-{ "xl" if dark else "sm"}">'
            f'<div class="flex items-center gap-2 md:gap-3 mb-2 md:mb-3">'
            f'<div class="w-9 h-9 md:w-11 md:h-11 {icon_color} rounded-full flex items-center justify-center"><i class="{items[0][0]} text-base md:text-xl"></i></div>'
            f'<h3 class="{title_cls}">{e(t)}</h3></div>'
            f'{rows}</div>')
    return (
        '<div class="w-full max-w-5xl mx-auto mb-3 md:mb-4">'
        '<div class="grid grid-cols-1 md:grid-cols-3 gap-2 md:gap-3 items-stretch">'
        + block(title1, items1)
        + block(title2, items2)
        + block(title3, items3, dark=True)
        + '</div></div>'
    )


def numbered(items: list[str], cols: str = "grid-cols-1 md:grid-cols-2") -> str:
    cells = "".join(
        f'<div class="bg-white border border-grayBase rounded-2xl '
        f'p-2 md:p-4 shadow-sm flex items-start gap-2 md:gap-3">'
        f'<div class="w-7 h-7 md:w-9 md:h-9 bg-solar rounded-full '
        f'flex items-center justify-center text-black font-black text-[11px] md:text-sm shrink-0">{i+1}</div>'
        f'<p class="font-bold text-[11px] md:text-sm leading-snug pt-0.5 md:pt-1">{e(t)}</p></div>'
        for i, t in enumerate(items))
    return (f'<div class="grid {cols} gap-2 md:gap-3 max-w-5xl mx-auto '
            f'w-full mb-3 md:mb-6">{cells}</div>')


def quote_box(kicker: str, main: str, tail: str) -> str:
    return (
        '<div class="w-full max-w-4xl mx-auto bg-black border-2 border-solar '
        'rounded-[24px] md:rounded-[32px] p-4 md:p-10 '
        'shadow-[0_0_40px_rgba(53,240,199,0.25)] text-white text-center '
        'mb-3 md:mb-6">'
        f'<p class="text-[10px] md:text-xs font-bold uppercase tracking-widest '
        f'text-solar/70 mb-2 md:mb-4">{e(kicker)}</p>'
        f'<p class="text-lg md:text-3xl lg:text-4xl font-black text-solar '
        f'leading-tight mb-2 md:mb-5">{e(main)}</p>'
        f'<p class="text-white/70 text-[11px] md:text-base font-medium">{e(tail)}</p></div>'
    )


def pyramid(rows: list[str]) -> str:
    n = len(rows)
    out = []
    for i, r in enumerate(rows):
        width = 65 + i * (30 / max(1, n - 1))
        bg = "bg-grayBase/40" if i < n - 1 else "bg-solar"
        out.append(
            f'<div class="{bg} border border-grayBase rounded-xl md:rounded-2xl '
            f'py-2 px-3 md:py-3 md:px-5 flex items-center gap-2 md:gap-3" style="width:{width:.0f}%">'
            f'<div class="w-7 h-7 md:w-8 md:h-8 shrink-0 rounded-lg md:rounded-xl '
            f'bg-white flex items-center justify-center text-black font-black '
            f'text-xs md:text-base border border-grayBase">{i+1}</div>'
            f'<p class="text-[11px] md:text-base font-bold leading-tight text-black">{e(r)}</p></div>')
    return (f'<div class="flex flex-col items-center gap-1.5 md:gap-3 '
            f'w-full max-w-3xl mx-auto mb-3 md:mb-6">{"".join(out)}</div>')


def emphasis_black(text: str) -> str:
    """Чёрная плашка-emphasis (контрастная solar-плашке внизу)."""
    return ('<div class="bg-black border-2 border-solar rounded-2xl p-3 md:p-4 '
            'max-w-4xl mx-auto w-full text-white text-center mb-3">'
            f'<p class="font-black text-[11px] md:text-base text-solar">{e(text)}</p></div>')


# ============== дополнительные визуальные шаблоны =============================
def flow_horizontal(steps: list[tuple[str, str]]) -> str:
    """Pipeline шагов со стрелками. Последний шаг — тёмный акцент.
    Desktop = горизонтально, mobile = вертикально (стрелки сверху-вниз)."""
    n = len(steps)
    parts = []
    for i, (icon, lab) in enumerate(steps):
        is_last = i == n - 1
        bg = "bg-black border-2 border-solar text-white" if is_last else "bg-white border border-grayBase"
        text_cls = "text-solar" if is_last else ""
        font = "font-black" if is_last else "font-bold"
        shadow = "shadow-xl" if is_last else "shadow-sm"
        parts.append(
            f'<div class="{bg} rounded-2xl p-2 md:p-3 {shadow} flex flex-col items-center text-center w-full md:flex-1 min-w-0">'
            f'<i class="{icon} text-solar text-lg md:text-2xl mb-1 md:mb-2"></i>'
            f'<p class="{font} text-[10px] md:text-xs leading-tight {text_cls}">{e(lab)}</p>'
            f'</div>')
        if not is_last:
            parts.append(
                '<i class="ph-bold ph-caret-right text-solar text-base md:text-2xl shrink-0 hidden md:block"></i>'
                '<i class="ph-bold ph-caret-down text-solar text-base shrink-0 md:hidden self-center"></i>')
    return ('<div class="flex flex-col md:flex-row items-stretch md:items-center justify-center '
            'gap-1.5 md:gap-2 max-w-5xl mx-auto w-full mb-3 md:mb-6">' + "".join(parts) + '</div>')


def bento(big: tuple[str, str, str, str], smalls: list[tuple[str, str]],
          *, cols: str = "grid-cols-2 md:grid-cols-4") -> str:
    """1 крупная карточка (icon, title, body, kicker) + N маленьких (icon, label).
    Крупная занимает 2x2, мелкие — 1x1."""
    big_icon, big_title, big_body, big_kicker = big
    bigcard = (
        f'<div class="bg-black border-2 border-solar rounded-[20px] md:rounded-3xl '
        f'p-4 md:p-6 shadow-xl text-white col-span-2 md:row-span-2 flex flex-col justify-center">'
        f'<div class="flex items-center gap-2 md:gap-3 mb-2 md:mb-3">'
        f'<div class="w-9 h-9 md:w-12 md:h-12 bg-solar rounded-full flex items-center justify-center shrink-0"><i class="{big_icon} text-black text-base md:text-xl"></i></div>'
        f'<p class="text-[10px] md:text-xs font-bold uppercase tracking-widest text-solar/70">{e(big_kicker)}</p></div>'
        f'<h3 class="font-black text-sm md:text-2xl mb-1 md:mb-2 text-solar leading-tight">{e(big_title)}</h3>'
        f'<p class="text-[11px] md:text-sm text-white/80 leading-snug">{e(big_body)}</p></div>')
    smcards = "".join(
        f'<div class="bg-white border border-grayBase rounded-2xl p-2 md:p-4 shadow-sm flex flex-col items-center text-center justify-center">'
        f'<i class="{icon} text-solar text-base md:text-2xl mb-1 md:mb-2"></i>'
        f'<p class="font-bold text-[10px] md:text-sm leading-tight">{e(lab)}</p></div>'
        for icon, lab in smalls)
    return (f'<div class="grid {cols} gap-2 md:gap-3 max-w-5xl mx-auto w-full mb-3 md:mb-6">'
            + bigcard + smcards + '</div>')


def cycle_loop(items: list[tuple[str, str]]) -> str:
    """6 шагов в форме «петли»: первый — solar, последний — чёрный.
    На desktop сетка 3x2, на mobile 2x3. items = list of (icon, label)."""
    n = len(items)
    cells = []
    for i, (icon, t) in enumerate(items):
        if i == 0:
            bg = "bg-solar"; text_cls = "text-black"; icon_bg = "bg-black"
            icon_text = "text-solar"
        elif i == n - 1:
            bg = "bg-black border-2 border-solar"; text_cls = "text-solar"
            icon_bg = "bg-solar"; icon_text = "text-black"
        else:
            bg = "bg-white border border-grayBase"; text_cls = ""
            icon_bg = "bg-grayBase"; icon_text = "text-black"
        cells.append(
            f'<div class="{bg} rounded-2xl p-2 md:p-4 shadow-sm flex items-center gap-2 md:gap-3 min-w-0">'
            f'<div class="w-9 h-9 md:w-11 md:h-11 shrink-0 rounded-full {icon_bg} flex items-center justify-center {icon_text} font-black text-[11px] md:text-sm">'
            f'<i class="{icon} text-base md:text-xl"></i></div>'
            f'<div class="min-w-0 flex-1">'
            f'<p class="text-[9px] md:text-[10px] font-bold uppercase tracking-widest opacity-60 mb-0.5">Шаг {i+1}</p>'
            f'<p class="font-bold text-[11px] md:text-sm leading-tight {text_cls}">{e(t)}</p>'
            f'</div></div>')
    return ('<div class="grid grid-cols-2 md:grid-cols-3 gap-2 md:gap-3 max-w-5xl mx-auto '
            'w-full mb-3 md:mb-6">' + "".join(cells) + '</div>')


def concentric_layers(rows: list[str]) -> str:
    """Слои с прогрессирующим отступом — как «вложенность мышления»."""
    n = len(rows)
    out = []
    for i, t in enumerate(rows):
        indent_pct = i * 4
        is_last = i == n - 1
        bg = "bg-solar" if is_last else "bg-white border border-grayBase"
        text_cls = "text-black"
        shadow = "shadow-md" if is_last else "shadow-sm"
        out.append(
            f'<div class="{bg} rounded-2xl py-2 px-3 md:py-3 md:px-5 flex items-center gap-2 md:gap-3 {shadow} w-full" '
            f'style="margin-left:{indent_pct}%; margin-right:{indent_pct}%;">'
            f'<div class="w-7 h-7 md:w-9 md:h-9 shrink-0 rounded-full bg-white flex items-center justify-center text-black font-black text-xs md:text-base border border-grayBase">{i+1}</div>'
            f'<p class="text-[11px] md:text-base font-bold leading-tight {text_cls}">{e(t)}</p>'
            f'</div>')
    return (f'<div class="flex flex-col gap-1.5 md:gap-2 max-w-4xl mx-auto w-full mb-3 md:mb-6">'
            f'{"".join(out)}</div>')


def step_progression(steps: list[tuple[str, str, str]]) -> str:
    """Сегменты-«ступеньки»: time-label + content + connecting line.
    items = list of (label, body, icon)."""
    n = len(steps)
    parts = []
    for i, (lab, body, icon) in enumerate(steps):
        is_last = i == n - 1
        is_first = i == 0
        bg = "bg-black border-2 border-solar text-white" if is_last else "bg-white border border-grayBase"
        kicker_cls = "text-solar"
        body_cls = "text-solar" if is_last else "text-black/80"
        shadow = "shadow-xl" if is_last else "shadow-sm"
        parts.append(
            f'<div class="{bg} rounded-2xl md:rounded-3xl p-3 md:p-5 {shadow} relative">'
            f'<div class="flex items-center gap-2 md:gap-3 mb-1 md:mb-2">'
            f'<div class="w-9 h-9 md:w-11 md:h-11 rounded-full bg-solar text-black flex items-center justify-center shrink-0"><i class="{icon} text-base md:text-xl"></i></div>'
            f'<p class="text-[10px] md:text-xs font-bold uppercase tracking-widest {kicker_cls}">{e(lab)}</p></div>'
            f'<p class="font-black text-[12px] md:text-sm {body_cls} leading-snug">{e(body)}</p>'
            f'</div>')
    return ('<div class="grid grid-cols-1 md:grid-cols-2 gap-2 md:gap-3 max-w-5xl mx-auto '
            'w-full mb-3 md:mb-6">' + "".join(parts) + '</div>')


def mega_stat(big_text: str, kicker: str, support: list[tuple[str, str]]) -> str:
    """Большая центральная плашка + N маленьких карточек снизу."""
    cards = "".join(
        f'<div class="bg-white border border-grayBase rounded-2xl p-2 md:p-4 shadow-sm flex flex-col items-center text-center">'
        f'<i class="{icon} text-solar text-lg md:text-2xl mb-1 md:mb-2"></i>'
        f'<p class="font-bold text-[10px] md:text-sm">{e(t)}</p></div>'
        for icon, t in support)
    grid_cols = f"grid-cols-{min(len(support), 2)} md:grid-cols-{min(len(support), 4)}"
    return ('<div class="w-full max-w-4xl mx-auto mb-3 md:mb-6">'
            '<div class="bg-black border-2 border-solar rounded-[24px] md:rounded-[32px] '
            'p-5 md:p-10 shadow-[0_0_40px_rgba(53,240,199,0.25)] text-white text-center mb-2 md:mb-4">'
            f'<p class="text-2xl md:text-5xl lg:text-6xl font-black text-solar leading-tight mb-2 md:mb-3">{e(big_text)}</p>'
            f'<p class="text-[10px] md:text-sm font-bold uppercase tracking-widest text-white/70">{e(kicker)}</p></div>'
            f'<div class="grid {grid_cols} gap-2 md:gap-3">{cards}</div></div>')


def wrap(idx: int, comment: str, body: str, *, dark: bool = False) -> str:
    bg = " bg-black text-white" if dark else ""
    state = "opacity-100 translate-y-0" if idx == 0 else "opacity-0 pointer-events-none translate-y-8"
    return (
        f'\n    <!-- ============================================================== -->\n'
        f'    <!-- СЛАЙД {idx+1}: {comment} -->\n'
        f'    <!-- ============================================================== -->\n'
        f'    <div class="slide-container px-3 sm:px-6 md:px-12 {state}{bg}" id="slide-{idx}">\n'
        f'        <div class="content-z max-w-6xl w-full">\n{body}\n'
        f'        </div>\n    </div>\n')


# ============================== SLIDES =======================================
# Slide 1 — копия того, что одобрено в текущем new_7/index.html.
def s1() -> str:
    body = (
        '<div class="text-center w-full">'
        '<div class="flex justify-center mb-3 md:mb-10">'
        '<div class="bg-grayBase/30 border border-grayBase rounded-full '
        'px-3 py-1 md:px-4 md:py-2 shadow-sm">'
        '<p class="text-black font-bold uppercase tracking-widest text-[9px] md:text-sm m-0">Лекция 7: AI-трансформация компании</p>'
        '</div></div>'
        '<h1 class="text-xl sm:text-4xl md:text-5xl lg:text-[60px] font-black mb-2 md:mb-6 leading-tight tracking-tight text-black">'
        'Люди, машины и <span class="text-solar">новая логика управления</span></h1>'
        '<p class="text-black/70 font-bold text-[11px] md:text-2xl mb-2 md:mb-6 max-w-3xl mx-auto">Как компания становится гибридной системой</p>'
        '<p class="text-black/50 font-medium text-[10px] md:text-base mb-4 md:mb-12 max-w-3xl mx-auto">AI меняет не только процессы — он меняет само устройство компании</p>'
        + grid_cards([
            card_center("ph-fill ph-target", "Решения"),
            card_center("ph-fill ph-shield-check", "Ответственность"),
            card_center("ph-fill ph-flow-arrow", "Процессы"),
            card_center("ph-fill ph-graduation-cap", "Обучение"),
            card_center("ph-fill ph-eye", "Внимание"),
            card_center("ph-fill ph-users-three", "Гибрид", dark=True),
        ], "grid-cols-3 md:grid-cols-6")
        + punch("Человеческая · Гибридная · AI-First компания")
        + '</div>'
    )
    # Override default content-z text-align via div wrap
    state = "opacity-100 translate-y-0"
    return (
        '\n    <!-- ============================================================== -->\n'
        '    <!-- СЛАЙД 1: Титульный — AI как изменение компании -->\n'
        '    <!-- ============================================================== -->\n'
        '    <div class="slide-container px-3 sm:px-6 md:px-12 ' + state + '" id="slide-0">\n'
        '        <div class="content-z text-center max-w-6xl">\n' + body[len('<div class="text-center w-full">'):-len('</div>')] + '\n'
        '        </div>\n    </div>\n'
    )


def s2() -> str:
    body = (
        H("Главная идея лекции", "лекции")
        + S("AI-агенты меняют компанию не только технически, но и организационно")
        + two_panel(
            "Раньше — человеческая система",
            [("ph-fill ph-user", "Люди думают"),
             ("ph-fill ph-user-gear", "Люди принимают решения"),
             ("ph-fill ph-check-square", "Люди контролируют"),
             ("ph-fill ph-shield-check", "Люди отвечают за результат")],
            "Теперь — гибридная",
            [("", "AI анализирует данные"),
             ("", "AI предлагает варианты"),
             ("", "AI выполняет действия"),
             ("", "AI отслеживает отклонения")])
        + punch("Часть работы делают люди, часть — AI, часть готовится машиной и утверждается человеком")
    )
    return wrap(1, "Главная идея — гибридная система", body)


def s3() -> str:
    body = (
        H("Новый главный вопрос", "вопрос")
        + S("«Как нам внедрить AI?» — уже недостаточно. Спрашивать нужно по-другому")
        + '<div class="bg-grayBase/40 border border-grayBase rounded-2xl p-3 md:p-5 max-w-4xl mx-auto w-full mb-3 md:mb-5 text-center">'
        + '<p class="text-[10px] md:text-xs font-bold uppercase tracking-widest text-black/40 mb-1 md:mb-2">Старый вопрос</p>'
        + '<p class="text-sm md:text-xl font-bold text-black/50 line-through">Как нам внедрить AI?</p></div>'
        + label("Новые вопросы")
        + grid_cards([
            card_row("ph-fill ph-robot", "Где AI может действовать сам?"),
            card_row("ph-fill ph-eye", "Где человек должен контролировать?"),
            card_row("ph-fill ph-gavel", "Где обязательно финальное слово человека?"),
            card_row("ph-fill ph-shield-check", "Кто отвечает за результат?", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + punch("Не просто подключить AI, а встроить его так, чтобы компания стала сильнее")
    )
    return wrap(2, "Новый главный вопрос — управление гибридом", body)


def s4() -> str:
    body = (
        H("ИИ — не просто автоматизация", "автоматизация")
        + S("Автоматизация ускоряет старую логику. AI меняет саму логику процесса")
        + two_panel(
            "Автоматизация",
            [("ph-fill ph-fast-forward", "Ускоряет существующий шаг"),
             ("ph-fill ph-arrows-clockwise", "Заменяет ручную операцию"),
             ("ph-fill ph-clock-counter-clockwise", "Та же логика, быстрее")],
            "Искусственный интеллект",
            [("", "Анализирует ситуацию"),
             ("", "Находит закономерности"),
             ("", "Предлагает решения"),
             ("", "Контролирует отклонения")])
        + punch("Меняется не только скорость, но и сама логика процесса")
    )
    return wrap(3, "ИИ — не просто автоматизация", body)


def s5() -> str:
    # Bento: одна крупная карточка-вывод + 4 маленькие про неизменённые элементы
    body = (
        H("Почему старые подходы перестают работать", "перестают работать")
        + S("Можно технически внедрить AI и остаться старой компанией по устройству")
        + bento(
            big=("ph-fill ph-warning-octagon",
                 "AI внедрён, компания — нет",
                 "Должностные инструкции не отражают реальность. Часть действий выполняет AI, но ответственность не пересобрана.",
                 "Главная ловушка"),
            smalls=[
                ("ph-fill ph-clipboard-text", "Должностные инструкции"),
                ("ph-fill ph-chart-bar", "Старые KPI измеряют занятость"),
                ("ph-fill ph-graduation-cap", "Обучение «как раньше»"),
                ("ph-fill ph-warning", "Размытая ответственность"),
            ])
        + punch("Внедрение AI — это не IT-проект. Это управленческая трансформация")
    )
    return wrap(4, "Почему старые подходы не работают", body)


def s6() -> str:
    body = (
        H("Управленческая трансформация", "трансформация")
        + S("Купили инструмент, подключили модель, запустили пилот — это ещё не изменение")
        + quote_box(
            "Ключевой переход",
            "AI входит не в вакуум — в живую организацию",
            "С людьми, ответственностью, привычками и управленческой логикой")
        + label("Что должно пересобраться")
        + grid_cards([
            card_center("ph-fill ph-user-circle-gear", "Роли"),
            card_center("ph-fill ph-flow-arrow", "Процессы"),
            card_center("ph-fill ph-scroll", "Правила"),
            card_center("ph-fill ph-graduation-cap", "Обучение"),
            card_center("ph-fill ph-chart-line-up", "Показатели", dark=True),
        ], "grid-cols-3 md:grid-cols-5")
        + punch("Иначе AI будет работать сбоку от реального бизнеса")
    )
    return wrap(5, "Внедрение AI = управленческая трансформация", body)


def s7() -> str:
    body = (
        H("Что такое гибридная система", "гибридная система")
        + S("Человек и AI участвуют в одном процессе, но выполняют разные функции")
        + two_panel(
            "Человек",
            [("ph-fill ph-compass", "Задаёт цель"),
             ("ph-fill ph-scroll", "Определяет правила"),
             ("ph-fill ph-warning-octagon", "Принимает рискованные решения"),
             ("ph-fill ph-shield-check", "Отвечает за последствия")],
            "AI",
            [("", "Анализирует данные"),
             ("", "Выполняет операции"),
             ("", "Ищет закономерности"),
             ("", "Следит за отклонениями")])
        + punch("Не замена человека — правильное распределение работы между ним и машиной")
    )
    return wrap(6, "Что такое гибридная система", body)


def s8() -> str:
    body = (
        H("Результат создаётся взаимодействием", "взаимодействием")
        + S("Ценность появляется в связке, а не отдельно у человека или AI")
        + two_panel(
            "Слабая модель",
            [("ph-fill ph-x-circle", "AI «добавили» в процесс"),
             ("ph-fill ph-x-circle", "Эффект ждут сам собой"),
             ("ph-fill ph-x-circle", "Роли не описаны"),
             ("ph-fill ph-x-circle", "Ответственность размыта")],
            "Сильная модель",
            [("", "Кто ставит задачу"),
             ("", "Кто готовит решение"),
             ("", "Кто проверяет результат"),
             ("", "Кто принимает финальное решение"),
             ("", "Кто отвечает за последствия")])
        + punch("Взаимодействие AI и человека должно быть специально спроектировано")
    )
    return wrap(7, "Результат — через взаимодействие", body)


def s9() -> str:
    body = (
        H("Было: человеческая организация", "человеческая")
        + S("Человек был главным центром смысла, решения и контроля")
        + pyramid([
            "Человек принимает решение",
            "Человек согласовывает",
            "Человек контролирует",
            "Человек делает",
            "Человек отвечает за результат",
        ])
        + emphasis_black("Естественное ограничение — человеческое внимание")
        + punch("Компания упирается не только в нехватку людей, но и в их способность обрабатывать сложность")
    )
    return wrap(8, "Было: человеческая организация", body)


def s10() -> str:
    body = (
        H("Стало: гибридная организация", "гибридная")
        + S("AI становится внешним слоем мышления компании")
        + pyramid([
            "AI: рутина и мониторинг",
            "AI: первичный анализ",
            "AI: подготовка вариантов",
            "Человек: цели и правила",
            "Человек: ответственность за последствия",
        ])
        + emphasis_black("Не компания без людей — компания, где мышление усилено машиной")
        + punch("AI расширяет возможности, направление всё равно задаёт человек")
    )
    return wrap(9, "Стало: гибридная организация", body)


def s11() -> str:
    body = (
        H("Новая роль человека", "роль человека")
        + S("Человек не исчезает. Его роль становится важнее — но иначе устроена")
        + numbered([
            "Задавать цели",
            "Формулировать правила",
            "Определять границы автономности AI",
            "Отвечать за последствия",
        ])
        + emphasis_black("Не просто выполнять задачи внутри процесса — проектировать саму логику работы")
        + punch("Человек становится архитектором и оператором системы")
    )
    return wrap(10, "Новая роль человека", body)


def s12() -> str:
    body = (
        H("Гибридность ≠ полная автоматизация", "не полная автоматизация")
        + S("Разница в том, остаётся человек в процессе или нет")
        + two_panel(
            "Полная автоматизация",
            [("ph-fill ph-user-minus", "Человек полностью вне процесса"),
             ("ph-fill ph-robot", "Только машинная логика"),
             ("ph-fill ph-warning", "Допустима лишь там, где нет смыслов и этики")],
            "Гибридность",
            [("", "Функции и ответственность распределены"),
             ("", "AI: скорость, масштаб, мониторинг"),
             ("", "Человек: цель, этика, риск, выбор"),
             ("", "Ответственность перед клиентом и обществом")])
        + punch("Не «что автоматизировать полностью?» — а «где AI действует, а где человек обязан остаться?»")
    )
    return wrap(11, "Гибридность — не полная автоматизация", body)


def s13() -> str:
    body = (
        H("Где человек остаётся главным", "главным")
        + S("Четыре зоны, в которых нельзя отдавать решение алгоритму")
        + grid_cards([
            card_row("ph-fill ph-compass", "Постановка целей — ради чего существует бизнес"),
            card_row("ph-fill ph-warning-octagon", "Рискованные решения — финансовые, юридические, репутационные"),
            card_row("ph-fill ph-scales", "Этика — не всё эффективное допустимо"),
            card_row("ph-fill ph-shield-check", "Ответственность перед клиентом и регулятором", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + punch("«Так решил алгоритм» — не ответ ни клиенту, ни регулятору")
    )
    return wrap(12, "Где человек остаётся главным", body)


def s14() -> str:
    body = (
        H("Где ИИ объективно сильнее", "сильнее")
        + S("Четыре зоны, в которых AI делает работу лучше человека")
        + grid_cards([
            card_row("ph-fill ph-database", "Большие объёмы данных и документов"),
            card_row("ph-fill ph-magnifying-glass", "Поиск слабых сигналов и закономерностей"),
            card_row("ph-fill ph-arrows-clockwise", "Повторяемые рутинные действия"),
            card_row("ph-fill ph-eye", "Круглосуточный мониторинг", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + punch("Человек устаёт и отвлекается — AI мониторит непрерывно")
    )
    return wrap(13, "Где ИИ объективно сильнее", body)


def s15() -> str:
    # 4 numbered mode cards in 2x2 grid, last one dark
    cards = []
    items = [
        ("1", "AI предлагает, человек решает", "Самый безопасный режим: сложные и рискованные задачи"),
        ("2", "AI действует, человек контролирует", "Повторяемые процессы с понятными правилами"),
        ("3", "AI действует самостоятельно", "Низкие риски, понятные сценарии, систему можно остановить"),
        ("4", "Соавторство", "Человек и AI вместе создают документ, анализ, стратегию"),
    ]
    for i, (n, t, d) in enumerate(items):
        is_last = (i == len(items) - 1)
        bg = ('bg-black border-2 border-solar text-white' if is_last
              else 'bg-white border border-grayBase')
        title_cls = 'font-black text-[12px] md:text-lg' + (' text-solar' if is_last else '')
        body_cls = 'text-[11px] md:text-sm ' + ('text-white/70' if is_last else 'text-black/60')
        cards.append(
            f'<div class="{bg} rounded-2xl md:rounded-3xl p-3 md:p-5 shadow-{ "xl" if is_last else "sm"}">'
            f'<div class="flex items-center gap-2 md:gap-3 mb-1 md:mb-3">'
            f'<div class="w-8 h-8 md:w-11 md:h-11 bg-solar rounded-full flex items-center justify-center text-black font-black text-[12px] md:text-base">{n}</div>'
            f'<h3 class="{title_cls}">{e(t)}</h3></div>'
            f'<p class="{body_cls}">{e(d)}</p></div>')
    body = (
        H("Режимы самостоятельности ИИ", "самостоятельности")
        + S("Четыре уровня — от полной проверки человеком до соавторства")
        + ('<div class="grid grid-cols-1 md:grid-cols-2 gap-2 md:gap-4 max-w-5xl mx-auto w-full mb-3 md:mb-6">'
           + ''.join(cards) + '</div>')
        + punch("Главная задача управления — определить, где какой режим допустим")
    )
    return wrap(14, "Режимы самостоятельности AI", body)


def s16() -> str:
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
        + punch("Управляемый режим внутри заранее определённых границ — не свобода алгоритма")
    )
    return wrap(15, "Где допустима автономность AI", body)


def s17() -> str:
    body = (
        H("Управление = управление границей", "управление границей")
        + S("Где AI, где человек — и эта граница не задаётся один раз навсегда")
        + quote_box(
            "Главная задача",
            "Провести границу между человеком и AI",
            "И постоянно её перепроектировать по мере роста доверия")
        + label("Что нужно решить заново")
        + grid_cards([
            card_row("ph-fill ph-question", "Что доверить машине?"),
            card_row("ph-fill ph-check-square", "Что контролирует человек?"),
            card_row("ph-fill ph-gavel", "Где финальное слово руководителя?"),
            card_row("ph-fill ph-hand-palm", "Где человек не должен мешать?", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + punch("Управление изменениями — это постоянное проектирование ответственности")
    )
    return wrap(16, "Управление = управление границей", body)


def s18() -> str:
    body = (
        H("Если граница не определена", "не определена")
        + S("Два опасных сценария — и оба разрушают управляемость")
        + two_panel(
            "Сценарий 1 — страх",
            [("ph-fill ph-warning", "Люди боятся пользоваться AI"),
             ("ph-fill ph-question", "Не понимают, за что отвечают"),
             ("ph-fill ph-pause-circle", "Используют AI формально и осторожно")],
            "Сценарий 2 — хаос",
            [("", "Решения перекладывают на алгоритм"),
             ("", "Ответственность размывается"),
             ("", "Компания теряет управляемость")])
        + label("Любая AI-система должна отвечать на 4 вопроса")
        + grid_cards([
            card_row("ph-fill ph-user-check", "Кто решает"),
            card_row("ph-fill ph-eye", "Кто проверяет"),
            card_row("ph-fill ph-hand-palm", "Кто вмешивается"),
            card_row("ph-fill ph-shield-check", "Кто отвечает", dark=True),
        ], "grid-cols-2 md:grid-cols-4")
        + punch("Без чёткой границы — либо парализованность, либо хаос")
    )
    return wrap(17, "Если граница не определена", body)


def s19() -> str:
    # mega_stat — крупный визуальный акцент на главной мысли + 4 опоры снизу
    body = (
        H("ИИ как усилитель управляемости", "усилитель")
        + S("Больше сигналов, быстрее реакция, шире контекст для решений")
        + mega_stat(
            big_text="×10 управляемости",
            kicker="Команда удерживает больше процессов одновременно",
            support=[
                ("ph-fill ph-broadcast", "Больше сигналов"),
                ("ph-fill ph-lightning", "Быстрее реакция"),
                ("ph-fill ph-warning", "Раньше видны риски"),
                ("ph-fill ph-binoculars", "Шире контекст"),
            ])
        + punch("Не вручную собирать информацию — видеть, где процесс нормален, где риск, где нужен человек")
    )
    return wrap(18, "AI как усилитель управляемости", body)


def s20() -> str:
    # Flow horizontal: 6 шагов конвейера решения со стрелками. Финал — чёрный.
    body = (
        H("Как меняется управленческое решение", "управленческое решение")
        + S("От опыта и интуиции — к гипотезе, данным, моделированию")
        + flow_horizontal([
            ("ph-fill ph-lightbulb", "Гипотеза"),
            ("ph-fill ph-database", "Данные"),
            ("ph-fill ph-shuffle", "Моделирование"),
            ("ph-fill ph-list-checks", "AI: рекомендации"),
            ("ph-fill ph-warning", "AI: риски"),
            ("ph-fill ph-gavel", "Человек: решение"),
        ])
        + punch("Руководитель понимает, на каких данных, какие ограничения у AI, какую ответственность берёт компания")
    )
    return wrap(19, "Как меняется управленческое решение", body)


def s21() -> str:
    body = (
        H("Руководитель как модератор интеллекта", "модератор")
        + S("Не единственный источник ответа, а архитектор мышления системы")
        + quote_box(
            "Сильный руководитель сегодня",
            "Не тот, кто быстрее даёт готовый ответ",
            "А тот, кто строит среду, где лучшие ответы появляются быстрее и качественнее")
        + label("Что он делает")
        + grid_cards([
            card_row("ph-fill ph-question", "Задаёт правильный вопрос"),
            card_row("ph-fill ph-list-checks", "Определяет критерии выбора"),
            card_row("ph-fill ph-flag-banner", "Обозначает границы допустимого"),
            card_row("ph-fill ph-gavel", "Принимает финальное решение", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + punch("AI расширяет поле вариантов — руководитель определяет, какие допустимы")
    )
    return wrap(20, "Руководитель как модератор интеллекта", body)


def s22() -> str:
    # Concentric layers — выглядит как вложенные слои мышления (3D-эффект отступами)
    body = (
        H("ИИ как внешний слой мышления", "слой мышления")
        + S("Расширяет внимание, память и способность удерживать много процессов одновременно")
        + concentric_layers([
            "Удерживает контекст",
            "Сравнивает варианты",
            "Возвращает к прошлым решениям",
            "Замечает отклонения",
            "Подсвечивает слабые сигналы",
        ])
        + emphasis_black("Правильный AI снижает шум, а не увеличивает его")
        + punch("Если стало больше отчётов и уведомлений — это плохой результат внедрения")
    )
    return wrap(21, "ИИ как внешний слой мышления", body)


def s23() -> str:
    body = (
        H("Руководитель как архитектор внимания", "архитектор внимания")
        + S("В AI-первой компании руководитель проектирует систему внимания организации")
        + numbered([
            "Какие сигналы действительно важны",
            "Какие отклонения требуют реакции",
            "Какие решения необратимы",
            "Где AI справляется сам",
            "Где человек обязан вмешаться",
        ])
        + punch("Конкурентное преимущество — у компании, у которой быстрее и точнее мышление")
    )
    return wrap(22, "Руководитель как архитектор внимания", body)


def s24() -> str:
    body = (
        H("ИИ внедряет новый тип труда", "новый тип труда")
        + S("Ценность человека смещается от исполнения к проектированию работы")
        + two_panel(
            "Старая модель",
            [("ph-fill ph-clipboard-text", "Получил задачу"),
             ("ph-fill ph-hammer", "Сделал руками"),
             ("ph-fill ph-paper-plane-right", "Передал результат"),
             ("ph-fill ph-check-square", "Руководитель проверил")],
            "Гибридная модель",
            [("", "Поставить цель"),
             ("", "Задать ограничения"),
             ("", "Выбрать режим автономности AI"),
             ("", "Проверить результат"),
             ("", "Принять решение")])
        + punch("Работа теперь — это не только «сделать руками»")
    )
    return wrap(23, "Новый тип труда", body)


def s25() -> str:
    body = (
        H("Почему эффект не появляется сам", "не появляется сам")
        + S("Технология внедрена, но организационная модель не изменилась")
        + label("Что ломается без перестройки")
        + grid_cards([
            card_row("ph-fill ph-user-circle-minus", "Сотрудник не понимает, за что отвечает"),
            card_row("ph-fill ph-question", "Руководитель не знает, как оценивать результат"),
            card_row("ph-fill ph-bug", "ИТ отвечает за внедрение, но не за бизнес-эффект"),
            card_row("ph-fill ph-buildings", "Бизнес ждёт результата, не меняя процесс", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + punch("Эффект от AI нужно не ждать — его нужно проектировать")
    )
    return wrap(24, "Почему эффект не появляется сам", body)


def s26() -> str:
    body = (
        H("Роль — это не должность", "не должность")
        + S("Должность — название в структуре. Роль — логика ответственности")
        + two_panel(
            "Должность",
            [("ph-fill ph-identification-card", "Название в структуре"),
             ("ph-fill ph-buildings", "Привязка к департаменту"),
             ("ph-fill ph-clock", "Часто статична")],
            "Роль",
            [("", "Логика ответственности"),
             ("", "Кто за что отвечает"),
             ("", "Кто принимает решение"),
             ("", "По каким правилам действует"),
             ("", "Где финальная ответственность")])
        + punch("AI может анализировать и действовать, но ответственность — за человеком")
    )
    return wrap(25, "Роль ≠ должность", body)


def s27() -> str:
    # Bento: главная роль крупно + 4 маленькие
    body = (
        H("Новые роли в гибридной компании", "новые роли")
        + S("Старой ролевой модели уже недостаточно — появляются новые зоны ответственности")
        + bento(
            big=("ph-fill ph-flow-arrow",
                 "Владелец гибридного процесса",
                 "Знает, как процесс реально работает с AI: что отдать машине, что оставить человеку, где нужен контроль и как измерить эффект.",
                 "Ключевая роль"),
            smalls=[
                ("ph-fill ph-blueprint", "Архитектор автоматизации"),
                ("ph-fill ph-medal-military", "Бизнес-владелец результата"),
                ("ph-fill ph-shield-warning", "Владелец риска"),
                ("ph-fill ph-trophy", "AI-чемпион"),
            ])
        + punch("Появляются зоны ответственности, которых раньше не было явно выражено")
    )
    return wrap(26, "Новые роли в компании", body)


def s28() -> str:
    body = (
        H("Владелец процесса + архитектор автоматизации", "две ключевые роли")
        + S("Две роли на разном уровне абстракции")
        + two_panel(
            "Владелец процесса",
            [("ph-fill ph-flow-arrow", "Как реально работает процесс с AI"),
             ("ph-fill ph-question", "Что отдать AI, что оставить человеку"),
             ("ph-fill ph-check-square", "Где нужен контроль человеком"),
             ("ph-fill ph-chart-line-up", "Как измерить эффект")],
            "Архитектор автоматизации",
            [("", "Связка людей, агентов, данных, систем"),
             ("", "Где AI помогает / где автономен"),
             ("", "Где система обязана остановиться"),
             ("", "Интеграции с корпоративными системами")])
        + punch("Один смотрит вглубь процесса, другой — на систему целиком")
    )
    return wrap(27, "Владелец процесса + архитектор", body)


def s29() -> str:
    body = (
        H("Бизнес-владелец, владелец риска, ИИ-чемпион", "три роли")
        + S("Три роли, без которых реальный эффект от AI не появится")
        + three_panel(
            "Бизнес-владелец",
            [("ph-fill ph-medal-military", "Отвечает за эффект, не за пилот — быстрее, дешевле, качественнее")],
            "Владелец риска",
            [("ph-fill ph-shield-warning", "Юридические, этические, репутационные, операционные последствия")],
            "AI-чемпион",
            [("ph-fill ph-trophy", "Помогает команде освоить новый способ работы")])
        + punch("AI превращается из внешней технологии в норму ежедневной работы")
    )
    return wrap(28, "Бизнес-владелец, риск, чемпион", body)


def s30() -> str:
    body = (
        H("Матрица компетенций", "Матрица")
        + S("Не просто знание инструмента — умение работать вместе с AI")
        + numbered([
            "Правильно поставить задачу",
            "Задать ограничения",
            "Понимать, где AI может ошибаться",
            "Проверять результат",
            "Интерпретировать рекомендации",
            "Давать обратную связь",
            "Понимать свою ответственность",
        ])
        + punch("Матрица — разная для руководителей, владельцев процессов, архитекторов и сотрудников")
    )
    return wrap(29, "Матрица компетенций", body)


def s31() -> str:
    body = (
        H("Регламент — это не бюрократия", "не бюрократия")
        + S("Способ сохранить управляемость и безопасность, когда в процесс приходит AI")
        + label("На какие вопросы отвечает регламент")
        + grid_cards([
            card_row("ph-fill ph-user-check", "Кто может запускать агента"),
            card_row("ph-fill ph-pencil", "Кто меняет правила его работы"),
            card_row("ph-fill ph-database", "Какие данные можно использовать"),
            card_row("ph-fill ph-check-square", "Когда результат обязан проверить человек"),
            card_row("ph-fill ph-warning-octagon", "Что делать при ошибке"),
            card_row("ph-fill ph-stop-circle", "Кто может остановить систему", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + punch("Хороший регламент не тормозит — он делает масштабирование безопасным")
    )
    return wrap(30, "Регламент — не бюрократия", body)


def s32() -> str:
    body = (
        H("ИИ не нейтрален", "не нейтрален")
        + S("AI всегда отражает человеческие управленческие выборы")
        + grid_cards([
            card_row("ph-fill ph-database", "Работает на данных, которые кто-то выбрал"),
            card_row("ph-fill ph-target", "Оптимизирует цели, которые кто-то задал"),
            card_row("ph-fill ph-chart-bar", "Использует показатели, которые кто-то признал важными"),
            card_row("ph-fill ph-flag-banner", "Действует в границах, которые кто-то разрешил", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + punch("За каждым решением AI стоят решения людей")
    )
    return wrap(31, "ИИ не нейтрален", body)


def s33() -> str:
    body = (
        H("Ответственность нельзя переложить на алгоритм", "нельзя переложить")
        + S("Если решение повлияло на людей и деньги — отвечают люди")
        + label("У каждого AI-сценария должны быть владельцы")
        + grid_cards([
            card_center("ph-fill ph-medal-military", "Бизнес-результат"),
            card_center("ph-fill ph-shield-warning", "Риск"),
            card_center("ph-fill ph-eye", "Проверка спорных решений"),
            card_center("ph-fill ph-stop-circle", "Остановка системы"),
            card_center("ph-fill ph-clipboard-text", "Разбор ошибок", dark=True),
        ], "grid-cols-2 md:grid-cols-5")
        + emphasis_black("«Это не мы, это алгоритм» — не примет ни клиент, ни регулятор")
        + punch("AI помогает принимать решения, но не несёт ответственность вместо компании")
    )
    return wrap(32, "Ответственность нельзя переложить", body)


def s34() -> str:
    body = (
        H("Этика — это процесс", "процесс")
        + S("Не декларация на сайте, а встроенные в работу механизмы")
        + grid_cards([
            card_row("ph-fill ph-list-bullets", "Журнал действий агента"),
            card_row("ph-fill ph-eye", "Проверка человеком в критичных случаях"),
            card_row("ph-fill ph-stop-circle", "Возможность ручной остановки"),
            card_row("ph-fill ph-magnifying-glass", "Порядок разбора инцидентов"),
            card_row("ph-fill ph-arrows-counter-clockwise", "Правила обновления моделей"),
            card_row("ph-fill ph-user-circle-gear", "Понятные зоны ответственности", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + punch("Доверие появляется не от обещаний, а от прозрачности")
    )
    return wrap(33, "Этика — это процесс", body)


def s35() -> str:
    body = (
        H("Показатели гибридной системы", "Показатели")
        + S("Меряем не объём активности, а эффект для системы")
        + two_panel(
            "Старые показатели",
            [("ph-fill ph-clock", "Сколько часов потрачено"),
             ("ph-fill ph-clipboard-text", "Сколько задач выполнено"),
             ("ph-fill ph-files", "Сколько документов обработано"),
             ("ph-fill ph-cursor-click", "Сколько действий сделал сотрудник")],
            "Новые показатели",
            [("", "Скорость решений"),
             ("", "Меньше ошибок и переделок"),
             ("", "Стабильность и предсказуемость"),
             ("", "Снижение затрат · рост выручки")])
        + punch("Не «сколько мы сделали», а «насколько лучше стала работать система»")
    )
    return wrap(34, "Показатели гибридной системы", body)


def s36() -> str:
    body = (
        H("Метрики человека и ИИ не должны конфликтовать", "не должны конфликтовать")
        + S("Если AI оптимизирует одно, а человека оценивают по другому — сопротивление неизбежно")
        + two_panel(
            "Конфликт",
            [("ph-fill ph-warning", "AI улучшает качество"),
             ("ph-fill ph-warning", "Человека мерят только скоростью"),
             ("ph-fill ph-x-circle", "AI снижает риск"),
             ("ph-fill ph-x-circle", "Команду мотивируют только на продажи")],
            "Согласованность",
            [("", "Скорость без потери качества"),
             ("", "Рост объёма без ухудшения CX"),
             ("", "Эффект без нарушения этики"),
             ("", "Метрики согласованы на уровне процесса")])
        + punch("Иначе люди будут не усиливать систему, а защищаться от неё")
    )
    return wrap(35, "Метрики не должны конфликтовать", body)


def s37() -> str:
    body = (
        H("Автоматизация ≠ изменение", "не равна изменению")
        + S("Пилот показывает, что технология работает. Это не доказывает, что компания умеет встраивать AI")
        + two_panel(
            "Вопрос автоматизации",
            [("ph-fill ph-question", "Что может сделать AI?"),
             ("ph-fill ph-flask", "Технический пилот"),
             ("ph-fill ph-check-circle", "Технология работает")],
            "Вопрос изменения",
            [("", "Как должна измениться компания?"),
             ("", "Роли, правила, обучение, KPI"),
             ("", "Принятие и ответственность"),
             ("", "Устойчивая ценность")])
        + punch("Успешный пилот — это не финал, а вход в управленческую трансформацию")
    )
    return wrap(36, "Автоматизация ≠ изменение", body)


def s38() -> str:
    # Bento: главная стратегическая цель крупно + 3 поменьше
    body = (
        H("ИИ как портфель изменений", "портфель")
        + S("Не хаос экспериментов — а связанная со стратегией программа")
        + bento(
            big=("ph-fill ph-strategy",
                 "AI = инструмент достижения бизнес-целей",
                 "Каждый сценарий должен отвечать на стратегическую задачу. Иначе компания получает витрину пилотов, а не системный эффект.",
                 "Стратегический подход"),
            smalls=[
                ("ph-fill ph-rocket-launch", "Ускорить выход на рынок"),
                ("ph-fill ph-currency-circle-dollar", "Снизить затраты"),
                ("ph-fill ph-trend-up", "Масштабироваться без штата"),
                ("ph-fill ph-smiley", "Улучшить клиентский опыт"),
            ])
        + punch("Важен не сам факт эксперимента, а его вклад в стратегию")
    )
    return wrap(37, "ИИ как портфель изменений", body)


def s39() -> str:
    body = (
        H("7 контрольных вопросов перед запуском", "7 вопросов")
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
        + punch("Если на эти вопросы нет ответов — это демонстрация, а не AI-сценарий")
    )
    return wrap(38, "7 контрольных вопросов", body)


def s40() -> str:
    # Cycle loop с иконками: 6 шагов жизненного цикла
    body = (
        H("Шесть фаз портфеля ИИ-изменений", "Шесть фаз")
        + S("Управляемый жизненный цикл — от поиска возможностей до закрытия")
        + cycle_loop([
            ("ph-fill ph-magnifying-glass", "Поиск возможностей"),
            ("ph-fill ph-funnel", "Приоритизация идей"),
            ("ph-fill ph-flask", "Пилот на реальном процессе"),
            ("ph-fill ph-factory", "Промышленная сборка"),
            ("ph-fill ph-trend-up", "Масштабирование"),
            ("ph-fill ph-x-circle", "Закрытие без эффекта"),
        ])
        + emphasis_black("Закрытие — не провал. Это накопленное знание о том, где AI не работает")
        + punch("Без жизненного цикла портфель превращается в витрину пилотов")
    )
    return wrap(39, "6 фаз портфеля AI-изменений", body)


def s41() -> str:
    # step_progression: 4 этапа с разной периодичностью + иконкой времени
    body = (
        H("Ритм управления изменениями", "Ритм")
        + S("AI-трансформация не управляется разовыми совещаниями")
        + step_progression([
            ("Каждую неделю", "Сам процесс — где AI помогает, где исключения, где обходят", "ph-fill ph-calendar-dots"),
            ("Раз в две недели", "Пилоты — эффект, принятие пользователей, риски", "ph-fill ph-calendar-check"),
            ("Раз в месяц", "Портфельный совет — что масштабировать, что закрыть", "ph-fill ph-calendar-blank"),
            ("Раз в квартал", "Стандарты, академия, регламенты, показатели", "ph-fill ph-calendar-star"),
        ])
        + punch("Эксперименты быстрые, ошибки дешёвые, масштабирование управляемое")
    )
    return wrap(40, "Ритм управления изменениями", body)


def s42() -> str:
    body = (
        H("ИИ-изменения = управление неопределённостью", "управление неопределённостью")
        + S("Через гипотезы, а не веру в технологию")
        + quote_box(
            "Жизненный цикл гипотезы",
            "Сформулировать → проверить → измерить → решить",
            "Масштабировать, доработать или закрыть — обе ветки нормальные")
        + emphasis_black("Настоящий провал — тащить проект без результата, без владельца, без принятия")
        + punch("Часть инициатив не даст эффекта — это нормально для управления неопределённостью")
    )
    return wrap(41, "AI-изменения — управление неопределённостью", body)


def s43() -> str:
    body = (
        H("Бизнес-владелец изменения", "Бизнес-владелец")
        + S("У каждого AI-изменения должен быть владелец со стороны бизнеса")
        + two_panel(
            "Кто НЕ может быть владельцем",
            [("ph-fill ph-x-circle", "IT"),
             ("ph-fill ph-x-circle", "Подрядчик"),
             ("ph-fill ph-x-circle", "Data-команда")],
            "За что отвечает бизнес-владелец",
            [("", "Смысл и цель изменения"),
             ("", "Люди и принятие"),
             ("", "Показатели и эффект"),
             ("", "Масштабирование")])
        + punch("Без бизнес-владельца AI становится технической демонстрацией")
    )
    return wrap(42, "Бизнес-владелец изменения", body)


def s44() -> str:
    body = (
        H("Сопротивление — нормальная реакция", "нормальная реакция")
        + S("Не ошибка и не признак плохой культуры — реакция живой системы на изменение")
        + label("Сотрудник часто боится потерять")
        + grid_cards([
            card_center("ph-fill ph-user-circle-gear", "Контроль"),
            card_center("ph-fill ph-medal", "Статус"),
            card_center("ph-fill ph-eye", "Понятность"),
            card_center("ph-fill ph-clipboard-text", "Привычную роль"),
            card_center("ph-fill ph-question", "Уверенность в будущем", dark=True),
        ], "grid-cols-2 md:grid-cols-5")
        + emphasis_black("Главный вопрос сотрудника очень простой: «Что изменится лично для меня?»")
        + punch("Пока человек не получил честный ответ — он формально соглашается, но работает по-старому")
    )
    return wrap(43, "Сопротивление — нормальная реакция", body)


def s45() -> str:
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
        ], "grid-cols-1 md:grid-cols-3")
        + punch("Без ответов — неопределённость, а за ней сопротивление")
    )
    return wrap(44, "Что нужно объяснить сотруднику", body)


def s46() -> str:
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
        + punch("Если менеджеры сами не используют AI, команда не поверит, что это новая норма")
    )
    return wrap(45, "Как работать с сопротивлением", body)


def s47() -> str:
    body = (
        H("Средний менеджмент и новая норма", "Средний менеджмент")
        + S("Ключевой слой AI-трансформации — переводчик стратегии в ежедневную работу")
        + label("Что менеджер объясняет команде")
        + grid_cards([
            card_row("ph-fill ph-calendar-check", "Что меняется завтра утром"),
            card_row("ph-fill ph-robot", "Где AI помогает"),
            card_row("ph-fill ph-eye", "Где человек обязан проверить"),
            card_row("ph-fill ph-chart-line", "Как теперь оценивается работа"),
            card_row("ph-fill ph-warning", "Что делать при ошибке"),
            card_row("ph-fill ph-rocket", "Как использовать AI в реальных задачах", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + punch("Если менеджер сам понимает AI и видит пользу — команда принимает изменение")
    )
    return wrap(46, "Средний менеджмент", body)


def s48() -> str:
    body = (
        H("ИИ нельзя спустить сверху", "нельзя спустить сверху")
        + S("Доступ, вебинар и письмо от руководства сами по себе не меняют поведение")
        + two_panel(
            "Что не работает",
            [("ph-fill ph-x-circle", "Доступ к инструменту"),
             ("ph-fill ph-x-circle", "Вебинар на час"),
             ("ph-fill ph-x-circle", "Письмо от руководства"),
             ("ph-fill ph-x-circle", "Лозунги «теперь все используют AI»")],
            "Что работает",
            [("", "Пример руководителей"),
             ("", "Реальная польза в работе"),
             ("", "Практические кейсы"),
             ("", "Видимый результат — быстрее, качественнее")])
        + punch("Когда люди видят, что AI действительно помогает — сопротивление превращается в интерес")
    )
    return wrap(47, "AI нельзя спустить сверху", body)


def s49() -> str:
    body = (
        H("Метрики принятия и правильный KPI", "правильный KPI")
        + S("AI внедрён не когда дали доступ, а когда изменилось поведение и результат")
        + two_panel(
            "Имитация активности",
            [("ph-fill ph-warning", "KPI = «использовал AI»"),
             ("ph-fill ph-clipboard-text", "Много запросов, мало смысла"),
             ("ph-fill ph-x-circle", "Результат работы не меняется"),
             ("ph-fill ph-eye-slash", "Возврат к старым способам")],
            "Глубина принятия",
            [("", "С помощью AI улучшил процесс"),
             ("", "Доля принятых рекомендаций"),
             ("", "Качество и скорость реальных решений"),
             ("", "Не возвращается к старому")])
        + punch("Правильный KPI — не «использовал AI», а «с помощью AI улучшил процесс»")
    )
    return wrap(48, "Метрики принятия", body)


def s50() -> str:
    # Bento: главная мысль крупно + 7 элементов системы обучения вокруг
    body = (
        H("AI-First обучающая система компании", "AI-First")
        + S("Компания, которая быстрее работает, быстрее учится и лучше управляет сложностью")
        + bento(
            big=("ph-fill ph-infinity",
                 "Ценность человека смещается",
                 "К суждению, смыслу, границам и ответственности. AI не обесценивает человека — он забирает операционную суету.",
                 "Финальный вывод"),
            smalls=[
                ("ph-fill ph-graduation-cap", "Академия"),
                ("ph-fill ph-chat-circle-text", "Обратная связь"),
                ("ph-fill ph-presentation", "Вебинары"),
                ("ph-fill ph-lightning", "Хакатоны"),
                ("ph-fill ph-scroll", "Регламенты"),
                ("ph-fill ph-brain", "Орг. память"),
                ("ph-fill ph-books", "Библиотека"),
                ("ph-fill ph-trophy", "Новая ценность"),
            ])
        + punch("Зрелая AI-first компания быстрее работает, быстрее учится и лучше управляет сложностью")
    )
    return wrap(49, "AI-First обучающая система", body)


def s51_test() -> str:
    body = (
        '<div class="relative z-10 w-full text-center">'
        '<div class="bg-solar/10 border border-solar/40 rounded-full px-4 py-1.5 md:py-2 mx-auto shadow-sm mb-4 md:mb-8 inline-block">'
        '<p class="text-solar font-bold uppercase tracking-widest text-[8px] md:text-sm m-0">Итог лекции</p></div>'
        '<h2 class="text-xl sm:text-3xl md:text-4xl lg:text-[50px] font-black mb-4 md:mb-6 tracking-tight leading-tight">'
        'Человеческая → Гибридная →<br><span class="text-solar font-black">AI-First компания</span></h2>'
        '<p class="text-white/70 font-medium text-[11px] md:text-base mb-6 md:mb-10 max-w-3xl mx-auto">AI меняет не процессы — он меняет саму компанию. Гибридная система — это спроектированное взаимодействие человека и машины.</p>'
        '<p class="text-[10px] md:text-sm font-bold uppercase tracking-widest text-white/50 mb-3 md:mb-5">Зрелая AI-first компания должна быть</p>'
        '<div class="grid grid-cols-2 md:grid-cols-4 gap-1.5 md:gap-2 mb-6 md:mb-10 w-full max-w-5xl mx-auto">'
        + ''.join(
            f'<div class="bg-white/10 p-2 md:p-2.5 rounded-xl text-center text-[10px] md:text-sm font-bold border border-white/20">{e(t)}</div>'
            for t in ["Гибридной", "Управляемой", "С чёткими границами", "С пересобранными ролями",
                      "С согласованными метриками", "С регулярным ритмом", "Обучающейся"])
        + '<div class="bg-solar text-black p-2 md:p-2.5 rounded-xl text-center text-[10px] md:text-sm font-black uppercase tracking-widest shadow-[0_0_15px_#35F0C7]">Этичной</div></div>'
        '<p class="text-[10px] md:text-sm font-bold uppercase tracking-widest text-white/50 mb-3">Проверьте понимание</p>'
        '<button id="open-quiz-btn" type="button" class="mt-2 md:mt-4 inline-flex items-center justify-center gap-2 md:gap-3 bg-solar text-black font-black text-sm md:text-xl px-6 md:px-10 py-3 md:py-5 rounded-full shadow-[0_0_30px_rgba(53,240,199,0.4)] hover:scale-105 transition-transform uppercase tracking-widest">'
        '<i class="ph-fill ph-graduation-cap text-lg md:text-2xl"></i>Пройти тест из 10 вопросов</button></div>'
    )
    return wrap(50, "Финальный — кнопка теста", body, dark=True)


# ============================== QUIZ =========================================
QUIZ = [
    {"q": "В чём главная идея лекции про AI-трансформацию компании?",
     "options": [
         "AI — это новый софт, который ускоряет существующие процессы",
         "AI меняет компанию организационно: роли, ответственность, метрики",
         "AI заменяет всех сотрудников",
         "AI — только инструмент для отдельных задач"],
     "correct": 1,
     "explanation": "AI меняет компанию не только технически, но и организационно — пересобираются роли, процессы, правила, обучение и показатели. Это не IT-проект, а управленческая трансформация."},
    {"q": "Что такое гибридная организация?",
     "options": [
         "Компания, в которой все процессы автоматизированы",
         "Компания, где AI заменил большинство сотрудников",
         "Компания, где человек и AI участвуют в одном процессе, но выполняют разные функции",
         "Компания, в которой AI применяется только в IT"],
     "correct": 2,
     "explanation": "Гибридная система — это компания, где человек задаёт цели, правила, отвечает за последствия, а AI анализирует данные, ищет закономерности и выполняет операции. Не замена человека, а правильное распределение работы."},
    {"q": "В каких четырёх зонах человек обязан оставаться главным?",
     "options": [
         "Постановка целей, рискованные решения, этика, ответственность",
         "Программирование, дизайн, маркетинг, продажи",
         "Анализ данных, мониторинг, рутина, отчётность",
         "HR, бухгалтерия, юр. отдел, операции"],
     "correct": 0,
     "explanation": "AI не должен решать, ради чего существует бизнес. Не должен принимать рискованные решения с серьёзными последствиями. Не должен подменять этический выбор. И не может нести ответственность вместо людей."},
    {"q": "Какие четыре режима самостоятельности AI существуют?",
     "options": [
         "Тестовый, продакшен, демо, отладочный",
         "Локальный, облачный, гибридный, кросс-доменный",
         "Только автоматический и только ручной",
         "AI предлагает / AI действует под контролем / AI действует сам / соавторство"],
     "correct": 3,
     "explanation": "Зрелая компания не использует один универсальный режим. Для рискованных задач — AI только предлагает. Для повторяемых — действует под контролем. В понятных сценариях с низкими рисками — самостоятельно. Для документов и стратегий — соавторство с человеком."},
    {"q": "Что значит «управление изменениями = управление границей»?",
     "options": [
         "Нужно поставить firewall между AI и пользователями",
         "Нужно ограничить доступ к AI только топ-менеджменту",
         "Нужно постоянно перепроектировать, что доверять AI, а что контролирует человек",
         "Нужно отделить AI-команду от остального бизнеса"],
     "correct": 2,
     "explanation": "Главная задача — не «что автоматизировать», а провести границу между человеком и AI. По мере роста доверия она меняется. Управление изменениями — это постоянное проектирование ответственности."},
    {"q": "Какие новые роли появляются в гибридной компании?",
     "options": [
         "Только AI-разработчик и data scientist",
         "Владелец процесса, архитектор автоматизации, бизнес-владелец, владелец риска, AI-чемпион",
         "Только IT-директор и CIO",
         "Только продакт-менеджер и UX-дизайнер"],
     "correct": 1,
     "explanation": "Старой ролевой модели недостаточно. Появляются зоны: кто владеет гибридным процессом, кто проектирует автоматизацию, кто отвечает за эффект, за риски, и кто помогает команде принять новый способ работы."},
    {"q": "Почему «эффект от AI не появляется сам»?",
     "options": [
         "Потому что модели всегда плохо обучены",
         "Потому что компания внедряет технологию, но не меняет роли, метрики и процессы",
         "Потому что не хватает GPU",
         "Потому что AI слишком дорогой"],
     "correct": 1,
     "explanation": "Инструмент появился, агент запущен, пилот проведён — но если роли, KPI и процессы остались прежними, сотрудники не понимают, за что отвечают они, а за что AI. Эффект нужно не ждать, а проектировать."},
    {"q": "Какие показатели правильны для гибридной системы?",
     "options": [
         "Только количество запросов к AI",
         "Только количество выполненных задач",
         "Эффект: скорость решений, меньше ошибок, стабильность, экономика",
         "Только время работы сотрудника"],
     "correct": 2,
     "explanation": "Старые метрики измеряли усилия — сколько часов и задач. Важнее не «сколько мы сделали», а «насколько лучше стала работать система»: скорость, ошибки, стабильность, выручка."},
    {"q": "Что главное в работе с сопротивлением сотрудников?",
     "options": [
         "Подавить приказом «теперь все используют AI»",
         "Признать сопротивление, дать ясность, показать пользу, дать практику, включить руководителей",
         "Уволить тех, кто сопротивляется",
         "Игнорировать — само пройдёт"],
     "correct": 1,
     "explanation": "Сопротивление — нормальная реакция живой системы. Главный вопрос сотрудника: «что изменится для меня?». Без честного ответа на него — формальное согласие, но работа по-старому."},
    {"q": "В чём правильный KPI использования AI?",
     "options": [
         "Количество запросов к AI в день",
         "Количество сотрудников с доступом",
         "Размер бюджета на AI",
         "«С помощью AI улучшил процесс» — глубина принятия, влияние на результат"],
     "correct": 3,
     "explanation": "Если поощрять количество запросов — получаем имитацию активности. Правильный KPI — не «использовал AI», а «с помощью AI улучшил процесс»: меняется ли поведение, принимаются ли рекомендации, влияет ли AI на реальные решения."},
]


# ============================== FOOTER =======================================
def build_footer() -> str:
    quiz_json = json.dumps(QUIZ, ensure_ascii=False, indent=8).replace("\n", "\n        ")
    return r"""
<!-- =================== SLIDES END =================== -->

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
    document.addEventListener('DOMContentLoaded', () => {
        const totalSlides = document.querySelectorAll('.slide-container').length;
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

        function videoSrcFor(slideIdx) {
            const el = document.getElementById(`slide-${slideIdx}`);
            if (el && el.classList.contains('bg-black')) return null;
            return `videos/${slideIdx + 1}.mp4`;
        }

        function triggerOverlayAutoFade() {
            if (!videoOverlay || !video) return;
            videoOverlay.classList.remove('opacity-0');
            clearTimeout(overlayTimeout);
            if (!video.paused) overlayTimeout = setTimeout(() => videoOverlay.classList.add('opacity-0'), 1500);
        }

        function setupVideoEvents() {
            video.addEventListener('ended', () => { if (currentSlide < totalSlides - 1) nextSlide(); });
            video.addEventListener('play', () => {
                if (videoIcon) videoIcon.className = 'ph-fill ph-pause-circle text-4xl md:text-6xl drop-shadow-md';
                if (videoOverlay) videoOverlay.classList.add('opacity-0');
                clearTimeout(overlayTimeout);
                if (videoLoader) videoLoader.classList.add('opacity-0');
            });
            video.addEventListener('playing', () => { if (videoLoader) videoLoader.classList.add('opacity-0'); });
            video.addEventListener('waiting', () => { if (videoLoader) videoLoader.classList.remove('opacity-0'); });
            video.addEventListener('pause', () => {
                if (videoIcon) videoIcon.className = 'ph-fill ph-play-circle text-4xl md:text-6xl drop-shadow-md';
                if (videoOverlay) videoOverlay.classList.remove('opacity-0');
                clearTimeout(overlayTimeout);
            });
            video.addEventListener('error', () => { if (videoLoader) videoLoader.classList.add('opacity-0'); showPlayPrompt(); });
        }

        function updateProgress() {
            if (!progressBar) return;
            progressBar.style.width = `${((currentSlide + 1) / totalSlides) * 100}%`;
        }
        function showLoaderInstant() {
            if (!videoLoader) return;
            videoLoader.style.transition = 'none';
            videoLoader.classList.remove('opacity-0');
            void videoLoader.offsetWidth;
            videoLoader.style.transition = '';
        }
        function hideLoader() { if (videoLoader) videoLoader.classList.add('opacity-0'); }
        function showPlayPrompt() {
            if (videoOverlay) videoOverlay.classList.remove('opacity-0');
            if (videoIcon) videoIcon.className = 'ph-fill ph-play-circle text-4xl md:text-6xl drop-shadow-md';
        }

        function switchVideo(slideIdx) {
            if (!video) return;
            const bubble = document.getElementById('video-bubble');
            const targetSrc = videoSrcFor(slideIdx);
            if (targetSrc === null) {
                if (bubble) bubble.style.display = 'none';
                try { video.pause(); } catch (e) {}
                loadedIdx = slideIdx;
                return;
            } else if (bubble && bubble.style.display === 'none') {
                bubble.style.display = 'block';
            }
            if (slideIdx === loadedIdx) return;
            showLoaderInstant();
            if (videoOverlay) videoOverlay.classList.add('opacity-0');
            video.src = targetSrc;
            loadedIdx = slideIdx;
            const playPromise = video.play();
            if (playPromise && playPromise.catch) {
                playPromise.then(() => { hideLoader(); triggerOverlayAutoFade(); })
                           .catch(() => { hideLoader(); showPlayPrompt(); });
            }
        }

        window.updateSlides = function() {
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
            const navPrev = document.getElementById('nav-prev');
            const navNext = document.getElementById('nav-next');
            if (navPrev) navPrev.style.display = currentSlide === 0 ? 'none' : 'flex';
            if (navNext) navNext.style.display = currentSlide === totalSlides - 1 ? 'none' : 'flex';
            if (!exportMode) switchVideo(currentSlide);
        };
        window.nextSlide = function() { if (currentSlide < totalSlides - 1) { currentSlide++; updateSlides(); } };
        window.prevSlide = function() { if (currentSlide > 0) { currentSlide--; updateSlides(); } };

        document.getElementById('start-overlay').addEventListener('click', function() {
            this.style.opacity = '0';
            setTimeout(() => this.style.display = 'none', 500);
            if (!exportMode) {
                document.getElementById('video-bubble').style.display = 'block';
                setupVideoEvents();
                video.muted = false;
                switchVideo(0);
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
            else if (e.key === 'ArrowLeft') prevSlide();
        });

        if (videoOverlay) {
            videoOverlay.addEventListener('click', (e) => {
                e.stopPropagation();
                if (video.paused) video.play().catch(() => showPlayPrompt());
                else video.pause();
            });
        }

        const bubble = document.getElementById('video-bubble');
        let isDragging = false, currentX = 0, currentY = 0, initialX = 0, initialY = 0, xOffset = 0, yOffset = 0;
        bubble.addEventListener("mousedown", dragStart);
        document.addEventListener("mouseup", () => isDragging = false);
        document.addEventListener("mousemove", drag);
        bubble.addEventListener("touchstart", dragStart, {passive: false});
        document.addEventListener("touchend", () => isDragging = false);
        document.addEventListener("touchmove", drag, {passive: false});
        function dragStart(e) {
            initialX = (e.type === "touchstart" ? e.touches[0].clientX : e.clientX) - xOffset;
            initialY = (e.type === "touchstart" ? e.touches[0].clientY : e.clientY) - yOffset;
            if (e.target === bubble || bubble.contains(e.target)) isDragging = true;
        }
        function drag(e) {
            if (!isDragging) return;
            e.preventDefault();
            currentX = (e.type === "touchmove" ? e.touches[0].clientX : e.clientX) - initialX;
            currentY = (e.type === "touchmove" ? e.touches[0].clientY : e.clientY) - initialY;
            xOffset = currentX; yOffset = currentY;
            bubble.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
        }

        let swipeStartX = 0, swipeStartY = 0, swipeActive = false;
        document.addEventListener('touchstart', (e) => {
            if (bubble.contains(e.target)) { swipeActive = false; return; }
            const navPrev = document.getElementById('nav-prev');
            const navNext = document.getElementById('nav-next');
            if ((navPrev && navPrev.contains(e.target)) || (navNext && navNext.contains(e.target))) { swipeActive = false; return; }
            const qm = document.getElementById('quiz-modal');
            if (qm && !qm.classList.contains('hidden')) { swipeActive = false; return; }
            swipeStartX = e.touches[0].clientX;
            swipeStartY = e.touches[0].clientY;
            swipeActive = true;
        }, {passive: true});
        document.addEventListener('touchend', (e) => {
            if (!swipeActive) return;
            swipeActive = false;
            const dx = e.changedTouches[0].clientX - swipeStartX;
            const dy = e.changedTouches[0].clientY - swipeStartY;
            if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.4) {
                if (dx > 0) prevSlide(); else nextSlide();
            }
        }, {passive: true});

        if (exportMode) body.classList.add('pdf-export-mode');
        else updateSlides();

        // ==================== QUIZ ====================
        const quizQuestions = ___QUIZ_JSON___;

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

        function openQuiz() {
            quizIndex = 0; quizScore = 0; quizAnswered = false;
            quizModal.classList.remove('hidden');
            quizModal.classList.add('flex');
            quizQuestionBlock.classList.remove('hidden');
            quizQuestionBlock.classList.add('flex');
            quizResultBlock.classList.add('hidden');
            quizResultBlock.classList.remove('flex');
            renderQuestion();
            if (video && !video.paused) video.pause();
        }
        function closeQuiz() { quizModal.classList.add('hidden'); quizModal.classList.remove('flex'); }

        function renderQuestion() {
            quizAnswered = false;
            const cur = quizQuestions[quizIndex];
            quizProgress.textContent = `Вопрос ${quizIndex + 1} из ${quizQuestions.length}`;
            quizProgressBar.style.width = `${((quizIndex + 1) / quizQuestions.length) * 100}%`;
            quizQuestionText.textContent = cur.q;
            quizOptions.innerHTML = '';
            cur.options.forEach((opt, i) => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'quiz-option text-left bg-white/5 hover:bg-white/10 border border-white/10 rounded-[16px] md:rounded-2xl p-3 md:p-5 flex items-start gap-3 md:gap-4 transition-all text-white';
                btn.innerHTML = `
                    <span class="quiz-option-letter shrink-0 w-7 h-7 md:w-9 md:h-9 rounded-full border border-white/20 flex items-center justify-center text-[11px] md:text-sm font-black">${String.fromCharCode(65 + i)}</span>
                    <span class="quiz-option-text text-[12px] md:text-base font-medium leading-snug pt-0.5 md:pt-1">${opt}</span>
                `;
                btn.addEventListener('click', () => handleAnswer(i, btn));
                quizOptions.appendChild(btn);
            });
            quizExplanation.classList.add('hidden');
            quizNextBtn.classList.add('hidden');
        }

        function handleAnswer(chosenIdx, btnEl) {
            if (quizAnswered) return;
            quizAnswered = true;
            const cur = quizQuestions[quizIndex];
            const buttons = quizOptions.querySelectorAll('.quiz-option');
            buttons.forEach((b, i) => {
                b.disabled = true;
                b.classList.remove('hover:bg-white/10');
                if (i === cur.correct) {
                    b.classList.remove('bg-white/5', 'border-white/10');
                    b.classList.add('bg-solar/20', 'border-solar');
                    const letter = b.querySelector('.quiz-option-letter');
                    letter.classList.remove('border-white/20');
                    letter.classList.add('bg-solar', 'text-black', 'border-solar');
                } else if (i === chosenIdx) {
                    b.classList.remove('bg-white/5', 'border-white/10');
                    b.classList.add('bg-red-500/15', 'border-red-500/60');
                    const letter = b.querySelector('.quiz-option-letter');
                    letter.classList.remove('border-white/20');
                    letter.classList.add('bg-red-500/80', 'text-white', 'border-red-500');
                }
            });
            const isCorrect = chosenIdx === cur.correct;
            if (isCorrect) quizScore++;
            quizExplanation.classList.remove('hidden');
            if (isCorrect) {
                quizExplanationIcon.className = 'ph-fill ph-check-circle text-xl md:text-2xl text-solar';
                quizExplanationTitle.textContent = 'Верно!';
                quizExplanationTitle.className = 'font-black text-sm md:text-lg text-solar';
            } else {
                quizExplanationIcon.className = 'ph-fill ph-x-circle text-xl md:text-2xl text-red-400';
                quizExplanationTitle.textContent = 'Неверно — вот как правильно';
                quizExplanationTitle.className = 'font-black text-sm md:text-lg text-red-400';
            }
            quizExplanationText.textContent = cur.explanation;
            quizNextBtn.classList.remove('hidden');
            if (quizIndex === quizQuestions.length - 1) {
                quizNextBtn.innerHTML = 'Посмотреть результат <i class="ph-bold ph-arrow-right ml-1"></i>';
            } else {
                quizNextBtn.innerHTML = 'Далее <i class="ph-bold ph-arrow-right ml-1"></i>';
            }
        }

        function nextQuestion() {
            if (!quizAnswered) return;
            if (quizIndex < quizQuestions.length - 1) { quizIndex++; renderQuestion(); }
            else { showResults(); }
        }

        function showResults() {
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
            if (score >= 9) {
                title = 'Превосходно!';
                desc = 'Вы отлично понимаете, как устроена AI-трансформация компании: гибридная система, новые роли, границы автономности, согласованные метрики, работа с сопротивлением.';
                iconClass = 'ph-fill ph-trophy text-black';
                wrapClass = 'bg-solar';
            } else if (score >= 7) {
                title = 'Отличный результат';
                desc = 'Вы уверенно владеете ключевыми принципами AI-первой компании. Пересмотрите блоки про режимы автономности, метрики принятия и работу с сопротивлением.';
                iconClass = 'ph-fill ph-medal text-solar';
                wrapClass = 'bg-solar/20 border-2 border-solar';
            } else if (score >= 5) {
                title = 'Неплохо, но есть над чем поработать';
                desc = 'Базу вы уловили, но стоит освежить разницу между автоматизацией и изменением, новые роли, контрольные вопросы перед запуском AI-сценария и метрики гибридной системы.';
                iconClass = 'ph-fill ph-chart-line-up text-solar';
                wrapClass = 'bg-white/10 border-2 border-solar/50';
            } else {
                title = 'Стоит вернуться к материалу';
                desc = 'AI-трансформация — это не IT-проект, а пересборка ролей, процессов и ответственности. Пересмотрите ключевые слайды и попробуйте ещё раз.';
                iconClass = 'ph-fill ph-book-open text-solar';
                wrapClass = 'bg-white/10 border-2 border-white/20';
            }
            resultIconWrap.className = 'w-20 h-20 md:w-28 md:h-28 rounded-full flex items-center justify-center mb-5 md:mb-8 shadow-2xl ' + wrapClass;
            resultIcon.className = iconClass + ' text-4xl md:text-6xl';
            resultTitle.textContent = title;
            resultDesc.textContent = desc;
        }

        const openBtn = document.getElementById('open-quiz-btn');
        if (openBtn) openBtn.addEventListener('click', openQuiz);
        document.getElementById('quiz-close-btn').addEventListener('click', closeQuiz);
        document.getElementById('quiz-finish-btn').addEventListener('click', closeQuiz);
        document.getElementById('quiz-restart-btn').addEventListener('click', openQuiz);
        quizNextBtn.addEventListener('click', nextQuestion);
    });
</script>
</body>
</html>
""".replace("___QUIZ_JSON___", quiz_json)


def main() -> int:
    fns = [
        s1, s2, s3, s4, s5, s6, s7, s8, s9, s10,
        s11, s12, s13, s14, s15, s16, s17, s18, s19, s20,
        s21, s22, s23, s24, s25, s26, s27, s28, s29, s30,
        s31, s32, s33, s34, s35, s36, s37, s38, s39, s40,
        s41, s42, s43, s44, s45, s46, s47, s48, s49, s50,
        s51_test,
    ]
    parts = [HEAD]
    for fn in fns:
        parts.append(fn())
    parts.append(build_footer())
    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {OUT} with {len(fns)} slides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
