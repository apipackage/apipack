"""
Plugin System for APIpack.

This module provides the base plugin system for extending APIpack functionality.
It includes the BasePlugin abstract base class that all plugins must implement,
and the PluginManager class for managing plugin lifecycle and discovery.
"""
import importlib
import inspect
import logging
import pkgutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast

from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Type variable for the plugin type
T = TypeVar("T", bound="BasePlugin")

class PluginConfig(BaseModel):
    """Base configuration model for plugins."""
    enabled: bool = True
    priority: int = 100  # Lower numbers are higher priority
    
class BasePlugin(ABC):
    """Abstract base class for all APIpack plugins.
    
    Plugins can hook into various stages of the API package generation process
    to extend or modify functionality.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the plugin with optional configuration.
        
        Args:
            config: Plugin configuration dictionary.
        """
        self.config = self.get_config_class()(**(config or {}))
        self._initialized = False
    
    @classmethod
    def get_name(cls) -> str:
        """Get the plugin's name.
        
        By default, returns the class name in snake_case.
        """
        name = cls.__name__
        if name.endswith("Plugin"):
            name = name[:-6]  # Remove 'Plugin' suffix if present
        return "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip("_")
    
    @classmethod
    def get_config_class(cls) -> Type[PluginConfig]:
        """Get the configuration class for this plugin.
        
        Plugins can override this to provide a custom configuration class.
        """
        return PluginConfig
    
    def initialize(self) -> None:
        """Initialize the plugin.
        
        This is called when the plugin is first loaded. Plugins should override
        this method to perform any necessary setup.
        """
        if not self._initialized:
            logger.debug("Initializing plugin: %s", self.get_name())
            self._initialized = True
    
    def cleanup(self) -> None:
        """Clean up any resources used by the plugin.
        
        This is called when the plugin is unloaded or when the application
        is shutting down.
        """
        if self._initialized:
            logger.debug("Cleaning up plugin: %s", self.get_name())
            self._initialized = False
    
    # Plugin hooks - subclasses should override these as needed
    
    def on_package_generate_start(self, spec: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Called when package generation starts.
        
        Args:
            spec: The package specification.
            context: The generation context.
        """
        pass
    
    def on_package_generate_end(self, spec: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Called when package generation completes successfully.
        
        Args:
            spec: The package specification.
            context: The generation context.
        """
        pass
    
    def on_package_generate_error(self, error: Exception, spec: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Called when package generation fails.
        
        Args:
            error: The exception that was raised.
            spec: The package specification.
            context: The generation context.
        """
        pass
    
    def on_file_generate(self, file_path: Path, content: str, context: Dict[str, Any]) -> Optional[str]:
        """Called when a file is about to be generated.
        
        Args:
            file_path: The path where the file will be written.
            content: The current content of the file.
            context: The generation context.
            
        Returns:
            The modified content, or None to use the original content.
        """
        return None
    
    def on_file_written(self, file_path: Path, context: Dict[str, Any]) -> None:
        """Called after a file has been written.
        
        Args:
            file_path: The path where the file was written.
            context: The generation context.
        """
        pass


class PluginManager:
    """Manages the loading and lifecycle of plugins."""
    
    def __init__(self, plugin_dirs: Optional[List[Union[str, Path]]] = None):
        """Initialize the plugin manager.
        
        Args:
            plugin_dirs: List of directories to search for plugins.
        """
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_dirs = [Path(d) for d in (plugin_dirs or [])]
        self._discovered_plugins: Dict[str, Type[BasePlugin]] = {}
    
    def discover_plugins(self, package_paths: Optional[List[str]] = None) -> None:
        """Discover plugins in the specified packages.
        
        Args:
            package_paths: List of package paths to search for plugins.
        """
        if package_paths is None:
            package_paths = ["apipack.plugins"]
            
        for package_path in package_paths:
            try:
                package = importlib.import_module(package_path)
                self._discover_plugins_in_package(package)
            except ImportError as e:
                logger.warning("Failed to import package %s: %s", package_path, e)
    
    def _discover_plugins_in_package(self, package: Any) -> None:
        """Discover plugins in a package.
        
        Args:
            package: The package to search for plugins.
        """
        try:
            package_path = Path(package.__file__).parent if hasattr(package, '__file__') else None
            
            # Skip if this is a namespace package without a __file__
            if package_path is None:
                return
                
            for finder, name, _ in pkgutil.iter_modules([str(package_path)]):
                try:
                    # Skip if this is the base_plugin module
                    if name == 'base_plugin':
                        continue
                        
                    full_name = f"{package.__name__}.{name}"
                    module = importlib.import_module(full_name)
                    
                    # Find all plugin classes in the module
                    for _, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, BasePlugin) and 
                                obj is not BasePlugin and 
                                not inspect.isabstract(obj)):
                            plugin_name = obj.get_name()
                            if plugin_name in self._discovered_plugins:
                                logger.warning(
                                    "Plugin %s already registered, skipping %s",
                                    plugin_name, full_name
                                )
                            else:
                                self._discovered_plugins[plugin_name] = obj
                                logger.debug("Discovered plugin: %s", plugin_name)
                                    
                except Exception as e:
                    logger.error("Error loading plugin %s: %s", name, e, exc_info=True)
                    
        except Exception as e:
            logger.error("Error discovering plugins in package %s: %s", package, e, exc_info=True)
    
    def load_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> Optional[BasePlugin]:
        """Load a plugin by name.
        
        Args:
            plugin_name: Name of the plugin to load.
            config: Configuration for the plugin.
            
        Returns:
            The loaded plugin instance, or None if loading failed.
        """
        if plugin_name in self.plugins:
            return self.plugins[plugin_name]
            
        plugin_class = self._discovered_plugins.get(plugin_name)
        if not plugin_class:
            logger.error("Plugin not found: %s", plugin_name)
            return None
            
        try:
            plugin = plugin_class(config or {})
            plugin.initialize()
            self.plugins[plugin_name] = plugin
            logger.info("Loaded plugin: %s", plugin_name)
            return plugin
        except Exception as e:
            logger.error("Error loading plugin %s: %s", plugin_name, e, exc_info=True)
            return None
    
    def load_plugins(self, plugin_configs: Dict[str, Dict[str, Any]]) -> Dict[str, BasePlugin]:
        """Load multiple plugins from a configuration dictionary.
        
        Args:
            plugin_configs: Dictionary mapping plugin names to their configurations.
                           If the config is None or has 'enabled: false', the plugin is skipped.
                           
        Returns:
            Dictionary of loaded plugin instances.
        """
        loaded = {}
        
        for plugin_name, config in plugin_configs.items():
            if config is None or config.get('enabled', True):
                plugin = self.load_plugin(plugin_name, config)
                if plugin:
                    loaded[plugin_name] = plugin
                    
        # Sort plugins by priority (lower number = higher priority)
        return dict(sorted(
            loaded.items(),
            key=lambda x: x[1].config.priority if hasattr(x[1].config, 'priority') else 100
        ))
    
    def unload_plugin(self, plugin_name: str) -> None:
        """Unload a plugin.
        
        Args:
            plugin_name: Name of the plugin to unload.
        """
        plugin = self.plugins.pop(plugin_name, None)
        if plugin:
            try:
                plugin.cleanup()
                logger.info("Unloaded plugin: %s", plugin_name)
            except Exception as e:
                logger.error("Error unloading plugin %s: %s", plugin_name, e, exc_info=True)
    
    def unload_all(self) -> None:
        """Unload all plugins."""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a loaded plugin by name.
        
        Args:
            plugin_name: Name of the plugin to get.
            
        Returns:
            The plugin instance, or None if not found.
        """
        return self.plugins.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: Type[T]) -> List[T]:
        """Get all loaded plugins of a specific type.
        
        Args:
            plugin_type: The type of plugins to get.
            
        Returns:
            List of plugin instances of the specified type.
        """
        return [
            cast(T, plugin) 
            for plugin in self.plugins.values() 
            if isinstance(plugin, plugin_type)
        ]
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - unload all plugins."""
        self.unload_all()
        return False
    
    def __del__(self):
        """Destructor - ensure all plugins are properly cleaned up."""
        self.unload_all()


def get_plugin_manager() -> PluginManager:
    """Get a configured plugin manager instance.
    
    Returns:
        A configured PluginManager instance.
    """
    return PluginManager()
