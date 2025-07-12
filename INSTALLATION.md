# Installation Guide for Python Alias Manager

This guide covers all the different ways to install the Python Alias Manager, now updated for the new modular package structure.

## Quick Start

The easiest way to get started:

```bash
python install_simple.py
```

This will install the package and create the `pam` command.

## Installation Options

### 1. Simple Installation (Recommended)

**File:** `install_simple.py`

```bash
python install_simple.py
```

**What it does:**
- Installs the package using pip with `-e` (editable mode)
- Creates the `pam` command entry point
- Tests the installation automatically
- Works on all platforms

**Pros:**
- Simplest setup
- Proper Python package installation
- Automatic entry points
- Easy to uninstall with `pip uninstall pythonaliasmanager`

### 2. Package Installation

**File:** `install_package.py`

```bash
python install_package.py
```

**What it does:**
- Full package installation with pip
- Creates command-line scripts in `~/.python_aliases/scripts/`
- Offers automatic PATH setup
- Provides multiple command aliases

**Pros:**
- More robust PATH handling
- Creates both `pam.bat` and `pam` scripts
- Manual PATH configuration options

### 3. Legacy File-based Installation

**File:** `install_alias_manager.py`

```bash
python install_alias_manager.py
```

**What it does:**
- Copies files to `~/.python_aliases/manager/`
- Creates wrapper scripts for cross-platform compatibility
- Manual PATH setup required

**Pros:**
- No pip required
- Works with any Python installation
- Backward compatible

### 4. WSL Installation

**File:** `install_wsl.sh`

```bash
bash install_wsl.sh
```

**What it does:**
- WSL-specific installation
- Handles Windows/WSL path conversion
- Optimized for WSL filesystem performance
- Automatic PATH configuration for bash

**Pros:**
- Optimized for WSL environments
- Handles cross-platform paths
- Works with existing Windows aliases

### 5. Direct pip Installation

For developers:

```bash
pip install -e .
```

**What it does:**
- Installs in development mode
- Creates entry points automatically
- Allows live editing of the package

**Pros:**
- Standard Python development workflow
- Live code updates
- Easy debugging

## Entry Points

After installation, you can use the tool in several ways:

```bash
# Primary command (created by entry points)
pam --help

# Alternative command name
python-alias-manager --help

# Direct module execution
python -m alias_manager --help
python -m alias_manager.cli --help

# Legacy wrapper (file-based installations)
./pam --help  # or pam.bat on Windows
```

## Verification

Test your installation:

```bash
# Check if the command works
pam --help

# Check if the package is installed
python -c "import alias_manager; print('Package installed correctly')"

# List current aliases (should work even if empty)
pam list
```

## Troubleshooting

### Command not found: 'pam'

1. **Check your PATH:**
   ```bash
   echo $PATH  # Linux/macOS/WSL
   echo $env:PATH  # PowerShell
   ```

2. **Restart your terminal** - Entry points may need a fresh shell

3. **Check pip installation location:**
   ```bash
   pip show pythonaliasmanager
   ```

4. **Use alternative commands:**
   ```bash
   python -m alias_manager --help
   ```

### Module not found errors

1. **Reinstall the package:**
   ```bash
   pip uninstall pythonaliasmanager
   python install_simple.py
   ```

2. **Check Python path:**
   ```bash
   python -c "import sys; print(sys.path)"
   ```

### WSL-specific issues

1. **Use the WSL installer:**
   ```bash
   bash install_wsl.sh
   ```

2. **Check Python in WSL:**
   ```bash
   which python3
   python3 --version
   ```

## Uninstallation

### For pip installations:
```bash
pip uninstall pythonaliasmanager
```

### For file-based installations:
```bash
rm -rf ~/.python_aliases
# Remove from PATH manually
```

## Migration from Old Versions

If you're upgrading from a previous version:

1. **Backup your aliases:**
   ```bash
   pam list > my_aliases_backup.txt
   ```

2. **Uninstall old version:**
   ```bash
   rm -rf ~/.python_aliases  # or pip uninstall if applicable
   ```

3. **Install new version:**
   ```bash
   python install_simple.py
   ```

4. **Re-create aliases from backup**

## Package Structure

The new modular structure includes:

```
alias_manager/
├── __init__.py          # Package exports
├── __main__.py          # Module execution support
├── cli.py              # Command-line interface
├── core.py             # Main functionality
├── config.py           # Configuration management
├── venv_detector.py    # Virtual environment detection
├── script_generator.py # Script generation
├── dependency_manager.py # Dependency handling
└── environment_setup.py # Environment setup
```

This allows for:
- Better code organization
- Easier testing and development
- Standard Python package practices
- Multiple installation methods
