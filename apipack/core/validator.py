"""
Code Validator for APIpack.

This module provides the CodeValidator class which is responsible for validating
generated code against various quality and style standards.
"""
import ast
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

logger = logging.getLogger(__name__)

class CodeValidator:
    """Validates generated code for syntax, style, and quality."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the code validator.
        
        Args:
            config: Configuration dictionary for the validator.
        """
        self.config = config or {}
        self._setup_validators()
    
    def _setup_validators(self) -> None:
        """Set up validators based on configuration."""
        self.validators = {
            'syntax': self._validate_syntax,
            'type_hints': self._validate_type_hints,
            'docstrings': self._validate_docstrings,
        }
        
        # Enable/disable validators based on config
        for validator in list(self.validators.keys()):
            if self.config.get(f'disable_{validator}', False):
                del self.validators[validator]
    
    def validate_file(self, file_path: Union[str, Path]) -> Dict[str, List[str]]:
        """Validate a single file.
        
        Args:
            file_path: Path to the file to validate.
            
        Returns:
            Dictionary mapping validator names to lists of error messages.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        results = {}
        
        # Read the file content once and pass it to validators
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Run each validator
            for name, validator in self.validators.items():
                try:
                    errors = validator(content, str(file_path))
                    if errors:
                        results[name] = errors
                except Exception as e:
                    logger.error("Validator %s failed: %s", name, str(e))
                    results[name] = [f"Validator error: {str(e)}"]
                    
        except Exception as e:
            logger.error("Error reading file %s: %s", file_path, str(e))
            results['file_error'] = [f"Failed to read file: {str(e)}"]
            
        return results
    
    def validate_directory(
        self, 
        dir_path: Union[str, Path], 
        file_pattern: str = "*.py"
    ) -> Dict[str, Dict[str, List[str]]]:
        """Validate all files in a directory matching the pattern.
        
        Args:
            dir_path: Directory to search for files.
            file_pattern: File pattern to match (e.g., '*.py').
            
        Returns:
            Nested dictionary mapping file paths to validation results.
        """
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Directory not found: {dir_path}")
            
        results = {}
        
        for file_path in dir_path.rglob(file_pattern):
            if file_path.is_file():
                file_results = self.validate_file(file_path)
                if file_results:
                    results[str(file_path.relative_to(dir_path))] = file_results
                    
        return results
    
    def _validate_syntax(self, content: str, file_path: str) -> List[str]:
        """Validate Python syntax.
        
        Args:
            content: Source code to validate.
            file_path: Path to the file (for error messages).
            
        Returns:
            List of error messages, or empty list if valid.
        """
        try:
            ast.parse(content)
            return []
        except SyntaxError as e:
            return [f"Syntax error in {file_path} at line {e.lineno}: {e.msg}"]
    
    def _validate_type_hints(self, content: str, file_path: str) -> List[str]:
        """Check for missing type hints in function signatures.
        
        Args:
            content: Source code to validate.
            file_path: Path to the file (for error messages).
            
        Returns:
            List of error messages, or empty list if valid.
        """
        if not self.config.get('check_type_hints', True):
            return []
            
        errors = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check return type annotation
                    if node.returns is None and not node.name.startswith('_'):
                        errors.append(
                            f"Missing return type annotation for function '{node.name}' "
                            f"in {file_path}:{node.lineno}"
                        )
                    
                    # Check argument type annotations
                    for arg in node.args.args:
                        if arg.annotation is None and not arg.arg.startswith('_'):
                            errors.append(
                                f"Missing type annotation for parameter '{arg.arg}' "
                                f"in function '{node.name}' in {file_path}:{node.lineno}"
                            )
                            
        except Exception as e:
            logger.error("Error checking type hints in %s: %s", file_path, str(e))
            return [f"Type hint check failed: {str(e)}"]
            
        return errors
    
    def _validate_docstrings(self, content: str, file_path: str) -> List[str]:
        """Check for missing or malformed docstrings.
        
        Args:
            content: Source code to validate.
            file_path: Path to the file (for error messages).
            
        Returns:
            List of error messages, or empty list if valid.
        """
        if not self.config.get('check_docstrings', True):
            return []
            
        errors = []
        
        try:
            tree = ast.parse(content)
            
            # Check module docstring
            if not (tree.body and isinstance(tree.body[0], ast.Expr) and 
                   isinstance(tree.body[0].value, ast.Str)):
                errors.append(f"Missing module docstring in {file_path}")
            
            # Check function and class docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if not (node.body and isinstance(node.body[0], ast.Expr) and 
                           isinstance(node.body[0].value, ast.Str)):
                        node_type = 'function' if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else 'class'
                        errors.append(
                            f"Missing {node_type} docstring for '{node.name}' in {file_path}:{node.lineno}"
                        )
                            
        except Exception as e:
            logger.error("Error checking docstrings in %s: %s", file_path, str(e))
            return [f"Docstring check failed: {str(e)}"]
            
        return errors
    
    def run_external_linter(
        self, 
        file_path: Union[str, Path], 
        linter: str = "pylint"
    ) -> Tuple[bool, str]:
        """Run an external linter on the given file.
        
        Args:
            file_path: Path to the file to lint.
            linter: Name of the linter to use (e.g., 'pylint', 'flake8').
            
        Returns:
            Tuple of (success, output) where success is a boolean indicating
            if the linting passed, and output is the linter output.
        """
        try:
            result = subprocess.run(
                [linter, str(file_path)],
                capture_output=True,
                text=True,
                check=False
            )
            
            # Consider it a pass if the linter returns 0 or 1 (some linters use 1 for warnings)
            success = result.returncode in (0, 1)
            output = result.stdout or result.stderr
            
            return success, output
            
        except FileNotFoundError:
            logger.warning("Linter '%s' not found", linter)
            return True, f"Linter '{linter}' not installed"
            
        except Exception as e:
            logger.error("Error running linter '%s': %s", linter, str(e))
            return False, f"Error running linter: {str(e)}"
