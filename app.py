from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"  # change this in production


# ---------------------- DB Setup ----------------------
def get_db():
    conn = sqlite3.connect("db.sqlite3")
    conn.row_factory = sqlite3.Row
    return conn

# initialize tables if not exist
with get_db() as conn:
    conn.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, uname TEXT UNIQUE, pwd TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY, user TEXT, project TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS friends(id INTEGER PRIMARY KEY, user TEXT, friend TEXT)")
    conn.commit()


# ---------------------- Routes ----------------------

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["u"]
        p = request.form["p"]

        conn = get_db()
        cur = conn.execute("SELECT * FROM users WHERE uname=? AND pwd=?", (u, p))
        if cur.fetchone():
            session["user"] = u
            return redirect(url_for("dashboard"))
        else:
            return "❌ Invalid login. Try again or sign up."

    return render_template("login.html")


@app.route("/signup", methods=["POST"])
def signup():
    u = request.form["u"]
    p = request.form["p"]

    conn = get_db()
    try:
        conn.execute("INSERT INTO users(uname, pwd) VALUES(?, ?)", (u, p))
        conn.commit()
    except sqlite3.IntegrityError:
        return "⚠️ Username already exists."

    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])


@app.route("/history")
def history():
    if "user" not in session:
        return redirect(url_for("login"))

    u = session["user"]
    conn = get_db()
    cur = conn.execute("SELECT * FROM history WHERE user=?", (u,))
    return render_template("history.html", logs=cur.fetchall())


@app.route("/friends")
def friends():
    if "user" not in session:
        return redirect(url_for("login"))

    u = session["user"]
    conn = get_db()
    cur = conn.execute("SELECT friend FROM friends WHERE user=?", (u,))
    return render_template("friends.html", friends=[r["friend"] for r in cur.fetchall()])


@app.route("/add_friend", methods=["POST"])
def add_friend():
    if "user" not in session:
        return redirect(url_for("login"))

    friend = request.form["friend"]
    u = session["user"]

    conn = get_db()
    conn.execute("INSERT INTO friends(user, friend) VALUES(?, ?)", (u, friend))
    conn.commit()

    return redirect(url_for("friends"))


@app.route("/run/<pname>")
def run_project(pname):
    if "user" not in session:
        return redirect(url_for("login"))

    u = session["user"]
    conn = get_db()
    conn.execute("INSERT INTO history(user, project) VALUES(?, ?)", (u, pname))
    conn.commit()

    return f"🚀 Project '{pname}' launched! (This is where your actual project would run)"


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------- Run App ----------------------
if __name__ == "__main__":
    app.run(debug=True)
