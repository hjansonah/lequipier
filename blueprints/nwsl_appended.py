import psycopg2
import psycopg2.extras
from flask import Blueprint, render_template, request, jsonify

records_bp = Blueprint('nwsl_appended', __name__)

# Database connection parameters
conn_params = {
    "host": "dpg-d1l8cgre5dus73fcn8mg-a.frankfurt-postgres.render.com",
    "port": 5432,
    "dbname": "flask_coets_db_0qzt",
    "user": "flask_coets_db_0qzt_user",
    "password": "vx9DALf0LaxT4bRKpsA2GssaxSA8sN16",
    "sslmode": "require"
}

@nwsl_appended_bp.route("/nwsl_appended")
def nwsl_appended():
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = 'SELECT * FROM "nwsl_appended";'
        cur.execute(query)
        rows = cur.fetchall()
        columns = list(rows[0].keys()) if rows else []

        cur.close()
        conn.close()

        if not rows:
            return "<h2>Tous les enregistrements ont été traités.</h2>"

        return render_template("nwsl_appended.html", rows=rows, columns=columns)

    except Exception as e:
        return f"An error occurred: {e}"

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Record updated successfully. Redirecting..."})

    except Exception as e:
        return jsonify({"message": f"Error updating records: {e}"}), 500
