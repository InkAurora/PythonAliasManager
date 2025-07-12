"""
Core Python Alias Manager class.
Main orchestrator that coordinates all other modules.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional

from .config import ConfigManager
from .venv_detector import VenvDetector
from .script_generator import ScriptGenerator
from .dependency_manager import DependencyManager
from .environment_setup import EnvironmentSetup


class PythonAliasManager:
    """Main class for managing Python script aliases."""
    
    def __init__(self):
        # Initialize all components
        self.config_manager = ConfigManager()
        self.venv_detector = VenvDetector()
        self.script_generator = ScriptGenerator(self.config_manager.batch_dir)
        self.dependency_manager = DependencyManager()
        self.environment_setup = EnvironmentSetup()
        
        # Load existing aliases
        self.aliases = self.config_manager.load_aliases()
    
    def add_alias(self, alias_name: str, script_path: str, conda_env: Optional[str] = None) -> bool:
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
        venv_info = self.venv_detector.detect_venv(script_path)
        
        # Override with specified conda environment if provided
        venv_info_override = None
        if conda_env:
            if self.venv_detector.check_conda_available():
                print(f"🐍 Using specified conda environment: {conda_env}")
                venv_info_override = {
                    'type': 'conda',
                    'conda_env_name': conda_env,
                    'conda_env_file': ''
                }
                # Use the override for display purposes
                venv_info = venv_info_override
            else:
                print(f"⚠️  Conda not available, ignoring --conda-env option")
        
        # Create both batch file (Windows) and shell script (Bash)
        try:
            batch_file = self.script_generator.create_batch_file(alias_name, script_path, venv_info_override)
            shell_file = self.script_generator.create_shell_script(alias_name, script_path, venv_info_override)
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
                elif venv_info.get('type') == 'conda':
                    print(f"   Type: Conda Environment")
                    print(f"   File: {venv_info['conda_env_file']}")
                    conda_env_name = venv_info.get('conda_env_name')
                    if conda_env_name:
                        print(f"   Environment: {conda_env_name}")
                    else:
                        print(f"   Warning: Environment name not found")
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
        self.config_manager.save_aliases(self.aliases)
        
        print(f"Alias '{alias_name}' created for '{script_path}'")
        print("Works in both Windows Command Prompt/PowerShell and Bash!")
        return True
    
    def remove_alias(self, alias_name: str) -> bool:
        """Remove an alias."""
        if alias_name not in self.aliases:
            print(f"Alias '{alias_name}' does not exist.")
            return False
        
        # Remove both batch file and shell script
        batch_file = self.config_manager.batch_dir / f"{alias_name}.bat"
        shell_file = self.config_manager.batch_dir / alias_name
        
        if batch_file.exists():
            batch_file.unlink()
            print(f"Removed Windows batch file: {batch_file}")
        
        if shell_file.exists():
            shell_file.unlink()
            print(f"Removed bash shell script: {shell_file}")
        
        # Remove from config
        del self.aliases[alias_name]
        self.config_manager.save_aliases(self.aliases)
        
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
            venv_info = self.venv_detector.detect_venv(script) if os.path.exists(script) else None
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
                conda_env_name = venv_info.get('conda_env_name')
                if conda_env_name:
                    print(f"   {'':>21}    Environment: {conda_env_name}")
                else:
                    print(f"   {'':>21}    Warning: Environment name not found")
            elif venv_info and venv_info.get('type') == 'project':
                print(f"   {'':>21}    Dependencies: {venv_info['requirements_file']}")
        
        # Show summary
        total_aliases = len(self.aliases)
        venv_aliases = sum(1 for script in self.aliases.values() 
                          if os.path.exists(script) and self.venv_detector.detect_venv(script))
        print("-" * 80)
        print(f"Total aliases: {total_aliases}")
        print(f"With virtual environments: {venv_aliases}")
        print(f"Without virtual environments: {total_aliases - venv_aliases}")
    
    def update_alias(self, alias_name: str, new_script_path: str, conda_env: str = None) -> bool:
        """Update an existing alias."""
        if alias_name not in self.aliases:
            print(f"Alias '{alias_name}' does not exist. Use 'add' to create it.")
            return False
        
        return self.add_alias(alias_name, new_script_path, conda_env)
    
    def check_path_setup(self):
        """Check if the alias directory is in PATH and provide setup instructions."""
        return self.config_manager.check_path_setup()
    
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
        
        venv_info = self.venv_detector.detect_venv(script_path)
        
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
            
            venv_python = self.venv_detector.get_venv_python_executable(venv_info)
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
                        if len(lines) > 2:
                            print(f"Installed packages: {len(lines) - 2} packages")
                        else:
                            print("Installed packages: None")
                except Exception:
                    print("Installed packages: Unable to determine")
            
        elif venv_info.get('type') == 'conda':
            print(f"Conda environment file: {venv_info['conda_env_file']}")
            conda_env_name = venv_info.get('conda_env_name')
            if conda_env_name:
                print(f"Environment name: {conda_env_name}")
                
                if self.venv_detector.check_conda_available():
                    print("✅ Conda is available")
                    
                    # Try to get Python version from conda env
                    try:
                        result = subprocess.run(['conda', 'run', '-n', conda_env_name, 'python', '--version'], 
                                             capture_output=True, text=True, timeout=30)
                        if result.returncode == 0:
                            print(f"Python version: {result.stdout.strip()}")
                    except Exception:
                        print("Python version: Unable to determine")
                    
                    # Try to list installed packages
                    try:
                        result = subprocess.run(['conda', 'list', '-n', conda_env_name], 
                                             capture_output=True, text=True, timeout=30)
                        if result.returncode == 0:
                            lines = result.stdout.strip().split('\n')
                            package_lines = [line for line in lines if not line.startswith('#') and line.strip()]
                            if package_lines:
                                print(f"Installed packages: {len(package_lines)} packages")
                            else:
                                print("Installed packages: None")
                    except Exception:
                        print("Installed packages: Unable to determine")
                else:
                    print("❌ Conda is not available in PATH")
                    print("Note: Install Anaconda/Miniconda or ensure conda is in your PATH")
            else:
                print("❌ Environment name not found in configuration file")
                print("Note: Make sure the environment.yml file contains a 'name:' field")
            
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

    def check_dependencies(self, alias_name: str, install_missing: bool = False) -> bool:
        """Check if dependencies for an alias are installed, optionally install missing ones."""
        if alias_name not in self.aliases:
            print(f"Alias '{alias_name}' not found.")
            return False
        
        script_path = self.aliases[alias_name]
        if not os.path.exists(script_path):
            print(f"Script '{script_path}' no longer exists.")
            return False
        
        print(f"Dependency Check for '{alias_name}':")
        print(f"Script: {script_path}")
        print("-" * 60)
        
        # Detect virtual environment and requirements
        venv_info = self.venv_detector.detect_venv(script_path)
        script_dir = Path(script_path).parent
        
        # Check for requirements files
        requirements_file = self.dependency_manager.find_requirements_file(script_dir)
        
        if not requirements_file:
            print("❌ No requirements file found")
            print("   Checked for: requirements.txt, pyproject.toml, setup.py, poetry.lock, environment.yml")
            if not venv_info:
                print("\nRecommendations:")
                print("• Create a requirements.txt file listing dependencies")
                print("• Or create a virtual environment with dependencies installed")
                print("• Or create an environment.yml file for conda environments")
            return False
        
        # Check if we have dependencies but no virtual environment
        if not venv_info or (venv_info.get('type') != 'venv' and venv_info.get('type') != 'conda'):
            # Parse requirements to see if there are any dependencies
            required_packages = self.dependency_manager.parse_requirements_file(requirements_file)
            req_path = Path(requirements_file)
            
            if required_packages and install_missing:
                if req_path.name in ['environment.yml', 'environment.yaml', 'conda.yml', 'conda.yaml']:
                    print("📦 Conda environment file found but no conda environment detected")
                    print("🔧 Creating conda environment automatically...")
                    
                    conda_env_created = self.environment_setup.create_conda_environment(script_path, requirements_file)
                    if not conda_env_created:
                        return False
                    
                    # Re-detect environment after creation
                    venv_info = self.venv_detector.detect_venv(script_path)
                    print("✅ Conda environment created and ready!")
                    
                    # Update the alias to use the new conda environment
                    self._update_alias_after_venv_creation(alias_name, script_path)
                else:
                    print("📦 Dependencies found but no virtual environment detected")
                    print("🔧 Creating virtual environment automatically...")
                    
                    venv_path_str = self.environment_setup.create_virtual_environment(script_path)
                    if not venv_path_str:
                        return False
                    
                    # Re-detect environment after creation
                    venv_info = self.venv_detector.detect_venv(script_path)
                    print("✅ Virtual environment created and ready!")
                    
                    # Update the alias to use the new virtual environment
                    self._update_alias_after_venv_creation(alias_name, script_path)
            elif required_packages:
                print("📦 Dependencies found but no virtual environment detected")
                print("💡 To auto-create virtual environment and install dependencies:")
                print(f"   python_alias_manager.py deps {alias_name} --install")
                return False
            elif not venv_info:
                print("❌ No virtual environment or dependencies detected")
                print("\nRecommendations:")
                print("• Create a requirements.txt file listing dependencies")
                print("• Or create a virtual environment with dependencies installed")
                print("• Or create an environment.yml file for conda environments")
                return False
        
        print(f"📋 Requirements file: {requirements_file}")
        
        # Parse requirements
        required_packages = self.dependency_manager.parse_requirements_file(requirements_file)
        
        if not required_packages:
            print("📦 No dependencies found in requirements file")
            return True
        
        print(f"📦 Found {len(required_packages)} required packages")
        
        # Determine Python executable to use
        python_exe = sys.executable  # Default fallback
        
        if venv_info and venv_info.get('type') == 'venv':
            venv_python = self.venv_detector.get_venv_python_executable(venv_info)
            if venv_python:
                python_exe = venv_python
                print(f"🐍 Using virtual environment Python: {venv_python}")
            else:
                print(f"⚠️  Virtual environment detected but Python executable not found, using: {python_exe}")
        elif venv_info and venv_info.get('type') == 'conda':
            conda_python = self.venv_detector.get_conda_python_executable(venv_info)
            if conda_python:
                python_exe = conda_python
                conda_env_name = venv_info.get('conda_env_name', 'unknown')
                print(f"🐍 Using conda environment Python: {conda_python} (env: {conda_env_name})")
            else:
                print(f"⚠️  Conda environment detected but Python executable not found, using: {python_exe}")
        else:
            print(f"🐍 Using system Python: {python_exe}")
        
        # Get installed packages
        print("\n🔍 Checking installed packages...")
        installed_packages = self.dependency_manager.get_installed_packages(python_exe)
        
        if not installed_packages:
            print("❌ Could not retrieve installed packages list")
            return False
        
        # Check each required package
        missing_packages = []
        installed_required = []
        
        for package in required_packages:
            package_lower = package.lower()
            if package_lower in installed_packages:
                installed_required.append(package)
            else:
                missing_packages.append(package)
        
        # Report results
        print(f"\n📊 Dependency Status:")
        print(f"   ✅ Installed: {len(installed_required)}")
        print(f"   ❌ Missing:   {len(missing_packages)}")
        
        if installed_required:
            print(f"\n✅ Installed packages:")
            for package in sorted(installed_required):
                print(f"   • {package}")
        
        if missing_packages:
            print(f"\n❌ Missing packages:")
            for package in sorted(missing_packages):
                print(f"   • {package}")
            
            if install_missing:
                print(f"\n🔧 Installing missing packages...")
                if venv_info and venv_info.get('type') == 'conda':
                    conda_env_name = venv_info.get('conda_env_name')
                    if conda_env_name:
                        return self.dependency_manager.install_conda_dependencies(conda_env_name, missing_packages)
                    else:
                        print("❌ Conda environment name not found")
                        return False
                else:
                    return self.dependency_manager.install_missing_dependencies(python_exe, missing_packages)
            else:
                print(f"\n💡 To install missing packages:")
                if venv_info and venv_info.get('type') == 'conda':
                    conda_env_name = venv_info.get('conda_env_name', 'your_env_name')
                    print(f"   conda install -n {conda_env_name} {' '.join(missing_packages)}")
                    print(f"   Or: python_alias_manager.py deps {alias_name} --install")
                else:
                    print(f"   python_alias_manager.py deps {alias_name} --install")
                    print(f"   Or manually: {python_exe} -m pip install {' '.join(missing_packages)}")
                return False
        else:
            print(f"\n🎉 All dependencies are installed!")
            return True

    def auto_setup_dependencies(self, alias_name: str, install_missing: bool = True) -> bool:
        """Automatically set up virtual environment and install dependencies for an alias."""
        if alias_name not in self.aliases:
            print(f"Alias '{alias_name}' not found.")
            return False
        
        script_path = self.aliases[alias_name]
        result = self.environment_setup.auto_setup_dependencies(script_path, self.aliases, install_missing)
        
        # Update the alias to use the new virtual environment if one was created
        if result:
            print("\n🔄 Updating alias to use new environment...")
            self._update_alias_after_venv_creation(alias_name, script_path)
            print(f"\n🎉 Setup complete! Alias '{alias_name}' is ready to use.")
        
        return result
    
    def _update_alias_after_venv_creation(self, alias_name: str, script_path: str) -> bool:
        """Update alias files after virtual environment creation to use the new venv Python."""
        if alias_name not in self.aliases:
            return False
        
        print(f"🔄 Updating alias '{alias_name}' to use new virtual environment...")
        
        # Create new batch and shell files with updated venv info
        try:
            batch_file = self.script_generator.create_batch_file(alias_name, script_path)
            shell_file = self.script_generator.create_shell_script(alias_name, script_path)
            print(f"✅ Updated alias files to use virtual environment")
            return True
        except Exception as e:
            print(f"⚠️  Warning: Could not update alias files: {e}")
            return False
