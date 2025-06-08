"""Basic tests for APIpack core functionality."""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from apipack.core.engine import APIPackEngine, GenerationResult

@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = MagicMock()
    client.generate_function = AsyncMock(return_value={
        'code': 'def greet(name):\n    return f"Hello, {name}!"',
        'explanation': 'A simple greeting function'
    })
    return client

@pytest.fixture
def mock_template_registry():
    """Create a mock template registry."""
    registry = MagicMock()
    registry.get_template = MagicMock(return_value="""
    # REST API for {{ function.name }}
    @app.get("/{{ function.name }}")
    async def {{ function.name }}({{ function.parameters|join(', ') }}):
        return {"result": {{ function.name }}({{ function.parameters|join(', ') }})}
    """)
    return registry

@pytest.fixture
def basic_engine(mock_llm_client, mock_template_registry):
    """Create an APIPackEngine with mocked dependencies."""
    engine = APIPackEngine()
    engine.llm_client = mock_llm_client
    engine.template_registry = mock_template_registry
    return engine

@pytest.mark.asyncio
async def test_generate_package_basic(basic_engine, tmp_path):
    """Test basic package generation with mocked components."""
    # Define test function specs
    function_specs = [
        {
            'name': 'greet',
            'description': 'Returns a greeting',
            'parameters': [
                {'name': 'name', 'type': 'string', 'required': True}
            ],
            'return_type': 'string'
        }
    ]
    
    # Generate the package
    result = await basic_engine.generate_package_async(
        function_specs=function_specs,
        interfaces=['rest'],
        language='python',
        output_dir=tmp_path,
        project_name='test_api',
        version='1.0.0',
        description='Test API'
    )
    
    # Verify the result
    assert isinstance(result, GenerationResult)
    assert result.success is True
    assert len(result.generated_files) > 0
    assert (tmp_path / 'test_api').exists()
    assert (tmp_path / 'test_api' / 'test_api').exists()
    assert (tmp_path / 'test_api' / 'requirements.txt').exists()

    # Verify the LLM client was called
    basic_engine.llm_client.generate_function.assert_called()
    
    # Verify templates were used
    basic_engine.template_registry.get_template.assert_called()

def test_engine_initialization():
    """Test that the API engine initializes correctly."""
    engine = APIPackEngine()
    assert engine is not None
    assert hasattr(engine, 'parser')
    assert hasattr(engine, 'llm_client')
    assert hasattr(engine, 'template_registry')
