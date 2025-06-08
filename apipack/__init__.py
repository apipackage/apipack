"""
APIpack - Automated API Package Generator

A framework for generating API packages from function specifications using
LLM integration (Mistral 7B) and customizable templates.

Example:
    >>> from apipack import APIPackEngine
    >>> engine = APIPackEngine()
    >>> package = engine.generate_package(
    ...     function_specs=[{"name": "pdf_to_text", "type": "converter"}],
    ...     interfaces=["rest", "grpc"],
    ...     language="python"
    ... )
    >>> package.deploy()
"""

from .core.engine import APIPackEngine
from .core.parser import FunctionSpecParser
from .core.generator import CodeGenerator
from .core.validator import CodeValidator
from .core.deployer import PackageDeployer

from .llm.mistral_client import MistralClient
from .templates.registry import TemplateRegistry
from .config.settings import Settings, get_settings
from .plugins.base_plugin import BasePlugin

# Version information
__version__ = "0.1.0"
__author__ = "APIpack Team"
__email__ = "team@apipack.dev"
__license__ = "MIT"

# Public API
__all__ = [
    # Core components
    "APIPackEngine",
    "FunctionSpecParser",
    "CodeGenerator",
    "CodeValidator",
    "PackageDeployer",

    # LLM integration
    "MistralClient",

    # Template system
    "TemplateRegistry",

    # Configuration
    "Settings",
    "get_settings",

    # Plugin system
    "BasePlugin",

    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]

# Default configuration
DEFAULT_CONFIG = {
    "llm": {
        "provider": "mistral",
        "model": "mistral:7b",
        "temperature": 0.1,
        "max_tokens": 2048,
    },
    "templates": {
        "auto_discover": True,
        "cache_enabled": True,
        "validation_level": "strict",
    },
    "output": {
        "format": "package",
        "include_tests": True,
        "include_docs": True,
    }
}


def create_engine(**kwargs) -> APIPackEngine:
    """
    Create an APIPackEngine instance with optional configuration.

    Args:
        **kwargs: Configuration options to override defaults

    Returns:
        APIPackEngine: Configured engine instance

    Example:
        >>> engine = create_engine(
        ...     llm_model="mistral:7b",
        ...     output_format="package"
        ... )
    """
    config = DEFAULT_CONFIG.copy()
    config.update(kwargs)
    return APIPackEngine(config=config)


def quick_generate(function_spec: dict, **kwargs) -> dict:
    """
    Quick generation function for simple use cases.

    Args:
        function_spec: Function specification dictionary
        **kwargs: Generation options

    Returns:
        dict: Generated package information

    Example:
        >>> result = quick_generate({
        ...     "name": "pdf_to_text",
        ...     "description": "Extract text from PDF",
        ...     "input_type": "bytes",
        ...     "output_type": "string"
        ... }, interfaces=["rest"], language="python")
    """
    engine = create_engine(**kwargs)
    return engine.generate_package([function_spec], **kwargs)


# Initialize logging
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())