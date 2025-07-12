#!/usr/bin/env python3
"""
Package Installer for Python Alias Manager
Installs the package using pip and sets up the command-line interface.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path


def run_command(cmd, check=True, capture_output=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=check, 
            capture_output=capture_output, 
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        raise


def check_pip():
    """Check if pip is available."""
    try:
        run_command("pip --version")
        return True
    except subprocess.CalledProcessError:
        return False


def install_package():
    """Install the package using pip."""
    print("Python Alias Manager Package Installer")
    print("=" * 40)
    
    # Check if pip is available
    if not check_pip():
        print("Error: pip is not available. Please install pip first.")
        return False
    
    # Get the directory where this installer is located
    package_dir = Path(__file__).parent.absolute()
    
    # Check if required files exist
    pyproject_file = package_dir / "pyproject.toml"
    if not pyproject_file.exists():
        print(f"Error: pyproject.toml not found in {package_dir}")
        return False
    
    # Install the package in development mode
    print(f"Installing package from: {package_dir}")
    try:
        cmd = f'pip install -e "{package_dir}"'
        result = run_command(cmd, capture_output=False)
        print("✓ Package installed successfully!")
    except subprocess.CalledProcessError:
        print("✗ Failed to install package with pip.")
        return False
    
    return True


def create_command_scripts():
    """Create command-line scripts for easy access."""
    print("\nCreating command-line scripts...")
    
    # Find the installed package location
    try:
        result = run_command("python -c \"import alias_manager; print(alias_manager.__file__)\"")
        package_path = Path(result.stdout.strip()).parent
        print(f"Package installed at: {package_path}")
    except subprocess.CalledProcessError:
        print("Warning: Could not determine package installation location.")
        return False
    
    # Create scripts directory
    scripts_dir = Path.home() / ".python_aliases" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    # Create Windows batch file
    batch_file = scripts_dir / "pam.bat"
    batch_content = f'''@echo off
python -m alias_manager.cli %*
'''
    
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    print(f"✓ Created Windows batch file: {batch_file}")
    
    # Create Unix shell script
    shell_file = scripts_dir / "pam"
    shell_content = '''#!/bin/bash
python -m alias_manager.cli "$@"
'''
    
    with open(shell_file, 'w') as f:
        f.write(shell_content)
    shell_file.chmod(0o755)
    print(f"✓ Created shell script: {shell_file}")
    
    return scripts_dir


def setup_path(scripts_dir):
    """Set up PATH environment variable."""
    path_env = os.environ.get('PATH', '')
    scripts_dir_str = str(scripts_dir)
    
    if scripts_dir_str not in path_env:
        print(f"\n⚠️  PATH Setup Required:")
        print(f"To use 'pam' command from anywhere, add this directory to your PATH:")
        print(f"  {scripts_dir_str}")
        print()
        print("Windows Setup Instructions:")
        print("1. Press Win + R, type 'sysdm.cpl' and press Enter")
        print("2. Click 'Environment Variables'")
        print("3. Under 'User variables', find 'Path' and click 'Edit'")
        print("4. Click 'New' and add the path above")
        print("5. Click 'OK' to save and restart your terminal")
        print()
        print("PowerShell Command (as Administrator):")
        print(f'[Environment]::SetEnvironmentVariable("Path", $env:Path + ";{scripts_dir_str}", [EnvironmentVariableTarget]::User)')
        print()
        print("Bash/Linux/macOS Setup Instructions:")
        print("Add this line to your ~/.bashrc, ~/.zshrc, or ~/.profile:")
        print(f'export PATH="$PATH:{scripts_dir_str}"')
        print("Then run: source ~/.bashrc (or restart your terminal)")
        
        response = input("\nWould you like to try adding to PATH automatically? (y/n): ")
        if response.lower() == 'y':
            try:
                cmd = [
                    'powershell', '-Command',
                    f'[Environment]::SetEnvironmentVariable("Path", $env:Path + ";{scripts_dir_str}", [EnvironmentVariableTarget]::User)'
                ]
                subprocess.run(cmd, check=True)
                print("✓ Added to PATH successfully!")
                print("Please restart your terminal for changes to take effect.")
            except subprocess.CalledProcessError:
                print("✗ Failed to add to PATH automatically. Please add manually.")
    else:
        print(f"✓ Directory already in PATH: {scripts_dir_str}")


def main():
    """Main installer function."""
    try:
        # Install the package
        if not install_package():
            return
        
        # Create command scripts
        scripts_dir = create_command_scripts()
        if not scripts_dir:
            return
        
        # Set up PATH
        setup_path(scripts_dir)
        
        print("\nInstallation complete!")
        print("\nThe 'pam' command is now available.")
        print("You can also use: python -m alias_manager.cli")
        print("\nUsage examples:")
        print("  pam add myapp C:\\path\\to\\my_script.py")
        print("  pam list")
        print("  pam remove myapp")
        print("  pam setup  # Check PATH configuration")
        
        # Test the installation
        print("\nTesting installation...")
        try:
            result = run_command("python -m alias_manager.cli --help", capture_output=False)
            print("✓ Installation test successful!")
        except subprocess.CalledProcessError:
            print("⚠️  Installation test failed. The package may not be properly installed.")
        
    except Exception as e:
        print(f"Installation failed: {e}")
        return


if __name__ == "__main__":
    main()
