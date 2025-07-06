from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")          # <--- Make sure the route string is inside parentheses
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
