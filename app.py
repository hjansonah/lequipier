import psycopg2
import psycopg2.extras
from flask import Flask, render_template, redirect, url_for, request, jsonify

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

# Reusable function to get DB connection
def get_db_connection():
    return psycopg2.connect(**conn_params)


@app.route("/")
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute('SELECT * FROM "coets_appended" ORDER BY "ID" DESC LIMIT 50;')
        rows = cur.fetchall()
        columns = list(rows[0].keys()) if rows else []

        cur.close()
        conn.close()

        return render_template("record.html", rows=rows, columns=columns)

    except Exception as e:
        return f"An error occurred: {e}", 500


@app.route("/update_records", methods=["POST"])
def update_records():
    try:
        data = request.get_json()
        updates = data.get("updates", [])

        if not updates:
            return jsonify({"message": "No records to update."}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        for row in updates:
            row_id = row.get("ID")
            if not row_id:
                continue

            columns = [k for k in row.keys() if k not in ("ID", "last_reviewed")]
            if not columns:
                continue

            values = [row[col] for col in columns]

            # Prepare SQL SET clause and append last_reviewed
            set_clause = ", ".join(f'"{col}" = %s' for col in columns)
            set_clause += ', "last_reviewed" = NOW()'

            sql = f'UPDATE "coets_appended" SET {set_clause} WHERE "ID" = %s'
            cur.execute(sql, values + [row_id])

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Records updated successfully."})

    except Exception as e:
        return jsonify({"message": f"Error updating records: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
