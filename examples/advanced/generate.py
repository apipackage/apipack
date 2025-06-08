"""
Advanced example of using APIpack to generate a complete TODO API with multiple interfaces.
"""
import os
import sys
import asyncio
import yaml
from pathlib import Path
from typing import Dict, List, Any

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from apipack.core.engine import APIPackEngine
from apipack.templates.registry import TemplateRegistry

class AdvancedExampleGenerator:
    """Generator for the advanced TODO API example."""
    
    def __init__(self, config_path: str):
        """Initialize with path to config file."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.engine = APIPackEngine()
        
        # Configure template registry with custom templates
        self.template_registry = TemplateRegistry()
        self._register_custom_templates()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load and validate the configuration."""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _register_custom_templates(self):
        """Register any custom templates for this example."""
        # In a real scenario, this would load custom templates
        # from a templates directory
        pass
    
    def _get_function_specs(self) -> List[Dict[str, Any]]:
        """Extract function specifications from config."""
        return self.config.get('functions', [])
    
    def _get_interfaces(self) -> List[str]:
        """Get list of interfaces to generate."""
        return [i['type'] for i in self.config.get('interfaces', [])]
    
    def _get_target_languages(self) -> List[str]:
        """Get list of target languages."""
        return [lang['name'] for lang in self.config.get('languages', [])]
    
    async def generate(self, output_dir: str = "generated/advanced-todo"):
        """Generate the API package."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print("🚀 Generating Advanced TODO API")
        print("=" * 50)
        print(f"Project: {self.config['name']} v{self.config['version']}")
        print(f"Description: {self.config['description']}")
        print(f"Languages: {', '.join(self._get_target_languages())}")
        print(f"Interfaces: {', '.join(self._get_interfaces())}")
        print("=" * 50)
        
        # Generate for each target language
        for language in self._get_target_languages():
            print(f"\n🌍 Generating {language.upper()} implementation...")
            
            # Configure language-specific settings
            language_config = self._get_language_config(language)
            
            # Generate the package
            result = await self.engine.generate_package_async(
                function_specs=self._get_function_specs(),
                interfaces=self._get_interfaces(),
                language=language,
                output_dir=output_path / language,
                project_name=self.config['name'].replace('-', '_'),
                version=self.config['version'],
                description=self.config['description'],
                author=self.config.get('author', ''),
                license=self.config.get('license', ''),
                **language_config
            )
            
            self._print_generation_result(result, language)
    
    def _get_language_config(self, language: str) -> Dict[str, Any]:
        """Get language-specific configuration."""
        # In a real implementation, this would return framework versions,
        # build tools, and other language-specific settings
        return {
            'python': {
                'package_manager': 'poetry',
                'test_framework': 'pytest',
                'async_framework': 'asyncio',
            },
            'javascript': {
                'package_manager': 'npm',
                'test_framework': 'jest',
                'runtime': 'node',
            },
            'go': {
                'module_path': f'github.com/username/{self.config["name"]}',
                'test_framework': 'testing',
            },
            'rust': {
                'edition': '2021',
                'test_framework': 'cargo_test',
            },
        }.get(language.lower(), {})
    
    def _print_generation_result(self, result: Any, language: str):
        """Print the result of package generation."""
        if result.success:
            print(f"✅ Successfully generated {language.upper()} package")
            print(f"   Location: {result.output_dir}")
            print(f"   Files generated: {len(result.generated_files)}")
            
            if result.warnings:
                print("\n⚠️  Warnings:")
                for warning in result.warnings:
                    print(f"   - {warning}")
        else:
            print(f"❌ Failed to generate {language.upper()} package")
            for error in result.errors:
                print(f"   - {error}")


async def main():
    """Run the advanced example generator."""
    # Path to the example configuration
    config_path = Path(__file__).parent / "config.yml"
    
    # Create and run the generator
    generator = AdvancedExampleGenerator(config_path)
    await generator.generate()
    
    print("\n🎉 Generation complete!")
    print("Next steps:")
    print("1. Explore the generated code in the 'generated/advanced-todo' directory")
    print("2. Follow the README in each language directory to run the API")
    print("3. Try out the different interfaces (REST, gRPC, GraphQL, WebSocket, CLI)")


if __name__ == "__main__":
    asyncio.run(main())
