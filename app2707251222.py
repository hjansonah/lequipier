import psycopg2
import psycopg2.extras
from flask import Flask, render_template, redirect, url_for, request, jsonify

app = Flask(__name__)

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
    # Your main landing page
    return render_template('index.html')

# --- Coets routes ---

@app.route('/record')
def record():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT "Coet ID" FROM coets_appended ORDER BY "Coet ID" ASC LIMIT 1')
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return redirect(url_for('record_by_id', coet_id=row['Coet ID']))
    else:
        return "No records found", 404

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
        return "Coët not found", 404

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
        return "End of records", 404

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
        return "Start of records", 404

# --- Hometasks routes ---

@app.route('/hometasks')
def hometasks_index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM hometasks ORDER BY id ASC LIMIT 1')
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return redirect(url_for('hometask_by_id', task_id=row['id']))
    else:
        return "No hometasks found", 404

@app.route('/hometasks/<int:task_id>', methods=['GET'])
def hometask_by_id(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, task, "Added date" FROM hometasks WHERE id = %s', (task_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return render_template('hometasks.html', task=row)
    else:
        return "Task not found", 404

@app.route('/hometasks/<int:task_id>', methods=['POST'])
def update_hometask(task_id):
    data = request.form
    task_done = 'task' in data and data['task'] == 'on'

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE hometasks SET task = %s WHERE id = %s', (task_done, task_id))
    conn.commit()
    cur.close()
    conn.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM hometasks WHERE id > %s ORDER BY id ASC LIMIT 1', (task_id,))
    next_task = cur.fetchone()
    cur.close()
    conn.close()

    if next_task:
        return redirect(url_for('hometask_by_id', task_id=next_task['id']))
    else:
        return redirect(url_for('hometask_by_id', task_id=task_id))

@app.route('/hometasks/next/<int:task_id>')
def hometask_next(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM hometasks WHERE id > %s ORDER BY id ASC LIMIT 1', (task_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return redirect(url_for('hometask_by_id', task_id=row['id']))
    else:
        return "No more tasks", 404

@app.route('/hometasks/previous/<int:task_id>')
def hometask_previous(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM hometasks WHERE id < %s ORDER BY id DESC LIMIT 1', (task_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return redirect(url_for('hometask_by_id', task_id=row['id']))
    else:
        return "No previous task", 404

# Other routes you have...

if __name__ == '__main__':
    app.run(debug=True)
