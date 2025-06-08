# Getting Started with APIpack

Welcome to APIpack! This guide will help you generate your first API package in just a few minutes.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Dependencies

1. **Python 3.8+**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **Ollama** (for local LLM)
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull Mistral model
   ollama pull mistral:7b
   
   # Start Ollama server
   ollama serve
   ```

3. **Docker** (optional, for containerization)
   ```bash
   docker --version
   ```

## Installation

### Install APIpack

```bash
# Install from PyPI
pip install apipack

# Or install development version
pip install git+https://github.com/apipack/apipack.git

# Verify installation
apipack --version
```

### Verify Setup

```bash
# Check if everything is working
apipack health
```

You should see output similar to:
```
✓ LLM: mistral:7b is healthy
✓ Templates: 15 templates available
✓ Interfaces: rest, grpc, graphql, websocket, cli
```

## Your First API Package

Let's create a simple PDF text extraction service.

### Step 1: Initialize Function Specification

```bash
apipack init --name pdf_to_text --description "Extract text from PDF files"
```

This creates a `function_spec.yml` file with a basic template.

### Step 2: Customize the Specification

Edit `function_spec.yml`:

```yaml
name: pdf_to_text
description: Extract text content from PDF files
input_type: bytes
output_type: string
parameters:
  - name: pdf_data
    type: bytes
    description: PDF file binary data
    required: true
dependencies:
  - PyPDF2>=3.0.0
examples:
  - input:
      pdf_data: "<binary PDF data>"
    output: "Extracted text content from PDF"
interfaces:
  - rest
  - cli
```

### Step 3: Validate the Specification

```bash
apipack validate function_spec.yml
```

You should see:
```
✓ Specification is valid
```

### Step 4: Generate the API Package

```bash
apipack generate function_spec.yml --language python --output ./pdf-service
```

This will:
- Generate function implementation using Mistral 7B
- Create REST API server with FastAPI
- Generate CLI interface
- Add Docker configuration
- Create comprehensive tests
- Generate documentation

### Step 5: Explore Generated Package

```bash
cd pdf-service
ls -la
```

You'll see:
```
├── functions/
│   └── pdf_to_text.py        # LLM-generated function
├── rest/
│   └── server.py             # FastAPI server
├── cli/
│   └── main.py              # CLI interface
├── tests/
│   ├── test_pdf_to_text.py  # Unit tests
│   └── test_integration.py  # Integration tests
├── Dockerfile               # Container configuration
├── requirements.txt         # Python dependencies
├── README.md               # Generated documentation
└── docker-compose.yml     # Multi-service setup
```

### Step 6: Test the Generated Function

```bash
# Install dependencies
pip install -r requirements.txt

# Run unit tests
python -m pytest tests/ -v

# Test the function directly
python -c "
from functions.pdf_to_text import pdf_to_text
# Test with sample data
result = pdf_to_text(b'sample pdf data')
print(result)
"
```

### Step 7: Run the REST API

```bash
# Start the server
python rest/server.py
```

Or using Docker:
```bash
# Build image
docker build -t pdf-service .

# Run container
docker run -p 8080:8080 pdf-service
```

### Step 8: Test the API

```bash
# Health check
curl http://localhost:8080/health

# API documentation
open http://localhost:8080/docs

# Test the endpoint
curl -X POST \
  -F "file=@sample.pdf" \
  http://localhost:8080/extract
```

### Step 9: Use the CLI

```bash
# Test CLI interface
python cli/main.py extract sample.pdf --output result.txt
```

## Next Steps

### Add More Functions

Create a multi-function service:

```yaml
# multi-service.yml
project:
  name: document-processor
  description: Complete document processing service

functions:
  - name: pdf_to_text
    description: Extract text from PDF
    input_type: bytes
    output_type: string
    
  - name: html_to_pdf
    description: Convert HTML to PDF
    input_type: string
    output_type: bytes
    
  - name: extract_images
    description: Extract images from documents
    input_type: bytes
    output_type: list

interfaces: [rest, grpc, cli]
language: python
```

Generate:
```bash
apipack generate multi-service.yml --output ./document-processor
```

### Try Different Languages

Generate the same service in Go:
```bash
apipack generate function_spec.yml --language go --output ./pdf-service-go
```

Or JavaScript:
```bash
apipack generate function_spec.yml --language javascript --output ./pdf-service-js
```

### Add More Interfaces

Include gRPC and WebSocket:
```bash
apipack generate function_spec.yml \
  --interfaces rest,grpc,websocket \
  --output ./pdf-service-full
```

### Deploy to Production

```bash
# Build production image
apipack build ./pdf-service --type docker --tag pdf-service:v1.0.0

# Deploy to Kubernetes
apipack build ./pdf-service --type kubernetes --deploy
```

## Common Patterns

### File Processing Service

```yaml
name: image_processor
description: Image processing and manipulation
input_type: bytes
output_type: bytes
parameters:
  - name: image_data
    type: bytes
    required: true
  - name: operation
    type: string
    required: true
    default: "resize"
  - name: width
    type: int
    default: 800
  - name: height
    type: int
    default: 600
dependencies:
  - Pillow>=9.0.0
```

### Data Processing Service

```yaml
name: data_analyzer
description: Analyze and process data
input_type: dict
output_type: dict
parameters:
  - name: data
    type: dict
    required: true
  - name: analysis_type
    type: string
    default: "summary"
dependencies:
  - pandas>=1.5.0
  - numpy>=1.21.0
```

### Web Scraping Service

```yaml
name: web_scraper
description: Extract data from web pages
input_type: string
output_type: dict
parameters:
  - name: url
    type: string
    required: true
  - name: selectors
    type: list
    default: []
dependencies:
  - requests>=2.28.0
  - beautifulsoup4>=4.11.0
```

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve

# Check available models
ollama list
```

### Template Issues

```bash
# List available templates
apipack templates

# Validate templates
python -c "
from apipack import TemplateRegistry
registry = TemplateRegistry()
print(registry.validate_template('rest.python'))
"
```

### Generated Code Issues

```bash
# Check LLM health
apipack health

# Regenerate with different temperature
apipack generate spec.yml --temperature 0.2

# Validate generated code
cd generated-package
python -m py_compile **/*.py
```

### Performance Issues

```bash
# Profile generation
python -m cProfile -o profile.stats \
  -c "from apipack import APIPackEngine; engine = APIPackEngine(); engine.generate_package(...)"

# Check memory usage
python -m memory_profiler your_script.py
```

## Best Practices

### Function Specifications

1. **Be Specific**: Provide detailed descriptions and examples
2. **Use Type Hints**: Specify precise input/output types
3. **Include Examples**: Add realistic input/output examples
4. **Document Parameters**: Describe each parameter clearly

### Generated Code

1. **Review Generated Functions**: Always review LLM-generated code
2. **Add Custom Logic**: Extend generated functions as needed
3. **Update Tests**: Add additional test cases for edge cases
4. **Monitor Performance**: Profile generated code for bottlenecks

### Deployment

1. **Environment Variables**: Use env vars for configuration
2. **Health Checks**: Implement proper health checking
3. **Logging**: Configure structured logging
4. **Monitoring**: Add metrics and alerting

## Getting Help

- **Documentation**: https://apipack.readthedocs.io
- **GitHub Issues**: https://github.com/apipack/apipack/issues
- **Discord Community**: https://discord.gg/apipack
- **Email Support**: team@apipack.dev

## What's Next?

Now that you have a basic understanding of APIpack, you can:

1. **Explore Examples**: Check out the `examples/` directory
2. **Read Advanced Guides**: Learn about custom templates and plugins
3. **Join the Community**: Connect with other APIpack users
4. **Contribute**: Help improve APIpack by contributing code or documentation

Happy coding with APIpack! 🚀