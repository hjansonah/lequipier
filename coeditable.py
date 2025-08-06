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

@app.route("/")
def index():
    return navigate_record(direction="next", current_id=None)

@app.route("/navigate")
def navigate():
    direction = request.args.get("direction")
    current_id = request.args.get("current_id")
    return navigate_record(direction, current_id)

def navigate_record(direction, current_id):
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        if current_id:
            # Mark current record as reviewed
            cur.execute(
                'UPDATE "coets_appended" SET "last_reviewed" = NOW() WHERE "ID" = %s;',
                (current_id,)
            )
            conn.commit()

        if direction == "next":
            query = '''
                SELECT * FROM "coets_appended"
                WHERE ("ID" > %s OR %s IS NULL)
                AND "last_reviewed" IS NULL
                ORDER BY "ID" ASC
                LIMIT 1;
            '''
            params = (current_id, current_id)
        else:
            query = '''
                SELECT * FROM "coets_appended"
                WHERE "ID" < %s
                AND "last_reviewed" IS NULL
                ORDER BY "ID" DESC
                LIMIT 1;
            '''
            params = (current_id,)

        cur.execute(query, params)
        rows = cur.fetchall()
        columns = list(rows[0].keys()) if rows else []

        cur.close()
        conn.close()

        if not rows:
            return "<h2>Fin de la liste.</h2>"

        return render_template("recordeditable.html", rows=rows, columns=columns)

    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/update_records', methods=['POST'])
def update_records():
    try:
        # Debug log raw request data
        print("RAW PAYLOAD:", request.get_data(as_text=True))

        data = request.get_json()
        print("Parsed JSON:", data)

        updates = data.get('updates', [])
        if not updates:
            return jsonify({"error": "No updates received"}), 400

        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        for row in updates:
            id_ = row.get('ID')
            if not id_:
                continue

            columns = []
            values = []

            for key, val in row.items():
                if key == 'ID':
                    continue
                if key == 'Still valid':
                    val = True if str(val).lower() in ['true', '1'] else False
                columns.append(f'"{key}" = %s')
                values.append(val)

            if columns:
                query = f'UPDATE "coets_appended" SET {", ".join(columns)} WHERE "ID" = %s;'
                values.append(id_)
                print("Executing SQL:", query)
                print("With values:", values)
                cur.execute(query, values)
                print(f"Updated rows: {cur.rowcount}")

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "success"})

    except Exception as e:
        print("ERROR in update_records:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

i can modify it on the web, but the change doesn't appear afterward in the database (postgresssql)