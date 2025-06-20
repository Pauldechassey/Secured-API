# URL Component Parser API

## Description

This project is a FastAPI-based application that receives a URL string and parses it into its components, such as scheme, hostname, port, path, query parameters, and fragment. It includes basic security features such as rate limiting and input validation.

## Prerequisites

* Python 3.8+
* pip
* Git (for cloning the repo)

## Installation

1. Clone this repository:

   ```bash
   git clone https://gitlab.com/epf-cachan/tp1-sujet-d.git
   cd tp1-sujet-d
   ```
2. Create and activate a Python virtual environment:

   ```bash
   python -m venv venv
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows (PowerShell/cmd):
   venv\Scripts\activate
   ```
3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To run the FastAPI application locally using Uvicorn:

```bash
uvicorn main:app --reload
```

The application will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000). The interactive API documentation (Swagger UI) can be found at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## API Endpoints

### `POST /parse_url` (limited to 120 requests/minute)

* **Description**: Parses the input URL into its components.
* **Request Body**:

```json
{
  "url": "https://www.example.com:8080/path?param=value#frag"
}
```

* **Response (200 OK)**:

```json
{
  "original_url": "https://www.example.com:8080/path?param=value#frag",
  "scheme": "https",
  "netloc": "www.example.com:8080",
  "hostname": "www.example.com",
  "port": 8080,
  "path": "/path",
  "query_string": "param=value",
  "query_params": {"param": ["value"]},
  "fragment": "frag"
}
```

### `POST /is_secure`

* **Description**: Verifies if a given URL uses the HTTPS protocol.
* **Request Body**:

```json
{
  "url": "https://secure.example.com"
}
```

* **Response**:

```json
{
  "is_secure": true
}
```

### `GET /health_url_parser`

* **Description**: Basic health check for the API.
* **Response**:

```json
{
  "status_url_parser": "ok"
}
```

## Project Structure

* `main.py`: Contains the FastAPI application logic for parsing URLs.
* `requirements.txt`: Lists the Python dependencies.
* `tests/`: Contains automated tests using `pytest`.
* `.gitlab-ci.yml`: Defines the GitLab CI/CD pipeline.
* `README.md`: This documentation file.

## Tests

* Complex URL parsing
* Simple HTTP URL
* Query-only URL
* `mailto:` URL
* IP-based URL
* HTTPS security check
* Validation error cases (invalid format or missing payload)

Run tests with:

```bash
pytest
```

## Security Audits

### pip-audit (SCA)

* ✅ No known vulnerabilities found.
* Screenshot:
  ![pip-audit result](./Capture%20d'écran%202025-05-19%20222537.png)

### bandit (SAST)

* ⚠️ Binding to 0.0.0.0 (development convenience; not recommended in production)
* ℹ️ Use of `assert` in tests is acceptable.
* Screenshot:
  ![bandit result](./Capture%20d'écran%202025-05-19%20222924.png)

### Liaison https

* Création d'un certificat pour la démonstration. Cela permet d'éviter que le mot de passese déplace en clair, étant donc visible pour un attaquant en position de MITM. 
Cependant, étant signé à la main, selon le browser utilisé, il se peut qu'il y ai un message d'erreur, signalant l'usage de 'faux' certificats.

## Authors

This project was developed as part of the EPF cybersecurity curriculum.
