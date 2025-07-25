"""
Configuration management for Python Alias Manager.
Handles loading and saving alias configurations.
"""

import json
import os
from pathlib import Path
from typing import Dict


def safe_print(*args, **kwargs):
    """Print with safe Unicode handling for Windows."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Replace Unicode characters with ASCII equivalents on Windows
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                arg = arg.replace('✓', '*').replace('⚠', '!').replace('❌', 'X').replace('🎉', '!')
            safe_args.append(arg)
        print(*safe_args, **kwargs)


class ConfigManager:
    """Manages configuration and alias storage for the Python Alias Manager."""
    
    def __init__(self):
        # Create a directory for storing aliases and config
        self.alias_dir = Path.home() / ".python_aliases"
        self.alias_dir.mkdir(exist_ok=True)
        
        # Config file to store alias mappings
        self.config_file = self.alias_dir / "aliases.json"
        
        # Directory where batch files will be created
        self.batch_dir = self.alias_dir / "bin"
        self.batch_dir.mkdir(exist_ok=True)
    
    def load_aliases(self) -> Dict[str, str]:
        """Load existing aliases from config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def save_aliases(self, aliases: Dict[str, str]):
        """Save aliases to config file."""
        with open(self.config_file, 'w') as f:
            json.dump(aliases, f, indent=2)
    
    def check_path_setup(self) -> bool:
        """Check if the alias directory is in PATH and provide setup instructions."""
        path_env = os.environ.get('PATH', '')
        batch_dir_str = str(self.batch_dir)
        
        if batch_dir_str not in path_env:
            safe_print(f"⚠️  Setup Required:")
            safe_print(f"The alias directory is not in your PATH.")
            safe_print(f"To use aliases from anywhere, add this directory to your PATH:")
            safe_print(f"  {batch_dir_str}")
            safe_print()
            safe_print("Windows Setup Instructions:")
            safe_print("1. Open System Properties (Win + Pause)")
            safe_print("2. Click 'Advanced system settings'")
            safe_print("3. Click 'Environment Variables'")
            safe_print("4. Under 'User variables', find and select 'Path', then click 'Edit'")
            safe_print("5. Click 'New' and add the path above")
            safe_print("6. Click 'OK' to save")
            safe_print("7. Restart your command prompt/PowerShell")
            safe_print()
            safe_print("PowerShell Command (as Administrator):")
            safe_print(f'[Environment]::SetEnvironmentVariable("Path", $env:Path + ";{batch_dir_str}", [EnvironmentVariableTarget]::User)')
            safe_print()
            safe_print("Bash/Linux/macOS Setup Instructions:")
            safe_print("Add this line to your ~/.bashrc, ~/.zshrc, or ~/.profile:")
            safe_print(f'export PATH="$PATH:{batch_dir_str}"')
            safe_print("Then run: source ~/.bashrc (or restart your terminal)")
            safe_print()
            safe_print("Git Bash on Windows:")
            safe_print("Add this line to ~/.bashrc:")
            safe_print(f'export PATH="$PATH:{batch_dir_str.replace(os.sep, "/")}"')
            return False
        else:
            safe_print(f"✓ Alias directory is in PATH: {batch_dir_str}")
            safe_print("Aliases will work in both Windows Command Prompt/PowerShell and Bash!")
            return True
