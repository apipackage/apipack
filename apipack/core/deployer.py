"""
Package Deployer for APIpack.

This module provides the PackageDeployer class which is responsible for
deploying generated API packages to various targets (local, Docker, cloud, etc.).
"""
import logging
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import docker
from docker.errors import DockerException

logger = logging.getLogger(__name__)

class PackageDeployer:
    """Handles deployment of generated API packages to various targets."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the package deployer.
        
        Args:
            config: Configuration dictionary for the deployer.
        """
        self.config = config or {}
        self.docker_client = None
        self._setup_docker()
    
    def _setup_docker(self) -> None:
        """Set up Docker client if available."""
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()  # Test the connection
            logger.debug("Docker client initialized successfully")
        except DockerException as e:
            logger.warning("Docker not available: %s", str(e))
            self.docker_client = None
    
    def deploy(
        self,
        package_path: Union[str, Path],
        target: str = "local",
        **kwargs
    ) -> Dict[str, Any]:
        """Deploy a package to the specified target.
        
        Args:
            package_path: Path to the package directory or archive.
            target: Deployment target ('local', 'docker', 'kubernetes', 'aws_lambda', etc.).
            **kwargs: Additional target-specific deployment options.
            
        Returns:
            Dictionary with deployment results and metadata.
        """
        package_path = Path(package_path)
        if not package_path.exists():
            raise FileNotFoundError(f"Package not found: {package_path}")
        
        # Dispatch to the appropriate deployment method
        deploy_method = getattr(self, f"deploy_to_{target}", None)
        if not callable(deploy_method):
            raise ValueError(f"Unsupported deployment target: {target}")
            
        return deploy_method(package_path, **kwargs)
    
    def deploy_to_local(
        self,
        package_path: Path,
        install: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Deploy a package locally.
        
        Args:
            package_path: Path to the package directory.
            install: Whether to install the package in development mode.
            **kwargs: Additional deployment options.
            
        Returns:
            Dictionary with deployment results.
        """
        results = {
            'success': True,
            'target': 'local',
            'installed': False,
            'message': 'Deployment completed successfully',
            'details': {}
        }
        
        try:
            if install:
                # Run pip install in development mode
                cmd = [sys.executable, '-m', 'pip', 'install', '-e', str(package_path)]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                results['installed'] = True
                results['details']['install_output'] = result.stdout
                logger.info("Package installed in development mode: %s", package_path)
            
            return results
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Local installation failed: {str(e)}\n{e.stderr}"
            logger.error(error_msg)
            results.update({
                'success': False,
                'message': 'Local installation failed',
                'error': error_msg,
                'details': {
                    'returncode': e.returncode,
                    'stdout': e.stdout,
                    'stderr': e.stderr
                }
            })
            return results
            
        except Exception as e:
            error_msg = f"Local deployment failed: {str(e)}"
            logger.exception(error_msg)
            results.update({
                'success': False,
                'message': 'Local deployment failed',
                'error': error_msg
            })
            return results
    
    def deploy_to_docker(
        self,
        package_path: Path,
        tag: str = "apipack/deployed",
        build_args: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Deploy a package as a Docker container.
        
        Args:
            package_path: Path to the package directory.
            tag: Docker image tag.
            build_args: Additional build arguments for Docker.
            **kwargs: Additional deployment options.
            
        Returns:
            Dictionary with deployment results.
        """
        results = {
            'success': False,
            'target': 'docker',
            'built': False,
            'pushed': False,
            'message': '',
            'details': {}
        }
        
        if not self.docker_client:
            error_msg = "Docker is not available. Make sure Docker is installed and running."
            logger.error(error_msg)
            results.update({
                'message': error_msg,
                'error': 'Docker not available'
            })
            return results
            
        try:
            # Check if we have a Dockerfile or need to generate one
            dockerfile = package_path / 'Dockerfile'
            if not dockerfile.exists():
                # Generate a simple Dockerfile if none exists
                self._generate_dockerfile(package_path, **kwargs)
            
            # Build the Docker image
            logger.info("Building Docker image: %s", tag)
            build_result = self.docker_client.images.build(
                path=str(package_path),
                tag=tag,
                buildargs=build_args or {},
                **kwargs.get('build_kwargs', {})
            )
            
            image, build_logs = build_result
            results['built'] = True
            results['details']['image_id'] = image.id
            results['details']['build_logs'] = list(build_logs)
            
            # Run the container if requested
            if kwargs.get('run_container', True):
                container = self.docker_client.containers.run(
                    image=tag,
                    detach=True,
                    ports=kwargs.get('ports'),
                    environment=kwargs.get('environment'),
                    **kwargs.get('run_kwargs', {})
                )
                results['details']['container_id'] = container.id
                logger.info("Started container: %s", container.id)
            
            # Push to registry if credentials are provided
            if kwargs.get('push_to_registry'):
                registry = kwargs.get('registry', 'docker.io')
                username = kwargs.get('username')
                password = kwargs.get('password')
                
                if username and password:
                    self.docker_client.login(
                        username=username,
                        password=password,
                        registry=registry
                    )
                    
                    # Tag for registry
                    registry_tag = f"{registry}/{tag}" if registry != 'docker.io' else tag
                    image.tag(registry_tag)
                    
                    # Push the image
                    push_logs = self.docker_client.images.push(
                        repository=registry_tag,
                        auth_config={"username": username, "password": password}
                    )
                    results['pushed'] = True
                    results['details']['push_logs'] = push_logs
                    logger.info("Pushed image to registry: %s", registry_tag)
            
            results.update({
                'success': True,
                'message': 'Docker deployment completed successfully',
                'image': tag
            })
            return results
            
        except DockerException as e:
            error_msg = f"Docker deployment failed: {str(e)}"
            logger.exception(error_msg)
            results.update({
                'message': 'Docker deployment failed',
                'error': str(e)
            })
            return results
            
        except Exception as e:
            error_msg = f"Unexpected error during Docker deployment: {str(e)}"
            logger.exception(error_msg)
            results.update({
                'message': 'Unexpected error during Docker deployment',
                'error': str(e)
            })
            return results
    
    def _generate_dockerfile(self, package_path: Path, **kwargs) -> None:
        """Generate a basic Dockerfile if one doesn't exist.
        
        Args:
            package_path: Path to the package directory.
            **kwargs: Additional options for Dockerfile generation.
        """
        dockerfile_path = package_path / 'Dockerfile'
        python_version = kwargs.get('python_version', '3.9')
        
        dockerfile_content = f"""# Generated by APIpack
FROM python:{python_version}-slim

WORKDIR /app

# Install system dependencies if needed
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     <your-packages-here> && \
#     rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Install the package in development mode
RUN pip install -e .

# Expose the API port
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "your_package.main"]
"""
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        logger.info("Generated Dockerfile at %s", dockerfile_path)
    
    def deploy_to_kubernetes(
        self,
        package_path: Path,
        kubeconfig: Optional[str] = None,
        namespace: str = "default",
        **kwargs
    ) -> Dict[str, Any]:
        """Deploy a package to a Kubernetes cluster.
        
        Args:
            package_path: Path to the package directory or Kubernetes manifests.
            kubeconfig: Path to kubeconfig file.
            namespace: Kubernetes namespace to deploy to.
            **kwargs: Additional deployment options.
            
        Returns:
            Dictionary with deployment results.
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the Kubernetes Python client
        # or shell out to kubectl to apply the manifests
        return {
            'success': False,
            'target': 'kubernetes',
            'message': 'Kubernetes deployment is not yet implemented',
            'error': 'Not implemented'
        }
    
    def deploy_to_aws_lambda(
        self,
        package_path: Path,
        function_name: str,
        role_arn: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Deploy a package as an AWS Lambda function.
        
        Args:
            package_path: Path to the package directory.
            function_name: Name of the Lambda function.
            role_arn: IAM role ARN for the Lambda function.
            **kwargs: Additional deployment options.
            
        Returns:
            Dictionary with deployment results.
        """
        # This is a placeholder implementation
        # In a real implementation, you would use boto3 to create/update
        # the Lambda function and its configuration
        return {
            'success': False,
            'target': 'aws_lambda',
            'message': 'AWS Lambda deployment is not yet implemented',
            'error': 'Not implemented'
        }
    
    def create_package_archive(
        self,
        package_path: Path,
        output_dir: Optional[Path] = None,
        format: str = "tar.gz"
    ) -> Path:
        """Create an archive of the package for distribution.
        
        Args:
            package_path: Path to the package directory.
            output_dir: Directory to save the archive. Defaults to a temp directory.
            format: Archive format ('tar.gz', 'zip').
            
        Returns:
            Path to the created archive.
        """
        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp())
            
        output_dir.mkdir(parents=True, exist_ok=True)
        package_name = package_path.name
        archive_path = output_dir / f"{package_name}.{format}"
        
        if format == 'tar.gz':
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(package_path, arcname=package_name)
        elif format == 'zip':
            import zipfile
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in package_path.rglob('*'):
                    arcname = file.relative_to(package_path.parent)
                    zipf.write(file, arcname)
        else:
            raise ValueError(f"Unsupported archive format: {format}")
            
        logger.info("Created package archive: %s", archive_path)
        return archive_path

# Helper function to get a deployer instance
def get_deployer(config: Optional[Dict[str, Any]] = None) -> PackageDeployer:
    """Get a configured PackageDeployer instance.
    
    Args:
        config: Optional configuration dictionary.
        
    Returns:
        A configured PackageDeployer instance.
    """
    return PackageDeployer(config=config)
