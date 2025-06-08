"""Test core functionality of APIpack."""
import pytest
from apipack.core.engine import APIEngine


def test_engine_initialization():
    """Test that the API engine initializes correctly."""
    engine = APIEngine()
    assert engine is not None


def test_generate_api():
    """Test basic API generation."""
    engine = APIEngine()
    spec = {
        "name": "test_api",
        "version": "1.0.0",
        "endpoints": [
            {
                "name": "get_users",
                "method": "GET",
                "path": "/users",
                "response": {"type": "array", "items": {"type": "string"}}
            }
        ]
    }
    
    result = engine.generate(spec)
    assert "code" in result
    assert "docs" in result
