"""
=============================================================
  UNION-BASED SQL INJECTION - EDUCATIONAL DEMO (LOCAL ONLY)
=============================================================
WARNING: The query in `search()` is DELIBERATELY vulnerable
(uses raw string formatting instead of parameterized queries)
so you can learn/demo union-based SQL injection.

NEVER write code like this in a real application.
Always use parameterized queries / ORM in production.
=============================================================
"""

from flask import Flask, request, render_template, session, redirect, url_for
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "shop.db")

app = Flask(__name__)
app.secret_key = "super_secret_key_for_demo"


def get_db():
    conn = sqlite3.connect(DB_PATH)

    # Mock information_schema so standard payloads work!
    conn.execute("ATTACH DATABASE ':memory:' AS information_schema")
    conn.execute("CREATE TABLE information_schema.tables (table_name TEXT, table_schema TEXT)")
    conn.execute("CREATE TABLE information_schema.columns (table_name TEXT, column_name TEXT)")
    
    conn.execute("INSERT INTO information_schema.tables (table_name, table_schema) VALUES ('products', 'public'), ('users', 'public')")
    
    columns = [
        ('products', 'id'), ('products', 'name'), ('products', 'price'),
        ('users', 'id'), ('users', 'username'), ('users', 'password')
    ]
    conn.executemany("INSERT INTO information_schema.columns (table_name, column_name) VALUES (?, ?)", columns)

    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    q = request.args.get("q", "")

    conn = get_db()
    cur = conn.cursor()

    # --------------------------------------------------------
    # VULNERABLE LINE (on purpose):
    # user input `q` is concatenated directly into the SQL
    # string instead of being passed as a bound parameter.
    # This is exactly what makes UNION-based injection possible.
    # --------------------------------------------------------
    query = "SELECT id, name, price FROM products WHERE name LIKE '%" + q + "%'"

    error = None
    rows = []
    try:
        cur.execute(query)
        rows = cur.fetchall()
    except sqlite3.Error as e:
        error = str(e)
    finally:
        conn.close()

    return render_template(
        "result.html", rows=rows, query=query, q=q, error=error
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        cur = conn.cursor()
        # Secure login query (the vulnerability is only in the search)
        cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["username"] = username
            if username == "admin":
                session["solved"] = True
            return redirect(url_for("index"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("Database not found! Run: python init_db.py")
    app.run(debug=True, host="127.0.0.1", port=5000)
