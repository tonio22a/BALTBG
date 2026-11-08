from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Список вопросов викторины
QUESTIONS = [
    {
        "id": 0,
        "question": "Какой язык используется для логики во Flask?",
        "options": ["Python", "C++", "HTML"],
        "answer": "Python"
    },
    {
        "id": 1,
        "question": "Какой шаблонизатор встроен во Flask?",
        "options": ["Jinja2", "Blade", "Twig"],
        "answer": "Jinja2"
    }
]

@app.route("/", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        score = 0
        for q in QUESTIONS:
            user_answer = request.form.get(f"question_{q['id']}")
            if user_answer == q["answer"]:
                score += 1
        return render_template("result.html", score=score, total=len(QUESTIONS))
    
    return render_template("quiz.html", questions=QUESTIONS)

if __name__ == "__main__":
    app.run(debug=True)
