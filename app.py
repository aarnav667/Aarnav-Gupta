from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "dev"

def get_db():
    conn = sqlite3.connect("db.sqlite3")
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB
with get_db() as conn:
    conn.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, uname TEXT, pwd TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY, user TEXT, project TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS friends(id INTEGER PRIMARY KEY, user TEXT, friend TEXT)")
    conn.commit()

@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["u"];p=request.form["p"]
        conn=get_db()
        cur=conn.execute("SELECT * FROM users WHERE uname=? AND pwd=?",(u,p))
        if cur.fetchone():
            session["user"]=u
            return redirect(url_for("dashboard"))
        else:
            return "Invalid login"
    return render_template("login.html")

@app.route("/signup", methods=["POST"])
def signup():
    u=request.form["u"];p=request.form["p"]
    conn=get_db();conn.execute("INSERT INTO users(uname,pwd) VALUES(?,?)",(u,p));conn.commit()
    return redirect(url_for("login"))

@app.route("/dashboard")
projectzdef dashboard():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])

@app.route("/history")
def history():
    u=session["user"]
    conn=get_db();cur=conn.execute("SELECT * FROM history WHERE user=?",(u,))
    return render_template("history.html", logs=cur.fetchall())

@app.route("/friends")
def friends():
    u=session["user"]
    conn=get_db();cur=conn.execute("SELECT friend FROM friends WHERE user=?",(u,))
    return render_template("friends.html", friends=[r["friend"] for r in cur.fetchall()])

# Example project launcher
@app.route("/run/<pname>")
def run_project(pname):
    u=session["user"]
    conn=get_db();conn.execute("INSERT INTO history(user,project) VALUES(?,?)",(u,pname));conn.commit()
    return f"Launching {pname}... (this would run the project)"

if __name__=="__main__":
    app.run(debug=True)
