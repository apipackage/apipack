"""
Mistral LLM Client

Client for interacting with local Mistral 7B model via Ollama.
Handles function generation, code optimization, and prompt management.
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
import ollama
from ollama import Client
import aiohttp

from .prompt_manager import PromptManager
from .response_parser import ResponseParser
from ..config.settings import get_settings

logger = logging.getLogger(__name__)

@dataclass
class GenerationRequest:
    """Request for code generation."""
    function_spec: Dict[str, Any]
    language: str
    context: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

@dataclass
class GenerationResponse:
    """Response from code generation."""
    success: bool
    code: Optional[str]
    explanation: Optional[str]
    metadata: Dict[str, Any]
    errors: List[str]

class MistralClient:
    """
    Client for Mistral 7B model integration.

    Provides methods for:
    - Function implementation generation
    - Code review and optimization
    - Documentation generation
    - Test case generation
    """

    def __init__(
        self,
        model: str = "mistral:7b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.1,
        max_tokens: int = 2048,
        timeout: int = 120
    ):
        """
        Initialize Mistral client.

        Args:
            model: Model name (default: mistral:7b)
            base_url: Ollama server URL
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
        """
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

        # Initialize components
        self.prompt_manager = PromptManager()
        self.response_parser = ResponseParser()

        # Initialize Ollama client
        try:
            self.client = Client(host=base_url)
            self._check_model_availability()
        except Exception as e:
            logger.error(f"Failed to initialize Mistral client: {e}")
            raise

    def _check_model_availability(self) -> bool:
        """Check if the specified model is available."""
        try:
            models = self.client.list()
            available_models = [model['name'] for model in models.get('models', [])]

            if self.model not in available_models:
                logger.warning(f"Model {self.model} not found. Available models: {available_models}")
                # Try to pull the model
                logger.info(f"Attempting to pull model: {self.model}")
                self.client.pull(self.model)
                logger.info(f"Successfully pulled model: {self.model}")

            return True

        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False

    def generate_function(
        self,
        function_spec: Dict[str, Any],
        language: str,
        **kwargs
    ) -> GenerationResponse:
        """
        Generate function implementation from specification.

        Args:
            function_spec: Function specification dictionary
            language: Target programming language
            **kwargs: Additional generation options

        Returns:
            GenerationResponse with generated code
        """
        logger.debug(f"Generating function: {function_spec.get('name')} in {language}")

        try:
            # Create generation request
            request = GenerationRequest(
                function_spec=function_spec,
                language=language,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                context=kwargs.get('context')
            )

            # Generate prompt
            prompt = self.prompt_manager.create_function_prompt(request)

            # Call Mistral model
            response = self._call_model(prompt, request.temperature, request.max_tokens)

            # Parse response
            parsed_response = self.response_parser.parse_function_response(
                response, language
            )

            if parsed_response.success:
                logger.debug(f"Successfully generated function: {function_spec.get('name')}")
            else:
                logger.warning(f"Function generation failed: {parsed_response.errors}")

            return parsed_response

        except Exception as e:
            logger.exception("Error generating function")
            return GenerationResponse(
                success=False,
                code=None,
                explanation=None,
                metadata={},
                errors=[str(e)]
            )

    async def generate_function_async(
        self,
        function_spec: Dict[str, Any],
        language: str,
        **kwargs
    ) -> GenerationResponse:
        """Async version of generate_function."""
        return await asyncio.to_thread(
            self.generate_function,
            function_spec,
            language,
            **kwargs
        )

    def generate_tests(
        self,
        function_code: str,
        function_spec: Dict[str, Any],
        language: str,
        test_framework: Optional[str] = None
    ) -> GenerationResponse:
        """
        Generate test cases for a function.

        Args:
            function_code: Generated function code
            function_spec: Function specification
            language: Programming language
            test_framework: Test framework to use (pytest, unittest, etc.)

        Returns:
            GenerationResponse with test code
        """
        logger.debug(f"Generating tests for function: {function_spec.get('name')}")

        try:
            prompt = self.prompt_manager.create_test_prompt(
                function_code, function_spec, language, test_framework
            )

            response = self._call_model(prompt, self.temperature, self.max_tokens)

            return self.response_parser.parse_test_response(response, language)

        except Exception as e:
            logger.exception("Error generating tests")
            return GenerationResponse(
                success=False,
                code=None,
                explanation=None,
                metadata={},
                errors=[str(e)]
            )

    def generate_documentation(
        self,
        function_code: str,
        function_spec: Dict[str, Any],
        language: str,
        doc_format: str = "markdown"
    ) -> GenerationResponse:
        """
        Generate documentation for a function.

        Args:
            function_code: Function code
            function_spec: Function specification
            language: Programming language
            doc_format: Documentation format (markdown, rst, etc.)

        Returns:
            GenerationResponse with documentation
        """
        logger.debug(f"Generating documentation for: {function_spec.get('name')}")

        try:
            prompt = self.prompt_manager.create_documentation_prompt(
                function_code, function_spec, language, doc_format
            )

            response = self._call_model(prompt, self.temperature, self.max_tokens)

            return self.response_parser.parse_documentation_response(
                response, doc_format
            )

        except Exception as e:
            logger.exception("Error generating documentation")
            return GenerationResponse(
                success=False,
                code=None,
                explanation=None,
                metadata={},
                errors=[str(e)]
            )

    def optimize_code(
        self,
        code: str,
        language: str,
        optimization_goals: List[str] = None
    ) -> GenerationResponse:
        """
        Optimize existing code.

        Args:
            code: Code to optimize
            language: Programming language
            optimization_goals: List of optimization goals (performance, readability, etc.)

        Returns:
            GenerationResponse with optimized code
        """
        logger.debug("Optimizing code")

        try:
            if optimization_goals is None:
                optimization_goals = ["performance", "readability", "maintainability"]

            prompt = self.prompt_manager.create_optimization_prompt(
                code, language, optimization_goals
            )

            response = self._call_model(prompt, self.temperature, self.max_tokens)

            return self.response_parser.parse_optimization_response(response, language)

        except Exception as e:
            logger.exception("Error optimizing code")
            return GenerationResponse(
                success=False,
                code=None,
                explanation=None,
                metadata={},
                errors=[str(e)]
            )

    def _call_model(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Call the Mistral model with a prompt.

        Args:
            prompt: Input prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Model response text
        """
        try:
            # Prepare options
            options = {
                "temperature": temperature or self.temperature,
                "num_predict": max_tokens or self.max_tokens,
                "stop": ["```", "---", "END"],
            }

            # Make request to Ollama
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options=options,
                stream=False
            )

            if 'response' in response:
                return response['response'].strip()
            else:
                raise Exception("No response from model")

        except Exception as e:
            logger.error(f"Error calling model: {e}")
            raise

    async def _call_model_stream(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from model (for long generations).

        Args:
            prompt: Input prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Response chunks
        """
        try:
            options = {
                "temperature": temperature or self.temperature,
                "num_predict": max_tokens or self.max_tokens,
                "stop": ["```", "---", "END"],
            }

            async with aiohttp.ClientSession() as session:
                data = {
                    "model": self.model,
                    "prompt": prompt,
                    "options": options,
                    "stream": True
                }

                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    async for line in response.content:
                        if line:
                            try:
                                chunk = json.loads(line.decode())
                                if 'response' in chunk:
                                    yield chunk['response']
                                if chunk.get('done', False):
                                    break
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"Error in streaming call: {e}")
            raise

    def health_check(self) -> Dict[str, Any]:
        """
        Check health of Mistral client and model.

        Returns:
            Dict with health status information
        """
        try:
            # Test basic connectivity
            models = self.client.list()

            # Test model availability
            available_models = [model['name'] for model in models.get('models', [])]
            model_available = self.model in available_models

            # Test simple generation
            test_prompt = "Hello, respond with 'OK' if you're working correctly."
            test_response = self._call_model(test_prompt, 0.1, 10)

            return {
                "status": "healthy",
                "model": self.model,
                "model_available": model_available,
                "available_models": available_models,
                "test_response": test_response,
                "base_url": self.base_url
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": self.model,
                "base_url": self.base_url
            }

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.

        Returns:
            Dict with model information
        """
        try:
            models = self.client.list()
            for model in models.get('models', []):
                if model['name'] == self.model:
                    return {
                        "name": model['name'],
                        "size": model.get('size', 'unknown'),
                        "modified": model.get('modified_at', 'unknown'),
                        "details": model.get('details', {})
                    }

            return {"error": f"Model {self.model} not found"}

        except Exception as e:
            return {"error": str(e)}

    def list_available_models(self) -> List[str]:
        """
        List all available models in Ollama.

        Returns:
            List of available model names
        """
        try:
            models = self.client.list()
            return [model['name'] for model in models.get('models', [])]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    def set_model(self, model_name: str) -> bool:
        """
        Switch to a different model.

        Args:
            model_name: Name of the model to switch to

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if model is available
            available_models = self.list_available_models()
            if model_name not in available_models:
                logger.warning(f"Model {model_name} not available. Attempting to pull...")
                self.client.pull(model_name)

            self.model = model_name
            logger.info(f"Switched to model: {model_name}")
            return True

        except Exception as e:
            logger.error(f"Error switching to model {model_name}: {e}")
            return False