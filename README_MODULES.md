# Python Alias Manager - Modular Architecture

The Python Alias Manager has been refactored into a modular architecture for better maintainability and organization.

## Project Structure

```
PythonAliasManager/
├── alias_manager/                 # Main package directory
│   ├── __init__.py               # Package initialization with exports
│   ├── cli.py                    # Command-line interface and argument parsing
│   ├── config.py                 # Configuration management and PATH setup
│   ├── core.py                   # Main PythonAliasManager class
│   ├── dependency_manager.py     # Dependency parsing and installation
│   ├── environment_setup.py      # Virtual environment and conda setup
│   ├── script_generator.py       # Batch/shell script generation
│   └── venv_detector.py          # Virtual environment detection
├── python_alias_manager.py       # Main entry point (modular)
├── python_alias_manager_original.py  # Backup of original monolithic file
└── README_MODULES.md             # This file
```

## Module Responsibilities

### 1. `config.py` - ConfigManager

- Manages configuration storage (aliases.json)
- Handles directory setup (.python_aliases, bin/)
- Provides PATH setup instructions
- Loads and saves alias configurations

### 2. `venv_detector.py` - VenvDetector

- Detects virtual environments (venv, conda)
- Parses conda environment files
- Gets Python executable paths
- Checks conda availability

### 3. `script_generator.py` - ScriptGenerator

- Creates Windows batch files (.bat)
- Creates Unix shell scripts
- Handles cross-platform path conversion
- Manages virtual environment activation scripts

### 4. `dependency_manager.py` - DependencyManager

- Parses requirements.txt files
- Parses pyproject.toml files
- Parses conda environment.yml files
- Installs missing dependencies
- Checks installed packages

### 5. `environment_setup.py` - EnvironmentSetup

- Creates virtual environments
- Creates conda environments
- Auto-setup functionality
- Environment validation

### 6. `core.py` - PythonAliasManager

- Main orchestrator class
- Coordinates all other modules
- Implements high-level alias operations
- Manages alias lifecycle (add, remove, list, update)

### 7. `cli.py` - Command Line Interface

- Argument parsing with argparse
- Command routing
- User interface logic
- Help and usage information

## Benefits of Modular Architecture

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Easier Testing**: Individual modules can be tested in isolation
3. **Better Maintainability**: Changes to one area don't affect others
4. **Improved Readability**: Smaller, focused files are easier to understand
5. **Extensibility**: New features can be added without modifying core logic
6. **Reusability**: Modules can be imported and used independently

## Usage

The main interface remains the same - use `python_alias_manager.py` as before:

```bash
# All commands work exactly as before
python python_alias_manager.py add myapp ~/scripts/my_app.py
python python_alias_manager.py list
python python_alias_manager.py deps myapp --install
```

## Importing Modules

You can also import and use individual modules in your own scripts:

```python
from alias_manager import PythonAliasManager, VenvDetector, DependencyManager

# Use individual components
detector = VenvDetector()
venv_info = detector.detect_venv("/path/to/script.py")

# Or use the main manager
manager = PythonAliasManager()
manager.add_alias("myapp", "/path/to/script.py")
```

## Migration Notes

- The original monolithic file is preserved as `python_alias_manager_original.py`
- All functionality has been preserved and should work identically
- Configuration files and existing aliases are fully compatible
- No changes to user workflow or commands
