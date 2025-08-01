import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Database connection configuration
conn_params = {
    "host": "dpg-d1l8cgre5dus73fcn8mg-a.frankfurt-postgres.render.com",
    "port": 5432,
    "dbname": "flask_coets_db_0qzt",
    "user": "flask_coets_db_0qzt_user",
    "password": "vx9DALf0LaxT4bRKpsA2GssaxSA8sN16",
    "sslmode": "require"
}

# Route: Display the next unreviewed record
@app.route("/")
def index():
    try:
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM "coets_appended"
                    WHERE "last_reviewed" IS NULL
                    ORDER BY "ID" ASC
                    LIMIT 1;
                """)
                rows = cur.fetchall()

        if not rows:
            return "<h2>Tous les enregistrements ont été traités.</h2>"

        columns = list(rows[0].keys())
        return render_template("recordeditable.html", rows=rows, columns=columns)

    except Exception as e:
        return f"An error occurred: {e}"

# Route: Update a record after review
@app.route("/update_records", methods=["POST"])
def update_records():
    try:
        data = request.get_json()
        updates = data.get("updates", [])

        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                for row in updates:
                    row_id = row.get("ID")
                    if not row_id:
                        continue

                    # Normalize booleans from string to proper boolean type
                    for key, val in row.items():
                        if isinstance(val, str) and val.lower() in ["true", "false"]:
                            row[key] = val.lower() == "true"

                    # Prepare the update
                    columns = [k for k in row if k not in ("ID", "last_reviewed")]
                    values = [row[col] for col in columns]

                    set_clause = ", ".join([f'"{col}" = %s' for col in columns])
                    if set_clause:
                        set_clause += ", "
                    set_clause += '"last_reviewed" = NOW()'

                    query = f'UPDATE "coets_appended" SET {set_clause} WHERE "ID" = %s'
                    cur.execute(query, values + [row_id])

        return jsonify({"message": "Record updated successfully. Redirecting..."})

    except Exception as e:
        return jsonify({"message": f"Error updating records: {e}"}), 500

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
