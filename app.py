from flask import Flask, app
from blueprints.users import users_bp
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)

app.register_blueprint(users_bp)

@app.before_request
def initialise_database():
    flyway_command = ['flyway', '-configFiles=flyway.conf', 'migrate']
    subprocess.run(flyway_command, check=True)

if __name__ == "__main__":
    app.run(debug=True)