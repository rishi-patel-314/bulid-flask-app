import configparser
import json
import multiprocessing
import os

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, Response
from pydantic import BaseModel, ValidationError
import logging
from typing import Dict, Any

# Read configurations from .ini file
config = configparser.RawConfigParser()
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


def config_from_ini(app: Flask):
    """Load configuration and append it to Flask app."""
    try:
        app_config = AppConfig.from_env()
        app.config.update(app_config.model_dump())
        setup_logging(app.config["LOGGING_LEVEL"])
    except ValidationError as e:
        logging.error("Configuration validation failed: %s", e)
        raise


# Define a custom JSONEncoder to handle Numpy and Pandas objects
class AdvancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Handle Numpy arrays
        if isinstance(obj, np.ndarray):
            return obj.tolist()  # Convert to a list
        # Handle Numpy numbers
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()  # Convert to Python scalar
        # Handle Pandas Timestamp
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()  # Convert to ISO format
        # Handle Pandas DataFrame
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient='records')  # Convert to list of dictionaries


# Create Flask App
app = Flask(__name__)

config_from_ini(app)



@app.route("/")
def home():
    return jsonify({"message": "Welcome to the app", "env": app.config["ENV"]})


@app.route('/data')
def get_data():
    # Create some Numpy and Pandas objects
    array = np.array([1, 2, 3])
    number = np.float64(42.42)
    timestamp = pd.Timestamp('2023-12-18 10:00:00')
    dataframe = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})

    # Use json.dumps with the custom encoder to serialize the response
    response_data = {
        "array": array,
        "number": number,
        "timestamp": timestamp,
        "dataframe": dataframe
    }
    response_json = json.dumps(response_data, cls=AdvancedJSONEncoder)
    return Response(response_json, content_type='application/json')


@app.route("/reload-config", methods=["POST"])
def reload_config():
    """Reload configuration dynamically without restarting the app."""
    try:
        config_from_ini(app)
        return jsonify({"message": "Configuration reloaded successfully", "config": app.config}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
