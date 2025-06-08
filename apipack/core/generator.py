"""
Code Generator for APIpack.

This module provides the CodeGenerator class which is responsible for generating
code based on templates and function specifications.
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import os
import shutil
import logging
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

logger = logging.getLogger(__name__)

class CodeGenerator:
    """Generates code based on templates and function specifications."""
    
    def __init__(self, template_dirs: List[str] = None):
        """Initialize the code generator.
        
        Args:
            template_dirs: List of directories to search for templates.
        """
        self.template_dirs = template_dirs or ["templates"]
        self.env = self._setup_environment()
    
    def _setup_environment(self):
        """Set up the Jinja2 environment with template loaders."""
        # Convert string paths to Path objects and ensure they exist
        template_paths = [Path(d) for d in self.template_dirs if Path(d).exists()]
        
        if not template_paths:
            logger.warning(
                "No template directories found in: %s. Using current directory.",
                ", ".join(self.template_dirs)
            )
            template_paths = [Path(".")]
            
        return Environment(
            loader=FileSystemLoader([str(p) for p in template_paths]),
            autoescape=True,
            keep_trailing_newline=True,
        )
    
    def generate_file(
        self,
        template_path: str,
        output_path: str,
        context: Dict[str, Any],
        overwrite: bool = False
    ) -> bool:
        """Generate a single file from a template.
        
        Args:
            template_path: Path to the template file.
            output_path: Path where the generated file should be saved.
            context: Dictionary of variables to pass to the template.
            overwrite: Whether to overwrite existing files.
            
        Returns:
            bool: True if file was generated, False otherwise.
        """
        output_path = Path(output_path)
        
        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists and handle overwrite
        if output_path.exists() and not overwrite:
            logger.debug("Skipping existing file: %s", output_path)
            return False
            
        try:
            template = self.env.get_template(template_path)
            rendered = template.render(**context)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rendered)
                
            logger.debug("Generated file: %s", output_path)
            return True
            
        except TemplateNotFound as e:
            logger.error("Template not found: %s", e)
            raise
        except Exception as e:
            logger.error("Error generating file %s: %s", output_path, str(e))
            raise
    
    def generate_directory(
        self,
        src_dir: str,
        dest_dir: str,
        context: Dict[str, Any],
        exclude: Optional[List[str]] = None,
        overwrite: bool = False
    ) -> int:
        """Generate a directory of files from templates.
        
        Args:
            src_dir: Source directory containing template files.
            dest_dir: Destination directory for generated files.
            context: Dictionary of variables to pass to templates.
            exclude: List of file patterns to exclude.
            overwrite: Whether to overwrite existing files.
            
        Returns:
            int: Number of files generated.
        """
        src_path = Path(src_dir)
        dest_path = Path(dest_dir)
        exclude = exclude or []
        generated = 0
        
        if not src_path.exists():
            logger.error("Source directory not found: %s", src_dir)
            return 0
            
        # Create destination directory if it doesn't exist
        dest_path.mkdir(parents=True, exist_ok=True)
        
        for item in src_path.rglob('*'):
            # Skip excluded files/directories
            if any(item.match(pattern) for pattern in exclude):
                continue
                
            rel_path = item.relative_to(src_path)
            dest_item = dest_path / rel_path
            
            if item.is_file():
                # For template files, render with context
                if item.suffix in ['.j2', '.jinja2']:
                    output_path = dest_item.with_suffix('')
                    if self.generate_file(
                        str(rel_path),
                        str(output_path),
                        context,
                        overwrite
                    ):
                        generated += 1
                else:
                    # For non-template files, just copy
                    if not dest_item.exists() or overwrite:
                        shutil.copy2(item, dest_item)
                        generated += 1
            
            elif item.is_dir() and not dest_item.exists():
                # Create subdirectories
                dest_item.mkdir(parents=True, exist_ok=True)
        
        return generated
    
    def generate_from_spec(
        self,
        spec: Dict[str, Any],
        output_dir: str,
        template_dir: Optional[str] = None,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """Generate code from a specification dictionary.
        
        Args:
            spec: Dictionary containing generation specifications.
            output_dir: Base directory for generated files.
            template_dir: Optional directory containing templates.
            overwrite: Whether to overwrite existing files.
            
        Returns:
            Dict with generation results and metadata.
        """
        results = {
            'success': True,
            'generated_files': [],
            'skipped_files': [],
            'errors': []
        }
        
        try:
            # Set up template directory
            if template_dir:
                self.template_dirs.insert(0, template_dir)
                self.env = self._setup_environment()
            
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Process each file in the spec
            for file_spec in spec.get('files', []):
                try:
                    template = file_spec['template']
                    output = file_spec['output']
                    file_context = {**spec.get('context', {}), **file_spec.get('context', {})}
                    
                    # Generate the file
                    output_file = output_path / output
                    if self.generate_file(template, str(output_file), file_context, overwrite):
                        results['generated_files'].append(str(output_file))
                    else:
                        results['skipped_files'].append(str(output_file))
                        
                except Exception as e:
                    error_msg = f"Error processing {file_spec.get('template', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            # Process each directory in the spec
            for dir_spec in spec.get('directories', []):
                try:
                    src = dir_spec['source']
                    dest = dir_spec.get('destination', '')
                    dir_context = {**spec.get('context', {}), **dir_spec.get('context', {})}
                    exclude = dir_spec.get('exclude', [])
                    
                    # Generate the directory
                    dest_path = output_path / dest
                    count = self.generate_directory(
                        src, str(dest_path), dir_context, exclude, overwrite
                    )
                    results['generated_files'].extend(
                        str(dest_path / f) for f in os.listdir(dest_path)
                    )
                    
                except Exception as e:
                    error_msg = f"Error processing directory {dir_spec.get('source', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            # Update success status if there were any errors
            if results['errors']:
                results['success'] = False
                
        except Exception as e:
            error_msg = f"Generation failed: {str(e)}"
            logger.exception(error_msg)
            results['success'] = False
            results['errors'].append(error_msg)
        
        return results
