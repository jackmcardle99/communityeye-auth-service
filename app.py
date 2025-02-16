from flask import Flask, app
from flask_cors import CORS
from db import init_database
from blueprints.auth.auth import auth_bp



def create_app():
    app = Flask(__name__)
    CORS(app)
    init_database()
    return app





# Initialize Flask app
app = create_app()
app.register_blueprint(auth_bp)

if __name__ == "__main__":
<<<<<<< Updated upstream
    app.run(debug=True)
=======
    app.run(debug=True, host='0.0.0.0', port=5001)
>>>>>>> Stashed changes
