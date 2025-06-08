"""
APIpack Core Engine

Main orchestrator for the API package generation process.
Coordinates all components: parser, LLM, templates, generator, validator, and deployer.
"""

import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ..config.settings import Settings, get_settings
from ..llm.mistral_client import MistralClient
from ..templates.registry import TemplateRegistry
from .parser import FunctionSpecParser
from .generator import CodeGenerator
from .validator import CodeValidator
from .deployer import PackageDeployer
from ..plugins.base_plugin import PluginManager
from ..utils.file_utils import ensure_directory

logger = logging.getLogger(__name__)


@dataclass
class GenerationContext:
    """Context object passed through the generation pipeline."""
    function_specs: List[Dict[str, Any]]
    interfaces: List[str]
    language: str
    output_dir: Path
    config: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_files: List[Path] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class GenerationResult:
    """Result of package generation process."""
    success: bool
    output_dir: Path
    generated_files: List[Path]
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    package_info: Optional[Dict[str, Any]] = None


class APIPackEngine:
    """
    Main engine for API package generation.

    Orchestrates the entire pipeline:
    1. Parse function specifications
    2. Generate function implementations using LLM
    3. Apply templates for interfaces
    4. Validate generated code
    5. Deploy package
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the APIpack engine.

        Args:
            config: Optional configuration dictionary
        """
        self.settings = get_settings()
        if config:
            self.settings.update(config)

        # Initialize components
        self.parser = FunctionSpecParser()
        self.llm_client = MistralClient(
            model=self.settings.llm.model,
            temperature=self.settings.llm.temperature,
            max_tokens=self.settings.llm.max_tokens
        )
        self.template_registry = TemplateRegistry()
        self.code_generator = CodeGenerator(
            llm_client=self.llm_client,
            template_registry=self.template_registry
        )
        self.validator = CodeValidator()
        self.deployer = PackageDeployer()
        self.plugin_manager = PluginManager()

        logger.info("APIpack engine initialized")

    def generate_package(
            self,
            function_specs: List[Dict[str, Any]],
            interfaces: List[str],
            language: str,
            output_dir: Union[str, Path] = "./generated",
            **kwargs
    ) -> GenerationResult:
        """
        Generate a complete API package.

        Args:
            function_specs: List of function specifications
            interfaces: List of interfaces to generate (rest, grpc, etc.)
            language: Target programming language
            output_dir: Output directory for generated package
            **kwargs: Additional options

        Returns:
            GenerationResult: Result of the generation process
        """
        logger.info(f"Starting package generation for {len(function_specs)} functions")

        # Create generation context
        context = GenerationContext(
            function_specs=function_specs,
            interfaces=interfaces,
            language=language,
            output_dir=Path(output_dir),
            config=dict(self.settings, **kwargs)
        )

        try:
            # Ensure output directory exists
            ensure_directory(context.output_dir)

            # Pipeline execution
            context = self._parse_specifications(context)
            context = self._generate_functions(context)
            context = self._generate_interfaces(context)
            context = self._validate_code(context)
            context = self._assemble_package(context)

            # Create result
            result = GenerationResult(
                success=len(context.errors) == 0,
                output_dir=context.output_dir,
                generated_files=context.generated_files,
                errors=context.errors,
                warnings=context.warnings,
                metadata=context.metadata
            )

            if result.success:
                logger.info(f"Package generation completed successfully at {result.output_dir}")
            else:
                logger.error(f"Package generation failed with {len(result.errors)} errors")

            return result

        except Exception as e:
            logger.exception("Unexpected error during package generation")
            return GenerationResult(
                success=False,
                output_dir=context.output_dir,
                generated_files=[],
                errors=[str(e)],
                warnings=[],
                metadata={}
            )

    async def generate_package_async(
            self,
            function_specs: List[Dict[str, Any]],
            interfaces: List[str],
            language: str,
            output_dir: Union[str, Path] = "./generated",
            **kwargs
    ) -> GenerationResult:
        """
        Async version of generate_package for better performance.
        """
        return await asyncio.to_thread(
            self.generate_package,
            function_specs,
            interfaces,
            language,
            output_dir,
            **kwargs
        )

    def _parse_specifications(self, context: GenerationContext) -> GenerationContext:
        """Parse and validate function specifications."""
        logger.debug("Parsing function specifications")

        try:
            parsed_specs = []
            for spec in context.function_specs:
                parsed_spec = self.parser.parse(spec)
                if parsed_spec:
                    parsed_specs.append(parsed_spec)
                else:
                    context.errors.append(f"Failed to parse specification: {spec}")

            context.function_specs = parsed_specs
            context.metadata["parsed_functions"] = len(parsed_specs)

        except Exception as e:
            context.errors.append(f"Specification parsing error: {str(e)}")

        return context

    def _generate_functions(self, context: GenerationContext) -> GenerationContext:
        """Generate function implementations using LLM."""
        logger.debug("Generating function implementations")

        try:
            generated_functions = []
            for spec in context.function_specs:
                logger.debug(f"Generating function: {spec['name']}")

                function_code = self.code_generator.generate_function(
                    spec, context.language
                )

                if function_code:
                    spec["implementation"] = function_code
                    generated_functions.append(spec)
                else:
                    context.errors.append(f"Failed to generate function: {spec['name']}")

            context.function_specs = generated_functions
            context.metadata["generated_functions"] = len(generated_functions)

        except Exception as e:
            context.errors.append(f"Function generation error: {str(e)}")

        return context

    def _generate_interfaces(self, context: GenerationContext) -> GenerationContext:
        """Generate interface implementations (REST, gRPC, etc.)."""
        logger.debug("Generating interface implementations")

        try:
            interface_files = []
            for interface in context.interfaces:
                logger.debug(f"Generating interface: {interface}")

                files = self.code_generator.generate_interface(
                    interface, context.function_specs, context.language
                )

                if files:
                    interface_files.extend(files)
                    context.generated_files.extend(files)
                else:
                    context.warnings.append(f"No templates found for interface: {interface}")

            context.metadata["generated_interfaces"] = len(context.interfaces)
            context.metadata["interface_files"] = len(interface_files)

        except Exception as e:
            context.errors.append(f"Interface generation error: {str(e)}")

        return context

    def _validate_code(self, context: GenerationContext) -> GenerationContext:
        """Validate generated code."""
        logger.debug("Validating generated code")

        try:
            validation_results = []
            for file_path in context.generated_files:
                if file_path.exists():
                    result = self.validator.validate_file(file_path, context.language)
                    validation_results.append(result)

                    if not result.is_valid:
                        context.warnings.extend(result.warnings)
                        if result.errors:
                            context.errors.extend(result.errors)

            context.metadata["validation_results"] = len(validation_results)
            context.metadata["valid_files"] = sum(1 for r in validation_results if r.is_valid)

        except Exception as e:
            context.errors.append(f"Code validation error: {str(e)}")

        return context

    def _assemble_package(self, context: GenerationContext) -> GenerationContext:
        """Assemble the final package with all components."""
        logger.debug("Assembling package")

        try:
            # Generate package structure
            package_files = self.code_generator.generate_package_structure(
                context.function_specs,
                context.interfaces,
                context.language,
                context.output_dir
            )

            context.generated_files.extend(package_files)

            # Generate additional files (Dockerfile, requirements, etc.)
            additional_files = self.code_generator.generate_additional_files(
                context.function_specs,
                context.language,
                context.output_dir
            )

            context.generated_files.extend(additional_files)
            context.metadata["total_files"] = len(context.generated_files)

        except Exception as e:
            context.errors.append(f"Package assembly error: {str(e)}")

        return context

    def deploy_package(
            self,
            package_dir: Union[str, Path],
            deployment_type: str = "docker",
            **kwargs
    ) -> Dict[str, Any]:
        """
        Deploy a generated package.

        Args:
            package_dir: Directory containing the generated package
            deployment_type: Type of deployment (docker, kubernetes, etc.)
            **kwargs: Deployment-specific options

        Returns:
            Dict containing deployment result information
        """
        logger.info(f"Deploying package from {package_dir} using {deployment_type}")

        try:
            result = self.deployer.deploy(
                package_dir=Path(package_dir),
                deployment_type=deployment_type,
                **kwargs
            )

            if result.get("success"):
                logger.info("Package deployed successfully")
            else:
                logger.error(f"Deployment failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.exception("Deployment error")
            return {
                "success": False,
                "error": str(e)
            }

    def list_available_templates(self) -> Dict[str, List[str]]:
        """
        List all available templates by category.

        Returns:
            Dict mapping categories to lists of template names
        """
        return self.template_registry.list_templates()

    def list_available_interfaces(self) -> List[str]:
        """
        List all available interface types.

        Returns:
            List of interface type names
        """
        return self.plugin_manager.list_plugins()

    def get_function_template(self, language: str) -> str:
        """
        Get the function template for a specific language.

        Args:
            language: Programming language

        Returns:
            Template string for functions in the specified language
        """
        return self.template_registry.get_function_template(language)

    def validate_specification(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a function specification without generating code.

        Args:
            spec: Function specification to validate

        Returns:
            Dict containing validation results
        """
        try:
            parsed_spec = self.parser.parse(spec)
            return {
                "valid": parsed_spec is not None,
                "parsed_spec": parsed_spec,
                "errors": self.parser.get_last_errors()
            }
        except Exception as e:
            return {
                "valid": False,
                "parsed_spec": None,
                "errors": [str(e)]
            }