from flask import Flask, Response
import json
import numpy as np
import pandas as pd
import configparser


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
        return super().default(obj)


# Function to load configuration from an INI file
def config_from_ini(app, filename='configs/app_config.ini'):
    config = configparser.ConfigParser()
    config.read(filename)

    # Load general configurations from the 'general' section of the .ini file
    app.config['DEBUG'] = config.getboolean('general', 'DEBUG')
    app.config['SECRET_KEY'] = config.get('general', 'SECRET_KEY')


# Create Flask app
app = Flask(__name__)

# Load configuration from the INI file
config_from_ini(app)

@app.route('/')
def home():
    response_data = {'api':'home of application'}
    response_json = json.dumps(response_data, cls=AdvancedJSONEncoder)
    return Response(response_json , content_type='application/json')


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


if __name__ == '__main__':
    # Run the Flask application with the configuration loaded from the INI file
    app.run(debug=app.config['DEBUG'])
