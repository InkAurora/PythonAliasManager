"""
Virtual environment detection for Python Alias Manager.
Handles detection of virtual environments (venv, conda) and project dependencies.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Optional


class VenvDetector:
    """Detects and manages virtual environment information for Python scripts."""
    
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
                        # Don't return yet, continue to check for requirements files
                        break
        
        # 2. Check for conda environment first (highest priority - most specific)
        conda_env_files = [
            script_dir / 'environment.yml',
            script_dir / 'environment.yaml',
            script_dir / 'conda.yml',
            script_dir / 'conda.yaml'
        ]
        
        for conda_env_file in conda_env_files:
            if conda_env_file.exists():
                venv_info['conda_env_file'] = str(conda_env_file)
                # Parse the environment name from the file
                conda_env_name = self.parse_conda_env_name(str(conda_env_file))
                if conda_env_name:
                    venv_info['conda_env_name'] = conda_env_name
                venv_info['type'] = 'conda'  # Conda environments take priority
                break
        
        # 3. Check for requirements.txt or pyproject.toml (suggests project with dependencies)
        requirements_files = [
            script_dir / 'requirements.txt',
            script_dir / 'pyproject.toml',
            script_dir / 'setup.py',
            script_dir / 'poetry.lock'
        ]
        
        for req_file in requirements_files:
            if req_file.exists():
                venv_info['requirements_file'] = str(req_file)
                if not venv_info.get('type'):  # Only set type if not already set (conda takes priority)
                    venv_info['type'] = 'project'
                break
        
        # 4. Check parent directories for venv (up to 3 levels) - only if no venv found yet
        if venv_info.get('type') != 'venv':
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
                                # Also check for requirements in parent dir
                                for req_file in requirements_files:
                                    if req_file.exists():
                                        venv_info['requirements_file'] = str(req_file)
                                        break
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
    
    def get_venv_python_from_path(self, venv_path: Path) -> Optional[str]:
        """Get Python executable from a virtual environment path."""
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
    
    def parse_conda_env_name(self, conda_env_file: str) -> Optional[str]:
        """Parse the environment name from a conda environment.yml file."""
        try:
            with open(conda_env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for name: field in the YAML file
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('name:'):
                    # Extract name after 'name:'
                    name_match = re.search(r'name:\s*([^\s#]+)', line)
                    if name_match:
                        return name_match.group(1).strip('"\'')
            
            return None
        except Exception as e:
            print(f"Error parsing conda environment file: {e}")
            return None
    
    def get_conda_python_executable(self, venv_info: Dict[str, str]) -> Optional[str]:
        """Get the Python executable path for a conda environment."""
        if not venv_info or venv_info.get('type') != 'conda':
            return None
        
        conda_env_name = venv_info.get('conda_env_name')
        if not conda_env_name:
            return None
        
        try:
            # Try to get conda environment info
            result = subprocess.run(['conda', 'info', '--envs'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and conda_env_name in result.stdout:
                # Environment exists, construct Python executable path
                env_path = None
                for line in result.stdout.split('\n'):
                    if conda_env_name in line and not line.startswith('#'):
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            env_path = Path(parts[-1])
                            break
                
                if env_path:
                    # Construct Python executable path
                    if os.name == 'nt':
                        python_exe = env_path / 'python.exe'
                    else:
                        python_exe = env_path / 'bin' / 'python'
                    
                    if python_exe.exists():
                        return str(python_exe)
            
            # Fallback: try conda run to get python executable
            result = subprocess.run(['conda', 'run', '-n', conda_env_name, 'python', '-c', 
                                   'import sys; print(sys.executable)'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                python_exe = result.stdout.strip()
                if python_exe and Path(python_exe).exists():
                    return python_exe
                    
        except Exception as e:
            print(f"Error getting conda Python executable: {e}")
        
        return None
    
    def check_conda_available(self) -> bool:
        """Check if conda is available in the system."""
        try:
            result = subprocess.run(['conda', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False
