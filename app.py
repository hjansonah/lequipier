import psycopg2
from flask import Flask, render_template

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
    conn = psycopg2.connect(**conn_params)
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/record')
@app.route('/record.html')
def record():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM coets_appended LIMIT 50;')
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Pass the rows to the template
    return render_template('record.html', records=rows)

@app.route('/atpgames')
@app.route('/atpgames.html')
def atpgames():
    return render_template('atpgames.html')

if __name__ == '__main__':
    app.run(debug=True)
