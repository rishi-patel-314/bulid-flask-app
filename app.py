import configparser
import json
import os
import logging
from flask import Flask, jsonify, Response
from flask.json.provider import DefaultJSONProvider
from pydantic import BaseModel, ValidationError
import numpy as np
import pandas as pd
from gevent.pywsgi import WSGIServer

# Read configurations from .ini file
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "configs/app_config.ini"))
ENV = os.environ.get("FLASK_ENV", "dev")  # Default to 'dev' if FLASK_ENV is not set

class AppConfig(BaseModel):
    ENV: str
    DEBUG: bool
    HOST: str
    PORT: int
    LOGGING_LEVEL: str

    class Config:
        populate_by_name = True

    @staticmethod
    def from_env():
        """Load configurations from environment and fallback to .ini"""
        return AppConfig(
            ENV=os.getenv("ENV", config.get(ENV, "env", fallback="dev")),
            DEBUG=os.getenv("DEBUG", config.getboolean(ENV, "debug", fallback="false")),
            HOST=os.getenv("HOST", config.get(ENV, "host", fallback="127.0.0.1")),
            PORT=os.getenv("PORT", config.getint(ENV, "port", fallback=5000)),
            LOGGING_LEVEL=os.getenv(
                "LOGGING_LEVEL", config.get(ENV, "logging_level", fallback="INFO")
            ),
        )

def setup_logging(level: str):
    """Set up logging for the application."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.info("Logging is set up with level: %s", level)

def create_app():
    """Application factory function."""
    app = Flask(__name__)

    # Load configuration
    try:
        app_config = AppConfig.from_env()
        app.config.update(app_config.model_dump())
        setup_logging(app.config["LOGGING_LEVEL"])
    except ValidationError as e:
        logging.error("Configuration validation failed: %s", e)
        raise

    # Define a custom JSONEncoder to handle Numpy and Pandas objects

    class CustomJSONProvider(DefaultJSONProvider):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()  # Convert NumPy array to list
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()  # Convert NumPy scalar to native Python scalar
            elif isinstance(obj, pd.Timestamp):
                return obj.isoformat()  # Convert Pandas Timestamp to ISO string
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict(orient="records")  # Convert DataFrame to dict
            return super().default(obj)  # Call parent class's default method

    app.json = CustomJSONProvider(app)  # Set the custom JSON provider

    @app.route("/")
    def home():
        return jsonify({"message": "Welcome to the app", "env": app.config["ENV"]})

    @app.route("/data")
    def get_data():
        array = np.array([1, 2, 3])
        number = np.float64(42.42)
        timestamp = pd.Timestamp("2023-12-18 10:00:00")
        dataframe = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        response_data = {
            "array": array,
            "number": number,
            "timestamp": timestamp,
            "dataframe": dataframe,
        }
        return jsonify(response_data)

    @app.route("/reload-config", methods=["POST"])
    def reload_config():
        try:
            app_config = AppConfig.from_env()
            app.config.update(app_config.model_dump())
            setup_logging(app.config["LOGGING_LEVEL"])
            return jsonify({"message": "Configuration reloaded successfully", "config": app.config}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"}), 200

    return app

app = create_app()

# Custom CLI command to run the server
@app.cli.command("runserver")
def runserver():
    """Run the application with WSGIServer."""
    host = app.config["HOST"]
    port = app.config["PORT"]
    if app.config["ENV"] == "development":
        app.run(host=host, port=port, debug=app.config["DEBUG"])
    else:
        http_server = WSGIServer((host, port), app)
        logging.info(f"Listening at: {host}:{port}")
        http_server.serve_forever()

if __name__ == "__main__":
    app.run()
