from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("users.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

app = Flask(__name__)
app.secret_key = "dgram-secret-key-123"

@app.route("/")
def home():
    if "user_id" not in session:
        return render_template("welcome.html")
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