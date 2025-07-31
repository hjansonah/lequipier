import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# PostgreSQL connection (Render)
conn_params = {
    "host": "dpg-d1l8cgre5dus73fcn8mg-a.frankfurt-postgres.render.com",
    "port": 5432,
    "dbname": "flask_coets_db_0qzt",
    "user": "flask_coets_db_0qzt_user",
    "password": "vx9DALf0LaxT4bRKpsA2GssaxSA8sN16",
    "sslmode": "require"
}

# Get a single record by ID
def get_record_by_id(record_id):
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('SELECT * FROM "coets_appended" WHERE "ID" = %s', (record_id,))
            return cur.fetchone()

# Route: View + edit a single record
@app.route('/record/<int:record_id>')
def show_record(record_id):
    record = get_record_by_id(record_id)
    if not record:
        return f"No record found with ID {record_id}", 404
    return render_template("record.html", record=record)

# Route: Save changes
@app.route("/update_record", methods=["POST"])
def update_record():
    try:
        data = request.json
        record_id = data.get("ID")
        if not record_id:
            return jsonify({"message": "Missing record ID."}), 400

        columns = [k for k in data.keys() if k != "ID" and k != "last_reviewed"]
        values = [data[col] for col in columns]

        set_clause = ", ".join([f'"{col}" = %s' for col in columns])
        if set_clause:
            set_clause += ', '
        set_clause += '"last_reviewed" = NOW()'

        query = f'UPDATE "coets_appended" SET {set_clause} WHERE "ID" = %s'

        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query, values + [record_id])
                conn.commit()

        return jsonify({"message": "Record updated successfully."})
    except Exception as e:
        return jsonify({"message": f"Error updating record: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
