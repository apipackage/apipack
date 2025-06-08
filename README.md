# APIpack - Architektura Systemu

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

## 📁 Struktura projektu

```
apipack/
├── apipack/                    # Main package
│   ├── __init__.py
│   ├── core/                   # Core engine
│   │   ├── __init__.py
│   │   ├── engine.py          # Main orchestrator
│   │   ├── parser.py          # Function spec parser
│   │   ├── generator.py       # Code generator
│   │   ├── validator.py       # Generated code validator
│   │   └── deployer.py        # Deployment manager
│   ├── llm/                   # LLM integration
│   │   ├── __init__.py
│   │   ├── mistral_client.py  # Mistral 7B client
│   │   ├── prompt_manager.py  # Prompt templates
│   │   └── response_parser.py # LLM response parser
│   ├── templates/             # Template system
│   │   ├── __init__.py
│   │   ├── base/              # Base templates
│   │   ├── interfaces/        # Interface templates
│   │   │   ├── rest/
│   │   │   ├── grpc/
│   │   │   ├── graphql/
│   │   │   ├── websocket/
│   │   │   └── cli/
│   │   ├── languages/         # Language-specific templates
│   │   │   ├── python/
│   │   │   ├── javascript/
│   │   │   ├── golang/
│   │   │   └── rust/
│   │   └── registry.py        # Template registry
│   ├── plugins/               # Plugin system
│   │   ├── __init__.py
│   │   ├── base_plugin.py
│   │   └── builtin/           # Built-in plugins
│   ├── config/                # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── schemas.py
│   └── utils/                 # Utilities
│       ├── __init__.py
│       ├── file_utils.py
│       ├── docker_utils.py
│       └── test_utils.py
├── examples/                  # Example projects
├── tests/                     # Test suite
├── docs/                      # Documentation
├── scripts/                   # Setup scripts
├── pyproject.toml            # Project configuration
├── requirements.txt          # Dependencies
├── README.md                 # Main documentation
└── setup.py                  # Package setup
```

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