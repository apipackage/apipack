"""
Prompt Manager

Manages prompts for different types of code generation tasks.
Provides optimized prompts for Mistral 7B model.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import json

from ..core.parser import FunctionSpec

logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """Template for generating prompts."""
    name: str
    template: str
    variables: List[str]
    language_specific: bool = False


class PromptManager:
    """
    Manages prompt templates for code generation.

    Provides specialized prompts for:
    - Function implementation
    - Test generation
    - Documentation
    - Code optimization
    """

    def __init__(self, custom_templates_dir: Optional[Path] = None):
        """
        Initialize prompt manager.

        Args:
            custom_templates_dir: Optional directory for custom prompt templates
        """
        self.templates: Dict[str, PromptTemplate] = {}
        self.language_configs: Dict[str, Dict[str, Any]] = {}

        # Load built-in templates
        self._load_builtin_templates()

        # Load language configurations
        self._load_language_configs()

        # Load custom templates if provided
        if custom_templates_dir:
            self._load_custom_templates(custom_templates_dir)

    def create_function_prompt(self, request) -> str:
        """
        Create prompt for function implementation generation.

        Args:
            request: GenerationRequest object

        Returns:
            Formatted prompt string
        """
        spec = request.function_spec
        language = request.language

        # Get language-specific configuration
        lang_config = self.language_configs.get(language, {})

        # Build function signature
        signature = self._build_function_signature(spec, language)

        # Create prompt
        prompt = f"""You are an expert {language} programmer. Generate a complete, production-ready function implementation.

FUNCTION SPECIFICATION:
Name: {spec.get('name')}
Description: {spec.get('description', 'No description provided')}
Input Type: {spec.get('input_type', 'any')}
Output Type: {spec.get('output_type', 'any')}

FUNCTION SIGNATURE:
{signature}

REQUIREMENTS:
1. Write clean, efficient, and well-documented code
2. Include proper error handling and validation
3. Follow {language} best practices and conventions
4. Add type hints/annotations where applicable
5. Handle edge cases appropriately
6. Make the function robust and production-ready

DEPENDENCIES AVAILABLE:
{self._format_dependencies(spec.get('dependencies', []), language)}

EXAMPLES:
{self._format_examples(spec.get('examples', []))}

RESPONSE FORMAT:
Provide only the function implementation without markdown formatting or explanations.
Start directly with the function definition.

FUNCTION IMPLEMENTATION:
"""

        return prompt

    def create_test_prompt(
            self,
            function_code: str,
            function_spec: Dict[str, Any],
            language: str,
            test_framework: Optional[str] = None
    ) -> str:
        """Create prompt for test generation."""

        # Determine test framework
        if not test_framework:
            test_framework = self._get_default_test_framework(language)

        prompt = f"""You are an expert in {language} testing. Generate comprehensive test cases for the following function.

FUNCTION TO TEST:
```{language}
{function_code}
```

FUNCTION SPECIFICATION:
Name: {function_spec.get('name')}
Description: {function_spec.get('description', 'No description')}
Input Type: {function_spec.get('input_type')}
Output Type: {function_spec.get('output_type')}

TEST REQUIREMENTS:
1. Use {test_framework} framework
2. Test normal operation cases
3. Test edge cases and boundary conditions
4. Test error conditions and exception handling
5. Include both positive and negative test cases
6. Add performance tests if applicable
7. Mock external dependencies if needed

RESPONSE FORMAT:
Provide complete test file with all necessary imports and test classes/functions.
Include setup and teardown methods if needed.

TEST CODE:
"""
        return prompt

    def create_documentation_prompt(
            self,
            function_code: str,
            function_spec: Dict[str, Any],
            language: str,
            doc_format: str = "markdown"
    ) -> str:
        """Create prompt for documentation generation."""

        prompt = f"""Generate comprehensive documentation for the following {language} function.

FUNCTION CODE:
```{language}
{function_code}
```

FUNCTION SPECIFICATION:
{json.dumps(function_spec, indent=2)}

DOCUMENTATION REQUIREMENTS:
1. Format: {doc_format}
2. Include function purpose and description
3. Document all parameters with types and descriptions
4. Document return value with type and description
5. Include usage examples
6. Document any exceptions that might be raised
7. Add performance notes if relevant
8. Include any dependencies or prerequisites

RESPONSE FORMAT:
Provide documentation in {doc_format} format only, without code blocks or additional formatting.

DOCUMENTATION:
"""
        return prompt

    def create_optimization_prompt(
            self,
            code: str,
            language: str,
            optimization_goals: List[str]
    ) -> str:
        """Create prompt for code optimization."""

        goals_text = ", ".join(optimization_goals)

        prompt = f"""You are an expert {language} developer specializing in code optimization. 
Optimize the following code focusing on: {goals_text}

ORIGINAL CODE:
```{language}
{code}
```

OPTIMIZATION GOALS:
{self._format_optimization_goals(optimization_goals)}

REQUIREMENTS:
1. Maintain the same functionality and interface
2. Improve code according to specified goals
3. Add comments explaining optimizations
4. Ensure code remains readable and maintainable
5. Follow {language} best practices
6. Preserve or improve error handling

RESPONSE FORMAT:
Provide the optimized code without markdown formatting, followed by a brief explanation of changes.

OPTIMIZED CODE:
"""
        return prompt

    def create_interface_prompt(
            self,
            functions: List[Dict[str, Any]],
            interface_type: str,
            language: str
    ) -> str:
        """Create prompt for interface generation (REST, gRPC, etc.)."""

        functions_list = "\n".join([
            f"- {func.get('name')}: {func.get('description', 'No description')}"
            for func in functions
        ])

        prompt = f"""Generate a {interface_type} interface in {language} for the following functions:

FUNCTIONS:
{functions_list}

INTERFACE REQUIREMENTS:
1. Create a complete {interface_type} server implementation
2. Include proper routing and endpoint definitions
3. Add request/response validation
4. Include error handling and status codes
5. Add logging and monitoring capabilities
6. Follow {interface_type} best practices
7. Include health check endpoints
8. Add proper documentation/comments

RESPONSE FORMAT:
Provide complete server code without markdown formatting.

{interface_type.upper()} SERVER:
"""
        return prompt

    def _build_function_signature(self, spec: Dict[str, Any], language: str) -> str:
        """Build function signature based on language and spec."""

        name = spec.get('name')
        params = spec.get('parameters', [])

        if language == "python":
            param_strings = []
            for param in params:
                param_str = f"{param['name']}: {param.get('type', 'Any')}"
                if not param.get('required', True) and 'default' in param:
                    param_str += f" = {param['default']}"
                param_strings.append(param_str)

            params_str = ", ".join(param_strings)
            return_type = spec.get('output_type', 'Any')
            return f"def {name}({params_str}) -> {return_type}:"

        elif language == "javascript":
            param_strings = [param['name'] for param in params]
            params_str = ", ".join(param_strings)
            return f"function {name}({params_str}) {{"

        elif language == "go":
            param_strings = []
            for param in params:
                go_type = self._convert_type_to_go(param.get('type', 'interface{}'))
                param_strings.append(f"{param['name']} {go_type}")

            params_str = ", ".join(param_strings)
            return_type = self._convert_type_to_go(spec.get('output_type', 'interface{}'))
            return f"func {name}({params_str}) {return_type} {{"

        else:
            # Generic signature
            param_strings = [param['name'] for param in params]
            params_str = ", ".join(param_strings)
            return f"{name}({params_str})"

    def _format_dependencies(self, dependencies: List[str], language: str) -> str:
        """Format dependencies list for the prompt."""
        if not dependencies:
            return "Standard library only"

        return "\n".join([f"- {dep}" for dep in dependencies])

    def _format_examples(self, examples: List[Dict[str, Any]]) -> str:
        """Format examples for the prompt."""
        if not examples:
            return "No examples provided"

        formatted = []
        for i, example in enumerate(examples, 1):
            formatted.append(f"Example {i}:")
            formatted.append(f"  Input: {example.get('input', 'N/A')}")
            formatted.append(f"  Output: {example.get('output', 'N/A')}")

        return "\n".join(formatted)

    def _format_optimization_goals(self, goals: List[str]) -> str:
        """Format optimization goals for the prompt."""
        goal_descriptions = {
            "performance": "Improve execution speed and reduce computational complexity",
            "memory": "Reduce memory usage and optimize data structures",
            "readability": "Improve code clarity and maintainability",
            "maintainability": "Make code easier to modify and extend",
            "security": "Enhance security and input validation",
            "error_handling": "Improve error detection and recovery"
        }

        formatted = []
        for goal in goals:
            description = goal_descriptions.get(goal, "General optimization")
            formatted.append(f"- {goal.title()}: {description}")

        return "\n".join(formatted)

    def _get_default_test_framework(self, language: str) -> str:
        """Get default test framework for a language."""
        frameworks = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
            "go": "testing",
            "java": "junit",
            "rust": "built-in",
            "csharp": "xunit"
        }
        return frameworks.get(language, "unittest")

    def _convert_type_to_go(self, type_name: str) -> str:
        """Convert generic type to Go type."""
        type_mapping = {
            "string": "string",
            "str": "string",
            "int": "int",
            "integer": "int",
            "float": "float64",
            "bool": "bool",
            "boolean": "bool",
            "bytes": "[]byte",
            "list": "[]interface{}",
            "dict": "map[string]interface{}",
            "any": "interface{}",
            "object": "interface{}"
        }
        return type_mapping.get(type_name, "interface{}")

    def _load_builtin_templates(self):
        """Load built-in prompt templates."""
        # This would load templates from embedded resources
        # For now, we use the methods above as templates
        pass

    def _load_language_configs(self):
        """Load language-specific configurations."""
        self.language_configs = {
            "python": {
                "file_extension": ".py",
                "import_style": "import",
                "type_system": "dynamic_typed",
                "test_framework": "pytest"
            },
            "javascript": {
                "file_extension": ".js",
                "import_style": "require/import",
                "type_system": "dynamic_typed",
                "test_framework": "jest"
            },
            "go": {
                "file_extension": ".go",
                "import_style": "import",
                "type_system": "static_typed",
                "test_framework": "testing"
            }
        }

    def _load_custom_templates(self, templates_dir: Path):
        """Load custom prompt templates from directory."""
        if not templates_dir.exists():
            return

        for template_file in templates_dir.glob("*.txt"):
            try:
                content = template_file.read_text(encoding="utf-8")
                template_name = template_file.stem

                # Parse template (simple format for now)
                self.templates[template_name] = PromptTemplate(
                    name=template_name,
                    template=content,
                    variables=[],  # Would be parsed from template
                    language_specific=False
                )

                logger.debug(f"Loaded custom template: {template_name}")

            except Exception as e:
                logger.warning(f"Failed to load template {template_file}: {e}")

    def add_custom_template(self, name: str, template: str, variables: List[str] = None):
        """Add a custom template programmatically."""
        self.templates[name] = PromptTemplate(
            name=name,
            template=template,
            variables=variables or [],
            language_specific=False
        )
        logger.debug(f"Added custom template: {name}")

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name."""
        return self.templates.get(name)

    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.templates.keys())