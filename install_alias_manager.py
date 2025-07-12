#!/usr/bin/env python3
"""
Installer for Python Alias Manager
Sets up the alias manager and optionally adds it to PATH.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    print("Python Alias Manager Installer")
    print("=" * 40)
    
    # Get the directory where this installer is located
    installer_dir = Path(__file__).parent.absolute()
    alias_manager_script = installer_dir / "python_alias_manager.py"
    alias_manager_package = installer_dir / "alias_manager"
    
    if not alias_manager_script.exists():
        print(f"Error: python_alias_manager.py not found in {installer_dir}")
        return
    
    if not alias_manager_package.exists():
        print(f"Error: alias_manager package not found in {installer_dir}")
        return
    
    # Create installation directory
    install_dir = Path.home() / ".python_aliases" / "manager"
    install_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy the main entry point script
    dest_script = install_dir / "python_alias_manager.py"
    shutil.copy2(alias_manager_script, dest_script)
    print(f"✓ Installed main script to: {dest_script}")
    
    # Copy the entire alias_manager package
    dest_package = install_dir / "alias_manager"
    if dest_package.exists():
        shutil.rmtree(dest_package)
    shutil.copytree(alias_manager_package, dest_package, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    print(f"✓ Installed alias_manager package to: {dest_package}")
    
    # Create a convenient batch file for the manager itself (Windows)
    manager_batch = install_dir / "pam.bat"
    python_exe = sys.executable
    
    batch_content = f'''@echo off
"{python_exe}" "{dest_script}" %*
'''
    
    with open(manager_batch, 'w') as f:
        f.write(batch_content)
    print(f"✓ Created Windows batch file: {manager_batch}")
    
    # Create a shell script for the manager (Bash)
    manager_shell = install_dir / "pam"
    
    shell_content = f'''#!/bin/bash
# Auto-detect Python executable and script path based on environment
if [[ "${{PWD}}" == /mnt/* ]] || command -v wslpath &> /dev/null; then
    # We're in WSL - use Linux Python and convert Windows paths
    PYTHON_CMD="python3"
    if [[ "{dest_script}" == [A-Za-z]:* ]]; then
        # Convert Windows path to WSL path
        SCRIPT_PATH=$(wslpath "{dest_script}")
    else
        SCRIPT_PATH="{dest_script}"
    fi
else
    # We're in regular Linux/macOS or Git Bash - use system Python
    PYTHON_CMD="python3"
    SCRIPT_PATH="{dest_script}"
fi

# Try python3 first, then python, then fall back to sys.executable path
if command -v python3 &> /dev/null; then
    "$PYTHON_CMD" "$SCRIPT_PATH" "$@"
elif command -v python &> /dev/null; then
    python "$SCRIPT_PATH" "$@"
else
    # Fallback to the original Python executable (may not work in WSL)
    "{python_exe}" "{dest_script}" "$@"
fi
'''
    
    with open(manager_shell, 'w') as f:
        f.write(shell_content)
    
    # Make the shell script executable
    manager_shell.chmod(0o755)
    print(f"✓ Created bash shell script: {manager_shell}")
    
    # Check PATH setup
    path_env = os.environ.get('PATH', '')
    install_dir_str = str(install_dir)
    
    if install_dir_str not in path_env:
        print(f"\n⚠️  PATH Setup Required:")
        print(f"To use 'pam' command from anywhere, add this directory to your PATH:")
        print(f"  {install_dir_str}")
        print()
        print("Windows Setup Instructions:")
        print("1. Press Win + R, type 'sysdm.cpl' and press Enter")
        print("2. Click 'Environment Variables'")
        print("3. Under 'User variables', find 'Path' and click 'Edit'")
        print("4. Click 'New' and add the path above")
        print("5. Click 'OK' to save and restart your terminal")
        print()
        print("PowerShell Command (as Administrator):")
        print(f'[Environment]::SetEnvironmentVariable("Path", $env:Path + ";{install_dir_str}", [EnvironmentVariableTarget]::User)')
        print()
        print("Bash/Linux/macOS Setup Instructions:")
        print("Add this line to your ~/.bashrc, ~/.zshrc, or ~/.profile:")
        print(f'export PATH="$PATH:{install_dir_str}"')
        print("Then run: source ~/.bashrc (or restart your terminal)")
        print()
        print("Git Bash on Windows:")
        print("Add this line to ~/.bashrc:")
        print(f'export PATH="$PATH:{install_dir_str.replace(os.sep, "/")}"')
        
        response = input("\nWould you like to try adding to PATH automatically? (y/n): ")
        if response.lower() == 'y':
            try:
                cmd = [
                    'powershell', '-Command',
                    f'[Environment]::SetEnvironmentVariable("Path", $env:Path + ";{install_dir_str}", [EnvironmentVariableTarget]::User)'
                ]
                subprocess.run(cmd, check=True)
                print("✓ Added to PATH successfully!")
                print("Please restart your terminal for changes to take effect.")
            except subprocess.CalledProcessError:
                print("✗ Failed to add to PATH automatically. Please add manually.")
    else:
        print(f"✓ Directory already in PATH: {install_dir_str}")
    
    print("\nInstallation complete!")
    print("\nThe 'pam' command now works in both:")
    print("  • Windows Command Prompt / PowerShell")
    print("  • Bash / Git Bash / WSL")
    print("\nUsage examples:")
    print("  pam add myapp C:\\path\\to\\my_script.py")
    print("  pam list")
    print("  pam remove myapp")
    print("  pam setup  # Check PATH configuration")
    
    # Run initial setup check
    print("\nRunning initial setup check...")
    subprocess.run([python_exe, str(dest_script), "setup"])

if __name__ == "__main__":
    main()
