"""
Environment setup for Python Alias Manager.
Handles creation of virtual environments and conda environments.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

from .venv_detector import VenvDetector
from .dependency_manager import DependencyManager


class EnvironmentSetup:
    """Handles creation and setup of Python virtual environments and conda environments."""
    
    def __init__(self):
        self.venv_detector = VenvDetector()
        self.dependency_manager = DependencyManager()
    
    def create_virtual_environment(self, script_path: str) -> Optional[str]:
        """Create a virtual environment for a script if it doesn't exist."""
        script_dir = Path(script_path).parent
        venv_path = script_dir / ".venv"
        
        if venv_path.exists():
            print(f"✅ Virtual environment already exists at: {venv_path}")
            return str(venv_path)
        
        print(f"🔧 Creating virtual environment at: {venv_path}")
        
        try:
            # Create virtual environment in the script's directory
            result = subprocess.run([sys.executable, "-m", "venv", str(venv_path)], 
                                  capture_output=True, text=True, timeout=60, cwd=str(script_dir))
            
            if result.returncode != 0:
                print(f"❌ Failed to create virtual environment:")
                print(f"   {result.stderr}")
                return None
            
            print(f"✅ Virtual environment created successfully!")
            
            # Upgrade pip in the new environment
            venv_python = self.venv_detector.get_venv_python_from_path(venv_path)
            if venv_python:
                print("🔧 Upgrading pip in virtual environment...")
                pip_result = subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], 
                                          capture_output=True, text=True, timeout=60, cwd=str(script_dir))
                if pip_result.returncode == 0:
                    print("✅ Pip upgraded successfully!")
                else:
                    print("⚠️  Pip upgrade failed, but virtual environment is ready")
            
            return str(venv_path)
            
        except subprocess.TimeoutExpired:
            print("❌ Virtual environment creation timed out")
            return None
        except Exception as e:
            print(f"❌ Error creating virtual environment: {e}")
            return None

    def create_conda_environment(self, script_path: str, env_file: str) -> bool:
        """Create a conda environment from an environment.yml file."""
        if not self.venv_detector.check_conda_available():
            print("❌ Conda is not available in PATH")
            print("   Please install Anaconda/Miniconda or ensure conda is in your PATH")
            return False
        
        script_dir = Path(script_path).parent
        env_name = self.venv_detector.parse_conda_env_name(env_file)
        
        if not env_name:
            print("❌ Could not find environment name in the conda environment file")
            print("   Make sure your environment.yml file contains a 'name:' field")
            print("   Example:")
            print("   name: myproject")
            print("   dependencies:")
            print("     - python=3.9")
            print("     - numpy")
            return False
        
        print(f"🔧 Creating conda environment '{env_name}' from: {env_file}")
        
        try:
            # Check if environment already exists
            result = subprocess.run(['conda', 'env', 'list'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and env_name in result.stdout:
                # More precise check - environment name should be at start of line
                for line in result.stdout.split('\n'):
                    if line.strip().startswith(env_name):
                        print(f"✅ Conda environment '{env_name}' already exists")
                        return True
            
            # Create conda environment from file
            print(f"🔄 Running: conda env create -f {env_file}")
            result = subprocess.run(['conda', 'env', 'create', '-f', env_file], 
                                  capture_output=False, text=True, timeout=300, cwd=str(script_dir))
            
            if result.returncode != 0:
                print(f"❌ Failed to create conda environment")
                print("   Try creating the environment manually with: conda env create -f environment.yml")
                return False
            
            print(f"✅ Conda environment '{env_name}' created successfully!")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ Conda environment creation timed out")
            print("   Try creating the environment manually with: conda env create -f environment.yml")
            return False
        except Exception as e:
            print(f"❌ Error creating conda environment: {e}")
            return False

    def auto_setup_dependencies(self, script_path: str, aliases: dict, install_missing: bool = True) -> bool:
        """Automatically set up virtual environment and install dependencies for a script."""
        if not os.path.exists(script_path):
            print(f"Script '{script_path}' no longer exists.")
            return False
        
        print(f"🚀 Auto-setup for script:")
        print(f"Script: {script_path}")
        print("-" * 60)
        
        # Detect current environment and requirements
        venv_info = self.venv_detector.detect_venv(script_path)
        script_dir = Path(script_path).parent
        
        # Check for requirements files
        requirements_file = self.dependency_manager.find_requirements_file(script_dir)
        
        if not requirements_file:
            print("❌ No requirements file found")
            print("   Checked for: requirements.txt, pyproject.toml, setup.py, poetry.lock, environment.yml")
            print("   Create a requirements.txt file with your dependencies first")
            print("   Or create an environment.yml file for conda environments")
            return False
        
        print(f"📋 Found requirements file: {requirements_file}")
        req_path = Path(requirements_file)
        
        # Determine environment type based on file
        is_conda_file = req_path.name in ['environment.yml', 'environment.yaml', 'conda.yml', 'conda.yaml']
        
        if is_conda_file:
            print("🐍 Detected Conda environment file - will set up Anaconda environment")
            if not self.venv_detector.check_conda_available():
                print("❌ Conda is not available in PATH")
                print("   Please install Anaconda/Miniconda or ensure conda is in your PATH")
                return False
        else:
            print("🐍 Detected Python package file - will set up virtual environment")
        
        # Parse requirements to see if there are any dependencies
        required_packages = self.dependency_manager.parse_requirements_file(requirements_file)
        
        if not required_packages:
            print("📦 No dependencies found in requirements file")
            print("✅ No setup needed!")
            return True
        
        print(f"📦 Found {len(required_packages)} required packages: {', '.join(required_packages)}")
        
        # Check if virtual environment exists
        has_venv = self._check_environment_exists(venv_info, is_conda_file)
        
        venv_created = False
        
        if not has_venv:
            print("❌ No virtual environment found")
            
            if not install_missing:
                print("💡 To create virtual environment and install dependencies:")
                print(f"   python_alias_manager.py setup-deps {script_path}")
                return False
            
            # Create appropriate environment based on requirements file type
            if is_conda_file:
                print("🔧 Creating Anaconda environment from environment file...")
                conda_env_created = self.create_conda_environment(script_path, requirements_file)
                if not conda_env_created:
                    return False
                venv_created = True
                print("✅ Anaconda environment created successfully!")
            else:
                print("🔧 Creating Python virtual environment...")
                venv_path_str = self.create_virtual_environment(script_path)
                if not venv_path_str:
                    return False
                venv_created = True
                print("✅ Virtual environment created successfully!")
            
            # Re-detect environment after creation
            venv_info = self.venv_detector.detect_venv(script_path)
        else:
            if venv_info and venv_info.get('type') == 'venv':
                print(f"✅ Virtual environment already exists: {venv_info['path']}")
            elif venv_info and venv_info.get('type') == 'conda':
                conda_env_name = venv_info.get('conda_env_name', 'unknown')
                print(f"✅ Anaconda environment already exists: {conda_env_name}")
        
        print(f"\n🎉 Setup complete! Environment is ready to use.")
        return True

    def _check_environment_exists(self, venv_info: dict, is_conda_file: bool) -> bool:
        """Check if the detected virtual environment actually exists."""
        has_venv = False
        
        if venv_info and venv_info.get('type') == 'venv':
            # For regular venv, check if directory exists
            venv_path = venv_info.get('path')
            has_venv = venv_path and Path(venv_path).exists()
        elif venv_info and venv_info.get('type') == 'conda':
            # For conda environments, check if they actually exist in conda
            conda_env_name = venv_info.get('conda_env_name')
            if conda_env_name and self.venv_detector.check_conda_available():
                try:
                    result = subprocess.run(['conda', 'env', 'list'], 
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        # Check if environment name appears as a separate word (not just substring)
                        for line in result.stdout.split('\n'):
                            if conda_env_name in line and not line.startswith('#'):
                                # More precise check - environment name should be at start of line
                                if line.strip().startswith(conda_env_name):
                                    has_venv = True
                                    break
                except Exception:
                    has_venv = False
        
        return has_venv
