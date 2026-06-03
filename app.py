import sqlite3
from flask import Flask, request, redirect, url_for, jsonify

app = Flask(__name__, static_folder="static")
DB_PATH = "data.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                bio TEXT,
                prenom TEXT,
                ville TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        existing_columns = [row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
        if "bio" not in existing_columns:
            conn.execute("ALTER TABLE users ADD COLUMN bio TEXT")
        if "prenom" not in existing_columns:
            conn.execute("ALTER TABLE users ADD COLUMN prenom TEXT")
        if "ville" not in existing_columns:
            conn.execute("ALTER TABLE users ADD COLUMN ville TEXT")

        conn.commit()


@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/form")
def form_page():
    return app.send_static_file("form.html")


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    bio = request.form.get("bio", "").strip()
    prenom = request.form.get("prenom", "").strip()
    ville = request.form.get("ville", "").strip()

    if not name or not email:
        return redirect(url_for("form_page"))

    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO users (name, email, bio, prenom, ville) VALUES (?, ?, ?, ?, ?)",
            (name, email, bio, prenom, ville),
        )
        conn.commit()

    return redirect(url_for("users", submitted=1))


@app.route("/users")
def users():
    return app.send_static_file("user.html")


@app.route("/users-data")
def users_data():
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, email, bio, prenom, ville, created_at FROM users ORDER BY id DESC"
        ).fetchall()
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    init_db()
    app.run(debug=True) 