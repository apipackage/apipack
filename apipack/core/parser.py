"""
Function Specification Parser

Parses and validates function specifications from various input formats.
Standardizes specifications into a common internal format.
"""

import logging
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError, Field

logger = logging.getLogger(__name__)


class FunctionParameter(BaseModel):
    """Function parameter specification."""
    name: str
    type: str
    description: Optional[str] = None
    required: bool = True
    default: Optional[Any] = None
    validation: Optional[Dict[str, Any]] = None


class FunctionSpec(BaseModel):
    """Complete function specification."""
    name: str
    description: Optional[str] = None
    input_type: str = "any"
    output_type: str = "any"
    parameters: List[FunctionParameter] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Interface-specific configurations
    rest_config: Optional[Dict[str, Any]] = None
    grpc_config: Optional[Dict[str, Any]] = None
    cli_config: Optional[Dict[str, Any]] = None


@dataclass
class ParseResult:
    """Result of parsing operation."""
    success: bool
    spec: Optional[FunctionSpec]
    errors: List[str]
    warnings: List[str]


class FunctionSpecParser:
    """
    Parser for function specifications.

    Supports multiple input formats:
    - Python dictionaries
    - JSON files
    - YAML files
    - Python function annotations
    """

    def __init__(self):
        self.last_errors: List[str] = []
        self.last_warnings: List[str] = []

    def parse(self, spec_input: Union[Dict, str, Path]) -> Optional[FunctionSpec]:
        """
        Parse function specification from various input types.

        Args:
            spec_input: Specification as dict, file path, or string

        Returns:
            Parsed FunctionSpec or None if parsing failed
        """
        self.last_errors = []
        self.last_warnings = []

        try:
            # Handle different input types
            if isinstance(spec_input, dict):
                return self._parse_dict(spec_input)
            elif isinstance(spec_input, (str, Path)):
                return self._parse_file(Path(spec_input))
            else:
                self.last_errors.append(f"Unsupported input type: {type(spec_input)}")
                return None

        except Exception as e:
            logger.exception("Error parsing function specification")
            self.last_errors.append(str(e))
            return None

    def parse_multiple(self, spec_inputs: List[Union[Dict, str, Path]]) -> List[FunctionSpec]:
        """
        Parse multiple function specifications.

        Args:
            spec_inputs: List of specification inputs

        Returns:
            List of successfully parsed FunctionSpecs
        """
        parsed_specs = []
        for spec_input in spec_inputs:
            spec = self.parse(spec_input)
            if spec:
                parsed_specs.append(spec)

        return parsed_specs

    def _parse_dict(self, spec_dict: Dict[str, Any]) -> Optional[FunctionSpec]:
        """Parse specification from dictionary."""
        try:
            # Normalize dictionary format
            normalized = self._normalize_dict_spec(spec_dict)

            # Validate using Pydantic
            spec = FunctionSpec(**normalized)

            # Additional validation
            validation_errors = self._validate_spec(spec)
            if validation_errors:
                self.last_errors.extend(validation_errors)
                return None

            return spec

        except ValidationError as e:
            self.last_errors.extend([str(error) for error in e.errors()])
            return None

    def _parse_file(self, file_path: Path) -> Optional[FunctionSpec]:
        """Parse specification from file."""
        if not file_path.exists():
            self.last_errors.append(f"File not found: {file_path}")
            return None

        try:
            content = file_path.read_text(encoding="utf-8")

            if file_path.suffix.lower() == ".json":
                data = json.loads(content)
            elif file_path.suffix.lower() in [".yml", ".yaml"]:
                data = yaml.safe_load(content)
            else:
                self.last_errors.append(f"Unsupported file format: {file_path.suffix}")
                return None

            return self._parse_dict(data)

        except json.JSONDecodeError as e:
            self.last_errors.append(f"JSON parsing error: {str(e)}")
            return None
        except yaml.YAMLError as e:
            self.last_errors.append(f"YAML parsing error: {str(e)}")
            return None

    def _normalize_dict_spec(self, spec_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize dictionary specification to standard format."""
        normalized = spec_dict.copy()

        # Handle legacy field names
        field_mappings = {
            "function_name": "name",
            "desc": "description",
            "input": "input_type",
            "output": "output_type",
            "params": "parameters",
            "deps": "dependencies",
        }

        for old_key, new_key in field_mappings.items():
            if old_key in normalized:
                normalized[new_key] = normalized.pop(old_key)

        # Normalize parameters
        if "parameters" in normalized:
            normalized["parameters"] = self._normalize_parameters(normalized["parameters"])

        # Extract interface configs
        for interface in ["rest", "grpc", "cli"]:
            config_key = f"{interface}_config"
            if interface in normalized:
                normalized[config_key] = normalized.pop(interface)

        return normalized

    def _normalize_parameters(self, params: Any) -> List[Dict[str, Any]]:
        """Normalize parameter specifications."""
        if not params:
            return []

        normalized_params = []

        # Handle different parameter formats
        if isinstance(params, dict):
            # Dict format: {"param_name": "type"} or {"param_name": {...}}
            for name, config in params.items():
                if isinstance(config, str):
                    # Simple type specification
                    param = {"name": name, "type": config}
                elif isinstance(config, dict):
                    # Full parameter specification
                    param = {"name": name, **config}
                else:
                    param = {"name": name, "type": "any"}

                normalized_params.append(param)

        elif isinstance(params, list):
            # List format: [{"name": "param", "type": "str"}, ...]
            for param in params:
                if isinstance(param, dict):
                    normalized_params.append(param)
                elif isinstance(param, str):
                    # Just parameter name, infer type
                    normalized_params.append({"name": param, "type": "any"})

        return normalized_params

    def _validate_spec(self, spec: FunctionSpec) -> List[str]:
        """Additional validation for function specification."""
        errors = []

        # Validate function name
        if not spec.name.isidentifier():
            errors.append(f"Invalid function name: {spec.name}")

        # Validate parameter names
        param_names = set()
        for param in spec.parameters:
            if not param.name.isidentifier():
                errors.append(f"Invalid parameter name: {param.name}")

            if param.name in param_names:
                errors.append(f"Duplicate parameter name: {param.name}")
            param_names.add(param.name)

        # Validate types
        valid_types = {
            "str", "string", "int", "integer", "float", "bool", "boolean",
            "bytes", "list", "dict", "any", "object", "file", "json"
        }

        if spec.input_type not in valid_types:
            self.last_warnings.append(f"Unknown input type: {spec.input_type}")

        if spec.output_type not in valid_types:
            self.last_warnings.append(f"Unknown output type: {spec.output_type}")

        return errors

    def get_last_errors(self) -> List[str]:
        """Get errors from the last parsing operation."""
        return self.last_errors.copy()

    def get_last_warnings(self) -> List[str]:
        """Get warnings from the last parsing operation."""
        return self.last_warnings.copy()

    def validate_spec_dict(self, spec_dict: Dict[str, Any]) -> ParseResult:
        """
        Validate a specification dictionary without creating a FunctionSpec.

        Args:
            spec_dict: Specification dictionary to validate

        Returns:
            ParseResult with validation results
        """
        self.last_errors = []
        self.last_warnings = []

        try:
            spec = self._parse_dict(spec_dict)
            return ParseResult(
                success=spec is not None,
                spec=spec,
                errors=self.last_errors.copy(),
                warnings=self.last_warnings.copy()
            )
        except Exception as e:
            return ParseResult(
                success=False,
                spec=None,
                errors=[str(e)],
                warnings=[]
            )

    def spec_to_dict(self, spec: FunctionSpec) -> Dict[str, Any]:
        """
        Convert a FunctionSpec back to dictionary format.

        Args:
            spec: FunctionSpec to convert

        Returns:
            Dictionary representation of the specification
        """
        return spec.dict(exclude_none=True)

    def generate_example_spec(self, function_name: str) -> Dict[str, Any]:
        """
        Generate an example specification for a given function name.

        Args:
            function_name: Name of the function

        Returns:
            Example specification dictionary
        """
        return {
            "name": function_name,
            "description": f"Example function: {function_name}",
            "input_type": "any",
            "output_type": "any",
            "parameters": [
                {
                    "name": "input_data",
                    "type": "any",
                    "description": "Input data for processing",
                    "required": True
                }
            ],
            "dependencies": [],
            "examples": [
                {
                    "input": {"input_data": "example"},
                    "output": "processed_example"
                }
            ],
            "rest_config": {
                "path": f"/{function_name}",
                "method": "POST"
            }
        }