# Basic API Example

This example demonstrates how to use APIpack to generate a simple API package with two functions:

1. `greet(name: str) -> str`: Returns a greeting message
2. `add_numbers(a: float, b: float) -> float`: Adds two numbers together

The generated package will include:
- REST API (FastAPI)
- Command-line interface (CLI)
- Basic tests
- Documentation

## Prerequisites

- Python 3.8+
- Ollama with Mistral 7B model
- APIpack installed in development mode

## Setup

1. Install APIpack in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

2. Make sure Ollama is running with Mistral 7B model:
   ```bash
   ollama serve &
   ollama pull mistral:7b
   ```

## Running the Example

1. Generate the API package:
   ```bash
   python examples/basic/generate.py
   ```

2. The generated package will be in the `generated/basic-api` directory.

3. Install the generated package in development mode:
   ```bash
   cd generated/basic-api
   pip install -e .
   ```

## Using the Generated API

### REST API

Start the REST API server:
```bash
python -m basic_api.rest.server
```

The API will be available at `http://localhost:8000` with Swagger UI at `http://localhost:8000/docs`.

### CLI

Use the command-line interface:
```bash
# Show help
python -m basic_api.cli --help

# Greet someone
python -m basic_api.cli greet --name World

# Add numbers
python -m basic_api.cli add-numbers --a 5 --b 3
```

## Project Structure

The generated package has the following structure:

```
basic-api/
├── basic_api/           # Main package
│   ├── __init__.py
│   ├── core/            # Core functionality
│   │   ├── __init__.py
│   │   ├── functions.py  # Generated functions
│   │   └── models.py    # Data models
│   ├── rest/            # REST API implementation
│   │   ├── __init__.py
│   │   ├── api.py       # FastAPI routes
│   │   ├── models.py    # Request/response models
│   │   └── server.py    # Server setup
│   └── cli/             # CLI implementation
│       ├── __init__.py
│       └── main.py      # CLI commands
├── tests/               # Tests
│   ├── __init__.py
│   ├── test_functions.py
│   └── test_rest.py
├── pyproject.toml       # Project configuration
├── README.md            # Generated documentation
└── requirements.txt     # Dependencies
```

## Extending the Example

To modify the example:

1. Edit the `config.yml` file to change the API specification
2. Re-run the generation script:
   ```bash
   python examples/basic/generate.py
   ```

## Troubleshooting

- If you get an error about Ollama not running:
  ```bash
  ollama serve &
  ```

- If you get an error about the Mistral model not being available:
  ```bash
  ollama pull mistral:7b
  ```

- For other issues, check the APIpack documentation or file an issue on GitHub.
