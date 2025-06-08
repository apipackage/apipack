# APIpack 🚀

**Automated API Package Generator with LLM Integration**

APIpack is a powerful framework that generates complete API packages from function specifications using local LLM models (Mistral 7B) and customizable templates. Focus on writing business logic while APIpack handles all the interface boilerplate.

## ✨ Features

- **🤖 LLM-Powered**: Uses Mistral 7B for intelligent function generation
- **🎯 Multi-Interface**: Generates REST, gRPC, GraphQL, WebSocket, and CLI interfaces
- **🌐 Multi-Language**: Supports Python, JavaScript, Go, Rust, and more
- **📦 Template System**: Extensible template engine with built-in and custom templates
- **🔌 Plugin Architecture**: Easy to extend with custom interfaces and generators
- **🐳 Deployment Ready**: Includes Docker, Kubernetes, and CI/CD configurations
- **🧪 Test Generation**: Automatically generates comprehensive test suites
- **📚 Documentation**: Auto-generates API docs, README files, and examples

## 🚀 Quick Start

### Installation

```bash
pip install apipack
```

### Prerequisites

1. **Install Ollama** (for local LLM):
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral:7b
```

2. **Start Ollama server**:
```bash
ollama serve
```

### Generate Your First API Package

1. **Create a function specification**:
```bash
apipack init --name pdf_to_text --description "Extract text from PDF files"
```

2. **Edit the generated `function_spec.yml`**:
```yaml
name: pdf_to_text
description: Extract text from PDF files
input_type: bytes
output_type: string
interfaces:
  - rest
  - grpc
  - cli
dependencies:
  - PyPDF2>=3.0.0
```

3. **Generate the package**:
```bash
apipack generate function_spec.yml --language python --output ./my-pdf-service
```

4. **Build and run**:
```bash
cd my-pdf-service
docker build -t pdf-service .
docker run -p 8080:8080 pdf-service
```

5. **Test your API**:
```bash
curl -X POST -F "file=@document.pdf" http://localhost:8080/extract
```

## 📋 Example Specifications

### Simple Function
```yaml
name: image_resize
description: Resize images to specified dimensions
input_type: bytes
output_type: bytes
parameters:
  - name: image_data
    type: bytes
    required: true
  - name: width
    type: int
    default: 800
  - name: height
    type: int
    default: 600
interfaces:
  - rest
  - cli
```

### Complex Service
```yaml
project:
  name: document-processor
  description: Multi-format document processing service

functions:
  - name: pdf_to_text
    description: Extract text from PDF
    input_type: bytes
    output_type: string
    
  - name: html_to_pdf
    description: Convert HTML to PDF
    input_type: string
    output_type: bytes
    
  - name: image_to_text
    description: OCR for images
    input_type: bytes
    output_type: string

interfaces: [rest, grpc, websocket]
language: python
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Function      │    │   Mistral 7B    │    │   Templates     │
│ Specifications  │───▶│   (Logic Gen)   │    │  (Interfaces)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────────────────────────┐
                       │         APIpack Engine             │
                       │  ┌─────────────┐ ┌─────────────┐   │
                       │  │   Parser    │ │  Generator  │   │
                       │  └─────────────┘ └─────────────┘   │
                       │  ┌─────────────┐ ┌─────────────┐   │
                       │  │ Validator   │ │  Deployer   │   │
                       │  └─────────────┘ └─────────────┘   │
                       └─────────────────────────────────────┘
                                        │
                                        ▼
                       ┌─────────────────────────────────────┐
                       │        Generated Package           │
                       │  ┌─────────┐ ┌─────────┐ ┌──────┐  │
                       │  │   REST  │ │  gRPC   │ │ CLI  │  │
                       │  └─────────┘ └─────────┘ └──────┘  │
                       └─────────────────────────────────────┘
```

## 🛠️ CLI Commands

### Core Commands

```bash
# Generate package from specification
apipack generate spec.yml --language python --interfaces rest,grpc

# Validate specification file
apipack validate spec.yml

# Initialize new specification
apipack init --name my_function

# List available templates
apipack templates

# Show current configuration
apipack config

# Health check
apipack health
```

### Advanced Usage

```bash
# Generate with custom output directory
apipack generate spec.yml -o ./custom-output --language go

# Dry run (preview without generating)
apipack generate spec.yml --dry-run

# Build generated package
apipack build ./generated-package --type docker --push

# Generate with specific interfaces
apipack generate spec.yml -i rest -i grpc -i websocket
```

## 🎯 Supported Interfaces

| Interface | Description | Status |
|-----------|-------------|--------|
| **REST** | HTTP/JSON API with OpenAPI docs | ✅ |
| **gRPC** | High-performance RPC | ✅ |
| **GraphQL** | Query language API | ✅ |
| **WebSocket** | Real-time bidirectional communication | ✅ |
| **CLI** | Command-line interface | ✅ |
| **Async** | Async/await patterns | 🚧 |

## 🌐 Supported Languages

| Language | Status | Features |
|----------|--------|----------|
| **Python** | ✅ | FastAPI, asyncio, type hints |
| **JavaScript** | ✅ | Express, async/await, ESM |
| **TypeScript** | ✅ | Type safety, decorators |
| **Go** | ✅ | Goroutines, channels, modules |
| **Rust** | 🚧 | Memory safety, performance |
| **Java** | 🚧 | Spring Boot, annotations |

## 📦 Template System

APIpack uses a flexible template system that can be extended:

### Built-in Templates

```
templates/
├── interfaces/
│   ├── rest/           # REST API templates
│   ├── grpc/           # gRPC service templates
│   ├── graphql/        # GraphQL schema templates
│   └── cli/            # CLI application templates
├── languages/
│   ├── python/         # Python-specific templates
│   ├── javascript/     # JavaScript-specific templates
│   └── go/             # Go-specific templates
└── deployment/
    ├── docker/         # Docker configurations
    ├── kubernetes/     # K8s manifests
    └── ci/             # CI/CD pipelines
```

### Custom Templates

Create custom templates in `~/.apipack/templates/`:

```yaml
# ~/.apipack/templates/my-interface/template.yml
name: my-interface
category: interface
language: python
description: Custom interface template

files:
  - src: server.py.j2
    dest: "{{ interface_type }}/server.py"
  - src: client.py.j2
    dest: "{{ interface_type }}/client.py"
```

## ⚙️ Configuration

### Global Configuration

Create `~/.apipack/config.yml`:

```yaml
llm:
  provider: mistral
  model: mistral:7b
  temperature: 0.1
  max_tokens: 2048

templates:
  auto_discover: true
  cache_enabled: true
  validation_level: strict

output:
  format: package
  include_tests: true
  include_docs: true
```

### Project Configuration

Create `project.apipack.yml` in your project:

```yaml
name: my-api-service
language: python
interfaces:
  - rest
  - grpc

functions:
  - spec: functions/pdf_processor.yml
  - spec: functions/image_resizer.yml

deployment:
  docker:
    base_image: python:3.11-slim
  kubernetes:
    replicas: 3
```

## 🔌 Plugin Development

Create custom plugins to extend APIpack:

```python
# plugins/my_plugin.py
from apipack.plugins import BasePlugin

class MyInterfacePlugin(BasePlugin):
    name = "my-interface"
    
    def generate(self, function_specs, language, output_dir):
        # Custom generation logic
        return generated_files
    
    def validate(self, generated_files):
        # Custom validation logic
        return validation_result
```

Register plugin:

```python
from apipack.plugins import register_plugin
register_plugin(MyInterfacePlugin())
```

## 📊 Examples

### PDF Processing Service

```bash
git clone https://github.com/apipack/examples
cd examples/pdf-processor
apipack generate config.yml
docker-compose up
```

### Image Resize API

```bash
apipack init --name image_resize
# Edit function_spec.yml
apipack generate function_spec.yml --language go --interfaces rest,grpc
```

### Multi-Function Service

```yaml
# multi-service.yml
project:
  name: document-tools
  
functions:
  - name: pdf_to_text
    input_type: bytes
    output_type: string
    
  - name: html_to_pdf  
    input_type: string
    output_type: bytes
    
  - name: compress_image
    input_type: bytes
    output_type: bytes

interfaces: [rest, grpc]
language: python
```

## 🧪 Testing

Generated packages include comprehensive tests:

```bash
# Run tests in generated package
cd generated-package
pytest tests/ --cov=src --cov-report=html

# Integration tests
python -m pytest tests/integration/

# Load tests
locust -f tests/load/locustfile.py
```

## 🚀 Deployment

### Docker

```bash
# Generated Dockerfile is production-ready
docker build -t my-service .
docker run -p 8080:8080 my-service
```

### Kubernetes

```bash
# Apply generated manifests
kubectl apply -f kubernetes/
```

### Cloud Platforms

```bash
# Deploy to various platforms
apipack deploy --platform heroku
apipack deploy --platform aws-lambda
apipack deploy --platform gcp-cloud-run
```

## 🔍 Monitoring & Observability

Generated services include:

- **Health Checks**: `/health` endpoint
- **Metrics**: Prometheus metrics
- **Logging**: Structured logging with correlation IDs
- **Tracing**: OpenTelemetry integration
- **Documentation**: Auto-generated OpenAPI/gRPC docs

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/apipack/apipack
cd apipack
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest tests/ --cov=apipack
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: https://apipack.readthedocs.io
- **GitHub**: https://github.com/apipack/apipack
- **PyPI**: https://pypi.org/project/apipack
- **Discord**: https://discord.gg/apipack

## 🆘 Support

- 📚 **Documentation**: Comprehensive guides and API reference
- 💬 **Discord**: Community support and discussions
- 🐛 **Issues**: Bug reports and feature requests on GitHub
- 📧 **Email**: team@apipack.dev for enterprise support

## 🎯 Roadmap

- [ ] **v0.2**: Rust and Java language support
- [ ] **v0.3**: GraphQL and WebSocket interfaces
- [ ] **v0.4**: Cloud-native deployment templates
- [ ] **v0.5**: Visual interface builder
- [ ] **v1.0**: Production-ready release

---

**Made with ❤️ by the APIpack team**






















# APIpack - Architektura Systemu

## 🎯 Cel projektu

APIpack to framework do automatycznego generowania pakietów API z funkcji biznesowych przy użyciu lokalnych modeli LLM (Mistral 7B) i systemu szablonów.

## 🏗️ Architektura wysokiego poziomu

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │    │   Mistral 7B    │    │   Templates     │
│  (Functions)    │───▶│  (Logic Gen)    │    │   (Interface)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────────────────────────┐
                       │         APIpack Core Engine        │
                       │  ┌─────────────┐ ┌─────────────┐   │
                       │  │   Parser    │ │  Generator  │   │
                       │  └─────────────┘ └─────────────┘   │
                       │  ┌─────────────┐ ┌─────────────┐   │
                       │  │ Validator   │ │  Deployer   │   │
                       │  └─────────────┘ └─────────────┘   │
                       └─────────────────────────────────────┘
                                        │
                                        ▼
                       ┌─────────────────────────────────────┐
                       │         Generated Package          │
                       │  ┌─────────┐ ┌─────────┐ ┌──────┐  │
                       │  │   REST  │ │  gRPC   │ │ CLI  │  │
                       │  └─────────┘ └─────────┘ └──────┘  │
                       └─────────────────────────────────────┘
```

## 📁 Kompletna struktura projektu

```
apipack/
├── README.md                       ✅ # Main documentation
├── LICENSE                         🔲 # MIT License
├── CHANGELOG.md                    🔲 # Version history
├── CONTRIBUTING.md                 🔲 # Contribution guidelines
├── CODE_OF_CONDUCT.md             🔲 # Community guidelines
├── .gitignore                      🔲 # Git ignore rules
├── .pre-commit-config.yaml        🔲 # Pre-commit hooks
├── .github/                        🔲 # GitHub configuration
│   ├── workflows/
│   │   ├── ci.yml                 🔲 # Continuous Integration
│   │   ├── release.yml            🔲 # Release automation
│   │   └── docs.yml               🔲 # Documentation build
│   ├── ISSUE_TEMPLATE/            🔲 # Issue templates
│   ├── PULL_REQUEST_TEMPLATE.md   🔲 # PR template
│   └── dependabot.yml             🔲 # Dependency updates
├── setup.py                        ✅ # Package setup
├── pyproject.toml                  ✅ # Modern Python config
├── requirements.txt                ✅ # Core dependencies
├── requirements-dev.txt            🔲 # Development dependencies
├── Makefile                        ✅ # Development automation
├── docker-compose.yml              ✅ # Development environment
├── Dockerfile                      🔲 # Production container
├── Dockerfile.dev                  🔲 # Development container
├── .dockerignore                   🔲 # Docker ignore rules
│
├── apipack/                        # Main package
│   ├── __init__.py                ✅ # Package initialization
│   ├── py.typed                   🔲 # Type hints marker
│   ├── core/                      # Core engine
│   │   ├── __init__.py           🔲 # Core module init
│   │   ├── engine.py             ✅ # Main orchestrator
│   │   ├── parser.py             ✅ # Function spec parser
│   │   ├── generator.py          🔲 # Code generator
│   │   ├── validator.py          🔲 # Generated code validator
│   │   └── deployer.py           🔲 # Deployment manager
│   ├── llm/                       # LLM integration
│   │   ├── __init__.py           🔲 # LLM module init
│   │   ├── mistral_client.py     ✅ # Mistral 7B client
│   │   ├── prompt_manager.py     ✅ # Prompt templates
│   │   ├── response_parser.py    🔲 # LLM response parser
│   │   └── base_client.py        🔲 # Base LLM client
│   ├── templates/                 # Template system
│   │   ├── __init__.py           🔲 # Templates module init
│   │   ├── registry.py           ✅ # Template registry
│   │   ├── base/                 # Base templates
│   │   │   ├── __init__.py       🔲
│   │   │   ├── function.py.j2    🔲 # Base function template
│   │   │   ├── requirements.txt.j2 🔲 # Dependencies template
│   │   │   ├── dockerfile.j2     🔲 # Docker template
│   │   │   └── readme.md.j2      🔲 # README template
│   │   ├── interfaces/           # Interface templates
│   │   │   ├── __init__.py       🔲
│   │   │   ├── rest/
│   │   │   │   ├── __init__.py   🔲
│   │   │   │   ├── template.yml  🔲 # REST template config
│   │   │   │   ├── server.py.template ✅ # REST server
│   │   │   │   ├── client.py.template 🔲 # REST client
│   │   │   │   ├── server.js.template 🔲 # Node.js server
│   │   │   │   ├── server.go.template 🔲 # Go server
│   │   │   │   └── openapi.yml.j2 🔲 # OpenAPI spec
│   │   │   ├── grpc/
│   │   │   │   ├── __init__.py   🔲
│   │   │   │   ├── template.yml  🔲 # gRPC template config
│   │   │   │   ├── server.py.template 🔲 # gRPC server
│   │   │   │   ├── client.py.template 🔲 # gRPC client
│   │   │   │   ├── service.proto.j2 🔲 # Protocol buffer
│   │   │   │   └── server.go.template 🔲 # Go gRPC server
│   │   │   ├── graphql/
│   │   │   │   ├── __init__.py   🔲
│   │   │   │   ├── server.py.template 🔲 # GraphQL server
│   │   │   │   ├── schema.graphql.j2 🔲 # GraphQL schema
│   │   │   │   └── resolvers.py.template 🔲 # Resolvers
│   │   │   ├── websocket/
│   │   │   │   ├── __init__.py   🔲
│   │   │   │   ├── server.py.template 🔲 # WebSocket server
│   │   │   │   └── client.js.template 🔲 # WebSocket client
│   │   │   └── cli/
│   │   │       ├── __init__.py   🔲
│   │   │       ├── main.py.template 🔲 # CLI main
│   │   │       ├── cli.js.template 🔲 # Node.js CLI
│   │   │       └── main.go.template 🔲 # Go CLI
│   │   ├── languages/            # Language-specific templates
│   │   │   ├── __init__.py       🔲
│   │   │   ├── python/
│   │   │   │   ├── __init__.py   🔲
│   │   │   │   ├── config.yml    🔲 # Python config
│   │   │   │   ├── function.py.j2 🔲 # Python function
│   │   │   │   ├── test.py.j2    🔲 # Python test
│   │   │   │   └── requirements.txt.j2 🔲 # Python deps
│   │   │   ├── javascript/
│   │   │   │   ├── __init__.py   🔲
│   │   │   │   ├── config.yml    🔲 # JS config
│   │   │   │   ├── function.js.j2 🔲 # JS function
│   │   │   │   ├── test.js.j2    🔲 # JS test
│   │   │   │   └── package.json.j2 🔲 # NPM config
│   │   │   ├── go/
│   │   │   │   ├── config.yml    🔲 # Go config
│   │   │   │   ├── function.go.j2 🔲 # Go function
│   │   │   │   ├── test.go.j2    🔲 # Go test
│   │   │   │   └── go.mod.j2     🔲 # Go modules
│   │   │   └── rust/
│   │   │       ├── config.yml    🔲 # Rust config
│   │   │       ├── function.rs.j2 🔲 # Rust function
│   │   │       ├── test.rs.j2    🔲 # Rust test
│   │   │       └── cargo.toml.j2 🔲 # Cargo config
│   │   └── deployment/           # Deployment templates
│   │       ├── __init__.py       🔲
│   │       ├── docker/
│   │       │   ├── dockerfile.j2 🔲 # Dockerfile
│   │       │   └── compose.yml.j2 🔲 # Docker Compose
│   │       ├── kubernetes/
│   │       │   ├── deployment.yml.j2 🔲 # K8s deployment
│   │       │   ├── service.yml.j2 🔲 # K8s service
│   │       │   └── ingress.yml.j2 🔲 # K8s ingress
│   │       └── ci/
│   │           ├── github.yml.j2 🔲 # GitHub Actions
│   │           ├── gitlab.yml.j2 🔲 # GitLab CI
│   │           └── jenkins.j2    🔲 # Jenkins pipeline
│   ├── plugins/                   # Plugin system
│   │   ├── __init__.py           🔲 # Plugin module init
│   │   ├── base_plugin.py        🔲 # Base plugin class
│   │   ├── manager.py            🔲 # Plugin manager
│   │   └── builtin/              # Built-in plugins
│   │       ├── __init__.py       🔲
│   │       ├── rest.py           🔲 # REST plugin
│   │       ├── grpc.py           🔲 # gRPC plugin
│   │       ├── graphql.py        🔲 # GraphQL plugin
│   │       ├── websocket.py      🔲 # WebSocket plugin
│   │       └── cli.py            🔲 # CLI plugin
│   ├── config/                    # Configuration
│   │   ├── __init__.py           🔲 # Config module init
│   │   ├── settings.py           🔲 # Settings management
│   │   ├── schemas.py            🔲 # Configuration schemas
│   │   └── defaults.yml          🔲 # Default configuration
│   ├── utils/                     # Utilities
│   │   ├── __init__.py           🔲 # Utils module init
│   │   ├── file_utils.py         🔲 # File operations
│   │   ├── docker_utils.py       🔲 # Docker utilities
│   │   ├── git_utils.py          🔲 # Git operations
│   │   ├── test_utils.py         🔲 # Testing utilities
│   │   └── validation.py         🔲 # Validation helpers
│   ├── exceptions.py              🔲 # Custom exceptions
│   └── cli.py                     ✅ # Command-line interface
│
├── examples/                      # Example projects
│   ├── README.md                  🔲 # Examples documentation
│   ├── pdf2text/
│   │   ├── config.yml            ✅ # PDF service config
│   │   ├── functions/
│   │   │   └── extract_text.py   🔲 # Example function
│   │   ├── generated/            🔲 # Generated code (gitignored)
│   │   ├── tests/
│   │   │   └── test_extract.py   🔲 # Function tests
│   │   └── ansible/
│   │       └── test.yml          🔲 # E2E tests
│   ├── html2pdf/
│   │   ├── config.yml            🔲 # HTML to PDF config
│   │   ├── functions/
│   │   │   └── convert.js        🔲 # JavaScript function
│   │   └── tests/                🔲 # Tests
│   ├── image-resize/
│   │   ├── config.yml            🔲 # Image resize config
│   │   ├── functions/
│   │   │   └── resize.go         🔲 # Go function
│   │   └── tests/                🔲 # Tests
│   └── multi-service/
│       ├── config.yml            🔲 # Multi-function service
│       └── functions/            🔲 # Multiple functions
│
├── tests/                         # Test suite
│   ├── __init__.py               🔲 # Tests init
│   ├── conftest.py               🔲 # Pytest configuration
│   ├── unit/                     # Unit tests
│   │   ├── __init__.py           🔲
│   │   ├── test_engine.py        🔲 # Engine tests
│   │   ├── test_parser.py        🔲 # Parser tests
│   │   ├── test_generator.py     🔲 # Generator tests
│   │   ├── test_templates.py     🔲 # Template tests
│   │   ├── test_llm.py           🔲 # LLM client tests
│   │   └── test_cli.py           🔲 # CLI tests
│   ├── integration/              # Integration tests
│   │   ├── __init__.py           🔲
│   │   ├── test_end_to_end.py    🔲 # Full pipeline tests
│   │   ├── test_llm_integration.py 🔲 # LLM integration
│   │   └── test_docker.py        🔲 # Docker tests
│   ├── e2e/                      # End-to-end tests
│   │   ├── __init__.py           🔲
│   │   ├── test_examples.py      🔲 # Example generation tests
│   │   └── test_deployment.py    🔲 # Deployment tests
│   ├── performance/              # Performance tests
│   │   ├── __init__.py           🔲
│   │   ├── benchmark.py          🔲 # Performance benchmarks
│   │   └── locustfile.py         🔲 # Load testing
│   ├── fixtures/                 # Test fixtures
│   │   ├── sample_specs/         🔲 # Sample specifications
│   │   ├── sample_functions/     🔲 # Sample functions
│   │   └── test_data/            🔲 # Test data files
│   └── mock_servers/             # Mock services for testing
│       ├── mock_ollama.py        🔲 # Mock Ollama server
│       └── mock_registry.py      🔲 # Mock template registry
│
├── docs/                          # Documentation
│   ├── index.md                  🔲 # Main index
│   ├── getting-started.md        ✅ # Getting started guide
│   ├── installation.md           🔲 # Installation guide
│   ├── user-guide/               # User documentation
│   │   ├── specification.md      🔲 # Function specifications
│   │   ├── templates.md          🔲 # Template system
│   │   ├── cli.md                🔲 # CLI reference
│   │   ├── api.md                🔲 # Python API
│   │   └── deployment.md         🔲 # Deployment guide
│   ├── developer-guide/          # Developer documentation
│   │   ├── architecture.md       🔲 # System architecture
│   │   ├── plugins.md            🔲 # Plugin development
│   │   ├── templates.md          🔲 # Template development
│   │   └── contributing.md       🔲 # How to contribute
│   ├── examples/                 # Example documentation
│   │   ├── quickstart.md         🔲 # Quick examples
│   │   ├── advanced.md           🔲 # Advanced examples
│   │   └── patterns.md           🔲 # Common patterns
│   ├── api/                      # API documentation
│   │   ├── core.md               🔲 # Core API
│   │   ├── templates.md          🔲 # Template API
│   │   └── plugins.md            🔲 # Plugin API
│   ├── conf.py                   🔲 # Sphinx configuration
│   ├── requirements.txt          🔲 # Docs dependencies
│   └── Makefile                  🔲 # Docs build automation
│
├── scripts/                       # Utility scripts
│   ├── setup_ollama.sh           🔲 # Ollama setup script
│   ├── validate_templates.py     🔲 # Template validation
│   ├── benchmark_languages.py    🔲 # Language benchmarks
│   ├── profile_generation.py     🔲 # Performance profiling
│   ├── check_dependencies.py     🔲 # Dependency checker
│   ├── release.py                🔲 # Release automation
│   └── init.sql                  🔲 # Database initialization
│
├── monitoring/                    # Monitoring configuration
│   ├── prometheus.yml            🔲 # Prometheus config
│   ├── grafana/
│   │   ├── dashboards/           🔲 # Grafana dashboards
│   │   └── datasources/          🔲 # Data sources
│   └── alerts/                   🔲 # Alert configurations
│
├── nginx/                         # Nginx configuration
│   ├── nginx.conf                🔲 # Main config
│   └── ssl/                      🔲 # SSL certificates
│
└── deployment/                    # Deployment configurations
    ├── kubernetes/               🔲 # K8s manifests
    │   ├── namespace.yml         🔲
    │   ├── deployment.yml        🔲
    │   ├── service.yml           🔲
    │   └── ingress.yml           🔲
    ├── terraform/                🔲 # Infrastructure as Code
    │   ├── main.tf               🔲
    │   ├── variables.tf          🔲
    │   └── outputs.tf            🔲
    ├── ansible/                  🔲 # Ansible playbooks
    │   ├── deploy.yml            🔲
    │   ├── inventory/            🔲
    │   └── roles/                🔲
    └── helm/                     🔲 # Helm charts
        ├── Chart.yaml            🔲
        ├── values.yaml           🔲
        └── templates/            🔲
```

## Status oznaczenia:
- ✅ Utworzone
- 🔲 Do utworzenia
- 🚧 W trakcie

## Kolejność implementacji (priorytet):

### Faza 1 - Podstawowa funkcjonalność
1. **Core modules** - generator.py, validator.py, deployer.py
2. **LLM integration** - response_parser.py, base_client.py
3. **Config system** - settings.py, schemas.py, defaults.yml
4. **Utils** - file_utils.py, validation.py

### Faza 2 - Szablony i pluginy
1. **Base templates** - function.py.j2, requirements.txt.j2, dockerfile.j2
2. **Interface templates** - wszystkie szablony interfejsów
3. **Language templates** - wszystkie szablony językowe
4. **Plugin system** - base_plugin.py, manager.py, builtin plugins

### Faza 3 - Testy i dokumentacja
1. **Test suite** - wszystkie testy jednostkowe i integracyjne
2. **Documentation** - pełna dokumentacja Sphinx
3. **Examples** - kompletne przykłady

### Faza 4 - Deployment i monitoring
1. **CI/CD** - GitHub Actions, release automation
2. **Docker** - Dockerfile, docker-compose
3. **Kubernetes** - manifesty K8s
4. **Monitoring** - Prometheus, Grafana

## 🔄 Przepływ pracy

### 1. Input Processing
```python
function_spec = {
    "name": "pdf_to_text",
    "description": "Extract text from PDF files",
    "input_type": "bytes",
    "output_type": "string",
    "interfaces": ["rest", "grpc", "cli"]
}
```

### 2. LLM Function Generation
- Mistral 7B generuje implementację funkcji
- Optimized prompts dla różnych języków
- Walidacja i sanityzacja kodu

### 3. Template Processing
- Wybór odpowiednich szablonów
- Generowanie interfejsów API
- Integracja z funkcjami biznesowymi

### 4. Package Assembly
- Kompilacja wszystkich komponentów
- Generowanie testów
- Przygotowanie deployment files

## 🧩 Komponenty systemu

### Core Engine
- **Parser**: Analizuje specyfikację funkcji
- **Generator**: Orkiestruje generowanie kodu
- **Validator**: Sprawdza poprawność kodu
- **Deployer**: Zarządza wdrożeniem

### LLM Integration
- **Mistral Client**: Interface do Mistral 7B
- **Prompt Manager**: Zarządza promptami
- **Response Parser**: Przetwarza odpowiedzi LLM

### Template System
- **Registry**: Rejestr dostępnych szablonów
- **Base Templates**: Podstawowe struktury
- **Interface Templates**: Szablony interfejsów
- **Language Templates**: Szablony językowe

### Plugin System
- **Base Plugin**: Abstrakcyjna klasa bazowa
- **Built-in Plugins**: Wbudowane rozszerzenia
- **Custom Plugins**: Możliwość dodawania własnych

## 🔌 Extensibility Points

### 1. Nowe Interfejsy
```python
# plugins/custom_interface.py
class CustomInterfacePlugin(BasePlugin):
    def generate(self, function_spec):
        # Custom interface generation logic
        pass
```

### 2. Nowe Języki
```yaml
# templates/languages/kotlin/config.yml
language: kotlin
extension: .kt
runtime: jvm
dependencies:
  - kotlinx-coroutines-core
```

### 3. Nowe LLM Providers
```python
# llm/custom_provider.py
class CustomLLMProvider(BaseLLMProvider):
    def generate_function(self, spec):
        # Custom LLM integration
        pass
```

## 📊 Konfiguracja

### Global Settings
```yaml
# config/default.yml
llm:
  provider: mistral
  model: mistral:7b
  temperature: 0.1
  max_tokens: 2048

templates:
  auto_discover: true
  cache_enabled: true
  validation_level: strict

output:
  format: package
  include_tests: true
  include_docs: true
```

### Project Settings
```yaml
# project.apipack.yml
name: my-api-service
language: python
interfaces:
  - rest
  - grpc
functions:
  - spec: functions/pdf_to_text.yml
  - spec: functions/image_resize.yml
```

## 🎯 Rozszerzalność

### Template Discovery
System automatycznie odkrywa nowe szablony w:
- `~/.apipack/templates/`
- `./templates/`
- Package templates

### Plugin Loading
Plugins są ładowane z:
- Built-in plugins
- `~/.apipack/plugins/`
- Project plugins directory

### Custom Generators
Możliwość dodania własnych generatorów:
```python
@register_generator("custom-api")
class CustomAPIGenerator(BaseGenerator):
    def generate(self, spec):
        # Custom generation logic
        pass
```

## 🚀 API Usage

### Programmatic API
```python
from apipack import APIPackEngine

engine = APIPackEngine()
package = engine.generate_package(
    function_specs=[pdf_to_text_spec],
    interfaces=["rest", "grpc"],
    language="python"
)
package.deploy()
```

### CLI Interface
```bash
apipack generate \
  --spec functions.yml \
  --interfaces rest,grpc \
  --language python \
  --output ./generated
```

### Configuration-based
```bash
apipack build --config project.apipack.yml
```

## 🔍 Monitoring & Observability

### Metrics Collection
- Generation time
- Template usage
- LLM token consumption
- Success/failure rates

### Logging
- Structured logging
- Debug modes
- Performance profiling

### Health Checks
- Template validation
- LLM connectivity
- Generated code syntax check





## 🔄 Przepływ pracy

### 1. Input Processing
```python
function_spec = {
    "name": "pdf_to_text",
    "description": "Extract text from PDF files",
    "input_type": "bytes",
    "output_type": "string",
    "interfaces": ["rest", "grpc", "cli"]
}
```

### 2. LLM Function Generation
- Mistral 7B generuje implementację funkcji
- Optimized prompts dla różnych języków
- Walidacja i sanityzacja kodu

### 3. Template Processing
- Wybór odpowiednich szablonów
- Generowanie interfejsów API
- Integracja z funkcjami biznesowymi

### 4. Package Assembly
- Kompilacja wszystkich komponentów
- Generowanie testów
- Przygotowanie deployment files

## 🧩 Komponenty systemu

### Core Engine
- **Parser**: Analizuje specyfikację funkcji
- **Generator**: Orkiestruje generowanie kodu
- **Validator**: Sprawdza poprawność kodu
- **Deployer**: Zarządza wdrożeniem

### LLM Integration
- **Mistral Client**: Interface do Mistral 7B
- **Prompt Manager**: Zarządza promptami
- **Response Parser**: Przetwarza odpowiedzi LLM

### Template System
- **Registry**: Rejestr dostępnych szablonów
- **Base Templates**: Podstawowe struktury
- **Interface Templates**: Szablony interfejsów
- **Language Templates**: Szablony językowe

### Plugin System
- **Base Plugin**: Abstrakcyjna klasa bazowa
- **Built-in Plugins**: Wbudowane rozszerzenia
- **Custom Plugins**: Możliwość dodawania własnych

## 🔌 Extensibility Points

### 1. Nowe Interfejsy
```python
# plugins/custom_interface.py
class CustomInterfacePlugin(BasePlugin):
    def generate(self, function_spec):
        # Custom interface generation logic
        pass
```

### 2. Nowe Języki
```yaml
# templates/languages/kotlin/config.yml
language: kotlin
extension: .kt
runtime: jvm
dependencies:
  - kotlinx-coroutines-core
```

### 3. Nowe LLM Providers
```python
# llm/custom_provider.py
class CustomLLMProvider(BaseLLMProvider):
    def generate_function(self, spec):
        # Custom LLM integration
        pass
```

## 📊 Konfiguracja

### Global Settings
```yaml
# config/default.yml
llm:
  provider: mistral
  model: mistral:7b
  temperature: 0.1
  max_tokens: 2048

templates:
  auto_discover: true
  cache_enabled: true
  validation_level: strict

output:
  format: package
  include_tests: true
  include_docs: true
```

### Project Settings
```yaml
# project.apipack.yml
name: my-api-service
language: python
interfaces:
  - rest
  - grpc
functions:
  - spec: functions/pdf_to_text.yml
  - spec: functions/image_resize.yml
```

## 🎯 Rozszerzalność

### Template Discovery
System automatycznie odkrywa nowe szablony w:
- `~/.apipack/templates/`
- `./templates/`
- Package templates

### Plugin Loading
Plugins są ładowane z:
- Built-in plugins
- `~/.apipack/plugins/`
- Project plugins directory

### Custom Generators
Możliwość dodania własnych generatorów:
```python
@register_generator("custom-api")
class CustomAPIGenerator(BaseGenerator):
    def generate(self, spec):
        # Custom generation logic
        pass
```

## 🚀 API Usage

### Programmatic API
```python
from apipack import APIPackEngine

engine = APIPackEngine()
package = engine.generate_package(
    function_specs=[pdf_to_text_spec],
    interfaces=["rest", "grpc"],
    language="python"
)
package.deploy()
```

### CLI Interface
```bash
apipack generate \
  --spec functions.yml \
  --interfaces rest,grpc \
  --language python \
  --output ./generated
```

### Configuration-based
```bash
apipack build --config project.apipack.yml
```

## 🔍 Monitoring & Observability

### Metrics Collection
- Generation time
- Template usage
- LLM token consumption
- Success/failure rates

### Logging
- Structured logging
- Debug modes
- Performance profiling

### Health Checks
- Template validation
- LLM connectivity
- Generated code syntax check