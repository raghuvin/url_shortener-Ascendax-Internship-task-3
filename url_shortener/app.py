from flask import Flask, render_template, request, redirect
import sqlite3
import string
import random
import os

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static'))

# Initialize DB
def init_db():
    with sqlite3.connect("urls.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original TEXT NOT NULL,
                short TEXT UNIQUE NOT NULL
            )
        """)

# Generate random short code
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

@app.route('/', methods=["GET", "POST"])
def index():
    short_url = None
    recent_urls = []

    if request.method == "POST":
        original_url = request.form.get("original_url")
        short_code = generate_short_code()
        with sqlite3.connect("urls.db") as conn:
            try:
                conn.execute("INSERT INTO urls (original, short) VALUES (?, ?)", (original_url, short_code))
                conn.commit()
                short_url = request.host_url + short_code
            except sqlite3.IntegrityError:
                short_url = "Error: Short URL already exists."

    with sqlite3.connect("urls.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT original, short FROM urls ORDER BY id DESC LIMIT 5")
        recent_urls = cursor.fetchall()

    return render_template("index.html", short_url=short_url, recent_urls=recent_urls)

@app.route('/<short_code>')
def redirect_short_url(short_code):
    with sqlite3.connect("urls.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT original FROM urls WHERE short = ?", (short_code,))
        row = cursor.fetchone()
        if row:
            return redirect(row[0])
        return "URL not found", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
