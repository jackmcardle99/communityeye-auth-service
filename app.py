from flask import Flask
from flask_cors import CORS
from db import init_database
from blueprints.auth.auth import auth_bp
from blueprints.users.users import users_bp
from config import FLASK_SECRET_KEY, FLASK_DEBUG, FLASK_HOST, FLASK_PORT
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["SECRET_KEY"] = FLASK_SECRET_KEY
    init_database()
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    return app


app = create_app()

if __name__ == "__main__":
    logger.info(
        f"Starting Flask app on {FLASK_HOST}:{FLASK_PORT} with debug={FLASK_DEBUG}"
    )
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)
