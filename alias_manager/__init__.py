"""
Python Script Alias Manager Package
Creates and manages aliases for Python scripts that can be run from anywhere in PATH.
"""

from .core import PythonAliasManager
from .config import ConfigManager
from .venv_detector import VenvDetector
from .script_generator import ScriptGenerator
from .dependency_manager import DependencyManager
from .environment_setup import EnvironmentSetup

__version__ = "1.0.0"
__all__ = [
    "PythonAliasManager",
    "ConfigManager", 
    "VenvDetector",
    "ScriptGenerator",
    "DependencyManager",
    "EnvironmentSetup"
]
