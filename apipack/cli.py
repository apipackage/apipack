"""
APIpack CLI

Command-line interface for the APIpack package generator.
Provides commands for generating, building, and deploying API packages.
"""

import logging
import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

import click
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax

from . import APIPackEngine, __version__
from .config.settings import get_settings
from .core.parser import FunctionSpecParser
from .utils.file_utils import ensure_directory

# Setup rich console
console = Console()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.pass_context
def main(ctx, verbose, config):
    """
    APIpack - Automated API Package Generator

    Generate complete API packages from function specifications using LLM integration.
    """
    # Setup logging level
    if verbose:
        logging.getLogger('apipack').setLevel(logging.DEBUG)

    # Store config in context
    ctx.ensure_object(dict)
    ctx.obj['config_file'] = config
    ctx.obj['verbose'] = verbose


@main.command()
@click.argument('spec_file', type=click.Path(exists=True))
@click.option('--output', '-o', default='./generated', help='Output directory')
@click.option('--language', '-l', default='python', help='Programming language')
@click.option('--interfaces', '-i', multiple=True, help='Interface types (rest, grpc, cli, etc.)')
@click.option('--dry-run', is_flag=True, help='Show what would be generated without creating files')
@click.pass_context
def generate(ctx, spec_file, output, language, interfaces, dry_run):
    """
    Generate API package from specification file.

    SPEC_FILE: Path to function specification file (JSON or YAML)
    """
    try:
        console.print(Panel(
            f"[bold blue]APIpack Generator[/bold blue]\n"
            f"Specification: {spec_file}\n"
            f"Output: {output}\n"
            f"Language: {language}\n"
            f"Interfaces: {', '.join(interfaces) if interfaces else 'auto-detect'}"
        ))

        # Load specification
        spec_path = Path(spec_file)
        if spec_path.suffix.lower() == '.json':
            with open(spec_path) as f:
                spec_data = json.load(f)
        else:
            with open(spec_path) as f:
                spec_data = yaml.safe_load(f)

        # Parse function specifications
        if isinstance(spec_data, dict) and 'functions' in spec_data:
            function_specs = spec_data['functions']
            project_config = {k: v for k, v in spec_data.items() if k != 'functions'}
        elif isinstance(spec_data, list):
            function_specs = spec_data
            project_config = {}
        else:
            function_specs = [spec_data]
            project_config = {}

        # Auto-detect interfaces if not specified
        if not interfaces:
            interfaces = _auto_detect_interfaces(function_specs)

        if dry_run:
            _show_dry_run_preview(function_specs, interfaces, language, output)
            return

        # Initialize engine
        engine = APIPackEngine(config=ctx.obj.get('config'))

        # Generate package
        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
        ) as progress:
            task = progress.add_task("Generating package...", total=None)

            result = engine.generate_package(
                function_specs=function_specs,
                interfaces=list(interfaces),
                language=language,
                output_dir=output,
                project_config=project_config
            )

        # Display results
        if result.success:
            console.print(f"[green]✓[/green] Package generated successfully!")
            console.print(f"[blue]Output directory:[/blue] {result.output_dir}")
            console.print(f"[blue]Generated files:[/blue] {len(result.generated_files)}")

            if ctx.obj.get('verbose'):
                _show_generated_files(result.generated_files)
        else:
            console.print(f"[red]✗[/red] Package generation failed!")
            for error in result.errors:
                console.print(f"[red]Error:[/red] {error}")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@main.command()
@click.argument('package_dir', type=click.Path(exists=True))
@click.option('--type', 'deploy_type', default='docker', help='Deployment type (docker, kubernetes, etc.)')
@click.option('--push', is_flag=True, help='Push to registry after building')
@click.option('--tag', help='Image tag')
@click.pass_context
def build(ctx, package_dir, deploy_type, push, tag):
    """
    Build generated package for deployment.

    PACKAGE_DIR: Directory containing generated package
    """
    try:
        console.print(Panel(
            f"[bold blue]Building Package[/bold blue]\n"
            f"Package: {package_dir}\n"
            f"Type: {deploy_type}\n"
            f"Push: {'Yes' if push else 'No'}"
        ))

        engine = APIPackEngine()

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
        ) as progress:
            task = progress.add_task("Building package...", total=None)

            result = engine.deploy_package(
                package_dir=package_dir,
                deployment_type=deploy_type,
                push=push,
                tag=tag
            )

        if result.get('success'):
            console.print(f"[green]✓[/green] Package built successfully!")
            if 'image' in result:
                console.print(f"[blue]Image:[/blue] {result['image']}")
        else:
            console.print(f"[red]✗[/red] Build failed: {result.get('error')}")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@main.command()
@click.argument('spec_file', type=click.Path(exists=True))
@click.pass_context
def validate(ctx, spec_file):
    """
    Validate function specification file.

    SPEC_FILE: Path to specification file to validate
    """
    try:
        console.print(f"[blue]Validating:[/blue] {spec_file}")

        # Load and parse specification
        parser = FunctionSpecParser()

        spec_path = Path(spec_file)
        if spec_path.suffix.lower() == '.json':
            with open(spec_path) as f:
                spec_data = json.load(f)
        else:
            with open(spec_path) as f:
                spec_data = yaml.safe_load(f)

        # Validate
        if isinstance(spec_data, list):
            all_valid = True
            for i, spec in enumerate(spec_data):
                result = parser.validate_spec_dict(spec)
                if result.success:
                    console.print(f"[green]✓[/green] Function {i + 1}: {spec.get('name', 'unnamed')}")
                else:
                    console.print(f"[red]✗[/red] Function {i + 1}: {spec.get('name', 'unnamed')}")
                    for error in result.errors:
                        console.print(f"  [red]Error:[/red] {error}")
                    all_valid = False
        else:
            result = parser.validate_spec_dict(spec_data)
            if result.success:
                console.print(f"[green]✓[/green] Specification is valid")
            else:
                console.print(f"[red]✗[/red] Specification is invalid")
                for error in result.errors:
                    console.print(f"  [red]Error:[/red] {error}")
                all_valid = False

        if not all_valid:
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@main.command()
def templates():
    """List available templates."""
    try:
        engine = APIPackEngine()
        templates_dict = engine.list_available_templates()

        console.print("[bold blue]Available Templates[/bold blue]\n")

        for category, template_list in templates_dict.items():
            table = Table(title=f"{category.title()} Templates")
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="green")

            for template_name in template_list:
                # Get template info (simplified for now)
                table.add_row(template_name, "Template description")

            console.print(table)
            console.print()

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@main.command()
@click.option('--name', prompt='Function name', help='Name of the function')
@click.option('--description', help='Function description')
@click.option('--output', '-o', default='function_spec.yml', help='Output file path')
def init(name, description, output):
    """Initialize a new function specification."""
    try:
        parser = FunctionSpecParser()
        spec = parser.generate_example_spec(name)

        if description:
            spec['description'] = description

        output_path = Path(output)
        with open(output_path, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, indent=2)

        console.print(f"[green]✓[/green] Specification created: {output_path}")
        console.print(f"[blue]Edit the file to customize your function specification[/blue]")

        # Show the generated spec
        if console.is_terminal:
            spec_content = output_path.read_text()
            syntax = Syntax(spec_content, "yaml", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="Generated Specification"))

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@main.command()
def config():
    """Show current configuration."""
    try:
        settings = get_settings()

        console.print("[bold blue]Current Configuration[/bold blue]\n")

        config_data = {
            "LLM Settings": {
                "Provider": settings.llm.provider,
                "Model": settings.llm.model,
                "Temperature": settings.llm.temperature,
                "Max Tokens": settings.llm.max_tokens
            },
            "Template Settings": {
                "Auto Discover": settings.templates.auto_discover,
                "Cache Enabled": settings.templates.cache_enabled,
                "Validation Level": settings.templates.validation_level
            },
            "Output Settings": {
                "Format": settings.output.format,
                "Include Tests": settings.output.include_tests,
                "Include Docs": settings.output.include_docs
            }
        }

        for section, values in config_data.items():
            table = Table(title=section)
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")

            for key, value in values.items():
                table.add_row(key, str(value))

            console.print(table)
            console.print()

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@main.command()
def health():
    """Check health of APIpack components."""
    try:
        console.print("[bold blue]Health Check[/bold blue]\n")

        engine = APIPackEngine()

        # Check LLM connection
        with console.status("Checking LLM connection..."):
            llm_health = engine.llm_client.health_check()

        if llm_health.get('status') == 'healthy':
            console.print(f"[green]✓[/green] LLM: {llm_health.get('model')} is healthy")
        else:
            console.print(f"[red]✗[/red] LLM: {llm_health.get('error', 'Unknown error')}")

        # Check templates
        templates = engine.list_available_templates()
        template_count = sum(len(t) for t in templates.values())
        console.print(f"[green]✓[/green] Templates: {template_count} templates available")

        # Check interfaces
        interfaces = engine.list_available_interfaces()
        console.print(f"[green]✓[/green] Interfaces: {', '.join(interfaces)}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


def _auto_detect_interfaces(function_specs: List[Dict[str, Any]]) -> List[str]:
    """Auto-detect interfaces based on function specifications."""
    interfaces = set()

    for spec in function_specs:
        # Check for explicit interface configuration
        if 'rest_config' in spec or 'rest' in spec:
            interfaces.add('rest')
        if 'grpc_config' in spec or 'grpc' in spec:
            interfaces.add('grpc')
        if 'cli_config' in spec or 'cli' in spec:
            interfaces.add('cli')

        # Default to REST if no interfaces specified
        if not interfaces:
            interfaces.add('rest')

    return list(interfaces)


def _show_dry_run_preview(function_specs, interfaces, language, output):
    """Show preview of what would be generated."""
    console.print("[bold yellow]Dry Run Preview[/bold yellow]\n")

    console.print(f"[blue]Output Directory:[/blue] {output}")
    console.print(f"[blue]Language:[/blue] {language}")
    console.print(f"[blue]Interfaces:[/blue] {', '.join(interfaces)}")
    console.print()

    console.print("[blue]Functions to generate:[/blue]")
    for spec in function_specs:
        console.print(f"  • {spec.get('name', 'unnamed')}: {spec.get('description', 'No description')}")

    console.print()
    console.print("[blue]Files that would be generated:[/blue]")

    # Estimate files that would be generated
    base_files = [
        "requirements.txt" if language == "python" else "package.json",
        "Dockerfile",
        "README.md",
        ".gitignore"
    ]

    for interface in interfaces:
        base_files.extend([
            f"{interface}/server.{_get_extension(language)}",
            f"{interface}/client.{_get_extension(language)}"
        ])

    for func in function_specs:
        base_files.append(f"functions/{func.get('name', 'unnamed')}.{_get_extension(language)}")

    for file_path in sorted(base_files):
        console.print(f"  • {file_path}")


def _show_generated_files(files: List[Path]):
    """Show list of generated files."""
    console.print("\n[blue]Generated Files:[/blue]")
    for file_path in sorted(files):
        console.print(f"  • {file_path}")


def _get_extension(language: str) -> str:
    """Get file extension for language."""
    extensions = {
        "python": "py",
        "javascript": "js",
        "typescript": "ts",
        "go": "go",
        "rust": "rs",
        "java": "java"
    }
    return extensions.get(language, "txt")


if __name__ == '__main__':
    main()