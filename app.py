import configparser
import os
import json
import logging
from flask import Flask, jsonify, Response
from flask.json.provider import DefaultJSONProvider
from flask.cli import with_appcontext
from pydantic import BaseModel, ValidationError
import numpy as np
import pandas as pd
from gevent.pywsgi import WSGIServer

# 1. Configuration Management (SRP)
class AppConfig(BaseModel):
    ENV: str
    DEBUG: bool
    HOST: str
    PORT: int
    LOGGING_LEVEL: str

    @staticmethod
    def from_env():
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), "configs/app_config.ini"))
        env = os.environ.get("FLASK_ENV", "dev")
        return AppConfig(
            ENV=os.getenv("ENV", config.get(env, "env", fallback="dev")),
            DEBUG=os.getenv("DEBUG", config.getboolean(env, "debug", fallback="false")),
            HOST=os.getenv("HOST", config.get(env, "host", fallback="127.0.0.1")),
            PORT=os.getenv("PORT", config.getint(env, "port", fallback=5000)),
            LOGGING_LEVEL=os.getenv(
                "LOGGING_LEVEL", config.get(env, "logging_level", fallback="INFO")
            ),
        )

# 2. Logging Setup (SRP)
def setup_logging(level: str):
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.info("Logging is set up with level: %s", level)

# 3. Custom JSON Provider (SRP, OCP)
class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
        return super().default(obj)

# 4. Flask Application Factory (SRP, DIP)
def create_app():
    app = Flask(__name__)
    app.json = CustomJSONProvider(app)

    # Load and validate configuration
    try:
        app_config = AppConfig.from_env()
        app.config.update(app_config.dict())
        setup_logging(app.config["LOGGING_LEVEL"])
    except ValidationError as e:
        logging.error("Configuration validation failed: %s", e)
        raise

    # Define Routes
    register_routes(app)

    # Register custom CLI commands
    register_cli_commands(app)

    return app

# 5. Route Management (SRP, OCP)
def register_routes(app: Flask):
    @app.route("/")
    def home():
        return jsonify({"message": "Welcome to the app", "env": app.config["ENV"]})

    @app.route("/data")
    def get_data():
        response_data = {
            "array": np.array([1, 2, 3]),
            "number": np.float64(42.42),
            "timestamp": pd.Timestamp("2023-12-18 10:00:00"),
            "dataframe": pd.DataFrame({"A": [1, 2], "B": [3, 4]}),
        }
        return jsonify(response_data)

    @app.route("/reload-config", methods=["POST"])
    def reload_config():
        try:
            app_config = AppConfig.from_env()
            app.config.update(app_config.dict())
            setup_logging(app.config["LOGGING_LEVEL"])
            return jsonify({"message": "Configuration reloaded successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"}), 200

# 6. CLI Command Registration (SRP)
def register_cli_commands(app: Flask):
    @app.cli.command("runserver")
    @with_appcontext
    def runserver():
        """Run the application with WSGIServer."""
        host = app.config["HOST"]
        port = app.config["PORT"]
        if app.config["ENV"] == "dev":
            app.run(host=host, port=port, debug=app.config["DEBUG"])
        else:
            http_server = WSGIServer((host, port), app)
            logging.info(f"Listening at: {host}:{port}")
            http_server.serve_forever()

# Main Entry Point
if __name__ == "__main__":
    app = create_app()
    app.run()
