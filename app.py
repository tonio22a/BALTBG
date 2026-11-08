from flask import Flask, render_template, request, redirect, session, render_template_string, url_for, flash, abort
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from urllib.parse import urlparse
from datetime import datetime, timedelta
import hmac
import os
import re
import time as time_mod
import uuid
import sqlite3

QUESTIONS1 = [
    {
        "id": 0,
        "question": "Кто забил два гола в ворота «Зенита» в 9 туре РПЛ (2:3)?",
        "options": [
            "Брайан Хиль и Максим Петров",
            "Илья Петров и Максим Петров",
            "Чинонсо Оффор и Егор Голенков",
            "Илья Петров и Брайан Хиль"
        ],
        "answer": "Илья Петров и Брайан Хиль"
    },
    {
        "id": 1,
        "question": "В каком матче Талалаев получил первую дисквалификацию в этом сезоне?",
        "options": [
            "«Балтика» - «Зенит»",
            "«Балтика» - «Ростов»",
            "«Балтика» - «Рубин»",
            "«Балтика» - «Спартак»"
        ],
        "answer": "«Балтика» - «Рубин»"
    },
    {
        "id": 2,
        "question": "Был ли в этом сезоне РПЛ пенальти в ворота «Балтики»?",
        "options": [
            "Да",
            "Нет"
        ],
        "answer": "Нет"
    },
    {
        "id": 3,
        "question": "А в ворота соперника балтийцев?",
        "options": [
            "Да",
            "Нет"
        ],
        "answer": "Да"
    },
    {
        "id": 4,
        "question": "Каким достижением отметился нападающий «Балтики» Чинонсо Оффор?",
        "options": [
            "Самое быстрое удаление",
            "Самый быстрый первый гол сезона",
            "Самый длинный гол по расстоянию до ворот",
            "Гол через себя"
        ],
        "answer": "Самый быстрый первый гол сезона"
    },
    {
        "id": 5,
        "question": "Как «Балтика» сыграла со «Спартаком»?",
        "options": [
            "1:3 проигрыш",
            "1:1 ничья",
            "1:2 проигрыш",
            "ещё не играли"
        ],
        "answer": "1:2 проигрыш"
    },
    {
        "id": 6,
        "question": "У кого из Петровых больше голов в этом сезоне РПЛ?",
        "options": [
            "Максим Петров",
            "Илья Петров",
            "Одинаково",
            "Никто не забивал"
        ],
        "answer": "Одинаково"
    },
    {
        "id": 7,
        "question": "В каком туре «Балтика» впервые выиграла в этом сезоне?",
        "options": [
            "Первый тур",
            "Второй тур",
            "Третий тур",
            "Четвертый тур"
        ],
        "answer": "Второй тур"
    },
    {
        "id": 8,
        "question": "А кого из команд «Балтика» первой победило в сезоне?",
        "options": [
            "ЦСКА",
            "«Крылья Советов»",
            "«Локомотив»",
            "«Динамо»"
        ],
        "answer": "«Динамо»"
    },
    {
        "id": 9,
        "question": "Когда «Балтика» сыграла первый матч в сезоне?",
        "options": [
            "28 июля",
            "1 августа",
            "24 июля",
            "20 июля"
        ],
        "answer": "24 июля"
    },
    {
        "id": 10,
        "question": "Перед началом сезона наша команда сыграла товарищеский матч против команды РПЛ, кто был соперником балтийцев?",
        "options": [
            "«Зенит»",
            "«Оренбург»",
            "«Акрон»",
            "«Краснодар»"
        ],
        "answer": "«Краснодар»"
    },
    {
        "id": 11,
        "question": "Какая команда нанесла «Балтике» первое поражение в сезоне?",
        "options": [
            "ЦСКА",
            "«Спартак»",
            "«Зенит»",
            "«Факел»"
        ],
        "answer": "ЦСКА"
    },
    {
        "id": 12,
        "question": "Сколько голов забила «Балтика» после 90 минуты в этом сезоне?",
        "options": [
            "1",
            "3",
            "2",
            "ни одного"
        ],
        "answer": "2"
    },
    {
        "id": 13,
        "question": "Кого бело-синие первые разгромили в этом сезоне?",
        "options": [
            "«Факел»",
            "«Акрон»",
            "«Крылья Советов»",
            "«Родина»"
        ],
        "answer": "«Родина»"
    },
    {
        "id": 14,
        "question": "Сколько голов «Балтика» забила в этом сезоне?",
        "options": [
            "17",
            "14",
            "20",
            "12"
        ],
        "answer": "14"
    },
    {
        "id": 15,
        "question": "А сколько пропустили калининградцы?",
        "options": [
            "12",
            "8",
            "15",
            "17"
        ],
        "answer": "12"
    },
    {
        "id": 16,
        "question": "Кто был старшим тренером во время дисквалификации Талалаева?",
        "options": [
            "Ю.А. Нагайцев",
            "А.А. Талалаев (младший)",
            "Никого не было",
            "Были вместе"
        ],
        "answer": "Ю.А. Нагайцев"
    },
    {
        "id": 17,
        "question": "Забивал ли Сергей Варатынов в этом сезоне?",
        "options": [
            "Да",
            "Нет"
        ],
        "answer": "Да"
    },
    {
        "id": 18,
        "question": "Кто забил больше: Оффор или Варатынов?",
        "options": [
            "Оффор",
            "Варатынов"
        ],
        "answer": "Оффор"
    },
    {
        "id": 19,
        "question": "Какому московскому клубу первым проиграла «Балтика» в сезоне?",
        "options": [
            "«Динамо»",
            "«Спартак»",
            "ЦСКА",
            "«Локомотив»"
        ],
        "answer": "ЦСКА"
    }
]

QUESTIONS2 = [
    {
        "id": 0,
        "question": "Против кого «Балтика» сыграла первый матч в сезоне 25/26?",
        "options": [
            "«Зенит»",
            "«Динамо»",
            "ЦСКА",
            "«Спартак»"
        ],
        "answer": "«Динамо»"
    },
    {
        "id": 1,
        "question": "Кто стал лучшим бомбардиром «Балтики» в сезоне?",
        "options": [
            "Брайан Хиль",
            "Максим Петров",
            "Николай Титков",
            "Чинонсо Оффор"
        ],
        "answer": "Брайан Хиль"
    },
    {
        "id": 2,
        "question": "Кто забил первый гол «Балтики» в РПЛ 25/26?",
        "options": [
            "Николай Титков",
            "Владислав Саусь",
            "Максим Петров",
            "Брайан Хиль"
        ],
        "answer": "Брайан Хиль"
    },
    {
        "id": 3,
        "question": "Сколько очков набрала «Балтика» в том сезоне?",
        "options": [
            "50",
            "42",
            "48",
            "46"
        ],
        "answer": "46"
    },
    {
        "id": 4,
        "question": "Сколько голов забила «Балтика» за весь сезон в РПЛ 25/26?",
        "options": [
            "45",
            "30",
            "38",
            "33"
        ],
        "answer": "38"
    },
    {
        "id": 5,
        "question": "А сколько пропустили бело-синие в том сезоне?",
        "options": [
            "15",
            "21",
            "25",
            "19"
        ],
        "answer": "21"
    },
    {
        "id": 6,
        "question": "Какой первый футболист «Балтики» удалился в сезоне 25/26?",
        "options": [
            "Ираклий Манелов",
            "Кевин Андраде",
            "Натан Гассама",
            "Андрей Мендель"
        ],
        "answer": "Кевин Андраде"
    },
    {
        "id": 7,
        "question": "За что Талалаев получил первую дисквалификацию в том сезоне?",
        "options": [
            "За толчок игрока соперника",
            "За выбивание мяча на трибуну",
            "За неприличный жест и слова в сторону скамейки соперника",
            "За драку с соперником"
        ],
        "answer": "За неприличный жест и слова в сторону скамейки соперника"
    },
    {
        "id": 8,
        "question": "А в матче с кем Андрей Викторович получил первую дисквалификацию?",
        "options": [
            "«Балтика» – ЦСКА",
            "«Балтика» – «Спартак»",
            "«Балтика» – «Зенит»",
            "«Балтика» – «Нижний Новгород»"
        ],
        "answer": "«Балтика» – «Спартак»"
    },
    {
        "id": 9,
        "question": "Кто из балтийцев забил шикарный гол со штрафного в матче «Балтика» – «Нижний Новгород» (2:2)?",
        "options": [
            "Максим Петров",
            "Николай Титков",
            "Илья Петров",
            "Элдар Чивич"
        ],
        "answer": "Элдар Чивич"
    },
    {
        "id": 10,
        "question": "С кем «Балтика» была в группе в кубке России?",
        "options": [
            "«Зенит», «Крылья Советов», «Ахмат»",
            "ЦСКА, «Локомотив», «Акрон»",
            "«Сочи», «Локомотив», ЦСКА",
            "«Краснодар», «Локомотив», «Оренбург»"
        ],
        "answer": "ЦСКА, «Локомотив», «Акрон»"
    },
    {
        "id": 11,
        "question": "Против кого балтийцы сыграли первый матч в кубке?",
        "options": [
            "«Акрон»",
            "«Оренбург»",
            "«Спартак»",
            "ЦСКА"
        ],
        "answer": "«Акрон»"
    },
    {
        "id": 12,
        "question": "Кто забил первый гол «Балтики» в кубке России сезона 25/26?",
        "options": [
            "Элдар Чивич",
            "Чинонсо Оффор",
            "Тентон Йенне",
            "Илья Петров"
        ],
        "answer": "Тентон Йенне"
    },
    {
        "id": 13,
        "question": "Кто в кубке сыграл больше матчей?",
        "options": [
            "Егор Любаков",
            "Иван Кукушкин",
            "Одинаково"
        ],
        "answer": "Одинаково"
    },
    {
        "id": 14,
        "question": "Против кого «Балтика» сыграла последний матч в кубке России в том сезоне?",
        "options": [
            "«Спартак»",
            "ЦСКА",
            "«Локомотив»",
            "«Зенит»"
        ],
        "answer": "«Зенит»"
    },
    {
        "id": 15,
        "question": "Какое место «Балтика» заняла на групповом этапе кубка России 25/26?",
        "options": [
            "1",
            "2",
            "3",
            "4"
        ],
        "answer": "3"
    },
    {
        "id": 16,
        "question": "Сколько очков набрала «Балтика» на том групповом этапе?",
        "options": [
            "6",
            "3",
            "4",
            "5"
        ],
        "answer": "5"
    },
    {
        "id": 17,
        "question": "Забивал ли Стефан Ковач в том сезоне кубка?",
        "options": [
            "Да",
            "Нет"
        ],
        "answer": "Нет"
    },
    {
        "id": 18,
        "question": "Забивал ли Владислав Поспелов в том сезоне кубка России?",
        "options": [
            "Да",
            "Нет"
        ],
        "answer": "Нет"
    },
    {
        "id": 19,
        "question": "Сколько голов забил Кирилл Степанов в кубке России 25/26?",
        "options": [
            "Два гола",
            "Один гол",
            "Три гола",
            "Ни одного"
        ],
        "answer": "Два гола"
    }
]

QUESTIONS3 = [
    {
        "id": 0,
        "question": "Кто играет под 9 номером?",
        "options": [
            "Чинонсо Оффор",
            "Брайан Хиль",
            "Егор Голенков",
            "Владислав Поспелов"
        ],
        "answer": "Чинонсо Оффор"
    },
    {
        "id": 1,
        "question": "Кто играет под 68 номером?",
        "options": [
            "Элдар Чивич",
            "Максим Петров",
            "Михаил Рядно",
            "Айман Мурид"
        ],
        "answer": "Михаил Рядно"
    },
    {
        "id": 2,
        "question": "Кто играет под 5 номером?",
        "options": [
            "Илья Петров",
            "Стефан Ковач",
            "Айман Мурид",
            "Андрей Мендель"
        ],
        "answer": "Айман Мурид"
    },
    {
        "id": 3,
        "question": "Кто играет под 8 номером?",
        "options": [
            "Андрей Мендель",
            "Константин Шильцов",
            "Александр Филин",
            "Нету игрока с таким номером"
        ],
        "answer": "Андрей Мендель"
    },
    {
        "id": 4,
        "question": "Кто играет под 24 номером?",
        "options": [
            "Мингиян Бевеев",
            "Лорис Муйоколо",
            "Эдуардо Андерсон",
            "Александр Филин"
        ],
        "answer": "Лорис Муйоколо"
    },
    {
        "id": 5,
        "question": "Кто играет под 7 номером?",
        "options": [
            "Элдар Чивич",
            "Константин Шильцов",
            "Владислав Поспелов",
            "Егор Голенков"
        ],
        "answer": "Константин Шильцов"
    },
    {
        "id": 6,
        "question": "Кто играет под 10 номером?",
        "options": [
            "Максим Петров",
            "Стефан Ковач",
            "Владислав Поспелов",
            "Илья Петров"
        ],
        "answer": "Илья Петров"
    },
    {
        "id": 7,
        "question": "Кто играет под 2 номером?",
        "options": [
            "Натан Гассама",
            "Фахд Муфи",
            "Сергей Варатынов",
            "Илья Кирш"
        ],
        "answer": "Сергей Варатынов"
    },
    {
        "id": 8,
        "question": "Кто играет под 44 номером?",
        "options": [
            "Владислав Поспелов",
            "Егор Любаков",
            "Иван Кукушкин",
            "Стефан Ковач"
        ],
        "answer": "Егор Любаков"
    },
    {
        "id": 9,
        "question": "Кто играет под 18 номером?",
        "options": [
            "Фахд Муфи",
            "Максим Шнапцев",
            "Иван Беликов",
            "Нет игрока с таким номером"
        ],
        "answer": "Фахд Муфи"
    },
    {
        "id": 10,
        "question": "Кто играет под 42 номером?",
        "options": [
            "Максим Петров",
            "Егор Голенков",
            "Максим Шнапцев",
            "Владислав Поспелов"
        ],
        "answer": "Владислав Поспелов"
    },
    {
        "id": 11,
        "question": "Кто играет под 81 номером?",
        "options": [
            "Эдуардо Андерсон",
            "Илья Петров",
            "Иван Кукушкин",
            "Егор Любаков"
        ],
        "answer": "Иван Кукушкин"
    },
    {
        "id": 12,
        "question": "Кто играет под 4 номером?",
        "options": [
            "Сергей Варатынов",
            "Эдуардо Андерсон",
            "Натан Гассама",
            "Александр Филин"
        ],
        "answer": "Натан Гассама"
    },
    {
        "id": 13,
        "question": "Кто играет под 22 номером?",
        "options": [
            "Фахд Муфи",
            "Мингиян Бевеев",
            "Максим Шнапцев",
            "Максим Петров"
        ],
        "answer": "Мингиян Бевеев"
    },
    {
        "id": 14,
        "question": "Кто играет под 19 номером?",
        "options": [
            "Эдуардо Андерсон",
            "Максим Шнапцев",
            "Мингиян Бевеев",
            "Александр Филин"
        ],
        "answer": "Максим Шнапцев"
    }
]

# # --- Проверка мобильного устройства ---
# MOBILE_AGENTS = (
#     'iphone', 'ipod', 'android', 'windows phone', 'mobile',
#     'opera mini', 'blackberry', 'webos', 'iemobile'
# )

# DESKTOP_BLOCK_PAGE = """
# <!DOCTYPE html>
# <html lang="ru">
# <head>
#     <meta charset="utf-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1">
#     <title>Только с телефона</title>
#     <style>
#         body {
#             font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
#             display: flex; align-items: center; justify-content: center;
#             min-height: 100vh; margin: 0; padding: 20px;
#             background: linear-gradient(135deg, #1e3c72, #2a5298);
#             color: #fff; text-align: center; box-sizing: border-box;
#         }
#         .box {
#             max-width: 420px; padding: 32px 24px;
#             background: rgba(255,255,255,0.1);
#             border-radius: 20px;
#             box-shadow: 0 8px 32px rgba(0,0,0,0.3);
#         }
#         .icon { font-size: 64px; margin-bottom: 16px; }
#         h1 { font-size: 24px; margin: 0 0 12px; }
#         p { font-size: 16px; line-height: 1.5; margin: 0; opacity: 0.9; }
#     </style>
# </head>
# <body>
#     <div class="box">
#         <div class="icon">📱</div>
#         <h1>Откройте с телефона</h1>
#         <p>Этот сайт доступен только с мобильного устройства. Откройте ссылку на смартфоне.</p>
#     </div>
# </body>
# </html>
# """

# def is_mobile():
#     ua = request.headers.get('User-Agent', '').lower()
#     return any(agent in ua for agent in MOBILE_AGENTS)

# ---------- Календарь матчей ----------
# Расписание и логотипы взяты с https://www.baltiho.ru/matches/ (сезон 2026/27).
#
# Ключ клуба (например "zenit") = имя файла логотипа:  static/logos/zenit.png
#   • если файла нет в static/logos/, логотип подтягивается с baltiho.ru;
#   • если и его нет — рисуется цветной кружок с сокращением (short).
# Скачать все логотипы к себе:  python download_logos.py
LOGO_REMOTE = "https://www.baltiho.ru/images/clubs/{key}.png"

CLUBS = {
    "cska":           {"name": "ЦСКА",            "short": "ЦСК", "color": "#C8102E"},
    "dynamo":         {"name": "Динамо Москва",   "short": "ДИН", "color": "#1E3A8A"},
    "krylia-sovetov": {"name": "Крылья Советов",  "short": "КРС", "color": "#2150A8"},
    "spartak":        {"name": "Спартак",         "short": "СПА", "color": "#D4202A"},
    "rubin":          {"name": "Рубин",           "short": "РУБ", "color": "#8B1A1A"},
    "rodina-moscow":  {"name": "Родина",          "short": "РОД", "color": "#C8102E"},
    "lokomotiv":      {"name": "Локомотив",       "short": "ЛОК", "color": "#0B7A3B"},
    "fakel":          {"name": "Факел",           "short": "ФАК", "color": "#B3262E"},
    "zenit":          {"name": "Зенит",           "short": "ЗЕН", "color": "#0A8FD8"},
    "akhmat":         {"name": "Ахмат",           "short": "АХМ", "color": "#2E7D32"},
    "rostov":         {"name": "Ростов",          "short": "РОС", "color": "#C99700"},
    "krasnodar":      {"name": "Краснодар",       "short": "КРА", "color": "#1B8A3A"},
    "akron":          {"name": "Акрон",           "short": "АКР", "color": "#1E4FA0"},
    "dinamo-mx":      {"name": "Динамо Махачкала", "short": "ДМХ", "color": "#2A6FB5"},
    "orenburg":       {"name": "Оренбург",        "short": "ОРЕ", "color": "#1F2A44"},
}

# Расписание «Балтики». Порядок не важен — сортируется по дате.
# Формат строки:
#   (club, date, time, home, tournament, score, pen)
#   club       — ключ из CLUBS
#   date       — "ГГГГ-ММ-ДД"
#   time       — "ЧЧ:ММ" (время КАЛИНИНГРАДСКОЕ, МСК +1 час) или None, если ещё не назначено
#   home       — True: дома, False: в гостях
#   tournament — подпись турнира
#   score      — счёт в порядке «хозяева:гости» (как в протоколе) или None, если матч не сыгран
#   pen        — счёт серии пенальти в том же порядке или None
# Если time=None — дата предварительная (помечается звёздочкой).
# После матча просто допишите score (и pen) — всё остальное посчитается само.
SCHEDULE = [
    ("cska",           "2026-07-24", "19:00", False, "РПЛ · 1 тур",   "2:1", None),
    ("dynamo",         "2026-08-01", "19:45", True,  "РПЛ · 2 тур",   "2:1", None),
    ("zenit",          "2026-08-05", "19:45", False, "Кубок · 1 тур", "1:0", None),
    ("krylia-sovetov", "2026-08-08", "14:30", False, "РПЛ · 3 тур",   "0:2", None),
    ("spartak",        "2026-08-16", "18:30", True,  "РПЛ · 4 тур",   "1:2", None),
    ("dinamo-mx",      "2026-08-20", "19:45", True,  "Кубок · 2 тур", "1:1", "5:4"),
    ("rubin",          "2026-08-24", "19:30", True,  "РПЛ · 5 тур",   "1:1", None),
    ("rodina-moscow",  "2026-08-30", "14:00", False, "РПЛ · 6 тур",   "0:3", None),
    ("krylia-sovetov", "2026-09-02", "19:45", True,  "Кубок · 3 тур", "0:0", "3:5"),
    ("lokomotiv",      "2026-09-06", "19:45", True,  "РПЛ · 7 тур",   "0:1", None),
    ("fakel",          "2026-09-12", "13:00", False, "РПЛ · 8 тур",   "2:2", None),
    ("zenit",          "2026-09-16", "19:45", True,  "РПЛ · 9 тур",   "2:3", None),
    ("akhmat",         "2026-10-11", "13:00", False, "РПЛ · 10 тур",  "0:0", None),
    ("krylia-sovetov", "2026-10-14", "15:15", False, "Кубок · 4 тур", "0:2", None),
    ("rostov",         "2026-10-18", "20:00", True,  "РПЛ · 11 тур",  "0:0", None),
    ("krasnodar",      "2026-10-24", "18:30", False, "РПЛ · 12 тур",  "1:1", None),
    ("zenit",          "2026-10-29", "20:45", True,  "Кубок · 5 тур", "2:3", None),
    ("akron",          "2026-11-01", "16:30", True,  "РПЛ · 13 тур",  "2:1", None),
    ("dinamo-mx",      "2026-11-08", "19:45", True,  "РПЛ · 14 тур",  None,  None),
    ("orenburg",       "2026-11-21", "12:00", False, "РПЛ · 15 тур",  None,  None),
    ("dinamo-mx",      "2026-11-25", "17:00", False, "Кубок · 6 тур", None,  None),
    ("akhmat",         "2026-11-28", "18:00", True,  "РПЛ · 16 тур",  None,  None),
    ("zenit",          "2026-12-05", "18:00", False, "РПЛ · 17 тур",  None,  None),
    # --- после зимнего перерыва: даты предварительные, время пока не назначено ---
    ("rodina-moscow",  "2027-02-26", None,    True,  "РПЛ · 18 тур",  None,  None),
    ("rostov",         "2027-03-05", None,    False, "РПЛ · 19 тур",  None,  None),
    ("krasnodar",      "2027-03-12", None,    True,  "РПЛ · 20 тур",  None,  None),
    ("dinamo-mx",      "2027-03-19", None,    False, "РПЛ · 21 тур",  None,  None),
    ("dynamo",         "2027-04-03", None,    False, "РПЛ · 22 тур",  None,  None),
    ("cska",           "2027-04-10", None,    True,  "РПЛ · 23 тур",  None,  None),
    ("rubin",          "2027-04-16", None,    False, "РПЛ · 24 тур",  None,  None),
    ("krylia-sovetov", "2027-04-23", None,    True,  "РПЛ · 25 тур",  None,  None),
    ("spartak",        "2027-05-01", None,    False, "РПЛ · 26 тур",  None,  None),
    ("fakel",          "2027-05-08", None,    True,  "РПЛ · 27 тур",  None,  None),
    ("lokomotiv",      "2027-05-15", None,    False, "РПЛ · 28 тур",  None,  None),
    ("akron",          "2027-05-22", None,    False, "РПЛ · 29 тур",  None,  None),
    ("orenburg",       "2027-05-29", None,    True,  "РПЛ · 30 тур",  None,  None),
]

MONTHS_RU = ["января", "февраля", "марта", "апреля", "мая", "июня",
             "июля", "августа", "сентября", "октября", "ноября", "декабря"]
MONTHS_NOM = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
              "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
WEEKDAYS_RU = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]

def find_logo(key):
    """Сначала static/logos/<key>.*, иначе логотип с baltiho.ru."""
    for ext in ("png", "svg", "webp", "jpg", "jpeg"):
        if os.path.exists(os.path.join(app.static_folder, "logos", f"{key}.{ext}")):
            return url_for("static", filename=f"logos/{key}.{ext}")
    return LOGO_REMOTE.format(key=key)

def match_result(score, pen, home):
    """'win' / 'draw' / 'loss' с точки зрения «Балтики» (при ничьей учитываются пенальти)."""
    if not score:
        return None
    a, b = (int(x) for x in score.split(":"))
    if a == b and pen:
        a, b = (int(x) for x in pen.split(":"))
    mine, other = (a, b) if home else (b, a)
    return "win" if mine > other else "loss" if mine < other else "draw"

def build_calendar():
    """Возвращает (months, start): месяцы с карточками матчей и индекс месяца, который открыть."""
    today = datetime.now().date()
    items = []
    for club_key, date, time, home, tournament, score, pen in sorted(
            SCHEDULE, key=lambda x: (x[1], x[2] or "")):
        club = CLUBS.get(club_key, {"name": club_key, "short": "?", "color": "#555555"})
        d = datetime.strptime(date, "%Y-%m-%d").date()
        items.append({
            "ym": (d.year, d.month),
            "date": d,
            "name": club["name"],
            "short": club["short"],
            "color": club["color"],
            "logo": find_logo(club_key),
            "date_text": f"{d.day} {MONTHS_RU[d.month - 1]}, {WEEKDAYS_RU[d.weekday()]}" + ("" if time else " *"),
            "time_text": time or "время уточняется",
            "home": home,
            "tournament": tournament,
            "score": score,
            "pen": pen,
            "result": match_result(score, pen, home),
            "past": d < today,
            "next": False,
        })

    # ближайший ещё не сыгранный матч — подсветим
    for m in items:
        if m["date"] >= today and not m["score"]:
            m["next"] = True
            break

    months, index = [], {}
    for m in items:
        if m["ym"] not in index:
            index[m["ym"]] = len(months)
            months.append({"title": f"{MONTHS_NOM[m['ym'][1] - 1]} {m['ym'][0]}", "matches": []})
        months[index[m["ym"]]]["matches"].append(m)

    # какой месяц открыть: текущий, иначе ближайший будущий, иначе последний
    start = len(months) - 1
    for i, ym in enumerate(index):
        if ym >= (today.year, today.month):
            start = i
            break
    return months, start

# ---------- Данные разделов (заполняйте здесь) ----------
# Новости теперь хранятся в базе (таблица news) и публикуются админами через сайт.
ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "webp", "gif"}

# Статьи тоже хранятся в базе (таблица articles) и редактируются админами через сайт.
LEADERBOARD_SIZE = 15   # сколько мест показывать в таблице лидеров
NEWS_MAX = 5000
ARTICLE_TITLE_MAX = 150
ARTICLE_TEXT_MAX = 20000
ARTICLE_AUTHOR_MAX = 60

def init_db():
    conn = sqlite3.connect("users.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            points INTEGER NOT NULL DEFAULT 0,
            v1_done INTEGER DEFAULT 0,
            v2_done INTEGER DEFAULT 0,
            v3_done INTEGER DEFAULT 0
        )
    """)
    # роль пользователя: 'noadm' (по умолчанию) или 'adm' (ставится вручную в базе)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
    if "role" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'noadm'")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            image TEXT,
            created_at TEXT NOT NULL,
            author_id INTEGER
        )
    """)
    news_cols = [r[1] for r in conn.execute("PRAGMA table_info(news)").fetchall()]
    if "updated_at" not in news_cols:
        conn.execute("ALTER TABLE news ADD COLUMN updated_at TEXT")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            text TEXT NOT NULL,
            image TEXT,
            author TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            author_id INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

app = Flask(__name__)
# Секретный ключ лучше задавать переменной окружения SECRET_KEY (на хостинге).
app.secret_key = os.environ.get("SECRET_KEY", "bg-secret-key-1010")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"   # защита от CSRF-запросов с чужих сайтов
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # фото до 8 МБ
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def is_admin():
    """Роль берём из базы при каждом запросе — смена на adm в БД действует сразу."""
    user_id = session.get("user_id")
    if not user_id:
        return False
    conn = sqlite3.connect("users.db")
    row = conn.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return bool(row and row[0] == "adm")

def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not is_admin():
            return "Нет доступа", 403
        return view(*args, **kwargs)
    return wrapper

def upload_url(filename):
    return url_for("static", filename=f"uploads/{filename}") if filename else None

def looks_like_image(stream):
    """Проверка по первым байтам, что файл — настоящая картинка, а не переименованный файл."""
    head = stream.read(16)
    stream.seek(0)
    return (head.startswith((b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"GIF87a", b"GIF89a"))
            or (head[:4] == b"RIFF" and head[8:12] == b"WEBP"))

def save_image(file):
    """Сохраняет загруженное фото. Возвращает (имя_файла, None) или (None, текст_ошибки)."""
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    ext = re.sub(r"[^a-z0-9]", "", ext)
    if ext not in ALLOWED_IMAGE_EXT:
        return None, "Допустимые форматы фото: png, jpg, jpeg, webp, gif."
    if not looks_like_image(file.stream):
        return None, "Файл не похож на изображение."
    filename = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return filename, None

def delete_upload(filename):
    if not filename:
        return
    try:
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], os.path.basename(filename)))
    except OSError:
        pass

def resolve_image(old, file, remove):
    """Что делать с фото при редактировании.
    Возвращает (новое_имя, файл_на_удаление, ошибка)."""
    if file and file.filename:
        name, err = save_image(file)
        if err:
            return old, None, err
        return name, old, None          # заменили: старый файл удалим после записи в базу
    if remove and old:
        return None, old, None          # убрали фото совсем
    return old, None, None

def back_url(default_endpoint="news"):
    ref = request.referrer
    if ref and urlparse(ref).netloc == request.host:
        return ref
    return url_for(default_endpoint)

# @app.before_request
# def block_desktop():
#     if request.path.startswith('/static'):
#         return None
#     if not is_mobile():
#         return render_template_string(DESKTOP_BLOCK_PAGE), 403
#     return None

@app.route("/")
def home():
    if "user_id" not in session:
       return render_template("welcome.html")
    now = datetime.now().strftime("%d/%b/%Y")
    tag = session.get("user_name", "Гость")
    return render_template("home.html", time=now, name=tag)

@app.route("/quizzes")
def quizzes():
    return render_template("quizzes.html")

@app.route("/calendar")
def calendar():
    months, start = build_calendar()
    return render_template("calendar.html", months=months, start=start)

# ======================= НОВОСТИ =======================
@app.route("/news")
def news():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, text, image, created_at, updated_at FROM news ORDER BY id DESC").fetchall()
    conn.close()
    items = [{
        "id": r["id"],
        "date": r["created_at"],
        "edited": bool(r["updated_at"]),
        "text": r["text"],
        "image": upload_url(r["image"]),
    } for r in rows]
    return render_template("news.html", news=items, is_admin=is_admin())

@app.route("/news/add", methods=["POST"])
@admin_required
def news_add():
    text = request.form.get("text", "").strip()
    file = request.files.get("image")
    has_file = bool(file and file.filename)

    if len(text) > NEWS_MAX:
        flash(f"Текст слишком длинный (максимум {NEWS_MAX} символов).")
        return redirect(url_for("news"))
    if not text and not has_file:
        flash("Напишите текст или добавьте фото.")
        return redirect(url_for("news"))

    filename = None
    if has_file:
        filename, err = save_image(file)
        if err:
            flash(err)
            return redirect(url_for("news"))

    conn = get_db()
    conn.execute(
        "INSERT INTO news (text, image, created_at, author_id) VALUES (?, ?, ?, ?)",
        (text, filename, datetime.now().strftime("%d.%m.%Y %H:%M"), session.get("user_id")),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("news"))

@app.route("/news/<int:news_id>/edit", methods=["GET", "POST"])
@admin_required
def news_edit(news_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM news WHERE id = ?", (news_id,)).fetchone()
    if not row:
        conn.close()
        abort(404)

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        file = request.files.get("image")
        remove = bool(request.form.get("remove_image"))
        will_have_image = bool(file and file.filename) or (row["image"] and not remove)

        error = None
        if len(text) > NEWS_MAX:
            error = f"Текст слишком длинный (максимум {NEWS_MAX} символов)."
        elif not text and not will_have_image:
            error = "Нельзя оставить новость пустой: нужен текст или фото."
        if not error:
            image, to_delete, error = resolve_image(row["image"], file, remove)
        if error:
            conn.close()
            flash(error)
            return redirect(url_for("news_edit", news_id=news_id))

        conn.execute(
            "UPDATE news SET text = ?, image = ?, updated_at = ? WHERE id = ?",
            (text, image, datetime.now().strftime("%d.%m.%Y %H:%M"), news_id),
        )
        conn.commit()
        conn.close()
        delete_upload(to_delete)
        flash("Новость сохранена.")
        return redirect(url_for("news") + f"#news-{news_id}")

    conn.close()
    item = {"id": row["id"], "text": row["text"], "image": upload_url(row["image"])}
    return render_template("news_edit.html", item=item)

@app.route("/news/<int:news_id>/delete", methods=["GET", "POST"])
@admin_required
def news_delete(news_id):
    conn = get_db()
    row = conn.execute("SELECT text, image FROM news WHERE id = ?", (news_id,)).fetchone()
    if not row:
        conn.close()
        abort(404)
    if request.method == "GET":          # страница «Точно удалить?»
        conn.close()
        return render_template("confirm_delete.html", what="новость",
                               preview=(row["text"] or "Новость с фото")[:120],
                               cancel=url_for("news") + f"#news-{news_id}")
    conn.execute("DELETE FROM news WHERE id = ?", (news_id,))
    conn.commit()
    conn.close()
    delete_upload(row["image"])
    flash("Новость удалена.")
    return redirect(url_for("news"))

# ======================= СТАТЬИ =======================
def read_article_form():
    """Читает и проверяет поля статьи. Возвращает (данные, ошибка)."""
    title = request.form.get("title", "").strip()
    text = request.form.get("text", "").strip()
    author = request.form.get("author", "").strip() or session.get("user_name", "")
    if not title or not text:
        return None, "Заполните заголовок и текст статьи."
    if len(title) > ARTICLE_TITLE_MAX:
        return None, f"Заголовок слишком длинный (максимум {ARTICLE_TITLE_MAX} символов)."
    if len(text) > ARTICLE_TEXT_MAX:
        return None, f"Текст слишком длинный (максимум {ARTICLE_TEXT_MAX} символов)."
    if len(author) > ARTICLE_AUTHOR_MAX:
        return None, f"Имя автора слишком длинное (максимум {ARTICLE_AUTHOR_MAX} символов)."
    return {"title": title, "text": text, "author": author}, None

@app.route("/articles")
def articles():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, title, text, image, author, created_at, updated_at FROM articles ORDER BY id DESC"
    ).fetchall()
    conn.close()
    items = [{
        "id": r["id"],
        "title": r["title"],
        "text": r["text"],
        "author": r["author"],
        "date": r["created_at"],
        "edited": bool(r["updated_at"]),
        "image": upload_url(r["image"]),
    } for r in rows]
    return render_template("articles.html", articles=items, is_admin=is_admin())

@app.route("/articles/add", methods=["POST"])
@admin_required
def article_add():
    data, error = read_article_form()
    if error:
        flash(error)
        return redirect(url_for("articles"))

    file = request.files.get("image")
    filename = None
    if file and file.filename:
        filename, error = save_image(file)
        if error:
            flash(error)
            return redirect(url_for("articles"))

    conn = get_db()
    conn.execute(
        "INSERT INTO articles (title, text, image, author, created_at, author_id) VALUES (?, ?, ?, ?, ?, ?)",
        (data["title"], data["text"], filename, data["author"],
         datetime.now().strftime("%d.%m.%Y %H:%M"), session.get("user_id")),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("articles"))

@app.route("/articles/<int:article_id>/edit", methods=["GET", "POST"])
@admin_required
def article_edit(article_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    if not row:
        conn.close()
        abort(404)

    if request.method == "POST":
        data, error = read_article_form()
        if not error:
            image, to_delete, error = resolve_image(
                row["image"], request.files.get("image"), bool(request.form.get("remove_image")))
        if error:
            conn.close()
            flash(error)
            return redirect(url_for("article_edit", article_id=article_id))

        conn.execute(
            "UPDATE articles SET title = ?, text = ?, author = ?, image = ?, updated_at = ? WHERE id = ?",
            (data["title"], data["text"], data["author"], image,
             datetime.now().strftime("%d.%m.%Y %H:%M"), article_id),
        )
        conn.commit()
        conn.close()
        delete_upload(to_delete)
        flash("Статья сохранена.")
        return redirect(url_for("articles") + f"#article-{article_id}")

    conn.close()
    item = {"id": row["id"], "title": row["title"], "text": row["text"],
            "author": row["author"] or "", "image": upload_url(row["image"])}
    return render_template("article_edit.html", item=item)

@app.route("/articles/<int:article_id>/delete", methods=["GET", "POST"])
@admin_required
def article_delete(article_id):
    conn = get_db()
    row = conn.execute("SELECT title, image FROM articles WHERE id = ?", (article_id,)).fetchone()
    if not row:
        conn.close()
        abort(404)
    if request.method == "GET":          # страница «Точно удалить?»
        conn.close()
        return render_template("confirm_delete.html", what="статью", preview=row["title"],
                               cancel=url_for("articles") + f"#article-{article_id}")
    conn.execute("DELETE FROM articles WHERE id = ?", (article_id,))
    conn.commit()
    conn.close()
    delete_upload(row["image"])
    flash("Статья удалена.")
    return redirect(url_for("articles"))

@app.errorhandler(413)
def too_large(e):
    flash("Файл слишком большой (максимум 8 МБ).")
    return redirect(back_url("news"))

@app.route("/faq")
def faq():
    return render_template("faq.html")

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/friends")
def friends():
    return render_template("friends.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/politic")
def politic():
    return render_template("politic.html")

@app.route("/invites")
def invites():
    return render_template("invites.html")

@app.route("/v1", methods=["GET", "POST"])
def v1():
    if request.method == "POST":
        score = 0
        for q in QUESTIONS1:
            user_answer = request.form.get(f"question_{q['id']}")
            if user_answer == q["answer"]:
                score += 1

        user_id = session.get("user_id")
        if user_id:
            conn = sqlite3.connect("users.db")
            row = conn.execute(
                "SELECT v1_done FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if row and not row[0]:
                conn.execute(
                    "UPDATE users SET points = points + ?, v1_done = 1 WHERE id = ?",
                    (score, user_id)
                )
                conn.commit()
            conn.close()

        return render_template("result.html", score=score, total=len(QUESTIONS1))
    
    return render_template("v1.html", questions=QUESTIONS1)

@app.route("/v2", methods=["GET", "POST"])
def v2():
    if request.method == "POST":
        score = 0
        for q in QUESTIONS2:
            user_answer = request.form.get(f"question_{q['id']}")
            if user_answer == q["answer"]:
                score += 1

        user_id = session.get("user_id")
        if user_id:
            conn = sqlite3.connect("users.db")
            row = conn.execute(
                "SELECT v2_done FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if row and not row[0]:
                conn.execute(
                    "UPDATE users SET points = points + ?, v2_done = 1 WHERE id = ?",
                    (score, user_id)
                )
                conn.commit()
            conn.close()

        return render_template("result.html", score=score, total=len(QUESTIONS2))
    
    return render_template("v2.html", questions=QUESTIONS2)

@app.route("/v3", methods=["GET", "POST"])
def v3():
    if request.method == "POST":
        score = 0
        for q in QUESTIONS3:
            user_answer = request.form.get(f"question_{q['id']}")
            if user_answer == q["answer"]:
                score += 1

        user_id = session.get("user_id")
        if user_id:
            conn = sqlite3.connect("users.db")
            row = conn.execute(
                "SELECT v3_done FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if row and not row[0]:
                conn.execute(
                    "UPDATE users SET points = points + ?, v3_done = 1 WHERE id = ?",
                    (score, user_id)
                )
                conn.commit()
            conn.close()

        return render_template("result.html", score=score, total=len(QUESTIONS3))
    
    return render_template("v3.html", questions=QUESTIONS3)

@app.route("/table")
def table():
    conn = sqlite3.connect("users.db")
    users = conn.execute(
        "SELECT name, points FROM users ORDER BY points DESC, name ASC LIMIT ?",
        (LEADERBOARD_SIZE,)
    ).fetchall()
    conn.close()
    return render_template("table.html", users=users)

# ======================= ВХОД / РЕГИСТРАЦИЯ =======================
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
NAME_MIN, NAME_MAX = 2, 30
PASSWORD_MIN, PASSWORD_MAX = 6, 128
MAX_LOGIN_FAILS, LOGIN_LOCK_SECONDS = 5, 300
_login_fails = {}   # (ip, email) -> [число ошибок, время первой ошибки]

def auth_error(template, message, status=400, **context):
    """Показывает ошибку на странице входа/регистрации (через flash-категорию 'auth')."""
    flash(message, "auth")
    return render_template(template, **context), status

def is_hashed(stored):
    return stored.startswith(("scrypt:", "pbkdf2:")) and stored.count("$") >= 2

def login_blocked(key):
    rec = _login_fails.get(key)
    if not rec:
        return False
    if time_mod.time() - rec[1] > LOGIN_LOCK_SECONDS:
        _login_fails.pop(key, None)
        return False
    return rec[0] >= MAX_LOGIN_FAILS

def login_failed(key):
    now = time_mod.time()
    rec = _login_fails.get(key)
    if not rec or now - rec[1] > LOGIN_LOCK_SECONDS:
        _login_fails[key] = [1, now]
    else:
        rec[0] += 1

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            return auth_error("login.html", "Введите email и пароль.", email=email)

        key = (request.remote_addr, email)
        if login_blocked(key):
            return auth_error("login.html",
                              "Слишком много неудачных попыток. Попробуйте через 5 минут.",
                              429, email=email)

        conn = sqlite3.connect("users.db")
        user = conn.execute(
            "SELECT id, name, password FROM users WHERE lower(email) = ?", (email,)
        ).fetchone()

        ok = False
        if user:
            stored = user[2] or ""
            if is_hashed(stored):
                ok = check_password_hash(stored, password)
            else:
                # старый аккаунт с паролем открытым текстом: проверяем и сразу переводим на хеш
                ok = hmac.compare_digest(stored.encode("utf-8"), password.encode("utf-8"))
                if ok:
                    conn.execute("UPDATE users SET password = ? WHERE id = ?",
                                 (generate_password_hash(password), user[0]))
                    conn.commit()
        conn.close()

        if not ok:
            login_failed(key)
            return auth_error("login.html", "Неверный email или пароль.", 401, email=email)

        _login_fails.pop(key, None)
        session.clear()                       # новая сессия после входа
        session["user_id"] = user[0]
        session["user_name"] = user[1]
        session.permanent = True
        return redirect("/")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        ctx = {"name": name, "email": email}

        if not (NAME_MIN <= len(name) <= NAME_MAX):
            return auth_error("register.html", f"Имя: от {NAME_MIN} до {NAME_MAX} символов.", **ctx)
        if len(email) > 120 or not EMAIL_RE.match(email):
            return auth_error("register.html", "Введите корректный email.", **ctx)
        if not (PASSWORD_MIN <= len(password) <= PASSWORD_MAX):
            return auth_error("register.html",
                              f"Пароль: от {PASSWORD_MIN} до {PASSWORD_MAX} символов.", **ctx)

        conn = sqlite3.connect("users.db")
        try:
            exists = conn.execute(
                "SELECT 1 FROM users WHERE lower(email) = ?", (email,)).fetchone()
            if exists:
                return auth_error("register.html",
                                  "Пользователь с таким email уже зарегистрирован.", 409, **ctx)
            conn.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, 'noadm')",
                (name, email, generate_password_hash(password)),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            return auth_error("register.html",
                              "Пользователь с таким email уже зарегистрирован.", 409, **ctx)
        finally:
            conn.close()

        flash("Регистрация прошла успешно. Теперь войдите.", "auth")
        return redirect("/login")

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)