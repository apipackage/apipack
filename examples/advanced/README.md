# Advanced TODO API Example

This example demonstrates the full power of APIpack by generating a complete TODO API with multiple interfaces and language support.

## 🌟 Features

### Core Functionality
- **CRUD Operations** for TODO items
- **Rich Data Model** with validation
- **Multi-language Support** (Python, JavaScript, Go, Rust)

### Interface Support
- **REST API** (FastAPI)
- **gRPC** for high-performance services
- **GraphQL** for flexible queries
- **WebSocket** for real-time updates
- **CLI** for command-line usage

### Advanced Features
- **Authentication & Authorization**
- **Database Integration** (SQL with migrations)
- **API Documentation** (OpenAPI/Swagger)
- **Testing Framework**
- **Docker & Kubernetes** support
- **Monitoring & Observability**

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Ollama with Mistral 7B model
- APIpack installed in development mode

### Installation

1. Install APIpack in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

2. Make sure Ollama is running with Mistral 7B model:
   ```bash
   ollama serve &
   ollama pull mistral:7b
   ```

### Generate the API

Run the example generator:
```bash
python examples/advanced/generate.py
```

This will generate API implementations in all supported languages in the `generated/advanced-todo` directory.

## 📁 Project Structure

```
generated/advanced-todo/
├── python/
│   ├── todo_api/            # Python package
│   │   ├── api/             # API endpoints
│   │   ├── core/            # Business logic
│   │   ├── db/              # Database models
│   │   ├── schemas/         # Pydantic models
│   │   └── main.py          # Application entry point
│   ├── tests/               # Test suite
│   ├── Dockerfile           # Container configuration
│   ├── pyproject.toml       # Project metadata
│   └── README.md            # Python-specific docs
│
├── javascript/
│   ├── src/                 # Source code
│   ├── test/                # Tests
│   ├── package.json         # Dependencies
│   └── Dockerfile           # Container config
│
├── go/
│   ├── cmd/                # CLI and main package
│   ├── internal/            # Internal packages
│   ├── pkg/                 # Library code
│   └── go.mod               # Go modules
│
└── rust/
    ├── src/                # Source code
    ├── tests/              # Integration tests
    └── Cargo.toml          # Rust package config
```

## 🛠️ Using the Generated APIs

### Python (FastAPI)

```bash
# Navigate to Python implementation
cd generated/advanced-todo/python

# Install dependencies
poetry install

# Run the development server
poetry run uvicorn todo_api.main:app --reload

# Access the API documentation at http://localhost:8000/docs
```

### JavaScript (Express)

```bash
# Navigate to JavaScript implementation
cd generated/advanced-todo/javascript

# Install dependencies
npm install

# Start the server
npm start

# Access the API at http://localhost:3000
```

### Go

```bash
# Navigate to Go implementation
cd generated/advanced-todo/go

# Build and run
go run cmd/server/main.go

# Access the API at http://localhost:8080
```

### Rust

```bash
# Navigate to Rust implementation
cd generated/advanced-todo/rust

# Build and run
cargo run --release

# Access the API at http://localhost:7878
```

## 🔌 Available Endpoints

### REST API
- `GET /api/todos` - List all TODOs
- `POST /api/todos` - Create a new TODO
- `GET /api/todos/{id}` - Get a TODO by ID
- `PUT /api/todos/{id}` - Update a TODO
- `DELETE /api/todos/{id}` - Delete a TODO

### GraphQL
```graphql
type Query {
  todos(status: String, priority: String): [Todo!]!
  todo(id: ID!): Todo
}

type Mutation {
  createTodo(input: CreateTodoInput!): Todo!
  updateTodo(id: ID!, input: UpdateTodoInput!): Todo!
  deleteTodo(id: ID!): Boolean!
}
```

### gRPC
```protobuf
service TodoService {
  rpc ListTodos (ListTodosRequest) returns (ListTodosResponse);
  rpc GetTodo (GetTodoRequest) returns (Todo);
  rpc CreateTodo (CreateTodoRequest) returns (Todo);
  rpc UpdateTodo (UpdateTodoRequest) returns (Todo);
  rpc DeleteTodo (DeleteTodoRequest) returns (google.protobuf.Empty);
}
```

## 🔍 Testing

Each language implementation includes a comprehensive test suite:

```bash
# Python
cd generated/advanced-todo/python
poetry run pytest

# JavaScript
cd generated/advanced-todo/javascript
npm test

# Go
cd generated/advanced-todo/go
go test ./...

# Rust
cd generated/advanced-todo/rust
cargo test
```

## 🐳 Docker Support

Each implementation includes a Dockerfile for containerization:

```bash
# Build the image
docker build -t todo-api-python -f python/Dockerfile .

# Run the container
docker run -p 8000:8000 todo-api-python
```

## 📊 Monitoring

The generated API includes built-in monitoring:
- Prometheus metrics at `/metrics`
- Health checks at `/health`
- OpenTelemetry tracing
- Structured logging

## 🔄 CI/CD

Pre-configured CI/CD pipelines are included for:
- GitHub Actions
- GitLab CI
- Docker Hub / GitHub Container Registry
- Kubernetes deployment

## 🚀 Deployment

### Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

### Serverless (AWS Lambda, Google Cloud Functions, Azure Functions)

Each implementation includes serverless configuration files for easy deployment to cloud providers.

## 📚 Documentation

- **API Documentation**: Auto-generated OpenAPI/Swagger UI
- **Architecture**: High-level design decisions
- **Development Guide**: Contributing and extending the API
- **Deployment Guide**: Production deployment instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
