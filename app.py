from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/record')
@app.route('/record.html')   # Add this to serve at /record.html too
def record():
    return render_template('record.html')

if __name__ == '__main__':
    app.run(debug=True)
