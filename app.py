from flask import Flask
from blueprints.home import home_bp
from blueprints.records import records_bp
from blueprints.nwsl_appended import nwsl_appended_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(home_bp)
app.register_blueprint(records_bp)
app.register_blueprint(nwsl_appended_bp)

if __name__ == "__main__":
    app.run(debug=True)
