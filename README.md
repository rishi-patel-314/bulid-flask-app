# Flask Application

This Flask application is designed with modularity and maintainability in mind, adhering to the SOLID principles and common design patterns. It includes support for custom configurations, structured logging, and extensible JSON serialization for handling NumPy and Pandas objects.

---

## Features

- **Custom Configuration Management:** Load configurations from `.ini` files or environment variables.
- **Structured Logging:** Setup logging dynamically based on configuration.
- **Custom JSON Serialization:** Handle NumPy arrays, Pandas DataFrames, and timestamps seamlessly.
- **Health Checks:** Basic health endpoint to verify application status.
- **CLI Commands:** Enhanced server management using Flask CLI.
- **Scalability:** Application factory pattern for easy extension and modularity.

---

## Installation

### Prerequisites

- Python 3.8 or later
- pip (Python package manager)

### Steps

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the application:
   - Update the `configs/app_config.ini` file with the desired settings.
   - Alternatively, set environment variables (e.g., `FLASK_ENV`, `DEBUG`, `HOST`, `PORT`).

---

## Configuration

Configurations are loaded from the following sources:

1. `.ini` file located in the `configs` folder.
2. Environment variables (take precedence over `.ini` settings).

Example `.ini` file:
```ini
[dev]
env = dev
debug = true
host = 127.0.0.1
port = 5000
logging_level = INFO

[prod]
env = prod
debug = false
host = 0.0.0.0
port = 8080
logging_level = WARNING
```

---

## Usage

### Run the Application

1. Start the Flask development server:
   ```bash
   flask run
   ```

2. Start the production server with Gevent:
   ```bash
   flask runserver
   ```

### Endpoints

- **Home (`/`):**
  ```json
  {
      "message": "Welcome to the app",
      "env": "<current environment>"
  }
  ```

- **Data (`/data`):**
  Returns serialized NumPy and Pandas objects.

- **Reload Config (`/reload-config`):**
  Reloads application configuration dynamically.

- **Health (`/health`):**
  Returns `{"status": "healthy"}` if the application is running.

---

## Code Structure

### Key Components

| Component               | Responsibility                                                                 |
|-------------------------|-------------------------------------------------------------------------------|
| `AppConfig`             | Manages application configuration loading and validation.                    |
| `setup_logging`         | Configures application logging dynamically.                                   |
| `CustomJSONProvider`    | Custom JSON serializer for NumPy and Pandas objects.                         |
| `create_app`            | Application factory for creating and initializing the Flask app.             |
| `register_routes`       | Defines all application routes.                                              |
| `register_cli_commands` | Adds custom CLI commands for managing the server.                            |

### Code Flow

1. **Configuration Management:**
   - Reads configurations from `.ini` file or environment variables.
   - Validates using `pydantic`.

2. **Application Initialization:**
   - Sets up logging based on configuration.
   - Installs a custom JSON provider for extended serialization.
   - Registers routes and CLI commands.

3. **Execution:**
   - Runs in development mode using Flask's built-in server.
   - Runs in production mode with Gevent WSGI server.

---

## Extensibility

- **Adding Routes:**
  Define new routes in the `register_routes` function or use Flask Blueprints for larger applications.

- **Enhancing Configuration:**
  Extend the `AppConfig` model to include additional settings.

- **Improving Serialization:**
  Extend the `CustomJSONProvider` to support additional data types.

---

## Testing

### Unit Tests

1. Install testing dependencies:
   ```bash
   pip install pytest flask-testing
   ```

2. Run the tests:
   ```bash
   pytest
   ```

Example test for `/data` endpoint:
```python
def test_get_data(client):
    response = client.get("/data")
    assert response.status_code == 200
    data = response.json
    assert "array" in data
    assert "number" in data
    assert "timestamp" in data
    assert "dataframe" in data
```

---

## Deployment

### Docker

1. Build the Docker image:
   ```bash
   docker build -t flask-app .
   ```

2. Run the container:
   ```bash
   docker run -p 5000:5000 flask-app
   ```

### Kubernetes

1. Create a deployment and service YAML file.
2. Apply the configuration:
   ```bash
   kubectl apply -f deployment.yaml
   ```

---


# Flask Application

This is a Flask-based web application designed with principles of the SOLID design pattern and includes custom configurations, routes, logging, and CLI commands.

---

## Features

- **Configuration Management**: Uses Pydantic for environment-based configuration validation.
- **Custom JSON Provider**: Handles NumPy and Pandas data serialization.
- **Health Check**: Simple health endpoint.
- **Dynamic Config Reloading**: Reload configurations without restarting the app.
- **Custom CLI Command**: Includes a CLI to run the server using Gevent.
- **Logging**: Configurable logging levels.

---

## Requirements

- Python 3.9+
- Flask
- Pydantic
- NumPy
- Pandas
- Gevent

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a configuration file:
   - Navigate to the `configs/` directory.
   - Create a file named `app_config.ini` and add environment-specific configurations:
     ```ini
     [dev]
     env = dev
     debug = true
     host = 127.0.0.1
     port = 5000
     logging_level = INFO
     ```

---

## Usage

### Running Locally

1. Start the application:
   ```bash
   python app.py
   ```

2. Access the application at:
   ```
   http://127.0.0.1:5000/
   ```

### CLI Commands

- Run the server:
  ```bash
  flask runserver
  ```

### Endpoints

| Endpoint           | Method | Description                              |
|--------------------|--------|------------------------------------------|
| `/`                | GET    | Welcome message with environment info.  |
| `/data`            | GET    | Returns example NumPy and Pandas data.  |
| `/reload-config`   | POST   | Reload application configurations.       |
| `/health`          | GET    | Health status of the application.       |

---

## Deployment

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t flask-app .
   ```

2. Run the container:
   ```bash
   docker run -p 5000:5000 flask-app
   ```

3. Access the application at:
   ```
   http://localhost:5000/
   ```

### Using Kubernetes

1. Apply Kubernetes manifests:
   ```bash
   kubectl apply -f deployment.yaml
   kubectl apply -f service.yaml
   ```

2. Check the status:
   ```bash
   kubectl get pods
   kubectl get svc
   ```

---

## Testing

1. Run unit tests using `unittest`:
   ```bash
   python -m unittest discover tests
   ```

2. Run tests using `pytest`:
   ```bash
   pytest
   ```


---

## Contributing

Contributions are welcome! Please follow the standard fork, branch, commit, and pull request workflow:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push the branch:
   ```bash
   git push origin feature-name
   ```
5. Create a pull request.

---

## Contact

For issues or questions, contact [Your Name/Team] at [your_email@example.com].



## License

This project is licensed under the MIT License. See the LICENSE file for details.

