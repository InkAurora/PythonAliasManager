# Python Script Alias Manager

A comprehensive tool for creating and managing aliases for Python scripts on Windows, Linux, and macOS, allowing you to run your Python scripts from anywhere in your system using simple commands. Features intelligent virtual environment detection and cross-platform compatibility for seamless script execution in any shell environment!

## Features

- **Cross-Platform**: Works in Windows CMD/PowerShell, Bash, Git Bash, WSL, Linux, and macOS
- **Smart Virtual Environment Detection**: Automatically detects and uses virtual environments (venv, conda, project dependencies)
- **Create Aliases**: Create short, memorable aliases for your Python scripts
- **Path Integration**: Run aliased scripts from anywhere in your system
- **Alias Management**: List, update, and remove aliases easily
- **Dual File Generation**: Creates both Windows batch files (.bat) and shell scripts for maximum compatibility
- **Path Validation**: Checks if scripts exist and validates PATH configuration
- **Cross-argument Support**: Pass arguments to your aliased scripts
- **Environment Analysis**: Detailed virtual environment information and package listing
- **WSL Path Conversion**: Automatic Windows-to-WSL path conversion for seamless cross-platform operation

## Installation

1. **Quick Install** (Windows):

   ```powershell
   python install_alias_manager.py
   ```

2. **WSL Installation** (Windows Subsystem for Linux):

   ```bash
   bash install_wsl.sh
   ```

3. **Manual Install**:
   - Copy `python_alias_manager.py` to a directory in your PATH
   - Or follow the PATH setup instructions below

## Usage

### Basic Commands

```powershell
# Add an alias
pam add myapp C:\path\to\my_script.py

# List all aliases (shows virtual environment status)
pam list

# Remove an alias
pam remove myapp

# Update an alias
pam update myapp C:\new\path\to\script.py

# Run a script by alias
pam run myapp --help

# Check virtual environment info for an alias
pam venv myapp

# Check PATH setup
pam setup
```

### PATH Setup

For aliases to work from anywhere, the alias directory must be in your PATH:

1. **Automatic** (Recommended):

   ```powershell
   # Windows
   python install_alias_manager.py

   # WSL
   bash install_wsl.sh
   ```

2. **Windows Manual Setup**:

   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Click "Environment Variables"
   - Under "User variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\Users\YourUsername\.python_aliases\manager`
   - Click "OK" and restart your terminal

3. **PowerShell** (Run as Administrator):

   ```powershell
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\$env:USERNAME\.python_aliases\manager", [EnvironmentVariableTarget]::User)
   ```

4. **WSL Setup**:
   Add this line to your `~/.bashrc`:

   ```bash
   export PATH="$PATH:$HOME/.python_aliases/manager"
   ```

   Then run: `source ~/.bashrc`

5. **Bash/Linux/macOS Setup**:
   Add this line to your `~/.bashrc`, `~/.zshrc`, or `~/.profile`:

   ```bash
   export PATH="$PATH:$HOME/.python_aliases/manager"
   ```

   Then run: `source ~/.bashrc` (or restart your terminal)

6. **Git Bash on Windows**:
   Add this line to `~/.bashrc`:
   ```bash
   export PATH="$PATH:/c/Users/$USER/.python_aliases/manager"
   ```

## How It Works

1. **Alias Creation**: When you create an alias, the manager:

   - Stores the script path in a configuration file
   - Creates a Windows batch file (`.bat`) for CMD/PowerShell
   - Creates a shell script (no extension) for Bash environments
   - Both files call Python with your script path

2. **Script Execution**: When you run an alias:

   - Windows finds the `.bat` file when using CMD/PowerShell
   - Bash finds the shell script when using Bash/Terminal
   - The appropriate file executes Python with your script
   - All arguments are passed through to your script

3. **Cross-Platform Compatibility**:
   - Works seamlessly in Windows Command Prompt
   - Works in PowerShell
   - Works in Git Bash on Windows
   - Works in WSL (Windows Subsystem for Linux)
   - Works in Linux and macOS terminals

## Example Workflow

1. **Create a Python script**:

   ```python
   # my_tool.py
   import argparse

   def main():
       parser = argparse.ArgumentParser()
       parser.add_argument('--name', default='World')
       args = parser.parse_args()
       print(f"Hello, {args.name}!")

   if __name__ == "__main__":
       main()
   ```

2. **Create an alias**:

   ```powershell
   pam add hello C:\scripts\my_tool.py
   ```

3. **Use from anywhere** (works in all shells):

   ```bash
   # Windows Command Prompt / PowerShell
   hello --name "Alice"

   # Bash / Git Bash / WSL / Linux / macOS
   hello --name "Alice"

   # Output: Hello, Alice!
   ```

## Directory Structure

After installation, your directory structure will look like:

```
C:\Users\YourUsername\.python_aliases\
├── aliases.json          # Configuration file storing alias mappings
├── bin\                  # Directory containing alias files (added to PATH)
│   ├── hello.bat        # Windows batch file for 'hello' alias (with venv support)
│   ├── hello            # Bash shell script for 'hello' alias (with venv activation)
│   ├── myapp.bat        # Windows batch file for 'myapp' alias
│   └── myapp            # Bash shell script for 'myapp' alias
└── manager\             # Installation directory (added to PATH)
    ├── python_alias_manager.py
    ├── pam.bat          # Windows batch file for the manager
    └── pam              # Bash shell script for the manager
```

## Advanced Usage

### Running Scripts Directly

```powershell
# Instead of: pam run myapp --help
# You can simply use:
myapp --help
```

### Updating Scripts

If you move or rename your Python script, update the alias:

```powershell
pam update myapp C:\new\location\script.py
```

### Checking Alias Status

The `list` command shows if the target scripts still exist and their virtual environment status:

```powershell
pam list
# Output:
# Current aliases:
# --------------------------------------------------------------------------------
# ✓ hello                -> C:\scripts\my_tool.py
# ✓ webproject           -> C:\dev\myproject\main.py 🐍 [venv]
#                            Virtual env: C:\dev\myproject\venv
# ✓ datatools            -> C:\analysis\processor.py 🐍 [conda]
#                            Conda env: C:\analysis\environment.yml
# ✓ simpleapp            -> C:\scripts\simple.py 📦 [project]
#                            Dependencies: C:\scripts\requirements.txt
# ✗ oldapp              -> C:\deleted\script.py
# --------------------------------------------------------------------------------
# Total aliases: 5
# With virtual environments: 3
# Without virtual environments: 2
```

### Detailed Virtual Environment Information

Check comprehensive virtual environment details for any alias:

```powershell
pam venv webproject
# Output:
# Virtual Environment Information for 'webproject':
# Script: C:\dev\myproject\main.py
# ------------------------------------------------------------
# ✅ Virtual environment detected!
# Type: VENV
# Path: C:\dev\myproject\venv
# Activate script: C:\dev\myproject\venv\Scripts\activate
# Python executable: C:\dev\myproject\venv\Scripts\python.exe
# Python version: Python 3.12.0
# Installed packages: 15
# First few packages:
#   beautifulsoup4    4.12.2
#   certifi          2023.7.22
#   charset-normalizer 3.2.0
#   idna             3.4
#   requests         2.31.0
#   ... and 10 more
```

## Troubleshooting

### "Command not found" errors

1. Check if the alias directory is in PATH: `pam setup`
2. Restart your terminal after PATH changes
3. Verify the alias exists: `pam list`

### "Script not found" errors

1. Check if the original script still exists
2. Update the alias if the script moved: `pam update alias_name new_path`

### WSL-specific issues

1. **"required file not found"**: Use the WSL installer: `bash install_wsl.sh`
2. **Python not found in WSL**: Install Python: `sudo apt update && sudo apt install python3`
3. **Path conversion issues**: The system automatically converts Windows paths to WSL paths

### Virtual environment issues

1. **"Virtual environment not detected"**:
   - Ensure your venv is in the script directory or up to 3 parent levels
   - Check that activation scripts exist (`activate` or `activate.bat`)
   - Use `pam venv alias_name` to see detailed detection info
2. **"Module not found" errors with venv**:
   - Verify packages are installed in the virtual environment
   - Check that the correct Python executable is being used
   - Try recreating the alias: `pam update alias_name script_path`
3. **WSL virtual environment issues**:
   - Ensure Python 3 is installed in WSL: `sudo apt install python3`
   - Check that Windows venv paths are being converted correctly
   - Virtual environments work best when created within WSL filesystem

### Permission errors

- Run PowerShell as Administrator when modifying system PATH
- Ensure you have write permissions to the alias directory
- In WSL, make sure shell scripts are executable: `chmod +x ~/.python_aliases/manager/pam`

## Examples

The included `example_script.py` demonstrates various features:

```bash
# Create alias for the example script (works in any shell)
pam add demo C:\Users\INK\Desktop\example_script.py

# Use the aliased script from Windows CMD/PowerShell
demo greet Alice --times 3 --enthusiastic
demo calc add 10 5
demo info

# Same commands work in Bash/Git Bash/WSL
demo greet Alice --times 3 --enthusiastic
demo calc add 10 5
demo info
```

## Tips

1. **Use descriptive names**: Choose alias names that are memorable and conflict-free
2. **Organize your scripts**: Keep your Python scripts in a dedicated directory
3. **Virtual environment best practices**:
   - Create virtual environments in your project directories
   - Use standard names (`venv`, `env`, `.venv`) for automatic detection
   - Install project dependencies in the virtual environment before creating aliases
4. **Version control**: Include the alias configuration in your development workflow
5. **Documentation**: Document your aliases for team members or future reference
6. **Cross-platform testing**: Test your aliases in different shell environments
7. **Git Bash users**: The system works seamlessly in Git Bash on Windows
8. **WSL compatibility**: All aliases work perfectly in Windows Subsystem for Linux
9. **Virtual environment monitoring**: Use `pam venv alias_name` to check if dependencies are up to date
10. **Project organization**: Keep related scripts and their virtual environments together

## License

This tool is provided as-is for personal and educational use.

## Virtual Environment Support

The Python Alias Manager automatically detects and handles virtual environments, ensuring your scripts run with the correct Python interpreter and dependencies.

### Automatic Detection

The system automatically detects:

1. **Virtual Environments (venv/virtualenv)**:

   - Searches for `venv`, `env`, `.venv`, `.env` directories
   - Checks script directory and up to 3 parent levels
   - Automatically uses the venv's Python executable
   - Sources activation scripts in shell environments

2. **Project Dependencies**:

   - Detects `requirements.txt`, `pyproject.toml`, `setup.py`, `poetry.lock`
   - Flags projects that might benefit from virtual environments

3. **Conda Environments**:
   - Identifies `environment.yml` files
   - Provides recommendations for conda setup

### Virtual Environment Features

```powershell
# When adding an alias, you'll see venv detection:
pam add myproject C:\dev\myproject\main.py

# Output shows detected environment:
# 🐍 Virtual Environment Detected:
#    Type: Virtual Environment
#    Path: C:\dev\myproject\venv
#    Python: C:\dev\myproject\venv\Scripts\python.exe

# Check detailed venv info for any alias:
pam venv myproject

# List shows venv status indicators:
pam list
# ✓ myproject            -> C:\dev\myproject\main.py 🐍 [venv]
# ✓ simple_script       -> C:\scripts\simple.py
# ✓ conda_project       -> C:\data\analysis.py 🐍 [conda]
```

### How Virtual Environments Are Used

1. **Windows (.bat files)**:

   - Uses the virtual environment's Python executable directly
   - No activation needed, runs isolated automatically

2. **Unix/Linux/macOS (shell scripts)**:

   - Sources the activation script before running
   - Converts Windows paths to WSL paths when needed
   - Falls back to system Python if activation fails

3. **WSL (Windows Subsystem for Linux)**:
   - Automatically converts Windows venv paths to WSL paths
   - Handles cross-filesystem virtual environment access
   - Maintains environment isolation across Windows/Linux boundary

### Virtual Environment Workflow Example

1. **Create a project with virtual environment**:

   ```powershell
   mkdir C:\dev\myproject
   cd C:\dev\myproject
   python -m venv venv
   venv\Scripts\activate
   pip install requests beautifulsoup4
   ```

2. **Create your Python script**:

   ```python
   # main.py
   import requests
   from bs4 import BeautifulSoup

   def main():
       print("Script running with virtual environment!")
       print(f"Requests version: {requests.__version__}")

   if __name__ == "__main__":
       main()
   ```

3. **Create alias (automatically detects venv)**:

   ```powershell
   pam add webtools C:\dev\myproject\main.py
   ```

4. **Use from anywhere** (automatically uses venv):

   ```powershell
   # Works in CMD/PowerShell with venv Python
   webtools

   # Works in Git Bash/WSL with venv activation
   webtools
   ```
