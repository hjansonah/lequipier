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
        query = 'SELECT * FROM "coets_appended" WHERE "last_reviewed" IS NULL ORDER BY "ExtractorCode" ASC LIMIT 1;'
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

        return render_template("recordeditable.html", rows=rows, columns=columns)

    except Exception as e:
        return f"An error occurred: {e}"

@app.route("/update_records", methods=["POST"])
def update_records():
    try:
        data = request.json
        updates = data.get("updates", [])

        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        for row in updates:
            row_id = row.get("ID")
            if not row_id:
                continue

            columns = [k for k in row.keys() if k != "ID" and k != "last_reviewed"]
            values = [row[col] for col in columns]

            set_clause = ", ".join([f'"{col}" = %s' for col in columns])
            if set_clause:
                set_clause += ', '
            set_clause += '"last_reviewed" = NOW()'

            query = f'UPDATE "coets_appended" SET {set_clause} WHERE "ID" = %s'
            cur.execute(query, values + [row_id])

        conn.commit()
        cur.close()
        conn.close()

        # After update, return success and trigger frontend redirect
        return jsonify({"message": "Record updated successfully. Redirecting..."})

    except Exception as e:
        return jsonify({"message": f"Error updating records: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
