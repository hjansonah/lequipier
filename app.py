import psycopg2
import psycopg2.extras
from flask import Flask, render_template, redirect, url_for, request

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

# Show list of records
@app.route("/")
def index():
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = 'SELECT * FROM "coets_appended" ORDER BY "ID" DESC LIMIT 50;'
        cur.execute(query)
        rows = cur.fetchall()

        columns = list(rows[0].keys()) if rows else []

        cur.close()
        conn.close()

        return render_template("record.html", rows=rows, columns=columns)
    except Exception as e:
        return f"An error occurred: {e}"

# Edit page for a single record
@app.route("/edit/<int:record_id>")
def edit_record(record_id):
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute('SELECT * FROM "coets_appended" WHERE "ID" = %s', (record_id,))
        record = cur.fetchone()

        cur.close()
        conn.close()

        if record:
            return render_template("edit_record.html", record=record)
        else:
            return f"No record found with ID {record_id}"
    except Exception as e:
        return f"An error occurred: {e}"

# Handle update submission
@app.route("/update/<int:record_id>", methods=["POST"])
def update_record(record_id):
    try:
        name = request.form.get("name")
        location = request.form.get("location")
        still_valid = request.form.get("still_valid")

        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        cur.execute("""
            UPDATE "coets_appended"
            SET name = %s, location = %s, still_valid = %s
            WHERE "ID" = %s
        """, (name, location, still_valid, record_id))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("index"))
    except Exception as e:
        return f"An error occurred during update: {e}"

if __name__ == "__main__":
    app.run(debug=True)
