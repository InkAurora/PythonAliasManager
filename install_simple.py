#!/usr/bin/env python3
"""
Simple installer for Python Alias Manager
Uses pip to install the package with proper entry points.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def main():
    """Main installation function."""
    print("Python Alias Manager - Simple Installer")
    print("=" * 40)
    
    # Get current directory
    current_dir = Path(__file__).parent.absolute()
    
    # Check if we have the required files
    if not (current_dir / "pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found!")
        print("Make sure you're running this from the project root directory.")
        return False
    
    if not (current_dir / "alias_manager").exists():
        print("❌ Error: alias_manager package not found!")
        return False
    
    print("📦 Installing Python Alias Manager...")
    
    # Install in editable mode for development
    install_cmd = f'pip install -e "{current_dir}"'
    success, output = run_command(install_cmd)
    
    if not success:
        print("❌ Installation failed!")
        print("Error output:", output)
        return False
    
    print("✅ Installation successful!")
    print()
    
    # Test the installation
    print("🧪 Testing installation...")
    test_success, test_output = run_command("pam --help")
    
    if test_success:
        print("✅ Command 'pam' is working correctly!")
        print()
        print("🎉 Installation Complete!")
        print()
        print("You can now use the following commands:")
        print("  • pam --help                    # Show help")
        print("  • pam add myapp script.py       # Add an alias")
        print("  • pam list                      # List all aliases")
        print("  • pam remove myapp             # Remove an alias")
        print("  • pam setup                     # Check configuration")
        print()
        print("Alternative command names:")
        print("  • python-alias-manager         # Same as 'pam'")
        print("  • python -m alias_manager.cli  # Direct module execution")
        
    else:
        print("⚠️  Command 'pam' not found in PATH.")
        print("The package was installed, but the entry point may not be in your PATH.")
        print()
        print("You can still use it with:")
        print("  python -m alias_manager.cli --help")
        print()
        print("To fix PATH issues, try:")
        print("  1. Restart your terminal/command prompt")
        print("  2. If using a virtual environment, make sure it's activated")
        print("  3. Check that your Python Scripts directory is in PATH")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
