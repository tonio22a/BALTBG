from flask import Flask, render_template, request, redirect, session, render_template_string
import sqlite3
from datetime import datetime

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
    conn.commit()
    conn.close()

init_db()

app = Flask(__name__)
app.secret_key = "bg-secret-key-1010"

# @app.before_request
# def block_desktop():
#     if request.path.startswith('/static'):
#         return None
#     if not is_mobile():
#         return render_template_string(DESKTOP_BLOCK_PAGE), 403
#     return None

@app.route("/")
def home():
    # if "user_id" not in session:
    #     return render_template("welcome.html")
    now = datetime.now().strftime("%d/%b/%Y")
    tag = session.get("user_name", "Гость")
    return render_template("home.html", time=now, name=tag)

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
        "SELECT name, points FROM users ORDER BY points DESC, name ASC"
    ).fetchall()
    conn.close()
    return render_template("table.html", users=users)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        conn = sqlite3.connect("users.db")
        user = conn.execute(
            "SELECT id, name FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()
        conn.close()

        if user:                             
            session["user_id"] = user[0]        
            session["user_name"] = user[1]         
            return redirect("/")                    
        else:
            return "Неверный email или пароль" 
        
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        
        conn = sqlite3.connect("users.db")
        conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
        conn.commit()
        conn.close()
        return redirect("/login")
    
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)