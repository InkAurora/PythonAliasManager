#!/usr/bin/env python3
"""
Python Script Alias Manager
Creates and manages aliases for Python scripts that can be run from anywhere in PATH.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple

class PythonAliasManager:
    def __init__(self):
        # Create a directory for storing aliases and config
        self.alias_dir = Path.home() / ".python_aliases"
        self.alias_dir.mkdir(exist_ok=True)
        
        # Config file to store alias mappings
        self.config_file = self.alias_dir / "aliases.json"
        
        # Directory where batch files will be created
        self.batch_dir = self.alias_dir / "bin"
        self.batch_dir.mkdir(exist_ok=True)
        
        # Load existing aliases
        self.aliases = self.load_aliases()
        
    def load_aliases(self) -> Dict[str, str]:
        """Load existing aliases from config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def save_aliases(self):
        """Save aliases to config file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.aliases, f, indent=2)
    
    def detect_venv(self, script_path: str) -> Optional[Dict[str, str]]:
        """Detect if there's a virtual environment associated with a script."""
        script_dir = Path(script_path).parent
        
        # Check for common virtual environment patterns
        venv_info = {}
        
        # 1. Check for venv/env directories in the script directory
        for venv_name in ['venv', 'env', '.venv', '.env']:
            venv_path = script_dir / venv_name
            if venv_path.exists() and venv_path.is_dir():
                # Check if it's a valid venv by looking for activate script
                activate_scripts = [
                    venv_path / 'Scripts' / 'activate',      # Windows
                    venv_path / 'Scripts' / 'activate.bat',  # Windows
                    venv_path / 'bin' / 'activate',          # Linux/macOS
                ]
                
                for activate_script in activate_scripts:
                    if activate_script.exists():
                        venv_info['path'] = str(venv_path)
                        venv_info['type'] = 'venv'
                        venv_info['activate_script'] = str(activate_script)
                        return venv_info
        
        # 2. Check for requirements.txt or pyproject.toml (suggests project with dependencies)
        requirements_files = [
            script_dir / 'requirements.txt',
            script_dir / 'pyproject.toml',
            script_dir / 'setup.py',
            script_dir / 'poetry.lock'
        ]
        
        for req_file in requirements_files:
            if req_file.exists():
                venv_info['requirements_file'] = str(req_file)
                venv_info['type'] = 'project'
                break
        
        # 3. Check for conda environment (look for environment.yml)
        conda_env_file = script_dir / 'environment.yml'
        if conda_env_file.exists():
            venv_info['conda_env_file'] = str(conda_env_file)
            venv_info['type'] = 'conda'
        
        # 4. Check parent directories for venv (up to 3 levels)
        parent_dir = script_dir.parent
        for level in range(3):
            if parent_dir == parent_dir.parent:  # Reached root
                break
            
            for venv_name in ['venv', 'env', '.venv', '.env']:
                venv_path = parent_dir / venv_name
                if venv_path.exists() and venv_path.is_dir():
                    activate_scripts = [
                        venv_path / 'Scripts' / 'activate',      # Windows
                        venv_path / 'Scripts' / 'activate.bat',  # Windows
                        venv_path / 'bin' / 'activate',          # Linux/macOS
                    ]
                    
                    for activate_script in activate_scripts:
                        if activate_script.exists():
                            venv_info['path'] = str(venv_path)
                            venv_info['type'] = 'venv'
                            venv_info['activate_script'] = str(activate_script)
                            venv_info['parent_level'] = level + 1
                            return venv_info
            
            parent_dir = parent_dir.parent
        
        return venv_info if venv_info else None
    
    def get_venv_python_executable(self, venv_info: Dict[str, str]) -> Optional[str]:
        """Get the Python executable path for a virtual environment."""
        if not venv_info or venv_info.get('type') != 'venv':
            return None
        
        venv_path = Path(venv_info['path'])
        
        # Check common Python executable locations in venv
        python_executables = [
            venv_path / 'Scripts' / 'python.exe',    # Windows
            venv_path / 'Scripts' / 'python',        # Windows
            venv_path / 'bin' / 'python',            # Linux/macOS
            venv_path / 'bin' / 'python3',           # Linux/macOS
        ]
        
        for python_exe in python_executables:
            if python_exe.exists():
                return str(python_exe)
        
        return None
    
    def create_batch_file(self, alias_name: str, script_path: str):
        """Create a batch file for the alias (Windows)."""
        batch_file = self.batch_dir / f"{alias_name}.bat"
        
        # Detect virtual environment
        venv_info = self.detect_venv(script_path)
        
        if venv_info and venv_info.get('type') == 'venv':
            # Use virtual environment Python
            venv_python = self.get_venv_python_executable(venv_info)
            if venv_python:
                python_exe = venv_python
            else:
                python_exe = sys.executable
        else:
            # Use system Python
            python_exe = sys.executable
        
        # Create batch file content
        batch_content = f'''@echo off
"{python_exe}" "{script_path}" %*
'''
        
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        
        return batch_file
    
    def create_shell_script(self, alias_name: str, script_path: str):
        """Create a shell script for the alias (Linux/macOS/Bash)."""
        shell_file = self.batch_dir / alias_name
        
        # Detect virtual environment
        venv_info = self.detect_venv(script_path)
        
        if venv_info and venv_info.get('type') == 'venv':
            # Use virtual environment Python
            venv_python = self.get_venv_python_executable(venv_info)
            activate_script = venv_info.get('activate_script', '')
            
            if venv_python and activate_script:
                # Create shell script content with venv activation
                shell_content = f'''#!/bin/bash
# Auto-detect Python executable and script path based on environment
if [[ "${{PWD}}" == /mnt/* ]] || command -v wslpath &> /dev/null; then
    # We're in WSL - use Linux Python and convert Windows paths
    if [[ "{script_path}" == [A-Za-z]:* ]]; then
        # Convert Windows path to WSL path
        SCRIPT_PATH=$(wslpath "{script_path}")
    else
        SCRIPT_PATH="{script_path}"
    fi
    
    # Try to find and activate the virtual environment
    if [[ "{activate_script}" == [A-Za-z]:* ]]; then
        ACTIVATE_SCRIPT=$(wslpath "{activate_script}")
    else
        ACTIVATE_SCRIPT="{activate_script}"
    fi
    
    # Source the activation script and run Python
    if [[ -f "$ACTIVATE_SCRIPT" ]]; then
        source "$ACTIVATE_SCRIPT"
        # Try python3 first, then python after activation
        if command -v python3 &> /dev/null; then
            python3 "$SCRIPT_PATH" "$@"
        elif command -v python &> /dev/null; then
            python "$SCRIPT_PATH" "$@"
        else
            echo "Error: No Python interpreter found after activating virtual environment"
            exit 1
        fi
    else
        # Fallback to system Python
        if command -v python3 &> /dev/null; then
            python3 "$SCRIPT_PATH" "$@"
        elif command -v python &> /dev/null; then
            python "$SCRIPT_PATH" "$@"
        else
            echo "Error: No Python interpreter found"
            exit 1
        fi
    fi
else
    # We're in regular Linux/macOS or Git Bash
    SCRIPT_PATH="{script_path}"
    
    # Activate virtual environment if available
    if [[ -f "{activate_script}" ]]; then
        source "{activate_script}"
        # Try python3 first, then python after activation
        if command -v python3 &> /dev/null; then
            python3 "$SCRIPT_PATH" "$@"
        elif command -v python &> /dev/null; then
            python "$SCRIPT_PATH" "$@"
        else
            echo "Error: No Python interpreter found after activating virtual environment"
            exit 1
        fi
    else
        # Fallback to system Python
        if command -v python3 &> /dev/null; then
            python3 "$SCRIPT_PATH" "$@"
        elif command -v python &> /dev/null; then
            python "$SCRIPT_PATH" "$@"
        else
            echo "Error: No Python interpreter found"
            exit 1
        fi
    fi
fi
'''
            else:
                # Fallback to system Python
                shell_content = f'''#!/bin/bash
# Auto-detect Python executable and script path based on environment
if [[ "${{PWD}}" == /mnt/* ]] || command -v wslpath &> /dev/null; then
    # We're in WSL - use Linux Python and convert Windows paths
    PYTHON_CMD="python3"
    if [[ "{script_path}" == [A-Za-z]:* ]]; then
        # Convert Windows path to WSL path
        SCRIPT_PATH=$(wslpath "{script_path}")
    else
        SCRIPT_PATH="{script_path}"
    fi
else
    # We're in regular Linux/macOS or Git Bash - use system Python
    PYTHON_CMD="python3"
    SCRIPT_PATH="{script_path}"
fi

# Try python3 first, then python
if command -v python3 &> /dev/null; then
    "$PYTHON_CMD" "$SCRIPT_PATH" "$@"
elif command -v python &> /dev/null; then
    python "$SCRIPT_PATH" "$@"
else
    # Fallback to the original Python executable
    "{sys.executable}" "{script_path}" "$@"
fi
'''
        else:
            # Create shell script content without venv
            shell_content = f'''#!/bin/bash
# Auto-detect Python executable and script path based on environment
if [[ "${{PWD}}" == /mnt/* ]] || command -v wslpath &> /dev/null; then
    # We're in WSL - use Linux Python and convert Windows paths
    PYTHON_CMD="python3"
    if [[ "{script_path}" == [A-Za-z]:* ]]; then
        # Convert Windows path to WSL path
        SCRIPT_PATH=$(wslpath "{script_path}")
    else
        SCRIPT_PATH="{script_path}"
    fi
else
    # We're in regular Linux/macOS or Git Bash - use system Python
    PYTHON_CMD="python3"
    SCRIPT_PATH="{script_path}"
fi

# Try python3 first, then python, then fall back to sys.executable path
if command -v python3 &> /dev/null; then
    "$PYTHON_CMD" "$SCRIPT_PATH" "$@"
elif command -v python &> /dev/null; then
    python "$SCRIPT_PATH" "$@"
else
    # Fallback to the original Python executable (may not work in WSL)
    "{sys.executable}" "{script_path}" "$@"
fi
'''
        
        with open(shell_file, 'w') as f:
            f.write(shell_content)
        
        # Make the shell script executable
        shell_file.chmod(0o755)
        
        return shell_file
    
    def add_alias(self, alias_name: str, script_path: str) -> bool:
        """Add a new alias for a Python script."""
        # Resolve the script path to absolute path
        script_path = os.path.abspath(script_path)
        
        # Check if script exists
        if not os.path.exists(script_path):
            print(f"Error: Script '{script_path}' does not exist.")
            return False
        
        # Check if it's a Python file
        if not script_path.endswith('.py'):
            print(f"Warning: '{script_path}' doesn't appear to be a Python file.")
        
        # Detect virtual environment
        venv_info = self.detect_venv(script_path)
        
        # Create both batch file (Windows) and shell script (Bash)
        try:
            batch_file = self.create_batch_file(alias_name, script_path)
            shell_file = self.create_shell_script(alias_name, script_path)
            print(f"Created Windows batch file: {batch_file}")
            print(f"Created bash shell script: {shell_file}")
            
            # Display virtual environment information
            if venv_info:
                print(f"🐍 Virtual Environment Detected:")
                if venv_info.get('type') == 'venv':
                    print(f"   Type: Virtual Environment")
                    print(f"   Path: {venv_info['path']}")
                    if venv_info.get('parent_level'):
                        print(f"   Location: {venv_info['parent_level']} level(s) up from script")
                    venv_python = self.get_venv_python_executable(venv_info)
                    if venv_python:
                        print(f"   Python: {venv_python}")
                elif venv_info.get('type') == 'conda':
                    print(f"   Type: Conda Environment")
                    print(f"   Config: {venv_info['conda_env_file']}")
                elif venv_info.get('type') == 'project':
                    print(f"   Type: Project with Dependencies")
                    print(f"   Requirements: {venv_info['requirements_file']}")
                    print(f"   Note: Consider creating a virtual environment for this project")
            else:
                print("ℹ️  No virtual environment detected")
                
        except Exception as e:
            print(f"Error creating alias files: {e}")
            return False
        
        # Save alias mapping
        self.aliases[alias_name] = script_path
        self.save_aliases()
        
        print(f"Alias '{alias_name}' created for '{script_path}'")
        print("Works in both Windows Command Prompt/PowerShell and Bash!")
        return True
    
    def remove_alias(self, alias_name: str) -> bool:
        """Remove an alias."""
        if alias_name not in self.aliases:
            print(f"Alias '{alias_name}' does not exist.")
            return False
        
        # Remove both batch file and shell script
        batch_file = self.batch_dir / f"{alias_name}.bat"
        shell_file = self.batch_dir / alias_name
        
        if batch_file.exists():
            batch_file.unlink()
            print(f"Removed Windows batch file: {batch_file}")
        
        if shell_file.exists():
            shell_file.unlink()
            print(f"Removed bash shell script: {shell_file}")
        
        # Remove from config
        del self.aliases[alias_name]
        self.save_aliases()
        
        print(f"Alias '{alias_name}' removed.")
        return True
    
    def list_aliases(self):
        """List all existing aliases."""
        if not self.aliases:
            print("No aliases found.")
            return
        
        print("Current aliases:")
        print("-" * 80)
        for alias, script in self.aliases.items():
            status = "✓" if os.path.exists(script) else "✗"
            
            # Get virtual environment info
            venv_info = self.detect_venv(script) if os.path.exists(script) else None
            venv_status = ""
            
            if venv_info:
                if venv_info.get('type') == 'venv':
                    venv_status = " 🐍 [venv]"
                elif venv_info.get('type') == 'conda':
                    venv_status = " 🐍 [conda]"
                elif venv_info.get('type') == 'project':
                    venv_status = " 📦 [project]"
            
            print(f"{status} {alias:<20} -> {script}{venv_status}")
            
            # Show detailed venv info if available
            if venv_info and venv_info.get('type') == 'venv':
                print(f"   {'':>21}    Virtual env: {venv_info['path']}")
                if venv_info.get('parent_level'):
                    print(f"   {'':>21}    Location: {venv_info['parent_level']} level(s) up")
            elif venv_info and venv_info.get('type') == 'conda':
                print(f"   {'':>21}    Conda env: {venv_info['conda_env_file']}")
            elif venv_info and venv_info.get('type') == 'project':
                print(f"   {'':>21}    Dependencies: {venv_info['requirements_file']}")
        
        # Show summary
        total_aliases = len(self.aliases)
        venv_aliases = sum(1 for script in self.aliases.values() 
                          if os.path.exists(script) and self.detect_venv(script))
        print("-" * 80)
        print(f"Total aliases: {total_aliases}")
        print(f"With virtual environments: {venv_aliases}")
        print(f"Without virtual environments: {total_aliases - venv_aliases}")
    
    def update_alias(self, alias_name: str, new_script_path: str) -> bool:
        """Update an existing alias."""
        if alias_name not in self.aliases:
            print(f"Alias '{alias_name}' does not exist. Use 'add' to create it.")
            return False
        
        return self.add_alias(alias_name, new_script_path)
    
    def check_path_setup(self):
        """Check if the alias directory is in PATH and provide setup instructions."""
        path_env = os.environ.get('PATH', '')
        batch_dir_str = str(self.batch_dir)
        
        if batch_dir_str not in path_env:
            print(f"⚠️  Setup Required:")
            print(f"The alias directory is not in your PATH.")
            print(f"To use aliases from anywhere, add this directory to your PATH:")
            print(f"  {batch_dir_str}")
            print()
            print("Windows Setup Instructions:")
            print("1. Open System Properties (Win + Pause)")
            print("2. Click 'Advanced system settings'")
            print("3. Click 'Environment Variables'")
            print("4. Under 'User variables', find and select 'Path', then click 'Edit'")
            print("5. Click 'New' and add the path above")
            print("6. Click 'OK' to save")
            print("7. Restart your command prompt/PowerShell")
            print()
            print("PowerShell Command (as Administrator):")
            print(f'[Environment]::SetEnvironmentVariable("Path", $env:Path + ";{batch_dir_str}", [EnvironmentVariableTarget]::User)')
            print()
            print("Bash/Linux/macOS Setup Instructions:")
            print("Add this line to your ~/.bashrc, ~/.zshrc, or ~/.profile:")
            print(f'export PATH="$PATH:{batch_dir_str}"')
            print("Then run: source ~/.bashrc (or restart your terminal)")
            print()
            print("Git Bash on Windows:")
            print("Add this line to ~/.bashrc:")
            print(f'export PATH="$PATH:{batch_dir_str.replace(os.sep, "/")}"')
            return False
        else:
            print(f"✓ Alias directory is in PATH: {batch_dir_str}")
            print("Aliases will work in both Windows Command Prompt/PowerShell and Bash!")
            return True
    
    def check_venv_info(self, alias_name: str) -> bool:
        """Check and display detailed virtual environment information for an alias."""
        if alias_name not in self.aliases:
            print(f"Alias '{alias_name}' not found.")
            return False
        
        script_path = self.aliases[alias_name]
        if not os.path.exists(script_path):
            print(f"Script '{script_path}' no longer exists.")
            return False
        
        print(f"Virtual Environment Information for '{alias_name}':")
        print(f"Script: {script_path}")
        print("-" * 60)
        
        venv_info = self.detect_venv(script_path)
        
        if not venv_info:
            print("❌ No virtual environment detected")
            print("\nRecommendations:")
            print("• Create a virtual environment for this project:")
            print(f"  cd {Path(script_path).parent}")
            print("  python -m venv venv")
            print("  venv\\Scripts\\activate  # Windows")
            print("  source venv/bin/activate  # Linux/macOS")
            print("• Install dependencies in the virtual environment")
            return False
        
        print("✅ Virtual environment detected!")
        print(f"Type: {venv_info['type'].upper()}")
        
        if venv_info.get('type') == 'venv':
            print(f"Path: {venv_info['path']}")
            print(f"Activate script: {venv_info.get('activate_script', 'Not found')}")
            
            if venv_info.get('parent_level'):
                print(f"Location: {venv_info['parent_level']} level(s) up from script")
            
            venv_python = self.get_venv_python_executable(venv_info)
            if venv_python:
                print(f"Python executable: {venv_python}")
                
                # Try to get Python version from venv
                try:
                    result = subprocess.run([venv_python, "--version"], 
                                         capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"Python version: {result.stdout.strip()}")
                except Exception:
                    print("Python version: Unable to determine")
                
                # Try to list installed packages
                try:
                    result = subprocess.run([venv_python, "-m", "pip", "list"], 
                                         capture_output=True, text=True)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if len(lines) > 2:  # Skip header lines
                            print(f"Installed packages: {len(lines) - 2}")
                            print("First few packages:")
                            for line in lines[2:7]:  # Show first 5 packages
                                print(f"  {line}")
                            if len(lines) > 7:
                                print(f"  ... and {len(lines) - 7} more")
                except Exception:
                    print("Installed packages: Unable to determine")
            
        elif venv_info.get('type') == 'conda':
            print(f"Conda environment file: {venv_info['conda_env_file']}")
            print("Note: Conda environments are not automatically used by aliases")
            print("Consider creating a conda environment and updating the alias manually")
            
        elif venv_info.get('type') == 'project':
            print(f"Requirements file: {venv_info['requirements_file']}")
            print("Note: Dependencies detected but no virtual environment found")
            print("Consider creating a virtual environment for this project")
        
        return True

    def run_script(self, alias_name: str, args: list = None):
        """Run a script by its alias."""
        if alias_name not in self.aliases:
            print(f"Alias '{alias_name}' not found.")
            return False
        
        script_path = self.aliases[alias_name]
        if not os.path.exists(script_path):
            print(f"Script '{script_path}' no longer exists.")
            return False
        
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)
        
        try:
            subprocess.run(cmd)
            return True
        except Exception as e:
            print(f"Error running script: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Python Script Alias Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python_alias_manager.py add myapp ~/scripts/my_application.py
  python_alias_manager.py list
  python_alias_manager.py remove myapp
  python_alias_manager.py run myapp --help
  python_alias_manager.py venv myapp
  python_alias_manager.py setup
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add alias command
    add_parser = subparsers.add_parser('add', help='Add a new alias')
    add_parser.add_argument('alias_name', help='Name for the alias')
    add_parser.add_argument('script_path', help='Path to the Python script')
    
    # Remove alias command
    remove_parser = subparsers.add_parser('remove', help='Remove an alias')
    remove_parser.add_argument('alias_name', help='Name of the alias to remove')
    
    # List aliases command
    subparsers.add_parser('list', help='List all aliases')
    
    # Update alias command
    update_parser = subparsers.add_parser('update', help='Update an existing alias')
    update_parser.add_argument('alias_name', help='Name of the alias to update')
    update_parser.add_argument('script_path', help='New path to the Python script')
    
    # Run script command
    run_parser = subparsers.add_parser('run', help='Run a script by alias')
    run_parser.add_argument('alias_name', help='Name of the alias to run')
    run_parser.add_argument('args', nargs='*', help='Arguments to pass to the script')
    
    # Setup command
    subparsers.add_parser('setup', help='Check and show PATH setup instructions')
    
    # Virtual environment info command
    venv_parser = subparsers.add_parser('venv', help='Check virtual environment info for an alias')
    venv_parser.add_argument('alias_name', help='Name of the alias to check')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = PythonAliasManager()
    
    if args.command == 'add':
        manager.add_alias(args.alias_name, args.script_path)
        manager.check_path_setup()
    elif args.command == 'remove':
        manager.remove_alias(args.alias_name)
    elif args.command == 'list':
        manager.list_aliases()
    elif args.command == 'update':
        manager.update_alias(args.alias_name, args.script_path)
    elif args.command == 'run':
        manager.run_script(args.alias_name, args.args)
    elif args.command == 'setup':
        manager.check_path_setup()
    elif args.command == 'venv':
        manager.check_venv_info(args.alias_name)

if __name__ == "__main__":
    main()
