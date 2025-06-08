"""
Basic example of using APIpack to generate a simple API package.
"""
import os
import sys
import asyncio
import yaml
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from apipack.core.engine import APIPackEngine

async def main():
    """Generate a basic API package."""
    # Load the configuration
    config_path = Path(__file__).parent / "config.yml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize the APIpack engine
    engine = APIPackEngine()
    
    # Output directory for the generated package
    output_dir = Path("generated/basic-api")
    
    print(f"Generating API package from {config_path}...")
    print(f"Language: {config['language']}")
    print(f"Interfaces: {', '.join(config['interfaces'])}")
    print(f"Functions: {[f['name'] for f in config['functions']]}")
    
    # Generate the package
    result = await engine.generate_package_async(
        function_specs=config['functions'],
        interfaces=config['interfaces'],
        language=config['language'],
        output_dir=output_dir,
        project_name=config['name'],
        version=config['version'],
        description=config['description']
    )
    
    if result.success:
        print(f"\n✅ Successfully generated package at: {result.output_dir}")
        print(f"Generated files: {len(result.generated_files)}")
        
        if result.warnings:
            print("\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        print("\nNext steps:")
        print(f"1. cd {result.output_dir}")
        print("2. pip install -e .  # Install in development mode")
        print("3. python -m basic_api.rest.server  # Start the REST API")
        print("4. python -m basic_api.cli --help    # Use the CLI")
    else:
        print("\n❌ Failed to generate package:")
        for error in result.errors:
            print(f"  - {error}")

if __name__ == "__main__":
    asyncio.run(main())
