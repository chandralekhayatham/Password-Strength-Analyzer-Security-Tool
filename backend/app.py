from pathlib import Path
import sqlite3
from flask import Flask, jsonify, request, send_from_directory

from services.password_analyzer import analyze_password
from services.password_generator import generate_password, generate_passphrase

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "analytics.db"
FRONTEND = ROOT / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS analyses (
            analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER NOT NULL,
            classification TEXT NOT NULL,
            password_length INTEGER NOT NULL,
            unique_character_ratio REAL NOT NULL,
            weakness_count INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS findings (
            finding_id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER NOT NULL,
            finding_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            FOREIGN KEY (analysis_id) REFERENCES analyses(analysis_id)
        );
        """)


def record_safe_metadata(result):
    metrics = result["metrics"]
    with db() as conn:
        cur = conn.execute(
            """INSERT INTO analyses
               (score, classification, password_length, unique_character_ratio, weakness_count)
               VALUES (?, ?, ?, ?, ?)""",
            (result["score"], result["classification"], metrics["length"],
             metrics["unique_character_ratio"], len(result["findings"]))
        )
        analysis_id = cur.lastrowid
        for finding in result["findings"]:
            severity = "high" if any(k in finding.lower() for k in ("common", "personal", "short")) else "medium"
            conn.execute(
                "INSERT INTO findings (analysis_id, finding_type, severity, description) VALUES (?, ?, ?, ?)",
                (analysis_id, finding.split(" ")[0].lower(), severity, finding)
            )


@app.after_request
def security_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.get("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


@app.post("/api/analyze")
def api_analyze():
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")
    if not isinstance(password, str):
        return jsonify({"error": "Password must be text."}), 400
    if len(password) > 128:
        return jsonify({"error": "Password exceeds the 128-character demo limit."}), 400

    context = data.get("context") or {}
    if not isinstance(context, dict):
        context = {}

    # The password is used only for immediate in-memory analysis.
    result = analyze_password(password, context)
    record_safe_metadata(result)
    return jsonify(result)


@app.get("/api/generate-password")
def api_generate_password():
    try:
        length = int(request.args.get("length", 20))
    except ValueError:
        return jsonify({"error": "Length must be a number."}), 400
    return jsonify({"password": generate_password(length)})


@app.get("/api/generate-passphrase")
def api_generate_passphrase():
    return jsonify({"passphrase": generate_passphrase()})


@app.get("/api/dashboard/stats")
def dashboard_stats():
    with db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        avg = conn.execute("SELECT COALESCE(AVG(score), 0) FROM analyses").fetchone()[0]
        rows = conn.execute("SELECT classification, COUNT(*) count FROM analyses GROUP BY classification").fetchall()
        weaknesses = conn.execute(
            "SELECT finding_type, COUNT(*) count FROM findings GROUP BY finding_type ORDER BY count DESC"
        ).fetchall()
        scores = conn.execute("SELECT score FROM analyses ORDER BY created_at ASC").fetchall()
        lengths = conn.execute("SELECT password_length FROM analyses ORDER BY created_at ASC").fetchall()
    distribution = {r["classification"]: r["count"] for r in rows}
    return jsonify({
        "total_analyses": total,
        "average_score": round(avg, 1),
        "strength_distribution": distribution,
        "weakness_frequency": [{"type": r["finding_type"], "count": r["count"]} for r in weaknesses],
        "score_distribution": [r["score"] for r in scores],
        "length_distribution": [r["password_length"] for r in lengths],
    })


@app.get("/api/analytics/weaknesses")
def analytics_weaknesses():
    with db() as conn:
        rows = conn.execute(
            "SELECT finding_type, severity, COUNT(*) count FROM findings GROUP BY finding_type, severity ORDER BY count DESC"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
else:
    init_db()
