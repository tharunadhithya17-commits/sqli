# Union-Based SQL Injection — Local Learning Lab

This is a **deliberately vulnerable** Flask + SQLite web app built purely to
demonstrate how **union-based SQL injection** works, so you can learn how to
find it and how to fix it. Run it only on your own machine, never expose it
publicly.

## Folder structure
```
sqli-demo/
├── app.py              # Flask backend (contains the vulnerable query)
├── init_db.py           # Creates shop.db with 'products' and 'users' tables
├── requirements.txt
├── templates/
│   ├── index.html       # Search page
│   └── result.html       # Shows results + the raw SQL executed
└── static/
    └── style.css
```

## Setup & Run

```bash
cd sqli-demo
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py             # creates shop.db
python app.py                 # starts server at http://127.0.0.1:5000
```

Open **http://127.0.0.1:5000** in your browser.

## Where the vulnerability lives

In `app.py`:
```python
query = "SELECT id, name, price FROM products WHERE name LIKE '%" + q + "%'"
cur.execute(query)
```

The user's input `q` is glued directly into the SQL string instead of being
passed as a bound parameter. This means whatever the user types becomes part
of the actual SQL statement — that's the root cause of injection bugs.

## How union-based injection works (step by step)

Union-based SQLi lets an attacker use `UNION SELECT` to append the results
of a query *of their choosing* onto the results of the original query — as
long as the column count and (roughly) the column types match.

**1. Find the number of columns** using `ORDER BY`:
```
Mouse' ORDER BY 1--
Mouse' ORDER BY 2--
Mouse' ORDER BY 3--
Mouse' ORDER BY 4--   <-- this one will error, so the table has 3 columns
```

**2. Confirm which columns are reflected on the page** using a UNION with
dummy values:
```
' UNION SELECT 1, 2, 3--
```

**3. Pull real data from another table** — in this lab, the hidden `users`
table has 3 columns too, so:
```
' UNION SELECT id, username, password FROM users--
```
Paste that (URL-encoded automatically by the browser) into the search box,
and the results table will show usernames and passwords that came from a
completely different table than `products`.

**4. Explore the schema itself** (this works because SQLite exposes table
info in `sqlite_master`):
```
' UNION SELECT 1, name, sql FROM sqlite_master WHERE type='table'--
```

Every "Actual SQL executed" line shown on the results page lets you see
exactly how your input reshaped the query — that's the key learning tool
here.

## How to fix this (the real-world takeaway)

Replace the vulnerable line with a **parameterized query**:
```python
query = "SELECT id, name, price FROM products WHERE name LIKE ?"
cur.execute(query, ('%' + q + '%',))
```
Parameterized queries send the user's input as *data*, never as part of the
SQL command itself, which makes union-based (and most other) SQL injection
impossible.

Other good practices:
- Use an ORM (SQLAlchemy, Django ORM, etc.) which parameterizes by default.
- Apply least-privilege DB accounts (the app's DB user shouldn't be able to
  read a `users`/`admin` table it doesn't need).
- Add input validation as defense-in-depth (not as your only defense).
- Use a WAF and enable verbose-error suppression in production so error
  messages don't leak schema details.

---
**Reminder:** this app is for local, educational use only. Testing SQL
injection against systems you don't own or don't have explicit written
permission to test is illegal in most jurisdictions.
