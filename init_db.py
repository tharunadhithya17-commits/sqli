"""
Creates shop.db with two tables:

1. products (3 columns: id, name, price)  -> shown on the search page
2. users    (3 columns: id, username, password) -> the "secret" table
             an attacker will try to reach via UNION SELECT

Having both tables with 3 columns each is what makes the
classic `UNION SELECT id, username, password FROM users` demo work.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "shop.db")

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL
)
""")

cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
""")

products = [
    ("Wireless Mouse", 599.00),
    ("Mechanical Keyboard", 2499.00),
    ("USB-C Hub", 899.00),
    ("27-inch Monitor", 12999.00),
    ("Laptop Stand", 749.00),
]

users = [
    ("admin", "admin@2026!SuperSecret"),
    ("john_doe", "password123"),
    ("priya_r", "trichy_pass99"),
]

cur.executemany("INSERT INTO products (name, price) VALUES (?, ?)", products)
cur.executemany("INSERT INTO users (username, password) VALUES (?, ?)", users)

conn.commit()
conn.close()

print("shop.db created with sample 'products' and 'users' tables.")
