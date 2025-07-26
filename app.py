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

def get_db_connection():
    return psycopg2.connect(**conn_params, cursor_factory=psycopg2.extras.RealDictCursor)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/record')
def record():
    # Get the first record by Coet ID
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT "Coet ID" FROM coets_appended ORDER BY "Coet ID" ASC LIMIT 1')
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return redirect(url_for('record_by_id', coet_id=row['Coet ID']))
    else:
        return "Aucun enregistrement trouvé", 404

@app.route('/record/<int:coet_id>')
def record_by_id(coet_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM coets_appended WHERE "Coet ID" = %s', (coet_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return render_template('record.html', row=row)
    else:
        return "Coët non trouvé", 404

@app.route('/next/<int:coet_id>')
def next_record(coet_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM coets_appended WHERE "Coet ID" > %s ORDER BY "Coet ID" ASC LIMIT 1', (coet_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return redirect(url_for('record_by_id', coet_id=row['Coet ID']))
    else:
        return "Fin des enregistrements", 404

@app.route('/previous/<int:coet_id>')
def previous_record(coet_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM coets_appended WHERE "Coet ID" < %s ORDER BY "Coet ID" DESC LIMIT 1', (coet_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return redirect(url_for('record_by_id', coet_id=row['Coet ID']))
    else:
        return "Début des enregistrements", 404

@app.route('/atpgames')
@app.route('/atpgames.html')
def atpgames():
    return render_template('atpgames.html')

@app.route('/silexview')
@app.route('/silexview.html')
def silexview():
    return render_template('silexview.html')

@app.route('/coetstable')
@app.route('/coetstable.html')
def coetstable():
    return render_template('coetstable.html')

@app.route('/')
def index():
    return render_template('hometasks.html')  # <-- serve your file

@app.route('/task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    cur = conn.cursor()
    cur.execute("SELECT id, task, \"Added date\" FROM public.hometasks WHERE id >= %s ORDER BY id LIMIT 1", (task_id,))
    row = cur.fetchone()
    cur.close()
    if row:
        return jsonify({'id': row[0], 'task': row[1], 'added_date': row[2].isoformat()})
    else:
        return jsonify({'message': 'No more tasks'}), 404

@app.route('/task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    data = request.json
    new_task = data.get('task')
    cur = conn.cursor()
    cur.execute("UPDATE public.hometasks SET task = %s WHERE id = %s", (new_task, task_id))
    conn.commit()
    cur.close()
    return jsonify({'message': 'Task updated'})

if __name__ == '__main__':
    app.run(debug=True)