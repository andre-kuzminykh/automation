#!/usr/bin/env python3
"""Build new_8/index.html — Лекция 8 в стиле 1-в-1 с aisala/ai-agents-corp/6.

Каждый из 50 слайдов прорабатывается отдельно ниже в виде функции sN().
Финал — слайд 51 с кнопкой запуска теста и модальное окно с 10
вопросами по содержанию лекции.

Запуск:
    python3 new_8/scripts/build.py
"""
from __future__ import annotations

import html as _html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "new_8/index.html"


def e(s: str) -> str:
    return _html.escape(s, quote=True)


# ============================== HEAD =========================================
HEAD = r"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Лекция 8: Экономика AI-трансформации</title>
    <meta name="description" content="Лекция 8: AI-трансформация компании. Гибридная система, новые роли, метрики, governance, работа с сопротивлением.">
    <meta name="theme-color" content="#35F0C7">

    <meta property="og:type" content="website">
    <meta property="og:title" content="Лекция 8: Экономика AI-трансформации">
    <meta property="og:description" content="Как компания становится гибридной системой">
    <meta property="og:locale" content="ru_RU">
    <meta property="og:site_name" content="Anthropolis">

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Лекция 8: Экономика AI-трансформации">
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
def s1() -> str:
    # Title — Экономика AI-трансформации
    body = (
        '<div class="text-center w-full">'
        '<div class="flex justify-center mb-3 md:mb-10">'
        '<div class="bg-grayBase/30 border border-grayBase rounded-full '
        'px-3 py-1 md:px-4 md:py-2 shadow-sm">'
        '<p class="text-black font-bold uppercase tracking-widest text-[9px] md:text-sm m-0">Лекция 8: Экономика AI-трансформации</p>'
        '</div></div>'
        '<h1 class="text-xl sm:text-4xl md:text-5xl lg:text-[60px] font-black mb-2 md:mb-6 leading-tight tracking-tight text-black">'
        'Экономика <span class="text-solar">AI-трансформации</span></h1>'
        '<p class="text-black/70 font-bold text-[11px] md:text-2xl mb-2 md:mb-6 max-w-3xl mx-auto">Baseline · Юнит · FTE · TCO · ROI · Масштабирование</p>'
        '<p class="text-black/50 font-medium text-[10px] md:text-base mb-4 md:mb-12 max-w-3xl mx-auto">AI меняет деньги, время, качество и способность бизнеса расти — не процесс ради процесса</p>'
        + grid_cards([
            card_center("ph-fill ph-currency-circle-dollar", "Деньги"),
            card_center("ph-fill ph-clock-clockwise", "Время"),
            card_center("ph-fill ph-shield-check", "Качество"),
            card_center("ph-fill ph-trend-up", "Масштаб"),
            card_center("ph-fill ph-chart-pie-slice", "Unit econ"),
            card_center("ph-fill ph-calculator", "ROI", dark=True),
        ], "grid-cols-3 md:grid-cols-6")
        + punch("AI — инструмент перестройки экономики работы, а не самоцель")
        + '</div>'
    )
    state = "opacity-100 translate-y-0"
    return ('\n    <!-- =============================== -->\n'
            '    <!-- СЛАЙД 1: Титульный -->\n'
            '    <!-- =============================== -->\n'
            '    <div class="slide-container px-3 sm:px-6 md:px-12 ' + state + '" id="slide-0">\n'
            '        <div class="content-z text-center max-w-6xl">\n'
            + body[len('<div class="text-center w-full">'):-len('</div>')] + '\n'
            '        </div>\n    </div>\n')


def s2() -> str:
    body = (
        H("Цель лекции", "лекции")
        + S("Научиться смотреть на AI-проект глазами бизнеса и финансов")
        + label("Что вы будете уметь")
        + grid_cards([
            card_row("ph-fill ph-chart-line", "Считать baseline (As Is) и To Be"),
            card_row("ph-fill ph-clock", "Переводить часы в FTE"),
            card_row("ph-fill ph-coins", "Считать unit economics и TCO"),
            card_row("ph-fill ph-calculator", "Считать ROI, payback, NPV", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + punch("AI становится не экспериментом, а понятным инвестиционным кейсом")
    )
    return wrap(1, "Цель лекции", body)


def s3() -> str:
    body = (
        H("Карта экономики ИИ-трансформации", "Карта")
        + S("Логика проста, но её часто нарушают: начинают с модели, а надо — с процесса")
        + flow_horizontal([
            ("ph-fill ph-flow-arrow", "Процесс"),
            ("ph-fill ph-camera", "Baseline / As Is"),
            ("ph-fill ph-blueprint", "To Be"),
            ("ph-fill ph-chart-line-up", "Эффект"),
            ("ph-fill ph-wallet", "TCO"),
            ("ph-fill ph-calculator", "ROI"),
        ])
        + punch("Так AI-проект превращается в бизнес-кейс, а не в красивую демонстрацию")
    )
    return wrap(2, "Карта экономики AI-трансформации", body)


def s4() -> str:
    body = (
        H("Почему технология — плохая точка старта", "плохая точка старта")
        + S("«Сделаем агента» — звучит современно, но для бизнеса значит почти ничего")
        + two_panel(
            "Плохая постановка",
            [("ph-fill ph-x-circle", "Сделаем чат-бота для HR"),
             ("ph-fill ph-x-circle", "Внедрим агента"),
             ("ph-fill ph-x-circle", "Подключим LLM к процессу")],
            "Хорошая постановка",
            [("", "Сократим время заявки с 2 дней до 15 минут"),
             ("", "Снизим ручную нагрузку HR на 40%"),
             ("", "Уменьшим количество ошибок"),
             ("", "Цифры до · цифры после · разница")])
        + punch("Язык процесса, экономики и эффекта — а не язык технологии")
    )
    return wrap(3, "Почему технология — плохая точка старта", body)


def s5() -> str:
    body = (
        H("Правильный вопрос трансформации", "правильный вопрос")
        + S("Какую экономику процесса мы хотим изменить?")
        + quote_box(
            "Главный вопрос",
            "Где процесс дорогой, медленный, нестабильный или плохо масштабируется?",
            "Именно там AI даёт настоящий рычаг — перестраивает способ работы, а не автоматизирует один шаг")
        + label("Что потребляет любой процесс")
        + grid_cards([
            card_center("ph-fill ph-currency-circle-dollar", "Деньги"),
            card_center("ph-fill ph-clock", "Время"),
            card_center("ph-fill ph-eye", "Внимание"),
            card_center("ph-fill ph-brain", "Экспертизу"),
            card_center("ph-fill ph-lightning", "Энергию", dark=True),
        ], "grid-cols-2 md:grid-cols-5")
        + punch("Если AI не меняет эту экономику — он остаётся красивым инструментом, не трансформацией")
    )
    return wrap(4, "Правильный вопрос трансформации", body)


def s6() -> str:
    body = (
        H("Что создаёт бизнес-эффект", "бизнес-эффект")
        + S("Создаёт не сам факт внедрения AI, а изменённый процесс")
        + bento(
            big=("ph-fill ph-arrows-down-up",
                 "AI должен изменить минимум один ключевой параметр",
                 "Если процесс не изменился — AI остался инструментом, а не трансформацией. Эффект возникает только когда что-то стало другим.",
                 "Условие эффекта"),
            smalls=[
                ("ph-fill ph-lightning", "Скорость"),
                ("ph-fill ph-currency-circle-dollar", "Стоимость"),
                ("ph-fill ph-shield-check", "Качество"),
                ("ph-fill ph-trend-up", "Масштаб без штата"),
            ])
        + punch("Сравниваем не «стало хорошо», а конкретные параметры процесса")
    )
    return wrap(5, "Что создаёт бизнес-эффект", body)


def s7() -> str:
    body = (
        H("Процесс как объект экономики", "объект экономики")
        + S("Не «у нас сложная поддержка», а конкретный процесс с границами")
        + label("Конкретный процесс — это")
        + grid_cards([
            card_row("ph-fill ph-flag-banner", "Где он начинается"),
            card_row("ph-fill ph-flag-checkered", "Где он заканчивается"),
            card_row("ph-fill ph-users-three", "Кто в нём участвует"),
            card_row("ph-fill ph-list-checks", "Какие шаги выполняются"),
            card_row("ph-fill ph-package", "Какой результат на выходе", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + punch("Только очерченный процесс можно измерить — время, стоимость, ошибки")
    )
    return wrap(6, "Процесс как объект экономики", body)


def s8() -> str:
    body = (
        H("Юнит процесса", "Юнит")
        + S("Измеряемая единица работы — сравниваем «до» и «после» AI")
        + label("Юнит — это")
        + grid_cards([
            card_center("ph-fill ph-headset", "Обращение"),
            card_center("ph-fill ph-handshake", "Лид / сделка"),
            card_center("ph-fill ph-file-text", "Договор"),
            card_center("ph-fill ph-receipt", "Отчёт / платёж"),
            card_center("ph-fill ph-user-circle-plus", "Кандидат"),
            card_center("ph-fill ph-shopping-cart", "Заявка"),
            card_center("ph-fill ph-package", "Заказ"),
            card_center("ph-fill ph-check-square", "QA-операция", dark=True),
        ], "grid-cols-2 md:grid-cols-4")
        + punch("Юнит — точка перехода от общих слов к точной экономике процесса")
    )
    return wrap(7, "Юнит процесса", body)


def s9() -> str:
    body = (
        H("Зачем нужен юнит", "Зачем")
        + S("Без юнита нельзя честно посчитать эффект")
        + numbered([
            "Сколько юнитов в месяц проходит",
            "Сколько времени занимает один юнит",
            "Сколько он стоит",
            "Сколько ошибок возникает",
            "Сколько возвратов и переделок",
            "Сколько нарушений SLA",
        ])
        + punch("Было столько-то минут и рублей — стало столько-то. Точный язык.")
    )
    return wrap(8, "Зачем нужен юнит", body)


def s10() -> str:
    body = (
        H("Базовая экономика юнита", "Базовая экономика")
        + S("Стоимость процесса = стоимость одного юнита × количество юнитов")
        + mega_stat(
            big_text="3 000 000 ₽/мес",
            kicker="10 000 заявок × 300 ₽ — стоимость всего процесса",
            support=[
                ("ph-fill ph-coin", "1 юнит = 300 ₽"),
                ("ph-fill ph-stack", "10 000 в месяц"),
                ("ph-fill ph-equals", "Полная стоимость"),
                ("ph-fill ph-question", "Что если AI?"),
            ])
        + punch("Не ощущение и не жалоба — конкретная финансовая модель процесса")
    )
    return wrap(9, "Базовая экономика юнита", body)


def s11() -> str:
    body = (
        H("Как ИИ меняет стоимость юнита", "стоимость юнита")
        + S("Главный вопрос — не «что умеет агент», а сколько стоила операция до и после")
        + two_panel(
            "Было",
            [("ph-fill ph-currency-circle-dollar", "300 ₽ за обработку одной заявки"),
             ("ph-fill ph-user-gear", "Полностью ручная работа"),
             ("ph-fill ph-clock-counter-clockwise", "Время и внимание сотрудника")],
            "Стало",
            [("", "120 ₽ за обработку одной заявки"),
             ("", "Большая часть — агентом"),
             ("", "Человек только на сложных случаях"),
             ("", "Экономия 180 ₽ на каждой операции")])
        + punch("Здесь начинается экономика трансформации — снижение стоимости повторяемой единицы")
    )
    return wrap(10, "Как ИИ меняет стоимость юнита", body)


def s12() -> str:
    body = (
        H("Экономика процесса в месяц", "в месяц")
        + S("Эффект показываем не на одной операции, а на масштабе процесса")
        + mega_stat(
            big_text="−1 800 000 ₽/мес",
            kicker="10 000 заявок × экономия 180 ₽ = масштаб эффекта",
            support=[
                ("ph-fill ph-coin", "До: 3 000 000 ₽"),
                ("ph-fill ph-coins", "После: 1 200 000 ₽"),
                ("ph-fill ph-arrow-fat-down", "Разница: 1 800 000 ₽"),
                ("ph-fill ph-calendar", "Каждый месяц"),
            ])
        + punch("Маленькое улучшение на юните превращается в серьёзный бизнес-эффект")
    )
    return wrap(11, "Экономика процесса в месяц", body)


def s13() -> str:
    body = (
        H("As Is как финансовый baseline", "финансовый baseline")
        + S("As Is — не схема, а точка отсчёта для измерения эффекта")
        + two_panel(
            "Слабый As Is",
            [("ph-fill ph-x-circle", "Красивая блок-схема"),
             ("ph-fill ph-x-circle", "Описание шагов словами"),
             ("ph-fill ph-x-circle", "«Стало лучше» без чисел")],
            "Финансовый baseline",
            [("", "Сколько процесс стоит сейчас"),
             ("", "Сколько времени занимает"),
             ("", "Сколько ошибок создаёт"),
             ("", "От какой базы считаем эффект")])
        + punch("Бизнесу нужно: насколько лучше и от какой базы")
    )
    return wrap(12, "As Is = финансовый baseline", body)


def s14() -> str:
    body = (
        H("Что входит в As Is", "Что входит")
        + S("Не только последовательность шагов, но и реальная механика работы")
        + grid_cards([
            card_row("ph-fill ph-users-three", "Кто участвует"),
            card_row("ph-fill ph-hand-grabbing", "Какие действия вручную"),
            card_row("ph-fill ph-database", "Какие данные используются"),
            card_row("ph-fill ph-clock-clockwise", "Где задержки"),
            card_row("ph-fill ph-warning", "Где ошибки и возвраты"),
            card_row("ph-fill ph-stamp", "Какие согласования замедляют", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + punch("Хороший As Is показывает, почему процесс стоит дорого или работает медленно")
    )
    return wrap(13, "Что входит в As Is", body)


def s15() -> str:
    body = (
        H("Что собрать для baseline", "Что собрать")
        + S("Baseline должен быть числовым — иначе улучшения превратятся в ощущения")
        + numbered([
            "Объём операций (юнитов в месяц)",
            "Среднее время на один юнит",
            "Медиана времени",
            "Роли участников и их доля",
            "Количество ошибок и возвратов",
            "Просрочки и нарушения SLA",
            "Стоимость часа сотрудников",
        ])
        + punch("Чем точнее baseline, тем убедительнее расчёт эффекта AI")
    )
    return wrap(14, "Что собрать для baseline", body)


def s16() -> str:
    body = (
        H("Почему важна медиана", "медиана")
        + S("Среднее часто обманывает — несколько сложных кейсов искажают картину")
        + two_panel(
            "Среднее",
            [("ph-fill ph-chart-bar", "Чувствительно к выбросам"),
             ("ph-fill ph-warning", "Сложные кейсы тянут вверх"),
             ("ph-fill ph-chart-line", "Показывает общую нагрузку")],
            "Медиана",
            [("", "Устойчива к выбросам"),
             ("", "Показывает типичную операцию"),
             ("", "Реальный стандарт процесса"),
             ("", "Лучше для оценки эффекта AI")])
        + punch("Нужны оба: среднее — про общую нагрузку, медиана — про типичную операцию")
    )
    return wrap(15, "Почему важна медиана", body)


def s17() -> str:
    body = (
        H("Ручные часы до ИИ", "Ручные часы")
        + S("Простая формула: объём × минут на юнит ÷ 60")
        + mega_stat(
            big_text="333 ч/мес",
            kicker="1 000 заявок × 20 минут ÷ 60 = ручная нагрузка процесса",
            support=[
                ("ph-fill ph-stack", "1 000 заявок"),
                ("ph-fill ph-hourglass-medium", "20 минут / шт"),
                ("ph-fill ph-divide", "÷ 60"),
                ("ph-fill ph-clock", "333 часа"),
            ])
        + punch("Не «команда перегружена», а конкретный объём человеческого времени")
    )
    return wrap(16, "Ручные часы до AI", body)


def s18() -> str:
    body = (
        H("Стоимость текущего процесса", "Стоимость процесса")
        + S("Часы переводим в деньги: трудозатраты × стоимость часа")
        + flow_horizontal([
            ("ph-fill ph-clock", "Часы / мес"),
            ("ph-fill ph-x", "×"),
            ("ph-fill ph-coins", "Стоимость часа"),
            ("ph-fill ph-equals", "="),
            ("ph-fill ph-currency-circle-dollar", "Стоимость процесса"),
        ])
        + emphasis_black("Без денежной оценки AI-проект остаётся разговором про удобство")
        + punch("С деньгами обсуждаем эффект, окупаемость и приоритет внедрения")
    )
    return wrap(17, "Стоимость текущего процесса", body)


def s19() -> str:
    body = (
        H("To Be как новая модель процесса", "To Be")
        + S("Не «появился агент» — а как изменилась логика работы")
        + bento(
            big=("ph-fill ph-blueprint",
                 "Новая операционная модель",
                 "Человек не исчезает — его время переносится с рутины на проверку, ответственность и сложные решения. Это и есть качество To Be.",
                 "Главная идея"),
            smalls=[
                ("ph-fill ph-robot", "Что делает агент"),
                ("ph-fill ph-user-check", "Что остаётся человеку"),
                ("ph-fill ph-eye", "Где стоит контроль"),
                ("ph-fill ph-funnel", "Типовые vs исключения"),
            ])
        + punch("Хороший To Be — это рабочая модель, а не красивое обещание")
    )
    return wrap(18, "To Be — новая модель процесса", body)


def s20() -> str:
    body = (
        H("Что нельзя писать в To Be", "Что нельзя писать")
        + S("«AI автоматизирует процесс» — слабая формулировка, ничего не объясняет")
        + two_panel(
            "Так нельзя",
            [("ph-fill ph-x-circle", "AI автоматизирует процесс"),
             ("ph-fill ph-x-circle", "Внедрим LLM"),
             ("ph-fill ph-x-circle", "Будет работать быстрее")],
            "Так конкретно",
            [("", "Агент классифицирует запрос"),
             ("", "Достаёт данные из CRM/KB"),
             ("", "Готовит черновик"),
             ("", "Оценивает уверенность"),
             ("", "Сложные случаи → человек"),
             ("", "Фиксирует метрики")])
        + punch("Только конкретный To Be становится рабочей моделью")
    )
    return wrap(19, "Что нельзя писать в To Be", body)


def s21() -> str:
    body = (
        H("Стандартные кейсы и исключения", "стандартные · исключения")
        + S("Правильная архитектура: AI — рутина, человек — сложные и рискованные случаи")
        + two_panel(
            "AI — типовые",
            [("ph-fill ph-robot", "Классификация запросов"),
             ("ph-fill ph-database", "Достать данные"),
             ("ph-fill ph-file-text", "Подготовить результат"),
             ("ph-fill ph-lightning", "Быстро, дёшево, повторяемо")],
            "Человек — сложные",
            [("", "Спорные кейсы"),
             ("", "Высокие риски"),
             ("", "Этика и ответственность"),
             ("", "Решения с последствиями")])
        + punch("Не автоматизируем всё — AI берёт рутину, человек держит контроль")
    )
    return wrap(20, "Стандартные кейсы и исключения", body)


def s22() -> str:
    body = (
        H("Источники данных в To Be", "Источники данных")
        + S("Агент не должен работать в вакууме — без данных он генератор текста")
        + grid_cards([
            card_center("ph-fill ph-address-book", "CRM"),
            card_center("ph-fill ph-books", "База знаний"),
            card_center("ph-fill ph-file-text", "Документы"),
            card_center("ph-fill ph-user-circle", "История клиента"),
            card_center("ph-fill ph-file-cloud", "Спецификации"),
            card_center("ph-fill ph-plugs-connected", "Внутренние системы", dark=True),
        ], "grid-cols-2 md:grid-cols-3")
        + punch("С данными агент становится частью операционной системы бизнеса")
    )
    return wrap(21, "Источники данных в To Be", body)


def s23() -> str:
    body = (
        H("Метрики в To Be", "Метрики")
        + S("Новая модель должна автоматически измеряться")
        + numbered([
            "Время обработки одного юнита",
            "Доля операций, автоматизированных AI",
            "Доля исключений, ушедших к человеку",
            "Количество ошибок и переделок",
            "Соблюдение SLA",
            "Стоимость одного юнита",
        ])
        + punch("Метрики превращают AI из чёрного ящика в управляемый инструмент")
    )
    return wrap(22, "Метрики в To Be", body)


def s24() -> str:
    body = (
        H("Пример To Be-расчёта", "Пример")
        + S("Считаем не абстрактную автоматизацию, а оставшиеся человеческие часы")
        + concentric_layers([
            "800 типовых заявок × 2 мин = 26,7 часа",
            "200 нестандартных × 12 мин = 40 часов",
            "Итого: 66,7 часа человеческой работы в месяц",
        ])
        + emphasis_black("До: 333 часа · После: 66,7 часа · Снижение в 5 раз")
        + punch("Конкретный расчёт — основа разговора с финансами")
    )
    return wrap(23, "Пример To Be-расчёта", body)


def s25() -> str:
    body = (
        H("Сравнение As Is и To Be", "As Is и To Be")
        + S("Экономика AI становится видимой только в сравнении")
        + mega_stat(
            big_text="−266,3 ч/мес",
            kicker="333 часа было · 66,7 осталось · разница — это эффект",
            support=[
                ("ph-fill ph-clock-counter-clockwise", "Было: 333 ч"),
                ("ph-fill ph-clock", "Стало: 66,7 ч"),
                ("ph-fill ph-arrow-fat-down", "−266,3 ч"),
                ("ph-fill ph-trend-down", "−80%"),
            ])
        + punch("Первый измеримый эффект — конкретное снижение трудоёмкости")
    )
    return wrap(24, "Сравнение As Is и To Be", body)


def s26() -> str:
    body = (
        H("Роль человека после ИИ", "Роль человека")
        + S("Человек не исчезает — меняется его задача")
        + bento(
            big=("ph-fill ph-user-focus",
                 "Хорошая AI-трансформация — не убирает человека, а усиливает",
                 "Освобождает от рутины и переносит внимание на контроль, качество, исключения и управленческие решения.",
                 "Принцип усиления"),
            smalls=[
                ("ph-fill ph-eye", "Проверка сложных случаев"),
                ("ph-fill ph-warning-octagon", "Работа с исключениями"),
                ("ph-fill ph-gavel", "Принятие решений"),
                ("ph-fill ph-pencil-line", "Улучшение правил агента"),
            ])
        + punch("Время с рутины переезжает на контроль, ответственность и сложные решения")
    )
    return wrap(25, "Роль человека после AI", body)


def s27() -> str:
    body = (
        H("Экономия времени ≠ экономия денег", "≠ экономия денег")
        + S("«Высвободили 266 часов» — финансовый директор спросит: где это в бюджете?")
        + quote_box(
            "Главная ошибка",
            "Автоматически переводить часы в прибыль",
            "Если headcount и зарплаты не изменились — это ещё не hard savings, а что-то другое")
        + label("Три варианта правильно назвать")
        + grid_cards([
            card_row("ph-fill ph-battery-charging", "Высвобождённая мощность"),
            card_row("ph-fill ph-user-minus", "Отказ от будущего найма"),
            card_row("ph-fill ph-arrow-fat-down", "Реальная экономия бюджета", dark=True),
        ], "grid-cols-1 md:grid-cols-3")
        + punch("Эффект важный, но его нужно правильно классифицировать")
    )
    return wrap(26, "Экономия времени ≠ экономия денег", body)


def s28() -> str:
    body = (
        H("Три типа эффекта", "Три типа")
        + S("Чтобы расчётам доверяли, эффект AI нужно правильно классифицировать")
        + three_panel(
            "Hard savings",
            [("ph-fill ph-arrow-fat-down", "Расходы реально исчезли из бюджета")],
            "Cost avoidance",
            [("ph-fill ph-no-smoking", "Избежали будущих расходов — не наняли")],
            "Capacity value",
            [("ph-fill ph-battery-charging", "Время переключилось на более ценные задачи")])
        + punch("У каждого типа своя логика и своя финансовая доказательность")
    )
    return wrap(27, "Три типа эффекта", body)


def s29() -> str:
    body = (
        H("Hard savings", "Hard savings")
        + S("Самый сильный и понятный для финансов тип — расходы реально исчезли")
        + label("Когда это происходит")
        + grid_cards([
            card_row("ph-fill ph-handshake", "Сократили внешних подрядчиков"),
            card_row("ph-fill ph-x", "Не продлили платный контракт"),
            card_row("ph-fill ph-user-minus", "Уменьшили количество ставок"),
            card_row("ph-fill ph-trash", "Закрыли платный ручной процесс", dark=True),
        ], "grid-cols-1 md:grid-cols-2")
        + punch("Hard savings легче всего защищать — реальное изменение затрат")
    )
    return wrap(28, "Hard savings", body)


def s30() -> str:
    body = (
        H("Формула hard savings", "Формула")
        + S("Сокращённые FTE × полная годовая стоимость одного FTE")
        + mega_stat(
            big_text="3 744 000 ₽/год",
            kicker="2 FTE × 1 872 000 ₽ = годовой эффект",
            support=[
                ("ph-fill ph-user-minus", "−2 FTE"),
                ("ph-fill ph-x", "×"),
                ("ph-fill ph-user-circle", "1 872 000 ₽ / FTE"),
                ("ph-fill ph-calendar", "В год"),
            ])
        + emphasis_black("Считаем полную стоимость FTE — не только оклад, а все накладные")
        + punch("Для компании человек стоит дороже своего оклада")
    )
    return wrap(29, "Формула hard savings", body)


def s31() -> str:
    body = (
        H("Cost avoidance", "Cost avoidance")
        + S("Предотвращение будущих расходов — не сокращение текущих")
        + two_panel(
            "Старая модель роста",
            [("ph-fill ph-stack", "10 000 заявок → 13 000"),
             ("ph-fill ph-user-plus", "Пришлось бы нанять +3 операторов"),
             ("ph-fill ph-currency-circle-dollar", "Постоянный рост бюджета")],
            "С AI",
            [("", "Та же команда обрабатывает 13 000"),
             ("", "Найма не было"),
             ("", "Бюджет не вырос"),
             ("", "Масштабируемся без расширения штата")])
        + punch("Для растущего бизнеса cost avoidance важнее прямой экономии")
    )
    return wrap(30, "Cost avoidance", body)


def s32() -> str:
    body = (
        H("Формула cost avoidance", "Формула")
        + S("Избежавшие наймы × полная годовая стоимость FTE")
        + mega_stat(
            big_text="5 616 000 ₽/год",
            kicker="3 не-нанятых × 1 872 000 ₽ = предотвращённые расходы",
            support=[
                ("ph-fill ph-user-plus", "−3 найма"),
                ("ph-fill ph-x", "×"),
                ("ph-fill ph-coins", "1 872 000 ₽"),
                ("ph-fill ph-trend-up", "/ год роста"),
            ])
        + emphasis_black("Не сокращение текущего бюджета, а предотвращение его будущего роста")
        + punch("Для быстрорастущих компаний — иногда важнее прямой экономии")
    )
    return wrap(31, "Формула cost avoidance", body)


def s33() -> str:
    body = (
        H("Capacity value", "Capacity value")
        + S("Высвобождённая мощность — люди остались, бюджет тот же, но время перераспределено")
        + bento(
            big=("ph-fill ph-battery-charging",
                 "Само по себе освобождённое время ещё не создаёт ценность",
                 "Ценность появляется только когда время реально перенаправлено в работу, дающую бизнес-результат.",
                 "Важное условие"),
            smalls=[
                ("ph-fill ph-user-focus", "Клиенты"),
                ("ph-fill ph-chart-pie-slice", "Аналитика"),
                ("ph-fill ph-stack-plus", "Закрытие backlog"),
                ("ph-fill ph-shield-check", "Улучшение качества"),
            ])
        + punch("Не переключили → ценности нет. Переключили → ценность есть")
    )
    return wrap(32, "Capacity value", body)


def s34() -> str:
    body = (
        H("Формула capacity value", "Формула")
        + S("Часы × стоимость часа × utilization factor (реалистичная доля)")
        + mega_stat(
            big_text="≈ 119 835 ₽/мес",
            kicker="266,3 ч × 900 ₽ × 50% utilization = ценность мощности",
            support=[
                ("ph-fill ph-clock", "266,3 ч"),
                ("ph-fill ph-coins", "900 ₽/ч"),
                ("ph-fill ph-percent", "50% utilization"),
                ("ph-fill ph-shield-check", "Консервативно"),
            ])
        + punch("Зрелый подход: не завышаем эффект, показываем реалистичную ценность")
    )
    return wrap(33, "Формула capacity value", body)


def s35() -> str:
    body = (
        H("FTE как язык бизнеса", "FTE")
        + S("Часы → FTE: эквивалент полной ставки, понятнее для управленцев")
        + two_panel(
            "Менее убедительно",
            [("ph-fill ph-clock", "«Сэкономили 266 часов в месяц»"),
             ("ph-fill ph-question", "Сколько это в людях?"),
             ("ph-fill ph-question", "В бюджете?")],
            "Сильнее",
            [("", "«Снизили трудоёмкость процесса на 1,5 FTE»"),
             ("", "Понятный масштаб"),
             ("", "Финансовый язык"),
             ("", "Готовый аргумент для решения")])
        + punch("Формула: годовая экономия часов ÷ годовой фонд рабочего времени")
    )
    return wrap(34, "FTE как язык бизнеса", body)


def s36() -> str:
    body = (
        H("Пример FTE", "Пример")
        + S("Считаем экономию через эквивалент полной ставки")
        + mega_stat(
            big_text="≈ 1,54 FTE",
            kicker="266,3 ч/мес × 12 ÷ 2 080 ч = FTE-эквивалент",
            support=[
                ("ph-fill ph-clock", "266,3 ч/мес"),
                ("ph-fill ph-calendar", "× 12 = 3 195,6 ч/год"),
                ("ph-fill ph-divide", "÷ 2 080 ч"),
                ("ph-fill ph-user-circle", "1,54 FTE"),
            ])
        + emphasis_black("Не «уволили 1,5 человека», а «снизили трудоёмкость процесса на 1,5 FTE»")
        + punch("Зрелая управленческая формулировка — корректный язык для бизнеса")
    )
    return wrap(35, "Пример FTE", body)


def s37() -> str:
    body = (
        H("Fully loaded cost", "Fully loaded cost")
        + S("Сотрудник стоит дороже оклада — нужна полная стоимость")
        + label("Из чего складывается")
        + grid_cards([
            card_center("ph-fill ph-currency-circle-dollar", "Зарплата"),
            card_center("ph-fill ph-bank", "Налоги · взносы"),
            card_center("ph-fill ph-trophy", "Бонусы · бенефиты"),
            card_center("ph-fill ph-laptop", "Техника · софт"),
            card_center("ph-fill ph-building-office", "Рабочее место"),
            card_center("ph-fill ph-graduation-cap", "Обучение"),
            card_center("ph-fill ph-users", "HR · администрирование"),
            card_center("ph-fill ph-stack", "Накладные", dark=True),
        ], "grid-cols-2 md:grid-cols-4")
        + punch("AI меняет реальную стоимость работы для компании — её и считаем")
    )
    return wrap(36, "Fully loaded cost", body)


def s38() -> str:
    body = (
        H("Стоимость часа", "Стоимость часа")
        + S("От часов к деньгам — считаем полную стоимость часа")
        + step_progression([
            ("Шаг 1", "120 000 ₽/мес × 12 = 1 440 000 ₽/год (оклад)", "ph-fill ph-currency-circle-dollar"),
            ("Шаг 2", "× 1,3 (коэф. полной стоимости) = 1 872 000 ₽/год", "ph-fill ph-stack-plus"),
            ("Шаг 3", "÷ 2 080 рабочих часов = 900 ₽/час", "ph-fill ph-divide"),
            ("Шаг 4", "Финансовая база для оценки эффекта AI", "ph-fill ph-flag-checkered"),
        ])
        + punch("Теперь оцениваем сколько стоит ручная работа и сколько мощности высвобождает AI")
    )
    return wrap(37, "Стоимость часа", body)


def s39() -> str:
    body = (
        H("Unit economics процесса", "Unit economics")
        + S("Руководителю проще понять эффект на одной операции, чем общую цифру")
        + mega_stat(
            big_text="−60% на юните",
            kicker="Было 300 ₽ — стало 120 ₽ за операцию",
            support=[
                ("ph-fill ph-arrow-left", "Было: 300 ₽"),
                ("ph-fill ph-arrow-right", "Стало: 120 ₽"),
                ("ph-fill ph-arrow-fat-down", "−180 ₽"),
                ("ph-fill ph-percent", "−60%"),
            ])
        + punch("Чем больше повторяемых операций — тем сильнее эффект малого снижения")
    )
    return wrap(38, "Unit economics процесса", body)


def s40() -> str:
    body = (
        H("Throughput", "Throughput")
        + S("AI меняет не только стоимость, но и пропускную способность команды")
        + mega_stat(
            big_text="+150% производительности",
            kicker="Было: 1 000 операций / чел. Стало: 2 500 / чел",
            support=[
                ("ph-fill ph-users-three", "10 человек"),
                ("ph-fill ph-stack", "Было: 10 000"),
                ("ph-fill ph-arrow-fat-up", "Стало: 25 000"),
                ("ph-fill ph-trend-up", "+150% throughput"),
            ])
        + emphasis_black("Главный вопрос: не «сколько нанять», а «какой объём обработаем существующей командой»")
        + punch("AI = способность масштабироваться без пропорционального роста штата")
    )
    return wrap(39, "Throughput", body)


def s41() -> str:
    body = (
        H("Ошибки и переделки", "Качество")
        + S("Ошибка в бизнес-процессе почти никогда не стоит ноль")
        + bento(
            big=("ph-fill ph-warning-octagon",
                 "AI-эффект нельзя считать только через скорость и стоимость",
                 "Если после внедрения стало меньше ошибок, возвратов и переделок — это тоже экономический результат, который переводится в деньги.",
                 "Экономика качества"),
            smalls=[
                ("ph-fill ph-magnifying-glass", "Найти ошибку"),
                ("ph-fill ph-pencil-line", "Исправить · пересогласовать"),
                ("ph-fill ph-clock-countdown", "Нарушение SLA"),
                ("ph-fill ph-shield-warning", "Регуляторный риск"),
            ])
        + punch("Меньше ошибок = меньше скрытых расходов и больше доверия клиентов")
    )
    return wrap(40, "Ошибки и переделки", body)


def s42() -> str:
    body = (
        H("Формула экономии на ошибках", "Формула")
        + S("Объём × снижение доли ошибок × стоимость одной ошибки")
        + mega_stat(
            big_text="100 000 ₽/мес",
            kicker="1 000 операций × 5 п.п. × 2 000 ₽ = экономия на ошибках",
            support=[
                ("ph-fill ph-stack", "1 000 операций"),
                ("ph-fill ph-trend-down", "−5 п.п. ошибок"),
                ("ph-fill ph-coins", "× 2 000 ₽ / ошибка"),
                ("ph-fill ph-arrow-fat-down", "= 100 000 ₽"),
            ])
        + emphasis_black("Если стоимость ошибки неизвестна — считаем 3 сценария: консерв · базовый · критический")
        + punch("Качество — измеримая экономическая величина")
    )
    return wrap(41, "Формула экономии на ошибках", body)


def s43() -> str:
    body = (
        H("Revenue uplift", "Revenue uplift")
        + S("AI создаёт не только экономию, но и дополнительную выручку")
        + flow_horizontal([
            ("ph-fill ph-user-plus", "Лид"),
            ("ph-fill ph-robot", "AI квалифицирует"),
            ("ph-fill ph-envelope-simple", "Персональный оффер"),
            ("ph-fill ph-arrow-up-right", "Следующий шаг"),
            ("ph-fill ph-trend-up", "Рост конверсии"),
        ])
        + punch("Считаем прирост бизнес-результата относительно baseline, а не сокращение затрат")
    )
    return wrap(42, "Revenue uplift", body)


def s44() -> str:
    body = (
        H("Валовая маржа", "Валовая маржа")
        + S("Не остановиться на красивой цифре оборота — финансам важна маржа")
        + mega_stat(
            big_text="+400 000 ₽/мес",
            kicker="1 000 лидов × +1 п.п. конверсии × 100 000 ₽ × 40% маржи",
            support=[
                ("ph-fill ph-user-plus", "1 000 лидов"),
                ("ph-fill ph-percent", "+1 п.п. конверсии"),
                ("ph-fill ph-coins", "Чек 100 000 ₽"),
                ("ph-fill ph-chart-pie-slice", "Маржа 40%"),
            ])
        + punch("Эффект на выручке всегда переводим в валовую маржу — это язык финансов")
    )
    return wrap(43, "Валовая маржа", body)


def s45() -> str:
    body = (
        H("Клиентская экономика", "Клиентская экономика")
        + S("Если AI касается клиента — связываем его с CAC, LTV, маржей и payback")
        + three_panel(
            "CAC ↓",
            [("ph-fill ph-arrow-fat-down", "Автоматизация лидогенерации, квалификации, follow-up")],
            "LTV ↑",
            [("ph-fill ph-arrow-fat-up", "Персонализация · удержание · снижение churn")],
            "Маржа ↑",
            [("ph-fill ph-chart-pie-slice", "Падает cost-to-serve — стоимость обслуживания клиента")])
        + punch("AI не просто ускорил коммуникацию — он улучшил экономику клиента")
    )
    return wrap(44, "Клиентская экономика", body)


def s46() -> str:
    body = (
        H("TCO ИИ-решения", "TCO")
        + S("Полная стоимость владения — у AI-решения есть не только выгоды")
        + bento(
            big=("ph-fill ph-wallet",
                 "Зрелый бизнес-кейс показывает две стороны",
                 "Какой эффект мы получаем — и сколько стоит этот эффект обеспечить. Без второго первая цифра не имеет смысла.",
                 "Total Cost of Ownership"),
            smalls=[
                ("ph-fill ph-code", "Разработка"),
                ("ph-fill ph-plugs-connected", "Интеграции · API"),
                ("ph-fill ph-cloud", "Инфраструктура"),
                ("ph-fill ph-lock-key", "Безопасность"),
                ("ph-fill ph-eye", "Мониторинг"),
                ("ph-fill ph-headset", "Поддержка"),
                ("ph-fill ph-graduation-cap", "Обучение"),
                ("ph-fill ph-shield-check", "Governance"),
            ])
        + punch("Агент в проде — это не лицензия, а целая операционная инфраструктура")
    )
    return wrap(45, "TCO AI-решения", body)


def s47() -> str:
    body = (
        H("Чистый эффект", "Чистый эффект")
        + S("Нельзя показывать только валовую выгоду — нужен баланс")
        + mega_stat(
            big_text="+80 000 ₽/мес",
            kicker="300 000 ₽ экономии − 220 000 ₽ TCO = чистый эффект",
            support=[
                ("ph-fill ph-arrow-fat-up", "+300 000 ₽ эффект"),
                ("ph-fill ph-arrow-fat-down", "−220 000 ₽ TCO"),
                ("ph-fill ph-equals", "= 80 000 ₽"),
                ("ph-fill ph-shield-check", "Реалистичная цифра"),
            ])
        + emphasis_black("Такая честность повышает доверие к расчётам и защищает от завышенных ожиданий")
        + punch("Чистый эффект показывает, насколько проект полезен экономически")
    )
    return wrap(46, "Чистый эффект", body)


def s48() -> str:
    body = (
        H("ROI · Payback · NPV", "ROI · Payback · NPV")
        + S("AI-проект переводим в язык инвестиций — после расчёта выгод и TCO")
        + three_panel(
            "ROI",
            [("ph-fill ph-trend-up", "Насколько эффект превышает стоимость проекта")],
            "Payback",
            [("ph-fill ph-hourglass-medium", "За сколько месяцев проект окупится")],
            "NPV",
            [("ph-fill ph-clock-counter-clockwise", "Учитывает стоимость денег во времени")])
        + punch("На этом уровне AI перестаёт быть экспериментом и становится инвестиционным решением")
    )
    return wrap(47, "ROI · Payback · NPV", body)


def s49() -> str:
    body = (
        H("Масштабирование и кривая затрат", "кривая затрат")
        + S("Главный стратегический эффект AI — не часы, а изменение кривой затрат")
        + two_panel(
            "Старая модель",
            [("ph-fill ph-arrow-up-right", "Рост объёма ⇒ рост штата"),
             ("ph-fill ph-arrow-up-right", "Рост штата ⇒ рост бюджета"),
             ("ph-fill ph-equals", "Расходы линейно следуют за выручкой")],
            "Новая модель",
            [("", "Фиксированные AI-затраты"),
             ("", "Низкая переменная стоимость нового юнита"),
             ("", "Расходы растут медленнее выручки"),
             ("", "Настоящая масштабируемость")])
        + punch("Компания растёт быстрее, чем растут её расходы — это и есть результат AI")
    )
    return wrap(48, "Масштабирование и кривая затрат", body)


def s50() -> str:
    body = (
        H("Итоговая модель экономики ИИ-трансформации", "Итог")
        + S("Финальная мысль: результат — не агент, а новая экономика процесса")
        + bento(
            big=("ph-fill ph-target",
                 "AI ценен не когда работает, а когда меняет экономику",
                 "Стоимость, скорость, качество и способность бизнеса расти. Без этого AI остаётся технологией без бизнес-смысла.",
                 "Финальный вывод"),
            smalls=[
                ("ph-fill ph-flow-arrow", "Процесс"),
                ("ph-fill ph-camera", "As Is / baseline"),
                ("ph-fill ph-blueprint", "To Be"),
                ("ph-fill ph-chart-line-up", "Метрики"),
                ("ph-fill ph-chart-pie-slice", "Unit economics"),
                ("ph-fill ph-wallet", "TCO"),
                ("ph-fill ph-calculator", "ROI · Payback · NPV"),
                ("ph-fill ph-trend-up", "Масштабирование"),
            ])
        + punch("Это и есть зрелый AI-бизнес-кейс — на одной картинке")
    )
    return wrap(49, "Итоговая модель экономики AI-трансформации", body)


def s51_test() -> str:
    body = (
        '<div class="relative z-10 w-full text-center">'
        '<div class="bg-solar/10 border border-solar/40 rounded-full px-4 py-1.5 md:py-2 mx-auto shadow-sm mb-4 md:mb-8 inline-block">'
        '<p class="text-solar font-bold uppercase tracking-widest text-[8px] md:text-sm m-0">Итог лекции</p></div>'
        '<h2 class="text-xl sm:text-3xl md:text-4xl lg:text-[50px] font-black mb-4 md:mb-6 tracking-tight leading-tight">'
        'Процесс → Baseline → To Be →<br><span class="text-solar font-black">Бизнес-кейс</span></h2>'
        '<p class="text-white/70 font-medium text-[11px] md:text-base mb-6 md:mb-10 max-w-3xl mx-auto">AI-трансформация = новая экономика процесса. Юнит, FTE, hard savings, cost avoidance, capacity value, TCO, ROI, payback и кривая затрат.</p>'
        '<p class="text-[10px] md:text-sm font-bold uppercase tracking-widest text-white/50 mb-3 md:mb-5">Что вы теперь умеете</p>'
        '<div class="grid grid-cols-2 md:grid-cols-4 gap-1.5 md:gap-2 mb-6 md:mb-10 w-full max-w-5xl mx-auto">'
        + ''.join(
            f'<div class="bg-white/10 p-2 md:p-2.5 rounded-xl text-center text-[10px] md:text-sm font-bold border border-white/20">{e(t)}</div>'
            for t in ["Считать baseline", "Считать unit economics", "Переводить часы в FTE",
                      "Считать fully loaded cost", "Различать 3 типа эффекта",
                      "Считать TCO и чистый эффект", "Считать ROI · payback · NPV"])
        + '<div class="bg-solar text-black p-2 md:p-2.5 rounded-xl text-center text-[10px] md:text-sm font-black uppercase tracking-widest shadow-[0_0_15px_#35F0C7]">Защищать кейс</div></div>'
        '<p class="text-[10px] md:text-sm font-bold uppercase tracking-widest text-white/50 mb-3">Проверьте понимание</p>'
        '<button id="open-quiz-btn" type="button" class="mt-2 md:mt-4 inline-flex items-center justify-center gap-2 md:gap-3 bg-solar text-black font-black text-sm md:text-xl px-6 md:px-10 py-3 md:py-5 rounded-full shadow-[0_0_30px_rgba(53,240,199,0.4)] hover:scale-105 transition-transform uppercase tracking-widest">'
        '<i class="ph-fill ph-graduation-cap text-lg md:text-2xl"></i>Пройти тест из 10 вопросов</button></div>'
    )
    return wrap(50, "Финальный — кнопка теста", body, dark=True)


# ============================== QUIZ =========================================
QUIZ = [
    {"q": "Когда начинается настоящая AI-трансформация?",
     "options": [
         "Когда в компании появился агент или чат-бот",
         "Когда подключили модную нейросеть",
         "Когда меняется операционная модель: процесс, стоимость, время, качество, масштабируемость",
         "Когда команда обучена работе с AI"],
     "correct": 2,
     "explanation": "AI — не самоцель, а инструмент перестройки работы. Трансформация — это про изменение экономики процесса, а не про факт наличия технологии в компании."},
    {"q": "Что такое юнит процесса?",
     "options": [
         "Любое описание шага процесса словами",
         "Измеряемая единица работы, которую можно посчитать и сравнить до и после AI",
         "Команда, отвечающая за процесс",
         "Один человек в процессе"],
     "correct": 1,
     "explanation": "Юнит — это, например, одно обращение в поддержке, лид в продажах, договор у юристов, отчёт в финансах. Юнит делает процесс управляемым и измеримым."},
    {"q": "Что такое As Is как финансовый baseline?",
     "options": [
         "Красивая блок-схема текущего процесса",
         "Точка отсчёта с числами: сколько стоит, сколько времени, сколько ошибок",
         "Описание шагов словами",
         "Список участников процесса"],
     "correct": 1,
     "explanation": "As Is как baseline должен быть числовым: объём, среднее, медиана, ошибки, SLA, стоимость часа. Без этого любые улучшения превращаются в ощущения."},
    {"q": "Почему важна медиана, а не только среднее?",
     "options": [
         "Так принято в статистике",
         "Среднее легче считать",
         "Медиана показывает типичную операцию, а среднее искажают редкие сложные кейсы",
         "Медиана важнее всегда"],
     "correct": 2,
     "explanation": "Нужны оба показателя: среднее показывает общую нагрузку, медиана — реальный стандарт типичной операции. Без медианы baseline легко обмануть выбросами."},
    {"q": "Чем hard savings отличается от cost avoidance?",
     "options": [
         "Hard savings — это будущая экономия, cost avoidance — текущая",
         "Hard savings — расходы реально исчезли. Cost avoidance — избежали будущих расходов",
         "Это одно и то же, просто разные названия",
         "Hard savings относится только к ИТ-проектам"],
     "correct": 1,
     "explanation": "Hard savings — реальное сокращение текущего бюджета. Cost avoidance — предотвращение его будущего роста (например, не наняли при росте объёма). Это разная финансовая доказательность."},
    {"q": "Когда capacity value реально создаёт ценность?",
     "options": [
         "Сразу, как только высвободили часы",
         "Только когда время реально перенаправлено в работу, дающую бизнес-результат",
         "Когда люди стали меньше уставать",
         "Когда компания сократила штат"],
     "correct": 1,
     "explanation": "Само по себе освобождённое время ещё не ценность. Ценность появляется, когда это время реально превращается в полезный результат — поэтому формула включает utilization factor."},
    {"q": "Что такое fully loaded cost сотрудника?",
     "options": [
         "Только годовой оклад",
         "Оклад + бонусы",
         "Полная стоимость сотрудника: оклад, налоги, бенефиты, техника, софт, обучение, накладные",
         "Стоимость часа сотрудника"],
     "correct": 2,
     "explanation": "Для компании сотрудник стоит дороже оклада. AI меняет именно полную стоимость работы, поэтому считать экономику нужно через fully loaded cost, а не только через зарплату."},
    {"q": "Что показывает throughput после внедрения AI?",
     "options": [
         "Сколько ошибок в процессе",
         "Сколько денег экономит проект",
         "Сколько операций может обработать та же команда",
         "Сколько FTE сократили"],
     "correct": 2,
     "explanation": "Throughput меняет управленческий вопрос с «сколько людей нанять» на «какой объём мы можем обработать текущей командой, если правильно встроим AI». Это масштабируемость без роста штата."},
    {"q": "Почему нельзя показывать только валовую выгоду от AI?",
     "options": [
         "Финансы её не поймут",
         "У AI-решения есть TCO — без чистого эффекта расчёт нечестен",
         "Валовая выгода всегда завышена",
         "Это запрещено стандартами учёта"],
     "correct": 1,
     "explanation": "Если агент экономит 300 тыс, но эксплуатация стоит 220 тыс — чистый эффект 80 тыс. Только чистый эффект показывает, насколько проект реально полезен экономически."},
    {"q": "Главный стратегический эффект AI — это…",
     "options": [
         "Экономия часов работы",
         "Снижение ошибок",
         "Изменение кривой затрат: расходы растут медленнее объёма",
         "Замена сотрудников агентами"],
     "correct": 2,
     "explanation": "В старой модели рост объёма требует роста штата. AI добавляет фиксированные затраты, но снижает переменную стоимость нового юнита — поэтому компания растёт быстрее, чем её расходы."},
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
                desc = 'Вы отлично владеете экономикой AI-трансформации: baseline и юнит, As Is и To Be, FTE, fully-loaded cost, три типа эффекта, TCO, ROI и кривую затрат.';
                iconClass = 'ph-fill ph-trophy text-black';
                wrapClass = 'bg-solar';
            } else if (score >= 7) {
                title = 'Отличный результат';
                desc = 'Уверенно владеете языком экономики AI-проектов. Пересмотрите блоки про FTE, capacity value, чистый эффект и масштабирование кривой затрат.';
                iconClass = 'ph-fill ph-medal text-solar';
                wrapClass = 'bg-solar/20 border-2 border-solar';
            } else if (score >= 5) {
                title = 'Неплохо, но есть над чем поработать';
                desc = 'Базу уловили, но стоит освежить hard savings vs cost avoidance vs capacity value, fully-loaded cost, TCO и формулы unit economics.';
                iconClass = 'ph-fill ph-chart-line-up text-solar';
                wrapClass = 'bg-white/10 border-2 border-solar/50';
            } else {
                title = 'Стоит вернуться к материалу';
                desc = 'AI-кейс — это деньги, время, качество и масштаб. Пересмотрите слайды про baseline, юнит, FTE, TCO и ROI.';
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
