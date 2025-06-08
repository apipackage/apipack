"""
Settings and configuration management for APIpack.
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field, validator


class LLMSettings(BaseModel):
    """Settings for LLM configuration."""
    model_name: str = "mistral:7b"
    temperature: float = 0.7
    max_tokens: int = 2000
    api_base: str = "http://localhost:11434"
    timeout: int = 300


class TemplateSettings(BaseModel):
    """Settings for template configuration."""
    template_dirs: List[str] = Field(
        default_factory=lambda: ["templates"]
    )
    auto_discover: bool = True


class GenerationSettings(BaseModel):
    """Settings for code generation."""
    output_dir: str = "generated"
    validate_code: bool = True
    format_code: bool = True
    overwrite: bool = False


class Settings(BaseModel):
    """Main settings class for APIpack."""
    llm: LLMSettings = Field(default_factory=LLMSettings)
    templates: TemplateSettings = Field(default_factory=TemplateSettings)
    generation: GenerationSettings = Field(default_factory=GenerationSettings)
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        env_prefix = "apipack_"
        case_sensitive = True


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get the global settings instance.
    
    Returns:
        Settings: The global settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def update_settings(**kwargs) -> None:
    """Update the global settings with new values.
    
    Args:
        **kwargs: Settings to update
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    _settings = _settings.copy(update=kwargs)
