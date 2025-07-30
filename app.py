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

# Helper: DB connection
def get_db_connection():
    return psycopg2.connect(**conn_params)


# View a single record
@app.route("/view_record/<int:record_id>")
def view_record(record_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Get record
        cur.execute('SELECT * FROM "coets_appended" WHERE "ID" = %s', (record_id,))
        record = cur.fetchone()
        if not record:
            return f"No record found with ID {record_id}", 404

        # Get column names
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'coets_appended'
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()

        return render_template("record.html", current_record=record, columns=columns)

    except Exception as e:
        return f"An error occurred: {e}", 500

# Navigate to next/previous record
@app.route("/view_record/<direction>/<int:current_id>")
def navigate_record(direction, current_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if direction == "next":
            cur.execute('SELECT "ID" FROM "coets_appended" WHERE "ID" > %s ORDER BY "ID" ASC LIMIT 1', (current_id,))
        elif direction == "prev":
            cur.execute('SELECT "ID" FROM "coets_appended" WHERE "ID" < %s ORDER BY "ID" DESC LIMIT 1', (current_id,))
        else:
            return redirect(url_for("view_record", record_id=current_id))

        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            return redirect(url_for("view_record", record_id=result[0]))
        else:
            return redirect(url_for("view_record", record_id=current_id))  # Stay on same record if no next/prev

    except Exception as e:
        return f"An error occurred: {e}", 500

# Update a single record
@app.route("/update_record", methods=["POST"])
def update_record():
    try:
        data = request.get_json()
        record_id = data.get("ID")

        if not record_id:
            return jsonify({"message": "Missing record ID"}), 400

        # Build update
        columns = [k for k in data if k not in ("ID", "last_reviewed")]
        if not columns:
            return jsonify({"message": "No columns to update."}), 400

        values = [data[col] for col in columns]
        set_clause = ", ".join(f'"{col}" = %s' for col in columns)
        set_clause += ', "last_reviewed" = NOW()'
        values.append(record_id)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f'UPDATE "coets_appended" SET {set_clause} WHERE "ID" = %s', values)

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": f"Record {record_id} updated successfully."})

    except Exception as e:
        return jsonify({"message": f"Error updating record: {e}"}), 500

# Batch update records from table view
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
            set_clause = ", ".join(f'"{col}" = %s' for col in columns)
            set_clause += ', "last_reviewed" = NOW()'

            query = f'UPDATE "coets_appended" SET {set_clause} WHERE "ID" = %s'
            cur.execute(query, values + [row_id])

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Records updated successfully."})

    except Exception as e:
        return jsonify({"message": f"Error updating records: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
