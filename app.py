from flask import Flask, render_template

app = Flask(__name__)

@app.route('/record')
def record():
    return render_template('record.html')

# Optional: homepage
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
