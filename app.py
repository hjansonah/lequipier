import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Database connection parameters
conn_params = {
    "host": "dpg-d1l8cgre5dus73fcn8mg-a.frankfurt-postgres.render.com",
    "port": 5432,
    "dbname": "flask_coets_db_0qzt",
    "user": "flask_coets_db_0qzt_user",
    "password": "vx9DALf0LaxT4bRKpsA2GssaxSA8sN16",
    "sslmode": "require"
}

@app.route("/")
def index():
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Fetch the next record with last_reviewed IS NULL
        query = 'SELECT * FROM "coets_appended" WHERE "last_reviewed" IS NULL ORDER BY "ID" ASC LIMIT 1;'
        cur.execute(query)
        rows = cur.fetchall()

        if rows:
            columns = list(rows[0].keys())
        else:
            columns = []

        cur.close()
        conn.close()

        if not rows:
            return "<h2>Tous les enregistrements ont été traités.</h2>"

        return render_template("record.html", rows=rows, columns=columns)

    except Exception as e:
        return f"An error occurred: {e}"

@app.route("/update_records", methods=["POST"])
def update_records():
    try:
        data = request.json
        updates = data.get("updates", [])

        conn = psycopg2.connect(**conn_params)
