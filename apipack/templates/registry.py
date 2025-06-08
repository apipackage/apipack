"""
Template Registry

Central registry for managing code generation templates.
Handles template discovery, loading, and caching.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import yaml
import json
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound

logger = logging.getLogger(__name__)


@dataclass
class TemplateInfo:
    """Information about a template."""
    name: str
    path: Path
    category: str
    language: Optional[str]
    interface_type: Optional[str]
    metadata: Dict[str, Any]
    dependencies: List[str]


@dataclass
class TemplateContext:
    """Context for template rendering."""
    function_specs: List[Dict[str, Any]]
    language: str
    interface_type: str
    project_config: Dict[str, Any]
    additional_vars: Dict[str, Any]


class TemplateRegistry:
    """
    Registry for managing and discovering templates.

    Organizes templates by:
    - Category (interface, language, deployment)
    - Language (python, javascript, go, etc.)
    - Interface type (rest, grpc, websocket, etc.)
    """

    def __init__(self, search_paths: Optional[List[Path]] = None):
        """
        Initialize template registry.

        Args:
            search_paths: Additional paths to search for templates
        """
        self.templates: Dict[str, TemplateInfo] = {}
        self.environments: Dict[str, Environment] = {}
        self.search_paths: List[Path] = []

        # Add default search paths
        self._add_default_search_paths()

        # Add custom search paths
        if search_paths:
            self.search_paths.extend(search_paths)

        # Discover and load templates
        self.discover_templates()

    def _add_default_search_paths(self):
        """Add default template search paths."""
        # Built-in templates (package templates)
        package_dir = Path(__file__).parent
        self.search_paths.append(package_dir)

        # User templates
        user_templates = Path.home() / ".apipack" / "templates"
        if user_templates.exists():
            self.search_paths.append(user_templates)

        # Current directory templates
        current_templates = Path.cwd() / "templates"
        if current_templates.exists():
            self.search_paths.append(current_templates)

    def discover_templates(self):
        """Discover all templates in search paths."""
        logger.debug(f"Discovering templates in {len(self.search_paths)} paths")

        for search_path in self.search_paths:
            if search_path.exists():
                self._discover_templates_in_path(search_path)

        logger.info(f"Discovered {len(self.templates)} templates")

    def _discover_templates_in_path(self, path: Path):
        """Discover templates in a specific path."""
        try:
            # Look for template configuration files
            for config_file in path.rglob("template.yml"):
                self._load_template_from_config(config_file)

            # Look for direct template files
            for template_file in path.rglob("*.template"):
                self._load_template_from_file(template_file)

        except Exception as e:
            logger.warning(f"Error discovering templates in {path}: {e}")

    def _load_template_from_config(self, config_file: Path):
        """Load template from configuration file."""
        try:
            config = yaml.safe_load(config_file.read_text())
            template_dir = config_file.parent

            template_info = TemplateInfo(
                name=config.get("name", template_dir.name),
                path=template_dir,
                category=config.get("category", "unknown"),
                language=config.get("language"),
                interface_type=config.get("interface_type"),
                metadata=config.get("metadata", {}),
                dependencies=config.get("dependencies", [])
            )

            self.templates[template_info.name] = template_info

            # Create Jinja2 environment for this template
            self.environments[template_info.name] = Environment(
                loader=FileSystemLoader(template_dir),
                trim_blocks=True,
                lstrip_blocks=True
            )

            logger.debug(f"Loaded template: {template_info.name}")

        except Exception as e:
            logger.warning(f"Error loading template config {config_file}: {e}")

    def _load_template_from_file(self, template_file: Path):
        """Load template from .template file."""
        try:
            # Parse template name and metadata from filename
            name_parts = template_file.stem.split(".")

            if len(name_parts) >= 2:
                interface_type = name_parts[0]
                language = name_parts[1] if len(name_parts) > 2 else None
                category = "interface"
            else:
                interface_type = None
                language = None
                category = "generic"

            template_name = template_file.stem

            template_info = TemplateInfo(
                name=template_name,
                path=template_file,
                category=category,
                language=language,
                interface_type=interface_type,
                metadata={},
                dependencies=[]
            )

            self.templates[template_name] = template_info

            # Create Jinja2 environment
            self.environments[template_name] = Environment(
                loader=FileSystemLoader(template_file.parent),
                trim_blocks=True,
                lstrip_blocks=True
            )

            logger.debug(f"Loaded template file: {template_name}")

        except Exception as e:
            logger.warning(f"Error loading template file {template_file}: {e}")

    def get_template(self, name: str) -> Optional[Template]:
        """
        Get a template by name.

        Args:
            name: Template name

        Returns:
            Jinja2 Template object or None if not found
        """
        if name not in self.templates:
            logger.warning(f"Template not found: {name}")
            return None

        try:
            template_info = self.templates[name]
            env = self.environments[name]

            if template_info.path.is_file():
                # Single template file
                return env.get_template(template_info.path.name)
            else:
                # Template directory - look for main template
                main_template = template_info.path / "main.template"
                if main_template.exists():
                    return env.get_template("main.template")
                else:
                    # Look for any .template file
                    template_files = list(template_info.path.glob("*.template"))
                    if template_files:
                        return env.get_template(template_files[0].name)

            logger.warning(f"No template file found for: {name}")
            return None

        except TemplateNotFound as e:
            logger.error(f"Template file not found: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading template {name}: {e}")
            return None

    def find_templates(
            self,
            category: Optional[str] = None,
            language: Optional[str] = None,
            interface_type: Optional[str] = None
    ) -> List[TemplateInfo]:
        """
        Find templates matching criteria.

        Args:
            category: Template category
            language: Programming language
            interface_type: Interface type

        Returns:
            List of matching TemplateInfo objects
        """
        results = []

        for template_info in self.templates.values():
            if category and template_info.category != category:
                continue
            if language and template_info.language != language:
                continue
            if interface_type and template_info.interface_type != interface_type:
                continue

            results.append(template_info)

        return results

    def render_template(
            self,
            template_name: str,
            context: TemplateContext
    ) -> Optional[str]:
        """
        Render a template with context.

        Args:
            template_name: Name of template to render
            context: Template context

        Returns:
            Rendered template string or None if error
        """
        template = self.get_template(template_name)
        if not template:
            return None

        try:
            # Prepare template variables
            template_vars = {
                "functions": context.function_specs,
                "language": context.language,
                "interface_type": context.interface_type,
                "project": context.project_config,
                **context.additional_vars
            }

            # Add helper functions
            template_vars.update(self._get_template_helpers())

            return template.render(**template_vars)

        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            return None

    def get_interface_templates(self, interface_type: str, language: str) -> List[str]:
        """
        Get all templates for a specific interface and language.

        Args:
            interface_type: Type of interface (rest, grpc, etc.)
            language: Programming language

        Returns:
            List of template names
        """
        templates = self.find_templates(
            category="interface",
            language=language,
            interface_type=interface_type
        )
        return [t.name for t in templates]

    def get_language_templates(self, language: str) -> List[str]:
        """
        Get all templates for a specific language.

        Args:
            language: Programming language

        Returns:
            List of template names
        """
        templates = self.find_templates(language=language)
        return [t.name for t in templates]

    def list_templates(self) -> Dict[str, List[str]]:
        """
        List all templates grouped by category.

        Returns:
            Dict mapping categories to template lists
        """
        categories: Dict[str, List[str]] = {}

        for template_info in self.templates.values():
            category = template_info.category
            if category not in categories:
                categories[category] = []
            categories[category].append(template_info.name)

        return categories

    def get_template_info(self, name: str) -> Optional[TemplateInfo]:
        """
        Get detailed information about a template.

        Args:
            name: Template name

        Returns:
            TemplateInfo object or None if not found
        """
        return self.templates.get(name)

    def register_template(
            self,
            name: str,
            path: Path,
            category: str,
            language: Optional[str] = None,
            interface_type: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Register a new template.

        Args:
            name: Template name
            path: Path to template file or directory
            category: Template category
            language: Programming language (optional)
            interface_type: Interface type (optional)
            metadata: Additional metadata (optional)
        """
        template_info = TemplateInfo(
            name=name,
            path=path,
            category=category,
            language=language,
            interface_type=interface_type,
            metadata=metadata or {},
            dependencies=[]
        )

        self.templates[name] = template_info

        # Create Jinja2 environment
        if path.is_file():
            loader_path = path.parent
        else:
            loader_path = path

        self.environments[name] = Environment(
            loader=FileSystemLoader(loader_path),
            trim_blocks=True,
            lstrip_blocks=True
        )

        logger.info(f"Registered template: {name}")

    def _get_template_helpers(self) -> Dict[str, Any]:
        """Get helper functions for templates."""
        return {
            "snake_case": self._snake_case,
            "camel_case": self._camel_case,
            "pascal_case": self._pascal_case,
            "kebab_case": self._kebab_case,
            "upper_case": str.upper,
            "lower_case": str.lower,
            "format_type": self._format_type,
            "format_imports": self._format_imports,
        }

    def _snake_case(self, text: str) -> str:
        """Convert text to snake_case."""
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()

    def _camel_case(self, text: str) -> str:
        """Convert text to camelCase."""
        components = text.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])

    def _pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        return ''.join(word.capitalize() for word in text.split('_'))

    def _kebab_case(self, text: str) -> str:
        """Convert text to kebab-case."""
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '-', text).lower().replace('_', '-')

    def _format_type(self, type_name: str, language: str) -> str:
        """Format type name for specific language."""
        type_mappings = {
            "python": {
                "string": "str",
                "integer": "int",
                "boolean": "bool",
                "list": "List",
                "dict": "Dict",
                "any": "Any"
            },
            "javascript": {
                "string": "string",
                "integer": "number",
                "boolean": "boolean",
                "list": "Array",
                "dict": "Object",
                "any": "any"
            },
            "go": {
                "string": "string",
                "integer": "int",
                "boolean": "bool",
                "list": "[]interface{}",
                "dict": "map[string]interface{}",
                "any": "interface{}"
            }
        }

        lang_mapping = type_mappings.get(language, {})
        return lang_mapping.get(type_name, type_name)

    def _format_imports(self, dependencies: List[str], language: str) -> str:
        """Format import statements for specific language."""
        if not dependencies:
            return ""

        if language == "python":
            return "\n".join(f"import {dep}" for dep in dependencies)
        elif language == "javascript":
            return "\n".join(f"const {dep.split('/')[-1]} = require('{dep}');" for dep in dependencies)
        elif language == "go":
            imports = "\n".join(f'    "{dep}"' for dep in dependencies)
            return f"import (\n{imports}\n)"
        else:
            return "\n".join(dependencies)

    def get_available_languages(self) -> Set[str]:
        """Get set of all available languages."""
        languages = set()
        for template_info in self.templates.values():
            if template_info.language:
                languages.add(template_info.language)
        return languages

    def get_available_interfaces(self) -> Set[str]:
        """Get set of all available interface types."""
        interfaces = set()
        for template_info in self.templates.values():
            if template_info.interface_type:
                interfaces.add(template_info.interface_type)
        return interfaces

    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """
        Validate a template for syntax and completeness.

        Args:
            template_name: Name of template to validate

        Returns:
            Dict with validation results
        """
        template = self.get_template(template_name)
        if not template:
            return {
                "valid": False,
                "errors": [f"Template {template_name} not found"]
            }

        errors = []
        warnings = []

        try:
            # Test template compilation
            template.new_context()

            # Check for required variables
            template_info = self.templates[template_name]
            required_vars = template_info.metadata.get("required_variables", [])

            # Try rendering with minimal context
            test_context = TemplateContext(
                function_specs=[],
                language="python",
                interface_type="rest",
                project_config={},
                additional_vars={}
            )

            try:
                self.render_template(template_name, test_context)
            except Exception as e:
                if "undefined" in str(e).lower():
                    warnings.append(f"Template may have undefined variables: {e}")
                else:
                    errors.append(f"Template rendering error: {e}")

        except Exception as e:
            errors.append(f"Template compilation error: {e}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }